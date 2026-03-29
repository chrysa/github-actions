# github-actions

[![CI](https://github.com/chrysa/github-actions/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/github-actions/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/chrysa/github-actions?sort=semver&label=release)](https://github.com/chrysa/github-actions/releases/latest)
[![License](https://img.shields.io/github/license/chrysa/github-actions)](LICENSE)

Shared composite GitHub Actions for `chrysa/*` repositories.

## Available actions

| Action | Description |
|---|---|
| `chrysa/github-actions/python-setup@main` | Set up Python + upgrade pip |
| `chrysa/github-actions/install-project@main` | `pip install -e '.[extras]'` |
| `chrysa/github-actions/tool-setup@main` | python-setup + install-project |
| `chrysa/github-actions/ruff-check@main` | ruff lint + format + JSON report |
| `chrysa/github-actions/mypy-check@main` | mypy type check + txt report |
| `chrysa/github-actions/run-tests@main` | pytest + coverage + Codecov |
| `chrysa/github-actions/sonar-scan@main` | SonarCloud scan |

## Usage

```yaml
- uses: chrysa/github-actions/tool-setup@main
  with:
    python-version: '3.14'
    extras: 'lint,test'

- uses: chrysa/github-actions/ruff-check@main
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    config: config-tools/ruff.toml
    sources: 'src tests'
```
