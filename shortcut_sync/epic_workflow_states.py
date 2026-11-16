"""Epic states resolved from ``GET /api/v3/epic-workflow`` — no state id is hardcoded."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from shortcut_sync.errors import ConfigurationError
from shortcut_sync.payloads import ShortcutEpic, ShortcutEpicState, ShortcutEpicWorkflow

EPIC_UNSTARTED: Final = "unstarted"
EPIC_STARTED: Final = "started"
EPIC_DONE: Final = "done"


def _state_position(state: ShortcutEpicState) -> int:
    return int(state.get("position", 0))


def _first_state_of_type(states: Sequence[ShortcutEpicState], state_type: str) -> int | None:
    matching = [
        state
        for state in states
        if str(state.get("type", "")).lower() == state_type and isinstance(state.get("id"), int)
    ]
    return int(min(matching, key=_state_position)["id"]) if matching else None


@dataclass(frozen=True, slots=True)
class EpicWorkflowStates:
    """The type of every epic state, and the first started / done state (leftmost)."""

    state_ids: Mapping[str, int]
    type_by_id: Mapping[int, str]

    @classmethod
    def from_workflow(cls, workflow: ShortcutEpicWorkflow) -> EpicWorkflowStates:
        """Index the workspace epic workflow; it must hold a started and a done state."""
        states = workflow.get("epic_states", [])
        state_ids = {
            state_type: state_id
            for state_type in (EPIC_STARTED, EPIC_DONE)
            if (state_id := _first_state_of_type(states, state_type)) is not None
        }
        if len(state_ids) != len((EPIC_STARTED, EPIC_DONE)):
            raise ConfigurationError("the Shortcut epic workflow has no started or no done state")
        type_by_id = {
            int(state["id"]): str(state.get("type", "")).lower()
            for state in states
            if isinstance(state.get("id"), int)
        }
        return cls(state_ids=state_ids, type_by_id=type_by_id)

    def state_id_for(self, state_type: str) -> int:
        """Target state of a move (``started`` or ``done``)."""
        return self.state_ids[state_type]

    def type_of(self, epic: ShortcutEpic) -> str | None:
        """``unstarted`` / ``started`` / ``done``, or None when the state is unknown."""
        state_id = epic.get("epic_state_id")
        return self.type_by_id.get(state_id) if isinstance(state_id, int) else None
