"""Typed parsing and compilation for version-3 lifecycle artifacts."""

from __future__ import annotations

import hashlib
import json
import tomllib
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

FRONT_MATTER_DELIMITER = "+++"
CONTRACT_VERSION = 3
ARTIFACT_KINDS = frozenset({"design", "plan", "truth-sync", "close"})
BODY_HEADINGS: dict[str, tuple[str, ...]] = {
    "design": ("# Design", "## Problem", "## Goals", "## Boundaries"),
    "plan": ("# Plan", "## Implementation"),
    "truth-sync": ("# Truth Sync", "## Scope"),
    "close": ("# Close", "## Decision"),
}
ReadText = Callable[[Path], str]


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


@dataclass(frozen=True)
class Artifact:
    """One parsed artifact and its human-facing Markdown body."""

    path: Path
    artifact_kind: str
    metadata: Mapping[str, object]
    body: str
    sha256: str


@dataclass(frozen=True)
class Task:
    """The immutable version-3 plan task shape needed before ledger initialization."""

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
class CompiledPlan:
    """A design-contained plan projection with content-addressed source artifacts."""

    design: Artifact
    plan: Artifact
    tasks: tuple[Task, ...]
    projection: Mapping[str, object]
    projection_sha256: str


class ReadTracker:
    """Wrap artifact reads so tests can prove one read per parse operation."""

    def __init__(self, reader: ReadText | None = None) -> None:
        self._reader = reader or _read_text
        self.counts: dict[Path, int] = {}

    def read(self, path: Path) -> str:
        """Read a path once and increment its observable count."""
        resolved = path.resolve()
        self.counts[resolved] = self.counts.get(resolved, 0) + 1
        return self._reader(resolved)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


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


