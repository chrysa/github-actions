"""Step 4 — the GuardRails scan of the default branch drives one tracking bug story (sc-5967).

GuardRails reports through a GitHub check run named ``guardrails/scan``. Its output carries
no severity (title only, empty summary, no annotation), and GuardRails fails the check only
for findings above the threshold set in its own configuration: the rule therefore keys on
the ``failure`` conclusion alone.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

from shortcut_sync.payloads import GitHubCheckRun, ShortcutStory
from shortcut_sync.references import STORY_TYPE_BUG, guardrails_marker
from shortcut_sync.repo_snapshot import RepoSnapshot
from shortcut_sync.story_draft import StoryDraft
from shortcut_sync.story_writer import StoryWriter
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.workflow_states import WorkflowStates

GUARDRAILS_CHECK_NAME: Final = "guardrails/scan"
GUARDRAILS_APP_SLUG: Final = "guardrails"
CONCLUSION_FAILURE: Final = "failure"
CONCLUSION_SUCCESS: Final = "success"
CONCLUSION_NEUTRAL: Final = "neutral"
GITHUB_RUN_URL_PREFIX: Final = "https://github.com/"
GUARDRAILS_STORY_NAME: Final = "GuardRails : failles hautes sur la branche par défaut"
GUARDRAILS_STORY_DESCRIPTION: Final = (
    "Opened by the daily Shortcut sync (chrysa/github-actions): the latest GuardRails scan of "
    "the default branch is failing. It moves to done on its own once the scan passes again."
)

ScanHandler = Callable[[RepoSnapshot, GitHubCheckRun], None]


class GuardRailsSync:
    """``failure`` → exactly one open bug story (marker ``owner/repo#guardrails``);
    ``success`` / ``neutral`` → that story done; no run or another conclusion → skipped."""

    def __init__(self, *, context: SyncContext, states: WorkflowStates, writer: StoryWriter) -> None:
        self._context = context
        self._states = states
        self._writer = writer
        self._handlers: dict[str, ScanHandler] = {
            CONCLUSION_FAILURE: self._on_failing,
            CONCLUSION_SUCCESS: self._on_passing,
            CONCLUSION_NEUTRAL: self._on_passing,
        }

    def sync_repo(self, snapshot: RepoSnapshot) -> None:
        """Read the latest completed GuardRails run on the default branch head."""
        run = self._latest_run(snapshot)
        handler = self._handlers.get(str(run.get("conclusion") or "")) if run is not None else None
        if run is None or handler is None:
            self._context.report.add(SyncCounter.GUARDRAILS_SKIPPED)
            return
        handler(snapshot, run)

    def _latest_run(self, snapshot: RepoSnapshot) -> GitHubCheckRun | None:
        if not snapshot.default_branch:
            return None
        return self._context.github.latest_check_run(
            repo=snapshot.mapping.repo,
            ref=snapshot.default_branch,
            check_name=GUARDRAILS_CHECK_NAME,
            app_slug=GUARDRAILS_APP_SLUG,
        )

    def _on_failing(self, snapshot: RepoSnapshot, run: GitHubCheckRun) -> None:
        self._context.report.add(SyncCounter.GUARDRAILS_FAILING)
        if self._open_stories(snapshot) or not self._context.report.reserve_creation():
            return
        mapping = snapshot.mapping
        run_url = str(run.get("html_url") or "")
        draft = StoryDraft(
            name=GUARDRAILS_STORY_NAME,
            epic_id=mapping.primary_epic_id,
            story_type=STORY_TYPE_BUG,
            workflow_state_id=self._states.creation_state_id,
            external_links=(run_url,) if run_url.startswith(GITHUB_RUN_URL_PREFIX) else (),
            description=GUARDRAILS_STORY_DESCRIPTION,
            external_id=guardrails_marker(owner=mapping.owner, repo=mapping.repo),
        )
        self._writer.create(draft, counter=SyncCounter.GUARDRAILS_STORIES_CREATED)

    def _on_passing(self, snapshot: RepoSnapshot, _run: GitHubCheckRun) -> None:
        self._context.report.add(SyncCounter.GUARDRAILS_PASSING)
        for story in self._open_stories(snapshot):
            self._writer.complete(story, counter=SyncCounter.GUARDRAILS_STORIES_MOVED_TO_DONE)

    def _open_stories(self, snapshot: RepoSnapshot) -> list[ShortcutStory]:
        marker = guardrails_marker(owner=snapshot.mapping.owner, repo=snapshot.mapping.repo)
        return [
            story
            for story in snapshot.stories
            if not story.get("archived")
            and not self._states.is_done(story)
            and str(story.get("external_id") or "").lower() == marker
        ]
