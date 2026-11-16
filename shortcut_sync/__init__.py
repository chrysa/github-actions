"""Daily Shortcut sync: GitHub issues mirrored into Shortcut, epic and objective states kept in step.

Run with ``python3 -m shortcut_sync`` (see ``.github/workflows/shortcut-sync.yml``).
Logic lives here and is unit-tested; the workflow stays glue (fleet GitHub Actions standard).
"""

__all__ = ["entrypoint"]
