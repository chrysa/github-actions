"""Stdlib JSON-over-HTTPS client with request pacing and bounded retries.

Retries cover rate limiting (429, or 403 with ``Retry-After`` — GitHub's secondary limit),
transient gateway errors and network errors. Error messages never carry the URL.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Collection, Mapping
from http import HTTPStatus
from http.client import HTTPMessage
from typing import IO, Final, override

from shortcut_sync.errors import ApiError

SECURE_SCHEME: Final = "https"
REQUEST_TIMEOUT_SECONDS: Final = 20
MAX_ATTEMPTS: Final = 5
BACKOFF_BASE_SECONDS: Final = 2.0
BACKOFF_CAP_SECONDS: Final = 60.0
RETRY_AFTER_HEADER: Final = "Retry-After"
RETRYABLE_STATUSES: Final = frozenset(
    {
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    }
)


def with_query(*, path: str, query: Mapping[str, str | int]) -> str:
    """Append an encoded query string to a path or URL."""
    return f"{path}?{urllib.parse.urlencode(query)}"


def backoff_delay(attempt: int) -> float:
    """Exponential backoff for the given 1-based attempt, capped."""
    return min(BACKOFF_CAP_SECONDS, BACKOFF_BASE_SECONDS**attempt)


def retry_after_delay(value: str | None) -> float | None:
    """Seconds from a ``Retry-After`` header (delta-seconds form), capped; None when unusable."""
    if value is None:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    return min(BACKOFF_CAP_SECONDS, max(0.0, seconds))


class _SameOriginRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only to the same https origin.

    urllib copies every request header onto the redirected request, so a redirect to another
    host would hand it the ``Authorization`` / ``Shortcut-Token`` header.
    """

    @override
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: HTTPMessage,
        newurl: str,
    ) -> urllib.request.Request | None:
        absolute = urllib.parse.urljoin(req.full_url, newurl)
        current = urllib.parse.urlsplit(req.full_url)
        target = urllib.parse.urlsplit(absolute)
        if target.scheme != SECURE_SCHEME or target.netloc != current.netloc:
            return None
        return super().redirect_request(req, fp, code, msg, headers, absolute)


_OPENER: Final = urllib.request.build_opener(_SameOriginRedirectHandler)


class HttpClient:
    """One remote service: base URL, fixed headers, minimum spacing between requests."""

    def __init__(
        self,
        *,
        service: str,
        base_url: str,
        headers: Mapping[str, str],
        min_interval_seconds: float = 0.0,
    ) -> None:
        self._service = service
        self._base_url = base_url.rstrip("/")
        self._headers = dict(headers)
        self._min_interval_seconds = min_interval_seconds
        self._last_request_at: float | None = None

    def request(
        self,
        *,
        method: str,
        path: str,
        body: object | None = None,
        absent_statuses: Collection[int] = (),
    ) -> object | None:
        """Send one JSON request. Returns the decoded body, or None for an absent resource."""
        url = f"{self._base_url}/{path.lstrip('/')}"
        data = json.dumps(body).encode() if body is not None else None
        attempt = 0
        while True:
            attempt += 1
            self._pace()
            try:
                return self._send(method=method, url=url, data=data)
            except urllib.error.HTTPError as error:
                delay = self._http_retry_delay(error=error, attempt=attempt)
                error.close()
                if delay is None and error.code in absent_statuses:
                    return None
                if delay is None:
                    raise ApiError(
                        service=self._service, method=method, reason=f"HTTP {error.code}"
                    ) from None
            except (urllib.error.URLError, TimeoutError):
                delay = backoff_delay(attempt) if attempt < MAX_ATTEMPTS else None
                if delay is None:
                    raise ApiError(service=self._service, method=method, reason="network error") from None
            time.sleep(delay)

    def request_object(
        self,
        *,
        method: str,
        path: str,
        body: object | None = None,
        absent_statuses: Collection[int] = (),
    ) -> dict[str, object] | None:
        """Send a request whose response is a JSON object (or empty / absent → None)."""
        result = self.request(method=method, path=path, body=body, absent_statuses=absent_statuses)
        if result is None or isinstance(result, dict):
            return result
        raise ApiError(service=self._service, method=method, reason="unexpected payload")

    def request_objects(self, *, path: str) -> list[dict[str, object]]:
        """GET a JSON array and keep its object items."""
        result = self.request(method="GET", path=path)
        if not isinstance(result, list):
            raise ApiError(service=self._service, method="GET", reason="unexpected payload")
        return [item for item in result if isinstance(item, dict)]

    def _http_retry_delay(self, *, error: urllib.error.HTTPError, attempt: int) -> float | None:
        retry_after = error.headers.get(RETRY_AFTER_HEADER) if error.headers else None
        rate_limited = error.code == HTTPStatus.FORBIDDEN and retry_after is not None
        if attempt >= MAX_ATTEMPTS or not (error.code in RETRYABLE_STATUSES or rate_limited):
            return None
        return retry_after_delay(retry_after) or backoff_delay(attempt)

    def _pace(self) -> None:
        if self._min_interval_seconds <= 0:
            return
        now = time.monotonic()
        if self._last_request_at is not None:
            wait = self._min_interval_seconds - (now - self._last_request_at)
            if wait > 0:
                time.sleep(wait)
                now += wait
        self._last_request_at = now

    def _send(self, *, method: str, url: str, data: bytes | None) -> object | None:
        request = urllib.request.Request(url, data=data, method=method, headers=self._headers)
        with _OPENER.open(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            raw = response.read()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except ValueError:
            raise ApiError(service=self._service, method=method, reason="invalid JSON response") from None
