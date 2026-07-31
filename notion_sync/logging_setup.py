"""Logging wired to the GitHub Actions log stream.

Actions read stdout: a plain message is a log line, `::warning::…` is an annotation.
So the formatter emits the message verbatim — no timestamps, no level prefix.
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a logger writing bare messages to stdout (the Actions log channel)."""
    return logging.getLogger(name)


def configure() -> None:
    """Install the stdout handler once, at entrypoint start."""
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s", force=True)
