"""State, digest, atomicity, and authority tests for the version-3 task ledger."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.harness import ledger as ledger_module
from runtime.harness.artifacts import HarnessError
from runtime.harness.external_touch import (
    apply_and_cleanup_intent,
    capture_baseline,
    prepare_intent,
    stage_payload,
)
from runtime.harness.ledger import (
    Ledger,
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
from runtime.harness.tests.test_v3_artifacts import (
    design_text,
    digest,
    plan_text,
    write_valid_pair,
)


def write_two_task_plan(tmp_path: Path) -> Path:
    """Build a dependency chain using the HSC-020 fixture helpers."""
    design, plan = write_valid_pair(tmp_path)
    second = "\n".join(
        (
            "",
            "[[tasks]]",
            'task_id = "HSC-030"',
            'depends_on = ["HSC-020"]',
            'verification_commands = ["uv run pytest runtime/harness/tests"]',
            'scope_slice = "Implement immutable ledger state."',
            'executor_mode = "subagent"',
            'parallel_group = "none"',
            'parallel_policy = "forbidden"',
            'delegation_policy = "allowed"',
            'execution_profile = "deep"',
            'reasoning_profile = "deep"',
            'isolation = "isolated-worktree"',
            'resource_locks = ["runtime-harness"]',
            "convergence_required = true",
            "review_budget = 1",
            'task_review_depth = "full"',
            'done_when = ["Ledger tests pass."]',
            'failure_policy = "fix_forward"',
            'rollback_trigger = ""',
            'rollback_target = ""',
            'rollback_verification = ""',
            "",
            "[tasks.scope]",
            'impl_file_refs = ["runtime/harness/ledger.py"]',
            'test_file_refs = ["runtime/harness/tests/test_ledger.py"]',
            "external_impl_file_refs = []",
        )
    )
    contents = plan_text(digest(design.read_text(encoding="utf-8"))).replace(
        'impl_file_refs = ["runtime/harness/artifacts.py"]', 'impl_file_refs = ["runtime/harness"]'
    )
    contents = contents.replace(
        'test_file_refs = ["runtime/harness/tests/test_v3_artifacts.py"]',
        'test_file_refs = ["runtime/harness/tests"]',
    )
    plan.write_text(
        contents.replace("+++\n# Plan", f"{second}\n+++\n# Plan"),
        encoding="utf-8",
    )
    return plan


def converge_first_task(ledger: Ledger) -> Ledger:
    """Advance the first task through required verification and review gates."""
    value = transition(ledger, "HSC-020", "in-progress")
    value = record_verification(value, "HSC-020", "uv run pytest runtime/harness/tests", True)
    value = transition(value, "HSC-020", "verified")
    value = record_review(value, "HSC-020", True, "review-1")
    value = transition(value, "HSC-020", "reviewed")
    return transition(value, "HSC-020", "converged")


def test_initialization_compiles_once_and_later_transition_is_digest_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Only initialization compiles artifacts; later changes validate stored byte digests."""
    ledger = initialize_ledger(write_two_task_plan(tmp_path))
    assert ready_set(ledger) == ("HSC-020",)

    def fail_compile(_: Path) -> Ledger:
        raise AssertionError("transition must not parse or compile the plan")

    monkeypatch.setattr(ledger_module, "compile_plan", fail_compile)
    advanced = transition(ledger, "HSC-020", "in-progress")

    tasks = advanced.data["tasks"]
    assert isinstance(tasks, list) and isinstance(tasks[0], dict)
    assert tasks[0]["status"] == "in-progress"


def test_initialization_uses_cwd_relative_artifact_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    design, plan = write_valid_pair(tmp_path)
    monkeypatch.chdir(tmp_path)

    ledger = initialize_ledger(plan)

    assert ledger.data["plan_ref"] == "plan.md"
    assert ledger.data["design_ref"] == "design.md"
    assert ready_set(ledger) == ("HSC-020",)


def test_transitions_refresh_ready_set_and_gate_truth_sync_and_close(tmp_path: Path) -> None:
    """Task convergence unlocks dependents and the explicit truth/close gates."""
    ledger = converge_first_task(initialize_ledger(write_two_task_plan(tmp_path)))
    assert ready_set(ledger) == ("HSC-030",)
    value = transition(ledger, "HSC-030", "in-progress")
    value = record_verification(value, "HSC-030", "uv run pytest runtime/harness/tests", True)
    value = transition(value, "HSC-030", "verified")
    value = record_review(value, "HSC-030", True, "review-2")
    value = transition(value, "HSC-030", "reviewed")
    value = transition(value, "HSC-030", "converged")
    assert truth_sync_decision(value, None) == "truth-sync-pending"


def test_digest_drift_and_invalid_transition_fail_closed(tmp_path: Path) -> None:
    """Artifact drift and skipped lifecycle gates never advance authority."""
    plan = write_two_task_plan(tmp_path)
    ledger = initialize_ledger(plan)
    with pytest.raises(HarnessError) as skipped:
        transition(ledger, "HSC-020", "verified")
    assert skipped.value.code == "invalid-transition"
    plan.write_text(f"{plan.read_text(encoding='utf-8')}\n", encoding="utf-8")
    with pytest.raises(HarnessError) as drift:
        transition(ledger, "HSC-020", "in-progress")
    assert drift.value.code == "artifact-digest-drift"


