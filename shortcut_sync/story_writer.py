"""The only place that writes stories: creation and move-to-done, dry-run aware."""

from __future__ import annotations

import logging

from shortcut_sync.payloads import ShortcutStory
from shortcut_sync.story_draft import StoryDraft
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.workflow_states import WorkflowStates

logger = logging.getLogger(__name__)


class StoryWriter:
    def __init__(self, *, context: SyncContext, states: WorkflowStates) -> None:
        self._context = context
        self._states = states

    def complete(self, story: ShortcutStory, *, counter: SyncCounter) -> None:
        """Move a story to the done state of its workflow (planned only, in dry-run)."""
        done_state_id = self._states.done_state_for(story)
        if done_state_id is None:
            logger.warning(f"::warning::story {story.get('id')}: its workflow has no done state")
            return
        if not self._context.config.dry_run:
            self._context.shortcut.move_story(story_id=int(story["id"]), workflow_state_id=done_state_id)
        self._context.report.record(counter, detail=f"story {story.get('id')}")

    def create(self, draft: StoryDraft, *, counter: SyncCounter) -> ShortcutStory | None:
        """Create a story; returns it, or None in dry-run. The caller reserved a creation slot."""
        if self._context.config.dry_run:
            self._context.report.record(counter, detail=f"epic {draft.epic_id}")
            return None
        story = self._context.shortcut.create_story(draft)
        self._context.report.record(counter, detail=f"epic {draft.epic_id}, story {story['id']}")
        return story
