# Architecture — github-actions

## Purpose

Shared, reusable **composite GitHub Actions** for the `chrysa/*` fleet of
repositories, plus the tested Python and shell entrypoints they call. Consumer
repos reference these actions as `chrysa/github-actions/<action>@v1` instead of
duplicating CI/CD logic. Actions are deployed as-is (YAML) — there is no build or
compile step.

## Stack

- **GitHub Actions** — every action is `using: composite`.
- **Python** `>=3.12` — the `notion_sync` package (Notion sync entrypoints) and
  helper scripts under `scripts/` (`gen_context_files.py`, `quality_gate.py`).
- **Shell (bash)** — lint/gist/branch-policy scripts under `scripts/`.
- **Tooling**: Ruff (lint + format, line-length 110), pytest, actionlint (action
  validation), pre-commit, GitVersion. Packaging via setuptools (`pyproject.toml`,
  package `notion_sync`).
- External CLIs invoked by actions: shellcheck/shfmt, hadolint, helm, yamllint,
  mypy, terraform, SonarCloud scanner, hatch/setuptools, npm.

## Layout

- `*/action.yml` — one composite action per top-level directory (see Entrypoints).
- `notion_sync/` — Python package: `branch_sync.py`, `roadmap_sync.py`,
  `notion_api.py`, `logging_setup.py`.
- `scripts/` — shell + Python helpers called by actions (branch policy, lint
  wrappers, gist publishing, `gen_context_files.py`, `quality_gate.py`).
- `tests/` — pytest suite (`test_actions_yaml.py`, `test_branch_sync.py`,
  `test_notion_api.py`, `test_roadmap_sync.py`, `test_sync_entrypoints.py`).
- `.github/workflows/` — this repo's own CI/CD and reusable workflows (ci*, deploy,
  release, sonar, sast, secret-scan, quality-gate-check, etc.).
- `standards/`, `docs/`, `legal/`, `changelog/` — supporting content.

## Entrypoints (composite actions)

| Action | Description |
|---|---|
| `python-setup` | Set up Python, print version, upgrade pip |
| `install-project` | `pip install -e '.[extras]'` |
| `tool-setup` | python-setup + install-project |
| `run-tests` | Run pytest, upload results, publish to PR, send coverage |
| `ruff-check` | Ruff lint + format checks, upload JSON report |
| `mypy-check` | mypy type check, upload text report |
| `lint-bash` | shellcheck + shfmt over shell scripts |
| `lint-docker` | hadolint over Dockerfiles |
| `lint-helm` | `helm lint --strict` on charts |
| `lint-yaml` | yamllint over YAML files |
| `validate-terraform` | terraform init (no backend), validate, fmt check (never applies) |
| `doc-drift` | Regenerate code-derived docs and fail on drift |
| `changelog` | Changelog generation |
| `gitversion` | Setup + run GitVersion to compute semver from git history |
| `check-branch-policy` | Enforce the chrysa branch model on a PR |
| `notion-branch-sync` | Sync pushed branch state to Notion (`python3 -m notion_sync.branch_sync`) |
| `notion-roadmap-sync` | Sync issue/PR events to Notion roadmap (`python3 -m notion_sync.roadmap_sync`) |
| `gist-publish` | Bump/tag/push the multi-machine setup gist |
| `publish-python-package` | Build + publish Python package to PyPI (hatch/setuptools) |
| `publish-node-package` | Build + publish scoped npm package to GitHub Packages |
| `sonar-scan-python` | SonarCloud scan (Python) |
| `sonar-scan-node` | SonarCloud scan (Node.js / TypeScript) |
| `sonar-js-scan` | SonarCloud scan (JavaScript / Google Apps Script) |
| `sonar-scan` | **[DEPRECATED]** generic SonarCloud scan |

## Data / External deps

- **Notion API** — `notion_sync` reads tokens/DB IDs from action inputs/env and
  writes branch and roadmap state. No secrets are committed; credentials arrive via
  workflow secrets/env.
- **SonarCloud** — scan actions upload analysis using a `SONAR_TOKEN` supplied by
  the caller.
- **PyPI / GitHub Packages (npm)** — publish actions authenticate via caller-provided
  tokens.
- **GitVersion**, **Codecov/coverage** consumers.

## Build & test (real commands)

Composite actions have no build step (`make build` and `make dev` are no-ops).
Verified targets from the `Makefile` / `pyproject.toml`:

```bash
make validate     # actionlint over the composite actions
make test         # validate + pytest
make test-cov     # validate + pytest with coverage
make lint         # ruff lint
make format       # prettier via pre-commit (YAML)
make typecheck    # mypy
make docker-test  # actionlint in Docker (CI-compatible)
make pre-commit   # pre-commit run --all-files
pytest            # run the Python suite directly (testpaths = tests)
ruff check .      # lint (select B,C90,E,F,I,PERF,PL,RUF,SIM,UP; line-length 110)
```

Doc note: the README's action table matches the `action.yml` manifests. Where this
file and the README differ, the manifests are authoritative.
