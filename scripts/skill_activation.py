#!/usr/bin/env python3
"""Shared activation-contract and provider-projection helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


VALID_ACTIVATION_MODES = {
    "native",
    "conditional",
    "controller",
    "explicit",
    "baseline",
}
VALID_DEFAULT_ROLES = {"primary", "overlay", "evaluator"}
EXPECTED_CODEX_PROJECTION = {
    "native": True,
    "conditional": True,
    "controller": False,
    "explicit": False,
    "baseline": True,
}
CLAUDE_DEFAULT_VISIBILITY = "default-visible"


def activation_modes(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    modes = contract.get("activation_modes")
    if not isinstance(modes, dict):
        return {}
    return {
        str(mode): entry
        for mode, entry in modes.items()
        if isinstance(entry, dict)
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


def effective_provider_state(
    contract: dict[str, Any], entry: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    return {
        "codex": {
            "allow_implicit_invocation": derived_implicit_invocation(
                contract, entry
            ),
            "source": "activation-mode-projection",
        },
        "claude": {
            "model_visibility": CLAUDE_DEFAULT_VISIBILITY,
            "source": "shared-frontmatter-default",
        },
    }


def _top_level_policy_bounds(lines: list[str]) -> tuple[int, int] | None:
    for index, line in enumerate(lines):
        if line == "policy:":
            end = index + 1
            while end < len(lines):
                candidate = lines[end]
                if candidate and not candidate[0].isspace():
                    break
                end += 1
            return index, end
    return None


def has_authored_codex_invocation_policy(text: str) -> bool:
    lines = text.splitlines()
    bounds = _top_level_policy_bounds(lines)
    if bounds is None:
        return False
    start, end = bounds
    return any(
        line.strip().startswith("allow_implicit_invocation:")
        for line in lines[start + 1 : end]
    )


def project_openai_metadata(text: str, allow_implicit: bool) -> str:
    """Return provider metadata with one deterministic derived policy value."""
    lines = text.splitlines()
    policy_line = (
        "  allow_implicit_invocation: true"
        if allow_implicit
        else "  allow_implicit_invocation: false"
    )
    bounds = _top_level_policy_bounds(lines)
    if bounds is None:
        if lines and lines[-1] == "":
            lines.pop()
        lines.extend(["policy:", policy_line])
        return "\n".join(lines) + "\n"

    start, end = bounds
    retained_children = [
        line
        for line in lines[start + 1 : end]
        if not line.strip().startswith("allow_implicit_invocation:")
    ]
    while retained_children and retained_children[-1] == "":
        retained_children.pop()
    replacement = ["policy:", policy_line, *retained_children]
    return "\n".join([*lines[:start], *replacement, *lines[end:]]) + "\n"


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
        expected = EXPECTED_CODEX_PROJECTION[mode]
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
        elif mode not in VALID_ACTIVATION_MODES:
            errors.append(f"{skill_name}: invalid activation_mode: {mode}")
        if role is None:
            errors.append(f"{skill_name}: missing default_role")
        elif role not in VALID_DEFAULT_ROLES:
            errors.append(f"{skill_name}: invalid default_role: {role}")
        if mode == "baseline" and role != "overlay":
            errors.append(f"{skill_name}: baseline activation requires default_role=overlay")

        if not check_sources:
            continue
        skill_dir = repo_root / "skills" / skill_name
        skill_path = skill_dir / "SKILL.md"
        try:
            skill_text = skill_path.read_text(encoding="utf-8")
        except OSError:
            skill_text = ""
        if _frontmatter(skill_text).get("disable-model-invocation", "").lower() == "true":
            errors.append(
                f"{skill_name}: unsupported shared frontmatter disable-model-invocation: true"
            )
        metadata_path = skill_dir / "agents" / "openai.yaml"
        try:
            metadata_text = metadata_path.read_text(encoding="utf-8")
        except OSError:
            metadata_text = ""
        expected_metadata = project_openai_metadata(
            metadata_text, derived_implicit_invocation(contract, entry)
        )
        if metadata_text != expected_metadata:
            errors.append(
                f"{skill_name}: Codex invocation projection is stale"
            )

    return errors
