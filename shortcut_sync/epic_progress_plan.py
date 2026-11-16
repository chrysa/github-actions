"""The state move one epic needs so it follows its stories (owner rule sc-5963, reduced by sc-6014).

Only ``epic_state_id`` is ever planned. Shortcut sets the epic's own ``started_at`` /
``completed_at`` when its state changes; ``started_at_override``, ``completed_at_override``,
``planned_start_date`` and ``deadline`` stay the owner's (manual corrections only).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Final

from shortcut_sync.epic_timeline import EpicTimeline
from shortcut_sync.epic_workflow_states import EPIC_DONE, EPIC_STARTED, EPIC_UNSTARTED, EpicWorkflowStates
from shortcut_sync.payloads import ShortcutEpic
from shortcut_sync.sync_counter import SyncCounter

STATE_FIELD: Final = "epic_state_id"
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
    if timeline.started or current == EPIC_DONE:
        return EPIC_STARTED
    return current


@dataclass(frozen=True, slots=True)
class EpicProgressPlan:
    """``changes`` is the ``PUT /epics/{id}`` body; ``counter`` is None when the epic stays put."""

    changes: Mapping[str, object] = field(default_factory=dict)
    counter: SyncCounter | None = None
    started: bool = False

    @classmethod
    def for_epic(
        cls, *, epic: ShortcutEpic, timeline: EpicTimeline, epic_states: EpicWorkflowStates
    ) -> EpicProgressPlan:
        """Plan the state move; an epic in an unknown state is left alone."""
        current = epic_states.type_of(epic)
        if current is None:
            return cls()
        target = _target_type(current=current, timeline=timeline)
        started = target != EPIC_UNSTARTED
        counter = TRANSITION_COUNTERS.get((current, target))
        if counter is None:
            return cls(started=started)
        return cls(changes={STATE_FIELD: epic_states.state_id_for(target)}, counter=counter, started=started)
