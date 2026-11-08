"""Step 1 — open GitHub issues without a Shortcut link become stories in the mapped epic."""

from __future__ import annotations

import logging
from typing import Final

from shortcut_sync.errors import ApiError
from shortcut_sync.issue_key import IssueKey
from shortcut_sync.payloads import GitHubIssue
from shortcut_sync.references import has_shortcut_reference, issue_comment, story_type_for
from shortcut_sync.repo_snapshot import RepoSnapshot
from shortcut_sync.story_draft import StoryDraft
from shortcut_sync.story_writer import StoryWriter
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.workflow_states import WorkflowStates

IMPORT_DESCRIPTION: Final = "Imported by the daily Shortcut sync (chrysa/github-actions) from {url}"

logger = logging.getLogger(__name__)


class IssueImporter:
    """Idempotent: an issue is linked once its body, comments or a story reference it."""

    def __init__(
        self,
        *,
        context: SyncContext,
        states: WorkflowStates,
        writer: StoryWriter,
        linked: set[IssueKey],
    ) -> None:
        self._context = context
        self._states = states
        self._writer = writer
        self._linked = linked

    def sync_repo(self, snapshot: RepoSnapshot) -> None:
        """Import every unlinked open issue of the repository, within the creation cap."""
        for issue in snapshot.open_issues:
            self._sync_issue(snapshot=snapshot, issue=issue)

    def _comment(self, *, snapshot: RepoSnapshot, key: IssueKey, story_id: int, app_url: str) -> None:
        try:
            self._context.github.create_issue_comment(
                repo=snapshot.mapping.repo,
                number=key.number,
                body=issue_comment(story_id=story_id, app_url=app_url),
            )
        except ApiError as error:
            # The story already carries the issue link, so the next run will not duplicate it.
            self._context.report.add(SyncCounter.ISSUE_COMMENTS_FAILED)
            logger.warning(f"::warning::story {story_id}: issue comment not posted ({error.reason})")
            return
        self._context.report.add(SyncCounter.ISSUE_COMMENTS_POSTED)

    def _draft(self, *, snapshot: RepoSnapshot, issue: GitHubIssue, key: IssueKey) -> StoryDraft:
        url = str(issue.get("html_url", ""))
        return StoryDraft(
            name=str(issue.get("title") or f"GitHub issue #{key.number}"),
            epic_id=snapshot.mapping.primary_epic_id,
            story_type=story_type_for(issue.get("labels", [])),
            workflow_state_id=self._states.creation_state_id,
            external_links=(url,),
            description=IMPORT_DESCRIPTION.format(url=url),
            external_id=key.external_id,
        )

    def _is_linked(self, *, snapshot: RepoSnapshot, issue: GitHubIssue, key: IssueKey) -> bool:
        if key in self._linked or has_shortcut_reference(issue.get("body")):
            return True
        if not issue.get("comments"):
            return False
        bodies = self._context.github.list_issue_comment_bodies(repo=snapshot.mapping.repo, number=key.number)
        return any(has_shortcut_reference(body) for body in bodies)

    def _sync_issue(self, *, snapshot: RepoSnapshot, issue: GitHubIssue) -> None:
        key = IssueKey.from_url(issue.get("html_url"))
        if key is None:
            return
        report = self._context.report
        if self._is_linked(snapshot=snapshot, issue=issue, key=key):
            report.add(SyncCounter.ISSUES_ALREADY_LINKED)
            return
        if not report.reserve_creation():
            return
        story = self._writer.create(
            self._draft(snapshot=snapshot, issue=issue, key=key), counter=SyncCounter.STORIES_CREATED
        )
        self._linked.add(key)
        if story is None:
            report.add(SyncCounter.ISSUE_COMMENTS_POSTED)
            return
        self._comment(
            snapshot=snapshot, key=key, story_id=int(story["id"]), app_url=str(story.get("app_url", ""))
        )
