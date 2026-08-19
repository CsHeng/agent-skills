"""Direct-file CLI tests for complete shared-runtime operations."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from runtime.harness.tests.test_v3_artifacts import write_valid_pair

ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "runtime" / "harness" / "cli.py"


def run_cli(tmp_path: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *arguments],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=os.environ | {"CODEX_HOME": str(tmp_path / ".codex")},
    )


def response(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.returncode == 0, result.stderr
    value = json.loads(result.stdout)
    assert isinstance(value, dict)
    return value


def test_direct_file_cli_initializes_transitions_binds_and_evaluates(tmp_path: Path) -> None:
    _, plan = write_valid_pair(tmp_path)
    ledger = tmp_path / "ledger.json"

    initialized = response(run_cli(tmp_path, "ledger", "init", str(plan), str(ledger)))
    assert initialized["status"] == "ok"
    assert ledger.is_file()
    advanced = response(
        run_cli(tmp_path, "ledger", "transition", str(ledger), "HSC-020", "in-progress")
    )
    ledger_data = advanced["ledger"]
    assert isinstance(ledger_data, dict)
    tasks = ledger_data["tasks"]
    assert isinstance(tasks, list) and isinstance(tasks[0], dict)
    assert tasks[0]["status"] == "in-progress"
    ready = response(run_cli(tmp_path, "ledger", "ready", str(ledger)))
    assert ready["ready"] == []

    verification_request = tmp_path / "verification.json"
    verification_request.write_text(
        json.dumps(
            {
                "command": "uv run pytest runtime/harness/tests",
                "passed": True,
            }
        ),
        encoding="utf-8",
    )
    response(
        run_cli(
            tmp_path,
            "ledger",
            "verification",
            str(ledger),
            "HSC-020",
            str(verification_request),
        )
    )
    response(run_cli(tmp_path, "ledger", "transition", str(ledger), "HSC-020", "verified"))
    review_request = tmp_path / "review.json"
    review_request.write_text(
        json.dumps({"accepted": True, "batch_id": "review-1"}), encoding="utf-8"
    )
    response(
        run_cli(
            tmp_path,
            "ledger",
            "review",
            str(ledger),
            "HSC-020",
            str(review_request),
        )
    )
    response(run_cli(tmp_path, "ledger", "transition", str(ledger), "HSC-020", "reviewed"))
    converged = response(
        run_cli(tmp_path, "ledger", "transition", str(ledger), "HSC-020", "converged")
    )
    converged_tasks = converged["ledger"]
    assert isinstance(converged_tasks, dict)
    assert converged_tasks["lifecycle_state"] == "task-complete"

    gate_request = tmp_path / "gate-command.json"
    gate_command = {
        "cwd": str(tmp_path),
        "argv": ["uv", "run", "pytest"],
        "command": "uv run pytest",
        "timeout_seconds": 300,
        "max_concurrency": 1,
        "output_bound_bytes": 65536,
        "resource_locks": ["implementation-gate"],
        "provenance": {"kind": "gate", "gate_id": "implementation-verification"},
    }
    gate_request.write_text(
        json.dumps(
            {
                "backend": "herdr",
                "binding_kind": "command-job",
                "controller_id": "controller-1",
                "run_id": "gate-1",
                "run_nonce": "gate-nonce-1",
                "model_policy": "inherit-main",
                "parent_reasoning_effort": "high",
                "minimum_reasoning_effort": "high",
                "command_job": gate_command,
                "physical_binding": {
                    "agent_kind": "codex",
                    "agent_name": "command-gate-1",
                    "capability_profile": "command-job",
                    "checkout_path": str(tmp_path),
                    "control_plane_endpoint": "local",
                    "credential_ref": "none",
                    "model": "none",
                    "pane_id": "pane-1",
                    "permission_mode": "always-approve",
                    "reasoning_effort": "none",
                    "sandbox_mode": "workspace-write",
                    "tab_id": "tab-1",
                    "terminal_backend": "herdr",
                    "workspace_id": "workspace-1",
                },
            }
        ),
        encoding="utf-8",
    )
    gate_envelope = response(
        run_cli(
            tmp_path,
            "execute",
            "bind",
            str(ledger),
            "implementation-verification",
            str(gate_request),
        )
    )["envelope"]
    assert isinstance(gate_envelope, dict)
    assert gate_envelope["command_job"] == gate_command

    binding_ledger = tmp_path / "binding-ledger.json"
    response(run_cli(tmp_path, "ledger", "init", str(plan), str(binding_ledger)))
    role_root = tmp_path / ".codex" / "agents"
    role_root.mkdir(parents=True)
    (tmp_path / ".codex" / "config.toml").write_text(
        "\n".join(
            (
                "[features]",
                "multi_agent = true",
                "[features.multi_agent_v2]",
                "enabled = true",
                "[agents]",
                "enabled = true",
                "max_depth = 1",
                "max_concurrent_threads_per_session = 4",
                "",
            )
        ),
        encoding="utf-8",
    )
    for role, sandbox in (("worker", "workspace-write"), ("reviewer", "read-only")):
        (role_root / f"{role}.toml").write_text(
            "\n".join(
                (
                    f'name = "{role}"',
                    'description = "bounded role"',
                    f'sandbox_mode = "{sandbox}"',
                    'developer_instructions = "bounded instructions"',
                    "",
                )
            ),
            encoding="utf-8",
        )
    binding_request = tmp_path / "binding.json"
    binding_request.write_text(
        json.dumps(
            {
                "binding_kind": "delegated-task",
                "controller_id": "controller-1",
                "run_id": "run-1",
                "run_nonce": "nonce-1",
                "model_policy": "inherit-main",
                "parent_reasoning_effort": "high",
                "minimum_reasoning_effort": "high",
            }
        ),
        encoding="utf-8",
    )
    envelope = response(
        run_cli(
            tmp_path,
            "execute",
            "bind",
            str(binding_ledger),
            "HSC-020",
            str(binding_request),
        )
    )
    envelope_data = envelope["envelope"]
    assert isinstance(envelope_data, dict)
    assert envelope_data["schema_version"] == 2

    review_brief = tmp_path / "review-brief.md"
    review_brief.write_text("Review only the approved task diff.\n", encoding="utf-8")
    review_binding = tmp_path / "review-binding.json"
    review_binding.write_text(
        json.dumps(
            {
                "binding_kind": "bounded-review",
                "controller_id": "controller-1",
                "run_id": "review-1",
                "run_nonce": "nonce-review-1",
                "model_policy": "inherit-main",
                "parent_reasoning_effort": "high",
                "minimum_reasoning_effort": "high",
                "review_brief_ref": str(review_brief),
                "review_brief_sha256": hashlib.sha256(review_brief.read_bytes()).hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    review_envelope = response(
        run_cli(
            tmp_path,
            "execute",
            "bind",
            str(ledger),
            "review-implementation",
            str(review_binding),
        )
    )["envelope"]
    assert isinstance(review_envelope, dict)
    review_backend = review_envelope["backend"]
    assert isinstance(review_backend, dict)
    review_extension = review_backend["extension"]
    assert isinstance(review_extension, dict)
    assert review_extension["role"] == "reviewer"

    original_plan = plan.read_text(encoding="utf-8")
    plan.write_text(f"{original_plan}\n", encoding="utf-8")
    drifted_review = run_cli(
        tmp_path,
        "execute",
        "bind",
        str(ledger),
        "review-implementation",
        str(review_binding),
    )
    assert drifted_review.returncode == 2
    assert json.loads(drifted_review.stderr)["code"] == "artifact-digest-drift"
    plan.write_text(original_plan, encoding="utf-8")

    execution_result = tmp_path / "execution-result.json"
    execution_result.write_text(
        json.dumps(
            {
                "status": "passed",
                "review_status": "passed",
                "verification_status": "passed",
                "plan_sha256": converged_tasks["plan_sha256"],
                "design_sha256": converged_tasks["design_sha256"],
                "projection_sha256": converged_tasks["projection_sha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    execution_sha256 = hashlib.sha256(execution_result.read_bytes()).hexdigest()
    ledger_sha256 = hashlib.sha256(ledger.read_bytes()).hexdigest()
    truth_request = tmp_path / "truth.md"
    truth_request.write_text(
        "\n".join(
            (
                "+++",
                'artifact_kind = "truth-sync"',
                "contract_version = 3",
                'execution_result_ref = "execution-result.json"',
                f'execution_result_sha256 = "{execution_sha256}"',
                'ledger_ref = "ledger.json"',
                f'ledger_sha256 = "{ledger_sha256}"',
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
                "Approve the bounded stable truth update.",
                "",
            )
        ),
        encoding="utf-8",
    )
    truth = response(run_cli(tmp_path, "truth-sync", "evaluate", str(ledger), str(truth_request)))
    assert truth["decision"] == "ready-for-close"

    truth_sha256 = hashlib.sha256(truth_request.read_bytes()).hexdigest()
    close_request = tmp_path / "close.md"
    close_request.write_text(
        "\n".join(
            (
                "+++",
                'artifact_kind = "close"',
                "contract_version = 3",
                'truth_sync_ref = "truth.md"',
                f'truth_sync_sha256 = "{truth_sha256}"',
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
                "Close only with explicit approval.",
                "",
            )
        ),
        encoding="utf-8",
    )
    close = response(run_cli(tmp_path, "close", "evaluate", str(ledger), str(close_request)))
    assert close["decision"] == "closed"

    execution_result.write_text('{"status":"tampered"}', encoding="utf-8")
    tampered = run_cli(tmp_path, "truth-sync", "evaluate", str(ledger), str(truth_request))
    assert tampered.returncode == 2
    assert json.loads(tampered.stderr)["code"] == "execution-result-digest-mismatch"


def test_cli_returns_typed_json_errors_for_invalid_request(tmp_path: Path) -> None:
    _, plan = write_valid_pair(tmp_path)
    ledger = tmp_path / "ledger.json"
    response(run_cli(tmp_path, "ledger", "init", str(plan), str(ledger)))
    request = tmp_path / "invalid.json"
    request.write_text("[]", encoding="utf-8")

    result = run_cli(tmp_path, "execute", "bind", str(ledger), "HSC-020", str(request))

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "invalid-json-request"


def test_binding_request_cannot_override_ledger_topology(tmp_path: Path) -> None:
    _, plan = write_valid_pair(tmp_path)
    ledger = tmp_path / "ledger.json"
    response(run_cli(tmp_path, "ledger", "init", str(plan), str(ledger)))
    request = tmp_path / "binding.json"
    request.write_text(
        json.dumps(
            {
                "binding_kind": "delegated-task",
                "controller_id": "controller-1",
                "run_id": "run-1",
                "run_nonce": "nonce-1",
                "model_policy": "inherit-main",
                "parent_reasoning_effort": "high",
                "minimum_reasoning_effort": "high",
                "touch_set": ["other"],
            }
        ),
        encoding="utf-8",
    )

    result = run_cli(tmp_path, "execute", "bind", str(ledger), "HSC-020", str(request))

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "invalid-json-request"


def test_shared_cli_exposes_external_touch_evidence_namespace(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    target = tmp_path / "external.txt"
    target.write_text("secret payload\n", encoding="utf-8")

    baseline = response(
        run_cli(
            tmp_path,
            "external-touch",
            "baseline",
            "--repo-root",
            str(repo),
            "--run-id",
            "run-1",
            "--task-id",
            "HSC-030",
            "--design-sha256",
            "a" * 64,
            "--plan-sha256",
            "b" * 64,
            "--ref",
            str(target),
        )
    )

    assert baseline["schema_version"] == 1
    refs = baseline["refs"]
    assert isinstance(refs, list) and isinstance(refs[0], dict)
    assert refs[0]["ref"] == str(target)
    assert "secret payload" not in repr(baseline)
