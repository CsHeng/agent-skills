"""State, digest, atomicity, and authority tests for the version-4 task ledger."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.harness import ledger as ledger_module
from runtime.harness.artifacts import HarnessError, compile_plan, parse_artifact
from runtime.harness.external_touch import (
    apply_and_cleanup_intent,
    capture_baseline,
    declare_intent,
    finalize_intent,
    stage_declared_payload,
)
from runtime.harness.ledger import (
    Ledger,
    admit_ready,
    assert_task_touch_set,
    close_decision,
    initialize_ledger,
    read_ledger,
    ready_set,
    record_external_evidence,
    record_review,
    record_verification,
    recovery_route,
    transition,
    truth_sync_decision,
    write_ledger,
)
from runtime.harness.tests.test_v3_artifacts import write_valid_pair as write_v3_pair
from runtime.harness.tests.test_v4_artifacts import (
    design_text,
    digest,
    plan_text,
    task_text,
    write_pair,
)

VERIFICATION_COMMAND = "uv run pytest tests"


def write_two_task_plan(tmp_path: Path) -> Path:
    """Build a serial version-4 dependency chain."""
    tasks = "\n\n".join(
        (
            task_text(
                "V4-010",
                impl_refs='["src/runtime/harness/artifacts.py"]',
                test_refs='["tests/test_artifacts.py"]',
            ),
            task_text(
                "V4-020",
                depends_on='["V4-010"]',
                impl_refs='["src/runtime/harness/ledger.py"]',
                test_refs='["tests/test_ledger.py"]',
            ),
        )
    )
    _, plan = write_pair(tmp_path, task_tables=tasks)
    return plan


def converge_first_task(ledger: Ledger) -> Ledger:
    """Advance the first task through required verification and review gates."""
    value = admit_ready(ledger, ("V4-010",), capacity=1)
    value = record_verification(value, "V4-010", VERIFICATION_COMMAND, True)
    value = transition(value, "V4-010", "verified")
    value = record_review(value, "V4-010", True, "review-1")
    value = transition(value, "V4-010", "reviewed")
    return transition(value, "V4-010", "converged")


def converged_v3_ledger(tmp_path: Path) -> Ledger:
    """Create immutable already-converged version-3 compatibility evidence."""
    tmp_path.mkdir()
    design, plan = write_v3_pair(tmp_path)
    compiled = compile_plan(plan)
    tasks: list[dict[str, object]] = []
    projected_tasks = compiled.projection["tasks"]
    assert isinstance(projected_tasks, list)
    for projected in projected_tasks:
        assert isinstance(projected, dict)
        tasks.append(
            {
                **projected,
                "status": "converged",
                "verification_evidence": [],
                "review": {"batch_id": "legacy-review", "status": "accepted"},
                "review_history": [],
                "external_evidence": [],
                "repair_attempts": 0,
                "batch_provenance": None,
                "attempt_history": [],
            }
        )
    return Ledger(
        {
            "ledger_version": 3,
            "plan_ref": str(plan),
            "design_ref": str(design),
            "plan_sha256": compiled.plan.sha256,
            "design_sha256": compiled.design.sha256,
            "projection": compiled.projection,
            "projection_sha256": compiled.projection_sha256,
            "tasks": tasks,
            "lifecycle_state": "task-complete",
        }
    )


def write_gate_artifact(tmp_path: Path, kind: str, version: int) -> Path:
    """Write one structurally valid gate artifact for version-matrix tests."""
    artifact = tmp_path / f"{kind}-v{version}.md"
    if kind == "truth-sync":
        metadata = (
            'execution_result_ref = "execution-result.json"',
            f'execution_result_sha256 = "{"a" * 64}"',
            'ledger_ref = "ledger.json"',
            f'ledger_sha256 = "{"b" * 64}"',
            'approval_status = "approved"',
        )
        headings = ["# Truth Sync", "", "## Scope"]
        if version == 4:
            headings.extend(
                ["", "## Evidence", "", "## Stable Truth Updates", "", "## Human Gate"]
            )
    else:
        metadata = (
            'truth_sync_ref = "truth-sync.md"',
            f'truth_sync_sha256 = "{"c" * 64}"',
            'decision = "ready-for-close"',
            'approval_status = "approved"',
        )
        headings = ["# Close", "", "## Decision"]
    artifact.write_text(
        "\n".join(
            (
                "+++",
                f'artifact_kind = "{kind}"',
                f"contract_version = {version}",
                *metadata,
                "",
                "[scope]",
                "impl_file_refs = []",
                "test_file_refs = []",
                "external_impl_file_refs = []",
                "+++",
                *headings,
                "",
            )
        ),
        encoding="utf-8",
    )
    return artifact


@pytest.mark.parametrize("kind", ["truth-sync", "close"])
@pytest.mark.parametrize(
    ("ledger_version", "artifact_version"), [(4, 3), (3, 4)]
)
def test_gate_artifact_version_must_match_ledger_authority(
    tmp_path: Path, kind: str, ledger_version: int, artifact_version: int
) -> None:
    """Neither compatibility direction may cross artifact and ledger authority versions."""
    if ledger_version == 4:
        v4_root = tmp_path / "v4"
        v4_root.mkdir()
        _, plan = write_pair(v4_root)
        ledger = converge_first_task(initialize_ledger(plan))
    else:
        ledger = converged_v3_ledger(tmp_path / "v3")
    artifact = parse_artifact(write_gate_artifact(tmp_path, kind, artifact_version))

    with pytest.raises(HarnessError) as captured:
        if kind == "truth-sync":
            truth_sync_decision(ledger, artifact, tmp_path / "ledger.json")
        else:
            close_decision(ledger, artifact, tmp_path / "ledger.json")

    assert captured.value.code == "artifact-contract-version-mismatch"


def test_same_version_v3_truth_sync_and_close_tail_remains_available(tmp_path: Path) -> None:
    """Already-converged v3 evidence may finish only its same-version lifecycle tail."""
    ledger = converged_v3_ledger(tmp_path / "v3")
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_bytes(ledger_module._canonical(ledger.data))
    execution_result = tmp_path / "execution-result.json"
    execution_result.write_text(
        json.dumps(
            {
                "status": "passed",
                "review_status": "passed",
                "verification_status": "passed",
                "plan_sha256": ledger.data["plan_sha256"],
                "design_sha256": ledger.data["design_sha256"],
                "projection_sha256": ledger.data["projection_sha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    truth_path = tmp_path / "truth-sync.md"
    truth_path.write_text(
        "\n".join(
            (
                "+++",
                'artifact_kind = "truth-sync"',
                "contract_version = 3",
                'execution_result_ref = "execution-result.json"',
                f'execution_result_sha256 = "{ledger_module._sha256_path(execution_result)}"',
                'ledger_ref = "ledger.json"',
                f'ledger_sha256 = "{ledger_module._sha256_path(ledger_path)}"',
                'approval_status = "approved"',
                "",
                "[scope]",
                'impl_file_refs = ["README.md"]',
                "test_file_refs = []",
                "external_impl_file_refs = []",
                "+++",
                "# Truth Sync",
                "",
                "## Scope",
                "",
            )
        ),
        encoding="utf-8",
    )
    truth = parse_artifact(truth_path)
    assert truth_sync_decision(ledger, truth, ledger_path) == "ready-for-close"

    close_path = tmp_path / "close.md"
    close_path.write_text(
        "\n".join(
            (
                "+++",
                'artifact_kind = "close"',
                "contract_version = 3",
                'truth_sync_ref = "truth-sync.md"',
                f'truth_sync_sha256 = "{ledger_module._sha256_path(truth_path)}"',
                'decision = "ready-for-close"',
                'approval_status = "approved"',
                "",
                "[scope]",
                "impl_file_refs = []",
                "test_file_refs = []",
                "external_impl_file_refs = []",
                "+++",
                "# Close",
                "",
                "## Decision",
                "",
            )
        ),
        encoding="utf-8",
    )
    assert close_decision(ledger, parse_artifact(close_path), ledger_path) == "closed"


def test_initialization_compiles_once_and_later_transition_is_digest_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Only initialization compiles artifacts; later changes validate stored byte digests."""
    ledger = initialize_ledger(write_two_task_plan(tmp_path))
    assert ready_set(ledger) == ("V4-010",)

    def fail_compile(_: Path) -> Ledger:
        raise AssertionError("transition must not parse or compile the plan")

    monkeypatch.setattr(ledger_module, "compile_plan", fail_compile)
    advanced = admit_ready(ledger, ("V4-010",), capacity=1)

    tasks = advanced.data["tasks"]
    assert isinstance(tasks, list) and isinstance(tasks[0], dict)
    assert tasks[0]["status"] == "in-progress"


