"""Pure pieces of shortcut_sync: references, keys, config, workflow states, mapping, report."""

from __future__ import annotations

import logging

import pytest

from shortcut_sync.errors import ConfigurationError, MissingSecretError
from shortcut_sync.issue_key import IssueKey
from shortcut_sync.references import (
    has_shortcut_reference,
    issue_comment,
    linked_issue_keys,
    same_link,
    sonar_dashboard_url,
    story_type_for,
)
from shortcut_sync.repo_mapping import RepoMapping
from shortcut_sync.story_draft import STORY_NAME_MAX_CHARS, StoryDraft
from shortcut_sync.sync_config import SyncConfig
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.sync_report import SyncReport
from shortcut_sync.workflow_states import WorkflowStates

SECRETS = {"SHORTCUT_API_TOKEN": "test-shortcut-token", "SYNC_GITHUB_TOKEN": "test-github-token"}


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("tracked in sc-12", True),
        ("[SC-5933] done", True),
        ("see https://app.shortcut.com/chrysa/story/5933/some-title", True),
        ("disc-12 is not a story", False),
        ("", False),
        (None, False),
    ],
)
def test_shortcut_reference_detection(text: object, expected: bool) -> None:
    assert has_shortcut_reference(text) is expected


@pytest.mark.parametrize(
    ("labels", "expected"),
    [
        ([{"name": "Bug"}], "bug"),
        ([{"name": "enhancement"}, {"name": "sentry"}], "bug"),
        ([{"name": "enhancement"}], "feature"),
        ([], "feature"),
    ],
)
def test_story_type_follows_the_bug_and_sentry_labels(labels: list[dict[str, str]], expected: str) -> None:
    assert story_type_for(labels) == expected


def test_issue_key_parsing_is_normalised() -> None:
    key = IssueKey.from_url("https://github.com/Chrysa/Alpha/issues/12#issuecomment-1")

    assert key == IssueKey(owner="chrysa", repo="alpha", number=12)
    assert key.external_id == "chrysa/alpha#12"
    assert IssueKey.from_external_id("chrysa/alpha#12") == key
    assert IssueKey.from_url("https://github.com/chrysa/alpha/pull/12") is None
    assert IssueKey.from_url(None) is None
    assert IssueKey.from_external_id("chrysa/alpha") is None


def test_linked_issue_keys_read_links_and_sync_markers() -> None:
    stories = [
        {"external_links": ["https://github.com/chrysa/alpha/issues/1", "https://example.test/x"]},
        {"external_links": [], "external_id": "chrysa/beta#2"},
        {"external_id": None},
    ]

    assert linked_issue_keys(stories) == {
        IssueKey(owner="chrysa", repo="alpha", number=1),
        IssueKey(owner="chrysa", repo="beta", number=2),
    }


def test_small_formatters() -> None:
    assert issue_comment(story_id=5, app_url="https://app.shortcut.com/chrysa/story/5") == (
        "Shortcut: sc-5 https://app.shortcut.com/chrysa/story/5"
    )
    assert sonar_dashboard_url(sonar_url="https://sonarcloud.io", project_key="chrysa_alpha") == (
        "https://sonarcloud.io/dashboard?id=chrysa_alpha"
    )
    assert same_link(
        "https://SonarCloud.io/dashboard?id=chrysa_alpha/", "https://sonarcloud.io/dashboard?id=chrysa_alpha"
    )


def test_config_defaults_are_safe_and_hide_tokens() -> None:
    config = SyncConfig.from_env(SECRETS)

    assert config.dry_run is True
    assert config.max_creations == 25
    assert config.workflow_id is None
    assert config.shortcut_api_url == "https://api.app.shortcut.com/api/v3"
    assert "test-shortcut-token" not in repr(config)
    assert "test-github-token" not in repr(config)


def test_config_reads_overrides() -> None:
    config = SyncConfig.from_env(
        {**SECRETS, "SYNC_DRY_RUN": "false", "SYNC_MAX_CREATIONS": "3", "SHORTCUT_WORKFLOW_ID": "9"}
    )

    assert (config.dry_run, config.max_creations, config.workflow_id) == (False, 3, 9)


@pytest.mark.parametrize(
    "overrides",
    [
        {"SYNC_DRY_RUN": "maybe"},
        {"SYNC_MAX_CREATIONS": "-1"},
        {"SHORTCUT_WORKFLOW_ID": "abc"},
        {"GITHUB_API_URL": "http://api.github.com"},
    ],
)
def test_config_rejects_invalid_values(overrides: dict[str, str]) -> None:
    with pytest.raises(ConfigurationError):
        SyncConfig.from_env({**SECRETS, **overrides})


