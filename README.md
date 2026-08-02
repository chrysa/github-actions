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
| `chrysa/github-actions/gitversion@main` | Compute semver from git history |
| `chrysa/github-actions/ruff-check@main` | ruff lint + format + JSON report |
| `chrysa/github-actions/mypy-check@main` | mypy type check + txt report |
| `chrysa/github-actions/run-tests@main` | pytest + coverage + Codecov |
| `chrysa/github-actions/sonar-scan@main` | SonarCloud scan (generic Python) |
| `chrysa/github-actions/sonar-scan-python@main` | SonarCloud scan (Python-specific) |
| `chrysa/github-actions/sonar-scan-node@main` | SonarCloud scan (Node.js / TypeScript) |
| `chrysa/github-actions/sonar-js-scan@main` | SonarCloud scan (JS / Google Apps Script) |
| `chrysa/github-actions/publish-python-package@main` | Build + publish Python package to PyPI |
| `chrysa/github-actions/notion-branch-sync@main` | Sync the pushed branch to the Notion Branch Activity database |
| `chrysa/github-actions/notion-roadmap-sync@main` | Sync an issue/PR event to the Notion roadmap row |
| `chrysa/github-actions/lint-yaml@main` | yamllint over the repo's YAML |
| `chrysa/github-actions/lint-bash@main` | shellcheck + shfmt over shell scripts |
| `chrysa/github-actions/lint-docker@main` | hadolint over Dockerfiles |
| `chrysa/github-actions/lint-helm@main` | `helm lint --strict` per chart |
| `chrysa/github-actions/validate-terraform@main` | terraform init/validate/fmt (never applies) |
| `chrysa/github-actions/check-branch-policy@main` | Enforce the chrysa branch model on a PR |

## Usage

### python-setup

Set up Python and upgrade pip.

```yaml
- uses: chrysa/github-actions/python-setup@main
  with:
    python-version: '3.14'
```

### install-project

Install a pip-based project with optional extras.

```yaml
# Minimal
- uses: chrysa/github-actions/install-project@main

# With extras
- uses: chrysa/github-actions/install-project@main
  with:
    extras: 'lint,test,dead_code'
```

### tool-setup

Combined Python setup + project install (wraps python-setup + install-project).

```yaml
- uses: chrysa/github-actions/tool-setup@main
  with:
    python-version: '3.14'
    extras: 'lint,test'
```

### gitversion

Compute semantic versioning from git history using GitVersion.

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0

- id: version
  uses: chrysa/github-actions/gitversion@main

- run: echo "Version: ${{ steps.version.outputs.semVer }}"
```

**Outputs:** `semVer`, `majorMinorPatch`, `major`, `minor`, `patch`, `preReleaseTag`, `fullSemVer`

### ruff-check

Run ruff lint and format checks, upload JSON report on latest Python.

```yaml
- uses: chrysa/github-actions/ruff-check@main
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    sources: 'src tests'

# With custom config
- uses: chrysa/github-actions/ruff-check@main
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    config: 'config-tools/ruff.toml'
    sources: 'src tests'
```

### mypy-check

Run mypy type check and upload text report on latest Python.

```yaml
- uses: chrysa/github-actions/mypy-check@main
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    sources: 'src'

# With custom config
- uses: chrysa/github-actions/mypy-check@main
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    config-file: 'pyproject.toml'
    sources: 'src'
```

### run-tests

Run pytest suite, upload results, publish to PR and send coverage to Codecov.

```yaml
- uses: chrysa/github-actions/run-tests@main
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    cov-module: 'my_package'
```

### sonar-scan

Download analysis reports and run SonarCloud scan (generic Python).

```yaml
- uses: chrysa/github-actions/sonar-scan@main
  with:
    latest-python: '3.14'
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    project-key: 'chrysa_my-project'
    organization: 'chrysa'
    project-name: 'my-project'
    sources: 'src'
    tests: 'tests'
```

### sonar-scan-python

Download Python analysis reports and run SonarCloud scan with Python-specific configuration.
Simplified interface with configurable report paths.

```yaml
# Minimal
- uses: chrysa/github-actions/sonar-scan-python@main
  with:
    python-version: '3.14'
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    project-key: 'chrysa_my-project'
    organization: 'chrysa'
    project-name: 'my-project'

