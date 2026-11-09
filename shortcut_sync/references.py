"""Pure helpers: Shortcut references, story typing, SonarCloud keys, sync markers, issue comments."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Final

from shortcut_sync.http_client import with_query
from shortcut_sync.issue_key import IssueKey
from shortcut_sync.payloads import GitHubLabel, ShortcutStory

SHORTCUT_REFERENCE_PATTERN: Final = re.compile(
    r"\bsc-\d+\b|app\.shortcut\.com/[^/\s]+/story/\d+",
    re.IGNORECASE,
)
STORY_TYPE_BUG: Final = "bug"
STORY_TYPE_FEATURE: Final = "feature"
STORY_TYPE_CHORE: Final = "chore"
BUG_LABELS: Final = frozenset({"bug", "sentry"})
GUARDRAILS_MARKER_SUFFIX: Final = "#guardrails"


def has_shortcut_reference(text: object) -> bool:
    """True when the text mentions ``sc-<digits>`` or an app.shortcut.com story URL."""
    return isinstance(text, str) and SHORTCUT_REFERENCE_PATTERN.search(text) is not None


def story_type_for(labels: Iterable[GitHubLabel]) -> str:
    """``bug`` when the issue carries the ``bug`` or ``sentry`` label, else ``feature``."""
    names = {str(label.get("name", "")).lower() for label in labels}
    return STORY_TYPE_BUG if names & BUG_LABELS else STORY_TYPE_FEATURE


def linked_issue_keys(stories: Iterable[ShortcutStory]) -> set[IssueKey]:
    """Every GitHub issue a story already points to, by external link or sync marker."""
    keys: set[IssueKey] = set()
    for story in stories:
        candidates = [IssueKey.from_url(link) for link in story.get("external_links", [])]
        candidates.append(IssueKey.from_external_id(story.get("external_id")))
        keys.update(key for key in candidates if key is not None)
    return keys


def issue_comment(*, story_id: int, app_url: str) -> str:
    """Comment posted on the GitHub issue once its story exists."""
    return f"Shortcut: sc-{story_id} {app_url}".strip()


def sonar_project_key(*, owner: str, repo: str) -> str:
    """SonarCloud project key convention of the fleet: ``<owner>_<repo>``."""
    return f"{owner}_{repo}"


def sonar_dashboard_url(*, sonar_url: str, project_key: str) -> str:
    """Dashboard URL, also the dedupe key of the quality-gate story."""
    return with_query(path=f"{sonar_url}/dashboard", query={"id": project_key})


def guardrails_marker(*, owner: str, repo: str) -> str:
    """``external_id`` of the GuardRails story of a repository: ``owner/repo#guardrails``."""
    return f"{owner}/{repo}{GUARDRAILS_MARKER_SUFFIX}".lower()


def same_link(left: str, right: str) -> bool:
    """Compare two URLs ignoring case and a trailing slash."""
    return left.strip().rstrip("/").lower() == right.strip().rstrip("/").lower()
