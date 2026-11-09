"""Step 5 — epic state and dates follow the stories, then objectives follow the epics (sc-5963).

Runs after the repository steps, over every non-archived epic of the workspace (mapped or
not) that holds at least one story. Stories are read again so this run's writes count.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from shortcut_sync.epic_progress_plan import EpicProgressPlan
from shortcut_sync.epic_timeline import EpicTimeline
from shortcut_sync.epic_workflow_states import EpicWorkflowStates
from shortcut_sync.errors import ShortcutSyncError
from shortcut_sync.objective_progress_sync import ObjectiveProgressSync
from shortcut_sync.payloads import ShortcutEpic
from shortcut_sync.progress_writer import ProgressWriter
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.workflow_states import WorkflowStates

logger = logging.getLogger(__name__)


def _may_hold_stories(epic: ShortcutEpic) -> bool:
    """Non-archived, and its stats (when present) do not say it is empty."""
    stats = epic.get("stats")
    empty = stats is not None and stats.get("num_stories_total") == 0
    return not epic.get("archived") and isinstance(epic.get("id"), int) and not empty


class EpicProgressSync:
    """Epic failures are contained per epic and counted; dates set by hand are never overwritten."""

    def __init__(
        self, *, context: SyncContext, states: WorkflowStates, epics: Sequence[ShortcutEpic]
    ) -> None:
        self._context = context
        self._states = states
        self._epics = epics
        self._writer = ProgressWriter(context=context)

    def run(self) -> None:
        """Sync every candidate epic, then the objectives of the epics that started."""
        epic_states = EpicWorkflowStates.from_workflow(self._context.shortcut.get_epic_workflow())
        starts: dict[int, str | None] = {}
        for epic in self._epics:
            if _may_hold_stories(epic):
                self._sync_contained(epic=epic, epic_states=epic_states, starts=starts)
        objectives = ObjectiveProgressSync(context=self._context, writer=self._writer)
        objectives.run(epics=self._epics, starts=starts)

    def _sync_contained(
        self, *, epic: ShortcutEpic, epic_states: EpicWorkflowStates, starts: dict[int, str | None]
    ) -> None:
        try:
            self._sync_epic(epic=epic, epic_states=epic_states, starts=starts)
        except ShortcutSyncError as error:
            self._context.report.add(SyncCounter.PROGRESS_STEP_FAILURES)
            logger.warning(f"::warning::epic {epic.get('id')}: progress not synced ({error})")

    def _sync_epic(
        self, *, epic: ShortcutEpic, epic_states: EpicWorkflowStates, starts: dict[int, str | None]
    ) -> None:
        epic_id = int(epic["id"])
        timeline = EpicTimeline.from_stories(
            stories=self._context.shortcut.list_epic_stories(epic_id), states=self._states
        )
        if not timeline.story_count:
            return
        report = self._context.report
        report.add(SyncCounter.EPICS_CHECKED)
        plan = EpicProgressPlan.for_epic(epic=epic, timeline=timeline, epic_states=epic_states)
        report.add(SyncCounter.MANUAL_DATES_KEPT, amount=plan.manual_dates_kept)
        written = not plan.changes or self._writer.update_epic(
            epic_id=epic_id, changes=plan.changes, counter=plan.counter
        )
        if plan.started and written:
            starts[epic_id] = plan.start
