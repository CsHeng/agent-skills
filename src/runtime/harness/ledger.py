"""Digest-bound task ledger state and lifecycle decisions for the Python harness."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from .artifacts import Artifact, CompiledPlan, HarnessError, Scope, compile_plan, parse_artifact
from .external_touch import (
    ExternalTouchError,
    compare_manifest,
    validate_evidence_state,
)

LEDGER_VERSION = 3
TERMINAL_TASK_STATES = frozenset({"converged", "failed"})
TASK_STATES = frozenset(
    {"pending", "ready", "in-progress", "verified", "reviewed", "converged", "failed"}
)
ALLOWED_TRANSITIONS = {
    "pending": {"ready"},
    "ready": {"in-progress"},
    "in-progress": {"verified", "failed"},
    "verified": {"reviewed", "failed"},
    "reviewed": {"converged", "in-progress", "failed"},
    "converged": set(),
    "failed": set(),
}
RECOVERY_ROUTES = {
    "requirement-ambiguity": "clarify",
    "truth-conflict": "truth-scan",
    "boundary-mismatch": "design-full",
    "plan-incompleteness": "plan",
    "parallel-conflict": "dependency-freeze",
    "verification-failure": "implement-serial",
    "truth-sync-failure": "truth-sync",
}
MUTABLE_TASK_FIELDS = frozenset(
    {
        "status",
        "verification_evidence",
        "review",
        "review_history",
        "external_evidence",
        "repair_attempts",
        "batch_provenance",
    }
)


@dataclass(frozen=True)
class Ledger:
    """Validated, immutable-in-shape task state for one compiled plan."""

    data: Mapping[str, object]


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scope_dict(scope: Scope) -> dict[str, list[str]]:
    return {
        "impl_file_refs": list(scope.impl_file_refs),
        "test_file_refs": list(scope.test_file_refs),
        "external_impl_file_refs": list(scope.external_impl_file_refs),
    }


def _task_statuses(compiled: CompiledPlan) -> list[dict[str, object]]:
    projection_tasks = compiled.projection.get("tasks")
    if not isinstance(projection_tasks, list) or not all(
        isinstance(task, dict) for task in projection_tasks
    ):
        raise HarnessError("invalid-plan-projection", "compiled task projection is malformed")
    statuses: list[dict[str, object]] = []
    for projected, compiled_task in zip(projection_tasks, compiled.tasks, strict=True):
        statuses.append(
            {
                **projected,
                "status": "ready" if not compiled_task.depends_on else "pending",
                "verification_evidence": [],
                "review": None,
                "review_history": [],
                "external_evidence": [],
                "repair_attempts": 0,
                "batch_provenance": None,
            }
        )
    return statuses


def _portable_ref(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(resolved)


def initialize_ledger(plan_path: Path) -> Ledger:
    """Compile a plan once and initialize the immutable ledger projection."""
    compiled = compile_plan(plan_path)
    if compiled.design.metadata.get("approval_status") != "approved":
        raise HarnessError("artifact-not-approved", "design approval is required")
    if compiled.plan.metadata.get("approval_status") != "approved":
        raise HarnessError("artifact-not-approved", "plan approval is required")
    return Ledger(
        {
            "ledger_version": LEDGER_VERSION,
            "plan_ref": _portable_ref(compiled.plan.path),
            "design_ref": _portable_ref(compiled.design.path),
            "plan_sha256": compiled.plan.sha256,
            "design_sha256": compiled.design.sha256,
            "projection": compiled.projection,
            "projection_sha256": compiled.projection_sha256,
            "tasks": _task_statuses(compiled),
            "lifecycle_state": "implementation-pending",
        }
    )


def _canonical(data: Mapping[str, object]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def write_ledger(path: Path, ledger: Ledger) -> None:
    """Durably replace a ledger using file and parent-directory fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(_canonical(ledger.data))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise HarnessError(
            "ledger-write-failed", f"cannot atomically replace ledger: {path}"
        ) from error


