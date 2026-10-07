# ARCHITECTURE — github-actions

> Scope: this document describes the *shape* of the repository — what it ships,
> how the pieces relate, and the versioning/consumption model. The per-action
> input/output reference lives in [`README.md`](README.md). Claims are tagged
> **FACT** (verified in-repo), **INFERENCE** (reasoned from evidence),
> **UNKNOWN** (not determinable from the repo).

## 1. Purpose (FACT)

Centralised, reusable **composite GitHub Actions** and **reusable workflows**
consumed across the `chrysa/*` fleet, plus the tested Python entrypoints that
back the Notion-sync actions.

- `pyproject.toml` description: *"Composite GitHub Actions and their tested
  Python entrypoints for the chrysa fleet"* (FACT).
- Consumers pin to the floating major tag `@v1`; only the latest major is
  supported (FACT — `SECURITY.md`, `docs/reference`).

## 2. Component catalogue (FACT)

### 2.1 Composite actions (24 — each is a directory with `action.yml`)

| Action | Inputs (required+optional) | Role |
| --- | --- | --- |
| `python-setup` | 2 | Set up Python + upgrade pip |
| `install-project` | 2 | `pip install -e '.[extras]'` |
| `tool-setup` | 2 | python-setup + install-project |
| `gitversion` | 0 | Compute semver from git history |
| `ruff-check` | 5 | ruff lint + format + JSON report |
| `mypy-check` | 4 | mypy type check + txt report |
| `run-tests` | 5 | pytest + coverage + Codecov |
| `sonar-scan` | 8 | SonarCloud scan (generic Python) |
| `sonar-scan-python` | 13 | SonarCloud scan (Python-specific) |
| `sonar-scan-node` | 7 | SonarCloud scan (Node/TS) |
| `sonar-js-scan` | 11 | SonarCloud scan (JS / Apps Script) |
| `publish-python-package` | 4 | Build + publish to PyPI |
| `publish-node-package` | 4 | Publish scoped npm package to GitHub Packages |
| `notion-branch-sync` | 3 | Sync pushed branch → Notion Branch Activity DB |
| `notion-roadmap-sync` | 2 | Sync issue/PR event → Notion roadmap row |
| `lint-yaml` | 4 | yamllint |
| `lint-bash` | 3 | shellcheck + shfmt |
| `lint-docker` | 3 | hadolint |
| `lint-helm` | 3 | `helm lint --strict` |
| `validate-terraform` | 2 | terraform init/validate/fmt (never applies) |
| `check-branch-policy` | 3 | Enforce chrysa branch model on a PR |
| `gist-publish` | 5 | Version + changelog + publish setup gist |
| `changelog` | 2 | Generate release changelog via git-cliff |
| `doc-drift` | 2 | Regenerate code-derived docs, fail on drift |

(Input counts from `grep -c "required:"` per `action.yml`; treat as approximate.)

### 2.2 Reusable workflows (`workflow_call`, in `.github/workflows/`) (FACT)

Consumable by other repos: `ci-python.yml`, `ci-python-app.yml`,
`ci-fullstack.yml`, `deploy.yml`, `release.yml`, `lint-python.yml`,
`pre-commit.yml`, `sast.yml`, `secret-scan.yml`, `quality-gate-check.yml`,
`mutation-testing.yml`, `enforce-shortcut-link.yml`, `enforce-feature-branch.yml`,
`pr-dependencies.yml`, `dependencies.yml`, `detect-conflicts.yml`,
`pull-request-size.yml`, `labeler.yml`, `sync-labels.yml`, `auto-assign.yml`,
`approved-label.yml`, `update-pr-body.yml`, `action-check.yml`,
`dependabot-auto-merge.yml`, `pages.yml`.

### 2.3 Python entrypoints (`notion_sync/` package) (FACT)

- `branch_sync.py`, `roadmap_sync.py` — logic behind the two Notion actions.
- `notion_api.py` — thin Notion REST client.
- `logging_setup.py`, `__init__.py`.
- Packaged via setuptools (`packages = ["notion_sync"]`); `requires-python >=3.12`.
- Backed by pytest suite in `tests/` (5 test modules).

### 2.4 Shell + Python helpers (`scripts/`) (FACT)

`check_branch_policy.sh`, `lint_{bash,docker,helm,yaml}.sh`,
`gist_{bump_version,changelog,publish}.sh`, `gen_context_files.py`,
`quality_gate.py`. These are invoked by the matching composite actions.

## 3. Consumption & versioning model

- **Versioning**: semver computed by GitVersion (`GitVersion.yml`); branch
  regexes map `chore/`→patch-alpha, `feature/`, etc. (FACT). Release changelog
  via git-cliff (`cliff.toml`) (FACT).
- **Floating major tag**: consumers reference `@v1`; the tag is moved forward on
  release so pinned consumers receive fixes automatically (FACT — `SECURITY.md`).
- **Internal self-reference**: this repo's own workflows call its actions by
  version tag (e.g. `chrysa/github-actions/tool-setup@v1.9.0`) and, in a few
  places, by `@main` (see SECURITY.md §self-reference) (FACT).

## 4. Repository-level artefacts of note

- `graphify` (11 MB), `sys` (33 MB), `graphify-out/`, `guideline-report.html`
  (86 KB) are large tracked artefacts at root (FACT). Whether they *earn their
  place* per the chrysa "every tracked file earns its place" standard is
  **UNKNOWN** / see REVIEW.md.
- Standards are vendored under `standards/rules/` and surfaced through `CLAUDE.md`.

## 5. Related documents

- [`README.md`](README.md) — full per-action usage & inputs.
- [`TRD.md`](TRD.md) — technical requirements & design detail.
- [`CONSTRAINTS.md`](CONSTRAINTS.md) — operating constraints.
- [`SECURITY.md`](SECURITY.md) — reporting policy; [`REVIEW.md`](REVIEW.md) — doc-audit findings.
- [`DECISIONS.md`](DECISIONS.md) — ADRs.
