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