def _validate_repository_ref(reference: str) -> str:
    path = PurePosixPath(reference)
    if path.is_absolute() or reference in {"", "."} or ".." in path.parts:
        raise HarnessError("unsafe-repository-ref", f"unsafe repository reference: {reference}")
    return path.as_posix()


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
        _validate_repository_ref(item) for item in _required_string_list(scope, "impl_file_refs")
    )
    test_refs = tuple(
        _validate_repository_ref(item) for item in _required_string_list(scope, "test_file_refs")
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


def _validate_envelope(metadata: Mapping[str, object], body: str) -> str:
    allowed_keys = {
        "artifact_kind",
        "contract_version",
        "scope",
        "design_ref",
        "design_sha256",
        "tasks",
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
    if version != CONTRACT_VERSION:
        raise HarnessError("unsupported-contract", f"expected contract version {CONTRACT_VERSION}")
    missing_headings = [heading for heading in BODY_HEADINGS[kind] if heading not in body]
    if missing_headings:
        raise HarnessError(
            "missing-human-section", f"missing required headings: {', '.join(missing_headings)}"
        )
    _scope(metadata)
    return kind


def parse_artifact(path: Path, tracker: ReadTracker | None = None) -> Artifact:
    """Read and validate one version-3 artifact exactly once."""
    reader = tracker.read if tracker is not None else _read_text
    try:
        text = reader(path)
    except OSError as error:
        raise HarnessError("artifact-read-failed", f"cannot read artifact: {path}") from error
    front_matter, body = _split_front_matter(text)
    metadata = _parse_metadata(front_matter)
    kind = _validate_envelope(metadata, body)
    _validate_kind_schema(kind, metadata)
    return Artifact(path.resolve(), kind, metadata, body, _sha256(text))


def _validate_kind_schema(kind: str, metadata: Mapping[str, object]) -> None:
    if kind == "design":
        if any(key in metadata for key in ("design_ref", "design_sha256", "tasks")):
            raise HarnessError("invalid-artifact", "design cannot declare plan fields")
        _required_choice(metadata, "approval_status", frozenset({"pending", "approved"}))
        return
    if kind == "plan":
        _validate_repository_ref(_required_string(metadata, "design_ref"))
        _required_sha256(metadata, "design_sha256")
        _tasks(metadata)
        _required_bool(metadata, "truth_sync_required")
        tuple(
            _validate_repository_ref(item)
            for item in _required_string_list(metadata, "stable_truth_refs")
        )
        _required_choice(metadata, "approval_status", frozenset({"pending", "approved"}))
        return
    if kind == "truth-sync":
        _validate_repository_ref(_required_string(metadata, "execution_result_ref"))
        _required_sha256(metadata, "execution_result_sha256")
        _validate_repository_ref(_required_string(metadata, "ledger_ref"))
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
            _validate_repository_ref(_required_string(metadata, "truth_sync_ref"))
            _required_sha256(metadata, "truth_sync_sha256")
        else:
            _validate_repository_ref(_required_string(metadata, "ledger_ref"))
            _required_sha256(metadata, "ledger_sha256")
            _validate_repository_ref(_required_string(metadata, "execution_result_ref"))
            _required_sha256(metadata, "execution_result_sha256")
        _required_choice(metadata, "approval_status", frozenset({"pending", "approved"}))
        if _required_string(metadata, "decision") not in {"ready-for-close", "blocked"}:
            raise HarnessError("invalid-artifact", "close decision is invalid")


def _tasks(metadata: Mapping[str, object]) -> tuple[Task, ...]:
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
        tasks.append(
            Task(
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
                    task_metadata,
                    "execution_profile",
                    frozenset({"deep", "balanced", "fast"}),
                ),
                reasoning_profile=_required_choice(
                    task_metadata,
                    "reasoning_profile",
                    frozenset({"deep", "standard", "light"}),
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
                rollback_verification=_optional_string_field(
                    task_metadata, "rollback_verification"
                ),
            )
        )
    for task in tasks:
        unknown_dependencies = set(task.depends_on).difference(task_ids)
        if unknown_dependencies or task.task_id in task.depends_on:
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
    return tuple(tasks)


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
    stable_truth_refs = _required_string_list(plan.metadata, "stable_truth_refs")
    if not all(_is_within(plan_scope.impl_file_refs, ref) for ref in stable_truth_refs):
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


def _artifact_ref(base: Path, reference: str) -> Path:
    candidate = (base / reference).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as error:
        raise HarnessError(
            "unsafe-repository-ref", f"artifact reference escapes repository: {reference}"
        ) from error
    return candidate


def compile_plan(plan_path: Path, tracker: ReadTracker | None = None) -> CompiledPlan:
    """Validate a plan and linked design once, then build its immutable projection."""
    active_tracker = tracker or ReadTracker()
    plan = parse_artifact(plan_path, active_tracker)
    if plan.artifact_kind != "plan":
        raise HarnessError("invalid-artifact-dag", "expected a plan artifact")
    design_ref = _required_string(plan.metadata, "design_ref")
    design = parse_artifact(_artifact_ref(plan.path.parent, design_ref), active_tracker)
    expected_design_sha256 = _required_string(plan.metadata, "design_sha256")
    if design.sha256 != expected_design_sha256:
        raise HarnessError(
            "design-digest-mismatch", "plan design_sha256 does not match the linked design"
        )
    tasks = _tasks(plan.metadata)
    _validate_plan_containment(design, plan, tasks)
    projection: dict[str, object] = {
        "artifact_kind": "compiled-plan",
        "contract_version": CONTRACT_VERSION,
        "truth_sync_required": _required_bool(plan.metadata, "truth_sync_required"),
        "stable_truth_refs": [
            _validate_repository_ref(item)
            for item in _required_string_list(plan.metadata, "stable_truth_refs")
        ],
        "design": {"ref": design_ref, "scope": _scope_projection(_scope(design.metadata))},
        "plan": {"ref": plan.path.name, "scope": _scope_projection(_scope(plan.metadata))},
        "tasks": [
            {
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
            for task in tasks
        ],
    }
    normalized = json.dumps(projection, sort_keys=True, separators=(",", ":"))
    return CompiledPlan(design, plan, tasks, projection, _sha256(normalized))


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
