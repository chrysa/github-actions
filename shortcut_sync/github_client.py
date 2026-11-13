"""GitHub REST API — issues and issue comments of the mapped repositories."""

from __future__ import annotations

import urllib.parse
from collections.abc import Mapping
from http import HTTPStatus
from typing import Final, cast

from shortcut_sync.http_client import HttpClient, with_query
from shortcut_sync.payloads import GitHubIssue, GitHubRepository

GITHUB_SERVICE: Final = "GitHub"
GITHUB_API_VERSION: Final = "2022-11-28"
USER_AGENT: Final = "chrysa-shortcut-sync"
PAGE_SIZE: Final = 100
MAX_PAGES: Final = 50
# A fine-grained token without access to a repository gets 404 (sometimes 403).
REPOSITORY_ABSENT_STATUSES: Final = (HTTPStatus.NOT_FOUND, HTTPStatus.FORBIDDEN)
ISSUE_ABSENT_STATUSES: Final = (HTTPStatus.NOT_FOUND, HTTPStatus.GONE)


class GitHubClient:
    def __init__(self, *, http: HttpClient, owner: str) -> None:
        self._http = http
        self._owner = owner

    @classmethod
    def from_token(cls, *, token: str, base_url: str, owner: str) -> GitHubClient:
        """Client authenticated with a bearer token (the fine-grained sync PAT)."""
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        }
        return cls(http=HttpClient(service=GITHUB_SERVICE, base_url=base_url, headers=headers), owner=owner)

    def create_issue_comment(self, *, repo: str, number: int, body: str) -> None:
        """Post one comment on an issue."""
        self._http.request_object(
            method="POST",
            path=f"{self._repo_path(repo)}/issues/{number}/comments",
            body={"body": body},
        )

    def get_issue(self, *, repo: str, number: int) -> GitHubIssue | None:
        """One issue, or None when it was deleted, transferred or is unreadable."""
        issue = self._http.request_object(
            method="GET",
            path=f"{self._repo_path(repo)}/issues/{number}",
            absent_statuses=ISSUE_ABSENT_STATUSES,
        )
        return cast(GitHubIssue, issue) if issue is not None else None

    def get_repository(self, repo: str) -> GitHubRepository | None:
        """Repository metadata, or None when the token cannot see it."""
        repository = self._http.request_object(
            method="GET",
            path=self._repo_path(repo),
            absent_statuses=REPOSITORY_ABSENT_STATUSES,
        )
        return cast(GitHubRepository, repository) if repository is not None else None

    def list_issue_comment_bodies(self, *, repo: str, number: int) -> list[str]:
        """Text of every comment of an issue."""
        comments = self._paginate(path=f"{self._repo_path(repo)}/issues/{number}/comments", query={})
        return [str(comment.get("body") or "") for comment in comments]

    def list_open_issues(self, repo: str) -> list[GitHubIssue]:
        """Open issues of a repository, pull requests excluded."""
        items = self._paginate(path=f"{self._repo_path(repo)}/issues", query={"state": "open"})
        return [cast(GitHubIssue, item) for item in items if "pull_request" not in item]

    def _paginate(self, *, path: str, query: Mapping[str, str]) -> list[dict[str, object]]:
        collected: list[dict[str, object]] = []
        for page in range(1, MAX_PAGES + 1):
            page_query: dict[str, str | int] = {**query, "per_page": PAGE_SIZE, "page": page}
            batch = self._http.request_objects(path=with_query(path=path, query=page_query))
            collected.extend(batch)
            if len(batch) < PAGE_SIZE:
                break
        return collected

    def _repo_path(self, repo: str) -> str:
        return f"repos/{urllib.parse.quote(self._owner)}/{urllib.parse.quote(repo)}"
