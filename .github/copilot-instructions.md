# github-actions — Copilot Instructions

## MANDATORY: Read Instructions Before Any Task

Before working on actions, tests, or CI, read relevant instruction files.

## Project Overview

Reusable GitHub Actions composite actions for the `chrysa` organization.
Referenced as `chrysa/github-actions@v1` across all chrysa repositories.

## Available Actions

| Action | Purpose |
|---|---|
| `tool-setup` | Install Python + dependencies via pip |
| `python-setup` | Setup Python version |
| `ruff-check` | Run ruff linter + formatter check |
| `mypy-check` | Run mypy type checker |
| `run-tests` | Run pytest with coverage |
| `sonar-scan` | SonarCloud analysis for Python |
| `sonar-js-scan` | SonarCloud analysis for JS/TS |
| `gitversion` | Compute semantic version via GitVersion |
| `install-project` | Install project with extras |

## Architecture

```
<action-name>/
    action.yml      # composite action definition
```

## Key Constraints

- **Always use `@v1`** when referencing this repo (never `@main`)
- **Semantic versioning** — tag releases as `v1`, `v1.0.0`, etc.
- **Backward compatible** — breaking changes need a new major version
- All action inputs must have descriptions
- Test actions in isolation before merging

## Tagging Strategy

```bash
git tag -fa v1 -m "Update v1 tag"
git push origin v1 --force
```

## Execution Standard Compliance

All chrysa CI workflows that call these actions must enforce the requirements in
`chrysa/shared-standards/EXECUTION_STANDARD.md`.

### What CI must run (§5)

Every `ci-*.yml` pipeline must execute in order:

| Step | Action | Requirement |
|------|--------|-------------|
| 1 | lint | `ruff-check@v1` or equivalent — must pass |
| 2 | typecheck | `mypy-check@v1` — must pass for typed projects |
| 3 | test-cov | `run-tests@v1` — generates `coverage.xml`, ≥ 80% line coverage |
| 4 | analysis | `sonar-scan@v1` or `sonar-js-scan@v1` after tests |

### Testing requirements (§4)

- Minimum **80% line coverage** — fail the job if below threshold
- Coverage artifact uploaded as `coverage.xml` on every CI run
- Test names: `test_<unit>_when_<condition>_should_<expected>`

### Makefile contract (§1)

Callers are expected to expose `make lint`, `make typecheck`, `make test-cov` as entry points.
Actions may call these Makefile targets or invoke tools directly — both are valid.
