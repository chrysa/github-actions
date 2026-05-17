# Changelog

## [1.0.12] - 2026-05-17

### Bug Fixes

- Fix(security): prevent script injection via env vars (S7630) ([`22b543a`](22b543a6da4730e4340157c90d6e2f87998fdc1d))

## [1.0.11] - 2026-05-17

### Miscellaneous

- Chore(sonar-scan): add DEPRECATED notice — migrate to sonar-scan-python (#45)

## Summary

Refs #43

Adds a `DEPRECATED` notice to `sonar-scan/action.yml`.

## Context

Issue #43 tracks the full migration from `sonar-scan@v1` to
`sonar-scan-python@v1`.
The action version was already fixed to `v4.2.1` in PR #44.

This PR handles the first task from #43:
> ✅ Add a `DEPRECATED` note in `sonar-scan/action.yml` description
pointing to `sonar-scan-python`

## Remaining work (tracked in #43)

- [ ] Migrate all ecosystem repos from `sonar-scan@v1` to
`sonar-scan-python@v1`
- [ ] After full migration: archive or remove `sonar-scan`
- [ ] Align scanner version audit across all 4 sonar actions

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`9b7a0b3`](9b7a0b37dae9717378397f9fe27de6f8227b699a))

## [1.0.9] - 2026-05-17

### Bug Fixes

- Fix(ci): stabilize sonar workflow for bot pull requests (#31) ([`4155245`](4155245f8815ff41c315aa3be044bfb264a59f03))
- Fix(sonar-scan): bump sonarqube-scan-action v5 → v8.0.0 (#33)

The `sonar-scan` composite action was pinned to
`SonarSource/sonarqube-scan-action@v5`.
All standalone `sonar.yml` in the ecosystem already use `@v8.0.0`.
This brings the composite in line with the rest of the ecosystem.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`9957c5f`](9957c5f38e4d2765ab2f2c58ca9c48aeae7871bd))
- Fix(sonar): bump sonarqube-scan-action to v8.0.0 (#34)

Bump `SonarSource/sonarqube-scan-action` from old version to `v8.0.0`
(latest stable) to align with the rest of the chrysa ecosystem.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`1930f4a`](1930f4a013cb5912c63fa9fe09e39ec7c64f1336))
- Fix(ci): bump sonarqube-scan-action to v8.0.0 (#35)

## Summary
Update `SonarSource/sonarqube-scan-action` to v8.0.0 to fix SonarCloud
scanner compatibility.

This is a security and compatibility fix — older versions of the scanner
are no longer supported by SonarCloud.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`05757bb`](05757bb662a1cb6e8603a30a58f829e32d8361df))
- Fix(ci): exclude GitVersion.yml from yaml-sorter ([`ed69f09`](ed69f09638a5e2e5d620178b87053a06b6dec372))
- Fix(quality): add docker-test target for CI-compatible action validation (#36)

## Changes

- Add `docker-test` Makefile target: validates composite actions via
`action-validator` running in Docker (Python 3.14-slim)

This enables CI/CD pipelines to run action validation without requiring
`action-validator` installed on the host.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`a13cf3d`](a13cf3d1e935b66dabddfa97acfdfd537faa8c5f))
- Fix(quality): add docker-test target for CI-compatible action validation (#37)

Quality baseline: Dockerfile.test + docker-test Makefile target +
coverage/lint fixes.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`77aafe9`](77aafe9badb7aab25c927830a33723e9e316cba0))
- Fix(ci): bump actions/checkout and setup-python to v6 (#38)

- actions/checkout@v4 → @v6, actions/setup-python@v5 → @v6
- Addresses Node.js 20 deprecation (deadline June 2 2026)

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`4b29152`](4b2915227617cc040048545e2b947c9ab476b79e))
- Fix(ci): add SKIP no-commit-to-branch in pre-commit step (#39)

Add SKIP: no-commit-to-branch env to pre-commit step in ci.yml to
prevent CI failures when runner is on main

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`f5933fc`](f5933fc376438c5084c5b6c2b20d9d7afec19097))
- Fix(ci): downgrade sonarqube-scan-action v8->v4.2.1 for SonarCloud (#40)

- SonarSource/sonarqube-scan-action v8.0.0 → v4.2.1
- Scanner 8.x incompatible with SonarCloud (Error 404
/analysis/analyses)
- v4.2.1 uses sonar-scanner-cli 5.x, known stable with SonarCloud

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`a9ae1f4`](a9ae1f4a069b3bdbeb09606270d20028c7a4d84e))
- Fix(sonar-scan): make latest-python, github-token, organization, project-name optional with defaults

