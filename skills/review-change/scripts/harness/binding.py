"""Digest-bound neutral binding projection and offline capability validation."""

from __future__ import annotations

import shlex
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .artifacts import HarnessError

DEFAULT_BACKEND = "codex-native"
MODEL_POLICIES = frozenset({"semantic-routing", "inherit-main", "runtime-default"})
READ_ONLY_ROLES = frozenset({"reviewer", "explorer"})
EFFORT_RANK = {"low": 1, "medium": 2, "high": 3, "xhigh": 4, "max": 5, "ultra": 6}
HERDR_V1_KEYS = frozenset(
    {
        "artifact_kind",
        "authority",
        "batch_provenance",
        "command_job",
        "controller",
        "physical_binding",
        "provenance",
        "schema_version",
        "task",
    }
)
DENIED_CAPABILITIES = (
    "select-task",
    "mutate-task-ledger",
    "converge-task",
    "invoke-review",
    "adjudicate-findings",
    "repair-implementation",
    "derive-lifecycle-tail",
    "claim-task-success",
)


@dataclass(frozen=True)
class BindingRequest:
    """Runtime-only input layered on one immutable ledger task projection."""

    binding_kind: str
    controller_id: str
    run_id: str
    run_nonce: str
    model_policy: str
    task: Mapping[str, object]
    provenance: Mapping[str, object]
    parent_reasoning_effort: str
    minimum_reasoning_effort: str
    requested_model: str = ""
    requested_reasoning_effort: str = ""
    default_reasoning_effort: str = ""
    resolution_source: str = "parent-inherit"
    multi_agent_enabled: bool = True
    max_depth: int | None = None
    concurrency_ceiling: int | None = None
    spawn_cwd_supported: bool = True
    required_uplift_supported: bool = True
    batch_provenance: Mapping[str, object] | None = None
    command_job: Mapping[str, object] | None = None
    herdr_physical_binding: Mapping[str, object] | None = None


def _stop(code: str, message: str) -> HarnessError:
    return HarnessError(code, message)


