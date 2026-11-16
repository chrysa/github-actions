"""Typed errors raised by the Shortcut sync.

Messages never carry a URL path, a token or a payload: the job runs in a public
repository, its logs are public, and API paths name repositories that may be private.
"""

from __future__ import annotations


class ShortcutSyncError(Exception):
    """Base class of every failure the sync raises on purpose."""


class ConfigurationError(ShortcutSyncError):
    """The job environment holds an invalid value."""


class MissingSecretError(ConfigurationError):
    """A required secret is not configured yet: the job skips instead of failing."""


class ApiError(ShortcutSyncError):
    """A remote API call failed."""

    def __init__(self, *, service: str, method: str, reason: str) -> None:
        self.service = service
        self.method = method
        self.reason = reason
        super().__init__(f"{service} {method} failed: {reason}")
