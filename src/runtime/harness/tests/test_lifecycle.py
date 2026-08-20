"""Deterministic lifecycle classification and phase-transition tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from runtime.harness.artifacts import HarnessError
from runtime.harness.lifecycle import (
    classify_request,
    load_lifecycle_contracts,
    next_phase,
)

ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "runtime" / "harness" / "cli.py"


def test_classification_is_derived_from_canonical_mode_signals() -> None:
    contracts = load_lifecycle_contracts()

    assert classify_request(
        {"signals": ["ordinary feature"], "repo_mutation": True}, contracts
    ) == {"mode": "standard", "initial_phase": "analyze", "owner": "analyze-project"}
    assert classify_request(
        {"signals": ["explanation"], "repo_mutation": False}, contracts
    ) == {"mode": "read_only", "initial_phase": "analyze", "owner": "analyze-project"}


@pytest.mark.parametrize(
    ("input_value", "code"),
    [
        (
            {"signals": ["typo", "infra"], "repo_mutation": True},
            "lifecycle-request-contradictory",
        ),
        ({"signals": ["unknown-signal"], "repo_mutation": True}, "lifecycle-request-unknown"),
        (
            {"signals": ["repo inspection"], "repo_mutation": True},
            "lifecycle-request-contradictory",
        ),
    ],
)
def test_classification_rejects_unknown_or_contradictory_requests(
    input_value: dict[str, object], code: str
) -> None:
    with pytest.raises(HarnessError) as captured:
        classify_request(input_value)

    assert captured.value.code == code


def test_phase_transition_requires_completion_and_human_gate_evidence() -> None:
    assert next_phase(
        {
            "mode": "standard",
            "current_phase": "analyze",
            "phase_complete": True,
            "approval_granted": False,
        }
    ) == {"state": "next", "phase": "design-lite", "owner": "design-change"}
    assert next_phase(
        {
            "mode": "standard",
            "current_phase": "design-lite",
            "phase_complete": True,
            "approval_granted": False,
        }
    ) == {"state": "stopped", "code": "approval-required", "phase": "design-lite"}
    assert next_phase(
        {
            "mode": "standard",
            "current_phase": "design-lite",
            "phase_complete": True,
            "approval_granted": True,
        }
    ) == {"state": "next", "phase": "plan", "owner": "plan-change"}
    assert next_phase(
        {
            "mode": "standard",
            "current_phase": "execute",
            "phase_complete": False,
            "approval_granted": False,
        }
    ) == {"state": "stopped", "code": "phase-evidence-required", "phase": "execute"}


def test_regulated_approval_follows_mandatory_design_and_plan_review() -> None:
    assert next_phase(
        {
            "mode": "regulated",
            "current_phase": "design-full",
            "phase_complete": True,
            "approval_granted": False,
        }
    ) == {"state": "next", "phase": "review-design", "owner": "review-change"}
    assert next_phase(
        {
            "mode": "regulated",
            "current_phase": "review-design",
            "phase_complete": True,
            "approval_granted": False,
        }
    ) == {"state": "stopped", "code": "approval-required", "phase": "review-design"}
    assert next_phase(
        {
            "mode": "regulated",
            "current_phase": "review-design",
            "phase_complete": True,
            "approval_granted": True,
        }
    ) == {"state": "next", "phase": "plan", "owner": "plan-change"}
    assert next_phase(
        {
            "mode": "regulated",
            "current_phase": "plan",
            "phase_complete": True,
            "approval_granted": False,
        }
    ) == {"state": "next", "phase": "review-plan", "owner": "review-change"}
    assert next_phase(
        {
            "mode": "regulated",
            "current_phase": "review-plan",
            "phase_complete": True,
            "approval_granted": False,
        }
    ) == {"state": "stopped", "code": "approval-required", "phase": "review-plan"}


def test_close_returns_one_terminal_state() -> None:
    assert next_phase(
        {
            "mode": "micro",
            "current_phase": "close",
            "phase_complete": True,
            "approval_granted": True,
        }
    ) == {"state": "terminal", "phase": "closed", "owner": None}


def test_source_and_copied_resources_normalize_to_the_same_contract(tmp_path: Path) -> None:
    source = load_lifecycle_contracts()
    resource_root = tmp_path / "resources"
    resource_root.mkdir()
    (resource_root / "lifecycle-contracts.json").write_text(
        json.dumps(source, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    assert load_lifecycle_contracts(resource_root) == source


def test_cli_exposes_complete_classify_and_next_operations(tmp_path: Path) -> None:
    classify = tmp_path / "classify.json"
    classify.write_text(
        json.dumps({"signals": ["ordinary fix"], "repo_mutation": True}),
        encoding="utf-8",
    )
    classified = subprocess.run(
        [sys.executable, str(CLI), "lifecycle", "classify", str(classify)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert classified.returncode == 0, classified.stderr
    assert json.loads(classified.stdout)["classification"]["mode"] == "standard"

    transition = tmp_path / "transition.json"
    transition.write_text(
        json.dumps(
            {
                "mode": "standard",
                "current_phase": "analyze",
                "phase_complete": True,
                "approval_granted": False,
            }
        ),
        encoding="utf-8",
    )
    advanced = subprocess.run(
        [sys.executable, str(CLI), "lifecycle", "next", str(transition)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert advanced.returncode == 0, advanced.stderr
    assert json.loads(advanced.stdout)["transition"]["phase"] == "design-lite"
