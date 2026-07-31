"""Unit tests for the branch-sync entrypoint (pure functions, no network)."""

from __future__ import annotations

import datetime

from notion_sync import branch_sync

CHANGELOG = """# Changelog

## [Unreleased]

### Added

- a first entry
- a second entry

## [1.2.0] - 2026-01-01

- older stuff
"""


def test_changelog_excerpt_keeps_first_section_only() -> None:
    excerpt = branch_sync.changelog_excerpt(CHANGELOG)

    assert excerpt.startswith("[Unreleased]")
    assert "a second entry" in excerpt
    assert "older stuff" not in excerpt


def test_changelog_excerpt_returns_empty_without_section() -> None:
    assert branch_sync.changelog_excerpt("no sections here") == ""


def test_normalise_date_accepts_github_timestamp() -> None:
    assert branch_sync.normalise_date("2026-07-31T10:11:12Z") == "2026-07-31"


def test_normalise_date_falls_back_to_today() -> None:
    assert branch_sync.normalise_date("not-a-date") == datetime.date.today().isoformat()


def test_ci_status_maps_conclusions() -> None:
    assert branch_sync.ci_status({"workflow_runs": [{"conclusion": "success"}]}) == "passing"
    assert branch_sync.ci_status({"workflow_runs": [{"conclusion": "timed_out"}]}) == "failing"
    assert branch_sync.ci_status({"workflow_runs": [{"conclusion": "cancelled"}]}) == "unknown"
    assert branch_sync.ci_status({"workflow_runs": []}) == "unknown"
    assert branch_sync.ci_status(None) == "unknown"


def test_read_context_derives_repo_parts_and_truncates() -> None:
    context = branch_sync.read_context(
        {
            "REPO_NAME": "chrysa/github-actions",
            "BRANCH_NAME": "feature/x",
            "COMMIT_SHA": "0123456789abcdef",
            "COMMIT_MSG": "feat: something\nbody line",
            "COMMIT_AUTHOR": "chrysa",
            "COMMIT_TS": "2026-07-31T10:11:12Z",
        }
    )

    assert context["repo_short"] == "github-actions"
    assert context["owner"] == "chrysa"
    assert context["sha"] == "0123456"
    assert context["message"] == "feat: something"
    assert context["updated_at"] == "2026-07-31"


def test_build_properties_omits_changelog_when_empty() -> None:
    context = branch_sync.read_context({"REPO_NAME": "chrysa/x", "BRANCH_NAME": "main"})

    without = branch_sync.build_properties(context, 0, "unknown", "")
    with_excerpt = branch_sync.build_properties(context, 2, "passing", "[1.0.0]\nnote")

    assert "Changelog" not in without
    assert with_excerpt["Changelog"]["rich_text"][0]["text"]["content"].startswith("[1.0.0]")
    assert with_excerpt["PR Count"] == {"number": 2}
    assert with_excerpt["CI Status"] == {"select": {"name": "passing"}}
