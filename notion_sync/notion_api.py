"""Minimal stdlib-only Notion + GitHub REST helpers shared by the sync entrypoints."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

NOTION_API_ROOT = "https://api.notion.com/v1/"
GITHUB_API_ROOT = "https://api.github.com/"
NOTION_VERSION = "2022-06-28"
GITHUB_API_VERSION = "2022-11-28"
REQUEST_TIMEOUT_SECONDS = 15
RICH_TEXT_MAX_CHARS = 2000

_DEFAULT_ANNOTATIONS = {
    "bold": False,
    "italic": False,
    "strikethrough": False,
    "underline": False,
    "code": False,
    "color": "default",
}


class NotionSyncError(RuntimeError):
    """A Notion or GitHub call failed in a way the caller must handle."""


def rich_text(content: object) -> list[dict[str, object]]:
    """Build a Notion `rich_text` payload from any printable value."""
    text = str(content)[:RICH_TEXT_MAX_CHARS]
    return [
        {
            "type": "text",
            "text": {"content": text},
            "plain_text": text,
            "annotations": dict(_DEFAULT_ANNOTATIONS),
        }
    ]


def _request(url: str, headers: dict[str, str], method: str, body: object | None) -> object | None:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        print(f"::warning::{method} {url} failed ({error.code}): {error.read().decode()[:500]}")
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f"::warning::{method} {url} failed: {error}")
    return None


def notion_request(method: str, path: str, body: object | None = None) -> object | None:
    """Call the Notion API. Returns the decoded body, or None when the call failed."""
    token = os.environ.get("NOTION_TOKEN", "")
    if not token:
        raise NotionSyncError("NOTION_TOKEN is not set")
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    return _request(NOTION_API_ROOT + path.lstrip("/"), headers, method, body)


def github_request(path: str) -> object | None:
    """Read the GitHub API with the workflow token. Returns None when the call failed."""
    headers = {
        "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    return _request(GITHUB_API_ROOT + path.lstrip("/"), headers, "GET", None)


def table_row_cells(block: object) -> list[object]:
    """Extract the cells of a Notion table-row block."""
    if not isinstance(block, dict):
        return []
    row = block.get(block.get("type", "table_row"), {})
    cells = row.get("cells", []) if isinstance(row, dict) else []
    return list(cells) if isinstance(cells, list) else []
