"""Command-line namespace for the version-4 lifecycle harness runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import NoReturn, TextIO

if not __package__:  # pragma: no cover - exercised by installed skill invocation examples.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "harness"

from .artifacts import HarnessError, compile_plan, validate_artifact
from .binding import (
    BindingRequest,
    binding_envelope,
    derive_runtime_role,
    load_codex_capabilities,
)
from .external_touch import main as external_touch_main
from .ledger import (
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
    task_binding_projection,
    transition,
    truth_sync_decision,
    verify_artifact_digests,
    write_ledger,
)
from .lifecycle import classify_request, next_phase


def parser() -> argparse.ArgumentParser:
    """Build only namespace commands; scalar field extraction is deliberately absent."""
    root = argparse.ArgumentParser(prog="harness")
    namespaces = root.add_subparsers(dest="namespace", required=True)
    for namespace in ("design", "plan", "truth-sync", "close"):
        command = namespaces.add_parser(namespace)
        commands = command.add_subparsers(dest="operation", required=True)
        validate = commands.add_parser("validate")
        validate.add_argument("artifact", type=Path)
        if namespace == "plan":
            compile_command = commands.add_parser("compile")
            compile_command.add_argument("artifact", type=Path)
        if namespace in {"truth-sync", "close"}:
            evaluate = commands.add_parser("evaluate")
            evaluate.add_argument("ledger", type=Path)
            evaluate.add_argument("request", type=Path)

    ledger = namespaces.add_parser("ledger")
    ledger_commands = ledger.add_subparsers(dest="operation", required=True)
    initialize = ledger_commands.add_parser("init")
    initialize.add_argument("plan", type=Path)
    initialize.add_argument("ledger", type=Path)
    ledger_transition = ledger_commands.add_parser("transition")
    ledger_transition.add_argument("ledger", type=Path)
    ledger_transition.add_argument("task_id")
    ledger_transition.add_argument("target")
    admit = ledger_commands.add_parser("admit")
    admit.add_argument("ledger", type=Path)
    admit.add_argument("request", type=Path)
    ready = ledger_commands.add_parser("ready")
    ready.add_argument("ledger", type=Path)
    result = ledger_commands.add_parser("result")
    result.add_argument("ledger", type=Path)
    recover = ledger_commands.add_parser("recover")
    recover.add_argument("failure_kind")
    for operation in ("verification", "review", "touch", "external-evidence"):
        evidence = ledger_commands.add_parser(operation)
        evidence.add_argument("ledger", type=Path)
        evidence.add_argument("task_id")
        evidence.add_argument("request", type=Path)

    execute = namespaces.add_parser("execute")
    execute_commands = execute.add_subparsers(dest="operation", required=True)
    bind = execute_commands.add_parser("bind")
    bind.add_argument("ledger", type=Path)
    bind.add_argument("task_id")
    bind.add_argument("request", type=Path)

    lifecycle = namespaces.add_parser("lifecycle")
    lifecycle_commands = lifecycle.add_subparsers(dest="operation", required=True)
    classify = lifecycle_commands.add_parser("classify")
    classify.add_argument("request", type=Path)
    advance = lifecycle_commands.add_parser("next")
    advance.add_argument("request", type=Path)

    external_touch = namespaces.add_parser("external-touch", add_help=False)
    external_touch.add_argument("external_arguments", nargs=argparse.REMAINDER)
    return root


def _emit(value: object, stream: TextIO = sys.stdout) -> None:
    print(json.dumps(value, sort_keys=True, separators=(",", ":")), file=stream)


def _error(error: HarnessError) -> NoReturn:
    _emit({"status": "error", "code": error.code, "message": str(error)}, sys.stderr)
    raise SystemExit(2)


def _read_request(path: Path) -> dict[str, object]:
    """Read one complete JSON request without scalar extraction helpers."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HarnessError("invalid-json-request", f"cannot read JSON request: {path}") from error
    if not isinstance(value, dict):
        raise HarnessError("invalid-json-request", "JSON request root must be an object")
    return value


