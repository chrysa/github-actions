"""Objectives start with their first started epic; they are never set to done (sc-5963).

Objectives have no workflow endpoint: their states are the fixed enum of the API
(``UpdateObjective.state`` in the v3 swagger: ``to do`` / ``in progress`` / ``done``).
Only the state is written: Shortcut stamps the objective's start date itself (sc-6014).
"""

from __future__ import annotations

import logging
from collections.abc import Sequence, Set
from typing import Final

from shortcut_sync.errors import ShortcutSyncError
from shortcut_sync.payloads import ShortcutEpic, ShortcutObjective
from shortcut_sync.progress_writer import ProgressWriter
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter

OBJECTIVE_TO_DO: Final = "to do"
OBJECTIVE_IN_PROGRESS: Final = "in progress"
STATE_FIELD: Final = "state"

logger = logging.getLogger(__name__)


class ObjectiveProgressSync:
    """A ``to do`` objective with a started epic moves to ``in progress``; nothing else is touched."""

    def __init__(self, *, context: SyncContext, writer: ProgressWriter) -> None:
        self._context = context
        self._writer = writer

    def run(self, *, epics: Sequence[ShortcutEpic], started: Set[int]) -> None:
        """``started`` holds the id of every epic that has started (or is done)."""
        objective_ids = self._objectives_of(epics=epics, started=started)
        if not objective_ids:
            return
        for objective in self._context.shortcut.list_objectives():
            objective_id = objective.get("id")
            if isinstance(objective_id, int) and objective_id in objective_ids:
                self._sync_contained(objective)

    def _sync_contained(self, objective: ShortcutObjective) -> None:
        try:
            self._sync_objective(objective)
        except ShortcutSyncError as error:
            self._context.report.add(SyncCounter.PROGRESS_STEP_FAILURES)
            logger.warning(f"::warning::objective {objective.get('id')}: progress not synced ({error})")

    def _sync_objective(self, objective: ShortcutObjective) -> None:
        if objective.get("archived") or objective.get("state") != OBJECTIVE_TO_DO:
            return
        self._writer.update_objective(
            objective_id=int(objective["id"]),
            changes={STATE_FIELD: OBJECTIVE_IN_PROGRESS},
            counter=SyncCounter.OBJECTIVES_MOVED_TO_STARTED,
        )

    @staticmethod
    def _objectives_of(*, epics: Sequence[ShortcutEpic], started: Set[int]) -> frozenset[int]:
        return frozenset(
            objective_id
            for epic in epics
            if epic.get("id") in started
            for objective_id in epic.get("objective_ids", [])
        )