def test_initialization_uses_cwd_relative_artifact_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    design, plan = write_pair(tmp_path)
    monkeypatch.chdir(tmp_path)

    ledger = initialize_ledger(plan)

    assert ledger.data["plan_ref"] == "plan.md"
    assert ledger.data["design_ref"] == "design.md"
    assert ready_set(ledger) == ("V4-010",)


def test_transitions_refresh_ready_set_and_gate_truth_sync_and_close(tmp_path: Path) -> None:
    """Task convergence unlocks dependents and the explicit truth/close gates."""
    ledger = converge_first_task(initialize_ledger(write_two_task_plan(tmp_path)))
    assert ready_set(ledger) == ("V4-020",)
    value = admit_ready(ledger, ("V4-020",), capacity=1)
    value = record_verification(value, "V4-020", VERIFICATION_COMMAND, True)
    value = transition(value, "V4-020", "verified")
    value = record_review(value, "V4-020", True, "review-2")
    value = transition(value, "V4-020", "reviewed")
    value = transition(value, "V4-020", "converged")
    assert truth_sync_decision(value, None) == "truth-sync-pending"


def test_digest_drift_and_invalid_transition_fail_closed(tmp_path: Path) -> None:
    """Artifact drift and skipped lifecycle gates never advance authority."""
    plan = write_two_task_plan(tmp_path)
    ledger = initialize_ledger(plan)
    with pytest.raises(HarnessError) as skipped:
        transition(ledger, "V4-010", "verified")
    assert skipped.value.code == "invalid-transition"
    plan.write_text(f"{plan.read_text(encoding='utf-8')}\n", encoding="utf-8")
    with pytest.raises(HarnessError) as drift:
        admit_ready(ledger, ("V4-010",), capacity=1)
    assert drift.value.code == "artifact-digest-drift"


