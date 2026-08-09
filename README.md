# github-actions

[![CI](https://github.com/chrysa/github-actions/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/github-actions/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/chrysa/github-actions?sort=semver&label=release)](https://github.com/chrysa/github-actions/releases/latest)
[![License](https://img.shields.io/github/license/chrysa/github-actions)](LICENSE)

Shared composite GitHub Actions for `chrysa/*` repositories.

## Versioning &amp; pinning

Releases are tagged with semantic-version tags (`vMAJOR.MINOR.PATCH`, latest
`v1.8.0`) computed by GitVersion. **Pin every `uses:` reference to an immutable
ref — never the floating `@main` branch.** Per the chrysa CI standard,
`chrysa/github-actions` and `actions/*` are pinned **by tag** (e.g. `@v1.8.0`),
while third-party actions are pinned by **full commit SHA** with the version in
a trailing comment. This mirrors this repo's own workflows: every third-party
action in `.github/workflows/*` is pinned by a full commit SHA.

The examples below use `@v1.8.0`. Bump the tag deliberately — Dependabot's
`github-actions` ecosystem raises the update PRs.

## Available actions

| Action | Description |
|---|---|
| `chrysa/github-actions/python-setup@v1.8.0` | Set up Python + upgrade pip |
| `chrysa/github-actions/install-project@v1.8.0` | `pip install -e '.[extras]'` |
| `chrysa/github-actions/tool-setup@v1.8.0` | python-setup + install-project |
| `chrysa/github-actions/gitversion@v1.8.0` | Compute semver from git history |
| `chrysa/github-actions/ruff-check@v1.8.0` | ruff lint + format + JSON report |
| `chrysa/github-actions/mypy-check@v1.8.0` | mypy type check + txt report |
| `chrysa/github-actions/run-tests@v1.8.0` | pytest + coverage + Codecov |
| `chrysa/github-actions/sonar-scan@v1.8.0` | SonarCloud scan (generic Python) |
| `chrysa/github-actions/sonar-scan-python@v1.8.0` | SonarCloud scan (Python-specific) |
| `chrysa/github-actions/sonar-scan-node@v1.8.0` | SonarCloud scan (Node.js / TypeScript) |
| `chrysa/github-actions/sonar-js-scan@v1.8.0` | SonarCloud scan (JS / Google Apps Script) |
| `chrysa/github-actions/publish-python-package@v1.8.0` | Build + publish Python package to PyPI |
| `chrysa/github-actions/publish-node-package@v1.8.0` | Build + publish a scoped npm package to GitHub Packages (private GHCR npm) |
| `chrysa/github-actions/notion-branch-sync@v1.8.0` | Sync the pushed branch to the Notion Branch Activity database |
| `chrysa/github-actions/notion-roadmap-sync@v1.8.0` | Sync an issue/PR event to the Notion roadmap row |
| `chrysa/github-actions/lint-yaml@v1.8.0` | yamllint over the repo's YAML |
| `chrysa/github-actions/lint-bash@v1.8.0` | shellcheck + shfmt over shell scripts |
| `chrysa/github-actions/lint-docker@v1.8.0` | hadolint over Dockerfiles |
| `chrysa/github-actions/lint-helm@v1.8.0` | `helm lint --strict` per chart |
| `chrysa/github-actions/validate-terraform@v1.8.0` | terraform init/validate/fmt (never applies) |
| `chrysa/github-actions/check-branch-policy@v1.8.0` | Enforce the chrysa branch model on a PR |
| `chrysa/github-actions/gist-publish@v1.8.0` | Version, changelog and publish the multi-machine setup gist |

## Usage

### python-setup

Set up Python and upgrade pip.

```yaml
- uses: chrysa/github-actions/python-setup@v1.8.0
  with:
    python-version: '3.14'
```

### install-project

Install a pip-based project with optional extras.

```yaml
# Minimal
- uses: chrysa/github-actions/install-project@v1.8.0

# With extras
- uses: chrysa/github-actions/install-project@v1.8.0
  with:
    extras: 'lint,test,dead_code'
```

### tool-setup

Combined Python setup + project install (wraps python-setup + install-project).

```yaml
- uses: chrysa/github-actions/tool-setup@v1.8.0
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
  uses: chrysa/github-actions/gitversion@v1.8.0

- run: echo "Version: ${{ steps.version.outputs.semVer }}"
```

**Outputs:** `semVer`, `majorMinorPatch`, `major`, `minor`, `patch`, `preReleaseTag`, `fullSemVer`

### ruff-check

Run ruff lint and format checks, upload JSON report on latest Python.

```yaml
- uses: chrysa/github-actions/ruff-check@v1.8.0
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    sources: 'src tests'

# With custom config
- uses: chrysa/github-actions/ruff-check@v1.8.0
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    config: 'config-tools/ruff.toml'
    sources: 'src tests'
```

### mypy-check

Run mypy type check and upload text report on latest Python.

```yaml
- uses: chrysa/github-actions/mypy-check@v1.8.0
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    sources: 'src'

# With custom config
- uses: chrysa/github-actions/mypy-check@v1.8.0
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    config-file: 'pyproject.toml'
    sources: 'src'
```

### run-tests

Run pytest suite, upload results, publish to PR and send coverage to Codecov.

```yaml
- uses: chrysa/github-actions/run-tests@v1.8.0
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    cov-module: 'my_package'
```

### sonar-scan

Download analysis reports and run SonarCloud scan (generic Python).

```yaml
- uses: chrysa/github-actions/sonar-scan@v1.8.0
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
- uses: chrysa/github-actions/sonar-scan-python@v1.8.0
  with:
    python-version: '3.14'
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    project-key: 'chrysa_my-project'
    organization: 'chrysa'
    project-name: 'my-project'

# Full
- uses: chrysa/github-actions/sonar-scan-python@v1.8.0
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
- uses: chrysa/github-actions/sonar-scan-node@v1.8.0
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
- uses: chrysa/github-actions/sonar-js-scan@v1.8.0
  with:
    sonar-token: ${{ secrets.SONAR_TOKEN }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    project-key: 'chrysa_my-project'
    organization: 'chrysa'
    project-name: 'my-project'

# Full (with coverage artifact)
- uses: chrysa/github-actions/sonar-js-scan@v1.8.0
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
- uses: chrysa/github-actions/publish-python-package@v1.8.0
  with:
    pypi-token: ${{ secrets.PYPI_TOKEN }}

# With setuptools
- uses: chrysa/github-actions/publish-python-package@v1.8.0
  with:
    pypi-token: ${{ secrets.PYPI_TOKEN }}
    build-backend: 'setuptools'

# Publish to TestPyPI
- uses: chrysa/github-actions/publish-python-package@v1.8.0
  with:
    pypi-token: ${{ secrets.TEST_PYPI_TOKEN }}
    build-backend: 'hatch'
    repository-url: 'https://test.pypi.org/legacy/'
```

### publish-node-package

Build and publish a scoped npm package to **GitHub Packages** (the private GHCR npm
registry, `https://npm.pkg.github.com`). The package selects the registry via its own
`publishConfig.registry`; auth uses the workflow `GITHUB_TOKEN` (never a plaintext PAT),
and the job needs `permissions: { packages: write }`.

```yaml
- uses: chrysa/github-actions/publish-node-package@v1.8.0
  with:
    package-dir: packages/typescript/ui
    node-auth-token: ${{ secrets.GITHUB_TOKEN }}

# Override the Node version or scope
- uses: chrysa/github-actions/publish-node-package@v1.8.0
  with:
    package-dir: packages/typescript/api-client
    node-auth-token: ${{ secrets.GITHUB_TOKEN }}
    node-version: '22'
    scope: '@chrysa'
```


### notion-branch-sync

Sync the pushed branch (commit, PR count, CI status, changelog excerpt) to the shared
Notion "Branch Activity" database. Requires a full-history checkout for the changelog.

```yaml
- uses: actions/checkout@v7.0.1
  with:
    fetch-depth: 0
- uses: chrysa/github-actions/notion-branch-sync@v1.8.0
  with:
    notion-token: ${{ secrets.NOTION_TOKEN }}
    branches-db-id: ${{ vars.NOTION_BRANCHES_DB_ID }}
    project-block-id: ${{ vars.NOTION_PROJECT_BLOCK_ID }}  # optional, main/master changelog sync
```

### notion-roadmap-sync

Sync an issue or pull-request event to the project's Notion roadmap table row.

```yaml
- uses: chrysa/github-actions/notion-roadmap-sync@v1.8.0
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
- uses: chrysa/github-actions/lint-yaml@v1.8.0
  with:
    config-file: .yamllint.yaml
    exclude-paths: "./.git/* ./archive/*"

- uses: chrysa/github-actions/lint-bash@v1.8.0    # severity, indent, exclude-paths
- uses: chrysa/github-actions/lint-docker@v1.8.0   # hadolint-version, failure-threshold
- uses: chrysa/github-actions/lint-helm@v1.8.0
  with:
    charts-root: apps
    helm-repositories: |
      bjw-s https://bjw-s-labs.github.io/helm-charts
      traefik https://helm.traefik.io/traefik

- uses: chrysa/github-actions/validate-terraform@v1.8.0
  with:
    working-directory: terraform
```

### check-branch-policy

Enforce the branch model on a pull request: `develop -> main` is the release promotion,
`hotfix/*` is the only other branch allowed to target `main`, everything else must match
`type/short-description` and integrate through `develop`.

```yaml
- uses: chrysa/github-actions/check-branch-policy@v1.8.0
```

### gist-publish

Bump `SETUP_VERSION`, write the changelog entry, tag, and push the multi-machine setup
files to the private gist. Extracted from a 149-line workflow duplicated byte-identically
in `chrysa-skills` and `claude-config`.

```yaml
- uses: chrysa/github-actions/gist-publish@v1.8.0
  with:
    gist-token: ${{ secrets.GH_PAT_GIST }}
    gist-id: ${{ secrets.CHRYSA_SETUP_GIST_ID }}
    bump: ${{ github.event.inputs.bump }}
```
