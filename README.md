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
