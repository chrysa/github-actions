"""Objectives start with their first started epic; they are never set to done (sc-5963).

Objectives have no workflow endpoint: their states are the fixed enum of the API
(``UpdateObjective.state`` in the v3 swagger: ``to do`` / ``in progress`` / ``done``).
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Final

from shortcut_sync.errors import ShortcutSyncError
from shortcut_sync.payloads import ShortcutEpic, ShortcutObjective
from shortcut_sync.progress_writer import ProgressWriter
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.timestamps import earliest, plan_override

OBJECTIVE_TO_DO: Final = "to do"
OBJECTIVE_IN_PROGRESS: Final = "in progress"
STATE_FIELD: Final = "state"
STARTED_OVERRIDE: Final = "started_at_override"

logger = logging.getLogger(__name__)


class ObjectiveProgressSync:
    """A ``to do`` objective moves to ``in progress``; its start = the earliest epic start."""

    def __init__(self, *, context: SyncContext, writer: ProgressWriter) -> None:
        self._context = context
        self._writer = writer

    def run(self, *, epics: Sequence[ShortcutEpic], starts: Mapping[int, str | None]) -> None:
        """``starts`` maps every started epic id to its start (None when it has no date)."""
        started = self._starts_by_objective(epics=epics, starts=starts)
        if not started:
            return
        for objective in self._context.shortcut.list_objectives():
            objective_id = objective.get("id")
            if isinstance(objective_id, int) and objective_id in started:
                self._sync_contained(objective=objective, starts=started[objective_id])

    def _sync_contained(self, *, objective: ShortcutObjective, starts: Sequence[str | None]) -> None:
        try:
            self._sync_objective(objective=objective, starts=starts)
        except ShortcutSyncError as error:
            self._context.report.add(SyncCounter.PROGRESS_STEP_FAILURES)
            logger.warning(f"::warning::objective {objective.get('id')}: progress not synced ({error})")

    def _sync_objective(self, *, objective: ShortcutObjective, starts: Sequence[str | None]) -> None:
        state = objective.get("state")
        if objective.get("archived") or state not in (OBJECTIVE_TO_DO, OBJECTIVE_IN_PROGRESS):
            return
        changes: dict[str, object] = {}
        if state == OBJECTIVE_TO_DO:
            changes[STATE_FIELD] = OBJECTIVE_IN_PROGRESS
        if plan_override(
            changes,
            field=STARTED_OVERRIDE,
            current=objective.get(STARTED_OVERRIDE),
            computed=earliest(starts),
        ):
            self._context.report.add(SyncCounter.MANUAL_DATES_KEPT)
        if not changes:
            return
        counter = SyncCounter.OBJECTIVE_DATES_SET
        if STATE_FIELD in changes:
            counter = SyncCounter.OBJECTIVES_MOVED_TO_STARTED
        self._writer.update_objective(objective_id=int(objective["id"]), changes=changes, counter=counter)

    @staticmethod
    def _starts_by_objective(
        *, epics: Sequence[ShortcutEpic], starts: Mapping[int, str | None]
    ) -> dict[int, list[str | None]]:
        grouped: dict[int, list[str | None]] = {}
        for epic in epics:
            epic_id = epic.get("id")
            if not isinstance(epic_id, int) or epic_id not in starts:
                continue
            for objective_id in epic.get("objective_ids", []):
                grouped.setdefault(objective_id, []).append(starts[epic_id])
        return grouped
