# DECISIONS — github-actions

> Repository-local ADRs (Architectural Decision Records). Numbering: D-XXXX.
> Any deviation from [CODE_MANIFEST.md](../../shared-standards/CODE_MANIFEST.md) must be documented here.
> No active deviation → this project follows all chrysa global standards.

---

## D-0001 — Adherence to chrysa global standards

**Date**: 2026-05-25
**Status**: accepted

This project follows all conventions defined in `CODE_MANIFEST.md` (chrysa portfolio standards).
No active deviation is in effect. Any future deviation must be added as a new ADR entry below.

---

## D-0002 — Release-gated lint via reusable workflow

**Date**: 2026-06-06
**Status**: accepted

Lint (ruff, ruff-format, mypy) previously ran on every branch push and PR across
~46 repos, driving high GitHub Actions billing. Lint now lives in pre-commit
(local, source of truth) and is replayed in CI **only at release time**.

`.github/workflows/lint-python.yml` is a `workflow_call` reusable workflow that
replays the full pre-commit suite (`pre-commit run --all-files --hook-stage
pre-push`, which covers ruff at all stages + mypy at the pre-push stage). Consumer
repos call it as a gate job at the top of their `release.yml` (`version: needs:
lint`). CI on PR/push keeps only tests + sonar.

Trade-off: PRs are no longer lint-gated in CI; correctness relies on local
pre-commit hooks, with the release gate as the final safety net.

---
