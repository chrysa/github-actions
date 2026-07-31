"""Every composite action definition in this repo must be valid and runnable."""

from __future__ import annotations

import pathlib

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ACTION_FILES = sorted(REPO_ROOT.glob("*/action.yml"))


def test_repo_exposes_action_definitions() -> None:
    assert ACTION_FILES, "no */action.yml found — the actions repo cannot be empty"


@pytest.mark.parametrize("action_file", ACTION_FILES, ids=lambda path: path.parent.name)
def test_action_definition_is_valid(action_file: pathlib.Path) -> None:
    definition = yaml.safe_load(action_file.read_text(encoding="utf-8"))

    assert isinstance(definition, dict), f"{action_file} is not a YAML mapping"
    assert definition.get("name"), f"{action_file} has no name"
    assert definition.get("description"), f"{action_file} has no description"
    assert "runs" in definition, f"{action_file} has no runs section"
