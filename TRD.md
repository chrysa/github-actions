# TRD — github-actions

> Technical Requirements Document for the chrysa shared GitHub Actions repository.
> Claims tagged **FACT / INFERENCE / UNKNOWN**. Requirements below are derived
> from repo evidence; a requirement is **IMPLEMENTED** only where verifiable in
> the tree. See also [ARCHITECTURE.md](ARCHITECTURE.md), [REQUIREMENTS.md](REQUIREMENTS.md).

## 1. Overview (FACT)

The repo delivers three product surfaces:

1. **Composite actions** (`*/action.yml`, `using: composite`) — reusable CI steps.
2. **Reusable workflows** (`.github/workflows/*.yml` with `on: workflow_call`).
3. **Python entrypoints** (`notion_sync/`) invoked by the Notion-sync actions,
   with a pytest suite (`tests/`).

## 2. Runtime & platform (FACT)

- Runner: GitHub-hosted Actions runners (composite shell = `bash`).
- Python: `requires-python >= 3.12` (`pyproject.toml`); actions accept a
  `python-version` matrix input where relevant.
- Node/TypeScript surfaces served by `sonar-scan-node`, `sonar-js-scan`,
  `publish-node-package` (INFERENCE from names + README).
- Build backend: setuptools (`build-backend = "setuptools.build_meta"`).

## 3. Interface contract (FACT)

- Each composite action declares typed `inputs` with `description` and
  `required` flags; several declare `default`s (e.g. `ruff-check.config =
  pyproject.toml`, `working-directory = .`).
- Inputs are passed to shell steps via `env:` mapping (e.g. `RUFF_CONFIG`,
  `RUFF_SOURCES`) rather than direct `${{ }}` interpolation into `run:` — this
  is the injection-safe pattern (FACT, verified in `ruff-check/action.yml`;
  INFERENCE that it is uniform — spot-checked, not exhaustively audited).
- Reports (ruff.json, mypy txt, coverage) are uploaded as artifacts on the
  latest-python matrix leg only (`if: always() && python-version == latest-python`).

## 4. Secret handling (FACT)

- No hardcoded secrets found (grep for `ghp_`, `glpat`, `AKIA`, PEM headers,
  inline tokens returned nothing in `*/action.yml` and `.github/workflows/*`).
- Secrets flow only through caller-provided inputs / `${{ secrets.* }}`:
  e.g. `publish-python-package` uses `TWINE_PASSWORD: ${{ inputs.pypi-token }}`;
  `deploy.yml` uses `password: ${{ secrets.GITHUB_TOKEN }}`.
- Policy: `secrets: inherit` is forbidden; callers name secrets explicitly
  (FACT — `SECURITY.md`).

## 5. Quality gates in this repo (FACT)

- Pre-commit is the lint source of truth (`.pre-commit-config.yaml`); lint is
  replayed in CI **only at release time** to cut Actions billing
  (FACT — `DECISIONS.md` D-0002).
- `make ci` = lint + typecheck + test; `make lint` runs actionlint + pre-commit.
- pytest config: `testpaths = ["tests"]`, `pythonpath = ["."]`, `-q`.
- ruff: line-length 110, target py312, rule set `B,C90,E,F,I,PERF,PL,RUF,SIM,UP`;
  excludes `.claude` and `scripts/quality_gate.py`.
- SAST + secret-scan workflows present (`sast.yml`, `secret-scan.yml`).

## 6. Versioning & release (FACT)

- GitVersion computes semver from branch/commit history (`GitVersion.yml`,
  ContinuousDeployment mode per branch class).
- git-cliff generates the changelog (`cliff.toml`, `CHANGELOG.md`).
- Consumers pin `@v1`; the floating major tag is advanced on release.

## 7. Known technical risks (INFERENCE — detail in [REVIEW.md](REVIEW.md) / [SECURITY.md](SECURITY.md))

- Third-party actions pinned to mutable tags, not commit SHAs.
- Some internal references use `@main`.
- Several `workflow_call` workflows omit an explicit top-level `permissions:` block.
