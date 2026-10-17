#!/usr/bin/env python3
"""Validate the authored Skill inventory, discovery, and semantic contracts."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.skill_activation import (  # noqa: E402 - imports follow path bootstrap
    validate_activation_contract,
)

CONTRACT_PATH = REPO_ROOT / "contracts" / "skills.toml"
PROBE_PATH = Path("tests") / "fixtures" / "selection-probes.toml"
VALID_CATEGORIES = {
    "workflow",
    "session",
    "discipline",
    "policy",
    "tool",
    "review-component",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NO_SKILL = "none"
ROUTING_VERSION = 2
SELECTABLE_MODES = {"native", "conditional", "explicit"}
RETIRED_ROUTING_TABLES = (
    "gate_policy",
    "phase_routes",
    "review_evaluators",
    "routing",
    "environment_instructions",
    "composition",
    "support_routes",
    "trigger_cases",
)


def validate_semantic_contracts(
    contract: dict[str, Any], repo_root: Path = REPO_ROOT
) -> list[str]:
    skills = contract.get("skills")
    if not isinstance(skills, dict):
        return ["skill contract must contain [skills.*] entries"]

    errors: list[str] = []
    public_entries = {
        name: entry for name, entry in skills.items() if isinstance(entry, dict)
    }
    routing_owners = {
        name for name, entry in public_entries.items() if entry.get("routing_contract")
    }
    adjacency: dict[str, set[str]] = {name: set() for name in public_entries}

    for skill_name, entry in sorted(public_entries.items()):
        requirements = entry.get("semantic_requires", [])
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
            if target == skill_name:
                errors.append(
                    f"{skill_name}: semantic_requires cannot reference itself"
                )
            elif target not in public_entries:
                errors.append(
                    f"{skill_name}: semantic_requires references unknown skill: {target}"
                )
            else:
                adjacency[skill_name].add(target)
        if entry.get("category") == "review-component" and requirements:
            errors.append(
                f"{skill_name}: review-component evaluators cannot invoke semantic dependencies"
            )
        if entry.get("category") == "review-component":
            if entry.get("may_spawn_agent", False):
                errors.append(
                    f"{skill_name}: review-component evaluators cannot delegate; may_spawn_agent must be false"
                )
            if entry.get("may_mutate_repo", False):
                errors.append(
                    f"{skill_name}: review-component evaluators are read-only; may_mutate_repo must be false"
                )
        if routing_owners.intersection(requirements):
            errors.append(
                f"{skill_name}: public skills cannot depend on the optional session router"
            )

    cycle = _semantic_dependency_cycle(adjacency)
    if cycle:
        errors.append(
            "semantic dependency graph contains a cycle: " + " -> ".join(cycle)
        )

    composers = {
        target
        for skill_name, targets in adjacency.items()
        if skill_name not in routing_owners
        for target in targets
    }
    for skill_name, entry in sorted(public_entries.items()):
        if (
            entry.get("activation_mode") == "composition"
            and entry.get("default_role") != "evaluator"
            and skill_name not in composers
        ):
            errors.append(
                f"{skill_name}: composition-only skill needs a semantic composer other than the router"
            )

    return errors


def canonical_skill_dirs() -> set[str]:
    result: set[str] = set()
    for skill_file in (REPO_ROOT / "skills").glob("*/SKILL.md"):
        result.add(skill_file.parent.name)
    return result


def validate_semantic_only_surface(repo_root: Path = REPO_ROOT) -> list[str]:
    """Reject executable workflow surfaces and stale maintained product truth."""
    errors: list[str] = []
    removed_paths = (
        Path(".pi"),
        Path("integrations") / "pi",
        Path("src") / "runtime" / "harness",
        Path("scripts") / ("generate-" + "pi-contracts.py"),
        Path("contracts") / ("runtime-" + "bundles.toml"),
    )
    for relative in removed_paths:
        if (repo_root / relative).exists():
            errors.append(f"retired executable workflow surface remains: {relative}")

    with (repo_root / "contracts" / "skills.toml").open("rb") as handle:
        skills = tomllib.load(handle)["skills"]
    for skill_id, entry in skills.items():
        if not isinstance(entry, dict) or entry.get("category") not in {
            "workflow",
            "review-component",
        }:
            continue
        for path in (repo_root / "skills" / skill_id / "scripts").rglob("*"):
            if path.is_file():
                errors.append(
                    "semantic workflow surface contains executable support: "
                    + path.relative_to(repo_root).as_posix()
                )

    project_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    if "coding-" + "harness-development" in project_text:
        errors.append("pyproject retains the retired development package identity")
    return errors


def _semantic_dependency_cycle(adjacency: dict[str, set[str]]) -> list[str] | None:
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


def target_error(
    target: object,
    public_entries: dict[str, dict[str, Any]],
    repo_root: Path,
    *,
    allow_none: bool,
    allow_evaluator: bool = False,
) -> str | None:
    """Explain why a selection target does not resolve; None means it resolves.

    A target is a public Skill ID, `<id>:<reference>` for a method reference
    inside that Skill, or `none` where no Skill of this collection is needed.
    """
    if not isinstance(target, str) or not target:
        return "must be a non-empty string"
    if target == NO_SKILL:
        return None if allow_none else f"cannot be {NO_SKILL}"
    skill_id, separator, reference = target.partition(":")
    entry = public_entries.get(skill_id)
    if entry is None:
        return f"references unknown skill: {skill_id}"
    if entry.get("default_role") == "evaluator" and not allow_evaluator:
        return f"cannot select a composition-only evaluator: {skill_id}"
    if separator and not (
        NAME_PATTERN.fullmatch(reference)
        and (repo_root / "skills" / skill_id / "references" / f"{reference}.md").is_file()
    ):
        return f"references unknown method: {target}"
    return None


def _string_duplicates(values: list[Any]) -> bool:
    strings = [value for value in values if isinstance(value, str)]
    return len(strings) != len(set(strings))


def _handoff_errors(
    label: str,
    handoff: object,
    public_entries: dict[str, dict[str, Any]],
    repo_root: Path,
) -> list[str]:
    if not isinstance(handoff, dict):
        return [f"{label}: must be a table"]
    errors: list[str] = []
    when = handoff.get("when")
    if not isinstance(when, str) or not when.strip():
        errors.append(f"{label}: requires a non-empty when")
    owner = handoff.get("owner")
    if not isinstance(owner, str):
        errors.append(f"{label}: exactly one owner is required")
    else:
        problem = target_error(owner, public_entries, repo_root, allow_none=True)
        if problem:
            errors.append(f"{label}: owner {problem}")
    candidates = handoff.get("instead_of")
    if not isinstance(candidates, list) or not candidates:
        errors.append(f"{label}: instead_of requires at least one candidate")
        return errors
    if _string_duplicates(candidates):
        errors.append(f"{label}: instead_of contains duplicates")
    for candidate in candidates:
        problem = target_error(
            candidate, public_entries, repo_root, allow_none=True, allow_evaluator=True
        )
        if problem:
            errors.append(f"{label}: instead_of {problem}")
        elif candidate == owner:
            errors.append(f"{label}: owner cannot also be a replaced candidate")
    return errors


def validate_scope_contract(
    skills: dict[str, Any],
    routing_contract: dict[str, Any],
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    public_entries = {
        name: entry for name, entry in skills.items() if isinstance(entry, dict)
    }
    clusters = routing_contract.get("clusters")
    if not isinstance(clusters, list) or not clusters:
        return ["routing contract requires non-empty [[clusters]] entries"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    clustered: set[str] = set()
    for index, cluster in enumerate(clusters, start=1):
        if not isinstance(cluster, dict):
            errors.append(f"cluster #{index} must be a table")
            continue
        cluster_id = cluster.get("id")
        label = f"cluster {cluster_id or f'#{index}'}"
        if not isinstance(cluster_id, str) or not NAME_PATTERN.fullmatch(cluster_id):
            errors.append(f"{label}: id must be a stable kebab-case string")
        elif cluster_id in seen_ids:
            errors.append(f"duplicate cluster id: {cluster_id}")
        else:
            seen_ids.add(cluster_id)

        question = cluster.get("question")
        if not isinstance(question, str) or not question.strip():
            errors.append(f"{label}: requires a non-empty question")

        members = cluster.get("members")
        if not isinstance(members, list) or not members:
            errors.append(f"{label}: requires non-empty members")
            members = []
        elif _string_duplicates(members):
            errors.append(f"{label}: members contain duplicates")
        for member in members:
            problem = target_error(member, public_entries, repo_root, allow_none=False)
            if problem:
                errors.append(f"{label}: member {problem}")
            else:
                clustered.add(member)

        handoffs = cluster.get("handoffs", [])
        if not isinstance(handoffs, list):
            errors.append(f"{label}: handoffs must be an array of tables")
            continue
        for number, handoff in enumerate(handoffs, start=1):
            errors.extend(
                _handoff_errors(
                    f"{label} handoff #{number}", handoff, public_entries, repo_root
                )
            )

    for public_id, entry in sorted(public_entries.items()):
        if (
            entry.get("activation_mode") in SELECTABLE_MODES
            and public_id not in clustered
        ):
            errors.append(
                f"{public_id}: selectable skill must be a member of at least one cluster"
            )
    return errors


def validate_selection_probes(
    skills: dict[str, Any], repo_root: Path = REPO_ROOT
) -> list[str]:
    try:
        with (repo_root / PROBE_PATH).open("rb") as handle:
            corpus = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [f"invalid selection probe corpus {PROBE_PATH.as_posix()}: {exc}"]
    probes = corpus.get("probes")
    if not isinstance(probes, list) or not probes:
        return ["selection probe corpus requires non-empty [[probes]] entries"]

    public_entries = {
        name: entry for name, entry in skills.items() if isinstance(entry, dict)
    }
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, probe in enumerate(probes, start=1):
        if not isinstance(probe, dict):
            errors.append(f"probe #{index} must be a table")
            continue
        probe_id = probe.get("id")
        label = f"probe {probe_id or f'#{index}'}"
        if not isinstance(probe_id, str) or not NAME_PATTERN.fullmatch(probe_id):
            errors.append(f"{label}: id must be a stable kebab-case string")
        elif probe_id in seen_ids:
            errors.append(f"duplicate probe id: {probe_id}")
        else:
            seen_ids.add(probe_id)

        selections = []
        for request_key, prefix in (("request", ""), ("counterexample", "counterexample_")):
            request = probe.get(request_key)
            if not isinstance(request, str) or not request.strip():
                errors.append(f"{label}: requires a non-empty {request_key}")
            primary = probe.get(f"{prefix}primary")
            problem = target_error(primary, public_entries, repo_root, allow_none=True)
            if problem:
                errors.append(f"{label}: {prefix}primary {problem}")
            overlays = probe.get(f"{prefix}overlays", [])
            if not isinstance(overlays, list):
                errors.append(f"{label}: {prefix}overlays must be an array")
                overlays = []
            elif _string_duplicates(overlays):
                errors.append(f"{label}: {prefix}overlays contain duplicates")
            for overlay in overlays:
                problem = target_error(
                    overlay, public_entries, repo_root, allow_none=False
                )
                if problem:
                    errors.append(f"{label}: {prefix}overlay {problem}")
                elif overlay == primary:
                    errors.append(f"{label}: {prefix}primary cannot also be an overlay")
            selections.append((primary, frozenset(map(str, overlays))))
        if selections[0] == selections[1]:
            errors.append(f"{label}: counterexample must expect a different selection")
    return errors


def validate_routing_contracts(
    skills: dict[str, Any],
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    errors: list[str] = []
    public_entries = {
        name: entry for name, entry in skills.items() if isinstance(entry, dict)
    }
    routing_entries = [
        (skill_name, entry)
        for skill_name, entry in sorted(public_entries.items())
        if entry.get("routing_contract") is not None
    ]

    if len(routing_entries) != 1:
        errors.append(
            "skill manifest must declare exactly one routing_contract; "
            f"found {len(routing_entries)}"
        )
        return errors

    skill_name, entry = routing_entries[0]
    routing_contract = entry.get("routing_contract")

    if entry.get("category") != "session":
        errors.append(f"{skill_name}: routing contract owner must be a session skill")
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
    contract_path = repo_root / "skills" / skill_name / routing_contract
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

    if contract.get("version") != ROUTING_VERSION:
        errors.append(
            f"{skill_name}: routing contract must declare version = {ROUTING_VERSION}"
        )
    for retired_table in RETIRED_ROUTING_TABLES:
        if retired_table in contract:
            errors.append(
                f"{skill_name}: routing contract retains retired table: {retired_table}"
            )

    errors.extend(validate_scope_contract(skills, contract, repo_root))
    return errors


def validate() -> list[str]:
    errors: list[str] = []
    try:
        with CONTRACT_PATH.open("rb") as handle:
            contract = tomllib.load(handle)
        skills = contract.get("skills")
        if not isinstance(skills, dict):
            raise TypeError("contracts/skills.toml must contain [skills.*] entries")
    except (OSError, tomllib.TOMLDecodeError, TypeError) as exc:
        return [str(exc)]

    canonical_ids = set(skills)
    forbidden_contract_fields = {
        "public_id",
        "install",
        "superseded_by",
        "lifecycle_owner",
        "source",
        "distributed",
        "runtime_bundle",
        "runtime_contract",
    }
    for field in ("semantic_install", "profiles"):
        if field in contract:
            errors.append(f"contract retains removed top-level schema: {field}")

    for skill_name, entry in sorted(skills.items()):
        if not isinstance(entry, dict):
            errors.append(f"{skill_name}: skill entry must be a table")
            continue
        if not NAME_PATTERN.fullmatch(skill_name):
            errors.append(f"{skill_name}: skill ID must be a kebab-case directory name")
            continue
        category = entry.get("category")
        source_path = REPO_ROOT / "skills" / skill_name
        if not source_path.is_dir():
            errors.append(f"{skill_name}: authored skill directory does not exist")
        elif not (source_path / "SKILL.md").is_file():
            errors.append(f"{skill_name}: authored skill directory lacks SKILL.md")
        forbidden = sorted(forbidden_contract_fields & set(entry))
        if forbidden:
            errors.append(
                f"{skill_name}: retains removed contract fields: {', '.join(forbidden)}"
            )

        if category not in VALID_CATEGORIES:
            errors.append(f"{skill_name}: invalid category: {category}")

        if entry.get("may_mutate_repo", False):
            has_guard = entry.get("requires_explicit_user_request", False) or entry.get(
                "requires_approved_plan", False
            )
            if not has_guard:
                errors.append(
                    f"{skill_name}: mutation-capable skills need explicit request or approved-plan guard"
                )

        if skill_name in {"sync-truth", "organize-docs"}:
            if not entry.get("requires_explicit_user_request", False):
                errors.append(
                    f"{skill_name}: direct mutation requires an explicit user request guard"
                )

    authored_ids = canonical_skill_dirs()
    unknown_ids = sorted(authored_ids - canonical_ids)
    missing_ids = sorted(canonical_ids - authored_ids)
    if unknown_ids:
        errors.append(
            "authored skills missing contract entries: " + ", ".join(unknown_ids)
        )
    if missing_ids:
        errors.append(
            "contracted skills missing authored directories: " + ", ".join(missing_ids)
        )

    skill_root = REPO_ROOT / "skills"
    non_flat_entries = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in skill_root.rglob("SKILL.md")
        if path.is_file() and path.parent.parent != skill_root
    )
    if non_flat_entries:
        errors.append(
            "Skill entrypoints must use skills/<id>/SKILL.md: "
            + ", ".join(non_flat_entries)
        )

    runtime_dirs = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "skills").glob("*/scripts/harness")
        if path.is_dir()
    )
    if runtime_dirs:
        errors.append("skill-local harness bundles remain: " + ", ".join(runtime_dirs))

    errors.extend(validate_activation_contract(contract, REPO_ROOT, check_sources=True))
    errors.extend(validate_semantic_only_surface())
    errors.extend(validate_routing_contracts(skills))
    errors.extend(validate_semantic_contracts(contract))
    errors.extend(validate_selection_probes(skills))
    if any((REPO_ROOT / "commands").glob("*.md")):
        errors.append("retired command wrappers must not be active entrypoints")
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