@pytest.mark.parametrize("artifact", ["design", "plan"])
def test_ledger_initialization_requires_approved_design_and_plan(
    tmp_path: Path, artifact: str
) -> None:
    design, plan = write_pair(tmp_path)
    original_design_sha256 = digest(design.read_bytes())
    target = design if artifact == "design" else plan
    target.write_text(
        target.read_text(encoding="utf-8").replace(
            'approval_status = "approved"', 'approval_status = "pending"'
        ),
        encoding="utf-8",
    )
    if artifact == "design":
        plan.write_text(
            plan.read_text(encoding="utf-8").replace(
                original_design_sha256, digest(design.read_bytes())
            ),
            encoding="utf-8",
        )

    with pytest.raises(HarnessError) as stopped:
        initialize_ledger(plan)

    assert stopped.value.code == "artifact-not-approved"


def test_rejected_review_invalidates_evidence_and_requires_active_attempt(
    tmp_path: Path,
) -> None:
    ledger = initialize_ledger(write_two_task_plan(tmp_path))
    with pytest.raises(HarnessError) as premature:
        record_verification(ledger, "V4-010", VERIFICATION_COMMAND, True)
    assert premature.value.code == "verification-not-ready"
    active = admit_ready(ledger, ("V4-010",), capacity=1)
    verified = record_verification(active, "V4-010", VERIFICATION_COMMAND, True)
    verified = transition(verified, "V4-010", "verified")
    repairing = record_review(verified, "V4-010", False, "review-rejected")
    tasks = repairing.data["tasks"]
    assert isinstance(tasks, list) and isinstance(tasks[0], dict)
    task = tasks[0]
    assert task["status"] == "ready"
    assert task["repair_attempts"] == 1
    assert task["verification_evidence"] == []
    assert task["review"] is None
    with pytest.raises(HarnessError) as stale:
        transition(repairing, "V4-010", "verified")
    assert stale.value.code == "invalid-transition"


