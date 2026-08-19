"""Offline contract tests for digest-bound Codex and explicit Herdr projections."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from runtime.harness.artifacts import HarnessError
from runtime.harness.binding import (
    BindingRequest,
    binding_envelope,
    load_codex_capabilities,
    project_herdr_v1,
)


def task_projection(
    *,
    touch_set: tuple[str, ...] = ("runtime/harness",),
    execution_profile: str = "deep",
    reasoning_profile: str = "deep",
    isolation: str = "isolated-worktree",
) -> dict[str, object]:
    return {
        "task_id": "HSC-040",
        "depends_on": [],
        "touch_set": list(touch_set),
        "external_impl_file_refs": [],
        "verification_commands": ["uv run pytest runtime/harness/tests"],
        "scope_slice": "Bind one immutable task.",
        "executor_mode": "subagent",
        "parallel_group": "none",
        "parallel_policy": "forbidden",
        "delegation_policy": "allowed",
        "execution_profile": execution_profile,
        "reasoning_profile": reasoning_profile,
        "isolation": isolation,
        "resource_locks": ["runtime-binding-contract"],
        "convergence_required": True,
        "review_budget": 1,
        "task_review_depth": "full",
        "done_when": ["Binding passes."],
        "failure_policy": "fix_forward",
        "rollback_trigger": "",
        "rollback_target": "",
        "rollback_verification": "",
        "status": "ready",
        "attempt": 1,
    }


def request(
    *,
    binding_kind: str = "delegated-task",
    model_policy: str = "semantic-routing",
    task: dict[str, object] | None = None,
    requested_model: str = "",
    requested_reasoning_effort: str = "",
    default_reasoning_effort: str = "",
    spawn_cwd_supported: bool = True,
    required_uplift_supported: bool = True,
) -> BindingRequest:
    return BindingRequest(
        binding_kind=binding_kind,
        controller_id="controller-1",
        run_id="run-1",
        run_nonce="nonce-1",
        model_policy=model_policy,
        task=task or task_projection(),
        provenance={
            "canonical_repository": "/tmp/repo",
            "repository_revision": "a" * 40,
            "plan_ref": "/tmp/repo/plan.md",
            "plan_sha256": "b" * 64,
            "ledger_ref": "/tmp/repo/ledger.json",
            "ledger_sha256": "c" * 64,
            "batch": None,
        },
        parent_reasoning_effort="high",
        minimum_reasoning_effort="high",
        requested_model=requested_model,
        requested_reasoning_effort=requested_reasoning_effort,
        default_reasoning_effort=default_reasoning_effort,
        spawn_cwd_supported=spawn_cwd_supported,
        required_uplift_supported=required_uplift_supported,
        herdr_physical_binding={
            "agent_kind": "codex",
            "agent_name": "worker-run-1-hsc-040-a1",
            "capability_profile": "delegated-local-writer",
            "checkout_path": "/tmp/repo-worktree",
            "control_plane_endpoint": "local",
            "credential_ref": "none",
            "model": "gpt-5.6-terra",
            "pane_id": "pane-1",
            "permission_mode": "always-approve",
            "reasoning_effort": "high",
            "sandbox_mode": "workspace-write",
            "tab_id": "tab-1",
            "terminal_backend": "herdr",
            "workspace_id": "workspace-1",
        },
    )


def role_file(tmp_path: Path, role: str = "worker", sandbox: str = "workspace-write") -> Path:
    path = tmp_path / f"{role}.toml"
    path.write_text(
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
    return path


def test_omitted_backend_equals_explicit_codex_native(tmp_path: Path) -> None:
    selected_role = role_file(tmp_path)
    binding = request()

    omitted = binding_envelope(binding, user_role_file=selected_role)
    explicit = binding_envelope(binding, backend="codex-native", user_role_file=selected_role)

    assert omitted == explicit
    assert omitted["schema_version"] == 2
    core = omitted["core"]
    assert isinstance(core, dict)
    assert core["task"] == binding.task


@pytest.mark.parametrize("model_policy", ["semantic-routing", "inherit-main", "runtime-default"])
def test_explicit_herdr_retains_complete_schema_v1(model_policy: str) -> None:
    envelope = binding_envelope(request(model_policy=model_policy), backend="herdr")

    assert set(envelope) == {
        "schema_version",
        "artifact_kind",
        "controller",
        "provenance",
        "batch_provenance",
        "task",
        "command_job",
        "physical_binding",
        "authority",
    }
    controller = envelope["controller"]
    task = envelope["task"]
    authority = envelope["authority"]
    assert isinstance(controller, dict)
    assert isinstance(task, dict)
    assert isinstance(authority, dict)
    assert controller["model_policy"] == model_policy
    assert task["touch_set"] == ["runtime/harness"]
    denied = authority["denied_capabilities"]
    assert isinstance(denied, list) and "mutate-task-ledger" in denied


def test_herdr_v1_projection_is_lossless_for_a_complete_envelope() -> None:
    envelope = binding_envelope(request(), backend="herdr")
    assert project_herdr_v1(envelope) == envelope


@pytest.mark.parametrize(
    ("binding", "role", "code"),
    [
        (request(), None, "controller_binding_role_file_missing"),
        (
            request(task={**task_projection(), "isolation": "shared-read-only"}),
            "worker",
            "controller_binding_isolation_conflict",
        ),
        (
            request(spawn_cwd_supported=False),
            "worker",
            "controller_binding_spawn_cwd_unsupported",
        ),
        (
            request(requested_model="gpt-5.6-terra"),
            "worker",
            "controller_binding_model_only_override",
        ),
        (
            request(requested_reasoning_effort="medium"),
            "worker",
            "controller_binding_required_uplift_unsupported",
        ),
        (
            request(model_policy="runtime-default", default_reasoning_effort="medium"),
            "worker",
            "controller_binding_required_uplift_unsupported",
        ),
        (
            request(required_uplift_supported=False),
            "worker",
            "controller_binding_required_uplift_unsupported",
        ),
        (
            replace(request(), multi_agent_enabled=False),
            "worker",
            "controller_binding_multi_agent_disabled",
        ),
        (
            replace(request(), max_depth=2),
            "worker",
            "controller_binding_depth_unsupported",
        ),
    ],
)
def test_codex_capability_stops_are_typed(
    tmp_path: Path, binding: BindingRequest, role: str | None, code: str
) -> None:
    selected_role = role_file(tmp_path) if role else None
    with pytest.raises(HarnessError) as captured:
        binding_envelope(binding, user_role_file=selected_role)
    assert captured.value.code == code


@pytest.mark.parametrize("model_policy", ["inherit-main", "semantic-routing"])
def test_inherited_effort_below_required_floor_requires_uplift(
    tmp_path: Path, model_policy: str
) -> None:
    selected_role = role_file(tmp_path)
    binding = replace(
        request(model_policy=model_policy),
        parent_reasoning_effort="medium",
        minimum_reasoning_effort="high",
    )

    with pytest.raises(HarnessError) as stopped:
        binding_envelope(binding, user_role_file=selected_role)

    assert stopped.value.code == "controller_binding_required_uplift_unsupported"


def test_role_file_resolution_rejects_symlink_pin_and_writable_reviewer(
    tmp_path: Path,
) -> None:
    worker = role_file(tmp_path)
    symlink = tmp_path / "linked.toml"
    symlink.symlink_to(worker)
    with pytest.raises(HarnessError) as linked:
        binding_envelope(request(), user_role_file=symlink)
    assert linked.value.code == "controller_binding_role_file_invalid"

    pinned = tmp_path / "pinned.toml"
    pinned.write_text(
        worker.read_text(encoding="utf-8") + 'model = "gpt-5.6-terra"\n',
        encoding="utf-8",
    )
    with pytest.raises(HarnessError) as pin:
        binding_envelope(request(), user_role_file=pinned)
    assert pin.value.code == "controller_binding_role_file_pinned"

    review_task = task_projection(touch_set=(), isolation="shared-read-only")
    writable_reviewer = role_file(tmp_path, "reviewer", "workspace-write")
    with pytest.raises(HarnessError) as reviewer:
        binding_envelope(
            request(binding_kind="bounded-review", task=review_task),
            user_role_file=writable_reviewer,
        )
    assert reviewer.value.code == "controller_binding_role_file_invalid"


def test_codex_capabilities_are_read_from_actual_config_shape(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text(
        "\n".join(
            (
                "[features]",
                "multi_agent = true",
                "[features.multi_agent_v2]",
                "enabled = true",
                "[agents]",
                "enabled = true",
                "max_depth = 1",
                "max_concurrent_threads_per_session = 7",
                'default_subagent_reasoning_effort = "high"',
                "",
            )
        ),
        encoding="utf-8",
    )

    assert load_codex_capabilities(config) == {
        "multi_agent_enabled": True,
        "max_depth": 1,
        "concurrency_ceiling": 7,
        "default_reasoning_effort": "high",
    }


def test_command_job_is_explicit_herdr_only() -> None:
    command = {
        "cwd": "/tmp/repo-worktree",
        "argv": ["uv", "run", "pytest"],
        "command": "uv run pytest",
        "timeout_seconds": 300,
        "max_concurrency": 1,
        "output_bound_bytes": 65536,
        "resource_locks": ["runtime-binding-contract"],
        "provenance": {"kind": "task", "task_id": "HSC-040"},
    }
    binding = request(
        binding_kind="command-job", task={**task_projection(), "status": "in-progress"}
    )
    binding = replace(binding, command_job=command)
    assert binding_envelope(binding, backend="herdr")["command_job"] == command
    with pytest.raises(HarnessError) as unsupported:
        binding_envelope(binding)
    assert unsupported.value.code == "controller_binding_command_job_unsupported"


def test_gate_command_job_has_distinct_gate_provenance() -> None:
    gate = task_projection(touch_set=(), isolation="shared-read-only")
    gate.update(
        {
            "task_id": "implementation-verification",
            "status": "gate-ready",
            "resource_locks": ["implementation-gate"],
        }
    )
    command = {
        "cwd": "/tmp/repo-worktree",
        "argv": ["uv", "run", "pytest"],
        "command": "uv run pytest",
        "timeout_seconds": 300,
        "max_concurrency": 1,
        "output_bound_bytes": 65536,
        "resource_locks": ["implementation-gate"],
        "provenance": {"kind": "gate", "gate_id": "implementation-verification"},
    }
    binding = replace(request(binding_kind="command-job", task=gate), command_job=command)

    assert binding_envelope(binding, backend="herdr")["command_job"] == command


def test_normalized_herdr_envelope_is_stable() -> None:
    envelope = binding_envelope(request(), backend="herdr")
    normalized = json.dumps(envelope, sort_keys=True, separators=(",", ":"))
    assert json.loads(normalized) == envelope


@pytest.mark.parametrize("binding_kind", ["delegated-task", "command-job", "bounded-review"])
@pytest.mark.parametrize("model_policy", ["semantic-routing", "inherit-main", "runtime-default"])
def test_all_explicit_herdr_binding_goldens(binding_kind: str, model_policy: str) -> None:
    selected_task = (
        task_projection(touch_set=(), isolation="shared-read-only")
        if binding_kind == "bounded-review"
        else {**task_projection(), "status": "in-progress"}
        if binding_kind == "command-job"
        else task_projection()
    )
    binding = request(binding_kind=binding_kind, model_policy=model_policy, task=selected_task)
    if binding_kind == "command-job":
        binding = replace(
            binding,
            command_job={
                "cwd": "/tmp/repo-worktree",
                "argv": ["uv", "run", "pytest"],
                "command": "uv run pytest",
                "timeout_seconds": 300,
                "max_concurrency": 1,
                "output_bound_bytes": 65536,
                "resource_locks": ["runtime-binding-contract"],
                "provenance": {"kind": "task", "task_id": "HSC-040"},
            },
        )
    envelope = binding_envelope(binding, backend="herdr")
    normalized = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()
    fixture_path = Path(__file__).parent / "fixtures/legacy_herdr_schema_v1.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    key = f"{binding_kind}:{model_policy}"
    assert hashlib.sha256(normalized).hexdigest() == fixture["golden_envelopes"][key]
