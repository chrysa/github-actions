"""What the stories of one epic say: when work started, and whether (and when) it all ended."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from shortcut_sync.payloads import ShortcutStory
from shortcut_sync.timestamps import earliest, latest
from shortcut_sync.workflow_states import WorkflowStates


@dataclass(frozen=True, slots=True)
class EpicTimeline:
    """Archived stories are ignored. A story's date is its override, else the API date."""

    story_count: int
    start: str | None
    all_done: bool
    completion: str | None

    @classmethod
    def from_stories(cls, *, stories: Iterable[ShortcutStory], states: WorkflowStates) -> EpicTimeline:
        """Earliest story start; latest story completion once every story is done."""
        live = [story for story in stories if not story.get("archived")]
        all_done = bool(live) and all(states.is_done(story) for story in live)
        start = earliest(story.get("started_at_override") or story.get("started_at") for story in live)
        completion = (
            latest(story.get("completed_at_override") or story.get("completed_at") for story in live)
            if all_done
            else None
        )
        return cls(story_count=len(live), start=start, all_done=all_done, completion=completion)
