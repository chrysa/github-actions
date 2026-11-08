"""Unit tests for the commit-hygiene check (pure functions and entrypoint, no network)."""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from commit_hygiene import check

ASSISTANT = re.compile(check.DEFAULT_ASSISTANT_PATTERN, flags=re.IGNORECASE)
ALLOWED = re.compile(r"@users\.noreply\.github\.com$", flags=re.IGNORECASE)
OWNER = "owner@users.noreply.github.com"
OUTSIDER = "someone@example.org"


def commit(
    *, sha: str = "a" * 40, message: str = "feat: x\n", author: str = OWNER, committer: str = OWNER
) -> dict:
    return {
        "sha": sha,
        "commit": {"message": message, "author": {"email": author}, "committer": {"email": committer}},
    }


def rules(findings: list[check.Finding]) -> list[str]:
    return [finding.rule for finding in findings]


def test_clean_commit_has_no_finding() -> None:
    findings = check.find_violations(commits=[commit()], assistant=ASSISTANT, allowed=ALLOWED)

    assert findings == [], f"expected no finding, got {findings}"


@pytest.mark.parametrize(
    ("line", "rule"),
    [
        ("Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>", "assistant-co-author"),
        ("co-authored-by: Copilot <copilot@example.org>", "assistant-co-author"),
        ("🤖 Generated with [Claude Code](https://claude.com/claude-code)", "generated-with"),
        ("Claude-Session: https://claude.ai/code/session_x", "session-link"),
    ],
)
def test_assistant_attribution_is_flagged(line: str, rule: str) -> None:
    message = f"fix: y\n\nbody\n\n{line}\n"

    findings = check.find_violations(commits=[commit(message=message)], assistant=ASSISTANT, allowed=None)

    assert rules(findings) == [rule], f"expected [{rule}] for {line!r}, got {rules(findings)}"


@pytest.mark.parametrize(
    "line",
    [
        "Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>",
        "Co-authored-by: owner <owner@users.noreply.github.com>",
        "docs: explain how the claude hook runs first",
        "Generated with make docs",
        "X-Request-Session: 1234",
    ],
)
def test_legitimate_lines_are_not_flagged(line: str) -> None:
    findings = check.trailer_findings(sha="abc1234", message=f"m\n\n{line}\n", assistant=ASSISTANT)

    assert findings == [], f"expected no finding for {line!r}, got {findings}"


def test_identity_check_is_off_without_a_pattern() -> None:
    findings = check.find_violations(
        commits=[commit(author=OUTSIDER, committer=OUTSIDER)], assistant=ASSISTANT, allowed=None
    )

    assert findings == [], f"identity check must be opt-in, got {findings}"


def test_foreign_author_committer_and_co_author_are_flagged() -> None:
    message = f"feat: x\n\nCo-authored-by: Someone <{OUTSIDER}>\n"

    findings = check.find_violations(
        commits=[commit(message=message, author=OUTSIDER, committer=OUTSIDER)],
        assistant=ASSISTANT,
        allowed=ALLOWED,
    )

    assert rules(findings) == ["author-identity", "committer-identity", "co-author-identity"], (
        f"expected the three identity findings, got {rules(findings)}"
    )


def test_github_web_flow_committer_is_accepted() -> None:
    findings = check.find_violations(
        commits=[commit(committer=check.GITHUB_WEB_FLOW_EMAIL)], assistant=ASSISTANT, allowed=ALLOWED
    )

    assert findings == [], f"the web-flow committer is GitHub itself, got {findings}"


def test_findings_never_print_an_email() -> None:
    message = f"feat: x\n\nCo-authored-by: Someone <{OUTSIDER}>\n"
    findings = check.find_violations(
        commits=[commit(message=message, author=OUTSIDER)], assistant=ASSISTANT, allowed=ALLOWED
    )

    rendered = "\n".join(check.annotate(finding=finding, level="warning") for finding in findings)

    assert OUTSIDER not in rendered, f"an email leaked into the annotations: {rendered}"


def test_annotation_escapes_untrusted_text() -> None:
    finding = check.Finding(
        sha="abc1234", rule="generated-with", detail="Generated with claude %0A::error::x"
    )

    rendered = check.annotate(finding=finding, level="warning")

    assert "%250A" in rendered, f"a literal %0A must be escaped, got {rendered}"
    assert rendered.count("\n") == 0, f"the annotation must stay on one line, got {rendered!r}"


def test_missing_fields_do_not_crash() -> None:
    findings = check.find_violations(
        commits=[{"sha": "b" * 40, "commit": {"message": None, "author": None, "committer": {}}}],
        assistant=ASSISTANT,
        allowed=ALLOWED,
    )

    assert rules(findings) == ["author-identity", "committer-identity"], (
        f"expected identity findings for empty emails, got {rules(findings)}"
    )


def write_commits(*, tmp_path: pathlib.Path, commits: list[dict]) -> pathlib.Path:
    path = tmp_path / "commits.jsonl"
    path.write_text("".join(json.dumps(item) + "\n" for item in commits), encoding="utf-8")
    return path


@pytest.mark.parametrize("case", [("info", 0, "warning"), ("error", 1, "error")], ids=["info", "error"])
def test_main_exit_code_follows_the_mode(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    case: tuple[str, int, str],
) -> None:
    mode, expected_code, level = case
    dirty = commit(message="fix: y\n\nCo-authored-by: Claude <noreply@anthropic.com>\n")
    monkeypatch.setenv("COMMITS_FILE", str(write_commits(tmp_path=tmp_path, commits=[dirty])))
    monkeypatch.setenv("MODE", mode)
    monkeypatch.delenv("ALLOWED_EMAIL_PATTERN", raising=False)
    monkeypatch.delenv("ASSISTANT_PATTERN", raising=False)

    code = check.main()

    output = capsys.readouterr().out
    assert code == expected_code, f"mode {mode}: expected exit {expected_code}, got {code}"
    assert f"::{level} title=Commit hygiene (assistant-co-author)::" in output, output


def test_main_passes_on_a_clean_pull_request(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("COMMITS_FILE", str(write_commits(tmp_path=tmp_path, commits=[commit()])))
    monkeypatch.setenv("MODE", "error")
    monkeypatch.setenv("ALLOWED_EMAIL_PATTERN", ALLOWED.pattern)

    code = check.main()

    assert code == 0, f"a clean pull request must pass, got exit {code}"
    assert "1 commit(s) checked, 0 finding(s)" in capsys.readouterr().out


def test_main_rejects_an_unknown_mode(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("COMMITS_FILE", str(write_commits(tmp_path=tmp_path, commits=[])))
    monkeypatch.setenv("MODE", "strict")

    code = check.main()

    assert code == 2, f"an unknown mode is a configuration error, got exit {code}"
    assert "MODE must be one of" in capsys.readouterr().out