@pytest.mark.parametrize("artifact", ["design", "plan"])
def test_ledger_initialization_requires_approved_design_and_plan(
    tmp_path: Path, artifact: str
) -> None:
    design, plan = write_valid_pair(tmp_path)
    target = design if artifact == "design" else plan
    target.write_text(
        target.read_text(encoding="utf-8").replace(
            'approval_status = "approved"', 'approval_status = "pending"'
        ),
        encoding="utf-8",
    )
    if artifact == "design":
        plan.write_text(plan_text(digest(design.read_text(encoding="utf-8"))), encoding="utf-8")

    with pytest.raises(HarnessError) as stopped:
        initialize_ledger(plan)

    assert stopped.value.code == "artifact-not-approved"


def test_rejected_review_invalidates_evidence_and_requires_active_attempt(
    tmp_path: Path,
) -> None:
    ledger = initialize_ledger(write_two_task_plan(tmp_path))
    with pytest.raises(HarnessError) as premature:
        record_verification(ledger, "HSC-020", "uv run pytest runtime/harness/tests", True)
    assert premature.value.code == "verification-not-ready"
    active = transition(ledger, "HSC-020", "in-progress")
    verified = record_verification(active, "HSC-020", "uv run pytest runtime/harness/tests", True)
    verified = transition(verified, "HSC-020", "verified")
    repairing = record_review(verified, "HSC-020", False, "review-rejected")
    tasks = repairing.data["tasks"]
    assert isinstance(tasks, list) and isinstance(tasks[0], dict)
    task = tasks[0]
    assert task["status"] == "in-progress"
    assert task["repair_attempts"] == 1
    assert task["verification_evidence"] == []
    assert task["review"] is None
    with pytest.raises(HarnessError) as stale:
        transition(repairing, "HSC-020", "verified")
    assert stale.value.code == "verification-evidence-required"


def test_non_truth_close_binds_directly_to_ledger_and_execution_result(tmp_path: Path) -> None:
    _, plan = write_valid_pair(tmp_path)
    plan.write_text(
        plan.read_text(encoding="utf-8").replace(
            "truth_sync_required = true", "truth_sync_required = false"
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
                "contract_version = 3",
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
    authored_design = design_text().replace("/tmp/harness-evidence", str(target_file))
    design.write_text(authored_design, encoding="utf-8")
    plan = repo / "plan.md"
    authored_plan = plan_text(digest(authored_design)).replace(
        'external_impl_file_refs = ["/tmp/harness-evidence"]',
        f'external_impl_file_refs = ["{target_file}"]',
    )
    authored_plan = authored_plan.replace(
        "external_impl_file_refs = []\n+++\n# Plan",
        f'external_impl_file_refs = ["{target_file}"]\n+++\n# Plan',
    )
    plan.write_text(authored_plan, encoding="utf-8")
    ledger = initialize_ledger(plan)
    target = tmp_path / "ledger.json"
    write_ledger(target, ledger)
    persisted = read_ledger(target)
    assert persisted.data["projection_sha256"] == ledger.data["projection_sha256"]
    assert_task_touch_set(persisted, "HSC-020", ("runtime/harness/artifacts.py",))
    with pytest.raises(HarnessError) as touch:
        assert_task_touch_set(persisted, "HSC-020", ("other/unowned.py",))
    assert touch.value.code == "touch-set-violation"
    active = transition(persisted, "HSC-020", "in-progress")
    baseline = capture_baseline(
        repo_root=repo,
        refs=[str(target_file)],
        run_id="run-1",
        task_id="HSC-020",
        design_sha256=str(active.data["design_sha256"]),
        plan_sha256=str(active.data["plan_sha256"]),
    )
    run_dir = external / "run"
    run_dir.mkdir(mode=0o700)
    candidate = external / "candidate.toml"
    candidate.write_text("value = 2\n", encoding="utf-8")
    staged = stage_payload(run_dir=run_dir, intent_id="intent-1", source_file=candidate)
    prepared = prepare_intent(
        repo_root=repo,
        baseline=baseline,
        intents=[],
        ref=str(target_file),
        intent_id="intent-1",
        staged_payload=staged,
    )
    applied = apply_and_cleanup_intent(repo_root=repo, intent=prepared)
    recorded = record_external_evidence(active, "HSC-020", baseline, [applied])
    tasks = recorded.data["tasks"]
    assert isinstance(tasks, list) and isinstance(tasks[0], dict)
    evidence = tasks[0]["external_evidence"]
    assert isinstance(evidence, list) and evidence[0]["state"] == "valid"
    assert evidence[0]["refs"][0]["ref"] == str(target_file)
    assert "value = 2" not in repr(evidence)
    verified = record_verification(recorded, "HSC-020", "uv run pytest runtime/harness/tests", True)
    verified = transition(verified, "HSC-020", "verified")
    reviewed = record_review(verified, "HSC-020", True, "external-review")
    reviewed = transition(reviewed, "HSC-020", "reviewed")
    missing_data = json.loads(json.dumps(reviewed.data))
    missing_data["tasks"][0]["external_evidence"] = []
    with pytest.raises(HarnessError) as missing:
        transition(Ledger(missing_data), "HSC-020", "converged")
    assert missing.value.code == "external-evidence-required"
    assert transition(reviewed, "HSC-020", "converged").data["lifecycle_state"] == "task-complete"


def test_projection_tampering_fails_before_transition(tmp_path: Path) -> None:
    """Stored immutable topology cannot be changed without a new compiled ledger."""
    ledger = initialize_ledger(write_two_task_plan(tmp_path))
    tampered = dict(ledger.data)
    tampered["projection"] = {"tasks": []}
    with pytest.raises(HarnessError) as drift:
        transition(Ledger(tampered), "HSC-020", "in-progress")
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
