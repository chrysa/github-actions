"""Entrypoint: read the environment, run the job, log counts, set the exit code.

Exit codes: 0 = done (or skipped because a secret is not configured yet),
1 = invalid configuration, aborted run, or contained failures (see the counters).
"""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from shortcut_sync.errors import ConfigurationError, MissingSecretError, ShortcutSyncError
from shortcut_sync.sync_config import SyncConfig
from shortcut_sync.sync_context import SyncContext
from shortcut_sync.sync_job import ShortcutSyncJob
from shortcut_sync.sync_report import SyncReport

STEP_SUMMARY_ENV: Final = "GITHUB_STEP_SUMMARY"
EXIT_OK: Final = 0
EXIT_FAILURE: Final = 1

logger = logging.getLogger(__name__)


def main(env: Mapping[str, str] | None = None) -> int:
    """Run one sync. ``env`` defaults to the process environment."""
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s", force=True)
    source = dict(os.environ) if env is None else env
    try:
        config = SyncConfig.from_env(source)
    except MissingSecretError as error:
        logger.warning(f"::warning::{error}: Shortcut sync skipped")
        return EXIT_OK
    except ConfigurationError as error:
        logger.error(f"::error::{error}")
        return EXIT_FAILURE
    context = SyncContext.from_config(config)
    try:
        ShortcutSyncJob(context=context).run()
    except ShortcutSyncError as error:
        logger.error(f"::error::Shortcut sync aborted: {error}")
        _publish(report=context.report, env=source)
        return EXIT_FAILURE
    _publish(report=context.report, env=source)
    return EXIT_FAILURE if context.report.has_failures else EXIT_OK


def _publish(*, report: SyncReport, env: Mapping[str, str]) -> None:
    for line in report.summary_lines():
        logger.info(line)
    path = env.get(STEP_SUMMARY_ENV, "")
    if not path:
        return
    try:
        with Path(path).open("a", encoding="utf-8") as handle:
            handle.write(report.markdown_summary())
    except OSError as error:
        logger.warning(f"::warning::step summary not written ({error.strerror})")
