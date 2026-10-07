# REVIEW — documentation audit (github-actions)

Docs-only pass, 2026-09-25. No source, test, dependency, CI, or config file was
modified. This file records what was documented, what was skipped, open
questions, and debt.

## Docs created this pass

- `ARCHITECTURE.md` — component catalogue (24 actions, 24 reusable workflows,
  `notion_sync` package), versioning/consumption model.
- `TRD.md` — runtime, interface contract, secret handling, quality gates, release.
- `REQUIREMENTS.md` — REQ-TECH matrix traced to evidence.
- `CONSTRAINTS.md` — platform/consumption/process/standards constraints.
- `REVIEW.md` — this file.

## Docs updated

- `SECURITY.md` — appended a *Documentation-audit findings* section (policy text
  preserved). See findings below.
- `CLAUDE.md` — added a compact "Documentation map".

## Docs skipped (and why)

- **PRD** — no end-user product; this is CI infrastructure. Skipped.
- **Data model / persistence** — none (no DB). Skipped.
- **OBSERVABILITY** (of a running app) — N/A; the repo *provides* observability
  workflows to others rather than running a service. Skipped.
- **GLOSSARY** — terms are standard GitHub Actions vocabulary; not warranted.
- **ROADMAP / TESTING** as standalone — testing is covered in TRD §5 and the
  `tests/` suite; no separate doc warranted. `docs/specs/` already holds a
  self-hosted-CI design spec (future direction) — preserved, not duplicated.

## Existing docs — preserved, not contradicted

`README.md` (per-action usage — canonical reference), `DECISIONS.md` (ADRs
D-0001..), `CHANGELOG.md`, `CONTRIBUTING.md`, `AGENTS.md`, `.github/copilot-
instructions.md`, `docs/reference/`, `docs/specs/`, `.claude/rules/folder-readme.md`.
No contradictions found between them and the new docs.

## Security findings (see SECURITY.md for detail)

| Severity | Finding |
| --- | --- |
| MEDIUM | Third-party `uses` pinned to mutable tags, not commit SHAs |
| MEDIUM | Internal `@main` references vs "never `@main`" policy |
| LOW | 9 `workflow_call` workflows lack an explicit `permissions:` block |
| — | No hardcoded secrets found (clean) |

## Open questions / UNKNOWNs

- Disposition of large tracked artefacts at root — `graphify` (11 MB), `sys`
  (33 MB), `graphify-out/`, `guideline-report.html` (86 KB) — vs the chrysa
  "every tracked file earns its place" rule. Are these intentional or drift?
- Whether the injection-safe `env:`-mapping pattern seen in `ruff-check` is
  uniform across all 24 actions (spot-checked only, not exhaustively audited).
- CHANGELOG top entry is `1.0.7`; internal `uses` reference `v1.9.0`. The
  version-history source of truth vs the moving `@v1` tag is not reconciled here.

## Documentation debt

- No CONTRIBUTING guidance on SHA-pinning policy for third-party actions.
- REQ-TECH matrix statuses marked PARTIAL/UNKNOWN need a code-level audit to
  promote to IMPLEMENTED (out of scope for a docs-only pass).
