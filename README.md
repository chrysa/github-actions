# github-actions

[![CI](https://github.com/chrysa/github-actions/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/github-actions/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/chrysa/github-actions?sort=semver&label=release)](https://github.com/chrysa/github-actions/releases/latest)
[![License](https://img.shields.io/github/license/chrysa/github-actions)](LICENSE)

Reusable composite GitHub Actions that wire up CI for `chrysa/*` repos — Python setup, lint, type-check, tests, SonarCloud, semver, doc-drift and PyPI publish — so each repo references one action instead of duplicating step YAML.

**For:** developers maintaining or wiring CI on a `chrysa/*` repository who want the shared, version-pinned building blocks instead of copy-pasted workflow steps.

Reference each action by its sub-folder path: `uses: chrysa/github-actions/<action>@<ref>`. Pin `<ref>` to a release tag (e.g. `@v1.0.7`) for reproducible CI; `@main` tracks the latest.

## Available actions

| Action | Description | Key inputs |
|---|---|---|
| `python-setup` | Set up Python (`actions/setup-python`) + upgrade pip | `python-version` (req), `cache` |
| `install-project` | `pip install -e '.[extras]'` | `extras`, `working-directory` |
| `tool-setup` | python-setup + install-project combined | `python-version` (req), `extras` |
| `gitversion` | Compute semver from git history (GitVersion) | — (outputs only) |
| `ruff-check` | ruff lint + format, upload JSON report on latest Python | `python-version` (req), `latest-python` (req), `sources` (req), `config`, `working-directory` |
| `mypy-check` | mypy type check, upload text report on latest Python | `python-version` (req), `latest-python` (req), `sources` (req), `config-file` |
| `run-tests` | pytest + coverage, publish to PR, upload to Codecov | `python-version` (req), `latest-python` (req), `cov-module` |
| `doc-drift` | Regenerate code-derived docs, fail if they drift from committed copy | `paths` (`docs/`), `target` (`docs-code`) |
| `sonar-scan` | SonarCloud scan (generic Python) | `sonar-token`, `github-token`, `project-key`, `organization`, `project-name` |
| `sonar-scan-python` | SonarCloud scan (Python-specific, configurable report paths) | same + `coverage-report`, `ruff-report`, `mypy-report`, `junit-report` |
| `sonar-scan-node` | SonarCloud scan (Node.js / TypeScript) | same + `tsconfig` |
| `sonar-js-scan` | SonarCloud scan (JS / Google Apps Script) | same + `js-file-suffixes`, `coverage-report-paths` |
| `publish-python-package` | Build + publish Python package to PyPI | `pypi-token` (req), `build-backend`, `repository-url` |

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

### doc-drift

Regenerate code-derived docs via a make target and fail the job if the committed copy is stale (checks `git diff` on the inspected paths).

```yaml
- uses: chrysa/github-actions/doc-drift@main
  with:
    target: 'docs-code'
    paths: 'docs/'
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

## Minimal CI job

A matrix lint + test job using the shared actions:

```yaml
jobs:
  check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12', '3.14']
    steps:
      - uses: actions/checkout@v4
      - uses: chrysa/github-actions/tool-setup@main
        with:
          python-version: ${{ matrix.python-version }}
          extras: 'lint,test'
      - uses: chrysa/github-actions/ruff-check@main
        with:
          python-version: ${{ matrix.python-version }}
          latest-python: '3.14'
          sources: 'src tests'
      - uses: chrysa/github-actions/run-tests@main
        with:
          python-version: ${{ matrix.python-version }}
          latest-python: '3.14'
          cov-module: 'my_package'
```

## Docs

- [CHANGELOG.md](CHANGELOG.md) — release history
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution guide
- [DECISIONS.md](DECISIONS.md) — architecture decision records
- [docs/specs/spec-v1.md](docs/specs/spec-v1.md) — design spec
