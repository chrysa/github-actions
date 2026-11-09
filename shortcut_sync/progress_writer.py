"""The only place that writes epics and objectives: dry-run aware, within the update cap."""

from __future__ import annotations

from collections.abc import Mapping

from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter


class ProgressWriter:
    """Each update takes one slot of ``SYNC_MAX_PROGRESS_UPDATES``; logs carry the id only."""

    def __init__(self, *, context: SyncContext) -> None:
        self._context = context

    def update_epic(self, *, epic_id: int, changes: Mapping[str, object], counter: SyncCounter) -> bool:
        """Write (or, in dry-run, plan) one epic update; False when the cap deferred it."""
        if not self._context.report.reserve_progress_update():
            return False
        if not self._context.config.dry_run:
            self._context.shortcut.update_epic(epic_id=epic_id, changes=changes)
        self._context.report.record(counter, detail=f"epic {epic_id}")
        return True

    def update_objective(
        self, *, objective_id: int, changes: Mapping[str, object], counter: SyncCounter
    ) -> bool:
        """Write (or, in dry-run, plan) one objective update; False when the cap deferred it."""
        if not self._context.report.reserve_progress_update():
            return False
        if not self._context.config.dry_run:
            self._context.shortcut.update_objective(objective_id=objective_id, changes=changes)
        self._context.report.record(counter, detail=f"objective {objective_id}")
        return True
