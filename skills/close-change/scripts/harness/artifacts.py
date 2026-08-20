"""Typed parsing and compilation for versioned lifecycle artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

FRONT_MATTER_DELIMITER = "+++"
CONTRACT_VERSION = 4
SUPPORTED_CONTRACT_VERSIONS = frozenset({3, 4})
ARTIFACT_KINDS = frozenset({"design", "plan", "truth-sync", "close"})
BODY_HEADINGS: dict[int, dict[str, tuple[str, ...]]] = {
    3: {
        "design": ("# Design", "## Problem", "## Goals", "## Boundaries"),
        "plan": ("# Plan", "## Implementation"),
        "truth-sync": ("# Truth Sync", "## Scope"),
        "close": ("# Close", "## Decision"),
    },
    4: {
        "design": ("# Design", "## Problem", "## Goals", "## Boundaries"),
        "plan": (
            "# Plan",
            "## Implementation",
            "## Work Package Readiness",
            "## Execution Continuity",
            "## Recovery",
            "## Truth Sync Handoff",
        ),
        "truth-sync": (
            "# Truth Sync",
            "## Scope",
            "## Evidence",
            "## Stable Truth Updates",
            "## Human Gate",
        ),
        "close": ("# Close", "## Decision"),
    },
}
ReadBytes = Callable[[Path], bytes]
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_GLOB_CHARACTERS = frozenset("*?[]")


class HarnessError(ValueError):
    """A deterministic artifact-contract failure with a machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Scope:
    """Repository and exact external write references declared by an artifact."""

    impl_file_refs: tuple[str, ...]
    test_file_refs: tuple[str, ...]
    external_impl_file_refs: tuple[str, ...]

    @property
    def repository_refs(self) -> tuple[str, ...]:
        """Return all repository-owned write references in declaration order."""
        return self.impl_file_refs + self.test_file_refs

    @property
    def all_refs(self) -> tuple[str, ...]:
        """Return repository and exact external write references."""
        return self.repository_refs + self.external_impl_file_refs


@dataclass(frozen=True)
class Artifact:
    """One parsed artifact and its human-facing Markdown body."""

    path: Path
    artifact_kind: str
    metadata: Mapping[str, object]
    body: str
    sha256: str

    @property
    def contract_version(self) -> int:
        """Return the validated artifact contract version."""
        version = self.metadata["contract_version"]
        if not isinstance(version, int):  # pragma: no cover - validated at construction.
            raise AssertionError("validated contract version is not an integer")
        return version


@dataclass(frozen=True)
class Task:
    """The immutable plan task shape needed before ledger initialization."""

    task_id: str
    depends_on: tuple[str, ...]
    scope: Scope
    verification_commands: tuple[str, ...]
    scope_slice: str
    executor_mode: str
    parallel_group: str
    parallel_policy: str
    delegation_policy: str
    execution_profile: str
    reasoning_profile: str
    isolation: str
    resource_locks: tuple[str, ...]
    convergence_required: bool
    review_budget: int
    task_review_depth: str
    done_when: tuple[str, ...]
    failure_policy: str
    rollback_trigger: str
    rollback_target: str
    rollback_verification: str


@dataclass(frozen=True)
class ParallelBatch:
    """One dependency-frozen named batch compiled into plan authority."""

    batch_id: str
    tasks: tuple[str, ...]
    max_parallelism: int
    convergence_task: str


@dataclass(frozen=True)
class CompiledPlan:
    """A design-contained plan projection with content-addressed source artifacts."""

    design: Artifact
    plan: Artifact
    tasks: tuple[Task, ...]
    parallel_batches: tuple[ParallelBatch, ...]
    projection: Mapping[str, object]
    projection_sha256: str


