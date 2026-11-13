"""Names of the counters the job reports. Logs carry only these counts and numeric ids."""

from __future__ import annotations

from enum import StrEnum


class SyncCounter(StrEnum):
    EPICS_MAPPED = "epics_mapped"
    REPOS_MAPPED = "repos_mapped"
    REPOS_WITH_SEVERAL_EPICS = "repos_with_several_epics"
    REPOS_UNREACHABLE = "repos_unreachable"
    REPOS_ARCHIVED = "repos_archived"
    REPOS_WITHOUT_ISSUES = "repos_without_issues"
    ISSUES_OPEN = "issues_open"
    ISSUES_ALREADY_LINKED = "issues_already_linked"
    STORIES_CREATED = "stories_created_from_issues"
    ISSUE_COMMENTS_POSTED = "issue_comments_posted"
    STORIES_MOVED_TO_DONE = "stories_moved_to_done"
    EPICS_CHECKED = "epics_checked"
    EPICS_MOVED_TO_STARTED = "epics_moved_to_started"
    EPICS_MOVED_TO_DONE = "epics_moved_to_done"
    EPICS_MOVED_BACK_TO_STARTED = "epics_moved_back_to_started"
    OBJECTIVES_MOVED_TO_STARTED = "objectives_moved_to_started"
    CREATIONS_DEFERRED = "creations_deferred_by_cap"
    PROGRESS_UPDATES_DEFERRED = "progress_updates_deferred_by_cap"
    ISSUE_COMMENTS_FAILED = "issue_comments_failed"
    REPO_STEP_FAILURES = "repo_step_failures"
    PROGRESS_STEP_FAILURES = "progress_step_failures"