def test_non_truth_close_binds_directly_to_ledger_and_execution_result(tmp_path: Path) -> None:
    design, plan = write_pair(tmp_path)
    design_payload = design_text(truth_impact="low", truth_sync_required=False).encode()
    design.write_bytes(design_payload)
    plan.write_text(
        plan_text(
            digest(design_payload), truth_sync_required=False, stable_truth_refs="[]"
        ),
        encoding="utf-8",
    )
    ledger = converge_first_task(initialize_ledger(plan))
    ledger_path = tmp_path / "ledger.json"
    write_ledger(ledger_path, ledger)
    result = tmp_path / "execution-result.json"
    result.write_text(
        json.dumps(
            {
                "status": "passed",
                "review_status": "passed",
                "verification_status": "passed",
                "plan_sha256": ledger.data["plan_sha256"],
                "design_sha256": ledger.data["design_sha256"],
                "projection_sha256": ledger.data["projection_sha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    close_path = tmp_path / "close.md"
    close_path.write_text(
        "\n".join(
            (
                "+++",
                'artifact_kind = "close"',
                "contract_version = 4",
                'ledger_ref = "ledger.json"',
                f'ledger_sha256 = "{ledger_module._sha256_path(ledger_path)}"',
                'execution_result_ref = "execution-result.json"',
                f'execution_result_sha256 = "{ledger_module._sha256_path(result)}"',
                'decision = "ready-for-close"',
                'approval_status = "approved"',
                "",
                "[scope]",
                "impl_file_refs = []",
                "test_file_refs = []",
                "external_impl_file_refs = []",
                "+++",
                "# Close",
                "",
                "## Decision",
                "",
                "Approved direct close.",
            )
        ),
        encoding="utf-8",
    )

    assert close_decision(ledger, ledger_module.parse_artifact(close_path), ledger_path) == "closed"


def test_atomic_write_preserves_previous_ledger_on_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed atomic replacement retains the last valid ledger bytes."""
    target = tmp_path / "ledger.json"
    target.write_text('{"previous":true}', encoding="utf-8")
    ledger = initialize_ledger(write_two_task_plan(tmp_path))

    def fail_replace(_: Path, __: Path) -> None:
        raise OSError("injected replace failure")

    monkeypatch.setattr(ledger_module.os, "replace", fail_replace)
    with pytest.raises(HarnessError) as failure:
        write_ledger(target, ledger)

    assert failure.value.code == "ledger-write-failed"
    assert target.read_text(encoding="utf-8") == '{"previous":true}'


def test_persisted_ledger_round_trips_and_records_complete_external_evidence(
    tmp_path: Path,
) -> None:
    """Ledger retains a safe summary only after a complete applied and cleaned chain."""
    repo = tmp_path / "repo"
    repo.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    target_file = external / "target.toml"
    target_file.write_text("value = 1\n", encoding="utf-8")
    target_file.chmod(0o600)
    design = repo / "design.md"
    external_ref = f'["{target_file}"]'
    authored_design = design_text().replace(
        "external_impl_file_refs = []", f"external_impl_file_refs = {external_ref}"
    )
    design.write_text(authored_design, encoding="utf-8")
    plan = repo / "plan.md"
    external_task = task_text(
        "V4-010",
        impl_refs='["src/runtime/harness/artifacts.py"]',
        test_refs='["tests/test_runtime.py"]',
        external_refs=external_ref,
    )
    authored_plan = plan_text(
        digest(authored_design.encode()),
        task_tables=external_task,
        external_scope=external_ref,
    )
    plan.write_text(authored_plan, encoding="utf-8")
    ledger = initialize_ledger(plan)
    target = tmp_path / "ledger.json"
    write_ledger(target, ledger)
    persisted = read_ledger(target)
    assert persisted.data["projection_sha256"] == ledger.data["projection_sha256"]
    assert_task_touch_set(persisted, "V4-010", ("src/runtime/harness/artifacts.py",))
    with pytest.raises(HarnessError) as touch:
        assert_task_touch_set(persisted, "V4-010", ("other/unowned.py",))
    assert touch.value.code == "touch-set-violation"
    active = admit_ready(persisted, ("V4-010",), capacity=1)
    baseline = capture_baseline(
        repo_root=repo,
        refs=[str(target_file)],
        run_id="run-1",
        task_id="V4-010",
        design_sha256=str(active.data["design_sha256"]),
        plan_sha256=str(active.data["plan_sha256"]),
    )
    run_dir = external / "run"
    run_dir.mkdir(mode=0o700)
    candidate = external / "candidate.toml"
    candidate.write_text("value = 2\n", encoding="utf-8")
    staging = declare_intent(
        repo_root=repo,
        baseline=baseline,
        intents=[],
        ref=str(target_file),
        intent_id="intent-1",
        run_dir=run_dir,
        source_file=candidate,
    )
    staged = stage_declared_payload(intent=staging, source_file=candidate)
    prepared = finalize_intent(intent=staging, staged_payload=staged)
    applied = apply_and_cleanup_intent(repo_root=repo, intent=prepared)
    recorded = record_external_evidence(active, "V4-010", baseline, [applied])
    tasks = recorded.data["tasks"]
    assert isinstance(tasks, list) and isinstance(tasks[0], dict)
    evidence = tasks[0]["external_evidence"]
    assert isinstance(evidence, list) and evidence[0]["state"] == "valid"
    assert evidence[0]["refs"][0]["ref"] == str(target_file)
    assert "value = 2" not in repr(evidence)
    verified = record_verification(recorded, "V4-010", VERIFICATION_COMMAND, True)
    verified = transition(verified, "V4-010", "verified")
    repairing = record_review(verified, "V4-010", False, "external-review-rejected")
    active_repair = admit_ready(repairing, ("V4-010",), capacity=1)
    refreshed_baseline = capture_baseline(
        repo_root=repo,
        refs=[str(target_file)],
        run_id="run-1",
        task_id="V4-010",
        design_sha256=str(active_repair.data["design_sha256"]),
        plan_sha256=str(active_repair.data["plan_sha256"]),
    )
    with pytest.raises(HarnessError) as forked:
        record_external_evidence(active_repair, "V4-010", refreshed_baseline, [])
    assert forked.value.code == "external-evidence-chain-fork"

    second_candidate = external / "candidate-2.toml"
    second_candidate.write_text("value = 3\n", encoding="utf-8")
    second_staging = declare_intent(
        repo_root=repo,
        baseline=baseline,
        intents=[applied],
        ref=str(target_file),
        intent_id="intent-2",
        run_dir=run_dir,
        source_file=second_candidate,
    )
    second_staged = stage_declared_payload(
        intent=second_staging, source_file=second_candidate
    )
    second_prepared = finalize_intent(
        intent=second_staging, staged_payload=second_staged
    )
    second_applied = apply_and_cleanup_intent(repo_root=repo, intent=second_prepared)
    repaired = record_external_evidence(
        active_repair, "V4-010", baseline, [applied, second_applied]
    )
    repaired_tasks = repaired.data["tasks"]
    assert isinstance(repaired_tasks, list) and isinstance(repaired_tasks[0], dict)
    repaired_evidence = repaired_tasks[0]["external_evidence"]
    assert isinstance(repaired_evidence, list) and isinstance(repaired_evidence[0], dict)
    assert repaired_evidence[0]["refs"][0]["applied_intent_count"] == 2
    verified_repair = record_verification(repaired, "V4-010", VERIFICATION_COMMAND, True)
    verified_repair = transition(verified_repair, "V4-010", "verified")
    reviewed = record_review(verified_repair, "V4-010", True, "external-review-accepted")
    reviewed = transition(reviewed, "V4-010", "reviewed")
    missing_data = json.loads(json.dumps(reviewed.data))
    missing_data["tasks"][0]["external_evidence"] = []
    with pytest.raises(HarnessError) as missing:
        transition(Ledger(missing_data), "V4-010", "converged")
    assert missing.value.code == "external-evidence-required"
    assert transition(reviewed, "V4-010", "converged").data["lifecycle_state"] == "task-complete"


def test_projection_tampering_fails_before_transition(tmp_path: Path) -> None:
    """Stored immutable topology cannot be changed without a new compiled ledger."""
    ledger = initialize_ledger(write_two_task_plan(tmp_path))
    tampered = dict(ledger.data)
    tampered["projection"] = {"tasks": []}
    with pytest.raises(HarnessError) as drift:
        admit_ready(Ledger(tampered), ("V4-010",), capacity=1)
    assert drift.value.code == "ledger-projection-drift"


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("depends_on", ["undeclared"]),
        (
            "scope",
            {"impl_file_refs": ["other"], "test_file_refs": [], "external_impl_file_refs": []},
        ),
        ("verification_commands", ["true"]),
        ("delegation_policy", "preferred"),
        ("resource_locks", []),
    ],
)
def test_duplicated_immutable_task_fields_cannot_drift(
    tmp_path: Path, field: str, replacement: object
) -> None:
    ledger = initialize_ledger(write_two_task_plan(tmp_path))
    tampered = json.loads(json.dumps(ledger.data))
    tampered["tasks"][0][field] = replacement

    with pytest.raises(HarnessError) as drift:
        ready_set(Ledger(tampered))

    assert drift.value.code == "ledger-projection-drift"


@pytest.mark.parametrize(
    ("failure_kind", "route"),
    [
        ("verification-failure", "implement-serial"),
        ("parallel-conflict", "dependency-freeze"),
        ("truth-sync-failure", "truth-sync"),
    ],
)
def test_recovery_routing_is_typed_and_does_not_expand(failure_kind: str, route: str) -> None:
    """Recovery stays at the selected phase for each evidence class."""
    assert recovery_route(failure_kind) == route
