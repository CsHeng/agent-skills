"""Version-4 artifact, task, batch, and truth-contract tests."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from runtime.harness.artifacts import HarnessError, ReadTracker, compile_plan, parse_artifact


def digest(payload: bytes) -> str:
    """Return the exact byte digest used by artifact authority."""
    return hashlib.sha256(payload).hexdigest()


def design_text(
    *,
    truth_impact: str = "high",
    truth_sync_required: bool = True,
    impl_refs: str = '["src", "README.md"]',
) -> str:
    """Create one approved version-4 design."""
    required = str(truth_sync_required).lower()
    return "\n".join(
        (
            "+++",
            'artifact_kind = "design"',
            "contract_version = 4",
            'approval_status = "approved"',
            f'truth_impact = "{truth_impact}"',
            f"truth_sync_required = {required}",
            "",
            "[scope]",
            f"impl_file_refs = {impl_refs}",
            'test_file_refs = ["tests"]',
            "external_impl_file_refs = []",
            "+++",
            "# Design",
            "",
            "## Problem",
            "",
            "Authority needs a versioned contract.",
            "",
            "## Goals",
            "",
            "Compile one immutable projection.",
            "",
            "## Boundaries",
            "",
            "Version 3 is read-only after refresh.",
            "",
        )
    )


def task_text(
    task_id: str = "V4-010",
    *,
    depends_on: str = "[]",
    impl_refs: str = '["src/runtime.py"]',
    test_refs: str = '["tests/test_runtime.py"]',
    external_refs: str = "[]",
    executor_mode: str = "main",
    parallel_group: str = "none",
    parallel_policy: str = "forbidden",
    delegation_policy: str = "forbidden",
    isolation: str = "controller-checkout",
    resource_locks: str = '["runtime"]',
    failure_policy: str = "fix_forward",
    rollback_trigger: str = "",
    rollback_target: str = "",
    rollback_verification: str = "",
) -> str:
    """Create one complete version-4 task table."""
    return "\n".join(
        (
            "[[tasks]]",
            f'task_id = "{task_id}"',
            f"depends_on = {depends_on}",
            'verification_commands = ["uv run pytest tests"]',
            'scope_slice = "Implement the runtime contract."',
            f'executor_mode = "{executor_mode}"',
            f'parallel_group = "{parallel_group}"',
            f'parallel_policy = "{parallel_policy}"',
            f'delegation_policy = "{delegation_policy}"',
            'execution_profile = "deep"',
            'reasoning_profile = "deep"',
            f'isolation = "{isolation}"',
            f"resource_locks = {resource_locks}",
            "convergence_required = true",
            "review_budget = 1",
            'task_review_depth = "full"',
            'done_when = ["The runtime contract passes."]',
            f'failure_policy = "{failure_policy}"',
            f'rollback_trigger = "{rollback_trigger}"',
            f'rollback_target = "{rollback_target}"',
            f'rollback_verification = "{rollback_verification}"',
            "",
            "[tasks.scope]",
            f"impl_file_refs = {impl_refs}",
            f"test_file_refs = {test_refs}",
            f"external_impl_file_refs = {external_refs}",
        )
    )


def plan_text(
    design_sha256: str,
    *,
    truth_sync_required: bool = True,
    stable_truth_refs: str = '["README.md"]',
    task_tables: str | None = None,
    parallel_execution_approved: bool = False,
    batch_tables: str = "",
    external_scope: str = "[]",
) -> str:
    """Create one approved version-4 plan."""
    required = str(truth_sync_required).lower()
    parallel = str(parallel_execution_approved).lower()
    tasks = task_tables or task_text()
    return "\n".join(
        (
            "+++",
            'artifact_kind = "plan"',
            "contract_version = 4",
            'design_ref = "design.md"',
            f'design_sha256 = "{design_sha256}"',
            'approval_status = "approved"',
            f"truth_sync_required = {required}",
            f"stable_truth_refs = {stable_truth_refs}",
            'default_runtime_model_policy = "semantic-routing"',
            f"parallel_execution_approved = {parallel}",
            "",
            "[scope]",
            'impl_file_refs = ["src", "README.md"]',
            'test_file_refs = ["tests"]',
            f"external_impl_file_refs = {external_scope}",
            "",
            tasks,
            batch_tables,
            "+++",
            "# Plan",
            "",
            "## Implementation",
            "",
            "Implement version 4.",
            "",
            "## Work Package Readiness",
            "",
            "The work package is executable.",
            "",
            "## Execution Continuity",
            "",
            "The serial path is continuous.",
            "",
            "## Recovery",
            "",
            "Fix forward.",
            "",
            "## Truth Sync Handoff",
            "",
            "Update stable truth after verification.",
            "",
        )
    )


def write_pair(
    tmp_path: Path,
    *,
    truth_sync_required: bool = True,
    stable_truth_refs: str = '["README.md"]',
    task_tables: str | None = None,
    parallel_execution_approved: bool = False,
    batch_tables: str = "",
    external_scope: str = "[]",
) -> tuple[Path, Path]:
    """Write one exact-byte-linked version-4 design and plan pair."""
    design = tmp_path / "design.md"
    design_payload = design_text().encode()
    design.write_bytes(design_payload)
    plan = tmp_path / "plan.md"
    plan.write_text(
        plan_text(
            digest(design_payload),
            truth_sync_required=truth_sync_required,
            stable_truth_refs=stable_truth_refs,
            task_tables=task_tables,
            parallel_execution_approved=parallel_execution_approved,
            batch_tables=batch_tables,
            external_scope=external_scope,
        ),
        encoding="utf-8",
    )
    return design, plan


def test_parse_hashes_the_exact_crlf_bytes_once(tmp_path: Path) -> None:
    """CRLF identity is preserved from the same one-read payload used for parsing."""
    artifact_path = tmp_path / "design.md"
    payload = design_text().replace("\n", "\r\n").encode()
    artifact_path.write_bytes(payload)
    tracker = ReadTracker()

    artifact = parse_artifact(artifact_path, tracker)

    assert artifact.sha256 == digest(payload)
    assert tracker.counts == {artifact_path.resolve(): 1}


def test_parse_rejects_invalid_utf8_with_a_typed_error(tmp_path: Path) -> None:
    """Artifact bytes are decoded strictly after their exact digest is known."""
    artifact_path = tmp_path / "design.md"
    artifact_path.write_bytes(design_text().encode() + b"\xff")

    with pytest.raises(HarnessError) as captured:
        parse_artifact(artifact_path)

    assert captured.value.code == "invalid-artifact-encoding"


@pytest.mark.parametrize(
    "replacement",
    (
        "## Problematic",
        "```markdown\n## Problem\n```",
        "```markdown\n````not-a-close\n## Problem",
        "```markdown\n\t```\n## Problem",
    ),
)
def test_required_headings_are_exact_and_outside_fences(
    tmp_path: Path, replacement: str
) -> None:
    """Substrings and fenced examples cannot satisfy structural headings."""
    artifact_path = tmp_path / "design.md"
    artifact_path.write_text(design_text().replace("## Problem", replacement), encoding="utf-8")

    with pytest.raises(HarnessError) as captured:
        parse_artifact(artifact_path)

    assert captured.value.code == "missing-human-section"


@pytest.mark.parametrize(
    "unsafe_ref",
    (
        "src//runtime.py",
        "src/./runtime.py",
        "src\\runtime.py",
        "src/*.py",
        "src/\x1fruntime.py",
        "C:/outside.py",
    ),
)
def test_repository_refs_reject_aliases_globs_and_control_characters(
    tmp_path: Path, unsafe_ref: str
) -> None:
    """Repository authority uses one safe normalized spelling."""
    artifact_path = tmp_path / "design.md"
    toml_ref = unsafe_ref.replace("\\", "\\\\").replace("\x1f", "\\u001f")
    refs = f'["{toml_ref}", "README.md"]'
    artifact_path.write_text(design_text(impl_refs=refs), encoding="utf-8")

    with pytest.raises(HarnessError) as captured:
        parse_artifact(artifact_path)

    assert captured.value.code == "unsafe-repository-ref"


def test_compile_v4_projects_truth_and_runtime_policy(tmp_path: Path) -> None:
    """The immutable projection carries the full version-4 authority shape."""
    _, plan = write_pair(tmp_path)

    compiled = compile_plan(plan)

    assert compiled.projection["contract_version"] == 4
    assert compiled.projection["truth_impact"] == "high"
    assert compiled.projection["truth_sync_required"] is True
    assert compiled.projection["default_runtime_model_policy"] == "semantic-routing"
    assert compiled.projection["parallel_execution_approved"] is False
    assert compiled.projection["parallel_batches"] == []


@pytest.mark.parametrize(
    ("required", "stable_refs", "expected_code"),
    (
        (False, "[]", "truth-contract-mismatch"),
        (True, "[]", "truth-sync-scope-required"),
        (True, '["docs/plans/change.md"]', "invalid-stable-truth-ref"),
    ),
)
def test_compile_rejects_truth_contract_downgrades(
    tmp_path: Path, required: bool, stable_refs: str, expected_code: str
) -> None:
    """A high-impact design cannot compile an empty or contradictory truth handoff."""
    _, plan = write_pair(
        tmp_path,
        truth_sync_required=required,
        stable_truth_refs=stable_refs,
    )

    with pytest.raises(HarnessError) as captured:
        compile_plan(plan)

    assert captured.value.code == expected_code


@pytest.mark.parametrize(
    "task",
    (
        task_text(delegation_policy="allowed"),
        task_text(isolation="shared-read-only"),
        task_text(parallel_policy="required"),
        task_text(rollback_trigger="any failure"),
        task_text(
            external_refs='["/tmp/runtime"]',
            executor_mode="subagent",
            delegation_policy="allowed",
            isolation="isolated-worktree",
        ),
    ),
)
def test_compile_rejects_contradictory_task_contracts(tmp_path: Path, task: str) -> None:
    """Cross-field invariants are executable before ledger initialization."""
    external_scope = '["/tmp/runtime"]' if "/tmp/runtime" in task else "[]"
    _, plan = write_pair(tmp_path, task_tables=task, external_scope=external_scope)

    with pytest.raises(HarnessError) as captured:
        compile_plan(plan)

    assert captured.value.code == "invalid-task-contract"


def parallel_tasks(*, overlapping: bool = False, dependent: bool = False) -> str:
    """Create two tasks for one named version-4 batch."""
    second_impl = '["src/a.py"]' if overlapping else '["src/b.py"]'
    second_dependencies = '["V4-010"]' if dependent else "[]"
    return "\n\n".join(
        (
            task_text(
                "V4-010",
                impl_refs='["src/a.py"]',
                test_refs='["tests/test_a.py"]',
                executor_mode="subagent",
                parallel_group="batch-a",
                parallel_policy="required",
                delegation_policy="preferred",
                isolation="isolated-worktree",
                resource_locks='["lock-a"]',
            ),
            task_text(
                "V4-020",
                depends_on=second_dependencies,
                impl_refs=second_impl,
                test_refs='["tests/test_b.py"]',
                executor_mode="subagent",
                parallel_group="batch-a",
                parallel_policy="required",
                delegation_policy="preferred",
                isolation="isolated-worktree",
                resource_locks='["lock-b"]',
            ),
        )
    )


def batch_text(tasks: str = '["V4-010", "V4-020"]') -> str:
    """Create one complete named batch record."""
    return "\n".join(
        (
            "[[parallel_batches]]",
            'batch_id = "batch-a"',
            f"tasks = {tasks}",
            "max_parallelism = 2",
            'convergence_task = "controller"',
        )
    )


def test_compile_projects_a_valid_named_batch(tmp_path: Path) -> None:
    """A dependency-frozen conflict-free batch becomes immutable authority."""
    _, plan = write_pair(
        tmp_path,
        task_tables=parallel_tasks(),
        parallel_execution_approved=True,
        batch_tables=batch_text(),
    )

    compiled = compile_plan(plan)

    assert compiled.projection["parallel_batches"] == [
        {
            "batch_id": "batch-a",
            "convergence_task": "controller",
            "max_parallelism": 2,
            "tasks": ["V4-010", "V4-020"],
        }
    ]


@pytest.mark.parametrize(
    "tasks",
    (
        parallel_tasks(overlapping=True),
        parallel_tasks(dependent=True),
    ),
)
def test_compile_rejects_batch_write_and_dependency_conflicts(
    tmp_path: Path, tasks: str
) -> None:
    """Named peers cannot share writes or depend on each other."""
    _, plan = write_pair(
        tmp_path,
        task_tables=tasks,
        parallel_execution_approved=True,
        batch_tables=batch_text(),
    )

    with pytest.raises(HarnessError) as captured:
        compile_plan(plan)

    assert captured.value.code == "invalid-parallel-batch"
