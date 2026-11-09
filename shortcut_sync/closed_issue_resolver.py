"""Step 2 — a story created by the sync moves to done once its GitHub issue is closed."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from shortcut_sync.issue_key import IssueKey
from shortcut_sync.payloads import ShortcutStory
from shortcut_sync.repo_snapshot import RepoSnapshot
from shortcut_sync.story_writer import StoryWriter
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.workflow_states import WorkflowStates

CLOSED_STATE: Final = "closed"


class ClosedIssueResolver:
    """Only stories carrying the sync marker (``external_id`` = ``owner/repo#n``) are touched."""

    def __init__(
        self,
        *,
        context: SyncContext,
        states: WorkflowStates,
        writer: StoryWriter,
        snapshots: Sequence[RepoSnapshot],
    ) -> None:
        self._context = context
        self._states = states
        self._writer = writer
        self._open_keys = frozenset(key for snapshot in snapshots for key in snapshot.open_issue_keys)
        self._repos = frozenset(snapshot.mapping.repo.lower() for snapshot in snapshots)

    def sync_repo(self, snapshot: RepoSnapshot) -> None:
        """Close the stories of the repository's epics whose issue is closed."""
        for story in snapshot.stories:
            self._sync_story(story)

    def _is_candidate(self, *, story: ShortcutStory, key: IssueKey) -> bool:
        return (
            key.owner == self._context.config.github_owner.lower()
            and key.repo in self._repos
            and key not in self._open_keys
            and not story.get("archived")
            and not self._states.is_done(story)
        )

    def _sync_story(self, story: ShortcutStory) -> None:
        key = IssueKey.from_external_id(story.get("external_id"))
        if key is None or not self._is_candidate(story=story, key=key):
            return
        issue = self._context.github.get_issue(repo=key.repo, number=key.number)
        if issue is None or issue.get("state") != CLOSED_STATE:
            return
        self._writer.complete(story, counter=SyncCounter.STORIES_MOVED_TO_DONE)
