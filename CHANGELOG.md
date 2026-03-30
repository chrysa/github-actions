# Changelog

## [1.0.6] - 2026-03-30

### Miscellaneous

- Chore: add gitignore, copilot-instructions, instruction files (#7) ([`03b4d11`](03b4d110b7787d8fe6ea60257719e3dff71c0695))

## [1.0.5] - 2026-03-30

### Miscellaneous

- Chore: add Copilot instructions file (#5)

Co-authored-by: anthony-greau <anthony.greau@padam.io> ([`e4a173b`](e4a173be84a9502e4a1174bb122fc58e96d71f03))
- Chore: update CHANGELOG.md for v1.0.5 [skip ci] ([`2166540`](2166540f045379b10146536a17e8d22b116c8370))

## [1.0.4] - 2026-03-29

### Miscellaneous

- Chore: uniformize YAML syntax to match padam-av style (--- header, 4-space indent, timeout-minutes, shell: bash) ([`e05adfd`](e05adfd7981446417bbf0fdd905f1af232e19daa))

## [1.0.3] - 2026-03-29

### Documentation

- Docs: add CI, release and license badges to README ([`87a8f4f`](87a8f4fd2b22a51dad7fb7848de3a91b0c3db1aa))

### Miscellaneous

- Chore: update CHANGELOG.md for v1.0.3 [skip ci] ([`5ef783d`](5ef783dc8ce27f80d6ee28481765b5b49f81b6d6))

## [1.0.2] - 2026-03-29

### Bug Fixes

- Fix: fix changelog generation in release workflow ([`2e857da`](2e857da4006e5ef45fc628cb898d578ca54415c5))
- Fix: reorder changelog steps - generate before tagging, use body_path ([`a70ac45`](a70ac4561b14fd7c36b8dd44dc645df5425b4328))
- Fix: replace preReleaseTag condition with tag existence check ([`2d77e87`](2d77e872591ed29b09e678dc72bbeb0e44692371))

### Features

- Feat: add gitversion action and changelog generation with git-cliff ([`81203cf`](81203cf92fb71cdf55fca82a7b44599747eb0552))

### Miscellaneous

- Chore: add dependabot configuration for github-actions ([`abf0883`](abf088388658a6d35e9d18402639c79e28de36ce))
- Chore: update CHANGELOG.md for v1.0.2 [skip ci] ([`1452774`](14527749daee477413ea283a359c6fa0d4377a9b))

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


