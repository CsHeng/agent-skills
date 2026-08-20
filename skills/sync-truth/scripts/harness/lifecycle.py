"""Contract-derived request classification and lifecycle phase transitions."""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping
from pathlib import Path

from .artifacts import HarnessError

RESOURCE_NAME = "lifecycle-contracts.json"


def _load_toml(path: Path) -> dict[str, object]:
    try:
        with path.open("rb") as handle:
            value = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise HarnessError(
            "lifecycle-contract-unavailable", f"cannot load lifecycle contract: {path}"
        ) from error
    return value


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise HarnessError("invalid-lifecycle-contract", f"{field} must be an object")
    return value


def normalize_lifecycle_sources(
    lifecycle_path: Path, workflow_modes_path: Path, routing_path: Path
) -> dict[str, object]:
    """Project the minimum runtime authority from the three canonical TOML sources."""
    lifecycle = _load_toml(lifecycle_path)
    workflow_modes = _load_toml(workflow_modes_path)
    routing = _load_toml(routing_path)
    lifecycle_table = _mapping(lifecycle.get("lifecycle"), "lifecycle")
    return {
        "schema_version": 1,
        "kernel": lifecycle_table.get("kernel"),
        "mode_signals": _mapping(lifecycle.get("routing"), "routing"),
        "modes": _mapping(workflow_modes.get("modes"), "modes"),
        "gate_policy": _mapping(routing.get("gate_policy"), "gate_policy"),
        "phase_routes": _mapping(routing.get("phase_routes"), "phase_routes"),
        "review_evaluators": _mapping(
            routing.get("review_evaluators"), "review_evaluators"
        ),
    }


def _validate_contracts(value: object) -> dict[str, object]:
    contracts = _mapping(value, "lifecycle contracts")
    if contracts.get("schema_version") != 1:
        raise HarnessError("invalid-lifecycle-contract", "unsupported lifecycle schema")
    kernel = contracts.get("kernel")
    if not isinstance(kernel, list) or not kernel or not all(
        isinstance(item, str) and item for item in kernel
    ):
        raise HarnessError("invalid-lifecycle-contract", "kernel must be a string array")
    for field in (
        "mode_signals",
        "modes",
        "gate_policy",
        "phase_routes",
        "review_evaluators",
    ):
        _mapping(contracts.get(field), field)
    return contracts


