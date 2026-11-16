"""What the stories of one epic say: whether work has started, and whether it all ended."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from shortcut_sync.payloads import ShortcutStory
from shortcut_sync.workflow_states import WorkflowStates


@dataclass(frozen=True, slots=True)
class EpicTimeline:
    """Archived stories are ignored. A story has started once Shortcut set its ``started_at``."""

    story_count: int
    started: bool
    all_done: bool

    @classmethod
    def from_stories(cls, *, stories: Iterable[ShortcutStory], states: WorkflowStates) -> EpicTimeline:
        """Whether any live story has started, and whether every live story is done."""
        live = [story for story in stories if not story.get("archived")]
        return cls(
            story_count=len(live),
            started=any(story.get("started_at") for story in live),
            all_done=bool(live) and all(states.is_done(story) for story in live),
        )
