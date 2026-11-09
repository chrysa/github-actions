"""Job configuration read from the environment."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Final

from shortcut_sync.errors import ConfigurationError, MissingSecretError

SHORTCUT_TOKEN_ENV: Final = "SHORTCUT_API_TOKEN"
GITHUB_TOKEN_ENV: Final = "SYNC_GITHUB_TOKEN"
DRY_RUN_ENV: Final = "SYNC_DRY_RUN"
MAX_CREATIONS_ENV: Final = "SYNC_MAX_CREATIONS"
MAX_PROGRESS_UPDATES_ENV: Final = "SYNC_MAX_PROGRESS_UPDATES"
WORKFLOW_ID_ENV: Final = "SHORTCUT_WORKFLOW_ID"
SHORTCUT_API_URL_ENV: Final = "SHORTCUT_API_URL"
GITHUB_API_URL_ENV: Final = "GITHUB_API_URL"
SONAR_URL_ENV: Final = "SONAR_HOST_URL"

DEFAULT_SHORTCUT_API_URL: Final = "https://api.app.shortcut.com/api/v3"
DEFAULT_GITHUB_API_URL: Final = "https://api.github.com"
DEFAULT_SONAR_URL: Final = "https://sonarcloud.io"
DEFAULT_MAX_CREATIONS: Final = 25
DEFAULT_MAX_PROGRESS_UPDATES: Final = 50
GITHUB_OWNER: Final = "chrysa"
HTTPS_PREFIX: Final = "https://"

_BOOLEAN_VALUES: Final[Mapping[str, bool]] = {
    "true": True,
    "1": True,
    "yes": True,
    "false": False,
    "0": False,
    "no": False,
}


@dataclass(frozen=True, slots=True)
class SyncConfig:
    """Everything the job needs, validated once at start-up. Tokens never appear in repr()."""

    shortcut_token: str = field(repr=False)
    github_token: str = field(repr=False)
    dry_run: bool
    max_creations: int
    max_progress_updates: int
    workflow_id: int | None
    shortcut_api_url: str
    github_api_url: str
    sonar_url: str
    github_owner: str = GITHUB_OWNER

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> SyncConfig:
        """Build the configuration; raise MissingSecretError or ConfigurationError on bad input."""
        return cls(
            shortcut_token=_required_secret(env=env, name=SHORTCUT_TOKEN_ENV),
            github_token=_required_secret(env=env, name=GITHUB_TOKEN_ENV),
            dry_run=_parse_bool(env=env, name=DRY_RUN_ENV, default=True),
            max_creations=_parse_count(env=env, name=MAX_CREATIONS_ENV, default=DEFAULT_MAX_CREATIONS),
            max_progress_updates=_parse_count(
                env=env, name=MAX_PROGRESS_UPDATES_ENV, default=DEFAULT_MAX_PROGRESS_UPDATES
            ),
            workflow_id=_parse_optional_id(env=env, name=WORKFLOW_ID_ENV),
            shortcut_api_url=_https_url(env=env, name=SHORTCUT_API_URL_ENV, default=DEFAULT_SHORTCUT_API_URL),
            github_api_url=_https_url(env=env, name=GITHUB_API_URL_ENV, default=DEFAULT_GITHUB_API_URL),
            sonar_url=_https_url(env=env, name=SONAR_URL_ENV, default=DEFAULT_SONAR_URL),
        )


def _required_secret(*, env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise MissingSecretError(f"{name} is not set")
    return value


def _parse_bool(*, env: Mapping[str, str], name: str, default: bool) -> bool:
    raw = env.get(name, "").strip().lower()
    if not raw:
        return default
    if raw not in _BOOLEAN_VALUES:
        raise ConfigurationError(f"{name} must be true or false")
    return _BOOLEAN_VALUES[raw]


def _parse_count(*, env: Mapping[str, str], name: str, default: int) -> int:
    raw = env.get(name, "").strip()
    if not raw:
        return default
    if not raw.isdigit():
        raise ConfigurationError(f"{name} must be a non-negative integer")
    return int(raw)


def _parse_optional_id(*, env: Mapping[str, str], name: str) -> int | None:
    raw = env.get(name, "").strip()
    if not raw:
        return None
    if not raw.isdigit():
        raise ConfigurationError(f"{name} must be a numeric id")
    return int(raw)


def _https_url(*, env: Mapping[str, str], name: str, default: str) -> str:
    value = (env.get(name, "").strip() or default).rstrip("/")
    if not value.startswith(HTTPS_PREFIX):
        raise ConfigurationError(f"{name} must be an https:// URL")
    return value