class ReadTracker:
    """Wrap byte reads so tests can prove one read per parse operation."""

    def __init__(self, reader: ReadBytes | None = None) -> None:
        self._reader = reader or _read_bytes
        self.counts: dict[Path, int] = {}

    def read(self, path: Path) -> bytes:
        """Read a path once and increment its observable count."""
        resolved = path.resolve()
        self.counts[resolved] = self.counts.get(resolved, 0) + 1
        return self._reader(resolved)


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _required_string(metadata: Mapping[str, object], key: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value:
        raise HarnessError("invalid-artifact", f"{key} must be a non-empty string")
    return value


def _required_string_list(metadata: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = metadata.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise HarnessError("invalid-artifact", f"{key} must be a list of non-empty strings")
    result = tuple(value)
    if len(result) != len(set(result)):
        raise HarnessError("invalid-artifact", f"{key} must not contain duplicates")
    return result


def _required_bool(metadata: Mapping[str, object], key: str) -> bool:
    value = metadata.get(key)
    if not isinstance(value, bool):
        raise HarnessError("invalid-artifact", f"{key} must be a boolean")
    return value


def _required_positive_int(metadata: Mapping[str, object], key: str) -> int:
    value = metadata.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise HarnessError("invalid-artifact", f"{key} must be a positive integer")
    return value


def _required_choice(metadata: Mapping[str, object], key: str, choices: frozenset[str]) -> str:
    value = _required_string(metadata, key)
    if value not in choices:
        raise HarnessError("invalid-artifact", f"{key} has unsupported value: {value}")
    return value


def _required_sha256(metadata: Mapping[str, object], key: str) -> str:
    value = _required_string(metadata, key)
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise HarnessError("invalid-artifact", f"{key} must be a lowercase SHA-256 digest")
    return value


def _optional_string_field(metadata: Mapping[str, object], key: str) -> str:
    value = metadata.get(key, "")
    if not isinstance(value, str):
        raise HarnessError("invalid-artifact", f"{key} must be a string")
    return value


def _mapping(value: object, key: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(name, str) for name in value):
        raise HarnessError("invalid-artifact", f"{key} must be a TOML table")
    return value


def validate_repository_ref(reference: str) -> str:
    """Return one safe normalized repository-relative reference."""
    segments = reference.split("/")
    if (
        not reference
        or reference.startswith("/")
        or bool(PureWindowsPath(reference).drive)
        or "\\" in reference
        or any(segment in {"", ".", ".."} for segment in segments)
        or any(ord(character) < 32 or ord(character) == 127 for character in reference)
        or any(character in _GLOB_CHARACTERS for character in reference)
    ):
        raise HarnessError("unsafe-repository-ref", f"unsafe repository reference: {reference}")
    return reference


def _validate_external_ref(reference: str) -> str:
    path = Path(reference)
    if not path.is_absolute() or ".." in path.parts:
        raise HarnessError("unsafe-external-ref", f"unsafe external reference: {reference}")
    return str(path)


def _scope(metadata: Mapping[str, object]) -> Scope:
    scope = _mapping(metadata.get("scope"), "scope")
    allowed_keys = {"impl_file_refs", "test_file_refs", "external_impl_file_refs"}
    unknown = set(scope).difference(allowed_keys)
    if unknown:
        raise HarnessError("invalid-artifact", f"scope has unsupported keys: {sorted(unknown)}")
    impl_refs = tuple(
        validate_repository_ref(item) for item in _required_string_list(scope, "impl_file_refs")
    )
    test_refs = tuple(
        validate_repository_ref(item) for item in _required_string_list(scope, "test_file_refs")
    )
    external_refs = tuple(
        _validate_external_ref(item)
        for item in _required_string_list(scope, "external_impl_file_refs")
    )
    combined = impl_refs + test_refs
    if len(combined) != len(set(combined)):
        raise HarnessError("invalid-artifact", "scope repository refs must not overlap")
    return Scope(impl_refs, test_refs, external_refs)


def _split_front_matter(text: str) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != FRONT_MATTER_DELIMITER:
        raise HarnessError(
            "invalid-front-matter", "artifact must start with one TOML front-matter block"
        )
    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == FRONT_MATTER_DELIMITER:
            front_matter = "".join(lines[1:index])
            body = "".join(lines[index + 1 :])
            if any(item.rstrip("\r\n") == FRONT_MATTER_DELIMITER for item in lines[index + 1 :]):
                raise HarnessError(
                    "invalid-front-matter", "artifact must contain exactly one front-matter block"
                )
            return front_matter, body
    raise HarnessError("invalid-front-matter", "artifact front-matter block is not closed")


def _parse_metadata(front_matter: str) -> Mapping[str, object]:
    try:
        metadata = tomllib.loads(front_matter)
    except tomllib.TOMLDecodeError as error:
        raise HarnessError("invalid-front-matter", f"invalid TOML front matter: {error}") from error
    if not isinstance(metadata, dict):
        raise HarnessError("invalid-front-matter", "front matter must decode to a TOML table")
    return metadata


def _structural_headings(body: str) -> set[str]:
    headings: set[str] = set()
    fence_character = ""
    fence_length = 0
    for line in body.splitlines():
        if fence_character:
            stripped = line.lstrip(" ")
            indentation = len(line) - len(stripped)
            marker_length = len(stripped) - len(stripped.lstrip(fence_character))
            trailing = stripped[marker_length:]
            if (
                indentation <= 3
                and marker_length >= fence_length
                and not trailing.strip(" \t")
            ):
                fence_character = ""
                fence_length = 0
            continue
        match = _FENCE.match(line)
        if match:
            marker = match.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            continue
        if not fence_character and line.startswith("#"):
            headings.add(line)
    return headings


def _validate_envelope(metadata: Mapping[str, object], body: str) -> tuple[str, int]:
    allowed_keys = {
        "artifact_kind",
        "contract_version",
        "scope",
        "design_ref",
        "design_sha256",
        "tasks",
        "parallel_batches",
        "parallel_execution_approved",
        "default_runtime_model_policy",
        "truth_impact",
        "execution_result_ref",
        "truth_sync_ref",
        "decision",
        "truth_sync_required",
        "stable_truth_refs",
        "ledger_ref",
        "ledger_sha256",
        "execution_result_sha256",
        "truth_sync_sha256",
        "approval_status",
    }
    unknown = set(metadata).difference(allowed_keys)
    if unknown:
        raise HarnessError("invalid-artifact", f"unsupported metadata keys: {sorted(unknown)}")
    kind = _required_string(metadata, "artifact_kind")
    if kind not in ARTIFACT_KINDS:
        raise HarnessError("invalid-artifact-kind", f"unsupported artifact kind: {kind}")
    version = metadata.get("contract_version")
    if isinstance(version, bool) or not isinstance(version, int):
        raise HarnessError("unsupported-contract", "contract version must be an integer")
    if version not in SUPPORTED_CONTRACT_VERSIONS:
        raise HarnessError(
            "unsupported-contract",
            f"supported contract versions are {sorted(SUPPORTED_CONTRACT_VERSIONS)}",
        )
    headings = _structural_headings(body)
    missing = [heading for heading in BODY_HEADINGS[version][kind] if heading not in headings]
    if missing:
        raise HarnessError(
            "missing-human-section", f"missing required headings: {', '.join(missing)}"
        )
    _scope(metadata)
    return kind, version


def parse_artifact(path: Path, tracker: ReadTracker | None = None) -> Artifact:
    """Read exact artifact bytes once, decode strictly, and validate their contract."""
    reader = tracker.read if tracker is not None else _read_bytes
    try:
        payload = reader(path)
    except OSError as error:
        raise HarnessError("artifact-read-failed", f"cannot read artifact: {path}") from error
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise HarnessError(
            "invalid-artifact-encoding", f"artifact is not valid UTF-8: {path}"
        ) from error
    front_matter, body = _split_front_matter(text)
    metadata = _parse_metadata(front_matter)
    kind, version = _validate_envelope(metadata, body)
    _validate_kind_schema(kind, metadata, version)
    return Artifact(path.resolve(), kind, metadata, body, _sha256(payload))


def _reject_fields(metadata: Mapping[str, object], fields: frozenset[str], kind: str) -> None:
    present = sorted(set(metadata).intersection(fields))
    if present:
        raise HarnessError("invalid-artifact", f"{kind} has unsupported fields: {present}")


def _validate_kind_schema(kind: str, metadata: Mapping[str, object], version: int) -> None:
    v4_fields = frozenset(
        {
            "truth_impact",
            "parallel_batches",
            "parallel_execution_approved",
            "default_runtime_model_policy",
        }
    )
    if version == 3:
        _reject_fields(metadata, v4_fields, "version-3 artifact")
    if kind == "design":
        _reject_fields(
            metadata,
            frozenset(
                {
                    "design_ref",
                    "design_sha256",
                    "tasks",
                    "parallel_batches",
                    "parallel_execution_approved",
                    "default_runtime_model_policy",
                    "stable_truth_refs",
                }
            ),
            "design",
        )
        _required_choice(metadata, "approval_status", frozenset({"pending", "approved"}))
        if version == 4:
            impact = _required_choice(
                metadata,
                "truth_impact",
                frozenset({"none", "low", "medium", "high"}),
            )
            required = _required_bool(metadata, "truth_sync_required")
            if impact in {"medium", "high"} and not required:
                raise HarnessError(
                    "invalid-truth-contract",
                    "medium or high truth impact requires truth sync",
                )
        return
    if kind == "plan":
        _reject_fields(metadata, frozenset({"truth_impact"}), "plan")
        validate_repository_ref(_required_string(metadata, "design_ref"))
        _required_sha256(metadata, "design_sha256")
        tasks = _tasks(metadata, version)
        _required_bool(metadata, "truth_sync_required")
        tuple(
            validate_repository_ref(item)
            for item in _required_string_list(metadata, "stable_truth_refs")
        )
        _required_choice(metadata, "approval_status", frozenset({"pending", "approved"}))
        if version == 4:
            _required_choice(
                metadata,
                "default_runtime_model_policy",
                frozenset({"semantic-routing", "inherit-main", "runtime-default"}),
            )
            batches = _parallel_batches(metadata)
            _validate_parallel_batches(
                tasks,
                batches,
                _required_bool(metadata, "parallel_execution_approved"),
            )
        return
    _reject_fields(metadata, v4_fields, kind)
    if kind == "truth-sync":
        validate_repository_ref(_required_string(metadata, "execution_result_ref"))
        _required_sha256(metadata, "execution_result_sha256")
        validate_repository_ref(_required_string(metadata, "ledger_ref"))
        _required_sha256(metadata, "ledger_sha256")
        _required_choice(metadata, "approval_status", frozenset({"pending", "approved"}))
        return
    if kind == "close":
        truth_ref = metadata.get("truth_sync_ref")
        truth_sha256 = metadata.get("truth_sync_sha256")
        direct_fields = (
            "ledger_ref",
            "ledger_sha256",
            "execution_result_ref",
            "execution_result_sha256",
        )
        if truth_ref is not None or truth_sha256 is not None:
            if any(metadata.get(field) is not None for field in direct_fields):
                raise HarnessError(
                    "invalid-artifact", "close must use either truth-sync or direct evidence"
                )
            validate_repository_ref(_required_string(metadata, "truth_sync_ref"))
            _required_sha256(metadata, "truth_sync_sha256")
        else:
            validate_repository_ref(_required_string(metadata, "ledger_ref"))
            _required_sha256(metadata, "ledger_sha256")
            validate_repository_ref(_required_string(metadata, "execution_result_ref"))
            _required_sha256(metadata, "execution_result_sha256")
        _required_choice(metadata, "approval_status", frozenset({"pending", "approved"}))
        if _required_string(metadata, "decision") not in {"ready-for-close", "blocked"}:
            raise HarnessError("invalid-artifact", "close decision is invalid")


def _tasks(metadata: Mapping[str, object], version: int | None = None) -> tuple[Task, ...]:
    active_version = version if version is not None else metadata.get("contract_version")
    if active_version not in SUPPORTED_CONTRACT_VERSIONS:
        raise HarnessError("unsupported-contract", "task contract version is unsupported")
    value = metadata.get("tasks")
    if not isinstance(value, list) or not value:
        raise HarnessError(
            "invalid-artifact", "plan tasks must be a non-empty TOML array of tables"
        )
    tasks: list[Task] = []
    task_ids: set[str] = set()
    for entry in value:
        task_metadata = _mapping(entry, "tasks entry")
        allowed_keys = {
            "task_id",
            "depends_on",
            "scope",
            "verification_commands",
            "scope_slice",
            "executor_mode",
            "parallel_group",
            "parallel_policy",
            "delegation_policy",
            "execution_profile",
            "reasoning_profile",
            "isolation",
            "resource_locks",
            "convergence_required",
            "review_budget",
            "task_review_depth",
            "done_when",
            "failure_policy",
            "rollback_trigger",
            "rollback_target",
            "rollback_verification",
        }
        unknown = set(task_metadata).difference(allowed_keys)
        if unknown:
            raise HarnessError("invalid-artifact", f"task has unsupported keys: {sorted(unknown)}")
        task_id = _required_string(task_metadata, "task_id")
        if task_id in task_ids:
            raise HarnessError("invalid-artifact", f"duplicate task_id: {task_id}")
        task_ids.add(task_id)
        task = Task(
            task_id=task_id,
            depends_on=_required_string_list(task_metadata, "depends_on"),
            scope=_scope(task_metadata),
            verification_commands=_required_string_list(task_metadata, "verification_commands"),
            scope_slice=_required_string(task_metadata, "scope_slice"),
            executor_mode=_required_choice(
                task_metadata, "executor_mode", frozenset({"main", "subagent"})
            ),
            parallel_group=_required_string(task_metadata, "parallel_group"),
            parallel_policy=_required_choice(
                task_metadata,
                "parallel_policy",
                frozenset({"forbidden", "allowed", "required"}),
            ),
            delegation_policy=_required_choice(
                task_metadata,
                "delegation_policy",
                frozenset({"forbidden", "allowed", "preferred"}),
            ),
            execution_profile=_required_choice(
                task_metadata, "execution_profile", frozenset({"deep", "balanced", "fast"})
            ),
            reasoning_profile=_required_choice(
                task_metadata, "reasoning_profile", frozenset({"deep", "standard", "light"})
            ),
            isolation=_required_choice(
                task_metadata,
                "isolation",
                frozenset({"controller-checkout", "shared-read-only", "isolated-worktree"}),
            ),
            resource_locks=_required_string_list(task_metadata, "resource_locks"),
            convergence_required=_required_bool(task_metadata, "convergence_required"),
            review_budget=_required_positive_int(task_metadata, "review_budget"),
            task_review_depth=_required_choice(
                task_metadata, "task_review_depth", frozenset({"focused", "full"})
            ),
            done_when=_required_string_list(task_metadata, "done_when"),
            failure_policy=_required_choice(
                task_metadata,
                "failure_policy",
                frozenset({"fix_forward", "guarded_rollback"}),
            ),
            rollback_trigger=_optional_string_field(task_metadata, "rollback_trigger"),
            rollback_target=_optional_string_field(task_metadata, "rollback_target"),
            rollback_verification=_optional_string_field(task_metadata, "rollback_verification"),
        )
        if active_version == 4:
            _validate_task_contract(task)
        tasks.append(task)
    _validate_task_dag(tasks)
    return tuple(tasks)


def _validate_task_contract(task: Task) -> None:
    if (task.executor_mode == "main") != (task.delegation_policy == "forbidden"):
        raise HarnessError(
            "invalid-task-contract",
            f"executor and delegation policy conflict: {task.task_id}",
        )
    if task.parallel_policy == "forbidden" and task.parallel_group != "none":
        raise HarnessError(
            "invalid-task-contract", f"forbidden task names a parallel group: {task.task_id}"
        )
    if task.parallel_policy != "forbidden" and task.parallel_group == "none":
        raise HarnessError(
            "invalid-task-contract", f"parallel task requires a named group: {task.task_id}"
        )
    if task.isolation == "shared-read-only" and task.scope.all_refs:
        raise HarnessError(
            "invalid-task-contract", f"shared-read-only task has write refs: {task.task_id}"
        )
    if (
        task.executor_mode == "subagent"
        and task.scope.all_refs
        and task.isolation != "isolated-worktree"
    ):
        raise HarnessError(
            "invalid-task-contract", f"delegated writer lacks isolation: {task.task_id}"
        )
    if task.scope.external_impl_file_refs and (
        task.executor_mode != "main"
        or task.delegation_policy != "forbidden"
        or task.parallel_policy != "forbidden"
        or task.parallel_group != "none"
        or task.isolation != "controller-checkout"
        or not task.resource_locks
    ):
        raise HarnessError(
            "invalid-task-contract", f"external task violates main-only contract: {task.task_id}"
        )
    rollback_fields = (
        task.rollback_trigger,
        task.rollback_target,
        task.rollback_verification,
    )
    if task.failure_policy == "fix_forward" and any(rollback_fields):
        raise HarnessError(
            "invalid-task-contract", f"fix-forward task carries rollback authority: {task.task_id}"
        )
    if task.failure_policy == "guarded_rollback" and not all(rollback_fields):
        raise HarnessError(
            "invalid-task-contract", f"guarded rollback is incomplete: {task.task_id}"
        )


def _validate_task_dag(tasks: Sequence[Task]) -> None:
    task_ids = {task.task_id for task in tasks}
    for task in tasks:
        unknown = set(task.depends_on).difference(task_ids)
        if unknown or task.task_id in task.depends_on:
            raise HarnessError("invalid-artifact", f"task dependencies are invalid: {task.task_id}")
    dependency_map = {task.task_id: set(task.depends_on) for task in tasks}
    visited: set[str] = set()
    visiting: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise HarnessError("invalid-artifact-dag", "task dependencies contain a cycle")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in dependency_map[task_id]:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in dependency_map:
        visit(task_id)


def _parallel_batches(metadata: Mapping[str, object]) -> tuple[ParallelBatch, ...]:
    value = metadata.get("parallel_batches", [])
    if not isinstance(value, list):
        raise HarnessError("invalid-parallel-batch", "parallel_batches must be an array of tables")
    batches: list[ParallelBatch] = []
    batch_ids: set[str] = set()
    for entry in value:
        batch_metadata = _mapping(entry, "parallel batch")
        allowed = {"batch_id", "tasks", "max_parallelism", "convergence_task"}
        unknown = set(batch_metadata).difference(allowed)
        if unknown:
            raise HarnessError(
                "invalid-parallel-batch",
                f"parallel batch has unsupported keys: {sorted(unknown)}",
            )
        batch_id = _required_string(batch_metadata, "batch_id")
        if batch_id == "none" or batch_id in batch_ids:
            raise HarnessError("invalid-parallel-batch", f"invalid batch id: {batch_id}")
        batch_ids.add(batch_id)
        batches.append(
            ParallelBatch(
                batch_id=batch_id,
                tasks=_required_string_list(batch_metadata, "tasks"),
                max_parallelism=_required_positive_int(batch_metadata, "max_parallelism"),
                convergence_task=_required_string(batch_metadata, "convergence_task"),
            )
        )
    return tuple(batches)


def _dependency_closure(tasks: Sequence[Task]) -> dict[str, set[str]]:
    direct = {task.task_id: set(task.depends_on) for task in tasks}
    closure: dict[str, set[str]] = {}

    def ancestors(task_id: str) -> set[str]:
        if task_id not in closure:
            closure[task_id] = set(direct[task_id])
            for dependency in direct[task_id]:
                closure[task_id].update(ancestors(dependency))
        return closure[task_id]

    for task_id in direct:
        ancestors(task_id)
    return closure


def _refs_overlap(first: Sequence[str], second: Sequence[str]) -> bool:
    return any(
        left == right or left.startswith(f"{right}/") or right.startswith(f"{left}/")
        for left in first
        for right in second
    )


def _validate_parallel_batches(
    tasks: Sequence[Task], batches: Sequence[ParallelBatch], approved: bool
) -> None:
    if approved != bool(batches):
        raise HarnessError(
            "invalid-parallel-batch", "parallel approval and named batch records disagree"
        )
    task_by_id = {task.task_id: task for task in tasks}
    grouped: dict[str, list[str]] = {}
    for task in tasks:
        if task.parallel_group != "none":
            grouped.setdefault(task.parallel_group, []).append(task.task_id)
    if set(grouped) != {batch.batch_id for batch in batches}:
        raise HarnessError(
            "invalid-parallel-batch", "task parallel groups and batch records disagree"
        )
    closure = _dependency_closure(tasks)
    for batch in batches:
        members = grouped[batch.batch_id]
        if list(batch.tasks) != members or len(members) < 2:
            raise HarnessError(
                "invalid-parallel-batch", f"batch membership is incomplete: {batch.batch_id}"
            )
        if batch.max_parallelism < 2 or batch.max_parallelism > len(members):
            raise HarnessError(
                "invalid-parallel-batch", f"batch width is invalid: {batch.batch_id}"
            )
        if batch.convergence_task != "controller":
            if batch.convergence_task not in task_by_id or batch.convergence_task in members:
                raise HarnessError(
                    "invalid-parallel-batch",
                    f"batch convergence owner is invalid: {batch.batch_id}",
                )
            if not set(members).issubset(closure[batch.convergence_task]):
                raise HarnessError(
                    "invalid-parallel-batch",
                    f"batch convergence task lacks dependencies: {batch.batch_id}",
                )
        for index, left_id in enumerate(members):
            left = task_by_id[left_id]
            for right_id in members[index + 1 :]:
                right = task_by_id[right_id]
                if left_id in closure[right_id] or right_id in closure[left_id]:
                    raise HarnessError(
                        "invalid-parallel-batch",
                        f"batch peers depend on each other: {batch.batch_id}",
                    )
                if _refs_overlap(left.scope.all_refs, right.scope.all_refs):
                    raise HarnessError(
                        "invalid-parallel-batch", f"batch write sets overlap: {batch.batch_id}"
                    )
                if set(left.resource_locks).intersection(right.resource_locks):
                    raise HarnessError(
                        "invalid-parallel-batch", f"batch resource locks overlap: {batch.batch_id}"
                    )


def _is_within(declared_refs: Sequence[str], candidate: str) -> bool:
    return any(
        candidate == reference or candidate.startswith(f"{reference}/")
        for reference in declared_refs
    )


def _validate_plan_containment(design: Artifact, plan: Artifact, tasks: Sequence[Task]) -> None:
    if design.artifact_kind != "design" or plan.artifact_kind != "plan":
        raise HarnessError("invalid-artifact-dag", "plan compilation requires a design and plan")
    design_scope = _scope(design.metadata)
    plan_scope = _scope(plan.metadata)
    if not all(_is_within(design_scope.impl_file_refs, ref) for ref in plan_scope.impl_file_refs):
        raise HarnessError(
            "design-containment-failed", "plan implementation refs escape the design"
        )
    if not all(_is_within(design_scope.test_file_refs, ref) for ref in plan_scope.test_file_refs):
        raise HarnessError("design-containment-failed", "plan test refs escape the design")
    if set(plan_scope.external_impl_file_refs).difference(design_scope.external_impl_file_refs):
        raise HarnessError("design-containment-failed", "plan external refs escape the design")
    stable_refs = _required_string_list(plan.metadata, "stable_truth_refs")
    if not all(_is_within(plan_scope.impl_file_refs, ref) for ref in stable_refs):
        raise HarnessError(
            "plan-containment-failed", "stable truth refs escape plan implementation scope"
        )
    for task in tasks:
        if not all(_is_within(plan_scope.impl_file_refs, ref) for ref in task.scope.impl_file_refs):
            raise HarnessError(
                "plan-containment-failed", f"task implementation refs escape plan: {task.task_id}"
            )
        if not all(_is_within(plan_scope.test_file_refs, ref) for ref in task.scope.test_file_refs):
            raise HarnessError(
                "plan-containment-failed", f"task test refs escape plan: {task.task_id}"
            )
        if set(task.scope.external_impl_file_refs).difference(plan_scope.external_impl_file_refs):
            raise HarnessError(
                "plan-containment-failed", f"task external refs escape plan: {task.task_id}"
            )


def _validate_truth_contract(design: Artifact, plan: Artifact) -> None:
    if plan.contract_version != 4:
        return
    design_required = _required_bool(design.metadata, "truth_sync_required")
    plan_required = _required_bool(plan.metadata, "truth_sync_required")
    if design_required != plan_required:
        raise HarnessError(
            "truth-contract-mismatch", "design and plan truth-sync requirements disagree"
        )
    impact = _required_choice(
        design.metadata,
        "truth_impact",
        frozenset({"none", "low", "medium", "high"}),
    )
    stable_refs = _required_string_list(plan.metadata, "stable_truth_refs")
    if plan_required and not stable_refs:
        raise HarnessError(
            "truth-sync-scope-required", "truth-sync requires non-empty stable truth refs"
        )
    if not plan_required and stable_refs:
        raise HarnessError(
            "truth-contract-mismatch", "truth-sync disabled plans require an empty truth scope"
        )
    if impact in {"medium", "high"} and not plan_required:
        raise HarnessError("truth-contract-mismatch", "truth impact requires truth sync")
    if any(ref == "docs/plans" or ref.startswith("docs/plans/") for ref in stable_refs):
        raise HarnessError(
            "invalid-stable-truth-ref", "stage artifacts cannot be stable truth refs"
        )


def _artifact_ref(base: Path, reference: str) -> Path:
    validate_repository_ref(reference)
    candidate = (base / reference).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as error:
        raise HarnessError(
            "unsafe-repository-ref", f"artifact reference escapes repository: {reference}"
        ) from error
    return candidate


def _task_projection(task: Task) -> dict[str, object]:
    return {
        "task_id": task.task_id,
        "depends_on": list(task.depends_on),
        "scope": _scope_projection(task.scope),
        "verification_commands": list(task.verification_commands),
        "scope_slice": task.scope_slice,
        "executor_mode": task.executor_mode,
        "parallel_group": task.parallel_group,
        "parallel_policy": task.parallel_policy,
        "delegation_policy": task.delegation_policy,
        "execution_profile": task.execution_profile,
        "reasoning_profile": task.reasoning_profile,
        "isolation": task.isolation,
        "resource_locks": list(task.resource_locks),
        "convergence_required": task.convergence_required,
        "review_budget": task.review_budget,
        "task_review_depth": task.task_review_depth,
        "done_when": list(task.done_when),
        "failure_policy": task.failure_policy,
        "rollback_trigger": task.rollback_trigger,
        "rollback_target": task.rollback_target,
        "rollback_verification": task.rollback_verification,
    }


def _batch_projection(batch: ParallelBatch) -> dict[str, object]:
    return {
        "batch_id": batch.batch_id,
        "tasks": list(batch.tasks),
        "max_parallelism": batch.max_parallelism,
        "convergence_task": batch.convergence_task,
    }


def compile_plan(plan_path: Path, tracker: ReadTracker | None = None) -> CompiledPlan:
    """Validate a plan and linked design once, then build its immutable projection."""
    active_tracker = tracker or ReadTracker()
    plan = parse_artifact(plan_path, active_tracker)
    if plan.artifact_kind != "plan":
        raise HarnessError("invalid-artifact-dag", "expected a plan artifact")
    design_ref = _required_string(plan.metadata, "design_ref")
    design = parse_artifact(_artifact_ref(plan.path.parent, design_ref), active_tracker)
    if design.contract_version != plan.contract_version:
        raise HarnessError(
            "artifact-contract-version-mismatch", "design and plan contract versions disagree"
        )
    expected_design_sha256 = _required_string(plan.metadata, "design_sha256")
    if design.sha256 != expected_design_sha256:
        raise HarnessError(
            "design-digest-mismatch", "plan design_sha256 does not match the linked design"
        )
    tasks = _tasks(plan.metadata, plan.contract_version)
    batches = _parallel_batches(plan.metadata) if plan.contract_version == 4 else ()
    _validate_truth_contract(design, plan)
    _validate_plan_containment(design, plan, tasks)
    projection: dict[str, object] = {
        "artifact_kind": "compiled-plan",
        "contract_version": plan.contract_version,
        "truth_sync_required": _required_bool(plan.metadata, "truth_sync_required"),
        "stable_truth_refs": [
            validate_repository_ref(item)
            for item in _required_string_list(plan.metadata, "stable_truth_refs")
        ],
        "design": {"ref": design_ref, "scope": _scope_projection(_scope(design.metadata))},
        "plan": {"ref": plan.path.name, "scope": _scope_projection(_scope(plan.metadata))},
        "tasks": [_task_projection(task) for task in tasks],
    }
    if plan.contract_version == 4:
        projection.update(
            {
                "truth_impact": _required_string(design.metadata, "truth_impact"),
                "default_runtime_model_policy": _required_string(
                    plan.metadata, "default_runtime_model_policy"
                ),
                "parallel_execution_approved": _required_bool(
                    plan.metadata, "parallel_execution_approved"
                ),
                "parallel_batches": [_batch_projection(batch) for batch in batches],
            }
        )
    normalized = json.dumps(projection, sort_keys=True, separators=(",", ":")).encode()
    return CompiledPlan(design, plan, tasks, batches, projection, _sha256(normalized))


def _scope_projection(scope: Scope) -> dict[str, list[str]]:
    return {
        "external_impl_file_refs": list(scope.external_impl_file_refs),
        "impl_file_refs": list(scope.impl_file_refs),
        "test_file_refs": list(scope.test_file_refs),
    }


def validate_artifact(path: Path, expected_kind: str) -> Artifact:
    """Validate a single artifact for a namespace-specific CLI operation."""
    artifact = parse_artifact(path)
    if artifact.artifact_kind != expected_kind:
        raise HarnessError(
            "invalid-artifact-kind", f"expected {expected_kind}, got {artifact.artifact_kind}"
        )
    return artifact
