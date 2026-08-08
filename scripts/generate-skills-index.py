#!/usr/bin/env python3
"""Generate a deterministic skill inventory from contracts/skills.toml."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from skill_activation import (
    derived_implicit_invocation,
    effective_provider_state,
)

CONTRACT_PATH = REPO_ROOT / "contracts" / "skills.toml"
INDEX_PATH = REPO_ROOT / "skills.index.json"


def load_contract() -> dict[str, Any]:
    with CONTRACT_PATH.open("rb") as handle:
        return tomllib.load(handle)


def load_manifest() -> dict[str, Any]:
    data = load_contract()
    skills = data.get("skills")
    if not isinstance(skills, dict):
        raise SystemExit("contracts/skills.toml must contain [skills.*] entries")
    return skills


def transitive_requirements(
    public_id: str, adjacency: dict[str, list[str]]
) -> list[str]:
    visited: set[str] = set()
    stack = list(reversed(adjacency.get(public_id, [])))
    while stack:
        target = stack.pop()
        if target in visited:
            continue
        visited.add(target)
        stack.extend(reversed(adjacency.get(target, [])))
    visited.discard(public_id)
    return sorted(visited)


def trigger_case_index(
    manifest: dict[str, Any],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    owned: dict[str, list[str]] = {
        entry["public_id"]: [] for entry in manifest.values()
    }
    overlaid: dict[str, list[str]] = {
        entry["public_id"]: [] for entry in manifest.values()
    }
    routing_entries = [
        entry for entry in manifest.values() if entry.get("routing_contract")
    ]
    if len(routing_entries) != 1:
        raise SystemExit("exactly one skill must declare routing_contract")
    routing_entry = routing_entries[0]
    routing_path = (
        REPO_ROOT / routing_entry["source"] / routing_entry["routing_contract"]
    )
    with routing_path.open("rb") as handle:
        routing = tomllib.load(handle)
    for trigger_case in routing.get("trigger_cases", []):
        case_id = trigger_case["id"]
        owner = trigger_case["owner"]
        owned[owner].append(case_id)
        for overlay in trigger_case.get("overlays", []):
            overlaid[overlay].append(case_id)
    return owned, overlaid


def build_index() -> dict[str, Any]:
    contract = load_contract()
    manifest = contract.get("skills")
    if not isinstance(manifest, dict):
        raise SystemExit("contracts/skills.toml must contain [skills.*] entries")
    adjacency = {
        entry["public_id"]: list(entry.get("semantic_requires", []))
        for entry in manifest.values()
    }
    owned_cases, overlay_cases = trigger_case_index(manifest)
    skills = []
    for skill_name, entry in sorted(manifest.items()):
        public_id = entry["public_id"]
        record = {
            "id": skill_name,
            "source": entry["source"],
            "public_id": public_id,
            "category": entry["category"],
            "install": entry.get("install", []),
            "lifecycle_owner": entry.get("lifecycle_owner", False),
            "activation_mode": entry["activation_mode"],
            "default_role": entry["default_role"],
            "implicit_invocation": derived_implicit_invocation(contract, entry),
            "effective_provider_state": effective_provider_state(contract, entry),
            "owned_trigger_cases": sorted(owned_cases[public_id]),
            "overlay_trigger_cases": sorted(overlay_cases[public_id]),
            "may_mutate_repo": entry.get("may_mutate_repo", False),
            "semantic_requires": adjacency[public_id],
            "semantic_transitive_requires": transitive_requirements(
                public_id, adjacency
            ),
        }
        if "runtime_contract" in entry:
            record["runtime_contract"] = entry["runtime_contract"]
        if "routing_contract" in entry:
            record["routing_contract"] = entry["routing_contract"]
        if "runtime_bundle" in entry:
            record["runtime_bundle"] = entry["runtime_bundle"]
        if "superseded_by" in entry:
            record["superseded_by"] = entry["superseded_by"]
        skills.append(record)

    profiles: dict[str, Any] = {}
    declared_profiles = contract.get("profiles", {})
    if not isinstance(declared_profiles, dict):
        raise SystemExit("contracts/skills.toml profiles must be tables")
    public_ids = sorted(adjacency)
    for profile_name, profile in sorted(declared_profiles.items()):
        if not isinstance(profile, dict) or profile.get("selection") != "all-public":
            raise SystemExit(f"unsupported profile selection: {profile_name}")
        selected = public_ids
        selected_set = set(selected)
        closure_complete = all(
            set(transitive_requirements(public_id, adjacency)) <= selected_set
            for public_id in selected
        )
        profiles[profile_name] = {
            "selection": "all-public",
            "skills": selected,
            "semantic_closure_complete": closure_complete,
        }

    semantic_install = contract.get("semantic_install")
    if not isinstance(semantic_install, dict):
        raise SystemExit("contracts/skills.toml must contain [semantic_install]")
    command_retirement = contract.get("command_retirement")
    if not isinstance(command_retirement, dict):
        raise SystemExit("contracts/skills.toml must contain [command_retirement]")
    return {
        "command_retirement": command_retirement,
        "generated_from": "contracts/skills.toml",
        "semantic_install": semantic_install,
        "profiles": profiles,
        "skills": skills,
    }


def formatted_index() -> str:
    return json.dumps(build_index(), indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if skills.index.json is stale")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    rendered = formatted_index()
    if args.check:
        if not INDEX_PATH.is_file():
            print("skills.index.json is missing", file=sys.stderr)
            return 1
        current = INDEX_PATH.read_text(encoding="utf-8")
        if current != rendered:
            print("skills.index.json is stale; run scripts/generate-skills-index.py", file=sys.stderr)
            return 1
        return 0
    INDEX_PATH.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