def load_lifecycle_contracts(resource_root: Path | None = None) -> dict[str, object]:
    """Load standalone normalized resources or normalize canonical repository sources."""
    resources = resource_root or Path(__file__).resolve().parent / "resources"
    resource = resources / RESOURCE_NAME
    if resource.is_file() and not resource.is_symlink():
        try:
            value = json.loads(resource.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise HarnessError(
                "invalid-lifecycle-contract", "normalized lifecycle resource is invalid"
            ) from error
        return _validate_contracts(value)
    if resource_root is not None:
        raise HarnessError(
            "lifecycle-contract-unavailable", "standalone lifecycle resource is missing"
        )
    repository = Path(__file__).resolve().parents[3]
    return _validate_contracts(
        normalize_lifecycle_sources(
            repository / "contracts" / "lifecycle.toml",
            repository / "contracts" / "workflow-modes.toml",
            repository
            / "src"
            / "skills"
            / "session"
            / "use-coding-skills"
            / "references"
            / "routing.toml",
        )
    )


def _exact_request(request: Mapping[str, object], expected: set[str]) -> None:
    if set(request) != expected:
        raise HarnessError("invalid-lifecycle-request", "lifecycle request schema is not exact")


def classify_request(
    request: Mapping[str, object], contracts: Mapping[str, object] | None = None
) -> dict[str, object]:
    """Classify typed signals into exactly one canonical workflow mode."""
    _exact_request(request, {"signals", "repo_mutation"})
    signals = request.get("signals")
    mutation = request.get("repo_mutation")
    if (
        not isinstance(signals, list)
        or not signals
        or not all(isinstance(item, str) and item for item in signals)
        or len(signals) != len(set(signals))
        or not isinstance(mutation, bool)
    ):
        raise HarnessError("invalid-lifecycle-request", "typed request fields are invalid")
    active = (
        _validate_contracts(dict(contracts))
        if contracts is not None
        else load_lifecycle_contracts()
    )
    mode_signals = _mapping(active.get("mode_signals"), "mode_signals")
    signal_owners: dict[str, str] = {}
    for mode, values in mode_signals.items():
        if not isinstance(mode, str) or not isinstance(values, list) or not all(
            isinstance(item, str) for item in values
        ):
            raise HarnessError("invalid-lifecycle-contract", "mode signals are malformed")
        for signal in values:
            if signal in signal_owners:
                raise HarnessError(
                    "invalid-lifecycle-contract", "one signal is owned by multiple modes"
                )
            signal_owners[signal] = mode
    unknown = [signal for signal in signals if signal not in signal_owners]
    if unknown:
        raise HarnessError(
            "lifecycle-request-unknown", f"request signals are unknown: {unknown}"
        )
    matched = {signal_owners[signal] for signal in signals}
    if len(matched) != 1:
        raise HarnessError(
            "lifecycle-request-contradictory", "request signals select multiple modes"
        )
    mode = matched.pop()
    modes = _mapping(active.get("modes"), "modes")
    mode_contract = _mapping(modes.get(mode), f"modes.{mode}")
    if mode_contract.get("allows_repo_mutation") is not mutation:
        raise HarnessError(
            "lifecycle-request-contradictory", "request mutation intent disagrees with mode"
        )
    phases = mode_contract.get("phases")
    if not isinstance(phases, list) or not phases or not all(
        isinstance(phase, str) and phase for phase in phases
    ):
        raise HarnessError("invalid-lifecycle-contract", "mode phases are malformed")
    initial = phases[0]
    routes = _mapping(active.get("phase_routes"), "phase_routes")
    owner = routes.get(initial)
    if not isinstance(owner, str) or not owner:
        raise HarnessError("invalid-lifecycle-contract", "initial phase owner is missing")
    return {"mode": mode, "initial_phase": initial, "owner": owner}


def _approval_phases(
    gate_policy: Mapping[str, object], mode_phases: list[object]
) -> set[str]:
    phases: set[str] = set()
    for phase_field, review_field in (
        ("design_phases", "design_review_phase"),
        ("plan_phases", "plan_review_phase"),
    ):
        values = gate_policy.get(phase_field)
        review_phase = gate_policy.get(review_field)
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise HarnessError("invalid-lifecycle-contract", f"{phase_field} is malformed")
        if not isinstance(review_phase, str) or not review_phase:
            raise HarnessError("invalid-lifecycle-contract", f"{review_field} is malformed")
        if review_phase in mode_phases:
            phases.add(review_phase)
        else:
            phases.update(value for value in values if value in mode_phases)
    for field in ("truth_sync_phase", "close_phase"):
        value = gate_policy.get(field)
        if not isinstance(value, str) or not value:
            raise HarnessError("invalid-lifecycle-contract", f"{field} is malformed")
        phases.add(value)
    return phases


def next_phase(
    request: Mapping[str, object], contracts: Mapping[str, object] | None = None
) -> dict[str, object]:
    """Return one next phase or typed terminal stop from the selected mode contract."""
    _exact_request(
        request, {"mode", "current_phase", "phase_complete", "approval_granted"}
    )
    mode = request.get("mode")
    current = request.get("current_phase")
    complete = request.get("phase_complete")
    approved = request.get("approval_granted")
    if (
        not isinstance(mode, str)
        or not isinstance(current, str)
        or not isinstance(complete, bool)
        or not isinstance(approved, bool)
    ):
        raise HarnessError("invalid-lifecycle-request", "phase request fields are invalid")
    active = (
        _validate_contracts(dict(contracts))
        if contracts is not None
        else load_lifecycle_contracts()
    )
    modes = _mapping(active.get("modes"), "modes")
    if mode not in modes:
        raise HarnessError("invalid-lifecycle-transition", f"unknown workflow mode: {mode}")
    mode_contract = _mapping(modes[mode], f"modes.{mode}")
    phases = mode_contract.get("phases")
    if not isinstance(phases, list) or current not in phases:
        raise HarnessError(
            "invalid-lifecycle-transition", "current phase does not belong to the mode"
        )
    if not complete:
        return {"state": "stopped", "code": "phase-evidence-required", "phase": current}
    gate_policy = _mapping(active.get("gate_policy"), "gate_policy")
    if current in _approval_phases(gate_policy, phases) and not approved:
        return {"state": "stopped", "code": "approval-required", "phase": current}
    current_index = phases.index(current)
    if current_index == len(phases) - 1:
        terminal = "closed" if current == gate_policy.get("close_phase") else "complete"
        return {"state": "terminal", "phase": terminal, "owner": None}
    following = phases[current_index + 1]
    routes = _mapping(active.get("phase_routes"), "phase_routes")
    owner = routes.get(following)
    if not isinstance(owner, str) or not owner:
        raise HarnessError("invalid-lifecycle-contract", "next phase owner is missing")
    return {"state": "next", "phase": following, "owner": owner}
