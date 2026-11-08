"""Shortcut REST API v3 — only the calls the sync needs."""

from __future__ import annotations

from http import HTTPStatus
from typing import Final, cast

from shortcut_sync.errors import ApiError
from shortcut_sync.http_client import HttpClient, with_query
from shortcut_sync.payloads import ShortcutEpic, ShortcutStory, ShortcutWorkflow
from shortcut_sync.story_draft import StoryDraft

SHORTCUT_SERVICE: Final = "Shortcut"
# Shortcut allows ~200 requests/minute: 0.3 s between calls keeps the job under it.
SHORTCUT_MIN_INTERVAL_SECONDS: Final = 0.3
WITHOUT_DESCRIPTION: Final = {"includes_description": "false"}


class ShortcutClient:
    def __init__(self, *, http: HttpClient) -> None:
        self._http = http

    @classmethod
    def from_token(cls, *, token: str, base_url: str) -> ShortcutClient:
        """Client authenticated with the ``Shortcut-Token`` header."""
        headers = {"Shortcut-Token": token, "Content-Type": "application/json", "Accept": "application/json"}
        http = HttpClient(
            service=SHORTCUT_SERVICE,
            base_url=base_url,
            headers=headers,
            min_interval_seconds=SHORTCUT_MIN_INTERVAL_SECONDS,
        )
        return cls(http=http)

    def create_story(self, draft: StoryDraft) -> ShortcutStory:
        """``POST /stories``; the response must carry the new story id."""
        story = self._http.request_object(method="POST", path="stories", body=draft.to_payload())
        if story is None or not isinstance(story.get("id"), int):
            raise ApiError(
                service=SHORTCUT_SERVICE, method="POST", reason="story id missing from the response"
            )
        return cast(ShortcutStory, story)

    def get_epic_health(self, epic_id: int) -> str | None:
        """Current health status of an epic, or None when it has none."""
        health = self._http.request_object(
            method="GET",
            path=f"epics/{epic_id}/health",
            absent_statuses=(HTTPStatus.NOT_FOUND,),
        )
        status = health.get("status") if health else None
        return status if isinstance(status, str) else None

    def list_epic_stories(self, epic_id: int) -> list[ShortcutStory]:
        """Every story of an epic (slim payload, no description)."""
        path = with_query(path=f"epics/{epic_id}/stories", query=WITHOUT_DESCRIPTION)
        return [cast(ShortcutStory, story) for story in self._http.request_objects(path=path)]

    def list_epics(self) -> list[ShortcutEpic]:
        """Every epic of the workspace (slim payload, no description)."""
        path = with_query(path="epics", query=WITHOUT_DESCRIPTION)
        return [cast(ShortcutEpic, epic) for epic in self._http.request_objects(path=path)]

    def list_workflows(self) -> list[ShortcutWorkflow]:
        """Every workflow with its states."""
        return [cast(ShortcutWorkflow, workflow) for workflow in self._http.request_objects(path="workflows")]

    def move_story(self, *, story_id: int, workflow_state_id: int) -> None:
        """``PUT /stories/{id}`` with a new workflow state."""
        self._http.request_object(
            method="PUT",
            path=f"stories/{story_id}",
            body={"workflow_state_id": workflow_state_id},
        )

    def set_epic_health(self, *, epic_id: int, status: str, text: str) -> None:
        """``POST /epics/{id}/health`` — a new health record (status + short text)."""
        self._http.request_object(
            method="POST",
            path=f"epics/{epic_id}/health",
            body={"status": status, "text": text},
        )