def read_ledger(path: Path) -> Ledger:
    """Read a ledger once and validate its shape without parsing linked artifacts."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HarnessError("invalid-ledger", f"cannot read ledger: {path}") from error
    if not isinstance(data, dict) or data.get("ledger_version") != LEDGER_VERSION:
        raise HarnessError("invalid-ledger", "unsupported ledger version")
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        raise HarnessError("invalid-ledger", "ledger tasks must be a list")
    ledger = Ledger(data)
    _validate_projection(ledger)
    return ledger


def _validate_projection(ledger: Ledger) -> None:
    projection = ledger.data.get("projection")
    expected = ledger.data.get("projection_sha256")
    if not isinstance(projection, dict) or not isinstance(expected, str):
        raise HarnessError("ledger-projection-drift", "ledger projection binding is malformed")
    observed = hashlib.sha256(_canonical(projection)).hexdigest()
    if observed != expected:
        raise HarnessError("ledger-projection-drift", "ledger projection digest drifted")
    projection_tasks = projection.get("tasks")
    tasks = ledger.data.get("tasks")
    if not isinstance(projection_tasks, list) or not isinstance(tasks, list):
        raise HarnessError("ledger-projection-drift", "ledger projection task shape is malformed")
    if len(projection_tasks) != len(tasks):
        raise HarnessError("ledger-projection-drift", "ledger task count drifted")
    for projected, task in zip(projection_tasks, tasks, strict=True):
        if not isinstance(projected, dict) or not isinstance(task, dict):
            raise HarnessError("ledger-projection-drift", "ledger task shape drifted")
        immutable = {key: value for key, value in task.items() if key not in MUTABLE_TASK_FIELDS}
        if immutable != projected:
            raise HarnessError(
                "ledger-projection-drift",
                f"ledger immutable task projection drifted: {projected.get('task_id')}",
            )


def verify_artifact_digests(ledger: Ledger) -> None:
    """Check linked artifact bytes only; later transitions never reparse a plan."""
    _validate_projection(ledger)
    data = ledger.data
    for ref_key, digest_key in (("plan_ref", "plan_sha256"), ("design_ref", "design_sha256")):
        reference = data.get(ref_key)
        expected = data.get(digest_key)
        if not isinstance(reference, str) or not isinstance(expected, str):
            raise HarnessError("invalid-ledger", "ledger artifact binding is malformed")
        try:
            observed = _sha256_path(Path(reference))
        except OSError as error:
            raise HarnessError(
                "artifact-digest-drift", f"cannot hash linked artifact: {reference}"
            ) from error
        if observed != expected:
            raise HarnessError(
                "artifact-digest-drift", f"linked artifact digest drifted: {reference}"
            )


def _tasks(ledger: Ledger) -> list[dict[str, object]]:
    tasks = ledger.data["tasks"]
    if not isinstance(tasks, list) or not all(isinstance(task, dict) for task in tasks):
        raise HarnessError("invalid-ledger", "ledger task shape is invalid")
    return tasks


def _copy_data(ledger: Ledger) -> dict[str, object]:
    return json.loads(_canonical(ledger.data))


def _find_task(tasks: list[dict[str, object]], task_id: str) -> dict[str, object]:
    for task in tasks:
        if task.get("task_id") == task_id:
            return task
    raise HarnessError("unknown-task", f"task does not exist: {task_id}")


def transition(ledger: Ledger, task_id: str, target: str) -> Ledger:
    """Advance one task after digest validation and preserve ready-set ordering."""
    verify_artifact_digests(ledger)
    if target not in TASK_STATES:
        raise HarnessError("invalid-transition", f"unknown task state: {target}")
    data = _copy_data(ledger)
    tasks = _tasks(Ledger(data))
    task = _find_task(tasks, task_id)
    status = task.get("status")
    if not isinstance(status, str) or target not in ALLOWED_TRANSITIONS.get(status, set()):
        raise HarnessError(
            "invalid-transition", f"cannot transition {task_id} from {status} to {target}"
        )
    if target == "in-progress" and not _dependencies_converged(tasks, task):
        raise HarnessError("task-not-ready", f"dependencies are not converged: {task_id}")
    if target == "verified" and not _has_verification_evidence(task):
        raise HarnessError(
            "verification-evidence-required", f"verification evidence is required: {task_id}"
        )
    if target in {"reviewed", "converged"} and not _has_accepted_review(task):
        raise HarnessError("review-evidence-required", f"accepted review is required: {task_id}")
    if target == "converged" and not _has_complete_external_evidence(task):
        raise HarnessError(
            "external-evidence-required", f"complete external evidence is required: {task_id}"
        )
    task["status"] = target
    _refresh_ready(tasks)
    data["lifecycle_state"] = _lifecycle_state(tasks)
    return Ledger(data)


def _dependencies_converged(tasks: list[dict[str, object]], task: Mapping[str, object]) -> bool:
    dependencies = task.get("depends_on")
    if not isinstance(dependencies, list):
        raise HarnessError("invalid-ledger", "task dependencies are malformed")
    states = {item.get("task_id"): item.get("status") for item in tasks}
    return all(states.get(dependency) == "converged" for dependency in dependencies)


def _refresh_ready(tasks: list[dict[str, object]]) -> None:
    for task in tasks:
        if task.get("status") == "pending" and _dependencies_converged(tasks, task):
            task["status"] = "ready"


def ready_set(ledger: Ledger) -> tuple[str, ...]:
    """Return ready task IDs in immutable plan order after digest validation."""
    verify_artifact_digests(ledger)
    ready: list[str] = []
    for task in _tasks(ledger):
        task_id = task.get("task_id")
        if task.get("status") == "ready" and isinstance(task_id, str):
            ready.append(task_id)
    return tuple(ready)


def task_binding_projection(ledger: Ledger, task_id: str) -> dict[str, object]:
    """Derive a runtime task envelope only from digest-bound ledger authority."""
    verify_artifact_digests(ledger)
    task = _find_task(_tasks(ledger), task_id)
    scope = task.get("scope")
    if not isinstance(scope, dict):
        raise HarnessError("invalid-ledger", "task scope is malformed")
    impl_refs = scope.get("impl_file_refs")
    test_refs = scope.get("test_file_refs")
    attempts = task.get("repair_attempts")
    if (
        not isinstance(impl_refs, list)
        or not isinstance(test_refs, list)
        or not isinstance(attempts, int)
    ):
        raise HarnessError("invalid-ledger", "task binding state is malformed")
    projection = {
        key: value
        for key, value in task.items()
        if key not in MUTABLE_TASK_FIELDS and key != "scope"
    }
    projection.update(
        {
            "touch_set": [*impl_refs, *test_refs],
            "external_impl_file_refs": list(scope.get("external_impl_file_refs", [])),
            "status": task.get("status"),
            "attempt": attempts + 1,
        }
    )
    return projection


def _lifecycle_state(tasks: list[dict[str, object]]) -> str:
    if all(task.get("status") == "converged" for task in tasks):
        return "task-complete"
    return "implementation-pending"


def _has_verification_evidence(task: Mapping[str, object]) -> bool:
    evidence = task.get("verification_evidence")
    commands = task.get("verification_commands")
    if not isinstance(evidence, list) or not isinstance(commands, list) or not commands:
        return False
    attempts = task.get("repair_attempts")
    if not isinstance(attempts, int):
        return False
    active_attempt = attempts + 1
    passed = {
        item.get("command")
        for item in evidence
        if isinstance(item, dict)
        and item.get("passed") is True
        and item.get("attempt") == active_attempt
    }
    return passed == set(commands)


def _has_accepted_review(task: Mapping[str, object]) -> bool:
    review = task.get("review")
    return isinstance(review, dict) and review.get("status") == "accepted"


def record_verification(ledger: Ledger, task_id: str, command: str, passed: bool) -> Ledger:
    """Record one declared verification result before review may advance."""
    verify_artifact_digests(ledger)
    data = _copy_data(ledger)
    task = _find_task(_tasks(Ledger(data)), task_id)
    if task.get("status") != "in-progress":
        raise HarnessError(
            "verification-not-ready", f"verification requires an active task: {task_id}"
        )
    commands = task.get("verification_commands")
    if not isinstance(commands, list) or command not in commands:
        raise HarnessError("verification-command-violation", f"command is not declared: {command}")
    if not passed:
        raise HarnessError("verification-failed", f"verification failed: {command}")
    evidence = task.get("verification_evidence")
    if not isinstance(evidence, list):
        raise HarnessError("invalid-ledger", "verification evidence state is malformed")
    attempts = task.get("repair_attempts")
    if not isinstance(attempts, int):
        raise HarnessError("invalid-ledger", "task attempt state is malformed")
    active_attempt = attempts + 1
    if not any(
        isinstance(item, dict)
        and item.get("command") == command
        and item.get("attempt") == active_attempt
        for item in evidence
    ):
        evidence.append({"attempt": active_attempt, "command": command, "passed": True})
    return Ledger(data)


def record_review(ledger: Ledger, task_id: str, accepted: bool, batch_id: str) -> Ledger:
    """Record one bounded review decision; accepted repair is limited to one retry."""
    verify_artifact_digests(ledger)
    data = _copy_data(ledger)
    task = _find_task(_tasks(Ledger(data)), task_id)
    if task.get("status") != "verified" or not _has_verification_evidence(task):
        raise HarnessError("review-not-ready", f"review is not ready: {task_id}")
    if not batch_id:
        raise HarnessError("invalid-review-evidence", "review batch id is required")
    decision = {"batch_id": batch_id, "status": "accepted" if accepted else "rejected"}
    task["review"] = decision
    task["batch_provenance"] = {"batch_id": batch_id, "convergence_required": True}
    if not accepted:
        attempts = task.get("repair_attempts")
        review_budget = task.get("review_budget")
        if (
            not isinstance(attempts, int)
            or not isinstance(review_budget, int)
            or attempts >= review_budget
        ):
            raise HarnessError("repair-budget-exhausted", f"repair budget exhausted: {task_id}")
        task["repair_attempts"] = attempts + 1
        task["status"] = "in-progress"
        history = task.get("review_history")
        if not isinstance(history, list):
            raise HarnessError("invalid-ledger", "review history state is malformed")
        history.append(decision)
        task["verification_evidence"] = []
        task["external_evidence"] = []
        task["review"] = None
        task["batch_provenance"] = None
    return Ledger(data)


def assert_task_touch_set(ledger: Ledger, task_id: str, changed_paths: tuple[str, ...]) -> None:
    """Reject repository writes that are outside the exact task scope."""
    verify_artifact_digests(ledger)
    task = _find_task(_tasks(ledger), task_id)
    scope = task.get("scope")
    if not isinstance(scope, dict):
        raise HarnessError("invalid-ledger", "task scope is malformed")
    impl_refs = scope.get("impl_file_refs")
    test_refs = scope.get("test_file_refs")
    if not isinstance(impl_refs, list) or not isinstance(test_refs, list):
        raise HarnessError("invalid-ledger", "task repository scope is malformed")
    allowed = tuple(impl_refs + test_refs)
    for path in changed_paths:
        if not any(path == reference or path.startswith(f"{reference}/") for reference in allowed):
            raise HarnessError("touch-set-violation", f"path is outside task touch set: {path}")


def _repository_root(plan_ref: object) -> Path:
    if not isinstance(plan_ref, str):
        raise HarnessError("invalid-ledger", "ledger plan ref is malformed")
    start = Path(plan_ref).resolve().parent
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return start


def record_external_evidence(
    ledger: Ledger,
    task_id: str,
    baseline: Mapping[str, object],
    intents: Sequence[Mapping[str, object]],
) -> Ledger:
    """Validate complete broker evidence and retain only its metadata summary."""
    verify_artifact_digests(ledger)
    data = _copy_data(ledger)
    task = _find_task(_tasks(Ledger(data)), task_id)
    if task.get("status") != "in-progress":
        raise HarnessError(
            "external-evidence-not-ready", f"external evidence requires an active task: {task_id}"
        )
    scope = task.get("scope")
    if not isinstance(scope, dict):
        raise HarnessError("invalid-ledger", "task external scope is malformed")
    refs = scope.get("external_impl_file_refs")
    run_id = baseline.get("run_id")
    if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
        raise HarnessError("invalid-ledger", "task external refs are malformed")
    if not refs:
        raise HarnessError("external-touch-violation", "task has no declared external refs")
    if not isinstance(run_id, str) or not run_id:
        raise HarnessError("invalid-external-evidence", "external baseline run id is missing")
    try:
        state = validate_evidence_state(
            baseline=baseline,
            intents=intents,
            expected_task_id=task_id,
            expected_run_id=run_id,
            expected_design_sha256=str(data.get("design_sha256", "")),
            expected_plan_sha256=str(data.get("plan_sha256", "")),
            expected_refs=refs,
            require_applied=True,
            require_cleanup=True,
            check_cleanup_paths=True,
        )
        manifest = compare_manifest(
            repo_root=_repository_root(data.get("plan_ref")),
            baseline=baseline,
            intents=intents,
        )
    except ExternalTouchError as error:
        raise HarnessError(error.code, str(error)) from error
    existing = task.get("external_evidence")
    attempts = task.get("repair_attempts")
    if not isinstance(existing, list) or not isinstance(attempts, int):
        raise HarnessError("invalid-ledger", "external evidence state is malformed")
    manifest_refs = manifest.get("refs")
    if not isinstance(manifest_refs, list):
        raise HarnessError("invalid-external-evidence", "external manifest is malformed")
    task["external_evidence"] = [
        {
            "attempt": attempts + 1,
            "run_id": run_id,
            "state": state.get("state"),
            "intent_count": state.get("intent_count"),
            "refs": [
                {
                    "ref": item.get("ref"),
                    "sha256": (
                        item.get("after", {}).get("sha256")
                        if isinstance(item, dict) and isinstance(item.get("after"), dict)
                        else None
                    ),
                    "applied_intent_count": item.get("applied_intent_count")
                    if isinstance(item, dict)
                    else None,
                }
                for item in manifest_refs
            ],
        }
    ]
    return Ledger(data)


def _has_complete_external_evidence(task: Mapping[str, object]) -> bool:
    scope = task.get("scope")
    if not isinstance(scope, dict):
        return False
    declared = scope.get("external_impl_file_refs")
    if not isinstance(declared, list):
        return False
    if not declared:
        return True
    evidence = task.get("external_evidence")
    if not isinstance(evidence, list) or len(evidence) != 1:
        return False
    result = evidence[0]
    attempts = task.get("repair_attempts")
    if (
        not isinstance(result, dict)
        or not isinstance(attempts, int)
        or result.get("attempt") != attempts + 1
        or result.get("state") != "valid"
    ):
        return False
    refs = result.get("refs")
    return (
        isinstance(refs, list)
        and sorted(item.get("ref") for item in refs if isinstance(item, dict)) == sorted(declared)
        and all(
            isinstance(item, dict)
            and isinstance(item.get("sha256"), str)
            and item.get("applied_intent_count", 0) >= 1
            for item in refs
        )
    )


def recovery_route(failure_kind: str) -> str:
    """Return the typed recovery route without widening from failure count."""
    try:
        return RECOVERY_ROUTES[failure_kind]
    except KeyError as error:
        raise HarnessError(
            "unknown-recovery-kind", f"unknown recovery failure: {failure_kind}"
        ) from error


def _linked_file(artifact: Artifact, reference: object) -> Path:
    if not isinstance(reference, str):
        raise HarnessError("invalid-artifact-link", "artifact link is missing")
    candidate = (artifact.path.parent / reference).resolve()
    try:
        candidate.relative_to(artifact.path.parent.resolve())
    except ValueError as error:
        raise HarnessError("invalid-artifact-link", "artifact link escapes its root") from error
    return candidate


def _projection_value(ledger: Ledger, key: str) -> object:
    projection = ledger.data.get("projection")
    if not isinstance(projection, dict):
        raise HarnessError("ledger-projection-drift", "ledger projection is malformed")
    return projection.get(key)


def _validate_ledger_and_execution_evidence(
    ledger: Ledger, artifact: Artifact, ledger_path: Path
) -> None:
    metadata = artifact.metadata
    if _linked_file(artifact, metadata.get("ledger_ref")) != ledger_path.resolve():
        raise HarnessError("truth-sync-ledger-mismatch", "ledger ref drifted")
    expected_ledger = hashlib.sha256(_canonical(ledger.data)).hexdigest()
    if metadata.get("ledger_sha256") != expected_ledger:
        raise HarnessError("truth-sync-ledger-mismatch", "ledger digest drifted")
    execution_result = _linked_file(artifact, metadata.get("execution_result_ref"))
    try:
        execution_digest = _sha256_path(execution_result)
    except OSError as error:
        raise HarnessError("invalid-artifact-link", "execution result is unreadable") from error
    if execution_digest != metadata.get("execution_result_sha256"):
        raise HarnessError("execution-result-digest-mismatch", "execution result digest drifted")
    try:
        result_data = json.loads(execution_result.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HarnessError("invalid-execution-result", "execution result is invalid") from error
    expected_result = {
        "status": "passed",
        "review_status": "passed",
        "verification_status": "passed",
        "plan_sha256": ledger.data.get("plan_sha256"),
        "design_sha256": ledger.data.get("design_sha256"),
        "projection_sha256": ledger.data.get("projection_sha256"),
    }
    if not isinstance(result_data, dict) or any(
        result_data.get(key) != value for key, value in expected_result.items()
    ):
        raise HarnessError("invalid-execution-result", "execution result evidence is incomplete")


def truth_sync_decision(
    ledger: Ledger, truth_sync: Artifact | None, ledger_path: Path | None = None
) -> str:
    """Return the next gate only from digest-linked human approval evidence."""
    verify_artifact_digests(ledger)
    if _lifecycle_state(_tasks(ledger)) != "task-complete":
        return "implementation-pending"
    required = _projection_value(ledger, "truth_sync_required")
    if required is not True:
        return "ready-for-close"
    if truth_sync is None:
        return "truth-sync-pending"
    if truth_sync.artifact_kind != "truth-sync":
        raise HarnessError("invalid-artifact-kind", "truth-sync evidence is required")
    metadata = truth_sync.metadata
    if ledger_path is None:
        raise HarnessError("truth-sync-ledger-mismatch", "ledger path evidence is required")
    _validate_ledger_and_execution_evidence(ledger, truth_sync, ledger_path)
    scope = metadata.get("scope")
    stable_truth_refs = _projection_value(ledger, "stable_truth_refs")
    if (
        not isinstance(scope, dict)
        or scope.get("impl_file_refs") != stable_truth_refs
        or scope.get("test_file_refs") != []
        or scope.get("external_impl_file_refs") != []
    ):
        raise HarnessError("truth-sync-scope-mismatch", "truth-sync scope drifted")
    return (
        "ready-for-close" if metadata.get("approval_status") == "approved" else "truth-sync-pending"
    )


def close_decision(ledger: Ledger, close: Artifact, ledger_path: Path) -> str:
    """Fail closed against linked truth or direct non-truth execution evidence."""
    if close.artifact_kind != "close":
        raise HarnessError("invalid-artifact-kind", "close evidence is required")
    required = _projection_value(ledger, "truth_sync_required")
    if required is True:
        truth_path = _linked_file(close, close.metadata.get("truth_sync_ref"))
        truth = parse_artifact(truth_path)
        if truth.sha256 != close.metadata.get("truth_sync_sha256"):
            raise HarnessError("truth-sync-digest-mismatch", "linked truth-sync digest drifted")
        state = truth_sync_decision(ledger, truth, ledger_path)
    else:
        verify_artifact_digests(ledger)
        if _lifecycle_state(_tasks(ledger)) != "task-complete":
            state = "implementation-pending"
        else:
            _validate_ledger_and_execution_evidence(ledger, close, ledger_path)
            state = "ready-for-close"
    if (
        state == "ready-for-close"
        and close.metadata.get("approval_status") == "approved"
        and close.metadata.get("decision") == "ready-for-close"
    ):
        return "closed"
    return "blocked"
