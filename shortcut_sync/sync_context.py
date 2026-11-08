"""Dependencies shared by every sync step: configuration, API clients, report."""

from __future__ import annotations

from dataclasses import dataclass

from shortcut_sync.github_client import GitHubClient
from shortcut_sync.shortcut_client import ShortcutClient
from shortcut_sync.sonar_client import SonarClient
from shortcut_sync.sync_config import SyncConfig
from shortcut_sync.sync_report import SyncReport


@dataclass(frozen=True, slots=True)
class SyncContext:
    config: SyncConfig
    shortcut: ShortcutClient
    github: GitHubClient
    sonar: SonarClient
    report: SyncReport

    @classmethod
    def from_config(cls, config: SyncConfig) -> SyncContext:
        """Wire the real HTTP clients for one run."""
        return cls(
            config=config,
            shortcut=ShortcutClient.from_token(token=config.shortcut_token, base_url=config.shortcut_api_url),
            github=GitHubClient.from_token(
                token=config.github_token,
                base_url=config.github_api_url,
                owner=config.github_owner,
            ),
            sonar=SonarClient.anonymous(base_url=config.sonar_url),
            report=SyncReport(dry_run=config.dry_run, max_creations=config.max_creations),
        )
