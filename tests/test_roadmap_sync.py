"""Unit tests for the roadmap-sync entrypoint (pure functions, no network)."""

from __future__ import annotations

from notion_sync import notion_api, roadmap_sync


def test_build_task_label_for_merged_pull_request() -> None:
    label = roadmap_sync.build_task_label(
        {
            "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_EVENT_ACTION": "closed",
            "PR_NUMBER": "42",
            "PR_TITLE": "feat: add thing",
            "PR_MERGED": "true",
        }
    )

    assert label == "PR#42 feat: add thing [merged]"


def test_build_task_label_for_open_pull_request_keeps_action() -> None:
    label = roadmap_sync.build_task_label(
        {
            "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_EVENT_ACTION": "opened",
            "PR_NUMBER": "7",
            "PR_TITLE": "fix: bug",
            "PR_MERGED": "false",
        }
    )

    assert label == "PR#7 fix: bug [opened]"


def test_build_task_label_for_issue() -> None:
    label = roadmap_sync.build_task_label(
        {
            "GITHUB_EVENT_NAME": "issues",
            "GITHUB_EVENT_ACTION": "opened",
            "ISSUE_NUMBER": "9",
            "ISSUE_TITLE": "broken",
        }
    )

    assert label == "Issue#9 broken [opened]"


def test_build_task_label_falls_back_to_event_name() -> None:
    assert (
        roadmap_sync.build_task_label({"GITHUB_EVENT_NAME": "push", "GITHUB_EVENT_ACTION": ""}) == "push []"
    )


def test_updated_cells_touches_only_task_and_date_columns() -> None:
    cells = [f"c{index}" for index in range(9)]

    updated = roadmap_sync.updated_cells(cells, "PR#1 x [merged]", "2026-07-31")

    assert updated[roadmap_sync.CELL_CURRENT_TASK][0]["text"]["content"] == "PR#1 x [merged]"
    assert updated[roadmap_sync.CELL_LAST_UPDATE][0]["text"]["content"] == "2026-07-31"
    assert [updated[index] for index in (0, 1, 2, 3, 5, 6, 8)] == ["c0", "c1", "c2", "c3", "c5", "c6", "c8"]
    assert cells[roadmap_sync.CELL_CURRENT_TASK] == "c4"


def test_updated_cells_tolerates_short_rows() -> None:
    assert roadmap_sync.updated_cells(["only"], "task", "2026-07-31") == ["only"]


def test_table_row_cells_reads_any_row_type() -> None:
    assert notion_api.table_row_cells({"type": "table_row", "table_row": {"cells": [1, 2]}}) == [1, 2]
    assert notion_api.table_row_cells({}) == []
