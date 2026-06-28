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

## D-0003 — Self-hosted runner default (chrysa-arc), public repos override to ubuntu-latest

**Date**: 2026-06-28
**Status**: accepted

All reusable workflows (`workflow_call`) in this repository now expose a `runner`
input (type: string, default: `chrysa-arc`) and set
`runs-on: ${{ inputs.runner || 'chrysa-arc' }}` on every job. The explicit
`|| 'chrysa-arc'` fallback keeps the self-hosted default even on non-`workflow_call`
trigger paths (e.g. `pull_request_target`, `schedule`), where the input default does
not apply and `inputs.runner` would otherwise be the empty string. The self-hosted
label `chrysa-arc` is the fleet label for ARC
(Actions Runner Controller) runners deployed on the chrysa Kimsufi host.

**Rationale for the public/private split:**
Private chrysa repos call the reusable workflows without overriding `runner`, so they
run on self-hosted `chrysa-arc` runners by default, eliminating GitHub-hosted runner
billing. Public repos (open-source mirrors, documentation sites) cannot safely route
CI to private infrastructure, so their caller workflows pass `runner: ubuntu-latest`
explicitly to force GitHub-hosted runners. The default deliberately favours the private
fleet; public callers must opt out.

**Affected workflows (16):** `ci-python.yml`, `ci-fullstack.yml`, `ci-python-app.yml`,
`deploy.yml`, `lint-python.yml`, `mutation-testing.yml`, `dependabot-auto-merge.yml`,
`dependencies.yml`, `enforce-feature-branch.yml`, `pages.yml`, `pre-commit.yml`,
`release.yml`, `secret-scan.yml`, `quality-gate-check.yml`, `labeler.yml`,
`pr-dependencies.yml`.

**Workflows intentionally left unchanged (10):** `action-check.yml`,
`approved-label.yml`, `auto-assign.yml`, `auto-update-pre-commit.yml`, `ci.yml`,
`detect-conflicts.yml`, `pull-request-size.yml`, `sonar.yml`, `sync-labels.yml`,
`update-pr-body.yml` — none of these are triggered by `workflow_call`; they are
standalone push/PR/schedule workflows owned by this repo and not called by others.

---
