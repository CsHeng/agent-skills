#!/usr/bin/env python3
"""Validate activation contracts and authored provider metadata."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

VALID_ACTIVATION_MODES = {
    "native",
    "conditional",
    "composition",
    "explicit",
    "baseline",
}
VALID_DEFAULT_ROLES = {"primary", "overlay", "evaluator"}
EXPECTED_CODEX_POLICY = {
    "native": True,
    "conditional": True,
    "composition": False,
    "explicit": False,
    "baseline": True,
}
CLAUDE_DEFAULT_VISIBILITY = "default-visible"


def activation_modes(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    modes = contract.get("activation_modes")
    if not isinstance(modes, dict):
        return {}
    return {
        str(mode): entry for mode, entry in modes.items() if isinstance(entry, dict)
    }


def codex_allows_implicit(contract: dict[str, Any], mode: str) -> bool:
    entry = activation_modes(contract).get(mode)
    if entry is None:
        raise ValueError(f"unknown activation mode: {mode}")
    value = entry.get("codex_allow_implicit_invocation")
    if not isinstance(value, bool):
        raise ValueError(
            f"activation mode {mode} lacks codex_allow_implicit_invocation"
        )
    return value


def derived_implicit_invocation(
    contract: dict[str, Any], entry: dict[str, Any]
) -> bool:
    mode = entry.get("activation_mode")
    if not isinstance(mode, str):
        raise ValueError("skill entry lacks activation_mode")
    return codex_allows_implicit(contract, mode)


def codex_invocation_policy(text: str) -> bool | None:
    """Read one boolean from the metadata's block-style policy mapping."""
    lines = text.splitlines()
    policy_starts = [index for index, line in enumerate(lines) if line == "policy:"]
    if len(policy_starts) != 1:
        return None
    values: list[str] = []
    for line in lines[policy_starts[0] + 1 :]:
        if line and not line[0].isspace() and not line.startswith("#"):
            break
        if line.strip().startswith("allow_implicit_invocation:"):
            match = re.fullmatch(
                r"  allow_implicit_invocation:\s*(true|false)\s*(?:#.*)?", line
            )
            if match is None:
                return None
            values.append(match[1])
    if values == ["true"]:
        return True
    if values == ["false"]:
        return False
    return None


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def validate_activation_contract(
    contract: dict[str, Any],
    repo_root: Path,
    *,
    check_sources: bool,
) -> list[str]:
    errors: list[str] = []
    modes = activation_modes(contract)
    missing_modes = sorted(VALID_ACTIVATION_MODES - set(modes))
    extra_modes = sorted(set(modes) - VALID_ACTIVATION_MODES)
    if missing_modes:
        errors.append("activation_modes missing: " + ", ".join(missing_modes))
    if extra_modes:
        errors.append("activation_modes unsupported: " + ", ".join(extra_modes))
    for mode in sorted(VALID_ACTIVATION_MODES & set(modes)):
        configured = modes[mode].get("codex_allow_implicit_invocation")
        expected = EXPECTED_CODEX_POLICY[mode]
        if configured is not expected:
            errors.append(
                f"activation_modes.{mode}.codex_allow_implicit_invocation "
                f"must be {expected!r}"
            )
        if modes[mode].get("claude_effective_visibility") != CLAUDE_DEFAULT_VISIBILITY:
            errors.append(
                f"activation_modes.{mode}.claude_effective_visibility must be "
                f"{CLAUDE_DEFAULT_VISIBILITY!r}"
            )

    skills = contract.get("skills")
    if not isinstance(skills, dict):
        return [*errors, "skill contract must contain [skills.*] entries"]
    for skill_name, raw_entry in sorted(skills.items()):
        if not isinstance(raw_entry, dict):
            errors.append(f"{skill_name}: skill entry must be a table")
            continue
        entry = raw_entry
        mode = entry.get("activation_mode")
        role = entry.get("default_role")
        if "implicit_invocation" in entry:
            errors.append(
                f"{skill_name}: authored implicit_invocation is forbidden; derive it from activation_mode"
            )
        if mode is None:
            errors.append(f"{skill_name}: missing activation_mode")
        elif not isinstance(mode, str) or mode not in VALID_ACTIVATION_MODES:
            errors.append(f"{skill_name}: invalid activation_mode: {mode}")
        if role is None:
            errors.append(f"{skill_name}: missing default_role")
        elif not isinstance(role, str) or role not in VALID_DEFAULT_ROLES:
            errors.append(f"{skill_name}: invalid default_role: {role}")
        if mode == "baseline" and role != "overlay":
            errors.append(
                f"{skill_name}: baseline activation requires default_role=overlay"
            )
        if not check_sources:
            continue
        skill_dir = repo_root / "skills" / skill_name
        skill_path = skill_dir / "SKILL.md"
        try:
            skill_text = skill_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{skill_name}: cannot read SKILL.md: {exc}")
            continue
        frontmatter = _frontmatter(skill_text)
        if frontmatter.get("name") != skill_name:
            errors.append(f"{skill_name}: frontmatter name must match the Skill ID")
        if not frontmatter.get("description"):
            errors.append(f"{skill_name}: frontmatter requires a non-empty description")
        if frontmatter.get("disable-model-invocation", "").lower() == "true":
            errors.append(
                f"{skill_name}: unsupported shared frontmatter disable-model-invocation: true"
            )
        metadata_path = skill_dir / "agents" / "openai.yaml"
        try:
            metadata_text = metadata_path.read_text(encoding="utf-8")
        except OSError:
            metadata_text = ""
        if not isinstance(mode, str) or mode not in VALID_ACTIVATION_MODES:
            continue
        expected = EXPECTED_CODEX_POLICY[mode]
        if codex_invocation_policy(metadata_text) is not expected:
            errors.append(
                f"{skill_name}: Codex invocation policy must match activation_mode "
                f"{mode}: allow_implicit_invocation: {str(expected).lower()}"
            )

    return errors