# Full
- uses: chrysa/github-actions/sonar-scan-python@main
  with:
    python-version: '3.14'
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    project-key: 'chrysa_my-project'
    organization: 'chrysa'
    project-name: 'my-project'
    sources: 'src,lib'
    tests: 'tests'
    coverage-report: 'reports/coverage.xml'
    ruff-report: 'reports/ruff.json'
    mypy-report: 'reports/mypy.txt'
    junit-report: 'reports/junit.xml'
```

### sonar-scan-node

Run SonarCloud scan for Node.js / TypeScript projects.

```yaml
- uses: chrysa/github-actions/sonar-scan-node@main
  with:
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    project-key: 'chrysa_my-project'
    organization: 'chrysa'
    project-name: 'my-project'
    sources: 'src'
    tsconfig: 'tsconfig.json'
```

### sonar-js-scan

Run SonarCloud scan for JavaScript / Google Apps Script projects, with optional artifact download.

```yaml
# Minimal
- uses: chrysa/github-actions/sonar-js-scan@main
  with:
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    project-key: 'chrysa_my-project'
    organization: 'chrysa'
    project-name: 'my-project'

# Full (with coverage artifact)
- uses: chrysa/github-actions/sonar-js-scan@main
  with:
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    project-key: 'chrysa_my-project'
    organization: 'chrysa'
    project-name: 'my-project'
    sources: 'src'
    tests: 'tests'
    js-file-suffixes: '.js,.gs,.ts,.jsx,.tsx'
    coverage-report-paths: 'coverage/lcov.info'
    artifact-name: 'coverage-lcov'
    artifact-path: 'coverage/'
```

### publish-python-package

Build and publish a Python package to PyPI.

```yaml
# With hatch (default)
- uses: chrysa/github-actions/publish-python-package@main
  with:
    pypi-token: ${{ secrets.PYPI_TOKEN }}

# With setuptools
- uses: chrysa/github-actions/publish-python-package@main
  with:
    pypi-token: ${{ secrets.PYPI_TOKEN }}
    build-backend: 'setuptools'

# Publish to TestPyPI
- uses: chrysa/github-actions/publish-python-package@main
  with:
    pypi-token: ${{ secrets.TEST_PYPI_TOKEN }}
    build-backend: 'hatch'
    repository-url: 'https://test.pypi.org/legacy/'
```

### notion-branch-sync

Sync the pushed branch (commit, PR count, CI status, changelog excerpt) to the shared
Notion "Branch Activity" database. Requires a full-history checkout for the changelog.

```yaml
- uses: actions/checkout@v7.0.1
  with:
    fetch-depth: 0
- uses: chrysa/github-actions/notion-branch-sync@main
  with:
    notion-token: ${{ secrets.NOTION_TOKEN }}
    branches-db-id: ${{ vars.NOTION_BRANCHES_DB_ID }}
    project-block-id: ${{ vars.NOTION_PROJECT_BLOCK_ID }}  # optional, main/master changelog sync
```

### notion-roadmap-sync

Sync an issue or pull-request event to the project's Notion roadmap table row.

```yaml
- uses: chrysa/github-actions/notion-roadmap-sync@main
  with:
    notion-token: ${{ secrets.NOTION_TOKEN }}
    block-id: ${{ vars.NOTION_PROJECT_BLOCK_ID }}
```

## Python entrypoints

Action logic that outgrows a one-line `run:` lives in `notion_sync/` and is unit-tested
(`tests/`, run by `make test`) — workflows stay glue, per the fleet GitHub Actions standard.

### lint-yaml / lint-bash / lint-docker / lint-helm / validate-terraform

Infrastructure linters extracted from `chrysa/server`, where they lived as repo-local
composite actions. Every path/version is an input, so any repo can consume them.

```yaml
- uses: chrysa/github-actions/lint-yaml@main
  with:
    config-file: .yamllint.yaml
    exclude-paths: "./.git/* ./archive/*"

- uses: chrysa/github-actions/lint-bash@main       # severity, indent, exclude-paths
- uses: chrysa/github-actions/lint-docker@main     # hadolint-version, failure-threshold
- uses: chrysa/github-actions/lint-helm@main
  with:
    charts-root: apps
    helm-repositories: |
      bjw-s https://bjw-s-labs.github.io/helm-charts
      traefik https://helm.traefik.io/traefik

- uses: chrysa/github-actions/validate-terraform@main
  with:
    working-directory: terraform
```

### check-branch-policy

Enforce the branch model on a pull request: `develop -> main` is the release promotion,
`hotfix/*` is the only other branch allowed to target `main`, everything else must match
`type/short-description` and integrate through `develop`.

```yaml
- uses: chrysa/github-actions/check-branch-policy@main
```
