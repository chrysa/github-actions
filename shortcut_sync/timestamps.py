"""Pure helpers over the ISO-8601 timestamps of the Shortcut API, and the override rule.

A timestamp keeps the exact string the API returned: it is compared as an instant but
written back unchanged.
"""

from __future__ import annotations

from collections.abc import Iterable, MutableMapping
from datetime import UTC, datetime


def parse_timestamp(value: object) -> datetime | None:
    """An aware datetime (naive values are read as UTC), or None when absent or invalid."""
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def earliest(values: Iterable[object]) -> str | None:
    """The earliest valid timestamp of ``values``, as the API wrote it."""
    dated = _dated(values)
    return min(dated, key=_instant)[1] if dated else None


def latest(values: Iterable[object]) -> str | None:
    """The latest valid timestamp of ``values``, as the API wrote it."""
    dated = _dated(values)
    return max(dated, key=_instant)[1] if dated else None


def same_instant(left: object, right: object) -> bool:
    """True when both values parse to the same instant."""
    parsed = parse_timestamp(left)
    return parsed is not None and parsed == parse_timestamp(right)


def plan_override(
    changes: MutableMapping[str, object], *, field: str, current: object, computed: str | None
) -> bool:
    """Owner rule: set an empty override, never overwrite a different one.

    Adds ``field`` to ``changes`` when the override is empty; returns True when an
    override already set (by hand) differs from the computed date and is kept.
    """
    if computed is None:
        return False
    if not current:
        changes[field] = computed
        return False
    return not same_instant(current, computed)


def _instant(item: tuple[datetime, str]) -> datetime:
    return item[0]


def _dated(values: Iterable[object]) -> list[tuple[datetime, str]]:
    return [
        (parsed, value)
        for value in values
        if isinstance(value, str) and (parsed := parse_timestamp(value)) is not None
    ]
