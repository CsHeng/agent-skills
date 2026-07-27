#!/usr/bin/env python3
"""Validate static workflow and invocation fixtures against contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures"
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def assert_equal(actual: Any, expected: Any, label: str, errors: list[str]) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def check_mode_fixture(name: str, modes: dict[str, Any], errors: list[str]) -> None:
    fixture = load_json(FIXTURE_DIR / f"{name}.json")
    golden = load_json(GOLDEN_DIR / f"{name}.expected.json")
    mode_name = fixture["expected_mode"]
    mode = modes.get(mode_name)
    if not mode:
        errors.append(f"{name}: missing workflow mode {mode_name}")
        return
    assert_equal(mode_name, golden["mode"], f"{name}.mode", errors)
    for key, expected in golden.items():
        if key == "mode":
            continue
        assert_equal(mode.get(key), expected, f"{name}.{key}", errors)


def check_smart_commit_fixture(skills: dict[str, Any], errors: list[str]) -> None:
    golden = load_json(GOLDEN_DIR / "implicit-smart-commit-request.expected.json")
    skill = skills.get("smart-commit")
    if not skill:
        errors.append("implicit-smart-commit-request: missing smart-commit contract")
        return
    for key, expected in golden.items():
        assert_equal(skill.get(key), expected, f"smart-commit.{key}", errors)


def main() -> int:
    errors: list[str] = []
    modes = load_toml(REPO_ROOT / "contracts" / "workflow-modes.toml")["modes"]
    skills = load_toml(REPO_ROOT / "contracts" / "skills.toml")["skills"]
    for name in ("read-only-request", "micro-doc-change", "regulated-infra-change"):
        check_mode_fixture(name, modes, errors)
    check_smart_commit_fixture(skills, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("fixtures ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
