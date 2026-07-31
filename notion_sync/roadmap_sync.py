"""Sync an issue/PR event to the project's Notion roadmap table row."""

from __future__ import annotations

import datetime
import os

from notion_sync.logging_setup import configure, get_logger
from notion_sync.notion_api import notion_request, rich_text, table_row_cells

TASK_TITLE_MAX_CHARS = 55
CELL_CURRENT_TASK = 4
CELL_LAST_UPDATE = 7


logger = get_logger(__name__)


def build_task_label(env: dict[str, str]) -> str:
    """Render the one-line task label written to the roadmap row."""
    event = env.get("GITHUB_EVENT_NAME", "")
    action = env.get("GITHUB_EVENT_ACTION", "")
    if event == "pull_request":
        merged = env.get("PR_MERGED", "false").lower() == "true"
        state = "merged" if merged else action
        title = env.get("PR_TITLE", "")[:TASK_TITLE_MAX_CHARS]
        return f"PR#{env.get('PR_NUMBER', '')} {title} [{state}]"
    if event == "issues":
        title = env.get("ISSUE_TITLE", "")[:TASK_TITLE_MAX_CHARS]
        return f"Issue#{env.get('ISSUE_NUMBER', '')} {title} [{action}]"
    return f"{event} [{action}]"


def updated_cells(cells: list[object], task: str, today: str) -> list[object]:
    """Return the row cells with the current-task and last-update columns refreshed."""
    updated = list(cells)
    if len(updated) > CELL_CURRENT_TASK:
        updated[CELL_CURRENT_TASK] = rich_text(task)
    if len(updated) > CELL_LAST_UPDATE:
        updated[CELL_LAST_UPDATE] = rich_text(today)
    return updated


def main() -> int:
    configure()
    block_id = os.environ.get("NOTION_BLOCK_ID", "").strip()
    if not block_id or not os.environ.get("NOTION_TOKEN", ""):
        logger.info("Missing NOTION_TOKEN or NOTION_BLOCK_ID — skipping")
        return 0

    block = notion_request("GET", f"blocks/{block_id}")
    if not block:
        logger.info("::warning::roadmap row unreadable — skipping")
        return 0

    task = build_task_label(dict(os.environ))
    cells = updated_cells(table_row_cells(block), task, datetime.date.today().isoformat())
    notion_request("PATCH", f"blocks/{block_id}", {"table_row": {"cells": cells}})
    logger.info(f"Notion roadmap row {block_id[:8]} → {task}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
