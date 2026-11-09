"""The update one epic needs so its state and dates follow its stories (owner rule sc-5963).

Only ``epic_state_id``, ``started_at_override`` and ``completed_at_override`` are ever
planned: ``planned_start_date`` and ``deadline`` stay the owner's.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Final

from shortcut_sync.epic_timeline import EpicTimeline
from shortcut_sync.epic_workflow_states import EPIC_DONE, EPIC_STARTED, EPIC_UNSTARTED, EpicWorkflowStates
from shortcut_sync.payloads import ShortcutEpic
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.timestamps import plan_override

STATE_FIELD: Final = "epic_state_id"
STARTED_OVERRIDE: Final = "started_at_override"
COMPLETED_OVERRIDE: Final = "completed_at_override"
TRANSITION_COUNTERS: Final[Mapping[tuple[str, str], SyncCounter]] = {
    (EPIC_UNSTARTED, EPIC_STARTED): SyncCounter.EPICS_MOVED_TO_STARTED,
    (EPIC_UNSTARTED, EPIC_DONE): SyncCounter.EPICS_MOVED_TO_DONE,
    (EPIC_STARTED, EPIC_DONE): SyncCounter.EPICS_MOVED_TO_DONE,
    (EPIC_DONE, EPIC_STARTED): SyncCounter.EPICS_MOVED_BACK_TO_STARTED,
}


def _target_type(*, current: str, timeline: EpicTimeline) -> str:
    """All stories done → done; a story started, or a done epic reopened → started."""
    if timeline.all_done:
        return EPIC_DONE
    if timeline.start is not None or current == EPIC_DONE:
        return EPIC_STARTED
    return current


@dataclass(frozen=True, slots=True)
class EpicProgressPlan:
    """``changes`` is the ``PUT /epics/{id}`` body (empty → nothing to write)."""

    changes: Mapping[str, object] = field(default_factory=dict)
    counter: SyncCounter = SyncCounter.EPIC_DATES_SET
    manual_dates_kept: int = 0
    started: bool = False
    start: str | None = None

    @classmethod
    def for_epic(
        cls, *, epic: ShortcutEpic, timeline: EpicTimeline, epic_states: EpicWorkflowStates
    ) -> EpicProgressPlan:
        """Plan the state move and the date overrides; an epic in an unknown state is left alone."""
        current = epic_states.type_of(epic)
        if current is None:
            return cls()
        target = _target_type(current=current, timeline=timeline)
        changes: dict[str, object] = {}
        if target != current:
            changes[STATE_FIELD] = epic_states.state_id_for(target)
        started = target != EPIC_UNSTARTED
        kept = 0
        if started and plan_override(
            changes, field=STARTED_OVERRIDE, current=epic.get(STARTED_OVERRIDE), computed=timeline.start
        ):
            kept += 1
        if target == EPIC_DONE and plan_override(
            changes,
            field=COMPLETED_OVERRIDE,
            current=epic.get(COMPLETED_OVERRIDE),
            computed=timeline.completion,
        ):
            kept += 1
        if current == EPIC_DONE and target != EPIC_DONE and epic.get(COMPLETED_OVERRIDE):
            changes[COMPLETED_OVERRIDE] = None
        start = (epic.get(STARTED_OVERRIDE) or timeline.start or epic.get("started_at")) if started else None
        return cls(
            changes=changes,
            counter=TRANSITION_COUNTERS.get((current, target), SyncCounter.EPIC_DATES_SET),
            manual_dates_kept=kept,
            started=started,
            start=start,
        )