def test_config_reports_a_missing_secret_by_name_only() -> None:
    with pytest.raises(MissingSecretError, match="SYNC_GITHUB_TOKEN is not set"):
        SyncConfig.from_env({"SHORTCUT_API_TOKEN": "test-shortcut-token"})


def _workflow(workflow_id: int, *, default: int, done: int | None) -> dict[str, object]:
    states: list[dict[str, object]] = [{"id": default, "type": "unstarted", "position": 1}]
    if done is not None:
        states.append({"id": done, "type": "done", "position": 3})
    return {"id": workflow_id, "default_state_id": default, "states": states}


def test_workflow_states_are_resolved_from_the_api_payload() -> None:
    states = WorkflowStates.from_workflows(workflows=[_workflow(1, default=10, done=12)], workflow_id=None)

    assert states.creation_state_id == 10
    assert states.is_done({"workflow_state_id": 12})
    assert not states.is_done({"workflow_state_id": 10})
    assert states.done_state_for({"workflow_id": 1}) == 12
    assert states.done_state_for({"workflow_id": 99}) is None


def test_several_workflows_need_an_explicit_id() -> None:
    workflows = [_workflow(1, default=10, done=12), _workflow(2, default=20, done=22)]

    with pytest.raises(ConfigurationError, match="SHORTCUT_WORKFLOW_ID"):
        WorkflowStates.from_workflows(workflows=workflows, workflow_id=None)

    states = WorkflowStates.from_workflows(workflows=workflows, workflow_id=2)
    assert states.creation_state_id == 20
    assert states.done_state_ids == frozenset({12, 22})


def test_workflow_without_done_state_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="no done-type state"):
        WorkflowStates.from_workflows(workflows=[_workflow(1, default=10, done=None)], workflow_id=None)
    with pytest.raises(ConfigurationError, match="does not match"):
        WorkflowStates.from_workflows(workflows=[_workflow(1, default=10, done=12)], workflow_id=5)


def test_repo_mapping_groups_valid_epics_only() -> None:
    epics = [
        {"id": 30, "external_id": "chrysa/alpha"},
        {"id": 10, "external_id": "chrysa/Alpha"},
        {"id": 11, "external_id": "chrysa/beta", "archived": True},
        {"id": 12, "external_id": "someone-else/gamma"},
        {"id": 13, "external_id": None},
        {"id": 14, "external_id": "chrysa/.."},
        {"id": 15, "external_id": "chrysa/delta/extra"},
    ]

    mappings = RepoMapping.from_epics(epics=epics, owner="chrysa")

    assert mappings == [RepoMapping(owner="chrysa", repo="alpha", epic_ids=(10, 30))]
    assert mappings[0].primary_epic_id == 10


def test_story_draft_payload_never_carries_labels() -> None:
    draft = StoryDraft(
        name="x" * 600,
        epic_id=1,
        story_type="bug",
        workflow_state_id=10,
        external_links=("https://github.com/chrysa/alpha/issues/1",),
        external_id="chrysa/alpha#1",
    )

    payload = draft.to_payload()

    assert len(str(payload["name"])) == STORY_NAME_MAX_CHARS
    assert payload["external_id"] == "chrysa/alpha#1"
    assert "labels" not in payload
    assert "label_ids" not in payload


def test_report_enforces_the_creation_cap() -> None:
    report = SyncReport(dry_run=False, max_creations=2)

    assert [report.reserve_creation() for _ in range(4)] == [True, True, False, False]
    assert report.count(SyncCounter.CREATIONS_DEFERRED) == 2
    assert not report.has_failures

    report.add(SyncCounter.REPO_STEP_FAILURES)
    assert report.has_failures


def test_report_marks_dry_run_actions(caplog: pytest.LogCaptureFixture) -> None:
    report = SyncReport(dry_run=True, max_creations=1)

    with caplog.at_level(logging.INFO):
        report.record(SyncCounter.STORIES_CREATED, detail="epic 1")

    assert caplog.messages == ["[dry-run] stories_created_from_issues: epic 1"]
    assert report.summary_lines()[0].startswith("mode: dry-run")
    assert "| `stories_created_from_issues` | 1 |" in report.markdown_summary()
