# CLAUDE.md — github-actions

## Vision

Shared composite GitHub Actions for all `chrysa/*` repositories.
Provides standardized CI building blocks to avoid duplicating CI logic across projects.

## Available actions

| Action path | Description |
|-------------|-------------|
| `chrysa/github-actions/python-setup@main` | Set up Python + upgrade pip |
| `chrysa/github-actions/install-project@main` | `pip install -e '.[extras]'` |
| `chrysa/github-actions/tool-setup@main` | python-setup + install-project (legacy) |
| `chrysa/github-actions/ruff-check@main` | ruff lint + format check + JSON report |
| `chrysa/github-actions/mypy-check@main` | mypy type check + txt report |
| `chrysa/github-actions/run-tests@main` | pytest + coverage + Codecov upload |
| `chrysa/github-actions/sonar-scan@main` | SonarCloud scan for Python projects |
| `chrysa/github-actions/sonar-js-scan@main` | SonarCloud scan for JS/TS projects |
| `chrysa/github-actions/gitversion@main` | GitVersion version calculation |

## Usage pattern

### Python project

```yaml
- uses: chrysa/github-actions/python-setup@main
  with:
    python-version: "3.14"

- uses: chrysa/github-actions/install-project@main
  with:
    extras: "dev"

- uses: chrysa/github-actions/ruff-check@main
  with:
    config: config-tools/ruff.toml
    sources: "src tests"

- uses: chrysa/github-actions/run-tests@main
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: "3.14"

- uses: chrysa/github-actions/sonar-scan@main
  with:
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    project-key: chrysa_my-project
    sources: src
    tests: tests
```

### Multi-package project (chrysa-lib pattern)

For repos with multiple packages where `tool-setup@v1` cannot be used directly:

```yaml
- uses: chrysa/github-actions/python-setup@main
  with:
    python-version: "3.12"

- name: Install packages
  run: |
    for pkg in packages/python/api packages/python/auth; do
      pip install -e "$pkg[dev]"
    done
```

## Important: tool-setup@v1 is deprecated

Use `python-setup@main` + `install-project@main` directly instead of `tool-setup@main`.
`tool-setup@v1` will not be maintained further.

## SonarCloud configuration (no sonar-project.properties)

All SonarCloud configuration must go in CI parameters — never in `sonar-project.properties`.

```yaml
- uses: chrysa/github-actions/sonar-scan@main
  with:
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    project-key: chrysa_my-project
    organization: chrysa
    sources: api
    tests: tests
    coverage-report: coverage.xml
    exclusions: "**/__pycache__/**,**/migrations/**"
```

## Structure

```
python-setup/action.yml         # Setup Python + pip upgrade
install-project/action.yml      # pip install -e '.[extras]'
tool-setup/action.yml           # Legacy: python-setup + install-project
ruff-check/action.yml           # Ruff lint + format
mypy-check/action.yml           # Mypy type check
run-tests/action.yml            # pytest + coverage
sonar-scan/action.yml           # SonarCloud (Python)
sonar-js-scan/action.yml        # SonarCloud (JS/TS)
gitversion/action.yml           # GitVersion calculation
```

## Conventions

- All actions use `runs: using: composite`
- All action.yml files must have `name`, `description`, `inputs`, and `runs`
- All inputs must have `required` and `description`
- All code, comments, and docs in English
- Breaking changes require a version bump via GitVersion

## Branch strategy

- `main` — protected, only via PR
- `feat/*` — new actions
- `fix/*` — bug fixes
- `chore/*` — maintenance

## Quickstart

Test an action locally using [act](https://github.com/nektos/act):

```bash
act -j test
```
