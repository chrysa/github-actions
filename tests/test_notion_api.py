"""Unit tests for the Notion/GitHub HTTP helpers — no real network."""

from __future__ import annotations

import json
import urllib.error
from typing import TYPE_CHECKING

import pytest

from notion_sync import notion_api

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


class _FakeResponse:
    def __init__(self, payload: object) -> None:
        self._payload = json.dumps(payload).encode()

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


def test_rich_text_truncates_and_stringifies() -> None:
    element = notion_api.rich_text(42)[0]

    assert element["text"] == {"content": "42"}
    assert element["plain_text"] == "42"

    long_element = notion_api.rich_text("x" * 5000)[0]

    assert len(long_element["plain_text"]) == notion_api.RICH_TEXT_MAX_CHARS


def test_notion_request_sends_token_and_returns_payload(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {"NOTION_TOKEN": "secret-token"}, clear=False)
    urlopen = mocker.patch.object(notion_api.urllib.request, "urlopen", return_value=_FakeResponse({"ok": True}))

    result = notion_api.notion_request("POST", "pages", {"a": 1})

    assert result == {"ok": True}
    request = urlopen.call_args.args[0]
    assert request.full_url == "https://api.notion.com/v1/pages"
    assert request.get_method() == "POST"
    assert request.headers["Authorization"] == "Bearer secret-token"
    assert request.headers["Notion-version"] == notion_api.NOTION_VERSION


def test_notion_request_without_token_raises(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {"NOTION_TOKEN": ""}, clear=False)

    with pytest.raises(notion_api.NotionSyncError):
        notion_api.notion_request("GET", "pages/1")


def test_request_returns_none_on_http_error(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {"NOTION_TOKEN": "t"}, clear=False)
    error = urllib.error.HTTPError("https://api.notion.com/v1/pages", 400, "Bad", {}, None)
    mocker.patch.object(error, "read", return_value=b"boom")
    mocker.patch.object(notion_api.urllib.request, "urlopen", side_effect=error)

    assert notion_api.notion_request("GET", "pages/1") is None


def test_request_returns_none_on_url_error(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {"GITHUB_TOKEN": "t"}, clear=False)
    mocker.patch.object(notion_api.urllib.request, "urlopen", side_effect=urllib.error.URLError("down"))

    assert notion_api.github_request("repos/chrysa/x/pulls") is None


def test_github_request_targets_the_rest_api(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {"GITHUB_TOKEN": "gh-token"}, clear=False)
    urlopen = mocker.patch.object(notion_api.urllib.request, "urlopen", return_value=_FakeResponse([1, 2]))

    assert notion_api.github_request("repos/chrysa/x/pulls") == [1, 2]
    assert urlopen.call_args.args[0].full_url == "https://api.github.com/repos/chrysa/x/pulls"


def test_table_row_cells_rejects_non_mappings() -> None:
    assert notion_api.table_row_cells("nope") == []
    assert notion_api.table_row_cells({"type": "table_row", "table_row": {"cells": "bad"}}) == []
