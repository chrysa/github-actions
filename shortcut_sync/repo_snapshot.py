"""What the run read for one reachable repository."""

from __future__ import annotations

from dataclasses import dataclass

from shortcut_sync.issue_key import IssueKey
from shortcut_sync.payloads import GitHubIssue, ShortcutStory
from shortcut_sync.repo_mapping import RepoMapping


@dataclass(frozen=True, slots=True)
class RepoSnapshot:
    mapping: RepoMapping
    stories: tuple[ShortcutStory, ...]
    open_issues: tuple[GitHubIssue, ...]

    @property
    def open_issue_keys(self) -> frozenset[IssueKey]:
        """Keys of the open issues read this run."""
        keys = (IssueKey.from_url(issue.get("html_url")) for issue in self.open_issues)
        return frozenset(key for key in keys if key is not None)
