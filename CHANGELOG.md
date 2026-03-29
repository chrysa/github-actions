# Changelog

## [1.0.2] - 2026-03-29

### Bug Fixes

- Fix: fix changelog generation in release workflow ([`2e857da`](2e857da4006e5ef45fc628cb898d578ca54415c5))
- Fix: reorder changelog steps - generate before tagging, use body_path ([`a70ac45`](a70ac4561b14fd7c36b8dd44dc645df5425b4328))
- Fix: replace preReleaseTag condition with tag existence check ([`2d77e87`](2d77e872591ed29b09e678dc72bbeb0e44692371))

### Features

- Feat: add gitversion action and changelog generation with git-cliff ([`81203cf`](81203cf92fb71cdf55fca82a7b44599747eb0552))

### Miscellaneous

- Chore: add dependabot configuration for github-actions ([`abf0883`](abf088388658a6d35e9d18402639c79e28de36ce))

## [1.0.1] - 2026-03-29

### Bug Fixes

- Fix(sonar): remove qualitygate.wait=true to avoid blocking CI on quality gate failure ([`d0ba6c0`](d0ba6c051b6420791f8052dc3fbdcb4293abc5b1))

## [1.0.0] - 2026-03-29

### Features

- Feat: initial composite actions for chrysa/* repos

Actions:
- python-setup: setup-python + pip upgrade
- install-project: pip install -e '.[extras]' (generic extras input)
- tool-setup: python-setup + install-project (single entry point)
- ruff-check: lint + format + JSON report + upload (inputs: config, sources)
- mypy-check: type check + txt report + upload (inputs: config-file, sources)
- run-tests: pytest + coverage + Codecov + PR publish (inputs: cov-module)
- sonar-scan: download reports + SonarCloud scan (inputs: project-key, org, ...)

Config:
- GitVersion.yml: GitHubFlow, fix=Patch, release=rc
- .pre-commit-config.yaml: trailing-whitespace, check-yaml, beautysh, bashate, detect-secrets
- .github/workflows/ci.yml: validate YAML + tag release (vX.Y.Z + floating vX) ([`d76d02f`](d76d02f0b11accc3befb57092445979136bb7364))


