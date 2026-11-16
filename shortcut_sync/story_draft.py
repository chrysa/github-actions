"""A story about to be created. Deliberately has no label field (owner rule: no labels)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

STORY_NAME_MAX_CHARS: Final = 512


@dataclass(frozen=True, slots=True)
class StoryDraft:
    name: str
    epic_id: int
    story_type: str
    workflow_state_id: int
    external_links: tuple[str, ...]
    description: str = ""
    external_id: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Body of ``POST /api/v3/stories``."""
        payload: dict[str, object] = {
            "name": self.name[:STORY_NAME_MAX_CHARS],
            "epic_id": self.epic_id,
            "story_type": self.story_type,
            "workflow_state_id": self.workflow_state_id,
            "external_links": list(self.external_links),
            "description": self.description,
        }
        if self.external_id:
            payload["external_id"] = self.external_id
        return payload
