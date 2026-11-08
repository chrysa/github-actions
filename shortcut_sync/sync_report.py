"""Run report: counters, the story-creation budget, and the dry-run aware action log."""

from __future__ import annotations

import logging
from collections import Counter
from typing import Final

from shortcut_sync.sync_counter import SyncCounter

DRY_RUN_PREFIX: Final = "[dry-run] "
FAILURE_COUNTERS: Final = (SyncCounter.REPO_STEP_FAILURES, SyncCounter.ISSUE_COMMENTS_FAILED)

logger = logging.getLogger(__name__)


class SyncReport:
    """Counts what the run did (or, in dry-run, would do)."""

    def __init__(self, *, dry_run: bool, max_creations: int) -> None:
        self._dry_run = dry_run
        self._max_creations = max_creations
        self._creations = 0
        self._counts: Counter[SyncCounter] = Counter()

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    @property
    def has_failures(self) -> bool:
        return any(self._counts[counter] for counter in FAILURE_COUNTERS)

    @property
    def mode(self) -> str:
        return "dry-run (planned actions, nothing written)" if self._dry_run else "apply"

    def add(self, counter: SyncCounter, *, amount: int = 1) -> None:
        """Increment a counter."""
        self._counts[counter] += amount

    def count(self, counter: SyncCounter) -> int:
        """Current value of a counter."""
        return self._counts[counter]

    def markdown_summary(self) -> str:
        """Counts as a Markdown table for ``$GITHUB_STEP_SUMMARY``."""
        rows = "\n".join(f"| `{counter.value}` | {self._counts[counter]} |" for counter in SyncCounter)
        return f"### Shortcut sync — {self.mode}\n\n| Counter | Count |\n|---|---|\n{rows}\n"

    def record(self, counter: SyncCounter, *, detail: str) -> None:
        """Increment a counter and log the action. ``detail`` must hold numeric ids only."""
        self.add(counter)
        prefix = DRY_RUN_PREFIX if self._dry_run else ""
        logger.info(f"{prefix}{counter.value}: {detail}")

    def reserve_creation(self) -> bool:
        """Take one slot of the per-run creation cap; count a deferral when it is exhausted."""
        if self._creations >= self._max_creations:
            self.add(SyncCounter.CREATIONS_DEFERRED)
            return False
        self._creations += 1
        return True

    def summary_lines(self) -> list[str]:
        """One ``name: count`` line per counter, preceded by the mode."""
        return [
            f"mode: {self.mode}",
            *(f"{counter.value}: {self._counts[counter]}" for counter in SyncCounter),
        ]
