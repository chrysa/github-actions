"""Workflow states resolved from ``GET /api/v3/workflows`` — no state id is hardcoded."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from shortcut_sync.errors import ConfigurationError
from shortcut_sync.payloads import ShortcutStory, ShortcutWorkflow, ShortcutWorkflowState

DONE_STATE_TYPE: Final = "done"


def _state_position(state: ShortcutWorkflowState) -> int:
    return int(state.get("position", 0))


def _first_done_state(workflow: ShortcutWorkflow) -> int | None:
    done_states = [state for state in workflow.get("states", []) if state.get("type") == DONE_STATE_TYPE]
    return int(min(done_states, key=_state_position)["id"]) if done_states else None


@dataclass(frozen=True, slots=True)
class WorkflowStates:
    """Where new stories start, and which states count as done (per workflow)."""

    creation_state_id: int
    done_state_ids: frozenset[int]
    done_state_by_workflow: Mapping[int, int]

    @classmethod
    def from_workflows(
        cls, *, workflows: Sequence[ShortcutWorkflow], workflow_id: int | None
    ) -> WorkflowStates:
        """Pick the creation workflow (explicit id, or the only one) and index the done states."""
        chosen = cls._choose(workflows=workflows, workflow_id=workflow_id)
        done_by_workflow = {
            int(workflow["id"]): done_id
            for workflow in workflows
            if (done_id := _first_done_state(workflow)) is not None
        }
        if int(chosen["id"]) not in done_by_workflow:
            raise ConfigurationError("the Shortcut workflow has no done-type state")
        done_ids = frozenset(
            int(state["id"])
            for workflow in workflows
            for state in workflow.get("states", [])
            if state.get("type") == DONE_STATE_TYPE
        )
        return cls(
            creation_state_id=int(chosen["default_state_id"]),
            done_state_ids=done_ids,
            done_state_by_workflow=done_by_workflow,
        )

    @staticmethod
    def _choose(*, workflows: Sequence[ShortcutWorkflow], workflow_id: int | None) -> ShortcutWorkflow:
        if workflow_id is not None:
            matches = [workflow for workflow in workflows if workflow.get("id") == workflow_id]
            if not matches:
                raise ConfigurationError("SHORTCUT_WORKFLOW_ID does not match any Shortcut workflow")
            return matches[0]
        if len(workflows) != 1:
            raise ConfigurationError("several (or no) Shortcut workflows exist: set SHORTCUT_WORKFLOW_ID")
        return workflows[0]

    def done_state_for(self, story: ShortcutStory) -> int | None:
        """Done state of the story's own workflow."""
        return self.done_state_by_workflow.get(int(story.get("workflow_id", 0)))

    def is_done(self, story: ShortcutStory) -> bool:
        """True when the story sits in any done-type state."""
        return story.get("workflow_state_id") in self.done_state_ids
