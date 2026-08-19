"""Retain HSC-010 legacy characterization as immutable fixture evidence.

The Shell owners were intentionally deleted by HSC-050. These tests prove the
captured matrix and Herdr-v1 literal hashes remain reviewable without reading a
deleted source path or attempting a compatibility replay.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"
EXPECTED_SMOKE_SUITES = {
    "test-artifact-dag.sh",
    "test-close-runner.sh",
    "test-design-runner.sh",
    "test-execute-runner.sh",
    "test-kernel-contracts.sh",
    "test-kernel-phase.sh",
    "test-kernel-routing.sh",
    "test-plan-runner.sh",
    "test-recovery-routing.sh",
    "test-sovereign-skill-surface.sh",
    "test-task-ledger.sh",
    "test-truth-sync-runner.sh",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_legacy_owner_matrix_is_complete_retained_evidence() -> None:
    matrix = read_json(FIXTURE_DIR / "legacy_harness_owner_matrix.json")
    assert matrix["schema_version"] == 1
    suites = matrix["suites"]
    assert isinstance(suites, list)
    assert {
        row["smoke_suite"]
        for row in suites
        if isinstance(row, dict) and isinstance(row.get("smoke_suite"), str)
    } == EXPECTED_SMOKE_SUITES
    for row in suites:
        assert isinstance(row, dict)
        assert all(
            isinstance(row.get(field), str) and row[field]
            for field in ("smoke_suite", "assertion_owner", "valid_fixture", "invalid_fixture")
        )


def test_legacy_herdr_v1_hashes_are_retained_evidence() -> None:
    fixture = read_json(FIXTURE_DIR / "legacy_herdr_schema_v1.json")
    assert fixture["schema_version"] == 1
    templates = fixture["golden_envelopes"]
    assert isinstance(templates, dict) and templates
    assert len(templates) == 9
    assert all(
        isinstance(name, str) and SHA256.fullmatch(value or "") for name, value in templates.items()
    )
