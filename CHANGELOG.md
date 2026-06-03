# Changelog

## [1.1.3] - 2026-06-03

### Bug Fixes

- Fix(secret-scan): grant pull-requests:read for gitleaks PR commit listing (#98)

## Problem
`gitleaks-action@v2` fails on **every PR across all consuming repos**
with:

```
GET /repos/chrysa/<repo>/pulls/<n>/commits → 403 "Resource not accessible by integration"
```

The action lists PR commits to scan only the diff. The reusable
`secret-scan.yml` declared `permissions: contents: read` only, so the
`GITHUB_TOKEN` lacked `pull-requests: read`.

## Fix
Add `pull-requests: read` to the workflow permissions block.

## Impact
Re-greens the **Detect secrets (Gitleaks)** check on ~160 open PRs once
consuming repos pick up the workflow.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com>
Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com> ([`7eb346e`](7eb346e196692578c8edc516da471daac0bed5ee))

## [1.1.2] - 2026-06-03

### Bug Fixes

- Fix(sonar-scan-python): revert to sonarqube-scan-action@v5 (fixes api.sonarcloud.io 404) (#97)

## Problem
The `v1.1.0` rewrite of `sonar-scan-python` replaced
`SonarSource/sonarqube-scan-action@v5` with a manual `sonar-scanner-cli
7.1.0.4889` download. That scanner targets the new `api.sonarcloud.io`
endpoint and fails with:

```
INFO  Detected project binding: NONEXISTENT
ERROR Error 404 on https://api.sonarcloud.io/analysis/analyses
EXECUTION FAILURE
```

This breaks SonarCloud analysis on every chrysa repo (none have an ALM
binding configured), blocking the entire `standards-realign` rollout
(~32 PRs).

## Fix
Restore the proven `SonarSource/sonarqube-scan-action@v5` step (classic
scanner / classic SonarCloud API, which tolerates NONEXISTENT binding).
This is a verbatim restore of the working `v1.0.12` step.

## Rollout
After merge: tag `v1.1.2`, move `v1` to it, bump consuming PRs `@v1.1.0
-> @v1.1.2`.

🤖 Generated with [Claude Code](https://claude.com/claude-code) ([`dd0bd6e`](dd0bd6ee4279f8593703f991977ce2713d2ef454))

### Miscellaneous

- Chore(standards): realign gitignore + pre-commit + sonar (#96)

Automated standards realignment: gitignore sonar-repin@v1

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`4e52dd4`](4e52dd4bceb875e3be4740ea124f796bcad113d8))

## [1.1.0] - 2026-06-03

### Bug Fixes

- Fix(security): prevent script injection via env vars (S7630) ([`22b543a`](22b543a6da4730e4340157c90d6e2f87998fdc1d))
- Fix(security): scope permissions to jobs and add --only-binary (S8233/S8541) ([`a88f699`](a88f699b8e7134dbb0dbff702aa338a55cf65dd9))
- Fix(ci): fix S7630 script injection and S8541/S8544 pip flags ([`8cdfe61`](8cdfe61d958dce413aa53a76ecd914bb97a22823))
- Fix(yaml): quote run values containing :all: to prevent YAML parsing errors (#50)

## Problem

In GitHub Actions composite actions YAML, a `run:` value containing
`--only-binary :all:` triggers a YAML parsing error: `:all: ` (colon
followed by space) is interpreted as a mapping key separator in plain
scalars.

Broke all jobs using `python-setup` and `publish-python-package` with:
```
Set up job → failure
```

## Fix

Wrap affected `run:` values in single quotes:

- `python-setup/action.yml`
- `publish-python-package/action.yml`
- `.github/workflows/pages.yml`
- `.github/workflows/auto-update-pre-commit.yml`

## Validation

All 4 files validated YAML-valid. Unblocks chrysa/guideline-checker#69.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`66a549d`](66a549d810e5ddd871d1c5dd32b8ce4a8ff725c2))
- Fix(yaml): quote pip :all: run values + migrate to actionlint (#51)

## Changes

- **Fix YAML parsing errors**: quote `run:` values containing `:all:` in
`python-setup/action.yml`, `publish-python-package/action.yml`, and
workflows (fixes downstream CI failures e.g. guideline-checker#69)
- **Migrate to actionlint**: replace deprecated `action-validator` (repo
deleted) with `actionlint` in `Makefile` and `docker-test` target
- **Fix SC2086**: quote `${exit_code:-0}` in `quality-gate-check.yml`

Closes: downstream CI failures caused by YAML parse error in
python-setup action.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`2038fb1`](2038fb14d3d572f76db95cd0eb0ea41b276b3fc0))
- Fix: yaml colon in run values (#52)

Auto-generated PR for branch `fix/yaml-colon-in-run-values`.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`0229e03`](0229e035dbfedd9e6d5c88d3ebc8aca82f1f1241))
- Fix(yaml): quote run values with colons to prevent YAML parsing errors (#54)

## Summary

Fix YAML parsing errors caused by unquoted and similar colon-containing
values in `run:` blocks of composite action files.

## Changes

- Quote pip `:all:` run values (e.g. `pip install '.[dev]'`)
- Migrate to actionlint for validation
- Add standards compliance files (CODEOWNERS, sonar, dependabot, cliff,
pre-commit)
- Add Python structure rules to copilot instructions
- Trim copilot-instructions to avoid duplication with workspace-level
instructions
- Fix CHANGELOG email/style references

## Related Issues

Fixes #50 #51

## Testing

Validated via actionlint on all composite action YAML files.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`d30323e`](d30323e923b7d2238aae214ef248dde481e6fed0))
- Fix(actions): fix YAML colon in run values, standards compliance, dependabot groups (#59)

## Summary

### Fixes
- Fix YAML colon-in-run-values issues across composite actions
(`gitversion`, `install-project`, `mypy-check`, `ruff-check`,
`run-tests`, `sonar-js-scan`, `sonar-scan-python`, `tool-setup`)
- Remove pip cache from composite-actions repo, fix sonar tests path
- Fix pre-commit issues across repo

### Chore
- Trim `copilot-instructions`, fix CHANGELOG email/style refs
- Add Python structure rules from Notion Engineering Standards
- Add Dependabot groups and throttling to limit open PRs
- Exclude `.codegraph/` from vcs, update quality-gate-check workflow
- Add standards compliance files (CODEOWNERS, sonar, dependabot, cliff,
pre-commit)

## CI
All checks pass on this branch.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`ab83bd3`](ab83bd3d5ec876682e4472d273221081aea68b09))
- Fix(sonar-scan-python): upgrade sonarqube-scan-action from v5 to v8 (#62)

## Summary

Upgrade `SonarSource/sonarqube-scan-action` from `@v5` to `@v8` in the
`sonar-scan-python` composite action.

### Motivation

`@v5` is deprecated and contains a security vulnerability (as flagged by
GitHub Actions runner warnings). `@v8` is the latest stable version,
consistent with the version already used in this repo's own `sonar.yml`
workflow.

### Impact

Fixes CI failure in downstream repos using
`chrysa/github-actions/sonar-scan-python@main` — previously receiving
`Error 404 on api.sonarcloud.io/analysis/analyses` due to the outdated
scanner engine in `@v5`.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`3556841`](3556841a5fc314b19509fecc26f4660b08b7692d))
- Fix(sonar-scan-python): pin scanner to 5.0.1.3006 to avoid /analysis/analyses 404 (#64)

## Summary

Pin the SonarScanner CLI version to **5.0.1.3006** in the
`sonar-scan-python` composite action.

### Root Cause

SonarScanner 8.x (default of `sonarqube-scan-action@v8`) uses a new
`/analysis/analyses` API endpoint to register analyses before scanning.
This endpoint is **not available on SonarCloud Community plans**,
causing:

```
ERROR Error during SonarScanner Engine execution
java.lang.IllegalStateException: Unable to create analysis
HttpException: Error 404 on https://api.sonarcloud.io/analysis/analyses
```

### Fix

Override `scannerVersion: 5.0.1.3006` so the action uses the last stable
5.x scanner which doesn't call the new endpoint — while keeping the
**action itself at v8** to comply with security requirements (v5 was
deprecated/insecure per GitHub Actions annotations).

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`a06f110`](a06f1105f4c46e6f08624f7fa5505dcbb3a0838e))
- Fix(yaml): handle YAML colon in run values (#72)

Fix YAML parsing issue where colon in 'run:' block values caused linting
errors.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`ed267d2`](ed267d26ed63cd04dd23a66bca1df808a924c931))
- Fix/yaml-colon-in-run-values (#77)

automated: fix/yaml-colon-in-run-values

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`cca92da`](cca92da77af4159f5266e665d9cc2f4b4756d225))
- Fix(pre-commit): apply yaml-sorter formatting to action files (#83)

Sort YAML keys alphabetically in python-setup/action.yml and
run-tests/action.yml. Remove trailing blank lines from dependabot.yml
and .pre-commit-config.yaml.

Fixes pre-commit CI failure caused by yaml-sorter detecting unsorted
keys.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`6a742f8`](6a742f8be666d1deba752d9174c16e1784f3137b))
- Fix(ci): implement dependabot-auto-merge as reusable workflow_call (#93)

The `dependabot-auto-merge.yml` was calling itself recursively (no
`workflow_call:` trigger), causing all 40+ repos that use it to fail
with 'workflow file issue'.\n\nThis PR adds the actual
implementation:\n- Responds to `workflow_call:` trigger\n- Fetches
Dependabot metadata to check update type\n- Auto-merges and approves
patch/minor updates via `gh pr merge --auto`\n\nFixes CI failures in:
sport-intelligence-hub and all other repos that call this workflow.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`62d88ce`](62d88ce732158b66fe3fd2ca2e78cc0eeec81d6f))
- Fix(sonar): repair sonar-scan-python (dead scanner pin → Maven Central + retry) (#95)

Root cause: scannerVersion 5.0.1.3006 removed from sonarsource CDN
(403). Fix: install sonar-scanner-cli from Maven Central with retry, run
scanner directly. Validated green on chrysa_sport-intelligence-hub.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`8b039e4`](8b039e4849805ee7071c99fadbdf2450bbc9753f))

### Changes

- [SKIP CI] [pre-commit] bump https://github.com/igorshubovych/markdownlint-cli from f7ed74202ac8ec26bab4a68359556c5243df142f to dd34288d0608e7b8825ee7e4e8c406e0a9780cf7 (#60)

Bumps
[https://github.com/igorshubovych/markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli)
from f7ed74202ac8ec26bab4a68359556c5243df142f to
dd34288d0608e7b8825ee7e4e8c406e0a9780cf7.
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/dd34288d0608e7b8825ee7e4e8c406e0a9780cf7"><code>dd34288</code></a>
Bump ava from 8.0.0 to 8.0.1</li>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/1e363dc0ddba97b89ae57f33c85d1b2f6715c346"><code>1e363dc</code></a>
Bump brace-expansion from 5.0.5 to 5.0.6</li>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/2f092d251b357b114d133ce472675970640237d7"><code>2f092d2</code></a>
Bump ava from 7.0.0 to 8.0.0</li>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/e3bd37fc2c178a97efb9ba0642ad5568fea3286d"><code>e3bd37f</code></a>
Remove support for &quot;EOL&quot; Node 20, add &quot;Current&quot; Node
26.</li>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/cfc833bfc00c7cc40f702bd9e02df34d850d0291"><code>cfc833b</code></a>
Bump tinyglobby from 0.2.15 to 0.2.16</li>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/fa11558348ca25f74763660527ed502a4e592420"><code>fa11558</code></a>
Bump nano-spawn from 2.0.0 to 2.1.0</li>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/804e22828e98e561085e47f39a15f42c8397b883"><code>804e228</code></a>
Bump lodash from 4.17.23 to 4.18.1</li>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/7d84be39168a8b2407e864ddd7ccab147b851f63"><code>7d84be3</code></a>
Update code for new, breaking lint rules in xo@2.</li>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/f3fa8bdfd22ea4ca150497d66577b7ecac70c5a7"><code>f3fa8bd</code></a>
Bump xo from 1.2.3 to 2.0.2</li>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/70466ee0aa1d9bca1fd4ce54bfbba370431ecced"><code>70466ee</code></a>
Bump minimatch from 10.2.4 to 10.2.5</li>
<li>See full diff in <a
href="https://github.com/igorshubovych/markdownlint-cli/compare/f7ed74202ac8ec26bab4a68359556c5243df142f...dd34288d0608e7b8825ee7e4e8c406e0a9780cf7">compare
view</a></li>
</ul>
</details>
<br />


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
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`a51482c`](a51482c2ce053f46edb853203d03354d0d3fcd7c))
- [SKIP CI] [pre-commit] bump https://github.com/pre-commit/pre-commit-hooks from f1dff44d3a9ae852957f34def96390f28719c232 to fa6b006f0e53d6c0a4a30d6f7b1200a899444634 (#61)

