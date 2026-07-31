"""Sync the pushed branch to the shared Notion "Branch Activity" database."""

from __future__ import annotations

import datetime
import os
import re
import urllib.parse

from notion_sync.logging_setup import configure, get_logger
from notion_sync.notion_api import (
    NotionSyncError,
    github_request,
    notion_request,
    rich_text,
    table_row_cells,
)

CHANGELOG_PATH = "CHANGELOG.md"
CHANGELOG_PREVIEW_LINES = 8
COMMIT_MSG_MAX_CHARS = 120
AUTHOR_MAX_CHARS = 60
SHA_SHORT_LEN = 7
ROADMAP_TASK_MAX_CHARS = 80
CELL_CURRENT_TASK = 4
CELL_LAST_UPDATE = 7
DEFAULT_BRANCHES = ("main", "master")
CHANGELOG_SECTION_RE = re.compile(r"(?m)^##\s+\[([^\]]+)\][^\n]*\n(.*?)(?=^##\s+\[|\Z)", re.S)
CI_CONCLUSION_TO_STATUS = {
    "success": "passing",
    "failure": "failing",
    "timed_out": "failing",
}


logger = get_logger(__name__)


def normalise_date(timestamp: str) -> str:
    """Return an ISO date for a commit timestamp, falling back to today."""
    try:
        parsed = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return datetime.date.today().isoformat()
    return parsed.date().isoformat()


def changelog_excerpt(raw: str) -> str:
    """Extract the first changelog section as a short labelled preview."""
    match = CHANGELOG_SECTION_RE.search(raw)
    if not match:
        return ""
    lines = [line for line in match.group(2).strip().splitlines() if line.strip()]
    preview = "\n".join(lines[:CHANGELOG_PREVIEW_LINES])
    return f"[{match.group(1)}]\n{preview}"


def read_changelog_excerpt(path: str = CHANGELOG_PATH) -> str:
    """Read the repo changelog excerpt, or an empty string when absent."""
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as handle:
        return changelog_excerpt(handle.read())


def ci_status(runs: object) -> str:
    """Map the latest workflow run conclusion to the Notion CI status value."""
    workflow_runs = runs.get("workflow_runs") if isinstance(runs, dict) else None
    if not isinstance(workflow_runs, list) or not workflow_runs:
        return "unknown"
    latest = workflow_runs[0]
    conclusion = (latest.get("conclusion") if isinstance(latest, dict) else None) or "unknown"
    return CI_CONCLUSION_TO_STATUS.get(conclusion, "unknown")


def build_properties(context: dict[str, str], pr_count: int, status: str, excerpt: str) -> dict[str, object]:
    """Build the Notion page properties for one branch row."""
    properties: dict[str, object] = {
        "Branch": {"title": rich_text(context["branch"])},
        "Repo": {"rich_text": rich_text(context["repo_short"])},
        "Status": {"select": {"name": "active"}},
        "Last SHA": {"rich_text": rich_text(context["sha"])},
        "Commit Msg": {"rich_text": rich_text(context["message"])},
        "Author": {"rich_text": rich_text(context["author"])},
        "PR Count": {"number": pr_count},
        "CI Status": {"select": {"name": status}},
        "Updated At": {"date": {"start": context["updated_at"]}},
    }
    if excerpt:
        properties["Changelog"] = {"rich_text": rich_text(excerpt)}
    return properties


def read_context(env: dict[str, str]) -> dict[str, str]:
    """Collect the commit/branch context from the workflow environment."""
    repo = env.get("REPO_NAME", "")
    return {
        "repo": repo,
        "repo_short": repo.split("/")[-1],
        "owner": repo.split("/")[0] if "/" in repo else "",
        "branch": env.get("BRANCH_NAME", "unknown"),
        "sha": env.get("COMMIT_SHA", "")[:SHA_SHORT_LEN],
        "message": env.get("COMMIT_MSG", "")[:COMMIT_MSG_MAX_CHARS].split("\n")[0],
        "author": env.get("COMMIT_AUTHOR", "")[:AUTHOR_MAX_CHARS],
        "updated_at": normalise_date(env.get("COMMIT_TS", "")),
    }


def _find_existing_page(database_id: str, context: dict[str, str]) -> str | None:
    query = {
        "filter": {
            "and": [
                {"property": "Branch", "title": {"equals": context["branch"]}},
                {"property": "Repo", "rich_text": {"equals": context["repo_short"]}},
            ]
        }
    }
    result = notion_request("POST", f"databases/{database_id}/query", query)
    results = result.get("results") if isinstance(result, dict) else None
    if not isinstance(results, list) or not results:
        return None
    first = results[0]
    page_id = first.get("id") if isinstance(first, dict) else None
    return str(page_id) if page_id else None


def _sync_roadmap_row(excerpt: str, branch: str) -> None:
    block_id = os.environ.get("NOTION_PROJECT_BLOCK_ID", "").strip()
    if branch not in DEFAULT_BRANCHES or not excerpt or not block_id:
        return
    block = notion_request("GET", f"blocks/{block_id}")
    if not block:
        return
    cells = table_row_cells(block)
    if len(cells) > CELL_CURRENT_TASK:
        cells[CELL_CURRENT_TASK] = rich_text(excerpt.split("\n", maxsplit=1)[0][:ROADMAP_TASK_MAX_CHARS])
    if len(cells) > CELL_LAST_UPDATE:
        cells[CELL_LAST_UPDATE] = rich_text(datetime.date.today().isoformat())
    notion_request("PATCH", f"blocks/{block_id}", {"table_row": {"cells": cells}})
    logger.info(f"Roadmap row {block_id[:8]} changelog synced")


def main() -> int:
    configure()
    database_id = os.environ.get("NOTION_BRANCHES_DB_ID", "").strip()
    if not database_id:
        logger.info("NOTION_BRANCHES_DB_ID not set — skipping")
        return 0

    context = read_context(dict(os.environ))
    branch_query = urllib.parse.quote(context["branch"])
    pulls = github_request(
        f"repos/{context['repo']}/pulls?state=open&head={context['owner']}:{context['branch']}&per_page=10"
    )
    pr_count = len(pulls) if isinstance(pulls, list) else 0
    status = ci_status(
        github_request(f"repos/{context['repo']}/actions/runs?branch={branch_query}&per_page=1")
    )
    excerpt = read_changelog_excerpt()

    properties = build_properties(context, pr_count, status, excerpt)
    page_id = _find_existing_page(database_id, context)
    if page_id:
        response = notion_request("PATCH", f"pages/{page_id}", {"properties": properties})
        action = "updated"
    else:
        body = {"parent": {"database_id": database_id}, "properties": properties}
        response = notion_request("POST", "pages", body)
        action = "created"

    if not response:
        raise NotionSyncError(f"could not sync {context['repo_short']}/{context['branch']} to Notion")
    logger.info(
        f"Notion branch entry {action}: {context['repo_short']}/{context['branch']} "
        f"(sha={context['sha']}, ci={status}, prs={pr_count})"
    )
    _sync_roadmap_row(excerpt, context["branch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
