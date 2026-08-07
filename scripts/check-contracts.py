#!/usr/bin/env python3
"""Validate skill manifest, structured sources, and generated inventory."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "contracts" / "skills.toml"
INDEX_PATH = REPO_ROOT / "skills.index.json"
VALID_CATEGORIES = {
    "workflow",
    "session",
    "discipline",
    "policy",
    "tool",
    "manual-tool",
    "review-component",
    "internal",
}
EXTERNAL_TARGETS = {"claude", "codex"}
VALID_WORKFLOW_ROLES = {"controller", "gate", "evaluator", "policy", "oracle", "support"}
RUNTIME_BUNDLES = {"harness": REPO_ROOT / "src/runtime/harness"}
EXPECTED_RUNTIME_OWNERS = {
    "close-change",
    "design-change",
    "implement-change",
    "plan-change",
    "review-change",
    "sync-truth",
}


def validate_distribution_contract(repo_root: Path = REPO_ROOT) -> list[str]:
    target_path = repo_root / "contracts" / "install-targets.toml"
    try:
        with target_path.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [f"invalid install target contract: {exc}"]

    distribution = data.get("distribution")
    targets = data.get("targets")
    if not isinstance(distribution, dict):
        return ["install target contract must contain [distribution]"]
    if not isinstance(targets, dict):
        return ["install target contract must contain [targets.*] entries"]

    errors: list[str] = []
    expected = {
        "provider_plugin_targets": ["claude", "codex"],
        "shared_payload_target": "root-flat",
        "long_tail_cli": "npx skills@latest",
        "long_tail_policy": "advisory",
        "long_tail_owner": "consumer",
        "enforce_destinations": False,
        "detect_duplicates": False,
        "coexistence_guaranteed": False,
        "public_name_prefix": "",
    }
    for field, expected_value in expected.items():
        if distribution.get(field) != expected_value:
            errors.append(
                f"distribution.{field} must be {expected_value!r}; "
                f"found {distribution.get(field)!r}"
            )
    unexpected_fields = sorted(set(distribution) - set(expected))
    if unexpected_fields:
        errors.append(
            "distribution contract contains unsupported enforcement fields: "
            + ", ".join(unexpected_fields)
        )

    required_targets = {"claude", "codex", "root-flat"}
    missing_targets = sorted(required_targets - set(targets))
    if missing_targets:
        errors.append(
            "install target contract is missing retained targets: "
            + ", ".join(missing_targets)
        )
    for target_name in required_targets:
        target = targets.get(target_name)
        if (
            isinstance(target, dict)
            and target.get("include_internal_runtime_support") is not False
        ):
            errors.append(
                f"targets.{target_name}.include_internal_runtime_support must be false"
            )
    return errors


def validate_semantic_contracts(
    contract: dict[str, Any], repo_root: Path = REPO_ROOT
) -> list[str]:
    skills = contract.get("skills")
    if not isinstance(skills, dict):
        return ["skill contract must contain [skills.*] entries"]

    errors: list[str] = []
    public_entries = {
        entry.get("public_id"): entry
        for entry in skills.values()
        if isinstance(entry, dict) and isinstance(entry.get("public_id"), str)
    }
    adjacency: dict[str, set[str]] = {
        public_id: set() for public_id in public_entries
    }

    for skill_name, entry in sorted(skills.items()):
        public_id = entry.get("public_id")
        requirements = entry.get("semantic_requires", [])
        if not isinstance(public_id, str):
            continue
        if not isinstance(requirements, list) or not all(
            isinstance(target, str) and target for target in requirements
        ):
            errors.append(
                f"{skill_name}: semantic_requires must be an array of non-empty strings"
            )
            continue
        if len(requirements) != len(set(requirements)):
            errors.append(f"{skill_name}: semantic_requires contains duplicates")
        for target in requirements:
            if target == public_id:
                errors.append(f"{skill_name}: semantic_requires cannot reference itself")
            elif target not in public_entries:
                errors.append(
                    f"{skill_name}: semantic_requires references unknown skill: {target}"
                )
            else:
                adjacency[public_id].add(target)
        if entry.get("category") == "review-component" and requirements:
            errors.append(
                f"{skill_name}: review-component evaluators cannot invoke semantic dependencies"
            )
        if "use-coding-skills" in requirements:
            errors.append(
                f"{skill_name}: public skills cannot depend on the optional session router"
            )

    cycle = _runtime_contract_cycle(adjacency)
    if cycle:
        errors.append(
            "semantic dependency graph contains a cycle: " + " -> ".join(cycle)
        )

    semantic_install = contract.get("semantic_install")
    if not isinstance(semantic_install, dict):
        errors.append("skill contract must contain [semantic_install]")
    else:
        expected_install = {
            "dependency_resolution": "consumer",
            "selective_install_requires_transitive_closure": True,
            "complete_profile": "sovereign-harness",
        }
        for field, expected_value in expected_install.items():
            if semantic_install.get(field) != expected_value:
                errors.append(
                    f"semantic_install.{field} must be {expected_value!r}; "
                    f"found {semantic_install.get(field)!r}"
                )

    profiles = contract.get("profiles")
    profile = profiles.get("sovereign-harness") if isinstance(profiles, dict) else None
    if not isinstance(profile, dict) or profile.get("selection") != "all-public":
        errors.append(
            "profiles.sovereign-harness.selection must be 'all-public'"
        )

    for skill_name, entry in sorted(skills.items()):
        routing_contract = entry.get("routing_contract")
        source = entry.get("source")
        public_id = entry.get("public_id")
        if not routing_contract or not isinstance(source, str) or not isinstance(public_id, str):
            continue
        routing_path = repo_root / source / routing_contract
        try:
            with routing_path.open("rb") as handle:
                routing = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError):
            continue
        expected_targets: set[str] = set()
        for table_name in ("phase_routes", "review_evaluators", "support_routes"):
            table = routing.get(table_name)
            if isinstance(table, dict):
                expected_targets.update(
                    target for target in table.values() if isinstance(target, str)
                )
        composition = routing.get("composition")
        if isinstance(composition, dict):
            rendering_baseline = composition.get("rendering_baseline")
            if isinstance(rendering_baseline, str):
                expected_targets.add(rendering_baseline)
        expected_targets.discard(public_id)
        declared_targets = adjacency.get(public_id, set())
        if declared_targets != expected_targets:
            errors.append(
                f"{skill_name}: semantic_requires must match routing targets; "
                f"expected={sorted(expected_targets)} actual={sorted(declared_targets)}"
            )

    for skill_name, entry in sorted(skills.items()):
        runtime_contract = entry.get("runtime_contract")
        source = entry.get("source")
        if not runtime_contract or not isinstance(source, str):
            continue
        contract_path = repo_root / source / runtime_contract
        try:
            with contract_path.open("rb") as handle:
                runtime = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError):
            continue
        for edge in runtime.get("edges", []):
            if not isinstance(edge, dict):
                continue
            source_id = edge.get("from")
            target_id = edge.get("to")
            if (
                isinstance(source_id, str)
                and isinstance(target_id, str)
                and target_id not in adjacency.get(source_id, set())
            ):
                errors.append(
                    f"{skill_name}: runtime edge lacks semantic_requires declaration: "
                    f"{source_id} -> {target_id}"
                )

    return errors


def validate_command_retirement_contract(
    contract: dict[str, Any], repo_root: Path = REPO_ROOT
) -> list[str]:
    retirement = contract.get("command_retirement")
    if not isinstance(retirement, dict):
        return ["skill contract must contain [command_retirement]"]

    errors: list[str] = []
    archive_destination = retirement.get("archive_destination")
    if archive_destination != "archived/commands":
        errors.append(
            "command_retirement.archive_destination must be 'archived/commands'"
        )
    if retirement.get("archive_ready") is not True:
        errors.append("command_retirement.archive_ready must be true after parity")

    groups: dict[str, list[str]] = {}
    for field in ("absorbed_by_skill", "thin_wrappers", "archive_only"):
        values = retirement.get(field)
        if not isinstance(values, list) or not all(
            isinstance(value, str) and value for value in values
        ):
            errors.append(
                f"command_retirement.{field} must be an array of non-empty strings"
            )
            groups[field] = []
        else:
            groups[field] = values

    classified = [item for values in groups.values() for item in values]
    if len(classified) != len(set(classified)):
        errors.append("command retirement classifications must be disjoint")
    if groups.get("archive_only") != ["check-secrets"]:
        errors.append("check-secrets must be the only archive-only command")

    active_root = repo_root / "commands"
    archive_root = repo_root / str(archive_destination)
    active_commands = {
        path.stem for path in active_root.glob("*.md") if path.is_file()
    }
    archived_commands = {
        path.stem for path in archive_root.glob("*.md") if path.is_file()
    }
    duplicates = sorted(active_commands & archived_commands)
    if duplicates:
        errors.append(
            "command docs cannot be active and archived simultaneously: "
            + ", ".join(duplicates)
        )
    actual_commands = active_commands | archived_commands
    expected_commands = set(classified)
    if actual_commands != expected_commands:
        errors.append(
            "command retirement inventory differs; "
            f"expected={sorted(expected_commands)} actual={sorted(actual_commands)}"
        )

    skills = contract.get("skills")
    public_ids = set()
    if isinstance(skills, dict):
        public_ids = {
            entry.get("public_id")
            for entry in skills.values()
            if isinstance(entry, dict)
        }
    for command_name in groups.get("absorbed_by_skill", []) + groups.get(
        "thin_wrappers", []
    ):
        if command_name not in public_ids:
            errors.append(
                f"command retirement owner is not a public skill: {command_name}"
            )

    return errors


def load_manifest() -> dict[str, Any]:
    with CONTRACT_PATH.open("rb") as handle:
        data = tomllib.load(handle)
    skills = data.get("skills")
    if not isinstance(skills, dict):
        raise TypeError("contracts/skills.toml must contain [skills.*] entries")
    return skills


def source_skill_dirs() -> set[str]:
    result: set[str] = set()
    for skill_file in (REPO_ROOT / "src" / "skills").rglob("SKILL.md"):
        result.add(skill_file.parent.relative_to(REPO_ROOT).as_posix())
    return result


def _runtime_contract_cycle(adjacency: dict[str, set[str]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visited:
            return None
        if node in visiting:
            start = stack.index(node)
            return stack[start:] + [node]

        visiting.add(node)
        stack.append(node)
        for target in sorted(adjacency.get(node, set())):
            cycle = visit(target)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in sorted(adjacency):
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def validate_runtime_contracts(skills: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    public_entries: dict[str, dict[str, Any]] = {}
    global_node_roles: dict[str, str] = {}
    global_edges: set[tuple[str, str]] = set()
    global_forbidden_edges: set[tuple[str, str]] = set()
    global_repair_owners: list[tuple[str, str]] = []
    for skill_name, entry in skills.items():
        public_id = entry.get("public_id")
        if isinstance(public_id, str) and public_id:
            public_entries[public_id] = entry

    for skill_name, entry in sorted(skills.items()):
        runtime_contract = entry.get("runtime_contract")
        if runtime_contract is None:
            continue
        if not isinstance(runtime_contract, str) or not runtime_contract:
            errors.append(f"{skill_name}: runtime_contract must be a non-empty relative path")
            continue
        if Path(runtime_contract).is_absolute() or ".." in Path(runtime_contract).parts:
            errors.append(f"{skill_name}: runtime_contract must stay inside the skill source")
            continue

        source = entry.get("source")
        if not isinstance(source, str):
            errors.append(f"{skill_name}: runtime contract requires a valid source")
            continue
        contract_path = repo_root / source / runtime_contract
        if not contract_path.is_file():
            errors.append(f"{skill_name}: runtime contract does not exist: {contract_path.relative_to(repo_root)}")
            continue

        try:
            with contract_path.open("rb") as handle:
                contract = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"{skill_name}: invalid runtime contract: {exc}")
            continue

        workflow = contract.get("workflow")
        nodes = contract.get("nodes")
        edges = contract.get("edges", [])
        forbidden_edges = contract.get("forbidden_edges", [])
        repair = contract.get("repair")
        public_id = entry.get("public_id")

        if not isinstance(workflow, dict) or workflow.get("id") != public_id:
            errors.append(f"{skill_name}: workflow.id must match public_id")
        if not isinstance(nodes, list) or not nodes:
            errors.append(f"{skill_name}: runtime contract requires at least one [[nodes]] entry")
            continue

        node_roles: dict[str, str] = {}
        repair_owners: list[str] = []
        for node in nodes:
            if not isinstance(node, dict):
                errors.append(f"{skill_name}: each runtime node must be a table")
                continue
            node_id = node.get("id")
            role = node.get("role")
            if not isinstance(node_id, str) or not node_id:
                errors.append(f"{skill_name}: runtime node id must be a non-empty string")
                continue
            if node_id in node_roles:
                errors.append(f"{skill_name}: duplicate runtime node: {node_id}")
                continue
            if node_id not in public_entries:
                errors.append(f"{skill_name}: unknown runtime node target: {node_id}")
            if role not in VALID_WORKFLOW_ROLES:
                errors.append(f"{skill_name}: invalid runtime node role for {node_id}: {role}")
            node_roles[node_id] = str(role)
            existing_role = global_node_roles.get(node_id)
            if existing_role is not None and existing_role != role:
                errors.append(
                    f"{skill_name}: runtime node role conflicts across contracts for {node_id}: "
                    f"{existing_role} != {role}"
                )
            else:
                global_node_roles[node_id] = str(role)
            if node.get("owns_repair_loop", False):
                repair_owners.append(node_id)

        edge_set: set[tuple[str, str]] = set()
        adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_roles}
        if not isinstance(edges, list):
            errors.append(f"{skill_name}: edges must be an array of tables")
            edges = []
        for edge in edges:
            if not isinstance(edge, dict):
                errors.append(f"{skill_name}: each runtime edge must be a table")
                continue
            source_id = edge.get("from")
            target_id = edge.get("to")
            if source_id not in node_roles or target_id not in node_roles:
                errors.append(f"{skill_name}: runtime edge references unknown node: {source_id} -> {target_id}")
                continue
            edge_pair = (str(source_id), str(target_id))
            edge_set.add(edge_pair)
            global_edges.add(edge_pair)
            adjacency[str(source_id)].add(str(target_id))
            if node_roles[str(source_id)] == "evaluator":
                errors.append(f"{skill_name}: evaluator cannot invoke another skill: {source_id} -> {target_id}")

        if not isinstance(forbidden_edges, list):
            errors.append(f"{skill_name}: forbidden_edges must be an array of tables")
            forbidden_edges = []
        for edge in forbidden_edges:
            if not isinstance(edge, dict):
                errors.append(f"{skill_name}: each forbidden edge must be a table")
                continue
            edge_pair = (str(edge.get("from", "")), str(edge.get("to", "")))
            global_forbidden_edges.add(edge_pair)
            if edge_pair in edge_set:
                errors.append(f"{skill_name}: forbidden runtime edge is active: {edge_pair[0]} -> {edge_pair[1]}")

        cycle = _runtime_contract_cycle(adjacency)
        if cycle:
            errors.append(f"{skill_name}: runtime invocation graph contains a cycle: {' -> '.join(cycle)}")

        if not isinstance(repair, dict):
            errors.append(f"{skill_name}: runtime contract requires a [repair] table")
            continue
        repair_owner = repair.get("owner")
        initial_review_passes = repair.get("initial_review_passes")
        focused_verification_passes = repair.get("focused_verification_passes")
        additional_repair_attempts = repair.get("additional_same_slice_repair_attempts")
        if repair_owners != [repair_owner]:
            errors.append(f"{skill_name}: runtime contract must declare exactly one matching repair-loop owner")
        if isinstance(repair_owner, str) and repair_owner:
            global_repair_owners.append((skill_name, repair_owner))
        if repair_owner != public_id or not entry.get("lifecycle_owner", False):
            errors.append(f"{skill_name}: repair-loop owner must be the lifecycle-owning public skill")
        if not all(
            isinstance(value, int)
            for value in (initial_review_passes, focused_verification_passes, additional_repair_attempts)
        ):
            errors.append(f"{skill_name}: bounded review pass limits must be integers")
        elif not (
            initial_review_passes == 1
            and focused_verification_passes == 1
            and 0 <= additional_repair_attempts <= 1
        ):
            errors.append(
                f"{skill_name}: bounded review requires one initial pass, one focused verification pass, "
                "and at most one additional same-slice repair attempt"
            )

    global_adjacency: dict[str, set[str]] = {
        node_id: set() for node_id in global_node_roles
    }
    for source_id, target_id in global_edges:
        global_adjacency.setdefault(source_id, set()).add(target_id)
        global_adjacency.setdefault(target_id, set())
        if global_node_roles.get(source_id) == "evaluator":
            errors.append(
                f"global runtime graph: evaluator cannot invoke another skill: "
                f"{source_id} -> {target_id}"
            )

    global_cycle = _runtime_contract_cycle(global_adjacency)
    if global_cycle:
        errors.append(
            "global runtime invocation graph contains a cycle: "
            + " -> ".join(global_cycle)
        )

    for source_id, target_id in sorted(global_forbidden_edges & global_edges):
        errors.append(
            f"global runtime graph: forbidden edge is active: {source_id} -> {target_id}"
        )

    if len(global_repair_owners) != 1:
        owner_summary = ", ".join(
            f"{skill_name}:{owner}" for skill_name, owner in global_repair_owners
        ) or "none"
        errors.append(
            "global runtime contracts must declare exactly one repair-loop owner; "
            f"found {owner_summary}"
        )

    return errors


def validate_routing_contracts(
    skills: dict[str, Any],
    repo_root: Path = REPO_ROOT,
    workflow_modes: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    public_entries = {
        entry.get("public_id"): entry
        for entry in skills.values()
        if isinstance(entry.get("public_id"), str)
    }
    routing_entries = [
        (skill_name, entry)
        for skill_name, entry in sorted(skills.items())
        if entry.get("routing_contract") is not None
    ]

    if len(routing_entries) != 1:
        errors.append(
            "skill manifest must declare exactly one routing_contract; "
            f"found {len(routing_entries)}"
        )
        return errors

    if workflow_modes is None:
        modes_path = repo_root / "contracts" / "workflow-modes.toml"
        try:
            with modes_path.open("rb") as handle:
                workflow_modes = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            return [f"invalid workflow mode contract: {exc}"]

    modes = workflow_modes.get("modes") if isinstance(workflow_modes, dict) else None
    if not isinstance(modes, dict) or not modes:
        return ["workflow mode contract must contain [modes.*] entries"]

    expected_phases: set[str] = set()
    for mode_name, mode in modes.items():
        phases = mode.get("phases") if isinstance(mode, dict) else None
        if not isinstance(phases, list) or not all(
            isinstance(phase, str) for phase in phases
        ):
            errors.append(f"workflow mode {mode_name}: phases must be a string array")
            continue
        expected_phases.update(phases)

    skill_name, entry = routing_entries[0]
    routing_contract = entry.get("routing_contract")
    source = entry.get("source")
    public_id = entry.get("public_id")

    if entry.get("category") != "session" or entry.get("lifecycle_owner", False):
        errors.append(
            f"{skill_name}: routing contract owner must be a non-lifecycle session skill"
        )
    if not isinstance(routing_contract, str) or not routing_contract:
        errors.append(
            f"{skill_name}: routing_contract must be a non-empty relative path"
        )
        return errors
    if Path(routing_contract).is_absolute() or ".." in Path(routing_contract).parts:
        errors.append(
            f"{skill_name}: routing_contract must stay inside the skill source"
        )
        return errors
    if not isinstance(source, str):
        errors.append(f"{skill_name}: routing contract requires a valid source")
        return errors

    contract_path = repo_root / source / routing_contract
    if not contract_path.is_file():
        errors.append(
            f"{skill_name}: routing contract does not exist: {contract_path.relative_to(repo_root)}"
        )
        return errors

    try:
        with contract_path.open("rb") as handle:
            contract = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [f"{skill_name}: invalid routing contract: {exc}"]

    routing = contract.get("routing")
    host_wrapper = contract.get("host_wrapper")
    composition = contract.get("composition")
    gate_policy = contract.get("gate_policy")
    phase_routes = contract.get("phase_routes")
    review_evaluators = contract.get("review_evaluators")
    support_routes = contract.get("support_routes")

    if not isinstance(routing, dict) or routing.get("id") != public_id:
        errors.append(f"{skill_name}: routing.id must match public_id")
    elif (
        routing.get("default_discovery") != "native-description-match"
        or routing.get("direct_match_bypasses_router") is not True
        or routing.get("ambiguous_router") != public_id
    ):
        errors.append(
            f"{skill_name}: routing must keep native discovery, direct-match bypass, and self-owned ambiguity routing"
        )

    if not isinstance(host_wrapper, dict):
        errors.append(f"{skill_name}: routing contract requires [host_wrapper]")
    else:
        for field in ("allowed", "forbidden"):
            values = host_wrapper.get(field)
            if (
                not isinstance(values, list)
                or not values
                or not all(isinstance(value, str) for value in values)
            ):
                errors.append(
                    f"{skill_name}: host_wrapper.{field} must be a non-empty string array"
                )

    if not isinstance(composition, dict):
        errors.append(f"{skill_name}: routing contract requires [composition]")
    else:
        if composition.get("primary_owner_count") != 1:
            errors.append(
                f"{skill_name}: composition must declare exactly one primary owner"
            )
        rendering_baseline = composition.get("rendering_baseline")
        if rendering_baseline not in public_entries:
            errors.append(
                f"{skill_name}: unknown rendering baseline: {rendering_baseline}"
            )
        if composition.get("lifecycle_owner_category") != "workflow":
            errors.append(
                f"{skill_name}: lifecycle owner category must remain workflow"
            )

    if not isinstance(gate_policy, dict):
        errors.append(f"{skill_name}: routing contract requires [gate_policy]")
        gate_policy = {}
    design_phases = gate_policy.get("design_phases")
    plan_phases = gate_policy.get("plan_phases")
    for field, values in (("design_phases", design_phases), ("plan_phases", plan_phases)):
        if not isinstance(values, list) or not values or not all(isinstance(value, str) for value in values):
            errors.append(f"{skill_name}: gate_policy.{field} must be a non-empty string array")
        elif unknown_gate_phases := sorted(set(values) - expected_phases):
            errors.append(
                f"{skill_name}: gate_policy.{field} contains unknown phases: {', '.join(unknown_gate_phases)}"
            )
    if gate_policy.get("implicit_review_when_missing") is not True:
        errors.append(f"{skill_name}: gate policy must preserve implicit design and plan review")
    for field in ("design_review_phase", "plan_review_phase", "truth_sync_phase", "close_phase"):
        phase = gate_policy.get(field)
        if phase not in expected_phases:
            errors.append(f"{skill_name}: gate_policy.{field} must name a workflow phase")

    if not isinstance(phase_routes, dict):
        errors.append(f"{skill_name}: routing contract requires [phase_routes]")
        phase_routes = {}
    missing_phases = sorted(expected_phases - set(phase_routes))
    extra_phases = sorted(set(phase_routes) - expected_phases)
    if missing_phases:
        errors.append(
            f"{skill_name}: phase routes missing workflow phases: {', '.join(missing_phases)}"
        )
    if extra_phases:
        errors.append(
            f"{skill_name}: phase routes contain unknown workflow phases: {', '.join(extra_phases)}"
        )

    for phase, target in phase_routes.items():
        target_entry = public_entries.get(target)
        if target_entry is None:
            errors.append(
                f"{skill_name}: phase {phase} routes to unknown skill: {target}"
            )
        elif not target_entry.get("lifecycle_owner", False):
            errors.append(
                f"{skill_name}: phase {phase} must route to a lifecycle owner: {target}"
            )

    if not isinstance(review_evaluators, dict):
        errors.append(f"{skill_name}: routing contract requires [review_evaluators]")
        review_evaluators = {}
    review_phases = {
        phase for phase, target in phase_routes.items() if target == "review-change"
    }
    if missing_review_phases := sorted(review_phases - set(review_evaluators)):
        errors.append(
            f"{skill_name}: review evaluators missing review phases: {', '.join(missing_review_phases)}"
        )
    if extra_review_phases := sorted(set(review_evaluators) - review_phases):
        errors.append(
            f"{skill_name}: review evaluators contain non-review phases: {', '.join(extra_review_phases)}"
        )
    for phase, target in review_evaluators.items():
        target_entry = public_entries.get(target)
        if target_entry is None:
            errors.append(
                f"{skill_name}: review phase {phase} uses unknown evaluator: {target}"
            )
        elif target_entry.get("category") != "review-component":
            errors.append(
                f"{skill_name}: review phase {phase} must use a review-component: {target}"
            )

    for field in ("design_review_phase", "plan_review_phase"):
        review_phase = gate_policy.get(field)
        if review_phase not in review_evaluators:
            errors.append(f"{skill_name}: gate_policy.{field} must select a review evaluator phase")

    if not isinstance(support_routes, dict) or not support_routes:
        errors.append(
            f"{skill_name}: routing contract requires non-empty [support_routes]"
        )
    else:
        for intent, target in support_routes.items():
            target_entry = public_entries.get(target)
            if target_entry is None:
                errors.append(
                    f"{skill_name}: support route {intent} targets unknown skill: {target}"
                )
            elif target_entry.get("lifecycle_owner", False):
                errors.append(
                    f"{skill_name}: support route {intent} cannot target a lifecycle owner: {target}"
                )

    return errors


def check_index() -> list[str]:
    if not INDEX_PATH.is_file():
        return ["skills.index.json is missing"]
    result = subprocess.run(
        [sys.executable, "scripts/generate-skills-index.py", "--check"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [result.stderr.strip() or result.stdout.strip() or "skills.index.json is stale"]
    try:
        json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"skills.index.json is invalid JSON: {exc}"]
    return []


def validate() -> list[str]:
    errors = validate_distribution_contract()
    try:
        with CONTRACT_PATH.open("rb") as handle:
            contract = tomllib.load(handle)
        skills = contract.get("skills")
        if not isinstance(skills, dict):
            raise TypeError("contracts/skills.toml must contain [skills.*] entries")
    except (OSError, tomllib.TOMLDecodeError, TypeError) as exc:
        return [str(exc)]

    manifest_sources: set[str] = set()
    public_ids: set[str] = set()
    runtime_owners: set[str] = set()

    for skill_name, entry in sorted(skills.items()):
        source = entry.get("source")
        public_id = entry.get("public_id")
        category = entry.get("category")
        install = entry.get("install", [])

        if not isinstance(source, str):
            errors.append(f"{skill_name}: source must be a string")
            continue
        manifest_sources.add(source)
        source_path = REPO_ROOT / source
        if not source_path.is_dir():
            errors.append(f"{skill_name}: source does not exist: {source}")
        elif not (source_path / "SKILL.md").is_file():
            errors.append(f"{skill_name}: source lacks SKILL.md: {source}")

        if not isinstance(public_id, str) or not public_id:
            errors.append(f"{skill_name}: public_id must be a non-empty string")
        elif public_id in public_ids:
            errors.append(f"{skill_name}: duplicate public_id: {public_id}")
        else:
            public_ids.add(public_id)

        if category not in VALID_CATEGORIES:
            errors.append(f"{skill_name}: invalid category: {category}")

        if entry.get("lifecycle_owner", False) and category != "workflow":
            errors.append(f"{skill_name}: only workflow skills may set lifecycle_owner=true")

        if category == "internal":
            external_installs = sorted(set(install) & EXTERNAL_TARGETS)
            if external_installs:
                errors.append(f"{skill_name}: internal skill exposes external targets: {external_installs}")
            if install and install != ["root-flat"]:
                errors.append(f"{skill_name}: internal install must be [] or ['root-flat']")
            if install == ["root-flat"] and not entry.get("runtime_support", False):
                errors.append(f"{skill_name}: root-flat internal support requires runtime_support=true")

        runtime_bundle = entry.get("runtime_bundle")
        if runtime_bundle is not None:
            if runtime_bundle not in RUNTIME_BUNDLES:
                errors.append(
                    f"{skill_name}: unknown runtime_bundle: {runtime_bundle}"
                )
            elif category != "workflow" or not entry.get("lifecycle_owner", False):
                errors.append(
                    f"{skill_name}: runtime bundles belong only to lifecycle workflow skills"
                )
            elif isinstance(public_id, str):
                runtime_owners.add(public_id)

        if category == "manual-tool" and entry.get("implicit_invocation", False):
            errors.append(f"{skill_name}: manual-tool cannot be implicitly invoked")

        if entry.get("may_mutate_repo", False):
            has_guard = entry.get("requires_explicit_user_request", False) or entry.get("requires_approved_plan", False)
            if not has_guard:
                errors.append(f"{skill_name}: mutation-capable skills need explicit request or approved-plan guard")

    source_dirs = source_skill_dirs()
    missing_manifest = sorted(source_dirs - manifest_sources)
    stale_manifest = sorted(manifest_sources - source_dirs)
    if missing_manifest:
        errors.append("source skills missing manifest entries: " + ", ".join(missing_manifest))
    if stale_manifest:
        errors.append("manifest sources missing from src/skills: " + ", ".join(stale_manifest))

    if runtime_owners != EXPECTED_RUNTIME_OWNERS:
        errors.append(
            "runtime bundle owners differ; "
            f"expected={sorted(EXPECTED_RUNTIME_OWNERS)} actual={sorted(runtime_owners)}"
        )
    for bundle_name, bundle_root in RUNTIME_BUNDLES.items():
        if not bundle_root.is_dir():
            errors.append(f"runtime bundle source is missing: {bundle_name}")
        elif (bundle_root / "SKILL.md").exists():
            errors.append(f"runtime bundle source must not be discoverable: {bundle_name}")

    errors.extend(validate_runtime_contracts(skills))
    errors.extend(validate_routing_contracts(skills))
    errors.extend(validate_semantic_contracts(contract))
    errors.extend(validate_command_retirement_contract(contract))
    errors.extend(check_index())
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("contracts ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
