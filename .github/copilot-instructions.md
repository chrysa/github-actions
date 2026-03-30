---
# github-actions — Copilot Instructions

## MANDATORY: Read Instructions Before Any Task

Before working on actions, check relevant instruction files in `.github/instructions/`.

| File | Applies to |
|---|---|
| `python_guidelines.instructions.md` | `**/*.py` |
| `typing.instructions.md` | `**/*.py` |

---

## Project Overview

`chrysa/github-actions` is a collection of reusable **GitHub Actions composite actions** for Python projects.

Available actions:

| Action | Purpose |
|---|---|
| `gitversion` | Compute semver from git history via GitVersion |
| `python-setup` | Set up Python, print version, upgrade pip |
| `install-project` | Install a pip-based project with extras |
| `tool-setup` | Combined: python-setup + install-project |
| `ruff-check` | Run ruff lint and format checks, upload JSON report |
| `mypy-check` | Run mypy type check, upload text report |
| `run-tests` | Run pytest, upload results, send coverage to Codecov |
| `sonar-scan` | Download analysis reports, run SonarCloud scan |

## Architecture

```
action-name/
    action.yml        ← composite action definition
README.md             ← global documentation
CHANGELOG.md          ← version history
cliff.toml            ← git-cliff changelog config
GitVersion.yml        ← semver versioning config
.github/
    workflows/
        ci.yml        ← validates action YAML + auto-tags releases
    dependabot.yml    ← weekly updates (pip, github-actions, pre-commit)
```

## Key Constraints

- **Tagging strategy**: Use `@v1` for stable, `@main` only in development
- **Python**: Actions support 3.12, 3.13, 3.14 (target 3.14, retro-compat to 3.12)
- **Inputs/Outputs**: All must be documented with `description` and `required`
- **All actions**: Must have `runs.using: composite`
- **No shell=True** in steps without justification
- **English only**: All action names, descriptions, commit messages

## Versioning

- Tags follow **semver**: `v1`, `v1.0.0`, `v1.0.4`
- The major tag (`v1`) is always moved to point to the latest minor/patch
- GitVersion.yml drives the version computation

## CI/CD

- **CI**: `.github/workflows/ci.yml` — validates all action YAML files, then tags release
- **Only on `main` push**: Creates the semver tag via GitVersion + git-cliff CHANGELOG
- **No sonar** for this repo (no Python/TS source code)

## Development Workflow

1. Create branch: `feature/action-name` or `fix/action-name`
2. Edit `action-name/action.yml`
3. Ensure all inputs have `description` and `required`
4. Commit with conventional commits
5. Open PR → CI validates YAML
6. Merge to main → auto-tagged release
