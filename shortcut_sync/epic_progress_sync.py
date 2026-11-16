"""Step 3 — epic states follow the stories, then objectives follow the epics (sc-5963, sc-6014).

Runs after the repository steps, over every non-archived epic of the workspace (mapped or
not) that holds at least one story. Stories are read again so this run's writes count.
Only states are written: Shortcut stamps the native start and completion dates itself.
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
    """Epic failures are contained per epic and counted; no date field is ever written."""

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
        started: set[int] = set()
        for epic in self._epics:
            if _may_hold_stories(epic):
                self._sync_contained(epic=epic, epic_states=epic_states, started=started)
        objectives = ObjectiveProgressSync(context=self._context, writer=self._writer)
        objectives.run(epics=self._epics, started=started)

    def _sync_contained(
        self, *, epic: ShortcutEpic, epic_states: EpicWorkflowStates, started: set[int]
    ) -> None:
        try:
            self._sync_epic(epic=epic, epic_states=epic_states, started=started)
        except ShortcutSyncError as error:
            self._context.report.add(SyncCounter.PROGRESS_STEP_FAILURES)
            logger.warning(f"::warning::epic {epic.get('id')}: progress not synced ({error})")

    def _sync_epic(self, *, epic: ShortcutEpic, epic_states: EpicWorkflowStates, started: set[int]) -> None:
        epic_id = int(epic["id"])
        timeline = EpicTimeline.from_stories(
            stories=self._context.shortcut.list_epic_stories(epic_id), states=self._states
        )
        if not timeline.story_count:
            return
        self._context.report.add(SyncCounter.EPICS_CHECKED)
        plan = EpicProgressPlan.for_epic(epic=epic, timeline=timeline, epic_states=epic_states)
        written = plan.counter is None or self._writer.update_epic(
            epic_id=epic_id, changes=plan.changes, counter=plan.counter
        )
        if plan.started and written:
            started.add(epic_id)
