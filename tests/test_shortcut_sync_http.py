"""HTTP layer and API clients of shortcut_sync — fake transport only, no network."""

from __future__ import annotations

import io
import urllib.error
import urllib.request
from http.client import HTTPMessage
from typing import TYPE_CHECKING

import pytest

from shortcut_sync import http_client
from shortcut_sync.errors import ApiError
from shortcut_sync.github_client import GitHubClient
from shortcut_sync.http_client import HttpClient, backoff_delay, retry_after_delay
from shortcut_sync.sonar_client import SonarClient

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from tests.conftest import FakeHttp

BASE = "https://api.example.test"


def _client(*, min_interval_seconds: float = 0.0) -> HttpClient:
    return HttpClient(
        service="Example",
        base_url=f"{BASE}/",
        headers={"X-Test": "1"},
        min_interval_seconds=min_interval_seconds,
    )


def test_request_sends_json_and_decodes_the_response(fake_http: FakeHttp) -> None:
    fake_http.add("POST", f"{BASE}/items", {"id": 7})

    assert _client().request(method="POST", path="/items", body={"a": 1}) == {"id": 7}
    assert fake_http.calls[0].body == {"a": 1}
    assert fake_http.calls[0].headers["X-test"] == "1"


def test_empty_body_decodes_to_none(fake_http: FakeHttp) -> None:
    fake_http.add("PUT", f"{BASE}/items/1", None)

    assert _client().request(method="PUT", path="items/1") is None


def test_rate_limit_is_retried_after_the_announced_delay(fake_http: FakeHttp, mocker: MockerFixture) -> None:
    fake_http.add("GET", f"{BASE}/items", {}, status=429, headers={"Retry-After": "3"})
    fake_http.add("GET", f"{BASE}/items", [1])

    assert _client().request(method="GET", path="items") == [1]
    assert http_client.time.sleep.call_args_list == [mocker.call(3.0)]


def test_github_secondary_rate_limit_403_is_retried(fake_http: FakeHttp) -> None:
    fake_http.add("GET", f"{BASE}/items", {}, status=403, headers={"Retry-After": "1"})
    fake_http.add("GET", f"{BASE}/items", [2])

    assert _client().request(method="GET", path="items", absent_statuses=(403,)) == [2]


def test_absent_status_returns_none_without_retry(fake_http: FakeHttp) -> None:
    fake_http.add("GET", f"{BASE}/repos/chrysa/private-repo", {}, status=404)

    assert _client().request(method="GET", path="repos/chrysa/private-repo", absent_statuses=(404,)) is None
    assert len(fake_http.calls) == 1


def test_non_retryable_error_raises_without_leaking_the_path(fake_http: FakeHttp) -> None:
    fake_http.add("GET", f"{BASE}/repos/chrysa/private-repo", {}, status=500)

    with pytest.raises(ApiError) as caught:
        _client().request(method="GET", path="repos/chrysa/private-repo")

    assert str(caught.value) == "Example GET failed: HTTP 500"
    assert len(fake_http.calls) == 1


def test_persistent_unavailability_gives_up_after_max_attempts(
    fake_http: FakeHttp, mocker: MockerFixture
) -> None:
    fake_http.add("GET", f"{BASE}/items", {}, status=503)

    with pytest.raises(ApiError):
        _client().request(method="GET", path="items")

    assert len(fake_http.calls) == http_client.MAX_ATTEMPTS
    assert http_client.time.sleep.call_args_list == [mocker.call(delay) for delay in (2.0, 4.0, 8.0, 16.0)]


def test_network_errors_are_retried_then_raised(fake_http: FakeHttp, mocker: MockerFixture) -> None:
    opener = mocker.patch.object(http_client._OPENER, "open", side_effect=urllib.error.URLError("down"))

    with pytest.raises(ApiError, match="network error"):
        _client().request(method="GET", path="items")

    assert opener.call_count == http_client.MAX_ATTEMPTS


def test_invalid_json_raises(fake_http: FakeHttp) -> None:
    fake_http.add("GET", f"{BASE}/items", b"<html>")

    with pytest.raises(ApiError, match="invalid JSON"):
        _client().request(method="GET", path="items")


def test_typed_helpers_reject_unexpected_payloads(fake_http: FakeHttp) -> None:
    fake_http.add("GET", f"{BASE}/list", {"not": "a list"})
    fake_http.add("GET", f"{BASE}/object", [1])

    with pytest.raises(ApiError, match="unexpected payload"):
        _client().request_objects(path="list")
    with pytest.raises(ApiError, match="unexpected payload"):
        _client().request_object(method="GET", path="object")


def test_requests_are_spaced_by_the_minimum_interval(fake_http: FakeHttp, mocker: MockerFixture) -> None:
    mocker.patch.object(http_client.time, "monotonic", return_value=100.0)
    fake_http.add("GET", f"{BASE}/items", [])
    client = _client(min_interval_seconds=0.3)

    client.request(method="GET", path="items")
    client.request(method="GET", path="items")

    assert http_client.time.sleep.call_args_list == [mocker.call(pytest.approx(0.3))]


def test_backoff_and_retry_after_parsing() -> None:
    assert backoff_delay(1) == 2.0
    assert backoff_delay(10) == http_client.BACKOFF_CAP_SECONDS
    assert retry_after_delay("5") == 5.0
    assert retry_after_delay("-4") == 0.0
    assert retry_after_delay("Wed, 21 Oct 2015 07:28:00 GMT") is None
    assert retry_after_delay(None) is None


def test_github_lists_every_page_and_drops_pull_requests(fake_http: FakeHttp) -> None:
    root = "https://api.github.com/repos/chrysa/alpha/issues?state=open&per_page=100"
    first_page = [{"number": n, "html_url": f"u{n}"} for n in range(100)]
    first_page[0]["pull_request"] = {}
    fake_http.add("GET", f"{root}&page=1", first_page)
    fake_http.add("GET", f"{root}&page=2", [{"number": 100}])
    client = GitHubClient.from_token(
        token="test-github-token", base_url="https://api.github.com", owner="chrysa"
    )

    issues = client.list_open_issues("alpha")

    assert len(issues) == 100
    assert all("pull_request" not in issue for issue in issues)
    assert fake_http.calls[0].headers["Authorization"] == "Bearer test-github-token"


def test_sonar_reads_anonymously_and_skips_private_projects(fake_http: FakeHttp) -> None:
    url = "https://sonarcloud.io/api/qualitygates/project_status?projectKey="
    fake_http.add("GET", f"{url}chrysa_public", {"projectStatus": {"status": "ERROR"}})
    fake_http.add("GET", f"{url}chrysa_private", {"errors": []}, status=404)
    client = SonarClient.anonymous(base_url="https://sonarcloud.io")

    assert client.quality_gate_status("chrysa_public") == "ERROR"
    assert client.quality_gate_status("chrysa_private") is None
    assert "Authorization" not in fake_http.calls[0].headers


@pytest.mark.parametrize(
    ("target", "followed"),
    [
        ("https://api.example.test/moved", True),
        ("/relative/moved", True),
        ("https://elsewhere.example/steal", False),
        ("http://api.example.test/downgrade", False),
    ],
)
def test_redirects_stay_on_the_same_https_origin(target: str, followed: bool) -> None:
    handler = http_client._SameOriginRedirectHandler()
    request = urllib.request.Request(f"{BASE}/items", headers={"Authorization": "Bearer test"})

    redirected = handler.redirect_request(request, io.BytesIO(), 302, "Found", HTTPMessage(), target)

    assert (redirected is not None) is followed