## Problem

The `sonar-scan` composite action had 4 required inputs that were not
being passed by the generated `sonar.yml` files across all repos:
- `latest-python` — required, no default
- `github-token` — required, no default
- `organization` — required, no default
- `project-name` — required, no default

This caused CI failures because the caller only passes `sonar-token`,
`project-key`, `sources`, and `tests`.

## Fix

Made all 4 inputs optional with sensible defaults:
- `latest-python`: default `'3.12'`
- `github-token`: default `''` (falls back to `github.token` in the
action via `|| github.token`)
- `organization`: default `'chrysa'`
- `project-name`: default `''` (falls back to `inputs.project-key` via
`|| inputs.project-key`)

Also updated `sources` default from `src` to `.` to better match repos
without a `src/` layout.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`58dbadc`](58dbadc527c0c75f18cf86632620707736ac7bae))
- Fix(sonar-scan): downgrade sonarqube-scan-action v8/v5 → v4.2.1 + make sonar-scan-node inputs optional (#44)

## Summary

### Problems fixed
- `sonar-scan/action.yml`: `sonarqube-scan-action@v8.0.0` → `@v4.2.1`
(billing-broken version)
- `sonar-scan-node/action.yml`: `sonarqube-scan-action@v5` → `@v4.2.1`
- `sonar-scan-node/action.yml`: `github-token`, `organization`,
`project-name` made optional (with `organization` defaulting to
`chrysa`)

### Impact
27 repos across the ecosystem now use
`chrysa/github-actions/sonar-scan@v1`. Once this fix is merged and the
`v1` floating tag is updated, all repos will use the working version
automatically without any change on their side.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`f3d0346`](f3d0346b98679547b764e06f2797dee3c1e0e2f6))

### Changes

