"""Repository ↔ epic mapping, keyed by the epic ``external_id`` ``<owner>/<repo>``."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

from shortcut_sync.payloads import ShortcutEpic

EPIC_EXTERNAL_ID_PATTERN: Final = re.compile(r"(?P<owner>[A-Za-z0-9-]+)/(?P<repo>[A-Za-z0-9._-]+)")


@dataclass(frozen=True, slots=True)
class RepoMapping:
    """One repository and every non-archived epic mapped to it (sorted ids)."""

    owner: str
    repo: str
    epic_ids: tuple[int, ...]

    @property
    def primary_epic_id(self) -> int:
        """Epic receiving new stories and health updates: the oldest (lowest id)."""
        return self.epic_ids[0]

    @classmethod
    def from_epics(cls, *, epics: Iterable[ShortcutEpic], owner: str) -> list[RepoMapping]:
        """Group mapped epics by repository; epics without a valid ``owner/repo`` id are skipped."""
        grouped: dict[str, list[int]] = {}
        names: dict[str, str] = {}
        for epic in epics:
            repo = cls._mapped_repo(epic=epic, owner=owner)
            if repo is None:
                continue
            grouped.setdefault(repo.lower(), []).append(int(epic["id"]))
            names.setdefault(repo.lower(), repo)
        return [
            cls(owner=owner, repo=names[key], epic_ids=tuple(sorted(epic_ids)))
            for key, epic_ids in sorted(grouped.items())
        ]

    @staticmethod
    def _mapped_repo(*, epic: ShortcutEpic, owner: str) -> str | None:
        if epic.get("archived") or not isinstance(epic.get("id"), int):
            return None
        external_id = epic.get("external_id")
        match = EPIC_EXTERNAL_ID_PATTERN.fullmatch(external_id) if isinstance(external_id, str) else None
        if match is None or match["owner"].lower() != owner.lower() or not match["repo"].strip("."):
            return None
        return match["repo"]
