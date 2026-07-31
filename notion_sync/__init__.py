"""Notion sync entrypoints used by the notion-* composite actions.

Kept out of workflow YAML on purpose: workflows are glue, logic lives here and is
unit-tested (see `standards/STANDARDS.chrysa.md` — GitHub Actions).
"""

__all__ = ["notion_api"]