- Add documentation and new GitHub Actions for Python packaging (#23)

## Summary
This PR adds comprehensive documentation for all shared GitHub Actions
and introduces two new actions for Python package publishing and
SonarCloud scanning with Python-specific configuration.

## Key Changes

### Documentation (README.md)
- Added detailed usage examples for all existing actions:
  - `python-setup`: Python environment setup with version configuration
  - `install-project`: Project installation with optional extras
  - `tool-setup`: Combined setup action
- `gitversion`: Semantic versioning from git history with output
examples
  - `ruff-check`: Linting and formatting with custom config support
  - `mypy-check`: Type checking with configuration options
  - `run-tests`: Test execution and coverage reporting
  - `sonar-scan`: Generic Python SonarCloud scanning
  - `sonar-scan-node`: Node.js/TypeScript SonarCloud scanning
- Updated action table with new actions and clarified descriptions

### New Actions

#### `sonar-scan-python` (sonar-scan-python/action.yml)
- Specialized SonarCloud scanning for Python projects with
Python-specific configuration
- Downloads analysis reports (coverage, ruff, mypy, junit) from
artifacts
- Configurable report paths with sensible defaults
- Supports multiple source and test directories
- Automatically excludes common Python artifacts (`__pycache__`,
`.egg-info`, etc.)

#### `publish-python-package` (publish-python-package/action.yml)
- Builds and publishes Python packages to PyPI
- Supports both `hatch` (default) and `setuptools` build backends
- Configurable Python version and repository URL
- Includes package validation with twine before publishing
- Supports TestPyPI for pre-release testing

## Implementation Details
- Both new actions use composite action format for portability
- `sonar-scan-python` includes error handling with `continue-on-error`
for optional reports
- `publish-python-package` uses environment variables for secure token
handling
- Documentation examples show both minimal and full configuration
options

https://claude.ai/code/session_01AQyW16RL2kQrc5dNLDzSeM

Co-authored-by: Claude <noreply@anthropic.com> ([`1d89654`](1d89654ebb144a8c3b3c3f4d1c95104be351fbee))

### Documentation

- Docs: add AGENTS.md with GitNexus instructions ([`b6bbddd`](b6bbddd9f64e41e495dabd20ac119b6fefee4566))

### Features

- Feat(sonar-js-scan): add coverage-report-paths and tests inputs

* feat: add sonar-js-scan composite action for JS/GAS projects

Adds a new sonar-js-scan/ composite action that runs SonarCloud
on JavaScript and Google Apps Script projects (no Python coverage
or ruff/mypy reports needed).

Inputs:
- sonar-token, github-token, project-key, organization, project-name (required)
- sources (optional, default: src)
- js-file-suffixes (optional, default: .js,.gs,.ts,.jsx,.tsx)

Difference from sonar-scan: no Python artifact downloads, no Python
sonar properties. Uses sonar.javascript.file.suffixes instead of
sonar.python.version so Sonar correctly identifies the language.

Use case: chrysa/notion-automation (Google Apps Script project)

* feat(sonar-js-scan): add coverage-report-paths and tests inputs

- Add optional coverage-report-paths input for LCOV coverage (e.g. coverage/lcov.info)
- Add optional tests input to exclude test directories from analysis
- Pass -Dsonar.javascript.lcov.reportPaths only when coverage-report-paths is non-empty
- Used by chrysa/satisfactory-automated_calculator CI

---------

Co-authored-by: anthony-greau <anthony.greau@padam.io> ([`096d83b`](096d83b65e94430d358bf71afe4e6dcb5703c9b2))
- Feat: add sonar-scan-node composite action for TypeScript/JavaScript projects

Co-authored-by: anthony-greau <anthony-greau@users.noreply.github.com> ([`33a8ac1`](33a8ac1c27ebecccab65dde34653df3b7b79b1b8))
- Feat(sonar-js-scan): add optional artifact download before sonar scan ([`4fa24a3`](4fa24a3b5000d65aa254fbe32ebbdeeb6c8f5024))
- Feat(workflows): add 16 reusable workflows + update labeler and dependencies

Add workflow_call: trigger to all utility workflows so any chrysa repo
can delegate to this central repo instead of maintaining copies.

New reusable workflows: action-check, approved-label, auto-assign,
auto-update-pre-commit, dependabot-auto-merge, detect-conflicts,
enforce-feature-branch, mutation-testing (inputs: paths/threshold),
pages, pre-commit, pull-request-size, quality-gate-check, release,
secret-scan, sync-labels, update-pr-body.

Updated: labeler, dependencies (added workflow_call trigger) ([`b9390c5`](b9390c5319e03253071d6e5e59bec8c2aba94dc6))

### Miscellaneous

- Chore: standardize repo configuration (#9)

* chore: standardize repo configuration

- chore: fix dependabot limits

* chore: add standard Makefile

* chore: update pre-commit hooks to latest versions ([`a6906ad`](a6906ad7fd86ae205084e4d01ab77bce781ddac1))
- Chore: add dependencies-action, PR labeler, CLAUDE.md, and pre-commit-tools integration

Standardization pass for chrysa/github-actions: add gregsdennis/dependencies-action, actions/labeler, CLAUDE.md, update .pre-commit-config.yaml to use chrysa/pre-commit-tools (yaml-sorter, json-sorter, env-file-check). Part of chrysa ecosystem standardization effort. ([`aa63430`](aa63430c923e6a051a857f62fccddb7d0ae08c82))
- Chore: bump actions/github-script from 7 to 8 (#21)

Bumps [actions/github-script](https://github.com/actions/github-script) from 7 to 8.
- [Release notes](https://github.com/actions/github-script/releases)
- [Commits](https://github.com/actions/github-script/compare/v7...v8)

---
updated-dependencies:
- dependency-name: actions/github-script
  dependency-version: '8'
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`ae3013c`](ae3013cbf5f276270396cebea36863d51cfb3291))
- Chore: bump actions/labeler from 5 to 6 (#22)

Bumps [actions/labeler](https://github.com/actions/labeler) from 5 to 6.
- [Release notes](https://github.com/actions/labeler/releases)
- [Commits](https://github.com/actions/labeler/compare/v5...v6)

---
updated-dependencies:
- dependency-name: actions/labeler
  dependency-version: '6'
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`3a195bc`](3a195bc7f95982604a38a93264111b491dea9837))
- Chore: update CLAUDE.md and add pull_request_template ([`0510ee9`](0510ee91b96a4801c1915a7f5a5c32fd7ec6dac8))
- Chore: propagate opencode.json MCP config ([`0461891`](0461891195a139e6cb7234c9f9a96eafde17dee4))
- Ci(standard): reference EXECUTION_STANDARD in copilot-instructions

Add Execution Standard Compliance section covering:
- §5 CI pipeline order (lint → typecheck → test-cov → sonar analysis)
- §4 testing requirements (80% coverage, coverage.xml, naming convention)
- §1 Makefile contract (lint / typecheck / test-cov as entry points) ([`33d48ce`](33d48ce55733f0edcaecf1ad41081dcd03e1e2d6))
- Ci: add FUNDING.yml (sponsoring) ([`7412db3`](7412db34c9ea45cd7e559685436262232b168cb5))
- Ci: add FUNDING.yml (sponsoring) ([`15882de`](15882de925eaf2e46260370ad2e72c4fff170b7f))
- Chore: sync issue/PR templates from shared-standards

- PR template: type field, squash merge, SonarCloud, 1 PR = 1 issue
- bug_report.yml: severity field, next step
- feature_request.yml: priority, out of scope, next step
- chore.yml: CI/tech debt context, next step
- security.yml: new template (CVE, GHSA, impact)
- Remove legacy .md format templates ([`6b26f60`](6b26f60257ce71367907b5f16dc41b6ef3b72c39))
- Chore(dx): add Claude Code optimization config (#24)

## Summary

Uniformize Claude Code and GitHub Copilot configuration across the
ecosystem.

### Changes

- : add , , and lifecycle hooks
- : copy shared hooks from (secret-scanner, circuit-breaker,
verifiable-thresholds, frustration-detection)
- : add  section for better context compaction
- : create if missing

### Why

Based on Claude Code best practices:
- Auto-compact at 85% (vs default 95%) → 2.3s faster responses on long
sessions
- PreCompact hook → -30% info loss during compaction
- Secret scanner + circuit breaker → prevent secrets leaks and repeated
API failures

### References

- [Claude Code Best
Practices](https://code.claude.com/docs/fr/best-practices)
- Source:  (private) ([`e55b9d9`](e55b9d929b2ef0118505ca187faee19116e2ba58))
- Chore: bump gittools/actions from 4.4.2 to 4.5.0 (#26)

Bumps [gittools/actions](https://github.com/gittools/actions) from 4.4.2
to 4.5.0.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/gittools/actions/releases">gittools/actions's
releases</a>.</em></p>
<blockquote>
<h2>v4.5.0</h2>
<p>As part of this release we had <a
href="https://github.com/GitTools/actions/compare/v4.4.2...v4.5.0">75
commits</a> which resulted in <a
href="https://github.com/GitTools/actions/milestone/36?closed=1">3
issues</a> being closed.</p>
<p><strong>Features</strong></p>
<ul>
<li>[<strong><a
href="https://redirect.github.com/gittools/actions/issues/1936">#1936</a></strong>](<a
href="https://redirect.github.com/GitTools/actions/issues/1936">GitTools/actions#1936</a>)
[ISSUE]: Add /updatewixversionfile to Azure DevOps task</li>
</ul>
<p><strong>Improvements</strong></p>
<ul>
<li>[<strong><a
href="https://redirect.github.com/gittools/actions/issues/1932">#1932</a></strong>](<a
href="https://redirect.github.com/GitTools/actions/issues/1932">GitTools/actions#1932</a>)
[ISSUE]: Better error handling in Azure</li>
<li>[<strong><a
href="https://redirect.github.com/gittools/actions/issues/2010">#2010</a></strong>](<a
href="https://redirect.github.com/GitTools/actions/issues/2010">GitTools/actions#2010</a>)
Improve CI/CD consistency and refresh published workflow examples</li>
</ul>
<h3>SHA256 Hashes of the release artifacts</h3>
<ul>

<li><code>ae208cf21cd3506d486516e2b977bc4e5b325fa649bef036e04131eafc1471e1
- gittools.gittools-4.5.0.260407213.vsix</code></li>
</ul>
</blockquote>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/GitTools/actions/commit/bc6623af8fc07d5a8903052dd46da33403eec8e8"><code>bc6623a</code></a>
ci(github): add delay before triggering update examples</li>
<li><a
href="https://github.com/GitTools/actions/commit/ace732b7a271b31a0af58775d4787152969656ba"><code>ace732b</code></a>
feat(github): add workflow automation prompts and git-commit skill</li>
<li><a
href="https://github.com/GitTools/actions/commit/462062fad3a4d34dfef396ad584757bec0d5e230"><code>462062f</code></a>
Merge pull request <a
href="https://redirect.github.com/gittools/actions/issues/2031">#2031</a>
from GitTools/dependabot/github_actions/gittools/cicd-2</li>
<li><a
href="https://github.com/GitTools/actions/commit/cd5bba8678d93ae4286557b273081dd4d3f338fc"><code>cd5bba8</code></a>
(github-actions): Bump gittools/cicd from 1 to 2</li>
<li><a
href="https://github.com/GitTools/actions/commit/300b335f5d8cc6f313cd225bb3d9894861a36186"><code>300b335</code></a>
Merge pull request <a
href="https://redirect.github.com/gittools/actions/issues/2030">#2030</a>
from GitTools/dependabot/npm_and_yarn/vite-3932ebd7b6</li>
<li><a
href="https://github.com/GitTools/actions/commit/e99f4951299100aa2f35f131f6898ab541f94102"><code>e99f495</code></a>
(npm): Bump vite from 8.0.6 to 8.0.7 in the vite group</li>
<li><a
href="https://github.com/GitTools/actions/commit/081cd6f0503794b1bdb51bc904dcfa4f6ee6c53c"><code>081cd6f</code></a>
dist update</li>
<li><a
href="https://github.com/GitTools/actions/commit/cc3b3f3283709dd385f922da014e79a60852031f"><code>cc3b3f3</code></a>
Merge pull request <a
href="https://redirect.github.com/gittools/actions/issues/1994">#1994</a>
from GitTools/dependabot/npm_and_yarn/vite-555ff24f4a</li>
<li><a
href="https://github.com/GitTools/actions/commit/ce57e8efe3648e6234d7d00a4c2b60378ff7e874"><code>ce57e8e</code></a>
build(vite): migrate to oxc and native tsconfig path resolution</li>
<li><a
href="https://github.com/GitTools/actions/commit/e600a39aa13032a8bbc7f85afaeaee544f446890"><code>e600a39</code></a>
(npm): Bump the vite group across 1 directory with 3 updates</li>
<li>Additional commits viewable in <a
href="https://github.com/gittools/actions/compare/v4.4.2...v4.5.0">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=gittools/actions&package-manager=github_actions&previous-version=4.4.2&new-version=4.5.0)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

Dependabot will resolve any conflicts with this PR as long as you don't
alter it yourself. You can also trigger a rebase manually by commenting
`@dependabot rebase`.

[//]: # (dependabot-automerge-start)
[//]: # (dependabot-automerge-end)

---

<details>
<summary>Dependabot commands and options</summary>
<br />

You can trigger Dependabot actions by commenting on this PR:
- `@dependabot rebase` will rebase this PR
- `@dependabot recreate` will recreate this PR, overwriting any edits
that have been made to it
- `@dependabot show <dependency name> ignore conditions` will show all
of the ignore conditions of the specified dependency
- `@dependabot ignore this major version` will close this PR and stop
Dependabot creating any more for this major version (unless you reopen
the PR or upgrade to it yourself)
- `@dependabot ignore this minor version` will close this PR and stop
Dependabot creating any more for this minor version (unless you reopen
the PR or upgrade to it yourself)
- `@dependabot ignore this dependency` will close this PR and stop
Dependabot creating any more for this dependency (unless you reopen the
PR or upgrade to it yourself)


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`f223103`](f223103bc3d5ceb24049aa929b98443fb325846a))
- Chore: bump softprops/action-gh-release from 2 to 3 (#27)

Bumps
[softprops/action-gh-release](https://github.com/softprops/action-gh-release)
from 2 to 3.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/softprops/action-gh-release/releases">softprops/action-gh-release's
releases</a>.</em></p>
<blockquote>
<h2>v3.0.0</h2>
<p><code>3.0.0</code> is a major release that moves the action runtime
from Node 20 to Node 24.
Use <code>v3</code> on GitHub-hosted runners and self-hosted fleets that
already support the
Node 24 Actions runtime. If you still need the last Node 20-compatible
line, stay on
<code>v2.6.2</code>.</p>
<h2>What's Changed</h2>
<h3>Other Changes 🔄</h3>
<ul>
<li>Move the action runtime and bundle target to Node 24</li>
<li>Update <code>@types/node</code> to the Node 24 line and allow future
Dependabot updates</li>
<li>Keep the floating major tag on <code>v3</code>; <code>v2</code>
remains pinned to the latest <code>2.x</code> release</li>
</ul>
<h2>v2.6.2</h2>
<!-- raw HTML omitted -->
<h2>What's Changed</h2>
<h3>Other Changes 🔄</h3>
<ul>
<li>chore(deps): bump picomatch from 4.0.3 to 4.0.4 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/softprops/action-gh-release/pull/775">softprops/action-gh-release#775</a></li>
<li>chore(deps): bump brace-expansion from 5.0.4 to 5.0.5 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/softprops/action-gh-release/pull/777">softprops/action-gh-release#777</a></li>
<li>chore(deps): bump vite from 8.0.0 to 8.0.5 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/softprops/action-gh-release/pull/781">softprops/action-gh-release#781</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/softprops/action-gh-release/compare/v2...v2.6.2">https://github.com/softprops/action-gh-release/compare/v2...v2.6.2</a></p>
<h2>v2.6.1</h2>
<p><code>2.6.1</code> is a patch release focused on restoring linked
discussion thread creation when
<code>discussion_category_name</code> is set. It fixes
<code>[#764](https://github.com/softprops/action-gh-release/issues/764)</code>,
where the draft-first publish flow
stopped carrying the discussion category through the final publish
step.</p>
<p>If you still hit an issue after upgrading, please open a report with
the bug template and include a minimal repro or sanitized workflow
snippet where possible.</p>
<h2>What's Changed</h2>
<h3>Bug fixes 🐛</h3>
<ul>
<li>fix: preserve discussion category on publish by <a
href="https://github.com/chenrui333"><code>@​chenrui333</code></a> in <a
href="https://redirect.github.com/softprops/action-gh-release/pull/765">softprops/action-gh-release#765</a></li>
</ul>
<h2>v2.6.0</h2>
<p><code>2.6.0</code> is a minor release centered on
<code>previous_tag</code> support for
<code>generate_release_notes</code>,
which lets workflows pin GitHub's comparison base explicitly instead of
relying on the default range.
It also includes the recent concurrent asset upload recovery fix, a
<code>working_directory</code> docs sync,
a checked-bundle freshness guard for maintainers, and clearer
immutable-prerelease guidance where
GitHub platform behavior imposes constraints on how prerelease asset
uploads can be published.</p>
<p>If you still hit an issue after upgrading, please open a report with
the bug template and include a minimal repro or sanitized workflow
snippet where possible.</p>
<h2>What's Changed</h2>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a
href="https://github.com/softprops/action-gh-release/blob/master/CHANGELOG.md">softprops/action-gh-release's
changelog</a>.</em></p>
<blockquote>
<h2>0.1.13</h2>
<ul>
<li>fix issue with multiple runs concatenating release bodies <a
href="https://redirect.github.com/softprops/action-gh-release/pull/145">#145</a></li>
</ul>
</blockquote>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/softprops/action-gh-release/commit/b4309332981a82ec1c5618f44dd2e27cc8bfbfda"><code>b430933</code></a>
release: cut v3.0.0 for Node 24 upgrade (<a
href="https://redirect.github.com/softprops/action-gh-release/issues/670">#670</a>)</li>
<li><a
href="https://github.com/softprops/action-gh-release/commit/c2e35e05a74208bafbfcbdae5ebc9da7236e980f"><code>c2e35e0</code></a>
chore(deps): bump the npm group across 1 directory with 7 updates (<a
href="https://redirect.github.com/softprops/action-gh-release/issues/783">#783</a>)</li>
<li>See full diff in <a
href="https://github.com/softprops/action-gh-release/compare/v2...v3">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=softprops/action-gh-release&package-manager=github_actions&previous-version=2&new-version=3)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

Dependabot will resolve any conflicts with this PR as long as you don't
alter it yourself. You can also trigger a rebase manually by commenting
`@dependabot rebase`.

[//]: # (dependabot-automerge-start)
[//]: # (dependabot-automerge-end)

---

<details>
<summary>Dependabot commands and options</summary>
<br />

You can trigger Dependabot actions by commenting on this PR:
- `@dependabot rebase` will rebase this PR
- `@dependabot recreate` will recreate this PR, overwriting any edits
that have been made to it
- `@dependabot show <dependency name> ignore conditions` will show all
of the ignore conditions of the specified dependency
- `@dependabot ignore this major version` will close this PR and stop
Dependabot creating any more for this major version (unless you reopen
the PR or upgrade to it yourself)
- `@dependabot ignore this minor version` will close this PR and stop
Dependabot creating any more for this minor version (unless you reopen
the PR or upgrade to it yourself)
- `@dependabot ignore this dependency` will close this PR and stop
Dependabot creating any more for this dependency (unless you reopen the
PR or upgrade to it yourself)


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`f5f47fe`](f5f47fe99808506b7cf131de32f8768aed17c2fe))
- Chore: bump actions/github-script from 8 to 9 (#25)

Bumps [actions/github-script](https://github.com/actions/github-script)
from 8 to 9.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/actions/github-script/releases">actions/github-script's
releases</a>.</em></p>
<blockquote>
<h2>v9.0.0</h2>
<p><strong>New features:</strong></p>
<ul>
<li><strong><code>getOctokit</code> factory function</strong> —
Available directly in the script context. Create additional
authenticated Octokit clients with different tokens for multi-token
workflows, GitHub App tokens, and cross-org access. See <a
href="https://github.com/actions/github-script#creating-additional-clients-with-getoctokit">Creating
additional clients with <code>getOctokit</code></a> for details and
examples.</li>
<li><strong>Orchestration ID in user-agent</strong> — The
<code>ACTIONS_ORCHESTRATION_ID</code> environment variable is
automatically appended to the user-agent string for request
tracing.</li>
</ul>
<p><strong>Breaking changes:</strong></p>
<ul>
<li><strong><code>require('@actions/github')</code> no longer works in
scripts.</strong> The upgrade to <code>@actions/github</code> v9
(ESM-only) means <code>require('@actions/github')</code> will fail at
runtime. If you previously used patterns like <code>const { getOctokit }
= require('@actions/github')</code> to create secondary clients, use the
new injected <code>getOctokit</code> function instead — it's available
directly in the script context with no imports needed.</li>
<li><code>getOctokit</code> is now an injected function parameter.
Scripts that declare <code>const getOctokit = ...</code> or <code>let
getOctokit = ...</code> will get a <code>SyntaxError</code> because
JavaScript does not allow <code>const</code>/<code>let</code>
redeclaration of function parameters. Use the injected
<code>getOctokit</code> directly, or use <code>var getOctokit =
...</code> if you need to redeclare it.</li>
<li>If your script accesses other <code>@actions/github</code> internals
beyond the standard <code>github</code>/<code>octokit</code> client, you
may need to update those references for v9 compatibility.</li>
</ul>
<h2>What's Changed</h2>
<ul>
<li>Add ACTIONS_ORCHESTRATION_ID to user-agent string by <a
href="https://github.com/Copilot"><code>@​Copilot</code></a> in <a
href="https://redirect.github.com/actions/github-script/pull/695">actions/github-script#695</a></li>
<li>ci: use deployment: false for integration test environments by <a
href="https://github.com/salmanmkc"><code>@​salmanmkc</code></a> in <a
href="https://redirect.github.com/actions/github-script/pull/712">actions/github-script#712</a></li>
<li>feat!: add getOctokit to script context, upgrade
<code>@​actions/github</code> v9, <code>@​octokit/core</code> v7, and
related packages by <a
href="https://github.com/salmanmkc"><code>@​salmanmkc</code></a> in <a
href="https://redirect.github.com/actions/github-script/pull/700">actions/github-script#700</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a href="https://github.com/Copilot"><code>@​Copilot</code></a> made
their first contribution in <a
href="https://redirect.github.com/actions/github-script/pull/695">actions/github-script#695</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/actions/github-script/compare/v8.0.0...v9.0.0">https://github.com/actions/github-script/compare/v8.0.0...v9.0.0</a></p>
</blockquote>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/actions/github-script/commit/3a2844b7e9c422d3c10d287c895573f7108da1b3"><code>3a2844b</code></a>
Merge pull request <a
href="https://redirect.github.com/actions/github-script/issues/700">#700</a>
from actions/salmanmkc/expose-getoctokit + prepare re...</li>
<li><a
href="https://github.com/actions/github-script/commit/ca10bbdd1a7739de09e99a200c7a59f5d73a4079"><code>ca10bbd</code></a>
fix: use <code>@​octokit/core/</code>types import for v7
compatibility</li>
<li><a
href="https://github.com/actions/github-script/commit/86e48e20ac85c970ed1f96e718fd068173948b7b"><code>86e48e2</code></a>
merge: incorporate main branch changes</li>
<li><a
href="https://github.com/actions/github-script/commit/c1084728b5b935ec4ddc1e4cee877b01797b3ff9"><code>c108472</code></a>
chore: rebuild dist for v9 upgrade and getOctokit factory</li>
<li><a
href="https://github.com/actions/github-script/commit/afff112e4f8b57c718168af75b89ce00bc8d091d"><code>afff112</code></a>
Merge pull request <a
href="https://redirect.github.com/actions/github-script/issues/712">#712</a>
from actions/salmanmkc/deployment-false + fix user-ag...</li>
<li><a
href="https://github.com/actions/github-script/commit/ff8117e5b78c415f814f39ad6998f424fee7b817"><code>ff8117e</code></a>
ci: fix user-agent test to handle orchestration ID</li>
<li><a
href="https://github.com/actions/github-script/commit/81c6b7876079abe10ff715951c9fc7b3e1ab389d"><code>81c6b78</code></a>
ci: use deployment: false to suppress deployment noise from integration
tests</li>
<li><a
href="https://github.com/actions/github-script/commit/3953caf8858d318f37b6cc53a9f5708859b5a7b7"><code>3953caf</code></a>
docs: update README examples from <a
href="https://github.com/v8"><code>@​v8</code></a> to <a
href="https://github.com/v9"><code>@​v9</code></a>, add getOctokit docs
and v9 brea...</li>
<li><a
href="https://github.com/actions/github-script/commit/c17d55b90dcdb3d554d0027a6c180a7adc2daf78"><code>c17d55b</code></a>
ci: add getOctokit integration test job</li>
<li><a
href="https://github.com/actions/github-script/commit/a047196d9a02fe92098771cafbb98c2f1814e408"><code>a047196</code></a>
test: add getOctokit integration tests via callAsyncFunction</li>
<li>Additional commits viewable in <a
href="https://github.com/actions/github-script/compare/v8...v9">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=actions/github-script&package-manager=github_actions&previous-version=8&new-version=9)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

Dependabot will resolve any conflicts with this PR as long as you don't
alter it yourself. You can also trigger a rebase manually by commenting
`@dependabot rebase`.

[//]: # (dependabot-automerge-start)
[//]: # (dependabot-automerge-end)

---

<details>
<summary>Dependabot commands and options</summary>
<br />

You can trigger Dependabot actions by commenting on this PR:
- `@dependabot rebase` will rebase this PR
- `@dependabot recreate` will recreate this PR, overwriting any edits
that have been made to it
- `@dependabot show <dependency name> ignore conditions` will show all
of the ignore conditions of the specified dependency
- `@dependabot ignore this major version` will close this PR and stop
Dependabot creating any more for this major version (unless you reopen
the PR or upgrade to it yourself)
- `@dependabot ignore this minor version` will close this PR and stop
Dependabot creating any more for this minor version (unless you reopen
the PR or upgrade to it yourself)
- `@dependabot ignore this dependency` will close this PR and stop
Dependabot creating any more for this dependency (unless you reopen the
PR or upgrade to it yourself)


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`7d18eb5`](7d18eb5d7cb0dca4979c918b2a21d0b1dca11a1f))
- Chore: add automation & industrialization guidelines (#28) ([`642e939`](642e9399e8bb80691f91f8fad444fc3b4b027963))
- Chore: bump SonarSource/sonarqube-scan-action from 5 to 7 (#30)

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`1c54b59`](1c54b596612f8d95199f1387077c4c3173f86c13))
- Chore: bump actions/checkout from 4 to 6 (#29)

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Co-authored-by: chrysa <chrysa@users.noreply.github.com> ([`ed98408`](ed9840866a9d706e747c3d36c42de912a2781b3e))
- Ci(pre-commit): bump chrysa/pre-commit-tools to v0.1.1-73 (#32)

Bump chrysa/pre-commit-tools rev to v0.1.1-73 in
.pre-commit-config.yaml.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`61e8cb8`](61e8cb82e02f3c4e5c42efb49b246663f0227141))
- Chore: migrate specs to docs/specs/, add docs/adr/, fix CI standards ([`e690a6a`](e690a6ad40293917cd3312c871bded0110bbef69))
- Ci: standardize python matrix 3.14, add pre-commit/ruff/mypy jobs ([`bef772d`](bef772d2b84b84f0f3a28946d31e22cc8fe835ac))
- Chore(sonar): add sonar-project.properties for SonarCloud ([`b781288`](b781288fa937e39f0bebed296868f726ed74e51b))
- Ci: centralize sonar scanning via chrysa/github-actions/sonar-scan@v1 (#41)

Migrate `sonar.yml` to use the centralized
`chrysa/github-actions/sonar-scan@v1` composite action instead of inline
`SonarSource/sonarqube-scan-action`.

## Changes
- Replace inline `SonarSource/sonarqube-scan-action` call with
`chrysa/github-actions/sonar-scan@v1`
- Add `concurrency` block to cancel duplicate runs
- Standardize trigger branches and `if: github.actor !=
'dependabot[bot]'` condition
- Bump `actions/checkout` to `@v6`

## Related
Part of ecosystem-wide CI centralization.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`aa81495`](aa81495f0f1523c8cfb26dcd8a7fcdf6f7c1b616))

## [1.0.7] - 2026-03-30

### Bug Fixes

- Fix(pre-commit): update hook revisions to stable tags (#8) ([`cd2171a`](cd2171a47b16107887a2aaad9eeed5c667716ecc))

### Miscellaneous

- Chore: update CHANGELOG.md for v1.0.7 [skip ci] ([`fec4701`](fec470154f8f784656e9d8fbe19dd78e41b77d8d))

## [1.0.6] - 2026-03-30

### Miscellaneous

- Chore: add gitignore, copilot-instructions, instruction files (#7) ([`03b4d11`](03b4d110b7787d8fe6ea60257719e3dff71c0695))
- Chore: update CHANGELOG.md for v1.0.6 [skip ci] ([`2cfca96`](2cfca96b87eb1cc9633769d4a08b4cdbcc7092bd))

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


