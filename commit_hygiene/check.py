"""Check the commits of a pull request for assistant attribution and foreign identities.

GitHub appends the squashed commits' authors and ``Co-authored-by`` trailers to every
squash-merge commit, whatever the repository's squash-message setting, so these must be
caught on the branch commits before merge (shared-standards ``SCM.md`` SC-016).

Environment (set by the ``check-commit-hygiene`` action):

- ``COMMITS_FILE``: JSON lines, one GitHub API commit object per line.
- ``MODE``: ``info`` (annotate, never fail; default) or ``error`` (fail on any finding).
- ``ASSISTANT_PATTERN``: regex naming assistants in trailers (default: ``DEFAULT_ASSISTANT_PATTERN``).
- ``ALLOWED_EMAIL_PATTERN``: optional regex; when set, every author, committer and
  co-author email must match it. Unset or empty disables the identity check.

Findings never print an email address: CI logs are public on public repositories.
"""

from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import re
import sys

from notion_sync.logging_setup import configure, get_logger

DEFAULT_ASSISTANT_PATTERN = (
    r"anthropic\.com|\bclaude\b|\bcopilot\b|openai\.com|\bcodex\b|\bgemini\b|\bcursor\b"
)
GITHUB_WEB_FLOW_EMAIL = "noreply@github.com"
MODES = ("info", "error")
DEFAULT_MODE = "info"
SHA_SHORT_LEN = 7
CO_AUTHOR_RE = re.compile(r"^\s*co-authored-by:\s*(?P<value>.*)$", re.IGNORECASE)
EMAIL_IN_TRAILER_RE = re.compile(r"<(?P<email>[^>]+)>")
GENERATED_WITH_RE = re.compile(r"^\W*generated with\b(?P<value>.*)$", re.IGNORECASE)
SESSION_LINK_RE = re.compile(r"^\s*[\w-]+-session:\s*\S+", re.IGNORECASE)

logger = get_logger(__name__)


@dataclasses.dataclass(frozen=True)
class Finding:
    """One rule broken by one commit."""

    sha: str
    rule: str
    detail: str


def trailer_findings(*, sha: str, message: str, assistant: re.Pattern[str]) -> list[Finding]:
    """Return the assistant-attribution lines of a commit message."""
    findings = []
    for line in message.splitlines():
        co_author = CO_AUTHOR_RE.match(line)
        generated = GENERATED_WITH_RE.match(line)
        if co_author and assistant.search(co_author.group("value")):
            findings.append(Finding(sha=sha, rule="assistant-co-author", detail=line.strip()))
        elif generated and assistant.search(generated.group("value")):
            findings.append(Finding(sha=sha, rule="generated-with", detail=line.strip()))
        elif SESSION_LINK_RE.match(line) and assistant.search(line):
            findings.append(Finding(sha=sha, rule="session-link", detail=line.split(":", 1)[0].strip()))
    return findings


def identity_findings(*, sha: str, commit: dict, allowed: re.Pattern[str]) -> list[Finding]:
    """Return the identities of a commit that fall outside the allowed set (emails withheld)."""
    findings = []
    author_email = (commit.get("author") or {}).get("email") or ""
    committer_email = (commit.get("committer") or {}).get("email") or ""
    if not allowed.search(author_email):
        findings.append(
            Finding(sha=sha, rule="author-identity", detail="author email not in the allowed set")
        )
    if committer_email != GITHUB_WEB_FLOW_EMAIL and not allowed.search(committer_email):
        findings.append(
            Finding(sha=sha, rule="committer-identity", detail="committer email not in the allowed set")
        )
    for line in (commit.get("message") or "").splitlines():
        co_author = CO_AUTHOR_RE.match(line)
        email = EMAIL_IN_TRAILER_RE.search(co_author.group("value")) if co_author else None
        if email and not allowed.search(email.group("email")):
            findings.append(
                Finding(sha=sha, rule="co-author-identity", detail="co-author email not in the allowed set")
            )
    return findings


def find_violations(
    *, commits: list[dict], assistant: re.Pattern[str], allowed: re.Pattern[str] | None
) -> list[Finding]:
    """Return every finding over the pull request's commits, in commit order."""
    findings = []
    for item in commits:
        sha = item.get("sha", "")[:SHA_SHORT_LEN]
        commit = item.get("commit") or {}
        findings.extend(trailer_findings(sha=sha, message=commit.get("message") or "", assistant=assistant))
        if allowed is not None:
            findings.extend(identity_findings(sha=sha, commit=commit, allowed=allowed))
    return findings


def load_commits(*, path: pathlib.Path) -> list[dict]:
    """Read JSON-lines commit objects as written by ``gh api --paginate --jq '.[]'``."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def escape_data(*, text: str) -> str:
    """Escape untrusted text (commit messages) for a workflow-command message."""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def annotate(*, finding: Finding, level: str) -> str:
    """Render one finding as a GitHub Actions workflow command."""
    message = escape_data(text=f"{finding.sha}: {finding.detail}")
    return f"::{level} title=Commit hygiene ({finding.rule})::{message}"


def main() -> int:
    """Run the check from the action's environment; return the process exit code."""
    configure()
    mode = os.environ.get("MODE", DEFAULT_MODE) or DEFAULT_MODE
    if mode not in MODES:
        logger.info(f"::error::MODE must be one of {', '.join(MODES)}, got '{mode}'")
        return 2
    assistant = re.compile(
        os.environ.get("ASSISTANT_PATTERN") or DEFAULT_ASSISTANT_PATTERN, flags=re.IGNORECASE
    )
    allowed_raw = os.environ.get("ALLOWED_EMAIL_PATTERN", "")
    allowed = re.compile(allowed_raw, flags=re.IGNORECASE) if allowed_raw else None
    commits = load_commits(path=pathlib.Path(os.environ["COMMITS_FILE"]))
    findings = find_violations(commits=commits, assistant=assistant, allowed=allowed)
    level = "error" if mode == "error" else "warning"
    for finding in findings:
        logger.info(annotate(finding=finding, level=level))
    logger.info(f"Commit hygiene: {len(commits)} commit(s) checked, {len(findings)} finding(s), mode {mode}.")
    if findings:
        logger.info("Clean the branch before merge: recreate its own commits with an allowed identity and")
        logger.info(
            "without the trailers (shared-standards SCM.md SC-016). GitHub copies them into the squash."
        )
    return 1 if findings and mode == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