Bumps
[https://github.com/pre-commit/pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
from f1dff44d3a9ae852957f34def96390f28719c232 to
fa6b006f0e53d6c0a4a30d6f7b1200a899444634.
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a
href="https://github.com/pre-commit/pre-commit-hooks/blob/main/CHANGELOG.md">https://github.com/pre-commit/pre-commit-hooks's
changelog</a>.</em></p>
<blockquote>
<h1>6.0.0 - 2025-08-09</h1>
<h2>Fixes</h2>
<ul>
<li><code>check-shebang-scripts-are-executable</code>: improve error
message.
<ul>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1115">#1115</a>
PR by <a
href="https://github.com/homebysix"><code>@​homebysix</code></a>.</li>
</ul>
</li>
</ul>
<h2>Migrating</h2>
<ul>
<li>now requires python &gt;= 3.9.
<ul>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1098">#1098</a>
PR by <a
href="https://github.com/asottile"><code>@​asottile</code></a>.</li>
</ul>
</li>
<li><code>file-contents-sorter</code>: disallow <code>--unique</code>
and <code>--ignore-case</code> at the same
time.
<ul>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1095">#1095</a>
PR by <a
href="https://github.com/nemacysts"><code>@​nemacysts</code></a>.</li>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/794">#794</a>
issue by <a
href="https://github.com/teksturi"><code>@​teksturi</code></a>.</li>
</ul>
</li>
<li>Removed <code>check-byte-order-marker</code> and
<code>fix-encoding-pragma</code>.
<ul>
<li><code>check-byte-order-marker</code>: migrate to
<code>fix-byte-order-marker</code>.</li>
<li><code>fix-encoding-pragma</code>: migrate to
<code>pyupgrade</code>.</li>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1034">#1034</a>
PR by <a href="https://github.com/mxr"><code>@​mxr</code></a>.</li>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1032">#1032</a>
issue by <a href="https://github.com/mxr"><code>@​mxr</code></a>.</li>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/522">#522</a>
PR by <a
href="https://github.com/jgowdy"><code>@​jgowdy</code></a>.</li>
</ul>
</li>
</ul>
<h1>5.0.0 - 2024-10-05</h1>
<h3>Features</h3>
<ul>
<li><code>requirements-txt-fixer</code>: also remove
<code>pkg_resources==...</code>.
<ul>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/850">#850</a>
PR by <a
href="https://github.com/ericfrederich"><code>@​ericfrederich</code></a>.</li>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1030">#1030</a>
issue by <a
href="https://github.com/ericfrederich"><code>@​ericfrederich</code></a>.</li>
</ul>
</li>
<li><code>check-illegal-windows-names</code>: new hook!
<ul>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1044">#1044</a>
PR by <a
href="https://github.com/ericfrederich"><code>@​ericfrederich</code></a>.</li>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/589">#589</a>
issue by <a
href="https://github.com/ericfrederich"><code>@​ericfrederich</code></a>.</li>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1049">#1049</a>
PR by <a
href="https://github.com/Jeffrey-Lim"><code>@​Jeffrey-Lim</code></a>.</li>
</ul>
</li>
<li><code>pretty-format-json</code>: continue processing even if a file
has a json error.
<ul>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1039">#1039</a>
PR by <a
href="https://github.com/amarvin"><code>@​amarvin</code></a>.</li>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1038">#1038</a>
issue by <a
href="https://github.com/amarvin"><code>@​amarvin</code></a>.</li>
</ul>
</li>
</ul>
<h3>Fixes</h3>
<ul>
<li><code>destroyed-symlinks</code>: set <code>stages</code> to
<code>[pre-commit, pre-push, manual]</code>
<ul>
<li>PR <a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1085">#1085</a>
by <a
href="https://github.com/AdrianDC"><code>@​AdrianDC</code></a>.</li>
</ul>
</li>
</ul>
<h3>Migrating</h3>
<ul>
<li>pre-commit-hooks now requires
<code>pre-commit&gt;=3.2.0</code>.</li>
<li>use non-deprecated names for <code>stages</code>.
<ul>
<li><a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1093">#1093</a>
PR by <a
href="https://github.com/asottile"><code>@​asottile</code></a>.</li>
</ul>
</li>
</ul>
<h1>4.6.0 - 2024-04-06</h1>
<h3>Features</h3>
<ul>
<li><code>requirements-txt-fixer</code>: remove duplicate packages.</li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/fa6b006f0e53d6c0a4a30d6f7b1200a899444634"><code>fa6b006</code></a>
Merge pull request <a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1256">#1256</a>
from pre-commit/pre-commit-ci-update-config</li>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/969e6999339ac3db21d3da51332435e50af298a6"><code>969e699</code></a>
[pre-commit.ci] pre-commit autoupdate</li>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/f23336e5dc4bf11588d7db19f675418cf570971b"><code>f23336e</code></a>
Merge pull request <a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1254">#1254</a>
from pre-commit/pre-commit-ci-update-config</li>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/cd561649165e90ed9df7a86469c2bf7671290be2"><code>cd56164</code></a>
[pre-commit.ci] pre-commit autoupdate</li>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/803469bde8523f208d030ce33f575d7bee0ba9bf"><code>803469b</code></a>
Merge pull request <a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1251">#1251</a>
from pre-commit/pre-commit-ci-update-config</li>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/722380c3a37595d3136e9a8efccb41315ae4bb83"><code>722380c</code></a>
[pre-commit.ci] pre-commit autoupdate</li>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/b89c5eef3ba3a74ecd506d968e63a8b80f697abf"><code>b89c5ee</code></a>
Merge pull request <a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1250">#1250</a>
from pre-commit/pre-commit-ci-update-config</li>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/6f16fa706534b6387527b2500839aaf1a5d4098b"><code>6f16fa7</code></a>
[pre-commit.ci] pre-commit autoupdate</li>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/d1283494cbdb854a9d6bbaa97275575a21d0e9e4"><code>d128349</code></a>
Merge pull request <a
href="https://redirect.github.com/pre-commit/pre-commit-hooks/issues/1247">#1247</a>
from pre-commit/pre-commit-ci-update-config</li>
<li><a
href="https://github.com/pre-commit/pre-commit-hooks/commit/8f4856d0a30818b9509f8283ed941932d49d9699"><code>8f4856d</code></a>
[pre-commit.ci] pre-commit autoupdate</li>
<li>See full diff in <a
href="https://github.com/pre-commit/pre-commit-hooks/compare/f1dff44d3a9ae852957f34def96390f28719c232...fa6b006f0e53d6c0a4a30d6f7b1200a899444634">compare
view</a></li>
</ul>
</details>
<br />


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
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`9897226`](9897226307dcedc4c30b1f2da71a02b087436482))
- [SKIP CI] [GA] bump the actions-official group in /.github/workflows with 2 updates (#79)

Bumps the actions-official group in /.github/workflows with 2 updates:
[actions/setup-python](https://github.com/actions/setup-python) and
[actions/labeler](https://github.com/actions/labeler).

Updates `actions/setup-python` from 5.5.0 to 6.2.0
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/actions/setup-python/releases">actions/setup-python's
releases</a>.</em></p>
<blockquote>
<h2>v6.2.0</h2>
<h2>What's Changed</h2>
<h3>Dependency Upgrades</h3>
<ul>
<li>Upgrade dependencies to Node 24 compatible versions by <a
href="https://github.com/salmanmkc"><code>@​salmanmkc</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1259">actions/setup-python#1259</a></li>
<li>Upgrade urllib3 from 2.5.0 to 2.6.3 in <code>/__tests__/data</code>
by <a href="https://github.com/dependabot"><code>@​dependabot</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1253">actions/setup-python#1253</a>
and <a
href="https://redirect.github.com/actions/setup-python/pull/1264">actions/setup-python#1264</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/actions/setup-python/compare/v6...v6.2.0">https://github.com/actions/setup-python/compare/v6...v6.2.0</a></p>
<h2>v6.1.0</h2>
<h2>What's Changed</h2>
<h3>Enhancements:</h3>
<ul>
<li>Add support for <code>pip-install</code> input by <a
href="https://github.com/gowridurgad"><code>@​gowridurgad</code></a> in
<a
href="https://redirect.github.com/actions/setup-python/pull/1201">actions/setup-python#1201</a></li>
<li>Add graalpy early-access and windows builds by <a
href="https://github.com/timfel"><code>@​timfel</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/880">actions/setup-python#880</a></li>
</ul>
<h3>Dependency and Documentation updates:</h3>
<ul>
<li>Enhanced wording and updated example usage for
<code>allow-prereleases</code> by <a
href="https://github.com/yarikoptic"><code>@​yarikoptic</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/979">actions/setup-python#979</a></li>
<li>Upgrade urllib3 from 1.26.19 to 2.5.0 and document breaking changes
in v6 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1139">actions/setup-python#1139</a></li>
<li>Upgrade typescript from 5.4.2 to 5.9.3 and Documentation update by
<a href="https://github.com/dependabot"><code>@​dependabot</code></a> in
<a
href="https://redirect.github.com/actions/setup-python/pull/1094">actions/setup-python#1094</a></li>
<li>Upgrade actions/publish-action from 0.3.0 to 0.4.0 &amp;
Documentation update for pip-install input by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1199">actions/setup-python#1199</a></li>
<li>Upgrade requests from 2.32.2 to 2.32.4 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1130">actions/setup-python#1130</a></li>
<li>Upgrade prettier from 3.5.3 to 3.6.2 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1234">actions/setup-python#1234</a></li>
<li>Upgrade <code>@​types/node</code> from 24.1.0 to 24.9.1 and update
macos-13 to macos-15-intel by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1235">actions/setup-python#1235</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a
href="https://github.com/yarikoptic"><code>@​yarikoptic</code></a> made
their first contribution in <a
href="https://redirect.github.com/actions/setup-python/pull/979">actions/setup-python#979</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/actions/setup-python/compare/v6...v6.1.0">https://github.com/actions/setup-python/compare/v6...v6.1.0</a></p>
<h2>v6.0.0</h2>
<h2>What's Changed</h2>
<h3>Breaking Changes</h3>
<ul>
<li>Upgrade to node 24 by <a
href="https://github.com/salmanmkc"><code>@​salmanmkc</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1164">actions/setup-python#1164</a></li>
</ul>
<p>Make sure your runner is on version v2.327.1 or later to ensure
compatibility with this release. <a
href="https://github.com/actions/runner/releases/tag/v2.327.1">See
Release Notes</a></p>
<h3>Enhancements:</h3>
<ul>
<li>Add support for <code>pip-version</code> by <a
href="https://github.com/priyagupta108"><code>@​priyagupta108</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1129">actions/setup-python#1129</a></li>
<li>Enhance reading from .python-version by <a
href="https://github.com/krystof-k"><code>@​krystof-k</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/787">actions/setup-python#787</a></li>
<li>Add version parsing from Pipfile by <a
href="https://github.com/aradkdj"><code>@​aradkdj</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1067">actions/setup-python#1067</a></li>
</ul>
<h3>Bug fixes:</h3>
<ul>
<li>Clarify pythonLocation behaviour for PyPy and GraalPy in environment
variables by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1183">actions/setup-python#1183</a></li>
<li>Change missing cache directory error to warning by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1182">actions/setup-python#1182</a></li>
<li>Add Architecture-Specific PATH Management for Python with --user
Flag on Windows by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1122">actions/setup-python#1122</a></li>
<li>Include python version in PyPy python-version output by <a
href="https://github.com/cdce8p"><code>@​cdce8p</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1110">actions/setup-python#1110</a></li>
<li>Update docs: clarification on pip authentication with setup-python
by <a
href="https://github.com/priya-kinthali"><code>@​priya-kinthali</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1156">actions/setup-python#1156</a></li>
</ul>
<h3>Dependency updates:</h3>
<ul>
<li>Upgrade idna from 2.9 to 3.7 in /<strong>tests</strong>/data by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/actions/setup-python/pull/843">actions/setup-python#843</a></li>
<li>Upgrade form-data to fix critical vulnerabilities <a
href="https://redirect.github.com/actions/setup-python/issues/182">#182</a>
&amp; <a
href="https://redirect.github.com/actions/setup-python/issues/183">#183</a>
by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1163">actions/setup-python#1163</a></li>
<li>Upgrade setuptools to 78.1.1 to fix path traversal vulnerability in
PackageIndex.download by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1165">actions/setup-python#1165</a></li>
<li>Upgrade actions/checkout from 4 to 5 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/actions/setup-python/pull/1181">actions/setup-python#1181</a></li>
<li>Upgrade <code>@​actions/tool-cache</code> from 2.0.1 to 2.0.2 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/actions/setup-python/pull/1095">actions/setup-python#1095</a></li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/actions/setup-python/commit/a309ff8b426b58ec0e2a45f0f869d46889d02405"><code>a309ff8</code></a>
Bump urllib3 from 2.6.0 to 2.6.3 in /<strong>tests</strong>/data (<a
href="https://redirect.github.com/actions/setup-python/issues/1264">#1264</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/bfe8cc55a7890e3d6672eda6460ef37bfcc70755"><code>bfe8cc5</code></a>
Upgrade <a href="https://github.com/actions"><code>@​actions</code></a>
dependencies to Node 24 compatible versions (<a
href="https://redirect.github.com/actions/setup-python/issues/1259">#1259</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/4f41a90a1f38628c7ccc608d05fbafe701bc20ae"><code>4f41a90</code></a>
Bump urllib3 from 2.5.0 to 2.6.0 in /<strong>tests</strong>/data (<a
href="https://redirect.github.com/actions/setup-python/issues/1253">#1253</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/83679a892e2d95755f2dac6acb0bfd1e9ac5d548"><code>83679a8</code></a>
Bump <code>@​types/node</code> from 24.1.0 to 24.9.1 and update macos-13
to macos-15-intel ...</li>
<li><a
href="https://github.com/actions/setup-python/commit/bfc4944b43a5d84377eca3cf6ab5b7992ba61923"><code>bfc4944</code></a>
Bump prettier from 3.5.3 to 3.6.2 (<a
href="https://redirect.github.com/actions/setup-python/issues/1234">#1234</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/97aeb3efb8a852c559869050c7fb175b4efcc8cf"><code>97aeb3e</code></a>
Bump requests from 2.32.2 to 2.32.4 in /<strong>tests</strong>/data (<a
href="https://redirect.github.com/actions/setup-python/issues/1130">#1130</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/443da59188462e2402e2942686db5aa6723f4bed"><code>443da59</code></a>
Bump actions/publish-action from 0.3.0 to 0.4.0 &amp; Documentation
update for pi...</li>
<li><a
href="https://github.com/actions/setup-python/commit/cfd55ca82492758d853442341ad4d8010466803a"><code>cfd55ca</code></a>
graalpy: add graalpy early-access and windows builds (<a
href="https://redirect.github.com/actions/setup-python/issues/880">#880</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/bba65e51ff35d50c6dbaaacd8a4681db13aa7cb4"><code>bba65e5</code></a>
Bump typescript from 5.4.2 to 5.9.3 and update docs/advanced-usage.md
(<a
href="https://redirect.github.com/actions/setup-python/issues/1094">#1094</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/18566f86b301499665bd3eb1a2247e0849c64fa5"><code>18566f8</code></a>
Improve wording and &quot;fix example&quot; (remove 3.13) on testing
against pre-releas...</li>
<li>Additional commits viewable in <a
href="https://github.com/actions/setup-python/compare/v5.5.0...v6.2.0">compare
view</a></li>
</ul>
</details>
<br />

Updates `actions/labeler` from 6.0.1 to 6.1.0
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/actions/labeler/releases">actions/labeler's
releases</a>.</em></p>
<blockquote>
<h2>v6.1.0</h2>
<h2>Enhancements</h2>
<ul>
<li>Add changed-files-labels-limit and max-files-changed configuration
options to cap the number of labels added by <a
href="https://github.com/bluca"><code>@​bluca</code></a> in <a
href="https://redirect.github.com/actions/labeler/pull/923">actions/labeler#923</a></li>
</ul>
<h2>Bug Fixes</h2>
<ul>
<li>Improve Labeler Action documentation and permission error handling
by <a
href="https://github.com/chiranjib-swain"><code>@​chiranjib-swain</code></a>
in <a
href="https://redirect.github.com/actions/labeler/pull/897">actions/labeler#897</a></li>
<li>Preserve manually added labels during workflow runs and refine label
synchronization logic by <a
href="https://github.com/chiranjib-swain"><code>@​chiranjib-swain</code></a>
in <a
href="https://redirect.github.com/actions/labeler/pull/917">actions/labeler#917</a></li>
</ul>
<h2>Dependency Updates</h2>
<ul>
<li>Upgrade brace-expansion from 1.1.11 to 1.1.12 and document breaking
changes in v6 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/labeler/pull/877">actions/labeler#877</a></li>
<li>Upgrade minimatch from 10.0.1 to 10.2.3 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/labeler/pull/926">actions/labeler#926</a></li>
<li>Upgrade dependencies (<code>@​actions/core</code>,
<code>@​actions/github</code>, js-yaml, minimatch, <a
href="https://github.com/typescript-eslint"><code>@​typescript-eslint</code></a>)
by <a href="https://github.com/Copilot"><code>@​Copilot</code></a> in <a
href="https://redirect.github.com/actions/labeler/pull/934">actions/labeler#934</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a
href="https://github.com/chiranjib-swain"><code>@​chiranjib-swain</code></a>
made their first contribution in <a
href="https://redirect.github.com/actions/labeler/pull/897">actions/labeler#897</a></li>
<li><a href="https://github.com/bluca"><code>@​bluca</code></a> made
their first contribution in <a
href="https://redirect.github.com/actions/labeler/pull/923">actions/labeler#923</a></li>
<li><a href="https://github.com/Copilot"><code>@​Copilot</code></a> made
their first contribution in <a
href="https://redirect.github.com/actions/labeler/pull/934">actions/labeler#934</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/actions/labeler/compare/v6...v6.1.0">https://github.com/actions/labeler/compare/v6...v6.1.0</a></p>
</blockquote>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/actions/labeler/commit/f27b608878404679385c85cfa523b85ccb86e213"><code>f27b608</code></a>
chore: upgrade dependencies (<code>@​actions/core</code>,
<code>@​actions/github</code>, js-yaml, minimat...</li>
<li><a
href="https://github.com/actions/labeler/commit/c5dadc2a45784a4b6adfcd20fea3465da3a5f904"><code>c5dadc2</code></a>
Add 'changed-files-labels-limit' and 'max-files-changed' configs to
allow cap...</li>
<li><a
href="https://github.com/actions/labeler/commit/e52e4fb63ed5cd0e07abaad9826b2a893ccb921f"><code>e52e4fb</code></a>
Bump minimatch from 10.0.1 to 10.2.3 (<a
href="https://redirect.github.com/actions/labeler/issues/926">#926</a>)</li>
<li><a
href="https://github.com/actions/labeler/commit/77a4082b841706ac431479b7e2bb11216ffef250"><code>77a4082</code></a>
Fix: Preserve manually added labels during workflow run and refine label
sync...</li>
<li><a
href="https://github.com/actions/labeler/commit/25abb3cad4f14b7ac27968a495c37798860a5a1a"><code>25abb3c</code></a>
Improve Labeler Action Documentation and Error Handling for Permissions
(<a
href="https://redirect.github.com/actions/labeler/issues/897">#897</a>)</li>
<li><a
href="https://github.com/actions/labeler/commit/395c8cfdb1e1e691cc4bad0dd315820af8eb67fd"><code>395c8cf</code></a>
Bump brace-expansion from 1.1.11 to 1.1.12 and document breaking changes
in v...</li>
<li>See full diff in <a
href="https://github.com/actions/labeler/compare/634933edcd8ababfe52f92936142cc22ac488b1b...f27b608878404679385c85cfa523b85ccb86e213">compare
view</a></li>
</ul>
</details>
<br />


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
- `@dependabot ignore <dependency name> major version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's major version (unless you unignore this specific
dependency's major version or upgrade to it yourself)
- `@dependabot ignore <dependency name> minor version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's minor version (unless you unignore this specific
dependency's minor version or upgrade to it yourself)
- `@dependabot ignore <dependency name>` will close this group update PR
and stop Dependabot creating any more for the specific dependency
(unless you unignore this specific dependency or upgrade to it yourself)
- `@dependabot unignore <dependency name>` will remove all of the ignore
conditions of the specified dependency
- `@dependabot unignore <dependency name> <ignore condition>` will
remove the ignore condition of the specified dependency and ignore
conditions


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`d03f955`](d03f95549de7a327e918fd50f31097b141f17c17))
- [SKIP CI] [GA] bump peter-evans/create-pull-request from 7.0.6 to 8.1.1 in /.github/workflows in the peter-evans group (#80)

Bumps the peter-evans group in /.github/workflows with 1 update:
[peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request).

Updates `peter-evans/create-pull-request` from 7.0.6 to 8.1.1
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/peter-evans/create-pull-request/releases">peter-evans/create-pull-request's
releases</a>.</em></p>
<blockquote>
<h2>Create Pull Request v8.1.1</h2>
<h2>What's Changed</h2>
<ul>
<li>build(deps-dev): bump the npm group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4305">peter-evans/create-pull-request#4305</a></li>
<li>build(deps): bump minimatch by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4311">peter-evans/create-pull-request#4311</a></li>
<li>build(deps): bump the github-actions group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4316">peter-evans/create-pull-request#4316</a></li>
<li>build(deps): bump <code>@​tootallnate/once</code> and
jest-environment-jsdom by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4323">peter-evans/create-pull-request#4323</a></li>
<li>build(deps-dev): bump undici from 6.23.0 to 6.24.0 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4328">peter-evans/create-pull-request#4328</a></li>
<li>build(deps-dev): bump flatted from 3.3.1 to 3.4.2 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4334">peter-evans/create-pull-request#4334</a></li>
<li>build(deps): bump picomatch by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4339">peter-evans/create-pull-request#4339</a></li>
<li>build(deps-dev): bump handlebars from 4.7.8 to 4.7.9 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4344">peter-evans/create-pull-request#4344</a></li>
<li>build(deps-dev): bump the npm group with 3 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4349">peter-evans/create-pull-request#4349</a></li>
<li>fix: retry post-creation API calls on 422 eventual consistency
errors by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4356">peter-evans/create-pull-request#4356</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/peter-evans/create-pull-request/compare/v8.1.0...v8.1.1">https://github.com/peter-evans/create-pull-request/compare/v8.1.0...v8.1.1</a></p>
<h2>Create Pull Request v8.1.0</h2>
<h2>What's Changed</h2>
<ul>
<li>README.md: bump given GitHub actions to their latest versions by <a
href="https://github.com/deining"><code>@​deining</code></a> in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4265">peter-evans/create-pull-request#4265</a></li>
<li>build(deps): bump the github-actions group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4273">peter-evans/create-pull-request#4273</a></li>
<li>build(deps-dev): bump the npm group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4274">peter-evans/create-pull-request#4274</a></li>
<li>build(deps-dev): bump undici from 6.22.0 to 6.23.0 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4284">peter-evans/create-pull-request#4284</a></li>
<li>Update distribution by <a
href="https://github.com/actions-bot"><code>@​actions-bot</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4289">peter-evans/create-pull-request#4289</a></li>
<li>fix: Handle remote prune failures gracefully on self-hosted runners
by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4295">peter-evans/create-pull-request#4295</a></li>
<li>feat: add <code>@​octokit/plugin-retry</code> to handle retriable
server errors by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4298">peter-evans/create-pull-request#4298</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a href="https://github.com/deining"><code>@​deining</code></a> made
their first contribution in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4265">peter-evans/create-pull-request#4265</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/peter-evans/create-pull-request/compare/v8.0.0...v8.1.0">https://github.com/peter-evans/create-pull-request/compare/v8.0.0...v8.1.0</a></p>
<h2>Create Pull Request v8.0.0</h2>
<h2>What's new in v8</h2>
<ul>
<li>Requires <a
href="https://github.com/actions/runner/releases/tag/v2.327.1">Actions
Runner v2.327.1</a> or later if you are using a self-hosted runner for
Node 24 support.</li>
</ul>
<h2>What's Changed</h2>
<ul>
<li>chore: Update checkout action version to v6 by <a
href="https://github.com/yonas"><code>@​yonas</code></a> in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4258">peter-evans/create-pull-request#4258</a></li>
<li>Update actions/checkout references to <a
href="https://github.com/v6"><code>@​v6</code></a> in docs by <a
href="https://github.com/Copilot"><code>@​Copilot</code></a> in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4259">peter-evans/create-pull-request#4259</a></li>
<li>feat: v8 by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4260">peter-evans/create-pull-request#4260</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a href="https://github.com/yonas"><code>@​yonas</code></a> made
their first contribution in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4258">peter-evans/create-pull-request#4258</a></li>
<li><a href="https://github.com/Copilot"><code>@​Copilot</code></a> made
their first contribution in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4259">peter-evans/create-pull-request#4259</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/peter-evans/create-pull-request/compare/v7.0.11...v8.0.0">https://github.com/peter-evans/create-pull-request/compare/v7.0.11...v8.0.0</a></p>
<h2>Create Pull Request v7.0.11</h2>
<h2>What's Changed</h2>
<ul>
<li>fix: restrict remote prune to self-hosted runners by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4250">peter-evans/create-pull-request#4250</a></li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/5f6978faf089d4d20b00c7766989d076bb2fc7f1"><code>5f6978f</code></a>
fix: retry post-creation API calls on 422 eventual consistency errors
(<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4356">#4356</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/d32e88dac789dcc7906e7d26f69f24116fa9c97d"><code>d32e88d</code></a>
build(deps-dev): bump the npm group with 3 updates (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4349">#4349</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/8170bccad11c0df62542c04dcaefe36d342dfd39"><code>8170bcc</code></a>
build(deps-dev): bump handlebars from 4.7.8 to 4.7.9 (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4344">#4344</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/00418193b417f888dbf1d993c5c0d31d27fdc7de"><code>0041819</code></a>
build(deps): bump picomatch (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4339">#4339</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/b993918c8536b6d44706130734d5456879762b27"><code>b993918</code></a>
build(deps-dev): bump flatted from 3.3.1 to 3.4.2 (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4334">#4334</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/36d7c8468b48f9c2f8f29e260e82f10d4b90d2bd"><code>36d7c84</code></a>
build(deps-dev): bump undici from 6.23.0 to 6.24.0 (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4328">#4328</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/a45d1fb447fcaf601166e405fd4f335cde1a8aa8"><code>a45d1fb</code></a>
build(deps): bump <code>@​tootallnate/once</code> and
jest-environment-jsdom (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4323">#4323</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/3499eb61835cc0015c0b786e203d74b1e8f55e43"><code>3499eb6</code></a>
build(deps): bump the github-actions group with 2 updates (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4316">#4316</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/3f3b473b8c148f5a7520efb4d1f9a70eea3d9d1f"><code>3f3b473</code></a>
build(deps): bump minimatch (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4311">#4311</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/6699836a213cf8b28c4f0408a404a6ac79d4458a"><code>6699836</code></a>
build(deps-dev): bump the npm group with 2 updates (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4305">#4305</a>)</li>
<li>Additional commits viewable in <a
href="https://github.com/peter-evans/create-pull-request/compare/67ccf781d68cd99b580ae25a5c18a1cc84ffff1f...5f6978faf089d4d20b00c7766989d076bb2fc7f1">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=peter-evans/create-pull-request&package-manager=github_actions&previous-version=7.0.6&new-version=8.1.1)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

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
- `@dependabot ignore <dependency name> major version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's major version (unless you unignore this specific
dependency's major version or upgrade to it yourself)
- `@dependabot ignore <dependency name> minor version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's minor version (unless you unignore this specific
dependency's minor version or upgrade to it yourself)
- `@dependabot ignore <dependency name>` will close this group update PR
and stop Dependabot creating any more for the specific dependency
(unless you unignore this specific dependency or upgrade to it yourself)
- `@dependabot unignore <dependency name>` will remove all of the ignore
conditions of the specified dependency
- `@dependabot unignore <dependency name> <ignore condition>` will
remove the ignore condition of the specified dependency and ignore
conditions


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`c2c909c`](c2c909c99eef37e728d4cf89e8e2f60c54424a20))
- [SKIP CI] [GA] bump raven-actions/actionlint from 2.0.1 to 2.1.2 in /.github/workflows in the community-actions group (#81)

Bumps the community-actions group in /.github/workflows with 1 update:
[raven-actions/actionlint](https://github.com/raven-actions/actionlint).

Updates `raven-actions/actionlint` from 2.0.1 to 2.1.2
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/raven-actions/actionlint/releases">raven-actions/actionlint's
releases</a>.</em></p>
<blockquote>
<h2>v2.1.2</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>docs: fix make link to code of conduct absolute <a
href="https://github.com/avishj"><code>@​avishj</code></a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/55">#55</a>)</li>
<li>fix: use legacy peer dependencies to resolve installation failures
<a
href="https://github.com/jessehouwing"><code>@​jessehouwing</code></a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/57">#57</a>)</li>
</ul>
<h2>👥 Contributors</h2>
<p><a href="https://github.com/avishj"><code>@​avishj</code></a> and <a
href="https://github.com/jessehouwing"><code>@​jessehouwing</code></a></p>
<p>See details of all code changes: <a
href="https://github.com/raven-actions/actionlint/compare/v2.1.1...v2.1.2">https://github.com/raven-actions/actionlint/compare/v2.1.1...v2.1.2</a>
since previous release.</p>
<h2>v2.1.1</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>ci(deps): bump actions/cache from 5.0.2 to 5.0.3 in the all group
@<a href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/53">#53</a>)</li>
<li>fix: pin installed version of <code>@​actions/tool-cache</code> <a
href="https://github.com/hghmn"><code>@​hghmn</code></a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/52">#52</a>)</li>
<li>ci(deps): bump the all group across 1 directory with 2 updates @<a
href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/50">#50</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/47">#47</a>)</li>
<li>ci(deps): bump actions/cache from 4.3.0 to 5.0.1 in the all group
@<a href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/48">#48</a>)</li>
</ul>
<h2>👥 Contributors</h2>
<p><a
href="https://github.com/DariuszPorowski"><code>@​DariuszPorowski</code></a>,
<a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot],
<a href="https://github.com/hghmn"><code>@​hghmn</code></a>, <a
href="https://github.com/raven-actions-sync"><code>@​raven-actions-sync</code></a>[bot],
<a href="https://github.com/apps/dependabot">dependabot[bot]</a> and <a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a></p>
<p>See details of all code changes: <a
href="https://github.com/raven-actions/actionlint/compare/v2.1.0...v2.1.1">https://github.com/raven-actions/actionlint/compare/v2.1.0...v2.1.1</a>
since previous release.</p>
<h2>v2.1.0</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>update action versions in workflows and action metadata <a
href="https://github.com/DariuszPorowski"><code>@​DariuszPorowski</code></a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/46">#46</a>)</li>
</ul>
<h2>👥 Contributors</h2>
<p><a
href="https://github.com/DariuszPorowski"><code>@​DariuszPorowski</code></a></p>
<p>See details of all code changes: <a
href="https://github.com/raven-actions/actionlint/compare/v2.0.2...v2.1.0">https://github.com/raven-actions/actionlint/compare/v2.0.2...v2.1.0</a>
since previous release.</p>
<h2>v2.0.2</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>ci(deps): bump actions/checkout from 5 to 6 in the all group @<a
href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/45">#45</a>)</li>
<li>fix: don't interfere with repo package.json <a
href="https://github.com/allejo"><code>@​allejo</code></a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/43">#43</a>)</li>
<li>ci(deps): bump actions/cache from 4.2.4 to 4.3.0 in the all group
@<a href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/42">#42</a>)</li>
<li>ci(deps): bump actions/github-script from 7.0.1 to 8.0.0 in the all
group @<a href="https://github.com/apps/dependabot">dependabot[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/41">#41</a>)</li>
<li>ci(deps): bump the all group across 1 directory with 2 updates @<a
href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/40">#40</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/38">#38</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/37">#37</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/36">#36</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/35">#35</a>)</li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/raven-actions/actionlint/commit/205b530c5d9fa8f44ae9ed59f341a0db994aa6f8"><code>205b530</code></a>
docs: fix make link to code of conduct absolute (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/55">#55</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/59a077201b1103d536cdbb901e0a56106f08970b"><code>59a0772</code></a>
fix: use legacy peer dependencies to resolve installation failures (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/57">#57</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/e01d1ea33dd6a5ed517d95b4c0c357560ac6f518"><code>e01d1ea</code></a>
chore: add permissions for publish-release job</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/3459946ddcf59c1fb7e850824461df3f55d6133a"><code>3459946</code></a>
ci(deps): bump actions/cache from 5.0.2 to 5.0.3 in the all group (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/53">#53</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/855a9ad92ebcccac55c8f3605ab46bcc588575f8"><code>855a9ad</code></a>
chore: add new URL to .lycheeignore</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/0277f3a759d600efd96680ce7286c7fb071293ec"><code>0277f3a</code></a>
fix: update permissions in release-draft workflow</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/06dd51c3fc6da21d49078939b3d1607b0edebdf4"><code>06dd51c</code></a>
fix: pin installed version of <code>@​actions/tool-cache</code> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/52">#52</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/6fc528e1e3b665b61cde1ca6fc4dc37fd139fa74"><code>6fc528e</code></a>
ci(deps): bump the all group across 1 directory with 2 updates (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/50">#50</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/6e8b85b8060c21661deacadf48389d0b2c896ea3"><code>6e8b85b</code></a>
chore: synced file(s) with raven-actions/.workflows (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/47">#47</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/580b34edf3f0039a5691481c6081049971ecd530"><code>580b34e</code></a>
ci(deps): bump actions/cache from 4.3.0 to 5.0.1 in the all group (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/48">#48</a>)</li>
<li>Additional commits viewable in <a
href="https://github.com/raven-actions/actionlint/compare/3a24062651993d40fed1019b58ac6fbdfbf276cc...205b530c5d9fa8f44ae9ed59f341a0db994aa6f8">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=raven-actions/actionlint&package-manager=github_actions&previous-version=2.0.1&new-version=2.1.2)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

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
- `@dependabot ignore <dependency name> major version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's major version (unless you unignore this specific
dependency's major version or upgrade to it yourself)
- `@dependabot ignore <dependency name> minor version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's minor version (unless you unignore this specific
dependency's minor version or upgrade to it yourself)
- `@dependabot ignore <dependency name>` will close this group update PR
and stop Dependabot creating any more for the specific dependency
(unless you unignore this specific dependency or upgrade to it yourself)
- `@dependabot unignore <dependency name>` will remove all of the ignore
conditions of the specified dependency
- `@dependabot unignore <dependency name> <ignore condition>` will
remove the ignore condition of the specified dependency and ignore
conditions


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`3b3836f`](3b3836f8ff2d29b3cbd59184f4b754952701b31f))
- [SKIP CI] [GA] bump raven-actions/actionlint from 2.0.1 to 2.1.2 in /.github/workflows in the community-actions group (#87)

Bumps the community-actions group in /.github/workflows with 1 update:
[raven-actions/actionlint](https://github.com/raven-actions/actionlint).

Updates `raven-actions/actionlint` from 2.0.1 to 2.1.2
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/raven-actions/actionlint/releases">raven-actions/actionlint's
releases</a>.</em></p>
<blockquote>
<h2>v2.1.2</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>docs: fix make link to code of conduct absolute <a
href="https://github.com/avishj"><code>@​avishj</code></a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/55">#55</a>)</li>
<li>fix: use legacy peer dependencies to resolve installation failures
<a
href="https://github.com/jessehouwing"><code>@​jessehouwing</code></a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/57">#57</a>)</li>
</ul>
<h2>👥 Contributors</h2>
<p><a href="https://github.com/avishj"><code>@​avishj</code></a> and <a
href="https://github.com/jessehouwing"><code>@​jessehouwing</code></a></p>
<p>See details of all code changes: <a
href="https://github.com/raven-actions/actionlint/compare/v2.1.1...v2.1.2">https://github.com/raven-actions/actionlint/compare/v2.1.1...v2.1.2</a>
since previous release.</p>
<h2>v2.1.1</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>ci(deps): bump actions/cache from 5.0.2 to 5.0.3 in the all group
@<a href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/53">#53</a>)</li>
<li>fix: pin installed version of <code>@​actions/tool-cache</code> <a
href="https://github.com/hghmn"><code>@​hghmn</code></a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/52">#52</a>)</li>
<li>ci(deps): bump the all group across 1 directory with 2 updates @<a
href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/50">#50</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/47">#47</a>)</li>
<li>ci(deps): bump actions/cache from 4.3.0 to 5.0.1 in the all group
@<a href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/48">#48</a>)</li>
</ul>
<h2>👥 Contributors</h2>
<p><a
href="https://github.com/DariuszPorowski"><code>@​DariuszPorowski</code></a>,
<a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot],
<a href="https://github.com/hghmn"><code>@​hghmn</code></a>, <a
href="https://github.com/raven-actions-sync"><code>@​raven-actions-sync</code></a>[bot],
<a href="https://github.com/apps/dependabot">dependabot[bot]</a> and <a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a></p>
<p>See details of all code changes: <a
href="https://github.com/raven-actions/actionlint/compare/v2.1.0...v2.1.1">https://github.com/raven-actions/actionlint/compare/v2.1.0...v2.1.1</a>
since previous release.</p>
<h2>v2.1.0</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>update action versions in workflows and action metadata <a
href="https://github.com/DariuszPorowski"><code>@​DariuszPorowski</code></a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/46">#46</a>)</li>
</ul>
<h2>👥 Contributors</h2>
<p><a
href="https://github.com/DariuszPorowski"><code>@​DariuszPorowski</code></a></p>
<p>See details of all code changes: <a
href="https://github.com/raven-actions/actionlint/compare/v2.0.2...v2.1.0">https://github.com/raven-actions/actionlint/compare/v2.0.2...v2.1.0</a>
since previous release.</p>
<h2>v2.0.2</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>ci(deps): bump actions/checkout from 5 to 6 in the all group @<a
href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/45">#45</a>)</li>
<li>fix: don't interfere with repo package.json <a
href="https://github.com/allejo"><code>@​allejo</code></a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/43">#43</a>)</li>
<li>ci(deps): bump actions/cache from 4.2.4 to 4.3.0 in the all group
@<a href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/42">#42</a>)</li>
<li>ci(deps): bump actions/github-script from 7.0.1 to 8.0.0 in the all
group @<a href="https://github.com/apps/dependabot">dependabot[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/41">#41</a>)</li>
<li>ci(deps): bump the all group across 1 directory with 2 updates @<a
href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/40">#40</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/38">#38</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/37">#37</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/36">#36</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/35">#35</a>)</li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/raven-actions/actionlint/commit/205b530c5d9fa8f44ae9ed59f341a0db994aa6f8"><code>205b530</code></a>
docs: fix make link to code of conduct absolute (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/55">#55</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/59a077201b1103d536cdbb901e0a56106f08970b"><code>59a0772</code></a>
fix: use legacy peer dependencies to resolve installation failures (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/57">#57</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/e01d1ea33dd6a5ed517d95b4c0c357560ac6f518"><code>e01d1ea</code></a>
chore: add permissions for publish-release job</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/3459946ddcf59c1fb7e850824461df3f55d6133a"><code>3459946</code></a>
ci(deps): bump actions/cache from 5.0.2 to 5.0.3 in the all group (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/53">#53</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/855a9ad92ebcccac55c8f3605ab46bcc588575f8"><code>855a9ad</code></a>
chore: add new URL to .lycheeignore</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/0277f3a759d600efd96680ce7286c7fb071293ec"><code>0277f3a</code></a>
fix: update permissions in release-draft workflow</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/06dd51c3fc6da21d49078939b3d1607b0edebdf4"><code>06dd51c</code></a>
fix: pin installed version of <code>@​actions/tool-cache</code> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/52">#52</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/6fc528e1e3b665b61cde1ca6fc4dc37fd139fa74"><code>6fc528e</code></a>
ci(deps): bump the all group across 1 directory with 2 updates (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/50">#50</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/6e8b85b8060c21661deacadf48389d0b2c896ea3"><code>6e8b85b</code></a>
chore: synced file(s) with raven-actions/.workflows (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/47">#47</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/580b34edf3f0039a5691481c6081049971ecd530"><code>580b34e</code></a>
ci(deps): bump actions/cache from 4.3.0 to 5.0.1 in the all group (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/48">#48</a>)</li>
<li>Additional commits viewable in <a
href="https://github.com/raven-actions/actionlint/compare/3a24062651993d40fed1019b58ac6fbdfbf276cc...205b530c5d9fa8f44ae9ed59f341a0db994aa6f8">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=raven-actions/actionlint&package-manager=github_actions&previous-version=2.0.1&new-version=2.1.2)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

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
- `@dependabot ignore <dependency name> major version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's major version (unless you unignore this specific
dependency's major version or upgrade to it yourself)
- `@dependabot ignore <dependency name> minor version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's minor version (unless you unignore this specific
dependency's minor version or upgrade to it yourself)
- `@dependabot ignore <dependency name>` will close this group update PR
and stop Dependabot creating any more for the specific dependency
(unless you unignore this specific dependency or upgrade to it yourself)
- `@dependabot unignore <dependency name>` will remove all of the ignore
conditions of the specified dependency
- `@dependabot unignore <dependency name> <ignore condition>` will
remove the ignore condition of the specified dependency and ignore
conditions


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`b3ef2a4`](b3ef2a488be8a4c2072e6b3f1a0cabe4b7792f49))
- [SKIP CI] [GA] bump peter-evans/create-pull-request from 7.0.6 to 8.1.1 in /.github/workflows in the peter-evans group (#86)

Bumps the peter-evans group in /.github/workflows with 1 update:
[peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request).

Updates `peter-evans/create-pull-request` from 7.0.6 to 8.1.1
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/peter-evans/create-pull-request/releases">peter-evans/create-pull-request's
releases</a>.</em></p>
<blockquote>
<h2>Create Pull Request v8.1.1</h2>
<h2>What's Changed</h2>
<ul>
<li>build(deps-dev): bump the npm group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4305">peter-evans/create-pull-request#4305</a></li>
<li>build(deps): bump minimatch by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4311">peter-evans/create-pull-request#4311</a></li>
<li>build(deps): bump the github-actions group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4316">peter-evans/create-pull-request#4316</a></li>
<li>build(deps): bump <code>@​tootallnate/once</code> and
jest-environment-jsdom by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4323">peter-evans/create-pull-request#4323</a></li>
<li>build(deps-dev): bump undici from 6.23.0 to 6.24.0 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4328">peter-evans/create-pull-request#4328</a></li>
<li>build(deps-dev): bump flatted from 3.3.1 to 3.4.2 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4334">peter-evans/create-pull-request#4334</a></li>
<li>build(deps): bump picomatch by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4339">peter-evans/create-pull-request#4339</a></li>
<li>build(deps-dev): bump handlebars from 4.7.8 to 4.7.9 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4344">peter-evans/create-pull-request#4344</a></li>
<li>build(deps-dev): bump the npm group with 3 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4349">peter-evans/create-pull-request#4349</a></li>
<li>fix: retry post-creation API calls on 422 eventual consistency
errors by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4356">peter-evans/create-pull-request#4356</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/peter-evans/create-pull-request/compare/v8.1.0...v8.1.1">https://github.com/peter-evans/create-pull-request/compare/v8.1.0...v8.1.1</a></p>
<h2>Create Pull Request v8.1.0</h2>
<h2>What's Changed</h2>
<ul>
<li>README.md: bump given GitHub actions to their latest versions by <a
href="https://github.com/deining"><code>@​deining</code></a> in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4265">peter-evans/create-pull-request#4265</a></li>
<li>build(deps): bump the github-actions group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4273">peter-evans/create-pull-request#4273</a></li>
<li>build(deps-dev): bump the npm group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4274">peter-evans/create-pull-request#4274</a></li>
<li>build(deps-dev): bump undici from 6.22.0 to 6.23.0 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4284">peter-evans/create-pull-request#4284</a></li>
<li>Update distribution by <a
href="https://github.com/actions-bot"><code>@​actions-bot</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4289">peter-evans/create-pull-request#4289</a></li>
<li>fix: Handle remote prune failures gracefully on self-hosted runners
by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4295">peter-evans/create-pull-request#4295</a></li>
<li>feat: add <code>@​octokit/plugin-retry</code> to handle retriable
server errors by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4298">peter-evans/create-pull-request#4298</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a href="https://github.com/deining"><code>@​deining</code></a> made
their first contribution in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4265">peter-evans/create-pull-request#4265</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/peter-evans/create-pull-request/compare/v8.0.0...v8.1.0">https://github.com/peter-evans/create-pull-request/compare/v8.0.0...v8.1.0</a></p>
<h2>Create Pull Request v8.0.0</h2>
<h2>What's new in v8</h2>
<ul>
<li>Requires <a
href="https://github.com/actions/runner/releases/tag/v2.327.1">Actions
Runner v2.327.1</a> or later if you are using a self-hosted runner for
Node 24 support.</li>
</ul>
<h2>What's Changed</h2>
<ul>
<li>chore: Update checkout action version to v6 by <a
href="https://github.com/yonas"><code>@​yonas</code></a> in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4258">peter-evans/create-pull-request#4258</a></li>
<li>Update actions/checkout references to <a
href="https://github.com/v6"><code>@​v6</code></a> in docs by <a
href="https://github.com/Copilot"><code>@​Copilot</code></a> in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4259">peter-evans/create-pull-request#4259</a></li>
<li>feat: v8 by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4260">peter-evans/create-pull-request#4260</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a href="https://github.com/yonas"><code>@​yonas</code></a> made
their first contribution in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4258">peter-evans/create-pull-request#4258</a></li>
<li><a href="https://github.com/Copilot"><code>@​Copilot</code></a> made
their first contribution in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4259">peter-evans/create-pull-request#4259</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/peter-evans/create-pull-request/compare/v7.0.11...v8.0.0">https://github.com/peter-evans/create-pull-request/compare/v7.0.11...v8.0.0</a></p>
<h2>Create Pull Request v7.0.11</h2>
<h2>What's Changed</h2>
<ul>
<li>fix: restrict remote prune to self-hosted runners by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4250">peter-evans/create-pull-request#4250</a></li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/5f6978faf089d4d20b00c7766989d076bb2fc7f1"><code>5f6978f</code></a>
fix: retry post-creation API calls on 422 eventual consistency errors
(<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4356">#4356</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/d32e88dac789dcc7906e7d26f69f24116fa9c97d"><code>d32e88d</code></a>
build(deps-dev): bump the npm group with 3 updates (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4349">#4349</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/8170bccad11c0df62542c04dcaefe36d342dfd39"><code>8170bcc</code></a>
build(deps-dev): bump handlebars from 4.7.8 to 4.7.9 (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4344">#4344</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/00418193b417f888dbf1d993c5c0d31d27fdc7de"><code>0041819</code></a>
build(deps): bump picomatch (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4339">#4339</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/b993918c8536b6d44706130734d5456879762b27"><code>b993918</code></a>
build(deps-dev): bump flatted from 3.3.1 to 3.4.2 (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4334">#4334</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/36d7c8468b48f9c2f8f29e260e82f10d4b90d2bd"><code>36d7c84</code></a>
build(deps-dev): bump undici from 6.23.0 to 6.24.0 (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4328">#4328</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/a45d1fb447fcaf601166e405fd4f335cde1a8aa8"><code>a45d1fb</code></a>
build(deps): bump <code>@​tootallnate/once</code> and
jest-environment-jsdom (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4323">#4323</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/3499eb61835cc0015c0b786e203d74b1e8f55e43"><code>3499eb6</code></a>
build(deps): bump the github-actions group with 2 updates (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4316">#4316</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/3f3b473b8c148f5a7520efb4d1f9a70eea3d9d1f"><code>3f3b473</code></a>
build(deps): bump minimatch (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4311">#4311</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/6699836a213cf8b28c4f0408a404a6ac79d4458a"><code>6699836</code></a>
build(deps-dev): bump the npm group with 2 updates (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4305">#4305</a>)</li>
<li>Additional commits viewable in <a
href="https://github.com/peter-evans/create-pull-request/compare/67ccf781d68cd99b580ae25a5c18a1cc84ffff1f...5f6978faf089d4d20b00c7766989d076bb2fc7f1">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=peter-evans/create-pull-request&package-manager=github_actions&previous-version=7.0.6&new-version=8.1.1)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

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
- `@dependabot ignore <dependency name> major version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's major version (unless you unignore this specific
dependency's major version or upgrade to it yourself)
- `@dependabot ignore <dependency name> minor version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's minor version (unless you unignore this specific
dependency's minor version or upgrade to it yourself)
- `@dependabot ignore <dependency name>` will close this group update PR
and stop Dependabot creating any more for the specific dependency
(unless you unignore this specific dependency or upgrade to it yourself)
- `@dependabot unignore <dependency name>` will remove all of the ignore
conditions of the specified dependency
- `@dependabot unignore <dependency name> <ignore condition>` will
remove the ignore condition of the specified dependency and ignore
conditions


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`0fe16f8`](0fe16f8f90fcda0e95a9fb62860b27b77725d6a1))
- [SKIP CI] [GA] bump the actions-official group in /.github/workflows with 2 updates (#85)

Bumps the actions-official group in /.github/workflows with 2 updates:
[actions/setup-python](https://github.com/actions/setup-python) and
[actions/labeler](https://github.com/actions/labeler).

Updates `actions/setup-python` from 5.5.0 to 6.2.0
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/actions/setup-python/releases">actions/setup-python's
releases</a>.</em></p>
<blockquote>
<h2>v6.2.0</h2>
<h2>What's Changed</h2>
<h3>Dependency Upgrades</h3>
<ul>
<li>Upgrade dependencies to Node 24 compatible versions by <a
href="https://github.com/salmanmkc"><code>@​salmanmkc</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1259">actions/setup-python#1259</a></li>
<li>Upgrade urllib3 from 2.5.0 to 2.6.3 in <code>/__tests__/data</code>
by <a href="https://github.com/dependabot"><code>@​dependabot</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1253">actions/setup-python#1253</a>
and <a
href="https://redirect.github.com/actions/setup-python/pull/1264">actions/setup-python#1264</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/actions/setup-python/compare/v6...v6.2.0">https://github.com/actions/setup-python/compare/v6...v6.2.0</a></p>
<h2>v6.1.0</h2>
<h2>What's Changed</h2>
<h3>Enhancements:</h3>
<ul>
<li>Add support for <code>pip-install</code> input by <a
href="https://github.com/gowridurgad"><code>@​gowridurgad</code></a> in
<a
href="https://redirect.github.com/actions/setup-python/pull/1201">actions/setup-python#1201</a></li>
<li>Add graalpy early-access and windows builds by <a
href="https://github.com/timfel"><code>@​timfel</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/880">actions/setup-python#880</a></li>
</ul>
<h3>Dependency and Documentation updates:</h3>
<ul>
<li>Enhanced wording and updated example usage for
<code>allow-prereleases</code> by <a
href="https://github.com/yarikoptic"><code>@​yarikoptic</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/979">actions/setup-python#979</a></li>
<li>Upgrade urllib3 from 1.26.19 to 2.5.0 and document breaking changes
in v6 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1139">actions/setup-python#1139</a></li>
<li>Upgrade typescript from 5.4.2 to 5.9.3 and Documentation update by
<a href="https://github.com/dependabot"><code>@​dependabot</code></a> in
<a
href="https://redirect.github.com/actions/setup-python/pull/1094">actions/setup-python#1094</a></li>
<li>Upgrade actions/publish-action from 0.3.0 to 0.4.0 &amp;
Documentation update for pip-install input by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1199">actions/setup-python#1199</a></li>
<li>Upgrade requests from 2.32.2 to 2.32.4 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1130">actions/setup-python#1130</a></li>
<li>Upgrade prettier from 3.5.3 to 3.6.2 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1234">actions/setup-python#1234</a></li>
<li>Upgrade <code>@​types/node</code> from 24.1.0 to 24.9.1 and update
macos-13 to macos-15-intel by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1235">actions/setup-python#1235</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a
href="https://github.com/yarikoptic"><code>@​yarikoptic</code></a> made
their first contribution in <a
href="https://redirect.github.com/actions/setup-python/pull/979">actions/setup-python#979</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/actions/setup-python/compare/v6...v6.1.0">https://github.com/actions/setup-python/compare/v6...v6.1.0</a></p>
<h2>v6.0.0</h2>
<h2>What's Changed</h2>
<h3>Breaking Changes</h3>
<ul>
<li>Upgrade to node 24 by <a
href="https://github.com/salmanmkc"><code>@​salmanmkc</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1164">actions/setup-python#1164</a></li>
</ul>
<p>Make sure your runner is on version v2.327.1 or later to ensure
compatibility with this release. <a
href="https://github.com/actions/runner/releases/tag/v2.327.1">See
Release Notes</a></p>
<h3>Enhancements:</h3>
<ul>
<li>Add support for <code>pip-version</code> by <a
href="https://github.com/priyagupta108"><code>@​priyagupta108</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1129">actions/setup-python#1129</a></li>
<li>Enhance reading from .python-version by <a
href="https://github.com/krystof-k"><code>@​krystof-k</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/787">actions/setup-python#787</a></li>
<li>Add version parsing from Pipfile by <a
href="https://github.com/aradkdj"><code>@​aradkdj</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1067">actions/setup-python#1067</a></li>
</ul>
<h3>Bug fixes:</h3>
<ul>
<li>Clarify pythonLocation behaviour for PyPy and GraalPy in environment
variables by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1183">actions/setup-python#1183</a></li>
<li>Change missing cache directory error to warning by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1182">actions/setup-python#1182</a></li>
<li>Add Architecture-Specific PATH Management for Python with --user
Flag on Windows by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1122">actions/setup-python#1122</a></li>
<li>Include python version in PyPy python-version output by <a
href="https://github.com/cdce8p"><code>@​cdce8p</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1110">actions/setup-python#1110</a></li>
<li>Update docs: clarification on pip authentication with setup-python
by <a
href="https://github.com/priya-kinthali"><code>@​priya-kinthali</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1156">actions/setup-python#1156</a></li>
</ul>
<h3>Dependency updates:</h3>
<ul>
<li>Upgrade idna from 2.9 to 3.7 in /<strong>tests</strong>/data by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/actions/setup-python/pull/843">actions/setup-python#843</a></li>
<li>Upgrade form-data to fix critical vulnerabilities <a
href="https://redirect.github.com/actions/setup-python/issues/182">#182</a>
&amp; <a
href="https://redirect.github.com/actions/setup-python/issues/183">#183</a>
by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1163">actions/setup-python#1163</a></li>
<li>Upgrade setuptools to 78.1.1 to fix path traversal vulnerability in
PackageIndex.download by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1165">actions/setup-python#1165</a></li>
<li>Upgrade actions/checkout from 4 to 5 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/actions/setup-python/pull/1181">actions/setup-python#1181</a></li>
<li>Upgrade <code>@​actions/tool-cache</code> from 2.0.1 to 2.0.2 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/actions/setup-python/pull/1095">actions/setup-python#1095</a></li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/actions/setup-python/commit/a309ff8b426b58ec0e2a45f0f869d46889d02405"><code>a309ff8</code></a>
Bump urllib3 from 2.6.0 to 2.6.3 in /<strong>tests</strong>/data (<a
href="https://redirect.github.com/actions/setup-python/issues/1264">#1264</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/bfe8cc55a7890e3d6672eda6460ef37bfcc70755"><code>bfe8cc5</code></a>
Upgrade <a href="https://github.com/actions"><code>@​actions</code></a>
dependencies to Node 24 compatible versions (<a
href="https://redirect.github.com/actions/setup-python/issues/1259">#1259</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/4f41a90a1f38628c7ccc608d05fbafe701bc20ae"><code>4f41a90</code></a>
Bump urllib3 from 2.5.0 to 2.6.0 in /<strong>tests</strong>/data (<a
href="https://redirect.github.com/actions/setup-python/issues/1253">#1253</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/83679a892e2d95755f2dac6acb0bfd1e9ac5d548"><code>83679a8</code></a>
Bump <code>@​types/node</code> from 24.1.0 to 24.9.1 and update macos-13
to macos-15-intel ...</li>
<li><a
href="https://github.com/actions/setup-python/commit/bfc4944b43a5d84377eca3cf6ab5b7992ba61923"><code>bfc4944</code></a>
Bump prettier from 3.5.3 to 3.6.2 (<a
href="https://redirect.github.com/actions/setup-python/issues/1234">#1234</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/97aeb3efb8a852c559869050c7fb175b4efcc8cf"><code>97aeb3e</code></a>
Bump requests from 2.32.2 to 2.32.4 in /<strong>tests</strong>/data (<a
href="https://redirect.github.com/actions/setup-python/issues/1130">#1130</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/443da59188462e2402e2942686db5aa6723f4bed"><code>443da59</code></a>
Bump actions/publish-action from 0.3.0 to 0.4.0 &amp; Documentation
update for pi...</li>
<li><a
href="https://github.com/actions/setup-python/commit/cfd55ca82492758d853442341ad4d8010466803a"><code>cfd55ca</code></a>
graalpy: add graalpy early-access and windows builds (<a
href="https://redirect.github.com/actions/setup-python/issues/880">#880</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/bba65e51ff35d50c6dbaaacd8a4681db13aa7cb4"><code>bba65e5</code></a>
Bump typescript from 5.4.2 to 5.9.3 and update docs/advanced-usage.md
(<a
href="https://redirect.github.com/actions/setup-python/issues/1094">#1094</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/18566f86b301499665bd3eb1a2247e0849c64fa5"><code>18566f8</code></a>
Improve wording and &quot;fix example&quot; (remove 3.13) on testing
against pre-releas...</li>
<li>Additional commits viewable in <a
href="https://github.com/actions/setup-python/compare/v5.5.0...v6.2.0">compare
view</a></li>
</ul>
</details>
<br />

Updates `actions/labeler` from 6.0.1 to 6.1.0
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/actions/labeler/releases">actions/labeler's
releases</a>.</em></p>
<blockquote>
<h2>v6.1.0</h2>
<h2>Enhancements</h2>
<ul>
<li>Add changed-files-labels-limit and max-files-changed configuration
options to cap the number of labels added by <a
href="https://github.com/bluca"><code>@​bluca</code></a> in <a
href="https://redirect.github.com/actions/labeler/pull/923">actions/labeler#923</a></li>
</ul>
<h2>Bug Fixes</h2>
<ul>
<li>Improve Labeler Action documentation and permission error handling
by <a
href="https://github.com/chiranjib-swain"><code>@​chiranjib-swain</code></a>
in <a
href="https://redirect.github.com/actions/labeler/pull/897">actions/labeler#897</a></li>
<li>Preserve manually added labels during workflow runs and refine label
synchronization logic by <a
href="https://github.com/chiranjib-swain"><code>@​chiranjib-swain</code></a>
in <a
href="https://redirect.github.com/actions/labeler/pull/917">actions/labeler#917</a></li>
</ul>
<h2>Dependency Updates</h2>
<ul>
<li>Upgrade brace-expansion from 1.1.11 to 1.1.12 and document breaking
changes in v6 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/labeler/pull/877">actions/labeler#877</a></li>
<li>Upgrade minimatch from 10.0.1 to 10.2.3 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/labeler/pull/926">actions/labeler#926</a></li>
<li>Upgrade dependencies (<code>@​actions/core</code>,
<code>@​actions/github</code>, js-yaml, minimatch, <a
href="https://github.com/typescript-eslint"><code>@​typescript-eslint</code></a>)
by <a href="https://github.com/Copilot"><code>@​Copilot</code></a> in <a
href="https://redirect.github.com/actions/labeler/pull/934">actions/labeler#934</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a
href="https://github.com/chiranjib-swain"><code>@​chiranjib-swain</code></a>
made their first contribution in <a
href="https://redirect.github.com/actions/labeler/pull/897">actions/labeler#897</a></li>
<li><a href="https://github.com/bluca"><code>@​bluca</code></a> made
their first contribution in <a
href="https://redirect.github.com/actions/labeler/pull/923">actions/labeler#923</a></li>
<li><a href="https://github.com/Copilot"><code>@​Copilot</code></a> made
their first contribution in <a
href="https://redirect.github.com/actions/labeler/pull/934">actions/labeler#934</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/actions/labeler/compare/v6...v6.1.0">https://github.com/actions/labeler/compare/v6...v6.1.0</a></p>
</blockquote>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/actions/labeler/commit/f27b608878404679385c85cfa523b85ccb86e213"><code>f27b608</code></a>
chore: upgrade dependencies (<code>@​actions/core</code>,
<code>@​actions/github</code>, js-yaml, minimat...</li>
<li><a
href="https://github.com/actions/labeler/commit/c5dadc2a45784a4b6adfcd20fea3465da3a5f904"><code>c5dadc2</code></a>
Add 'changed-files-labels-limit' and 'max-files-changed' configs to
allow cap...</li>
<li><a
href="https://github.com/actions/labeler/commit/e52e4fb63ed5cd0e07abaad9826b2a893ccb921f"><code>e52e4fb</code></a>
Bump minimatch from 10.0.1 to 10.2.3 (<a
href="https://redirect.github.com/actions/labeler/issues/926">#926</a>)</li>
<li><a
href="https://github.com/actions/labeler/commit/77a4082b841706ac431479b7e2bb11216ffef250"><code>77a4082</code></a>
Fix: Preserve manually added labels during workflow run and refine label
sync...</li>
<li><a
href="https://github.com/actions/labeler/commit/25abb3cad4f14b7ac27968a495c37798860a5a1a"><code>25abb3c</code></a>
Improve Labeler Action Documentation and Error Handling for Permissions
(<a
href="https://redirect.github.com/actions/labeler/issues/897">#897</a>)</li>
<li><a
href="https://github.com/actions/labeler/commit/395c8cfdb1e1e691cc4bad0dd315820af8eb67fd"><code>395c8cf</code></a>
Bump brace-expansion from 1.1.11 to 1.1.12 and document breaking changes
in v...</li>
<li>See full diff in <a
href="https://github.com/actions/labeler/compare/634933edcd8ababfe52f92936142cc22ac488b1b...f27b608878404679385c85cfa523b85ccb86e213">compare
view</a></li>
</ul>
</details>
<br />


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
- `@dependabot ignore <dependency name> major version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's major version (unless you unignore this specific
dependency's major version or upgrade to it yourself)
- `@dependabot ignore <dependency name> minor version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's minor version (unless you unignore this specific
dependency's minor version or upgrade to it yourself)
- `@dependabot ignore <dependency name>` will close this group update PR
and stop Dependabot creating any more for the specific dependency
(unless you unignore this specific dependency or upgrade to it yourself)
- `@dependabot unignore <dependency name>` will remove all of the ignore
conditions of the specified dependency
- `@dependabot unignore <dependency name> <ignore condition>` will
remove the ignore condition of the specified dependency and ignore
conditions


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`7b2581e`](7b2581e16accdfe64b4fd4f2086a03c00547f600))
- [SKIP CI] [pre-commit] bump https://github.com/igorshubovych/markdownlint-cli from dd34288d0608e7b8825ee7e4e8c406e0a9780cf7 to d36813544180cf94269aa8f1fb3dc145aab76d79 (#84)

Bumps
[https://github.com/igorshubovych/markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli)
from dd34288d0608e7b8825ee7e4e8c406e0a9780cf7 to
d36813544180cf94269aa8f1fb3dc145aab76d79.
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/igorshubovych/markdownlint-cli/commit/d36813544180cf94269aa8f1fb3dc145aab76d79"><code>d368135</code></a>
Bump markdown-it from 14.1.1 to 14.2.0</li>
<li>See full diff in <a
href="https://github.com/igorshubovych/markdownlint-cli/compare/dd34288d0608e7b8825ee7e4e8c406e0a9780cf7...d36813544180cf94269aa8f1fb3dc145aab76d79">compare
view</a></li>
</ul>
</details>
<br />


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
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`6ba6e8c`](6ba6e8c5a582b748117ed281c2cf55c1e013e477))
- [SKIP CI] [GA] bump chrysa/github-actions from 1 to 1.0.12 in /.github/workflows in the community-actions group (#88)

Bumps the community-actions group in /.github/workflows with 1 update:
[chrysa/github-actions](https://github.com/chrysa/github-actions).

Updates `chrysa/github-actions` from 1 to 1.0.12
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/chrysa/github-actions/releases">chrysa/github-actions's
releases</a>.</em></p>
<blockquote>
<h2>v1.0.7</h2>
<h2>[1.0.7] - 2026-03-30</h2>
<h3>Bug Fixes</h3>
<ul>
<li>Fix(pre-commit): update hook revisions to stable tags (<a
href="https://redirect.github.com/chrysa/github-actions/issues/8">#8</a>)
(<a
href="https://github.com/chrysa/github-actions/blob/HEAD/cd2171a47b16107887a2aaad9eeed5c667716ecc"><code>cd2171a</code></a>)</li>
</ul>
<h2>v1.0.6</h2>
<h2>[1.0.6] - 2026-03-30</h2>
<h3>Miscellaneous</h3>
<ul>
<li>Chore: add gitignore, copilot-instructions, instruction files (<a
href="https://redirect.github.com/chrysa/github-actions/issues/7">#7</a>)
(<a
href="https://github.com/chrysa/github-actions/blob/HEAD/03b4d110b7787d8fe6ea60257719e3dff71c0695"><code>03b4d11</code></a>)</li>
</ul>
<h2>v1.0.5</h2>
<h2>[1.0.5] - 2026-03-30</h2>
<h3>Miscellaneous</h3>
<ul>
<li>Chore: add Copilot instructions file (<a
href="https://redirect.github.com/chrysa/github-actions/issues/5">#5</a>)</li>
</ul>
<p>Co-authored-by: anthony-greau <a
href="mailto:anthony.greau@padam.io">anthony.greau@padam.io</a> (<a
href="https://github.com/chrysa/github-actions/blob/HEAD/e4a173be84a9502e4a1174bb122fc58e96d71f03"><code>e4a173b</code></a>)</p>
<h2>v1.0.3</h2>
<h2>[1.0.3] - 2026-03-29</h2>
<h3>Documentation</h3>
<ul>
<li>Docs: add CI, release and license badges to README (<a
href="https://github.com/chrysa/github-actions/blob/HEAD/87a8f4fd2b22a51dad7fb7848de3a91b0c3db1aa"><code>87a8f4f</code></a>)</li>
</ul>
<h2>v1.0.2</h2>
<h2>[1.0.2] - 2026-03-29</h2>
<h3>Bug Fixes</h3>
<ul>
<li>Fix: fix changelog generation in release workflow (<a
href="https://github.com/chrysa/github-actions/blob/HEAD/2e857da4006e5ef45fc628cb898d578ca54415c5"><code>2e857da</code></a>)</li>
<li>Fix: reorder changelog steps - generate before tagging, use
body_path (<a
href="https://github.com/chrysa/github-actions/blob/HEAD/a70ac4561b14fd7c36b8dd44dc645df5425b4328"><code>a70ac45</code></a>)</li>
<li>Fix: replace preReleaseTag condition with tag existence check (<a
href="https://github.com/chrysa/github-actions/blob/HEAD/2d77e872591ed29b09e678dc72bbeb0e44692371"><code>2d77e87</code></a>)</li>
</ul>
<h3>Features</h3>
<ul>
<li>Feat: add gitversion action and changelog generation with git-cliff
(<a
href="https://github.com/chrysa/github-actions/blob/HEAD/81203cf92fb71cdf55fca82a7b44599747eb0552"><code>81203cf</code></a>)</li>
</ul>
<h3>Miscellaneous</h3>
<ul>
<li>Chore: add dependabot configuration for github-actions (<a
href="https://github.com/chrysa/github-actions/blob/HEAD/abf088388658a6d35e9d18402639c79e28de36ce"><code>abf0883</code></a>)</li>
</ul>
<h2>v1.0.1</h2>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/chrysa/github-actions/compare/v1.0.0...v1.0.1">https://github.com/chrysa/github-actions/compare/v1.0.0...v1.0.1</a></p>
</blockquote>
</details>
<details>
<summary>Changelog</summary>
<p><em>Sourced from <a
href="https://github.com/chrysa/github-actions/blob/v1.0.12/CHANGELOG.md">chrysa/github-actions's
changelog</a>.</em></p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/chrysa/github-actions/commit/de480e8095d98af6a7209189398073c868c4fe71"><code>de480e8</code></a>
chore: update CHANGELOG.md for v1.0.12 [skip ci]</li>
<li><a
href="https://github.com/chrysa/github-actions/commit/22b543a6da4730e4340157c90d6e2f87998fdc1d"><code>22b543a</code></a>
fix(security): prevent script injection via env vars (S7630)</li>
<li><a
href="https://github.com/chrysa/github-actions/commit/9b7a0b37dae9717378397f9fe27de6f8227b699a"><code>9b7a0b3</code></a>
chore(sonar-scan): add DEPRECATED notice — migrate to sonar-scan-python
(<a
href="https://redirect.github.com/chrysa/github-actions/issues/45">#45</a>)</li>
<li><a
href="https://github.com/chrysa/github-actions/commit/f3d0346b98679547b764e06f2797dee3c1e0e2f6"><code>f3d0346</code></a>
fix(sonar-scan): downgrade sonarqube-scan-action v8/v5 → v4.2.1 + make
sonar-...</li>
<li><a
href="https://github.com/chrysa/github-actions/commit/58dbadc527c0c75f18cf86632620707736ac7bae"><code>58dbadc</code></a>
fix(sonar-scan): make latest-python, github-token, organization,
project-name...</li>
<li><a
href="https://github.com/chrysa/github-actions/commit/aa81495f0f1523c8cfb26dcd8a7fcdf6f7c1b616"><code>aa81495</code></a>
ci: centralize sonar scanning via chrysa/github-actions/sonar-scan@v1
(<a
href="https://redirect.github.com/chrysa/github-actions/issues/41">#41</a>)</li>
<li><a
href="https://github.com/chrysa/github-actions/commit/a9ae1f4a069b3bdbeb09606270d20028c7a4d84e"><code>a9ae1f4</code></a>
fix(ci): downgrade sonarqube-scan-action v8-&gt;v4.2.1 for SonarCloud
(<a
href="https://redirect.github.com/chrysa/github-actions/issues/40">#40</a>)</li>
<li><a
href="https://github.com/chrysa/github-actions/commit/f5933fc376438c5084c5b6c2b20d9d7afec19097"><code>f5933fc</code></a>
fix(ci): add SKIP no-commit-to-branch in pre-commit step (<a
href="https://redirect.github.com/chrysa/github-actions/issues/39">#39</a>)</li>
<li><a
href="https://github.com/chrysa/github-actions/commit/4b2915227617cc040048545e2b947c9ab476b79e"><code>4b29152</code></a>
fix(ci): bump actions/checkout and setup-python to v6 (<a
href="https://redirect.github.com/chrysa/github-actions/issues/38">#38</a>)</li>
<li><a
href="https://github.com/chrysa/github-actions/commit/77aafe9badb7aab25c927830a33723e9e316cba0"><code>77aafe9</code></a>
fix(quality): add docker-test target for CI-compatible action validation
(<a
href="https://redirect.github.com/chrysa/github-actions/issues/37">#37</a>)</li>
<li>Additional commits viewable in <a
href="https://github.com/chrysa/github-actions/compare/v1...v1.0.12">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=chrysa/github-actions&package-manager=github_actions&previous-version=1&new-version=1.0.12)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

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
- `@dependabot ignore <dependency name> major version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's major version (unless you unignore this specific
dependency's major version or upgrade to it yourself)
- `@dependabot ignore <dependency name> minor version` will close this
group update PR and stop Dependabot creating any more for the specific
dependency's minor version (unless you unignore this specific
dependency's minor version or upgrade to it yourself)
- `@dependabot ignore <dependency name>` will close this group update PR
and stop Dependabot creating any more for the specific dependency
(unless you unignore this specific dependency or upgrade to it yourself)
- `@dependabot unignore <dependency name>` will remove all of the ignore
conditions of the specified dependency
- `@dependabot unignore <dependency name> <ignore condition>` will
remove the ignore condition of the specified dependency and ignore
conditions


</details>

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`4e3190c`](4e3190c4bfb9c5da28276d4a8d348eb917d5d6c2))

### Documentation

- Docs(instructions): add Python structure rules from Notion Engineering Standards (#53)

docs(instructions): add Python structure rules from Notion Engineering
Standards

- One class per file convention
- Domain-driven structure  
- No print() in production (use structlog/logging)

Source: Notion Engineering Standards 2026-05-21

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`3c44fe8`](3c44fe859049da2f20cff1f9ab41daa789132a29))

### Features

- Feat(ruff-check,run-tests): add working-directory input for monorepo support (#48)

Add optional `working-directory` input (default: `.`) to `ruff-check`
and `run-tests`.

Closes #47
Closes #46

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`eaea825`](eaea82581d279e58026f16844f34d9af0a45e3f2))
- Feat(ruff): add working-directory support to ruff-check (#47) (#73)

Closes #47 — Add working-directory parameter to ruff-check composite
action.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`64cb7e5`](64cb7e5716de34d9511f4a3a2696ead856a3b29c))
- Feat/47-ruff-check-working-directory (#76)

automated: feat/47-ruff-check-working-directory

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`46ef0ab`](46ef0ab1a09b5b5991eed272fab72e814dcc3083))

### Miscellaneous

- Chore(ci): normalize YAML formatting (indentation and quotes) ([`114f3e1`](114f3e1ff2dd27834b0cad6836af5cdeb0c09aa9))
- Chore: migrate sonar-scan to sonar-scan-python (#49)

Migrate self CI from `sonar-scan@v1` to `sonar-scan-python@v1`.

Closes #43

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`0fd7d90`](0fd7d905da3321dac4c21e770c1162f690b3ba42))
- Chore: bump actions/setup-python from 5.5.0 to 6.2.0 (#56)

Bumps [actions/setup-python](https://github.com/actions/setup-python)
from 5.5.0 to 6.2.0.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/actions/setup-python/releases">actions/setup-python's
releases</a>.</em></p>
<blockquote>
<h2>v6.2.0</h2>
<h2>What's Changed</h2>
<h3>Dependency Upgrades</h3>
<ul>
<li>Upgrade dependencies to Node 24 compatible versions by <a
href="https://github.com/salmanmkc"><code>@​salmanmkc</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1259">actions/setup-python#1259</a></li>
<li>Upgrade urllib3 from 2.5.0 to 2.6.3 in <code>/__tests__/data</code>
by <a href="https://github.com/dependabot"><code>@​dependabot</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1253">actions/setup-python#1253</a>
and <a
href="https://redirect.github.com/actions/setup-python/pull/1264">actions/setup-python#1264</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/actions/setup-python/compare/v6...v6.2.0">https://github.com/actions/setup-python/compare/v6...v6.2.0</a></p>
<h2>v6.1.0</h2>
<h2>What's Changed</h2>
<h3>Enhancements:</h3>
<ul>
<li>Add support for <code>pip-install</code> input by <a
href="https://github.com/gowridurgad"><code>@​gowridurgad</code></a> in
<a
href="https://redirect.github.com/actions/setup-python/pull/1201">actions/setup-python#1201</a></li>
<li>Add graalpy early-access and windows builds by <a
href="https://github.com/timfel"><code>@​timfel</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/880">actions/setup-python#880</a></li>
</ul>
<h3>Dependency and Documentation updates:</h3>
<ul>
<li>Enhanced wording and updated example usage for
<code>allow-prereleases</code> by <a
href="https://github.com/yarikoptic"><code>@​yarikoptic</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/979">actions/setup-python#979</a></li>
<li>Upgrade urllib3 from 1.26.19 to 2.5.0 and document breaking changes
in v6 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1139">actions/setup-python#1139</a></li>
<li>Upgrade typescript from 5.4.2 to 5.9.3 and Documentation update by
<a href="https://github.com/dependabot"><code>@​dependabot</code></a> in
<a
href="https://redirect.github.com/actions/setup-python/pull/1094">actions/setup-python#1094</a></li>
<li>Upgrade actions/publish-action from 0.3.0 to 0.4.0 &amp;
Documentation update for pip-install input by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1199">actions/setup-python#1199</a></li>
<li>Upgrade requests from 2.32.2 to 2.32.4 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1130">actions/setup-python#1130</a></li>
<li>Upgrade prettier from 3.5.3 to 3.6.2 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1234">actions/setup-python#1234</a></li>
<li>Upgrade <code>@​types/node</code> from 24.1.0 to 24.9.1 and update
macos-13 to macos-15-intel by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1235">actions/setup-python#1235</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a
href="https://github.com/yarikoptic"><code>@​yarikoptic</code></a> made
their first contribution in <a
href="https://redirect.github.com/actions/setup-python/pull/979">actions/setup-python#979</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/actions/setup-python/compare/v6...v6.1.0">https://github.com/actions/setup-python/compare/v6...v6.1.0</a></p>
<h2>v6.0.0</h2>
<h2>What's Changed</h2>
<h3>Breaking Changes</h3>
<ul>
<li>Upgrade to node 24 by <a
href="https://github.com/salmanmkc"><code>@​salmanmkc</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1164">actions/setup-python#1164</a></li>
</ul>
<p>Make sure your runner is on version v2.327.1 or later to ensure
compatibility with this release. <a
href="https://github.com/actions/runner/releases/tag/v2.327.1">See
Release Notes</a></p>
<h3>Enhancements:</h3>
<ul>
<li>Add support for <code>pip-version</code> by <a
href="https://github.com/priyagupta108"><code>@​priyagupta108</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1129">actions/setup-python#1129</a></li>
<li>Enhance reading from .python-version by <a
href="https://github.com/krystof-k"><code>@​krystof-k</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/787">actions/setup-python#787</a></li>
<li>Add version parsing from Pipfile by <a
href="https://github.com/aradkdj"><code>@​aradkdj</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1067">actions/setup-python#1067</a></li>
</ul>
<h3>Bug fixes:</h3>
<ul>
<li>Clarify pythonLocation behaviour for PyPy and GraalPy in environment
variables by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1183">actions/setup-python#1183</a></li>
<li>Change missing cache directory error to warning by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1182">actions/setup-python#1182</a></li>
<li>Add Architecture-Specific PATH Management for Python with --user
Flag on Windows by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1122">actions/setup-python#1122</a></li>
<li>Include python version in PyPy python-version output by <a
href="https://github.com/cdce8p"><code>@​cdce8p</code></a> in <a
href="https://redirect.github.com/actions/setup-python/pull/1110">actions/setup-python#1110</a></li>
<li>Update docs: clarification on pip authentication with setup-python
by <a
href="https://github.com/priya-kinthali"><code>@​priya-kinthali</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1156">actions/setup-python#1156</a></li>
</ul>
<h3>Dependency updates:</h3>
<ul>
<li>Upgrade idna from 2.9 to 3.7 in /<strong>tests</strong>/data by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/actions/setup-python/pull/843">actions/setup-python#843</a></li>
<li>Upgrade form-data to fix critical vulnerabilities <a
href="https://redirect.github.com/actions/setup-python/issues/182">#182</a>
&amp; <a
href="https://redirect.github.com/actions/setup-python/issues/183">#183</a>
by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1163">actions/setup-python#1163</a></li>
<li>Upgrade setuptools to 78.1.1 to fix path traversal vulnerability in
PackageIndex.download by <a
href="https://github.com/aparnajyothi-y"><code>@​aparnajyothi-y</code></a>
in <a
href="https://redirect.github.com/actions/setup-python/pull/1165">actions/setup-python#1165</a></li>
<li>Upgrade actions/checkout from 4 to 5 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/actions/setup-python/pull/1181">actions/setup-python#1181</a></li>
<li>Upgrade <code>@​actions/tool-cache</code> from 2.0.1 to 2.0.2 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/actions/setup-python/pull/1095">actions/setup-python#1095</a></li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/actions/setup-python/commit/a309ff8b426b58ec0e2a45f0f869d46889d02405"><code>a309ff8</code></a>
Bump urllib3 from 2.6.0 to 2.6.3 in /<strong>tests</strong>/data (<a
href="https://redirect.github.com/actions/setup-python/issues/1264">#1264</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/bfe8cc55a7890e3d6672eda6460ef37bfcc70755"><code>bfe8cc5</code></a>
Upgrade <a href="https://github.com/actions"><code>@​actions</code></a>
dependencies to Node 24 compatible versions (<a
href="https://redirect.github.com/actions/setup-python/issues/1259">#1259</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/4f41a90a1f38628c7ccc608d05fbafe701bc20ae"><code>4f41a90</code></a>
Bump urllib3 from 2.5.0 to 2.6.0 in /<strong>tests</strong>/data (<a
href="https://redirect.github.com/actions/setup-python/issues/1253">#1253</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/83679a892e2d95755f2dac6acb0bfd1e9ac5d548"><code>83679a8</code></a>
Bump <code>@​types/node</code> from 24.1.0 to 24.9.1 and update macos-13
to macos-15-intel ...</li>
<li><a
href="https://github.com/actions/setup-python/commit/bfc4944b43a5d84377eca3cf6ab5b7992ba61923"><code>bfc4944</code></a>
Bump prettier from 3.5.3 to 3.6.2 (<a
href="https://redirect.github.com/actions/setup-python/issues/1234">#1234</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/97aeb3efb8a852c559869050c7fb175b4efcc8cf"><code>97aeb3e</code></a>
Bump requests from 2.32.2 to 2.32.4 in /<strong>tests</strong>/data (<a
href="https://redirect.github.com/actions/setup-python/issues/1130">#1130</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/443da59188462e2402e2942686db5aa6723f4bed"><code>443da59</code></a>
Bump actions/publish-action from 0.3.0 to 0.4.0 &amp; Documentation
update for pi...</li>
<li><a
href="https://github.com/actions/setup-python/commit/cfd55ca82492758d853442341ad4d8010466803a"><code>cfd55ca</code></a>
graalpy: add graalpy early-access and windows builds (<a
href="https://redirect.github.com/actions/setup-python/issues/880">#880</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/bba65e51ff35d50c6dbaaacd8a4681db13aa7cb4"><code>bba65e5</code></a>
Bump typescript from 5.4.2 to 5.9.3 and update docs/advanced-usage.md
(<a
href="https://redirect.github.com/actions/setup-python/issues/1094">#1094</a>)</li>
<li><a
href="https://github.com/actions/setup-python/commit/18566f86b301499665bd3eb1a2247e0849c64fa5"><code>18566f8</code></a>
Improve wording and &quot;fix example&quot; (remove 3.13) on testing
against pre-releas...</li>
<li>Additional commits viewable in <a
href="https://github.com/actions/setup-python/compare/v5.5.0...v6.2.0">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=actions/setup-python&package-manager=github_actions&previous-version=5.5.0&new-version=6.2.0)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

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
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`215f7e8`](215f7e87feadb2a2fb1979c2c40719fcdec02f73))
- Chore: bump raven-actions/actionlint from 2.0.1 to 2.1.2 (#57)

Bumps
[raven-actions/actionlint](https://github.com/raven-actions/actionlint)
from 2.0.1 to 2.1.2.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/raven-actions/actionlint/releases">raven-actions/actionlint's
releases</a>.</em></p>
<blockquote>
<h2>v2.1.2</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>docs: fix make link to code of conduct absolute <a
href="https://github.com/avishj"><code>@​avishj</code></a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/55">#55</a>)</li>
<li>fix: use legacy peer dependencies to resolve installation failures
<a
href="https://github.com/jessehouwing"><code>@​jessehouwing</code></a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/57">#57</a>)</li>
</ul>
<h2>👥 Contributors</h2>
<p><a href="https://github.com/avishj"><code>@​avishj</code></a> and <a
href="https://github.com/jessehouwing"><code>@​jessehouwing</code></a></p>
<p>See details of all code changes: <a
href="https://github.com/raven-actions/actionlint/compare/v2.1.1...v2.1.2">https://github.com/raven-actions/actionlint/compare/v2.1.1...v2.1.2</a>
since previous release.</p>
<h2>v2.1.1</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>ci(deps): bump actions/cache from 5.0.2 to 5.0.3 in the all group
@<a href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/53">#53</a>)</li>
<li>fix: pin installed version of <code>@​actions/tool-cache</code> <a
href="https://github.com/hghmn"><code>@​hghmn</code></a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/52">#52</a>)</li>
<li>ci(deps): bump the all group across 1 directory with 2 updates @<a
href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/50">#50</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/47">#47</a>)</li>
<li>ci(deps): bump actions/cache from 4.3.0 to 5.0.1 in the all group
@<a href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/48">#48</a>)</li>
</ul>
<h2>👥 Contributors</h2>
<p><a
href="https://github.com/DariuszPorowski"><code>@​DariuszPorowski</code></a>,
<a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot],
<a href="https://github.com/hghmn"><code>@​hghmn</code></a>, <a
href="https://github.com/raven-actions-sync"><code>@​raven-actions-sync</code></a>[bot],
<a href="https://github.com/apps/dependabot">dependabot[bot]</a> and <a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a></p>
<p>See details of all code changes: <a
href="https://github.com/raven-actions/actionlint/compare/v2.1.0...v2.1.1">https://github.com/raven-actions/actionlint/compare/v2.1.0...v2.1.1</a>
since previous release.</p>
<h2>v2.1.0</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>update action versions in workflows and action metadata <a
href="https://github.com/DariuszPorowski"><code>@​DariuszPorowski</code></a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/46">#46</a>)</li>
</ul>
<h2>👥 Contributors</h2>
<p><a
href="https://github.com/DariuszPorowski"><code>@​DariuszPorowski</code></a></p>
<p>See details of all code changes: <a
href="https://github.com/raven-actions/actionlint/compare/v2.0.2...v2.1.0">https://github.com/raven-actions/actionlint/compare/v2.0.2...v2.1.0</a>
since previous release.</p>
<h2>v2.0.2</h2>
<h2>🔄️ What's Changed</h2>
<ul>
<li>ci(deps): bump actions/checkout from 5 to 6 in the all group @<a
href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/45">#45</a>)</li>
<li>fix: don't interfere with repo package.json <a
href="https://github.com/allejo"><code>@​allejo</code></a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/43">#43</a>)</li>
<li>ci(deps): bump actions/cache from 4.2.4 to 4.3.0 in the all group
@<a href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/42">#42</a>)</li>
<li>ci(deps): bump actions/github-script from 7.0.1 to 8.0.0 in the all
group @<a href="https://github.com/apps/dependabot">dependabot[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/41">#41</a>)</li>
<li>ci(deps): bump the all group across 1 directory with 2 updates @<a
href="https://github.com/apps/dependabot">dependabot[bot]</a> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/40">#40</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/38">#38</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/37">#37</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/36">#36</a>)</li>
<li>chore: synced file(s) with raven-actions/.workflows @<a
href="https://github.com/apps/raven-actions-sync">raven-actions-sync[bot]</a>
(<a
href="https://redirect.github.com/raven-actions/actionlint/issues/35">#35</a>)</li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/raven-actions/actionlint/commit/205b530c5d9fa8f44ae9ed59f341a0db994aa6f8"><code>205b530</code></a>
docs: fix make link to code of conduct absolute (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/55">#55</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/59a077201b1103d536cdbb901e0a56106f08970b"><code>59a0772</code></a>
fix: use legacy peer dependencies to resolve installation failures (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/57">#57</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/e01d1ea33dd6a5ed517d95b4c0c357560ac6f518"><code>e01d1ea</code></a>
chore: add permissions for publish-release job</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/3459946ddcf59c1fb7e850824461df3f55d6133a"><code>3459946</code></a>
ci(deps): bump actions/cache from 5.0.2 to 5.0.3 in the all group (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/53">#53</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/855a9ad92ebcccac55c8f3605ab46bcc588575f8"><code>855a9ad</code></a>
chore: add new URL to .lycheeignore</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/0277f3a759d600efd96680ce7286c7fb071293ec"><code>0277f3a</code></a>
fix: update permissions in release-draft workflow</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/06dd51c3fc6da21d49078939b3d1607b0edebdf4"><code>06dd51c</code></a>
fix: pin installed version of <code>@​actions/tool-cache</code> (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/52">#52</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/6fc528e1e3b665b61cde1ca6fc4dc37fd139fa74"><code>6fc528e</code></a>
ci(deps): bump the all group across 1 directory with 2 updates (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/50">#50</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/6e8b85b8060c21661deacadf48389d0b2c896ea3"><code>6e8b85b</code></a>
chore: synced file(s) with raven-actions/.workflows (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/47">#47</a>)</li>
<li><a
href="https://github.com/raven-actions/actionlint/commit/580b34edf3f0039a5691481c6081049971ecd530"><code>580b34e</code></a>
ci(deps): bump actions/cache from 4.3.0 to 5.0.1 in the all group (<a
href="https://redirect.github.com/raven-actions/actionlint/issues/48">#48</a>)</li>
<li>Additional commits viewable in <a
href="https://github.com/raven-actions/actionlint/compare/3a24062651993d40fed1019b58ac6fbdfbf276cc...205b530c5d9fa8f44ae9ed59f341a0db994aa6f8">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=raven-actions/actionlint&package-manager=github_actions&previous-version=2.0.1&new-version=2.1.2)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

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
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`f4880ba`](f4880ba29c6bea7c153164d9031083c0cfe9f9f9))
- Chore: bump SonarSource/sonarqube-scan-action from 5 to 8 (#58)

Bumps
[SonarSource/sonarqube-scan-action](https://github.com/sonarsource/sonarqube-scan-action)
from 5 to 8.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/sonarsource/sonarqube-scan-action/releases">SonarSource/sonarqube-scan-action's
releases</a>.</em></p>
<blockquote>
<h2>v8.0.0</h2>
<h2>What's Changed</h2>
<h3>Breaking change</h3>
<ul>
<li>SQSCANGHA-145 Set skipSignatureVerification default value to false
by <a
href="https://github.com/antoine-vinot-sonarsource"><code>@​antoine-vinot-sonarsource</code></a>
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/241">SonarSource/sonarqube-scan-action#241</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/SonarSource/sonarqube-scan-action/compare/v7...v8.0.0">https://github.com/SonarSource/sonarqube-scan-action/compare/v7...v8.0.0</a></p>
<h2>v7.2.1</h2>
<h2>What's Changed</h2>
<ul>
<li>SQSCANGHA-140 Set skipSignatureVerification default value to true to
avoid breaking change by <a
href="https://github.com/gmmcal"><code>@​gmmcal</code></a> in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/240">SonarSource/sonarqube-scan-action#240</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/SonarSource/sonarqube-scan-action/compare/v7...v7.2.1">https://github.com/SonarSource/sonarqube-scan-action/compare/v7...v7.2.1</a></p>
<h2>v7.2.0</h2>
<h2>What's Changed</h2>
<ul>
<li>SQSCANGHA-133 Upgrade the Node version used in UTs + contribution
guide by <a
href="https://github.com/claire-villard-sonarsource"><code>@​claire-villard-sonarsource</code></a>
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/226">SonarSource/sonarqube-scan-action#226</a></li>
<li>SC-45750 Migrate to dateless license headers by <a
href="https://github.com/claire-villard-sonarsource"><code>@​claire-villard-sonarsource</code></a>
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/229">SonarSource/sonarqube-scan-action#229</a></li>
<li>SQSCANGHA-134 Upgrade the libraries to latest version by <a
href="https://github.com/claire-villard-sonarsource"><code>@​claire-villard-sonarsource</code></a>
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/227">SonarSource/sonarqube-scan-action#227</a></li>
<li>SQSCANGHA-138 Update dist and add ci test by <a
href="https://github.com/antoine-vinot-sonarsource"><code>@​antoine-vinot-sonarsource</code></a>
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/233">SonarSource/sonarqube-scan-action#233</a></li>
<li>SQSCANGHA-140 Add OpenPGP signature verification for scanner
downloads by <a
href="https://github.com/claire-villard-sonarsource"><code>@​claire-villard-sonarsource</code></a>
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/235">SonarSource/sonarqube-scan-action#235</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/SonarSource/sonarqube-scan-action/compare/v7...v7.2.0">https://github.com/SonarSource/sonarqube-scan-action/compare/v7...v7.2.0</a></p>
<h2>v7.1.0</h2>
<h2>What's Changed</h2>
<ul>
<li>SQSCANGHA-128 NO-JIRA Bump actions/cache from 4 to 5 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/219">SonarSource/sonarqube-scan-action#219</a></li>
<li>SQSCANGHA-130 Bump rollup from 4.50.1 to 4.59.0 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/221">SonarSource/sonarqube-scan-action#221</a></li>
<li>SQSCANGHA-131 Bump picomatch from 4.0.3 to 4.0.4 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/223">SonarSource/sonarqube-scan-action#223</a></li>
<li>SQSCANGHA-132 Upgrade Node to 24 by <a
href="https://github.com/claire-villard-sonarsource"><code>@​claire-villard-sonarsource</code></a>
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/224">SonarSource/sonarqube-scan-action#224</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/SonarSource/sonarqube-scan-action/compare/v7...v7.1.0">https://github.com/SonarSource/sonarqube-scan-action/compare/v7...v7.1.0</a></p>
<h2>v7.0.0</h2>
<h2>What's Changed</h2>
<ul>
<li>SQSCANGHA-120 NO-JIRA Bump actions/setup-node from 4 to 5 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/211">SonarSource/sonarqube-scan-action#211</a></li>
<li>Update SonarScanner CLI to 7.3.0.5189 by <a
href="https://github.com/github-actions"><code>@​github-actions</code></a>[bot]
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/212">SonarSource/sonarqube-scan-action#212</a></li>
<li>SQSCANGHA-122 Include caveats for running SCA by <a
href="https://github.com/subdavis"><code>@​subdavis</code></a> in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/213">SonarSource/sonarqube-scan-action#213</a></li>
<li>SQSCANGHA-123 NO-JIRA Bump actions/setup-node from 5 to 6 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/214">SonarSource/sonarqube-scan-action#214</a></li>
<li>SQSCANGHA-126 Update SonarScanner CLI to 8.0.1.6346 by <a
href="https://github.com/github-actions"><code>@​github-actions</code></a>[bot]
in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/218">SonarSource/sonarqube-scan-action#218</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a href="https://github.com/subdavis"><code>@​subdavis</code></a>
made their first contribution in <a
href="https://redirect.github.com/SonarSource/sonarqube-scan-action/pull/213">SonarSource/sonarqube-scan-action#213</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/SonarSource/sonarqube-scan-action/compare/v6.0.0...v7.0.0">https://github.com/SonarSource/sonarqube-scan-action/compare/v6.0.0...v7.0.0</a></p>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/7006c4492b2e0ee0f816d36501671557c97f5995"><code>7006c44</code></a>
Update SonarScanner CLI to 8.1.0.6389</li>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/edd319f2842a3d04654c967f40ba916b155c6256"><code>edd319f</code></a>
NO-JIRA Bump actions/setup-node from 6.3.0 to 6.4.0 (<a
href="https://redirect.github.com/sonarsource/sonarqube-scan-action/issues/234">#234</a>)</li>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/e050aa9e699112ca0664dd2a5c694ddab05dc555"><code>e050aa9</code></a>
NO-JIRA Bump actions/cache from 5.0.4 to 5.0.5 (<a
href="https://redirect.github.com/sonarsource/sonarqube-scan-action/issues/231">#231</a>)</li>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/6cd3d8f2ae5f9cd14e3c3c52b535e26e211f3051"><code>6cd3d8f</code></a>
NO-JIRA Bump madhead/semver-utils from 4.3.0 to 5.0.0</li>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/56568530eddcb15ab65e7880af318fba5b859e2e"><code>5656853</code></a>
SQSCANGHA-146 Add proxy support for GPG keyserver access (<a
href="https://redirect.github.com/sonarsource/sonarqube-scan-action/issues/244">#244</a>)</li>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/c4447538999e984fe7463a8068a88b784ed06988"><code>c444753</code></a>
SQSCANGHA-140 Add the missing requirements in README.md (<a
href="https://redirect.github.com/sonarsource/sonarqube-scan-action/issues/243">#243</a>)</li>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/59db25f34e16620e48ab4bb9e4a5dce155cb5432"><code>59db25f</code></a>
SQSCANGHA-145 Set skipSignatureVerification default value to false (<a
href="https://redirect.github.com/sonarsource/sonarqube-scan-action/issues/241">#241</a>)</li>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/ca30b65f4ea9f033b8a6fc0ffc9816a562d13f55"><code>ca30b65</code></a>
SQSCANGHA-143 SubmitReview: Use Vault token (<a
href="https://redirect.github.com/sonarsource/sonarqube-scan-action/issues/238">#238</a>)</li>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/c7ee0f9df90b7aa20e8dcf9695dcfe2e7da5b4f2"><code>c7ee0f9</code></a>
SQSCANGHA-140 Set skipSignatureVerification default value to true to
avoid br...</li>
<li><a
href="https://github.com/SonarSource/sonarqube-scan-action/commit/55e44800a8f495208cce6e4e82f5dedb45fcf0ef"><code>55e4480</code></a>
SQSCANGHA-140 Add OpenPGP signature verification for scanner downloads
(<a
href="https://redirect.github.com/sonarsource/sonarqube-scan-action/issues/235">#235</a>)</li>
<li>Additional commits viewable in <a
href="https://github.com/sonarsource/sonarqube-scan-action/compare/v5...v8">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=SonarSource/sonarqube-scan-action&package-manager=github_actions&previous-version=5&new-version=8)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

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
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`80bf90e`](80bf90e8679e6f75368276523dcca6f57bdd6a71))
- Chore: bump peter-evans/create-pull-request from 7.0.6 to 8.1.1 (#55)

Bumps
[peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request)
from 7.0.6 to 8.1.1.
<details>
<summary>Release notes</summary>
<p><em>Sourced from <a
href="https://github.com/peter-evans/create-pull-request/releases">peter-evans/create-pull-request's
releases</a>.</em></p>
<blockquote>
<h2>Create Pull Request v8.1.1</h2>
<h2>What's Changed</h2>
<ul>
<li>build(deps-dev): bump the npm group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4305">peter-evans/create-pull-request#4305</a></li>
<li>build(deps): bump minimatch by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4311">peter-evans/create-pull-request#4311</a></li>
<li>build(deps): bump the github-actions group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4316">peter-evans/create-pull-request#4316</a></li>
<li>build(deps): bump <code>@​tootallnate/once</code> and
jest-environment-jsdom by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4323">peter-evans/create-pull-request#4323</a></li>
<li>build(deps-dev): bump undici from 6.23.0 to 6.24.0 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4328">peter-evans/create-pull-request#4328</a></li>
<li>build(deps-dev): bump flatted from 3.3.1 to 3.4.2 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4334">peter-evans/create-pull-request#4334</a></li>
<li>build(deps): bump picomatch by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4339">peter-evans/create-pull-request#4339</a></li>
<li>build(deps-dev): bump handlebars from 4.7.8 to 4.7.9 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4344">peter-evans/create-pull-request#4344</a></li>
<li>build(deps-dev): bump the npm group with 3 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4349">peter-evans/create-pull-request#4349</a></li>
<li>fix: retry post-creation API calls on 422 eventual consistency
errors by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4356">peter-evans/create-pull-request#4356</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/peter-evans/create-pull-request/compare/v8.1.0...v8.1.1">https://github.com/peter-evans/create-pull-request/compare/v8.1.0...v8.1.1</a></p>
<h2>Create Pull Request v8.1.0</h2>
<h2>What's Changed</h2>
<ul>
<li>README.md: bump given GitHub actions to their latest versions by <a
href="https://github.com/deining"><code>@​deining</code></a> in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4265">peter-evans/create-pull-request#4265</a></li>
<li>build(deps): bump the github-actions group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4273">peter-evans/create-pull-request#4273</a></li>
<li>build(deps-dev): bump the npm group with 2 updates by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4274">peter-evans/create-pull-request#4274</a></li>
<li>build(deps-dev): bump undici from 6.22.0 to 6.23.0 by <a
href="https://github.com/dependabot"><code>@​dependabot</code></a>[bot]
in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4284">peter-evans/create-pull-request#4284</a></li>
<li>Update distribution by <a
href="https://github.com/actions-bot"><code>@​actions-bot</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4289">peter-evans/create-pull-request#4289</a></li>
<li>fix: Handle remote prune failures gracefully on self-hosted runners
by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4295">peter-evans/create-pull-request#4295</a></li>
<li>feat: add <code>@​octokit/plugin-retry</code> to handle retriable
server errors by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4298">peter-evans/create-pull-request#4298</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a href="https://github.com/deining"><code>@​deining</code></a> made
their first contribution in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4265">peter-evans/create-pull-request#4265</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/peter-evans/create-pull-request/compare/v8.0.0...v8.1.0">https://github.com/peter-evans/create-pull-request/compare/v8.0.0...v8.1.0</a></p>
<h2>Create Pull Request v8.0.0</h2>
<h2>What's new in v8</h2>
<ul>
<li>Requires <a
href="https://github.com/actions/runner/releases/tag/v2.327.1">Actions
Runner v2.327.1</a> or later if you are using a self-hosted runner for
Node 24 support.</li>
</ul>
<h2>What's Changed</h2>
<ul>
<li>chore: Update checkout action version to v6 by <a
href="https://github.com/yonas"><code>@​yonas</code></a> in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4258">peter-evans/create-pull-request#4258</a></li>
<li>Update actions/checkout references to <a
href="https://github.com/v6"><code>@​v6</code></a> in docs by <a
href="https://github.com/Copilot"><code>@​Copilot</code></a> in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4259">peter-evans/create-pull-request#4259</a></li>
<li>feat: v8 by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4260">peter-evans/create-pull-request#4260</a></li>
</ul>
<h2>New Contributors</h2>
<ul>
<li><a href="https://github.com/yonas"><code>@​yonas</code></a> made
their first contribution in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4258">peter-evans/create-pull-request#4258</a></li>
<li><a href="https://github.com/Copilot"><code>@​Copilot</code></a> made
their first contribution in <a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4259">peter-evans/create-pull-request#4259</a></li>
</ul>
<p><strong>Full Changelog</strong>: <a
href="https://github.com/peter-evans/create-pull-request/compare/v7.0.11...v8.0.0">https://github.com/peter-evans/create-pull-request/compare/v7.0.11...v8.0.0</a></p>
<h2>Create Pull Request v7.0.11</h2>
<h2>What's Changed</h2>
<ul>
<li>fix: restrict remote prune to self-hosted runners by <a
href="https://github.com/peter-evans"><code>@​peter-evans</code></a> in
<a
href="https://redirect.github.com/peter-evans/create-pull-request/pull/4250">peter-evans/create-pull-request#4250</a></li>
</ul>
<!-- raw HTML omitted -->
</blockquote>
<p>... (truncated)</p>
</details>
<details>
<summary>Commits</summary>
<ul>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/5f6978faf089d4d20b00c7766989d076bb2fc7f1"><code>5f6978f</code></a>
fix: retry post-creation API calls on 422 eventual consistency errors
(<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4356">#4356</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/d32e88dac789dcc7906e7d26f69f24116fa9c97d"><code>d32e88d</code></a>
build(deps-dev): bump the npm group with 3 updates (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4349">#4349</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/8170bccad11c0df62542c04dcaefe36d342dfd39"><code>8170bcc</code></a>
build(deps-dev): bump handlebars from 4.7.8 to 4.7.9 (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4344">#4344</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/00418193b417f888dbf1d993c5c0d31d27fdc7de"><code>0041819</code></a>
build(deps): bump picomatch (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4339">#4339</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/b993918c8536b6d44706130734d5456879762b27"><code>b993918</code></a>
build(deps-dev): bump flatted from 3.3.1 to 3.4.2 (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4334">#4334</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/36d7c8468b48f9c2f8f29e260e82f10d4b90d2bd"><code>36d7c84</code></a>
build(deps-dev): bump undici from 6.23.0 to 6.24.0 (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4328">#4328</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/a45d1fb447fcaf601166e405fd4f335cde1a8aa8"><code>a45d1fb</code></a>
build(deps): bump <code>@​tootallnate/once</code> and
jest-environment-jsdom (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4323">#4323</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/3499eb61835cc0015c0b786e203d74b1e8f55e43"><code>3499eb6</code></a>
build(deps): bump the github-actions group with 2 updates (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4316">#4316</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/3f3b473b8c148f5a7520efb4d1f9a70eea3d9d1f"><code>3f3b473</code></a>
build(deps): bump minimatch (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4311">#4311</a>)</li>
<li><a
href="https://github.com/peter-evans/create-pull-request/commit/6699836a213cf8b28c4f0408a404a6ac79d4458a"><code>6699836</code></a>
build(deps-dev): bump the npm group with 2 updates (<a
href="https://redirect.github.com/peter-evans/create-pull-request/issues/4305">#4305</a>)</li>
<li>Additional commits viewable in <a
href="https://github.com/peter-evans/create-pull-request/compare/67ccf781d68cd99b580ae25a5c18a1cc84ffff1f...5f6978faf089d4d20b00c7766989d076bb2fc7f1">compare
view</a></li>
</ul>
</details>
<br />


[![Dependabot compatibility
score](https://dependabot-badges.githubapp.com/badges/compatibility_score?dependency-name=peter-evans/create-pull-request&package-manager=github_actions&previous-version=7.0.6&new-version=8.1.1)](https://docs.github.com/en/github/managing-security-vulnerabilities/about-dependabot-security-updates#about-compatibility-scores)

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
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`19845bc`](19845bc157576e8615f7c612cb6c93b365b6c3ad))
- Chore(pre-commit): bump pre-commit-tools to v0.1.1-76, add regression-gate hook (#65)

## Summary

- Bump `pre-commit-tools` rev `v0.1.1-73` → `v0.1.1-76`
- Add `regression-gate` hook (pre-push stage) introduced in `v0.1.1-76`

## Changes

``.pre-commit-config.yaml``: rev bump + regression-gate entry

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`5acaca6`](5acaca6d291cf1bf4abca4cb6e5a51f0629c510d))
- Chore(pre-commit): bump pre-commit-tools to v0.1.1-76, add regression-gate hook (#63)

- Bump `pre-commit-tools` rev `v0.1.1-73` → `v0.1.1-76`
- Add `regression-gate` hook at pre-push stage

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`e473267`](e473267be1e8c4a35ef257ba63a8ee173e57e2c4))
- Chore(pre-commit): bump pre-commit-tools to v0.1.1-76, add regression-gate hook (#66)

- Bump `pre-commit-tools` rev → `v0.1.1-76`
- Add `regression-gate` hook at pre-push stage

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`76e6fee`](76e6feef532bd7567a50b15b520956d8e73284b7))
- Chore(ci): bump pre-commit-tools to v0.1.1-76 and migrate setup-python (#67)

- Bump pre-commit-tools to v0.1.1-76 (adds regression-gate hook)
- Migrate `actions/setup-python` to chrysa composite action
`python-setup`

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`069aa9e`](069aa9ebb5e884800c151636fd5592abc31ea762))
- Chore(ci): upgrade GitHub Actions to latest versions (#69)

Upgrades outdated GitHub Actions to latest versions.

Part of ecosystem-wide standards compliance.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`b102732`](b102732397fdc197f0530544ed15b570af3d90ac))
- Ci: extend run-tests composite with cov-fail-under input (#68)

Adds optional `cov-fail-under` input to `run-tests` action. When set,
appends `--cov-fail-under=N` to the pytest invocation.

Depends on: T13 migration across chrysa repos.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`ddfcac4`](ddfcac4cb1c813d7fefe1fea85b03d4c28f0fb98))
- Chore: standards compliance, dependabot groups, pre-commit updates (#70)

## Summary
- Standards compliance files (CODEOWNERS, sonar, dependabot, cliff,
pre-commit)
- Dependabot: add groups and throttling to limit open PRs
- Remove pip cache from composite-actions repo, fix sonar tests path
- Fix pre-commit issues, trim copilot-instructions

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`ec5ccb5`](ec5ccb58c5faa583ec1b21bd6e93b39246cdeb46))
- Chore(ci): upgrade GitHub Actions to latest versions (#71)

## Summary

Upgrade GitHub Actions to latest stable versions:

- `actions/checkout` v5 → **v6**
- `actions/setup-python` v5 → **v6**
- `actions/setup-node` v4 → **v6**
- `actions/upload-artifact` v4 → **v7**
- `actions/download-artifact` v4 → **v8**

Part of ecosystem-wide standards compliance audit.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`5524c19`](5524c198702e34abb1af1bd7bc09ce23029f408e))
- Chore(deps): bump pre-commit-tools to v0.1.1 (#76) (#74)

Bump chrysa/pre-commit-tools to v0.1.1 across all composite actions.

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`191f074`](191f0749b72884f756cbcd2b08e0eedfef0a7d11))
- Chore/bump-pre-commit-tools-v0.1.1-76 (#75)

automated: chore/bump-pre-commit-tools-v0.1.1-76

---------

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`6961d16`](6961d1602d96295119272fd0576078fd7f5fc32e))
- Chore(standards) (#78)

Add missing chrysa pre-commit hooks from standards audit. Brings the
repo into full compliance with the shared standards baseline.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`3ec7c73`](3ec7c732a7532e3574929000b3882682ad98a1f1))
- Chore(pre-commit): add missing chrysa hooks from standards audit (#82)

Part of ecosystem-wide standards audit. Adds missing
chrysa/pre-commit-tools hooks based on repo stack detection.

Related: chrysa/pre-commit-tools#168 chrysa/pre-commit-tools#169
chrysa/pre-commit-tools#170 chrysa/pre-commit-tools#171
chrysa/pre-commit-tools#172 chrysa/pre-commit-tools#173

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`cbaa55e`](cbaa55eb79c04fe1889576e1293c906570579505))
- Chore(pre-commit): update pre-commit-tools to v0.1.1-92 ([`9518da1`](9518da11c28ebe57faf9c2e1e59f7ea02d03d3cd))
- Chore(ui-ux): reference ui-ux skill in CLAUDE.md (#92)

Reference the ui-ux skill in CLAUDE.md.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`ef0f18e`](ef0f18e037727452678203697d23fb7ba5d81f90))
- Ci(actions): fix checkout@v4 and upload-artifact@v4 across all workflows (#94)

Fix invalid action versions causing CI failures.

Co-authored-by: chrysa <greau.anthony+chrysa@gmail.com> ([`9ef6cb7`](9ef6cb7c65258340e9a2f447de75bc4d777fbdce))

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


