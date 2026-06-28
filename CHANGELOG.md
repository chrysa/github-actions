# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-06-28
### Documentation

- Self-hosted CI design + implementation plan (exit Actions billing) (#150)


### Features

- **deploy:** Add frontend-target input (separate from backend target) (#151)


### Miscellaneous

- **standards:** Distribute shared standards (Notion logging) (#149)


## [1.2.4] - 2026-06-26
### Bug Fixes

- **ci-fullstack:** Install pre-commit before running make pre-commit gate


## [1.2.3] - 2026-06-26
### Bug Fixes

- **actions:** Self-install lint tools when absent (kill exit-127 reds) (#133)

- **pre-commit:** Drop leaked canonical-drift local hooks (#134)

- **release:** Tag with majorMinorPatch for clean SemVer tags (#140)

- **release:** Floor next-version to 1.2.2 to unstick self-versioning (#141)

- Resolve SonarCloud blocker & critical findings (#144)

- **quality-gate:** Skip verify when 'quality-gate-verify' target is absent (#148)


### CI

- Pin gregsdennis/dependencies-action to @v1.4.1 (#130)


### Miscellaneous

- Sync chrysa shared standards (#131)

- Sync chrysa shared standards (#132)

- Adopt canonical GitVersion.yml (ContinuousDeployment) (#135)

- Adopt canonical cliff.toml (#136)

- Sync chrysa shared standards (#138)

- Sync chrysa shared standards (#139)

- Sync chrysa shared standards (#142)

- Sync chrysa shared standards (#145)


### Style

- Apply pre-commit autofixes (eof/yaml-sort/json-sort) (#137)


## [1.2.0] - 2026-06-14
### Bug Fixes

- **secret-scan:** Grant pull-requests:read for gitleaks PR commit listing (#98)

- **secret-scan:** Move permissions to job level (top-level broke reusable startup) (#99)

- **sonar-scan-python:** Skip sonar.tests for non-existent test dirs (#107)

- **lint-python:** Resolve tool-setup via fully-qualified path (#110)

- **pre-commit:** Repair makefile-check hook indentation (#112)

- **ci:** Typecheck-paths input for ci-python reports job (#119)

- **ci:** Typecheck-paths input for ci-python reports job (#120)


### CI

- Fix dead label-sync action (marocchino 404 -> crazy-max v6) (#101)

- **pre-commit:** Wire makefile-check hook (v0.1.1-94) (#111)


### Features

- Add doc-drift composite action (#105)

- **workflows:** Reusable lint-python workflow for release-gated lint (#106)

- **ci:** Reusable lean ci-python workflow (#118)

- **ci:** Reusable ci-python-app workflow (compose-backed) (#121)

- **ci:** Reusable ci-fullstack workflow (Makefile-contract driven) (#122)

- **deploy:** Reusable deploy workflow (ghcr build/push + catalog gitops) (#123)

- **deploy:** Add backend/frontend build-args inputs (#124)

- **deploy:** Add frontend-target input (#125)


### Miscellaneous

- **standards:** Realign gitignore + sonar pin (#100)

- **config:** Normalize repo to chrysa standard (#109)

- **makefile:** Declare makefile-tier (lib) (#108)

- **claude:** Dump shared agents + .mcp.json + settings (#113)


## [1.1.2] - 2026-06-03
### Bug Fixes

- **sonar-scan-python:** Revert to sonarqube-scan-action@v5 (fixes api.sonarcloud.io 404) (#97)


### Miscellaneous

- **standards:** Realign gitignore + pre-commit + sonar (#96)


## [1.1.0] - 2026-06-03
### Bug Fixes

- **security:** Prevent script injection via env vars (S7630)

- **security:** Scope permissions to jobs and add --only-binary (S8233/S8541)

- **ci:** Fix S7630 script injection and S8541/S8544 pip flags

- **yaml:** Quote run values containing :all: to prevent YAML parsing errors (#50)

- **yaml:** Quote pip :all: run values + migrate to actionlint (#51)

- Yaml colon in run values (#52)

- **yaml:** Quote run values with colons to prevent YAML parsing errors (#54)

- **actions:** Fix YAML colon in run values, standards compliance, dependabot groups (#59)

- **sonar-scan-python:** Upgrade sonarqube-scan-action from v5 to v8 (#62)

- **sonar-scan-python:** Pin scanner to 5.0.1.3006 to avoid /analysis/analyses 404 (#64)

- **yaml:** Handle YAML colon in run values (#72)

- **pre-commit:** Apply yaml-sorter formatting to action files (#83)

- **ci:** Implement dependabot-auto-merge as reusable workflow_call (#93)

- **sonar:** Repair sonar-scan-python (dead scanner pin → Maven Central + retry) (#95)


### CI

- Extend run-tests composite with cov-fail-under input (#68)

- **actions:** Fix checkout@v4 and upload-artifact@v4 across all workflows (#94)


### Documentation

- **instructions:** Add Python structure rules from Notion Engineering Standards (#53)


### Features

- **ruff-check,run-tests:** Add working-directory input for monorepo support (#48)

- **ruff:** Add working-directory support to ruff-check (#47) (#73)


### Miscellaneous

- **ci:** Normalize YAML formatting (indentation and quotes)

- Migrate sonar-scan to sonar-scan-python (#49)

- Bump actions/setup-python from 5.5.0 to 6.2.0 (#56)

- Bump raven-actions/actionlint from 2.0.1 to 2.1.2 (#57)

- Bump SonarSource/sonarqube-scan-action from 5 to 8 (#58)

- Bump peter-evans/create-pull-request from 7.0.6 to 8.1.1 (#55)

- **pre-commit:** Bump pre-commit-tools to v0.1.1-76, add regression-gate hook (#65)

- **pre-commit:** Bump pre-commit-tools to v0.1.1-76, add regression-gate hook (#63)

- **pre-commit:** Bump pre-commit-tools to v0.1.1-76, add regression-gate hook (#66)

- **ci:** Bump pre-commit-tools to v0.1.1-76 and migrate setup-python (#67)

- **ci:** Upgrade GitHub Actions to latest versions (#69)

- Standards compliance, dependabot groups, pre-commit updates (#70)

- **ci:** Upgrade GitHub Actions to latest versions (#71)

- **deps:** Bump pre-commit-tools to v0.1.1 (#76) (#74)

- **pre-commit:** Add missing chrysa hooks from standards audit (#82)

- **pre-commit:** Update pre-commit-tools to v0.1.1-92

- **ui-ux:** Reference ui-ux skill in CLAUDE.md (#92)


## [1.0.11] - 2026-05-17
### Miscellaneous

- **sonar-scan:** Add DEPRECATED notice — migrate to sonar-scan-python (#45)


## [1.0.9] - 2026-05-17
### Bug Fixes

- **ci:** Stabilize sonar workflow for bot pull requests (#31)

- **sonar-scan:** Bump sonarqube-scan-action v5 → v8.0.0 (#33)

- **sonar:** Bump sonarqube-scan-action to v8.0.0 (#34)

- **ci:** Bump sonarqube-scan-action to v8.0.0 (#35)

- **ci:** Exclude GitVersion.yml from yaml-sorter

- **quality:** Add docker-test target for CI-compatible action validation (#36)

- **quality:** Add docker-test target for CI-compatible action validation (#37)

- **ci:** Bump actions/checkout and setup-python to v6 (#38)

- **ci:** Add SKIP no-commit-to-branch in pre-commit step (#39)

- **ci:** Downgrade sonarqube-scan-action v8->v4.2.1 for SonarCloud (#40)

- **sonar-scan:** Make latest-python, github-token, organization, project-name optional with defaults

- **sonar-scan:** Downgrade sonarqube-scan-action v8/v5 → v4.2.1 + make sonar-scan-node inputs optional (#44)


### CI

- **standard:** Reference EXECUTION_STANDARD in copilot-instructions

- Add FUNDING.yml (sponsoring)

- Add FUNDING.yml (sponsoring)

- **pre-commit:** Bump chrysa/pre-commit-tools to v0.1.1-73 (#32)

- Standardize python matrix 3.14, add pre-commit/ruff/mypy jobs

- Centralize sonar scanning via chrysa/github-actions/sonar-scan@v1 (#41)


### Documentation

- Add AGENTS.md with GitNexus instructions


### Features

- **sonar-js-scan:** Add coverage-report-paths and tests inputs

- Add sonar-scan-node composite action for TypeScript/JavaScript projects

- **sonar-js-scan:** Add optional artifact download before sonar scan

- **workflows:** Add 16 reusable workflows + update labeler and dependencies


### Miscellaneous

- Standardize repo configuration (#9)

- Add dependencies-action, PR labeler, CLAUDE.md, and pre-commit-tools integration

- Bump actions/github-script from 7 to 8 (#21)

- Bump actions/labeler from 5 to 6 (#22)

- Update CLAUDE.md and add pull_request_template

- Propagate opencode.json MCP config

- Sync issue/PR templates from shared-standards

- **dx:** Add Claude Code optimization config (#24)

- Bump gittools/actions from 4.4.2 to 4.5.0 (#26)

- Bump softprops/action-gh-release from 2 to 3 (#27)

- Bump actions/github-script from 8 to 9 (#25)

- Add automation & industrialization guidelines (#28)

- Bump SonarSource/sonarqube-scan-action from 5 to 7 (#30)

- Bump actions/checkout from 4 to 6 (#29)

- Migrate specs to docs/specs/, add docs/adr/, fix CI standards

- **sonar:** Add sonar-project.properties for SonarCloud


## [1.0.7] - 2026-03-30
### Bug Fixes

- **pre-commit:** Update hook revisions to stable tags (#8)


### Miscellaneous

- Update CHANGELOG.md for v1.0.7 [skip ci]


## [1.0.6] - 2026-03-30
### Miscellaneous

- Add gitignore, copilot-instructions, instruction files (#7)

- Update CHANGELOG.md for v1.0.6 [skip ci]


## [1.0.5] - 2026-03-30
### Miscellaneous

- Add Copilot instructions file (#5)

- Update CHANGELOG.md for v1.0.5 [skip ci]


## [1.0.4] - 2026-03-29
### Miscellaneous

- Uniformize YAML syntax to match padam-av style (--- header, 4-space indent, timeout-minutes, shell: bash)


## [1.0.3] - 2026-03-29
### Documentation

- Add CI, release and license badges to README


### Miscellaneous

- Update CHANGELOG.md for v1.0.3 [skip ci]


## [1.0.2] - 2026-03-29
### Bug Fixes

- Fix changelog generation in release workflow

- Reorder changelog steps - generate before tagging, use body_path

- Replace preReleaseTag condition with tag existence check


### Features

- Add gitversion action and changelog generation with git-cliff


### Miscellaneous

- Add dependabot configuration for github-actions

- Update CHANGELOG.md for v1.0.2 [skip ci]


## [1.0.1] - 2026-03-29
### Bug Fixes

- **sonar:** Remove qualitygate.wait=true to avoid blocking CI on quality gate failure


## [1.0.0] - 2026-03-29
### Features

- Initial composite actions for chrysa/* repos


<--apply generated by [git-cliff](https://git-cliff.org) -->
