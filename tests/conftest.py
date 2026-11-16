"""Shared fixtures. ``fake_http`` replaces the network for the shortcut_sync tests."""

from __future__ import annotations

import io
import json
import urllib.error
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

OK = 200


class _FakeResponse:
    def __init__(self, payload: object) -> None:
        if isinstance(payload, bytes):
            self._raw = payload
        else:
            self._raw = b"" if payload is None else json.dumps(payload).encode()

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return self._raw


@dataclass
class RecordedCall:
    method: str
    url: str
    body: object | None
    headers: dict[str, str]


@dataclass
class FakeHttp:
    """Answers the HTTP opener from registered routes; an unregistered request fails the test.

    A route holds a queue of responses: each call pops one, the last one repeats.
    """

    routes: dict[str, list[tuple[int, object, dict[str, str]]]] = field(default_factory=dict)
    calls: list[RecordedCall] = field(default_factory=list)

    def add(
        self,
        method: str,
        url: str,
        payload: object = None,
        *,
        status: int = OK,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.routes.setdefault(f"{method} {url}", []).append((status, payload, headers or {}))

    def writes(self) -> list[RecordedCall]:
        return [call for call in self.calls if call.method != "GET"]

    def __call__(self, request: urllib.request.Request, timeout: float | None = None) -> _FakeResponse:
        method = request.get_method()
        body = json.loads(request.data) if isinstance(request.data, bytes) else None
        self.calls.append(RecordedCall(method, request.full_url, body, dict(request.header_items())))
        queue = self.routes.get(f"{method} {request.full_url}")
        if not queue:
            raise AssertionError(f"unexpected request: {method} {request.full_url}")
        status, payload, headers = queue.pop(0) if len(queue) > 1 else queue[0]
        if status >= 400:
            raw = io.BytesIO(json.dumps(payload).encode())
            raise urllib.error.HTTPError(request.full_url, status, "error", headers, raw)  # type: ignore[arg-type]
        return _FakeResponse(payload)


@pytest.fixture
def fake_http(mocker: MockerFixture) -> Iterator[FakeHttp]:
    """Patch the shortcut_sync transport and its sleeps — no network, no waiting."""
    fake = FakeHttp()
    mocker.patch("shortcut_sync.http_client._OPENER.open", side_effect=fake)
    mocker.patch("shortcut_sync.http_client.time.sleep")
    yield fake
