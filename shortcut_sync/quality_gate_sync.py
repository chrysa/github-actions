"""Step 3 — the SonarCloud quality gate drives the epic health and one tracking story."""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

from shortcut_sync.payloads import ShortcutStory
from shortcut_sync.references import STORY_TYPE_CHORE, same_link, sonar_dashboard_url, sonar_project_key
from shortcut_sync.repo_snapshot import RepoSnapshot
from shortcut_sync.story_draft import StoryDraft
from shortcut_sync.story_writer import StoryWriter
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.workflow_states import WorkflowStates

GATE_FAILING: Final = "ERROR"
GATE_PASSING: Final = "OK"
HEALTH_AT_RISK: Final = "At Risk"
HEALTH_ON_TRACK: Final = "On Track"
HEALTH_TEXTS: Final = {
    HEALTH_AT_RISK: "SonarCloud quality gate failing (daily Shortcut sync).",
    HEALTH_ON_TRACK: "SonarCloud quality gate passing (daily Shortcut sync).",
}
QUALITY_STORY_NAME: Final = "SonarCloud quality gate failing"
QUALITY_STORY_DESCRIPTION: Final = (
    "Opened by the daily Shortcut sync (chrysa/github-actions): the SonarCloud quality gate of "
    "this repository is failing. It moves to done on its own once the gate passes again."
)

GateHandler = Callable[[RepoSnapshot, str], None]


class QualityGateSync:
    """``ERROR`` → health At Risk + one open story; ``OK`` → On Track + that story done."""

    def __init__(self, *, context: SyncContext, states: WorkflowStates, writer: StoryWriter) -> None:
        self._context = context
        self._states = states
        self._writer = writer
        self._handlers: dict[str, GateHandler] = {
            GATE_FAILING: self._on_failing,
            GATE_PASSING: self._on_passing,
        }

    def sync_repo(self, snapshot: RepoSnapshot) -> None:
        """Read the gate anonymously; private, absent or unrated projects are skipped."""
        config = self._context.config
        project_key = sonar_project_key(owner=config.github_owner, repo=snapshot.mapping.repo)
        status = self._context.sonar.quality_gate_status(project_key)
        handler = self._handlers.get(status or "")
        if handler is None:
            self._context.report.add(SyncCounter.QUALITY_GATE_SKIPPED)
            return
        handler(snapshot, sonar_dashboard_url(sonar_url=config.sonar_url, project_key=project_key))

    def _ensure_health(self, *, epic_id: int, status: str) -> None:
        if self._context.shortcut.get_epic_health(epic_id) == status:
            return
        if not self._context.config.dry_run:
            self._context.shortcut.set_epic_health(epic_id=epic_id, status=status, text=HEALTH_TEXTS[status])
        self._context.report.record(SyncCounter.EPIC_HEALTH_UPDATED, detail=f"epic {epic_id}")

    def _on_failing(self, snapshot: RepoSnapshot, dashboard_url: str) -> None:
        epic_id = snapshot.mapping.primary_epic_id
        self._context.report.add(SyncCounter.QUALITY_GATE_FAILING)
        self._ensure_health(epic_id=epic_id, status=HEALTH_AT_RISK)
        if self._open_quality_stories(snapshot=snapshot, dashboard_url=dashboard_url):
            return
        if not self._context.report.reserve_creation():
            return
        draft = StoryDraft(
            name=QUALITY_STORY_NAME,
            epic_id=epic_id,
            story_type=STORY_TYPE_CHORE,
            workflow_state_id=self._states.creation_state_id,
            external_links=(dashboard_url,),
            description=QUALITY_STORY_DESCRIPTION,
        )
        self._writer.create(draft, counter=SyncCounter.QUALITY_STORIES_CREATED)

    def _on_passing(self, snapshot: RepoSnapshot, dashboard_url: str) -> None:
        self._context.report.add(SyncCounter.QUALITY_GATE_PASSING)
        self._ensure_health(epic_id=snapshot.mapping.primary_epic_id, status=HEALTH_ON_TRACK)
        for story in self._open_quality_stories(snapshot=snapshot, dashboard_url=dashboard_url):
            self._writer.complete(story, counter=SyncCounter.QUALITY_STORIES_MOVED_TO_DONE)

    def _open_quality_stories(self, *, snapshot: RepoSnapshot, dashboard_url: str) -> list[ShortcutStory]:
        return [
            story
            for story in snapshot.stories
            if not story.get("archived")
            and not self._states.is_done(story)
            and any(same_link(link, dashboard_url) for link in story.get("external_links", []))
        ]
