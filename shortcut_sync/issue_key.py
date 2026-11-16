"""Identity of a GitHub issue, normalised so URLs and story markers compare equal."""

from __future__ import annotations

import re
from typing import Final, NamedTuple

ISSUE_URL_PATTERN: Final = re.compile(
    r"https://github\.com/(?P<owner>[A-Za-z0-9-]+)/(?P<repo>[A-Za-z0-9._-]+)/issues/(?P<number>\d+)(?:[/?#].*)?",
    re.IGNORECASE,
)
EXTERNAL_ID_PATTERN: Final = re.compile(
    r"(?P<owner>[A-Za-z0-9-]+)/(?P<repo>[A-Za-z0-9._-]+)#(?P<number>\d+)",
)


class IssueKey(NamedTuple):
    """``(owner, repo, number)``, owner and repo lower-cased (GitHub names are case-insensitive)."""

    owner: str
    repo: str
    number: int

    @property
    def external_id(self) -> str:
        """Marker stored in a story's ``external_id``: ``owner/repo#number``."""
        return f"{self.owner}/{self.repo}#{self.number}"

    @classmethod
    def from_external_id(cls, value: object) -> IssueKey | None:
        """Parse the marker written on stories created by the sync."""
        return cls._from_match(EXTERNAL_ID_PATTERN.fullmatch(value) if isinstance(value, str) else None)

    @classmethod
    def from_url(cls, value: object) -> IssueKey | None:
        """Parse a GitHub issue URL (``html_url`` or a story external link)."""
        return cls._from_match(ISSUE_URL_PATTERN.fullmatch(value.strip()) if isinstance(value, str) else None)

    @classmethod
    def of(cls, *, owner: str, repo: str, number: int) -> IssueKey:
        """Build a normalised key."""
        return cls(owner=owner.lower(), repo=repo.lower(), number=number)

    @classmethod
    def _from_match(cls, match: re.Match[str] | None) -> IssueKey | None:
        if match is None:
            return None
        return cls.of(owner=match["owner"], repo=match["repo"], number=int(match["number"]))
