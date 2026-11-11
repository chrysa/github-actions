# Sonar scan security migration

The four shared Sonar composites now use SonarSource/sonarqube-scan-action
v8.3.0, pinned to `d209202bc7d53ff1cc128f7f907dac145c9d6ae9`, matching
the repository's own Sonar workflow. This replaces v4.2.1 and the floating v5 tag.

## Security and compatibility

- [GHSA-f79p-9c5r-xg88 / CVE-2025-58178](https://github.com/SonarSource/sonarqube-scan-action/security/advisories/GHSA-f79p-9c5r-xg88):
  command injection through untrusted arguments; affects >=4 through 5.3.0.
- [GHSA-5xq9-5g24-4g6f / CVE-2025-59844](https://github.com/SonarSource/sonarqube-scan-action/security/advisories/GHSA-5xq9-5g24-4g6f):
  affects >=4 and <6 under the advisory's Windows/untrusted-args conditions.
- [v6 migration](https://github.com/SonarSource/sonarqube-scan-action/releases/tag/v6.0.0):
  args no longer use full Bash syntax. Quote the whole property when it contains
  spaces, for example `"-Dsonar.projectName=My Project"`.
- [v8.3.0 source](https://github.com/SonarSource/sonarqube-scan-action/tree/d209202bc7d53ff1cc128f7f907dac145c9d6ae9):
  uses Node 24 and defaults to scanner 8.1.0.6389. Self-hosted runners must
  support Node 24 actions and have gpg/dirmngr for signature verification.
  Validate scanner/server compatibility before rollout.

The composites retain their input contracts and token environment variables.
Their callers determine effective permissions, events and runner selection.
Do not pass untrusted PR content into scanner configuration or run untrusted
code with privileged tokens. No token or permission expansion is needed by
this change. Presence of an affected version does not establish exploitation.

## Validation and rollout

Local validation: 25 existing action-definition pytest cases passed; eight
argument-parsing cases passed using upstream string-argv 0.3.2 across all four
composites (project names with spaces and literal shell-expression text).
These checks do not run a real authenticated scan or prove fork isolation.

Before publishing the corrected shared-action release, run representative
Python and Node/GAS scans, verify coverage/report ingestion and Quality Gate,
and exercise PR and push events. Check fork PRs without exposing real secrets.
Test Windows if any consumer uses it. Verify the runner runtime, network/proxy,
signature tooling and Sonar server compatibility on self-hosted runners.

After the PR is merged, publish a new release through the normal release
workflow, then update consumer references to that release. Existing immutable
consumer tags are not repaired by merging this PR. Start with a canary consumer;
do not retag an existing release.

## Rollback

Do not blindly revert to v4.2.1 or v5: that restores an affected version.
No earlier corrected SHA has been functionally qualified as a rollback target
for these composites. Retain a tested >=6 SHA as fallback after canary testing.
If a scan must be suspended while repairing compatibility, require owner
approval and keep the missing security check visible; never report it as passed.

Tracking: [issue #351](https://github.com/chrysa/github-actions/issues/351).
