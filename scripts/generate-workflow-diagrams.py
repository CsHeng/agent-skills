#!/usr/bin/env python3
"""Generate stable PlantUML views from the installed workflow contract."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_CONTRACT = REPO_ROOT / "contracts" / "skills.toml"
LIFECYCLE_CONTRACT = REPO_ROOT / "contracts" / "lifecycle.toml"
WORKFLOW_MODES_CONTRACT = REPO_ROOT / "contracts" / "workflow-modes.toml"
CONTROLLER_ID = "implement-change"
ROUTER_ID = "use-coding-skills"
DIAGRAM_DIR = REPO_ROOT / "docs" / "architecture" / "diagrams"
GENERATED_DIR = REPO_ROOT / "docs" / "architecture" / "generated"
DAG_PATH = DIAGRAM_DIR / "implementation-invocation-dag.puml"
REPAIR_PATH = DIAGRAM_DIR / "implementation-repair-loop.puml"
ROUTING_SEQUENCE_PATH = DIAGRAM_DIR / "harness-routing-sequence.puml"
SKILL_PLANES_PATH = DIAGRAM_DIR / "skill-planes.puml"
TRIGGER_OWNERSHIP_PATH = DIAGRAM_DIR / "skill-trigger-ownership.puml"


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def controller_contract() -> tuple[Path, dict[str, Any]]:
    skills = load_toml(SKILLS_CONTRACT)["skills"]
    entry = skills.get(CONTROLLER_ID)
    if not entry:
        raise ValueError(f"missing {CONTROLLER_ID} skill contract")
    runtime_contract = entry.get("runtime_contract")
    if not runtime_contract:
        raise ValueError(f"missing runtime contract for {CONTROLLER_ID}")
    path = REPO_ROOT / entry["source"] / runtime_contract
    contract = load_toml(path)
    if contract.get("workflow", {}).get("id") != CONTROLLER_ID:
        raise ValueError(f"workflow id does not match {CONTROLLER_ID}")
    return path, contract


def routing_contract() -> tuple[Path, dict[str, Any]]:
    skills = load_toml(SKILLS_CONTRACT)["skills"]
    entry = skills.get(ROUTER_ID)
    if not entry:
        raise ValueError(f"missing {ROUTER_ID} skill contract")
    contract_ref = entry.get("routing_contract")
    if not contract_ref:
        raise ValueError(f"missing routing contract for {ROUTER_ID}")
    path = REPO_ROOT / entry["source"] / contract_ref
    contract = load_toml(path)
    if contract.get("routing", {}).get("id") != ROUTER_ID:
        raise ValueError(f"routing id does not match {ROUTER_ID}")
    return path, contract


def alias(value: str) -> str:
    return "n_" + re.sub(r"[^a-zA-Z0-9_]", "_", value)


def render_dag(contract_path: Path, contract: dict[str, Any]) -> str:
    nodes = contract["nodes"]
    edges = contract.get("edges", [])
    forbidden = contract.get("forbidden_edges", [])
    source = contract_path.relative_to(REPO_ROOT).as_posix()
    lines = [
        "@startuml",
        f"' Generated from {source}; do not edit by hand.",
        "title Implementation Invocation DAG",
        "left to right direction",
        "skinparam shadowing false",
        "skinparam componentStyle rectangle",
        "skinparam ArrowColor #475569",
        "skinparam rectangle {",
        "  BackgroundColor #F8FAFC",
        "  BorderColor #475569",
        "}",
        "",
    ]
    for node in nodes:
        node_id = node["id"]
        role = node["role"]
        lines.append(f'rectangle "{node_id}\\n({role})" as {alias(node_id)} <<{role}>>')
    lines.append("")
    for edge in edges:
        lines.append(f'{alias(edge["from"])} --> {alias(edge["to"])} : invoke')

    if forbidden:
        lines.extend(["", f"note bottom of {alias(contract['workflow']['id'])}", "  Forbidden reverse calls:"])
        for edge in forbidden:
            lines.append(f"  {edge['from']} -X-> {edge['to']}")
        lines.append("end note")

    lines.extend(
        [
            "",
            "legend right",
            "  controller = lifecycle and repair owner",
            "  gate = verdict normalization or next-state gate",
            "  evaluator = read-only evidence producer",
            "endlegend",
            "@enduml",
            "",
        ]
    )
    return "\n".join(lines)


def render_repair_loop(contract_path: Path, contract: dict[str, Any]) -> str:
    repair = contract["repair"]
    states = repair["states"]
    typed_exits = repair["typed_exits"]
    source = contract_path.relative_to(REPO_ROOT).as_posix()
    required_states = {"implement", "verify", "review", "classify", "diagnose", "repair"}
    if set(states) != required_states:
        raise ValueError(f"repair states differ from supported diagram shape: {states}")

    lines = [
        "@startuml",
        f"' Generated from {source}; do not edit by hand.",
        "title Controller-Owned Implementation Repair Loop",
        "hide empty description",
        "skinparam shadowing false",
        "skinparam state {",
        "  BackgroundColor #F8FAFC",
        "  BorderColor #475569",
        "}",
        "",
    ]
    for state in states:
        lines.append(f'state "{state}" as {alias(state)}')
    for exit_name in typed_exits:
        lines.append(f'state "{exit_name}" as {alias("exit_" + exit_name)} <<exit>>')

    lines.extend(
        [
            "",
            f"[*] --> {alias('implement')}",
            f"{alias('implement')} --> {alias('verify')} : task slice complete",
            f"{alias('verify')} --> {alias('review')} : declared oracles complete",
            f"{alias('review')} --> {alias('classify')} : bounded candidates",
            f"{alias('classify')} --> {alias('diagnose')} : accepted local repair",
            f"{alias('diagnose')} --> {alias('repair')} : root-cause hypothesis",
            f"{alias('repair')} --> {alias('verify')} : batched in-scope fix",
        ]
    )
    for exit_name in typed_exits:
        label = "review + verification pass" if exit_name == "pass" else "typed boundary"
        lines.append(f"{alias('classify')} --> {alias('exit_' + exit_name)} : {label}")
        lines.append(f"{alias('exit_' + exit_name)} --> [*]")

    lines.extend(
        [
            "",
            f"note right of {alias('repair')}",
            f"  Owner: {repair['owner']}",
            f"  Initial bounded review: {repair['initial_review_passes']}",
            f"  Focused verification: {repair['focused_verification_passes']}",
            f"  Additional same-slice repair attempts: {repair['additional_same_slice_repair_attempts']}",
            "  Only main-agent accepted findings enter repair.",
            "end note",
            "@enduml",
            "",
        ]
    )
    return "\n".join(lines)


def render_review_exchange(
    lines: list[str],
    review_gate: str,
    evaluator: str,
    phase: str,
) -> None:
    lines.extend(
        [
            f"{alias(review_gate)} -> {alias('review-evaluators')} : {phase} via {evaluator}",
            f"{alias('review-evaluators')} --> {alias(review_gate)} : candidate findings",
            f"{alias(review_gate)} -> {alias(review_gate)} : adjudicate + verdict",
        ]
    )


def render_mode_sequence(
    mode_name: str,
    mode: dict[str, Any],
    phase_routes: dict[str, str],
    review_evaluators: dict[str, str],
    gate_policy: dict[str, Any],
) -> list[str]:
    phases = mode["phases"]
    lines = [f"alt mode: {mode_name}"]
    current = alias("mode-selector")
    design_phases = set(gate_policy["design_phases"])
    plan_phases = set(gate_policy["plan_phases"])
    design_review_phase = gate_policy["design_review_phase"]
    plan_review_phase = gate_policy["plan_review_phase"]
    truth_sync_phase = gate_policy["truth_sync_phase"]
    close_phase = gate_policy["close_phase"]

    for index, phase in enumerate(phases):
        target = phase_routes[phase]
        target_alias = alias(target)
        lines.append(f"{current} -> {target_alias} : {phase}")
        current = target_alias

        if phase in review_evaluators:
            render_review_exchange(lines, target, review_evaluators[phase], phase)

        next_phase = phases[index + 1] if index + 1 < len(phases) else None
        if phase in design_phases and next_phase != design_review_phase:
            review_gate = phase_routes[design_review_phase]
            lines.append(f"{current} -> {alias(review_gate)} : mandatory design review")
            render_review_exchange(
                lines,
                review_gate,
                review_evaluators[design_review_phase],
                "design",
            )
            current = alias(review_gate)
        if phase in plan_phases and next_phase != plan_review_phase:
            review_gate = phase_routes[plan_review_phase]
            lines.append(f"{current} -> {alias(review_gate)} : plan review gate")
            render_review_exchange(
                lines,
                review_gate,
                review_evaluators[plan_review_phase],
                "plan",
            )
            current = alias(review_gate)

        if phase == design_review_phase or (phase in design_phases and next_phase != design_review_phase):
            lines.extend(
                [
                    f"{current} -> {alias('user')} : design approval gate",
                    f"{alias('user')} --> {current} : approved",
                ]
            )
        if phase == plan_review_phase or (phase in plan_phases and next_phase != plan_review_phase):
            lines.extend(
                [
                    f"{current} -> {alias('user')} : plan approval gate",
                    f"{alias('user')} --> {current} : approved",
                ]
            )
        if phase == truth_sync_phase:
            lines.extend(
                [
                    f"{current} -> {alias('user')} : truth-sync approval gate",
                    f"{alias('user')} --> {current} : approved",
                ]
            )

    if phases[-1] == close_phase:
        lines.append(
            f"{current} --> {alias('user')} : close decision + remaining human action"
        )
    else:
        lines.append(f"{current} --> {alias('user')} : result / typed stop")
    return lines


def render_routing_sequence(
    routing_path: Path,
    routing_contract_data: dict[str, Any],
    lifecycle: dict[str, Any],
    workflow_modes: dict[str, Any],
) -> str:
    routing_source = routing_path.relative_to(REPO_ROOT).as_posix()
    lifecycle_source = LIFECYCLE_CONTRACT.relative_to(REPO_ROOT).as_posix()
    modes_source = WORKFLOW_MODES_CONTRACT.relative_to(REPO_ROOT).as_posix()
    routing = routing_contract_data["routing"]
    host_wrapper = routing_contract_data["host_wrapper"]
    composition = routing_contract_data["composition"]
    gate_policy = routing_contract_data["gate_policy"]
    phase_routes = routing_contract_data["phase_routes"]
    review_evaluators = routing_contract_data["review_evaluators"]
    support_routes = routing_contract_data["support_routes"]
    kernel = lifecycle["lifecycle"]["kernel"]
    modes = workflow_modes["modes"]

    expected_targets = set(phase_routes.values())
    missing_kernel_targets = expected_targets - set(kernel)
    if missing_kernel_targets:
        raise ValueError(
            "phase routes target skills outside lifecycle kernel: "
            + ", ".join(sorted(missing_kernel_targets))
        )

    lines = [
        "@startuml",
        f"' Generated from {routing_source}, {lifecycle_source}, and {modes_source}; do not edit by hand.",
        "title Harness Request Routing And Lifecycle Sequence",
        "hide footbox",
        "autonumber",
        "skinparam shadowing false",
        "skinparam sequence {",
        "  ArrowColor #475569",
        "  LifeLineBorderColor #64748B",
        "  ParticipantBackgroundColor #F8FAFC",
        "  ParticipantBorderColor #475569",
        "}",
        "",
        f'actor "User" as {alias("user")}',
        f'participant "Host wrapper\\n(user-specific)" as {alias("host-wrapper")}',
        f'participant "Native skill\\nmatching" as {alias("native-matching")}',
        f'participant "{ROUTER_ID}\\n(optional router)" as {alias(ROUTER_ID)}',
        f'participant "Workflow mode\\nselector" as {alias("mode-selector")}',
        f'participant "Lower-plane\\noverlays" as {alias("overlays")}',
    ]
    for workflow_id in kernel:
        lines.append(f'participant "{workflow_id}" as {alias(workflow_id)}')
    lines.append(
        f'participant "review-design / review-plan /\\nreview-implementation" as {alias("review-evaluators")}'
    )
    lines.extend(
        [
            "",
            f"{alias('user')} -> {alias('host-wrapper')} : request",
            f"{alias('host-wrapper')} -> {alias('native-matching')} : request + user/runtime constraints",
            f"note right of {alias('host-wrapper')}",
            "  Allowed:",
        ]
    )
    lines.extend(f"  - {value}" for value in host_wrapper["allowed"])
    lines.append("  Forbidden:")
    lines.extend(f"  - {value}" for value in host_wrapper["forbidden"])
    lines.extend(
        [
            "end note",
            "",
            f"alt explicit skill or confident {routing['default_discovery']}",
            f"  {alias('native-matching')} -> {alias('native-matching')} : choose direct public skill",
            f"  note right of {alias('native-matching')} : {ROUTER_ID} bypassed",
            "else ambiguous multi-stage or explicit routing request",
            f"  {alias('native-matching')} -> {alias(ROUTER_ID)} : resolve primary intent",
            f"  {alias(ROUTER_ID)} --> {alias('native-matching')} : public route + mode hint",
            "end",
            "",
            f"{alias('native-matching')} -> {alias('overlays')} : match support routes",
            f"{alias('overlays')} --> {alias('native-matching')} : policy / method / evidence only",
            f"note right of {alias('overlays')}",
        ]
    )
    lines.extend(f"  {intent} -> {target}" for intent, target in support_routes.items())
    lines.extend(
        [
            "end note",
            "",
            "alt support-only request",
            f"  {alias('native-matching')} -> {alias('overlays')} : invoke matched support skill",
            f"  {alias('overlays')} --> {alias('user')} : result or evidence",
            "else lifecycle request",
            f"  {alias('native-matching')} -> {alias('mode-selector')} : {routing['mode_selector']}",
        ]
    )

    mode_lines: list[str] = []
    for index, (mode_name, mode) in enumerate(modes.items()):
        rendered = render_mode_sequence(
            mode_name,
            mode,
            phase_routes,
            review_evaluators,
            gate_policy,
        )
        if index > 0:
            rendered[0] = f"else mode: {mode_name}"
        mode_lines.extend(f"  {line}" for line in rendered)
    lines.extend(mode_lines)
    lines.extend(
        [
            "  end",
            "end",
            "",
            "legend right",
            f"  one primary owner = {composition['primary_owner_count']}",
            f"  lifecycle owner category = {composition['lifecycle_owner_category']}",
            f"  shared rendering baseline = {composition['rendering_baseline']}",
            "  lower-plane skills never advance lifecycle state",
            "endlegend",
            "@enduml",
            "",
        ]
    )
    return "\n".join(lines)


PLANE_ORDER = [
    ("workflow", "Sovereign Harness Kernel (workflow)"),
    ("session", "Session Plane"),
    ("review-component", "Evaluation Plane (review components)"),
    ("discipline", "Discipline Plane"),
    ("policy", "Policy Plane"),
    ("tool", "Tool Plane"),
    ("manual-tool", "Manual Tools (explicit user request only)"),
]


def render_skill_planes(skills: dict[str, Any]) -> str:
    source = SKILLS_CONTRACT.relative_to(REPO_ROOT).as_posix()
    by_category: dict[str, list[str]] = {}
    for skill_id, entry in sorted(skills.items()):
        category = entry.get("category", "unknown")
        if category == "internal":
            continue
        by_category.setdefault(category, []).append(skill_id)

    lines = [
        "@startuml",
        f"' Generated from {source}; do not edit by hand.",
        "title Skill Planes Overview",
        "top to bottom direction",
        "skinparam shadowing false",
        "skinparam packageStyle rectangle",
        "skinparam ArrowColor #475569",
        "skinparam rectangle {",
        "  BackgroundColor #F8FAFC",
        "  BorderColor #475569",
        "}",
        "",
    ]
    for category, label in PLANE_ORDER:
        members = by_category.get(category, [])
        if not members:
            continue
        stereotype = " <<kernel>>" if category == "workflow" else ""
        lines.append(f'package "{label}" as {alias("plane_" + category)}{stereotype} {{')
        for skill_id in members:
            lines.append(f'  rectangle "{skill_id}" as {alias(skill_id)}')
        lines.append("}")
        lines.append("")

    kernel_alias = alias("plane_workflow")
    visible_categories = [category for category, _label in PLANE_ORDER if by_category.get(category)]
    for previous, current in zip(visible_categories, visible_categories[1:]):
        lines.append(f"{alias('plane_' + previous)} -[hidden]-> {alias('plane_' + current)}")
    lines.append("")
    for category in visible_categories[1:]:
        lines.append(f"{kernel_alias} ..> {alias('plane_' + category)} : composes")

    lines.extend(
        [
            "",
            "note as ownership_note",
            "  Only workflow skills own lifecycle state.",
            "  Lower planes contribute methods, evidence, or policy.",
            "end note",
            "",
            "legend right",
            "  kernel = top-level lifecycle authority",
            "  review components = read-only evaluators",
            "  manual tools = explicit user request only",
            "  internal runtime support is intentionally omitted",
            "endlegend",
            "@enduml",
            "",
        ]
    )
    return "\n".join(lines)


ACTIVATION_ORDER = ["native", "conditional", "controller", "explicit", "baseline"]


def render_skill_trigger_ownership(
    skills: dict[str, Any],
    routing_path: Path,
    routing: dict[str, Any],
) -> str:
    skill_source = SKILLS_CONTRACT.relative_to(REPO_ROOT).as_posix()
    routing_source = routing_path.relative_to(REPO_ROOT).as_posix()
    by_mode: dict[str, list[tuple[str, dict[str, Any]]]] = {
        mode: [] for mode in ACTIVATION_ORDER
    }
    for skill_id, entry in sorted(skills.items()):
        mode = entry.get("activation_mode")
        if mode in by_mode:
            by_mode[mode].append((skill_id, entry))

    lines = [
        "@startuml",
        f"' Generated from {skill_source} and {routing_source}; do not edit by hand.",
        "title Skill Activation And Trigger Ownership",
        "left to right direction",
        "skinparam shadowing false",
        "skinparam packageStyle rectangle",
        "skinparam ArrowColor #475569",
        "skinparam rectangle {",
        "  BackgroundColor #F8FAFC",
        "  BorderColor #475569",
        "}",
        "",
    ]

    for mode in ACTIVATION_ORDER:
        members = by_mode[mode]
        lines.append(f'package "Activation: {mode}" as {alias("activation_" + mode)} {{')
        for skill_id, entry in members:
            role = entry.get("default_role", "unknown")
            compatibility = "\\n(compatibility)" if entry.get("superseded_by") else ""
            stereotype = " <<compatibility>>" if entry.get("superseded_by") else ""
            lines.append(
                f'  rectangle "{skill_id}\\n[{role}]{compatibility}" as '
                f'{alias("skill_" + skill_id)}{stereotype}'
            )
        lines.append("}")
        lines.append("")

    lines.append(f'package "Semantic trigger cases" as {alias("trigger_cases")} {{')
    for trigger_case in routing.get("trigger_cases", []):
        case_id = trigger_case["id"]
        lines.append(
            f'  rectangle "{case_id}" as {alias("case_" + case_id)} <<case>>'
        )
    lines.append("}")
    lines.append("")

    for trigger_case in routing.get("trigger_cases", []):
        case_id = trigger_case["id"]
        owner = trigger_case["owner"]
        lines.append(
            f'{alias("case_" + case_id)} --> {alias("skill_" + owner)} : case owner'
        )
        for overlay in trigger_case.get("overlays", []):
            lines.append(
                f'{alias("case_" + case_id)} ..> {alias("skill_" + overlay)} : overlay'
            )

    for skill_id, entry in sorted(skills.items()):
        successor = entry.get("superseded_by")
        if successor:
            lines.append(
                f'{alias("skill_" + skill_id)} ..> {alias("skill_" + successor)} : superseded_by'
            )

    review_evaluators = routing.get("review_evaluators", {})
    evaluator_phases: dict[str, list[str]] = {}
    if isinstance(review_evaluators, dict):
        for phase, evaluator in review_evaluators.items():
            evaluator_phases.setdefault(evaluator, []).append(phase)
    for evaluator, phases in sorted(evaluator_phases.items()):
        lines.append(
            f'{alias("skill_review-change")} --> {alias("skill_" + evaluator)} : '
            f'controller evaluator\\n{", ".join(sorted(phases))}'
        )

    phase_routes = routing.get("phase_routes", {})
    controller_phases: dict[str, list[str]] = {}
    if isinstance(phase_routes, dict):
        for phase, target in phase_routes.items():
            if skills.get(target, {}).get("activation_mode") == "controller":
                controller_phases.setdefault(target, []).append(phase)
    if controller_phases:
        lines.append(
            f'rectangle "Controller phase routes" as {alias("controller_routes")} <<controller>>'
        )
        for target, phases in sorted(controller_phases.items()):
            lines.append(
                f'{alias("controller_routes")} --> {alias("skill_" + target)} : '
                f'{", ".join(sorted(phases))}'
            )

    baseline = routing.get("composition", {}).get("rendering_baseline")
    if baseline:
        lines.extend(
            [
                f'rectangle "Response composition" as {alias("response_composition")}',
                f'{alias("response_composition")} ..> {alias("skill_" + baseline)} : rendering baseline',
            ]
        )

    lines.extend(
        [
            "",
            "legend right",
            "  solid case edge = one semantic case owner",
            "  dotted overlay edge = conditional composition",
            "  compatibility = explicit public handoff retained",
            "  lexical hints are intentionally not rendered as routing logic",
            "endlegend",
            "@enduml",
            "",
        ]
    )
    return "\n".join(lines)


def render_svg(puml_content: str) -> str:
    plantuml = shutil.which("plantuml")
    if not plantuml:
        raise RuntimeError("plantuml not found on PATH; install it to render tracked SVG views")
    result = subprocess.run(
        [plantuml, "-tsvg", "-charset", "UTF-8", "-pipe"],
        input=puml_content.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"plantuml SVG render failed: {result.stderr.decode('utf-8', 'replace')}")
    return result.stdout.decode("utf-8")


def svg_path_for(puml_path: Path) -> Path:
    return GENERATED_DIR / (puml_path.stem + ".svg")


def expected_outputs() -> dict[Path, str]:
    contract_path, contract = controller_contract()
    routing_path, routing = routing_contract()
    lifecycle = load_toml(LIFECYCLE_CONTRACT)
    workflow_modes = load_toml(WORKFLOW_MODES_CONTRACT)
    skills = load_toml(SKILLS_CONTRACT)["skills"]
    return {
        ROUTING_SEQUENCE_PATH: render_routing_sequence(
            routing_path,
            routing,
            lifecycle,
            workflow_modes,
        ),
        DAG_PATH: render_dag(contract_path, contract),
        REPAIR_PATH: render_repair_loop(contract_path, contract),
        SKILL_PLANES_PATH: render_skill_planes(skills),
        TRIGGER_OWNERSHIP_PATH: render_skill_trigger_ownership(
            skills,
            routing_path,
            routing,
        ),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when generated diagrams are stale")
    args = parser.parse_args(argv)

    try:
        outputs = expected_outputs()
    except (KeyError, OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"workflow diagram generation failed: {exc}", file=sys.stderr)
        return 1

    if args.check:
        stale = [path for path, expected in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != expected]
        if shutil.which("plantuml"):
            for path, expected in outputs.items():
                svg_path = svg_path_for(path)
                try:
                    expected_svg = render_svg(expected)
                except RuntimeError as exc:
                    print(f"workflow diagram check failed: {exc}", file=sys.stderr)
                    return 1
                if not svg_path.is_file() or svg_path.read_text(encoding="utf-8") != expected_svg:
                    stale.append(svg_path)
        else:
            missing_svg = [svg_path_for(path) for path in outputs if not svg_path_for(path).is_file()]
            if missing_svg:
                for svg_path in missing_svg:
                    print(f"missing rendered diagram: {svg_path.relative_to(REPO_ROOT)}", file=sys.stderr)
                stale.extend(missing_svg)
            else:
                print("warning: plantuml not found; SVG freshness not verified", file=sys.stderr)
        if stale:
            for path in stale:
                print(f"stale workflow diagram: {path.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
        print("workflow diagrams ok")
        return 0

    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    if not shutil.which("plantuml"):
        print(
            "plantuml not found on PATH; install it to render tracked SVG views",
            file=sys.stderr,
        )
        return 1
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
        try:
            svg_path_for(path).write_text(render_svg(content), encoding="utf-8")
        except RuntimeError as exc:
            print(f"workflow diagram generation failed: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
