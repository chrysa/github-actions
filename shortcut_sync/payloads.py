"""Typed shapes of the API payloads the sync reads (only the fields it uses).

Type declarations only — no behaviour — so they share one module.
"""

from __future__ import annotations

from typing import TypedDict


class GitHubLabel(TypedDict, total=False):
    name: str


class GitHubIssue(TypedDict, total=False):
    number: int
    title: str
    body: str | None
    html_url: str
    state: str
    comments: int
    labels: list[GitHubLabel]
    pull_request: dict[str, object]


class GitHubRepository(TypedDict, total=False):
    archived: bool
    has_issues: bool
    default_branch: str


class GitHubApp(TypedDict, total=False):
    slug: str


class GitHubCheckRun(TypedDict, total=False):
    id: int
    name: str
    status: str
    conclusion: str | None
    html_url: str
    app: GitHubApp


class ShortcutEpicStats(TypedDict, total=False):
    num_stories_total: int


class ShortcutEpic(TypedDict, total=False):
    id: int
    archived: bool
    external_id: str | None
    epic_state_id: int
    started_at: str | None
    started_at_override: str | None
    completed_at_override: str | None
    objective_ids: list[int]
    stats: ShortcutEpicStats


class ShortcutEpicState(TypedDict, total=False):
    id: int
    type: str
    position: int


class ShortcutEpicWorkflow(TypedDict, total=False):
    id: int
    epic_states: list[ShortcutEpicState]


class ShortcutObjective(TypedDict, total=False):
    id: int
    archived: bool
    state: str
    started_at_override: str | None


class ShortcutStory(TypedDict, total=False):
    id: int
    app_url: str
    archived: bool
    external_id: str | None
    external_links: list[str]
    workflow_id: int
    workflow_state_id: int
    started_at: str | None
    started_at_override: str | None
    completed_at: str | None
    completed_at_override: str | None


class ShortcutWorkflowState(TypedDict, total=False):
    id: int
    type: str
    position: int


class ShortcutWorkflow(TypedDict, total=False):
    id: int
    default_state_id: int
    states: list[ShortcutWorkflowState]