def _string(mapping: Mapping[str, object], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise _stop("controller_binding_invalid", f"binding requires {key}")
    return value


def _string_list(mapping: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = mapping.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise _stop("controller_binding_invalid", f"binding requires {key} string array")
    return tuple(value)


def derive_runtime_role(binding_kind: str, task: Mapping[str, object]) -> str:
    """Derive authority from the immutable task rather than caller-supplied role text."""
    if binding_kind == "bounded-review":
        return "reviewer"
    touch_set = _string_list(task, "touch_set")
    if (
        not touch_set
        and task.get("execution_profile") == "fast"
        and task.get("reasoning_profile") == "light"
        and task.get("isolation") == "shared-read-only"
    ):
        return "explorer"
    return "worker"


def _validate_task(request: BindingRequest) -> str:
    if request.binding_kind not in {"delegated-task", "bounded-review", "command-job"}:
        raise _stop("controller_binding_invalid", "unsupported binding kind")
    task = request.task
    _string(task, "task_id")
    touch_set = _string_list(task, "touch_set")
    _string_list(task, "resource_locks")
    if request.binding_kind == "command-job":
        command_job = request.command_job
        if not isinstance(command_job, Mapping):
            raise _stop("controller_binding_command_job_invalid", "command job is required")
        allowed = {
            "cwd",
            "argv",
            "command",
            "timeout_seconds",
            "max_concurrency",
            "output_bound_bytes",
            "resource_locks",
            "provenance",
        }
        if set(command_job) != allowed:
            raise _stop("controller_binding_command_job_invalid", "command job schema is not exact")
        cwd = _string(command_job, "cwd")
        if not Path(cwd).is_absolute():
            raise _stop("controller_binding_command_job_invalid", "command cwd must be absolute")
        argv = _string_list(command_job, "argv")
        if not argv or any(
            any(ord(character) < 32 or ord(character) == 127 for character in item) for item in argv
        ):
            raise _stop("controller_binding_command_job_invalid", "command argv is invalid")
        if _string(command_job, "command") != shlex.join(argv):
            raise _stop("controller_binding_command_job_invalid", "command text differs from argv")
        for field, minimum, maximum in (
            ("timeout_seconds", 1, 3600),
            ("max_concurrency", 1, 64),
            ("output_bound_bytes", 1, 16 * 1024 * 1024),
        ):
            value = command_job.get(field)
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or not minimum <= value <= maximum
            ):
                raise _stop("controller_binding_command_job_invalid", f"command {field} is invalid")
        command_locks = _string_list(command_job, "resource_locks")
        if not command_locks or command_locks != _string_list(task, "resource_locks"):
            raise _stop("controller_binding_command_job_invalid", "command resource locks drifted")
        provenance = command_job.get("provenance")
        if not isinstance(provenance, Mapping):
            raise _stop("controller_binding_command_job_invalid", "command provenance is required")
        kind = provenance.get("kind")
        if kind == "task":
            if set(provenance) != {"kind", "task_id"} or provenance.get("task_id") != task.get(
                "task_id"
            ):
                raise _stop(
                    "controller_binding_command_job_invalid", "task command provenance drifted"
                )
            if task.get("status") not in {"in-progress", "verified"}:
                raise _stop("controller_binding_task_not_ready", "task command job is not active")
        elif kind == "gate":
            if set(provenance) != {"kind", "gate_id"} or provenance.get("gate_id") != task.get(
                "task_id"
            ):
                raise _stop(
                    "controller_binding_command_job_invalid", "gate command provenance drifted"
                )
            if task.get("status") != "gate-ready":
                raise _stop("controller_binding_task_not_ready", "gate command job is not ready")
        else:
            raise _stop(
                "controller_binding_command_job_invalid", "command provenance kind is invalid"
            )
    elif task.get("status") != "ready":
        raise _stop("controller_binding_task_not_ready", "selected task is not ready")
    role = derive_runtime_role(request.binding_kind, task)
    if request.binding_kind != "command-job":
        if task.get("executor_mode") != "subagent" or task.get("delegation_policy") == "forbidden":
            raise _stop("controller_binding_authority_denied", "task is not delegated")
        if role in READ_ONLY_ROLES and touch_set:
            raise _stop(
                "controller_binding_isolation_conflict", "read-only roles cannot receive write refs"
            )
        if touch_set and task.get("isolation") != "isolated-worktree":
            raise _stop(
                "controller_binding_isolation_conflict",
                "delegated writers require isolated worktrees",
            )
        if touch_set and not request.spawn_cwd_supported:
            raise _stop(
                "controller_binding_spawn_cwd_unsupported",
                "writer spawn working directory is unavailable",
            )
    return role


def _validate_capabilities(request: BindingRequest) -> None:
    if request.model_policy not in MODEL_POLICIES:
        raise _stop("controller_binding_invalid", "unsupported model policy")
    if not request.multi_agent_enabled:
        raise _stop("controller_binding_multi_agent_disabled", "Codex multi-agent is disabled")
    if request.max_depth not in {None, 1}:
        raise _stop("controller_binding_depth_unsupported", "agents.max_depth must be one")
    if request.concurrency_ceiling is not None and request.concurrency_ceiling < 1:
        raise _stop("controller_binding_concurrency_invalid", "concurrency ceiling is invalid")
    if request.requested_model and not request.requested_reasoning_effort:
        raise _stop(
            "controller_binding_model_only_override", "model overrides require explicit effort"
        )
    if request.model_policy in {"inherit-main", "runtime-default"} and (
        request.requested_model or request.requested_reasoning_effort
    ):
        raise _stop(
            "controller_binding_invalid",
            "inherit-main and runtime-default cannot emit per-spawn overrides",
        )
    floor = max(
        EFFORT_RANK.get(request.parent_reasoning_effort, 0),
        EFFORT_RANK.get(request.minimum_reasoning_effort, 0),
    )
    if floor == 0:
        raise _stop("controller_binding_invalid", "unknown active reasoning floor")
    effective = (
        request.default_reasoning_effort
        if request.model_policy == "runtime-default"
        else request.requested_reasoning_effort
    )
    parent_rank = EFFORT_RANK.get(request.parent_reasoning_effort, 0)
    minimum_rank = EFFORT_RANK.get(request.minimum_reasoning_effort, 0)
    if not effective:
        if request.model_policy == "runtime-default":
            effective_rank = 0
        else:
            effective_rank = parent_rank
    else:
        effective_rank = EFFORT_RANK.get(effective, 0)
    if effective_rank < floor or (
        request.model_policy == "semantic-routing" and not effective and parent_rank < minimum_rank
    ):
        raise _stop(
            "controller_binding_required_uplift_unsupported",
            "effective effort is below the parent or required minimum",
        )
    if not request.required_uplift_supported:
        raise _stop(
            "controller_binding_required_uplift_unsupported",
            "runtime cannot satisfy the active reasoning floor",
        )


def resolve_role_file(
    project_role_file: Path | None,
    user_role_file: Path | None,
    role: str,
    has_writes: bool,
) -> tuple[Path, Mapping[str, object], str]:
    """Resolve project-before-user role configuration and reject unsafe role files."""
    selected: Path | None = None
    source = ""
    for candidate, candidate_source in (
        (project_role_file, "project"),
        (user_role_file, "user"),
    ):
        if candidate is not None and candidate.exists():
            selected = candidate
            source = candidate_source
            break
    if selected is None:
        raise _stop("controller_binding_role_file_missing", "a Codex role file is required")
    if selected.is_symlink() or not selected.is_file():
        raise _stop(
            "controller_binding_role_file_invalid", "role file must be regular and non-symlink"
        )
    try:
        with selected.open("rb") as handle:
            role_file = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise _stop(
            "controller_binding_role_file_invalid", "role file is not valid TOML"
        ) from error
    required = {"name", "description", "developer_instructions", "sandbox_mode"}
    if not required.issubset(role_file) or role_file.get("name") != role:
        raise _stop("controller_binding_role_file_invalid", "role file identity is incomplete")
    forbidden = {"model", "reasoning_effort", "model_reasoning_effort"}
    if forbidden.intersection(role_file):
        raise _stop(
            "controller_binding_role_file_pinned", "role files must not pin model or effort"
        )
    expected_sandbox = "workspace-write" if has_writes and role == "worker" else "read-only"
    if role_file.get("sandbox_mode") != expected_sandbox:
        raise _stop("controller_binding_role_file_invalid", "role file sandbox is incompatible")
    return selected.resolve(), role_file, source


def load_codex_capabilities(config_path: Path) -> dict[str, object]:
    """Read the actual user-owned Codex config without retaining unrelated values."""
    if config_path.is_symlink() or not config_path.is_file():
        raise _stop("controller_binding_config_invalid", "Codex config must be regular")
    try:
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise _stop("controller_binding_config_invalid", "Codex config is invalid TOML") from error
    features = config.get("features")
    agents = config.get("agents")
    if not isinstance(features, dict) or not isinstance(agents, dict):
        raise _stop(
            "controller_binding_config_invalid", "Codex feature and agent tables are required"
        )
    v2 = features.get("multi_agent_v2")
    multi_agent_enabled = (
        features.get("multi_agent") is True
        and isinstance(v2, dict)
        and v2.get("enabled") is True
        and agents.get("enabled") is True
    )
    max_depth = agents.get("max_depth")
    concurrency = agents.get("max_concurrent_threads_per_session")
    default_effort = agents.get("default_subagent_reasoning_effort", "")
    if max_depth is not None and (isinstance(max_depth, bool) or not isinstance(max_depth, int)):
        raise _stop("controller_binding_config_invalid", "agents.max_depth is invalid")
    if concurrency is not None and (
        isinstance(concurrency, bool) or not isinstance(concurrency, int)
    ):
        raise _stop("controller_binding_config_invalid", "agent concurrency is invalid")
    if not isinstance(default_effort, str):
        raise _stop("controller_binding_config_invalid", "agent default effort is invalid")
    return {
        "multi_agent_enabled": multi_agent_enabled,
        "max_depth": max_depth,
        "concurrency_ceiling": concurrency,
        "default_reasoning_effort": default_effort,
    }


def _neutral_core(request: BindingRequest) -> dict[str, object]:
    return {
        "controller": {
            "controller_id": request.controller_id,
            "binding_kind": request.binding_kind,
            "run_id": request.run_id,
            "run_nonce": request.run_nonce,
            "model_policy": request.model_policy,
        },
        "provenance": dict(request.provenance),
        "batch_provenance": (
            dict(request.batch_provenance) if request.batch_provenance is not None else None
        ),
        "task": dict(request.task),
        "command_job": (
            dict(request.command_job)
            if request.binding_kind == "command-job" and request.command_job
            else None
        ),
    }


def binding_envelope(
    request: BindingRequest,
    *,
    backend: str | None = None,
    project_role_file: Path | None = None,
    user_role_file: Path | None = None,
) -> dict[str, object]:
    """Project one ledger-bound task to codex-native v2 or explicit Herdr v1."""
    role = _validate_task(request)
    selected = backend or DEFAULT_BACKEND
    if selected not in {"codex-native", "herdr"}:
        raise _stop("controller_binding_invalid", "unsupported binding backend")
    core = _neutral_core(request)
    if selected == "herdr":
        if request.herdr_physical_binding is None:
            raise _stop("controller_binding_invalid", "Herdr physical binding is required")
        envelope = {
            "schema_version": 1,
            "artifact_kind": "controller-binding-envelope",
            **core,
            "physical_binding": dict(request.herdr_physical_binding),
            "authority": {
                "adapter_capabilities": [
                    "consume-binding",
                    "manage-run-owned-terminal-resources",
                    "persist-adapter-state",
                ],
                "denied_capabilities": list(DENIED_CAPABILITIES),
            },
        }
        return project_herdr_v1(envelope)
    if request.binding_kind == "command-job":
        raise _stop(
            "controller_binding_command_job_unsupported", "codex-native has no command-job binding"
        )
    _validate_capabilities(request)
    touch_set = _string_list(request.task, "touch_set")
    role_path, role_file, source = resolve_role_file(
        project_role_file, user_role_file, role, bool(touch_set)
    )
    extension = {
        "role": role,
        "role_agent_file": role_path.name,
        "role_agent_file_source": source,
        "expected_sandbox_mode": role_file["sandbox_mode"],
        "concurrency_ceiling": request.concurrency_ceiling,
        "max_depth": request.max_depth,
        "max_depth_enforcement": "configured"
        if request.max_depth is not None
        else "instruction-only",
        "requested_model": request.requested_model or None,
        "requested_reasoning_effort": request.requested_reasoning_effort or None,
        "parent_reasoning_effort": request.parent_reasoning_effort,
        "required_minimum_reasoning_effort": request.minimum_reasoning_effort,
        "resolution_source": request.resolution_source,
        "required_uplift_supported": request.required_uplift_supported,
        "spawn_cwd_supported": request.spawn_cwd_supported,
    }
    return {
        "schema_version": 2,
        "artifact_kind": "controller-binding-envelope",
        "core": core,
        "backend": {"backend_kind": "codex-native", "extension": extension},
    }


def project_herdr_v1(core: Mapping[str, object]) -> dict[str, object]:
    """Return a lossless, validated explicit Herdr schema-version-1 envelope."""
    if set(core) != HERDR_V1_KEYS:
        raise _stop("controller_binding_invalid", "Herdr v1 envelope keys drifted")
    if (
        core.get("schema_version") != 1
        or core.get("artifact_kind") != "controller-binding-envelope"
    ):
        raise _stop("controller_binding_invalid", "Herdr v1 envelope identity is invalid")
    for key in ("authority", "controller", "physical_binding", "provenance", "task"):
        if not isinstance(core.get(key), dict):
            raise _stop("controller_binding_invalid", f"Herdr v1 {key} must be an object")
    return dict(core)
