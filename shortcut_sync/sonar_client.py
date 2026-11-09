"""SonarCloud public web API, read anonymously (public projects only)."""

from __future__ import annotations

from http import HTTPStatus
from typing import Final

from shortcut_sync.http_client import HttpClient, with_query

SONAR_SERVICE: Final = "SonarCloud"
# Private or missing projects answer 404/401/403 to an anonymous call: they are skipped.
ABSENT_STATUSES: Final = (HTTPStatus.NOT_FOUND, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)


class SonarClient:
    def __init__(self, *, http: HttpClient) -> None:
        self._http = http

    @classmethod
    def anonymous(cls, *, base_url: str) -> SonarClient:
        """Client without credentials."""
        http = HttpClient(service=SONAR_SERVICE, base_url=base_url, headers={"Accept": "application/json"})
        return cls(http=http)

    def quality_gate_status(self, project_key: str) -> str | None:
        """``OK`` / ``ERROR`` / ``NONE``…, or None when the project is private or absent."""
        body = self._http.request_object(
            method="GET",
            path=with_query(path="api/qualitygates/project_status", query={"projectKey": project_key}),
            absent_statuses=ABSENT_STATUSES,
        )
        project_status = body.get("projectStatus") if body else None
        status = project_status.get("status") if isinstance(project_status, dict) else None
        return status if isinstance(status, str) else None
