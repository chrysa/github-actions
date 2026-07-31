"""Entrypoint-level tests: the main() flows with every network call mocked."""

from __future__ import annotations

from typing import TYPE_CHECKING

from notion_sync import branch_sync, roadmap_sync

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

BRANCH_ENV = {
    "NOTION_BRANCHES_DB_ID": "db-1",
    "NOTION_TOKEN": "t",
    "REPO_NAME": "chrysa/github-actions",
    "BRANCH_NAME": "main",
    "COMMIT_SHA": "0123456789",
    "COMMIT_MSG": "feat: x",
    "COMMIT_AUTHOR": "chrysa",
    "COMMIT_TS": "2026-07-31T10:00:00Z",
    "NOTION_PROJECT_BLOCK_ID": "",
}


def test_branch_sync_skips_without_database_id(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {"NOTION_BRANCHES_DB_ID": ""}, clear=False)

    assert branch_sync.main() == 0


def test_branch_sync_creates_a_row_when_none_exists(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", BRANCH_ENV, clear=False)
    mocker.patch.object(branch_sync, "read_changelog_excerpt", return_value="")
    mocker.patch.object(branch_sync, "github_request", return_value=[])
    notion = mocker.patch.object(branch_sync, "notion_request", side_effect=[{"results": []}, {"id": "page-1"}])

    assert branch_sync.main() == 0
    assert notion.call_args_list[-1].args[0] == "POST"
    assert notion.call_args_list[-1].args[1] == "pages"


def test_branch_sync_updates_the_existing_row(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", BRANCH_ENV, clear=False)
    mocker.patch.object(branch_sync, "read_changelog_excerpt", return_value="")
    mocker.patch.object(branch_sync, "github_request", return_value=[])
    notion = mocker.patch.object(
        branch_sync, "notion_request", side_effect=[{"results": [{"id": "page-9"}]}, {"id": "page-9"}]
    )

    assert branch_sync.main() == 0
    assert notion.call_args_list[-1].args[:2] == ("PATCH", "pages/page-9")


def test_branch_sync_raises_when_notion_write_fails(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", BRANCH_ENV, clear=False)
    mocker.patch.object(branch_sync, "read_changelog_excerpt", return_value="")
    mocker.patch.object(branch_sync, "github_request", return_value=[])
    mocker.patch.object(branch_sync, "notion_request", side_effect=[{"results": []}, None])

    try:
        branch_sync.main()
    except branch_sync.NotionSyncError:
        return
    raise AssertionError("a failed Notion write must raise")


def test_branch_sync_pushes_the_changelog_to_the_roadmap_row(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {**BRANCH_ENV, "NOTION_PROJECT_BLOCK_ID": "block-1"}, clear=False)
    mocker.patch.object(branch_sync, "read_changelog_excerpt", return_value="[1.0.0]\nnote")
    mocker.patch.object(branch_sync, "github_request", return_value=[{"number": 1}])
    row = {"type": "table_row", "table_row": {"cells": [f"c{i}" for i in range(9)]}}
    notion = mocker.patch.object(
        branch_sync, "notion_request", side_effect=[{"results": []}, {"id": "p"}, row, {"id": "block-1"}]
    )

    assert branch_sync.main() == 0
    method, path, body = notion.call_args_list[-1].args
    assert (method, path) == ("PATCH", "blocks/block-1")
    assert body["table_row"]["cells"][branch_sync.CELL_CURRENT_TASK][0]["text"]["content"] == "[1.0.0]"


def test_branch_sync_reads_the_changelog_from_disk(tmp_path, mocker: MockerFixture) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("## [9.9.9]\n\n- shipped\n", encoding="utf-8")

    assert branch_sync.read_changelog_excerpt(str(changelog)).startswith("[9.9.9]")
    assert branch_sync.read_changelog_excerpt(str(tmp_path / "missing.md")) == ""


def test_roadmap_sync_skips_without_configuration(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {"NOTION_BLOCK_ID": "", "NOTION_TOKEN": ""}, clear=False)

    assert roadmap_sync.main() == 0


def test_roadmap_sync_skips_when_the_row_is_unreadable(mocker: MockerFixture) -> None:
    mocker.patch.dict("os.environ", {"NOTION_BLOCK_ID": "b", "NOTION_TOKEN": "t"}, clear=False)
    mocker.patch.object(roadmap_sync, "notion_request", return_value=None)

    assert roadmap_sync.main() == 0


def test_roadmap_sync_patches_the_row(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        "os.environ",
        {
            "NOTION_BLOCK_ID": "b",
            "NOTION_TOKEN": "t",
            "GITHUB_EVENT_NAME": "issues",
            "GITHUB_EVENT_ACTION": "opened",
            "ISSUE_NUMBER": "3",
            "ISSUE_TITLE": "bug",
        },
        clear=False,
    )
    row = {"type": "table_row", "table_row": {"cells": [f"c{i}" for i in range(9)]}}
    notion = mocker.patch.object(roadmap_sync, "notion_request", side_effect=[row, {"id": "b"}])

    assert roadmap_sync.main() == 0
    method, path, body = notion.call_args_list[-1].args
    assert (method, path) == ("PATCH", "blocks/b")
    assert body["table_row"]["cells"][roadmap_sync.CELL_CURRENT_TASK][0]["text"]["content"] == "Issue#3 bug [opened]"
