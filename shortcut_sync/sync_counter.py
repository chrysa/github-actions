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
    QUALITY_GATE_FAILING = "quality_gate_failing"
    QUALITY_GATE_PASSING = "quality_gate_passing"
    QUALITY_GATE_SKIPPED = "quality_gate_skipped"
    EPIC_HEALTH_UPDATED = "epic_health_updated"
    QUALITY_STORIES_CREATED = "quality_stories_created"
    QUALITY_STORIES_MOVED_TO_DONE = "quality_stories_moved_to_done"
    CREATIONS_DEFERRED = "creations_deferred_by_cap"
    ISSUE_COMMENTS_FAILED = "issue_comments_failed"
    REPO_STEP_FAILURES = "repo_step_failures"