def _read_object_array(path: Path) -> list[dict[str, object]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HarnessError("invalid-json-request", f"cannot read JSON array: {path}") from error
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise HarnessError("invalid-json-request", "JSON request must be an object array")
    return value


def _required_string(request: dict[str, object], field: str) -> str:
    value = request.get(field)
    if not isinstance(value, str) or not value:
        raise HarnessError("invalid-json-request", f"JSON request requires {field}")
    return value


def _string_array(request: dict[str, object], field: str) -> tuple[str, ...]:
    value = request.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise HarnessError("invalid-json-request", f"JSON request requires {field} string array")
    return tuple(value)


def _required_bool(request: dict[str, object], field: str) -> bool:
    value = request.get(field)
    if not isinstance(value, bool):
        raise HarnessError("invalid-json-request", f"JSON request requires boolean {field}")
    return value


def _required_positive_int(request: Mapping[str, object], field: str) -> int:
    value = request.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise HarnessError("invalid-json-request", f"JSON request requires positive {field}")
    return value


def _optional_string(request: Mapping[str, object], field: str) -> str:
    value = request.get(field, "")
    if not isinstance(value, str):
        raise HarnessError("invalid-json-request", f"JSON request {field} must be a string")
    return value


def _optional_bool(request: Mapping[str, object], field: str, default: bool) -> bool:
    value = request.get(field, default)
    if not isinstance(value, bool):
        raise HarnessError("invalid-json-request", f"JSON request {field} must be boolean")
    return value


def _optional_int(request: Mapping[str, object], field: str) -> int | None:
    value = request.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise HarnessError("invalid-json-request", f"JSON request {field} must be an integer")
    return value


def _optional_mapping(request: Mapping[str, object], field: str) -> Mapping[str, object] | None:
    value = request.get(field)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise HarnessError("invalid-json-request", f"JSON request {field} must be an object")
    return value


def _repository_identity(plan_ref: Path) -> tuple[Path, str]:
    candidate = plan_ref.resolve().parent
    for parent in (candidate, *candidate.parents):
        if (parent / ".git").exists():
            result = subprocess.run(
                ["git", "-C", str(parent), "rev-parse", "HEAD"],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return parent, result.stdout.strip()
    return candidate, "unversioned"


def _file_identity(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _read_stable_review_brief(path: Path, expected_sha256: str) -> Path:
    """Hash one regular non-symlink brief through a stable open descriptor."""
    candidate = path.absolute()
    descriptor: int | None = None
    try:
        path_before = os.lstat(candidate)
        if stat.S_ISLNK(path_before.st_mode) or not stat.S_ISREG(path_before.st_mode):
            raise HarnessError(
                "controller_binding_review_invalid",
                "review brief must be a regular non-symlink file",
            )
        flags = os.O_RDONLY
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(candidate, flags)
        opened_before = os.fstat(descriptor)
        if not stat.S_ISREG(opened_before.st_mode) or _file_identity(
            opened_before
        ) != _file_identity(path_before):
            raise HarnessError(
                "controller_binding_review_invalid", "review brief identity changed while opening"
            )
        digest = hashlib.sha256()
        while payload := os.read(descriptor, 64 * 1024):
            digest.update(payload)
        opened_after = os.fstat(descriptor)
        path_after = os.lstat(candidate)
        if (
            _file_identity(opened_after) != _file_identity(opened_before)
            or _file_identity(path_after) != _file_identity(opened_before)
        ):
            raise HarnessError(
                "controller_binding_review_invalid", "review brief identity changed while reading"
            )
        if digest.hexdigest() != expected_sha256:
            raise HarnessError("controller_binding_review_invalid", "review brief digest drifted")
        return candidate
    except HarnessError:
        raise
    except OSError as error:
        raise HarnessError(
            "controller_binding_review_invalid", "review brief is unreadable"
        ) from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _binding_request(
    request: dict[str, object], ledger_path: Path, task_id: str
) -> tuple[BindingRequest, str | None, Path | None, Path | None]:
    """Bind runtime-only input to one immutable ledger task and artifact identity."""
    allowed = {
        "backend",
        "binding_kind",
        "command_job",
        "controller_id",
        "minimum_reasoning_effort",
        "model_policy",
        "parent_reasoning_effort",
        "physical_binding",
        "requested_model",
        "requested_reasoning_effort",
        "required_uplift_supported",
        "review_brief_ref",
        "review_brief_sha256",
        "run_id",
        "run_nonce",
        "spawn_cwd_supported",
    }
    unknown = set(request).difference(allowed)
    if unknown:
        raise HarnessError(
            "invalid-json-request", f"binding request has unsupported keys: {sorted(unknown)}"
        )
    ledger = read_ledger(ledger_path)
    binding_kind = _required_string(request, "binding_kind")
    if ledger.data.get("ledger_version") != 4:
        raise HarnessError(
            "legacy-ledger-read-only", "version-3 ledger authority cannot emit bindings"
        )
    ledger_admission: Mapping[str, object] | None = None
    if binding_kind == "bounded-review":
        verify_artifact_digests(ledger)
        if ledger.data.get("lifecycle_state") != "task-complete":
            raise HarnessError(
                "controller_binding_review_not_ready",
                "bounded review requires converged task work",
            )
        review_ref = Path(_required_string(request, "review_brief_ref"))
        review_sha256 = _required_string(request, "review_brief_sha256")
        review_ref = _read_stable_review_brief(review_ref, review_sha256)
        task = {
            "task_id": task_id,
            "depends_on": [],
            "touch_set": [],
            "external_impl_file_refs": [],
            "verification_commands": [],
            "scope_slice": "Bounded implementation review.",
            "executor_mode": "subagent",
            "parallel_group": "none",
            "parallel_policy": "forbidden",
            "delegation_policy": "allowed",
            "execution_profile": "deep",
            "reasoning_profile": "deep",
            "isolation": "shared-read-only",
            "resource_locks": ["implementation-review"],
            "convergence_required": True,
            "review_budget": 1,
            "task_review_depth": "full",
            "done_when": ["Candidate findings are returned."],
            "failure_policy": "fix_forward",
            "rollback_trigger": "",
            "rollback_target": "",
            "rollback_verification": "",
            "status": "ready",
            "attempt": 1,
            "review_brief_ref": str(review_ref),
            "review_brief_sha256": review_sha256,
        }
    elif binding_kind == "command-job":
        if "review_brief_ref" in request or "review_brief_sha256" in request:
            raise HarnessError("invalid-json-request", "review brief fields require bounded-review")
        command_job = _optional_mapping(request, "command_job")
        provenance = command_job.get("provenance") if command_job is not None else None
        if isinstance(provenance, dict) and provenance.get("kind") == "gate":
            if command_job is None:  # pragma: no cover - narrowed by provenance above.
                raise HarnessError(
                    "controller_binding_command_job_invalid", "command job is required"
                )
            allowed_gates = {
                "implementation-verification",
                "implementation-review",
                "truth-sync",
                "close",
            }
            gate_id = provenance.get("gate_id")
            if gate_id not in allowed_gates or task_id != gate_id:
                raise HarnessError("controller_binding_command_job_invalid", "gate id is invalid")
            verify_artifact_digests(ledger)
            if ledger.data.get("lifecycle_state") != "task-complete":
                raise HarnessError(
                    "controller_binding_task_not_ready", "gate command requires converged tasks"
                )
            locks = command_job.get("resource_locks")
            if not isinstance(locks, list):
                raise HarnessError(
                    "controller_binding_command_job_invalid", "gate resource locks are required"
                )
            task = {
                "task_id": gate_id,
                "depends_on": [],
                "touch_set": [],
                "external_impl_file_refs": [],
                "verification_commands": [],
                "scope_slice": "Approved lifecycle gate command.",
                "executor_mode": "main-agent",
                "parallel_group": "none",
                "parallel_policy": "forbidden",
                "delegation_policy": "forbidden",
                "execution_profile": "fast",
                "reasoning_profile": "light",
                "isolation": "shared-read-only",
                "resource_locks": locks,
                "convergence_required": True,
                "review_budget": 0,
                "task_review_depth": "none",
                "done_when": ["Gate command completes."],
                "failure_policy": "fix_forward",
                "rollback_trigger": "",
                "rollback_target": "",
                "rollback_verification": "",
                "status": "gate-ready",
                "attempt": 1,
            }
        else:
            task = task_binding_projection(ledger, task_id)
            ledger_admission = _optional_mapping(task, "admission")
            task = {key: value for key, value in task.items() if key != "admission"}
    else:
        if "review_brief_ref" in request or "review_brief_sha256" in request:
            raise HarnessError("invalid-json-request", "review brief fields require bounded-review")
        task = task_binding_projection(ledger, task_id)
        ledger_admission = _optional_mapping(task, "admission")
        task = {key: value for key, value in task.items() if key != "admission"}
    backend = request.get("backend")
    if backend is not None and not isinstance(backend, str):
        raise HarnessError("invalid-json-request", "backend must be a string")
    plan_ref_value = ledger.data.get("plan_ref")
    plan_sha256 = ledger.data.get("plan_sha256")
    if not isinstance(plan_ref_value, str) or not isinstance(plan_sha256, str):
        raise HarnessError("invalid-ledger", "ledger plan identity is malformed")
    plan_ref = Path(plan_ref_value)
    repository, revision = _repository_identity(plan_ref)
    ledger_sha256 = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    capabilities: Mapping[str, object] = {}
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    if backend in {None, "codex-native"}:
        capabilities = load_codex_capabilities(codex_home / "config.toml")
    role = derive_runtime_role(_required_string(request, "binding_kind"), task)
    max_depth_value = capabilities.get("max_depth")
    concurrency_value = capabilities.get("concurrency_ceiling")
    model_policy = _required_string(request, "model_policy")
    requested_model = _optional_string(request, "requested_model")
    requested_effort = _optional_string(request, "requested_reasoning_effort")
    if model_policy == "semantic-routing":
        resolution_source = "per-spawn" if requested_model or requested_effort else "parent-inherit"
    elif model_policy == "runtime-default" and capabilities.get("default_reasoning_effort"):
        resolution_source = "agents-defaults"
    else:
        resolution_source = "parent-inherit"
    return (
        BindingRequest(
            binding_kind=binding_kind,
            controller_id=_required_string(request, "controller_id"),
            run_id=_required_string(request, "run_id"),
            run_nonce=_required_string(request, "run_nonce"),
            model_policy=model_policy,
            task=task,
            provenance={
                "canonical_repository": str(repository),
                "repository_revision": revision,
                "plan_ref": str(plan_ref.resolve()),
                "plan_sha256": plan_sha256,
                "ledger_ref": str(ledger_path.resolve()),
                "ledger_sha256": ledger_sha256,
                "batch": ledger_admission,
            },
            parent_reasoning_effort=_required_string(request, "parent_reasoning_effort"),
            minimum_reasoning_effort=_required_string(request, "minimum_reasoning_effort"),
            requested_model=requested_model,
            requested_reasoning_effort=requested_effort,
            default_reasoning_effort=str(capabilities.get("default_reasoning_effort", "")),
            resolution_source=resolution_source,
            multi_agent_enabled=capabilities.get("multi_agent_enabled", True) is True,
            max_depth=max_depth_value if isinstance(max_depth_value, int) else None,
            concurrency_ceiling=(concurrency_value if isinstance(concurrency_value, int) else None),
            spawn_cwd_supported=_optional_bool(request, "spawn_cwd_supported", True),
            required_uplift_supported=_optional_bool(request, "required_uplift_supported", True),
            batch_provenance=ledger_admission,
            command_job=_optional_mapping(request, "command_job"),
            herdr_physical_binding=_optional_mapping(request, "physical_binding"),
        ),
        backend,
        repository / ".codex" / "agents" / f"{role}.toml",
        codex_home / "agents" / f"{role}.toml",
    )


def _ledger_result(path: Path, ledger: object) -> dict[str, object]:
    data = getattr(ledger, "data", None)
    if not isinstance(data, dict):
        raise HarnessError("invalid-ledger", "ledger result is malformed")
    return {"status": "ok", "ledger_path": str(path), "ledger": data}


def main(argv: list[str] | None = None) -> None:
    """Execute one complete validation or compilation operation in one Python process."""
    args = parser().parse_args(argv)
    try:
        if args.namespace == "external-touch":
            raise SystemExit(external_touch_main(args.external_arguments))
        if args.namespace == "plan" and args.operation == "compile":
            compiled = compile_plan(args.artifact)
            _emit(
                {
                    "status": "ok",
                    "projection": compiled.projection,
                    "projection_sha256": compiled.projection_sha256,
                    "source_digests": {
                        "design_sha256": compiled.design.sha256,
                        "plan_sha256": compiled.plan.sha256,
                    },
                }
            )
            return
        if args.namespace == "ledger" and args.operation == "init":
            ledger = initialize_ledger(args.plan)
            write_ledger(args.ledger, ledger)
            _emit(_ledger_result(args.ledger, ledger))
            return
        if args.namespace == "ledger" and args.operation == "transition":
            ledger = transition(read_ledger(args.ledger), args.task_id, args.target)
            write_ledger(args.ledger, ledger)
            _emit(_ledger_result(args.ledger, ledger))
            return
        if args.namespace == "ledger" and args.operation == "admit":
            request = _read_request(args.request)
            if set(request) != {"task_ids", "capacity"}:
                raise HarnessError("invalid-json-request", "admission request schema is not exact")
            ledger = admit_ready(
                read_ledger(args.ledger),
                _string_array(request, "task_ids"),
                capacity=_required_positive_int(request, "capacity"),
            )
            write_ledger(args.ledger, ledger)
            _emit(_ledger_result(args.ledger, ledger))
            return
        if args.namespace == "ledger" and args.operation == "ready":
            _emit({"status": "ok", "ready": list(ready_set(read_ledger(args.ledger)))})
            return
        if args.namespace == "ledger" and args.operation == "result":
            ledger = read_ledger(args.ledger)
            _emit(
                {
                    "status": "ok",
                    "lifecycle_state": ledger.data.get("lifecycle_state"),
                    "plan_sha256": ledger.data.get("plan_sha256"),
                    "design_sha256": ledger.data.get("design_sha256"),
                    "projection_sha256": ledger.data.get("projection_sha256"),
                    "projection": ledger.data.get("projection"),
                }
            )
            return
        if args.namespace == "ledger" and args.operation == "recover":
            _emit({"status": "ok", "route": recovery_route(args.failure_kind)})
            return
        if args.namespace == "ledger" and args.operation == "verification":
            request = _read_request(args.request)
            ledger = record_verification(
                read_ledger(args.ledger),
                args.task_id,
                _required_string(request, "command"),
                _required_bool(request, "passed"),
            )
            write_ledger(args.ledger, ledger)
            _emit(_ledger_result(args.ledger, ledger))
            return
        if args.namespace == "ledger" and args.operation == "review":
            request = _read_request(args.request)
            ledger = record_review(
                read_ledger(args.ledger),
                args.task_id,
                _required_bool(request, "accepted"),
                _required_string(request, "batch_id"),
            )
            write_ledger(args.ledger, ledger)
            _emit(_ledger_result(args.ledger, ledger))
            return
        if args.namespace == "ledger" and args.operation == "touch":
            request = _read_request(args.request)
            assert_task_touch_set(
                read_ledger(args.ledger),
                args.task_id,
                _string_array(request, "changed_paths"),
            )
            _emit({"status": "ok", "task_id": args.task_id})
            return
        if args.namespace == "ledger" and args.operation == "external-evidence":
            request = _read_request(args.request)
            if set(request) != {"baseline_ref", "intents_ref"}:
                raise HarnessError(
                    "invalid-json-request", "external evidence request schema is not exact"
                )
            baseline = _read_request(Path(_required_string(request, "baseline_ref")))
            intents = _read_object_array(Path(_required_string(request, "intents_ref")))
            ledger = record_external_evidence(
                read_ledger(args.ledger), args.task_id, baseline, intents
            )
            write_ledger(args.ledger, ledger)
            _emit(_ledger_result(args.ledger, ledger))
            return
        if args.namespace == "execute" and args.operation == "bind":
            request, backend, project_role_file, user_role_file = _binding_request(
                _read_request(args.request), args.ledger, args.task_id
            )
            envelope = binding_envelope(
                request,
                backend=backend,
                project_role_file=project_role_file,
                user_role_file=user_role_file,
            )
            _emit({"status": "ok", "envelope": envelope})
            return
        if args.namespace == "lifecycle" and args.operation == "classify":
            _emit(
                {
                    "status": "ok",
                    "classification": classify_request(_read_request(args.request)),
                }
            )
            return
        if args.namespace == "lifecycle" and args.operation == "next":
            _emit(
                {
                    "status": "ok",
                    "transition": next_phase(_read_request(args.request)),
                }
            )
            return
        if args.namespace == "truth-sync" and args.operation == "evaluate":
            decision = truth_sync_decision(
                read_ledger(args.ledger),
                validate_artifact(args.request, "truth-sync"),
                args.ledger,
            )
            _emit({"status": "ok", "decision": decision})
            return
        if args.namespace == "close" and args.operation == "evaluate":
            decision = close_decision(
                read_ledger(args.ledger),
                validate_artifact(args.request, "close"),
                args.ledger,
            )
            _emit({"status": "ok", "decision": decision})
            return
        artifact = validate_artifact(args.artifact, args.namespace)
        _emit({"status": "ok", "artifact_kind": artifact.artifact_kind, "sha256": artifact.sha256})
    except HarnessError as error:
        _error(error)


if __name__ == "__main__":
    main()
