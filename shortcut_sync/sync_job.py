"""One run: read Shortcut and GitHub, close and import repo by repo, then sync epic progress."""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from typing import Final

from shortcut_sync.closed_issue_resolver import ClosedIssueResolver
from shortcut_sync.epic_progress_sync import EpicProgressSync
from shortcut_sync.errors import ShortcutSyncError
from shortcut_sync.issue_importer import IssueImporter
from shortcut_sync.payloads import GitHubRepository, ShortcutStory
from shortcut_sync.references import linked_issue_keys
from shortcut_sync.repo_mapping import RepoMapping
from shortcut_sync.repo_snapshot import RepoSnapshot
from shortcut_sync.story_writer import StoryWriter
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_counter import SyncCounter
from shortcut_sync.sync_report import SyncReport
from shortcut_sync.workflow_states import WorkflowStates

# (repository field, value that means "skip", counter) — archived repos are out of scope.
REPOSITORY_SKIP_RULES: Final = (
    ("archived", True, SyncCounter.REPOS_ARCHIVED),
    ("has_issues", False, SyncCounter.REPOS_WITHOUT_ISSUES),
)

RepoStep = Callable[[RepoSnapshot], None]

logger = logging.getLogger(__name__)


class ShortcutSyncJob:
    """Shortcut read failures abort the run (an incomplete link index could duplicate stories);
    GitHub and write failures are contained per repository, progress failures per epic or
    objective, and counted."""

    def __init__(self, *, context: SyncContext) -> None:
        self._context = context

    def run(self) -> SyncReport:
        """Execute the repository steps (closing first, then importing), then the epic and
        objective progress over the whole workspace."""
        shortcut = self._context.shortcut
        states = WorkflowStates.from_workflows(
            workflows=shortcut.list_workflows(),
            workflow_id=self._context.config.workflow_id,
        )
        epics = shortcut.list_epics()
        mappings = RepoMapping.from_epics(epics=epics, owner=self._context.config.github_owner)
        self._count_mappings(mappings)
        stories = {mapping: self._load_stories(mapping) for mapping in mappings}
        linked = linked_issue_keys(story for group in stories.values() for story in group)
        snapshots = [
            snapshot
            for mapping in mappings
            if (snapshot := self._load_snapshot(mapping=mapping, stories=stories[mapping])) is not None
        ]
        writer = StoryWriter(context=self._context, states=states)
        steps: tuple[RepoStep, ...] = (
            ClosedIssueResolver(
                context=self._context, states=states, writer=writer, snapshots=snapshots
            ).sync_repo,
            IssueImporter(context=self._context, states=states, writer=writer, linked=linked).sync_repo,
        )
        for step in steps:
            for snapshot in snapshots:
                self._run_contained(step=step, snapshot=snapshot)
        self._run_progress(EpicProgressSync(context=self._context, states=states, epics=epics))
        return self._context.report

    def _count_mappings(self, mappings: Sequence[RepoMapping]) -> None:
        report = self._context.report
        report.add(SyncCounter.REPOS_MAPPED, amount=len(mappings))
        report.add(SyncCounter.EPICS_MAPPED, amount=sum(len(mapping.epic_ids) for mapping in mappings))
        report.add(
            SyncCounter.REPOS_WITH_SEVERAL_EPICS,
            amount=sum(1 for mapping in mappings if len(mapping.epic_ids) > 1),
        )

    def _load_snapshot(
        self, *, mapping: RepoMapping, stories: tuple[ShortcutStory, ...]
    ) -> RepoSnapshot | None:
        report = self._context.report
        try:
            repository = self._context.github.get_repository(mapping.repo)
            skip = self._skip_counter(repository)
            if skip is not None:
                report.add(skip)
                return None
            issues = tuple(self._context.github.list_open_issues(mapping.repo))
        except ShortcutSyncError as error:
            report.add(SyncCounter.REPO_STEP_FAILURES)
            logger.warning(f"::warning::epic {mapping.primary_epic_id}: repository not read ({error})")
            return None
        report.add(SyncCounter.ISSUES_OPEN, amount=len(issues))
        return RepoSnapshot(mapping=mapping, stories=stories, open_issues=issues)

    def _load_stories(self, mapping: RepoMapping) -> tuple[ShortcutStory, ...]:
        return tuple(
            story
            for epic_id in mapping.epic_ids
            for story in self._context.shortcut.list_epic_stories(epic_id)
        )

    def _run_progress(self, progress: EpicProgressSync) -> None:
        try:
            progress.run()
        except ShortcutSyncError as error:
            self._context.report.add(SyncCounter.PROGRESS_STEP_FAILURES)
            logger.warning(f"::warning::epic progress step failed ({error})")

    def _run_contained(self, *, step: RepoStep, snapshot: RepoSnapshot) -> None:
        try:
            step(snapshot)
        except ShortcutSyncError as error:
            self._context.report.add(SyncCounter.REPO_STEP_FAILURES)
            logger.warning(f"::warning::epic {snapshot.mapping.primary_epic_id}: step failed ({error})")

    @staticmethod
    def _skip_counter(repository: GitHubRepository | None) -> SyncCounter | None:
        if repository is None:
            return SyncCounter.REPOS_UNREACHABLE
        for field, skip_value, counter in REPOSITORY_SKIP_RULES:
            if repository.get(field, not skip_value) == skip_value:
                return counter
        return None
