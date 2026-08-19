"""Contract and one-read tests for the non-active version-3 artifact runtime."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from runtime.harness.artifacts import (
    HarnessError,
    ReadTracker,
    compile_plan,
    parse_artifact,
    validate_artifact,
)

ROOT = Path(__file__).resolve().parents[3]


def digest(text: str) -> str:
    """Return the byte digest used by the plan-to-design contract."""
    return hashlib.sha256(text.encode()).hexdigest()


def design_text() -> str:
    """Create a valid human-reviewable design artifact."""
    return "\n".join(
        (
            "+++",
            'artifact_kind = "design"',
            "contract_version = 3",
            'approval_status = "approved"',
            "",
            "[scope]",
            'impl_file_refs = ["runtime/harness", "README.md"]',
            'test_file_refs = ["runtime/harness/tests"]',
            'external_impl_file_refs = ["/tmp/harness-evidence"]',
            "+++",
            "# Design",
            "",
            "## Problem",
            "",
            "The active Shell runtime is the baseline.",
            "",
            "## Goals",
            "",
            "Introduce a non-active typed parser.",
            "",
            "## Boundaries",
            "",
            "No active runtime path changes.",
            "",
        )
    )


def plan_text(design_sha256: str, task_impl_ref: str = "runtime/harness/artifacts.py") -> str:
    """Create a valid design-contained plan with one task."""
    return "\n".join(
        (
            "+++",
            'artifact_kind = "plan"',
            "contract_version = 3",
            'design_ref = "design.md"',
            f'design_sha256 = "{design_sha256}"',
            'approval_status = "approved"',
            "truth_sync_required = true",
            'stable_truth_refs = ["README.md"]',
            "",
            "[scope]",
            'impl_file_refs = ["runtime/harness", "README.md"]',
            'test_file_refs = ["runtime/harness/tests"]',
            'external_impl_file_refs = ["/tmp/harness-evidence"]',
            "",
            "[[tasks]]",
            'task_id = "HSC-020"',
            "depends_on = []",
            'verification_commands = ["uv run pytest runtime/harness/tests"]',
            'scope_slice = "Implement the typed artifact compiler."',
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
            'done_when = ["Typed compilation passes."]',
            'failure_policy = "fix_forward"',
            'rollback_trigger = ""',
            'rollback_target = ""',
            'rollback_verification = ""',
            "",
            "[tasks.scope]",
            f'impl_file_refs = ["{task_impl_ref}"]',
            'test_file_refs = ["runtime/harness/tests/test_v3_artifacts.py"]',
            "external_impl_file_refs = []",
            "+++",
            "# Plan",
            "",
            "## Implementation",
            "",
            "Compile this v3 plan once.",
            "",
        )
    )


def write_valid_pair(tmp_path: Path) -> tuple[Path, Path]:
    """Write a digest-linked design and plan pair."""
    design = tmp_path / "design.md"
    design_contents = design_text()
    design.write_text(design_contents, encoding="utf-8")
    plan = tmp_path / "plan.md"
    plan.write_text(plan_text(digest(design_contents)), encoding="utf-8")
    return design, plan


def test_parse_valid_design_once_and_preserves_human_body(tmp_path: Path) -> None:
    """A v3 design parses exactly once and keeps its human-facing body."""
    design, _ = write_valid_pair(tmp_path)
    tracker = ReadTracker()

    artifact = parse_artifact(design, tracker)

    assert artifact.artifact_kind == "design"
    assert "## Boundaries" in artifact.body
    assert tracker.counts == {design.resolve(): 1}


@pytest.mark.parametrize(
    ("contents", "code"),
    [
        (
            design_text().replace("contract_version = 3", "contract_version = 2"),
            "unsupported-contract",
        ),
        (
            design_text().replace('artifact_kind = "design"', 'artifact_kind = "legacy"'),
            "invalid-artifact-kind",
        ),
        (
            design_text().replace(
                'impl_file_refs = ["runtime/harness", "README.md"]',
                'impl_file_refs = ["../escape", "README.md"]',
            ),
            "unsafe-repository-ref",
        ),
    ],
)
def test_v3_parser_rejects_legacy_kind_and_unsafe_refs(
    tmp_path: Path, contents: str, code: str
) -> None:
    """Legacy versions and unsafe paths have exact typed failures without a compatibility parser."""
    artifact_path = tmp_path / "design.md"
    artifact_path.write_text(contents, encoding="utf-8")

    with pytest.raises(HarnessError) as captured:
        parse_artifact(artifact_path)

    assert captured.value.code == code


def test_front_matter_must_be_single_valid_toml_block(tmp_path: Path) -> None:
    """Malformed and duplicate front matter cannot be accepted as an artifact."""
    artifact_path = tmp_path / "design.md"
    artifact_path.write_text(f"{design_text()}\n+++\n", encoding="utf-8")

    with pytest.raises(HarnessError) as duplicate:
        parse_artifact(artifact_path)

    assert duplicate.value.code == "invalid-front-matter"
    artifact_path.write_text("+++\nartifact_kind = [\n+++\n# Design\n", encoding="utf-8")
    with pytest.raises(HarnessError) as malformed:
        parse_artifact(artifact_path)

    assert malformed.value.code == "invalid-front-matter"


def test_compile_plan_reads_each_artifact_once_and_normalizes_authority(tmp_path: Path) -> None:
    """Compilation validates the design DAG once and makes stable structured output."""
    design, plan = write_valid_pair(tmp_path)
    tracker = ReadTracker()

    compiled = compile_plan(plan, tracker)

    assert tracker.counts == {plan.resolve(): 1, design.resolve(): 1}
    assert compiled.projection["artifact_kind"] == "compiled-plan"
    assert compiled.projection["tasks"] == [
        {
            "task_id": "HSC-020",
            "depends_on": [],
            "convergence_required": True,
            "delegation_policy": "allowed",
            "done_when": ["Typed compilation passes."],
            "execution_profile": "deep",
            "executor_mode": "subagent",
            "failure_policy": "fix_forward",
            "isolation": "isolated-worktree",
            "parallel_group": "none",
            "parallel_policy": "forbidden",
            "reasoning_profile": "deep",
            "resource_locks": ["runtime-harness"],
            "review_budget": 1,
            "rollback_target": "",
            "rollback_trigger": "",
            "rollback_verification": "",
            "scope": {
                "external_impl_file_refs": [],
                "impl_file_refs": ["runtime/harness/artifacts.py"],
                "test_file_refs": ["runtime/harness/tests/test_v3_artifacts.py"],
            },
            "scope_slice": "Implement the typed artifact compiler.",
            "task_review_depth": "full",
            "verification_commands": ["uv run pytest runtime/harness/tests"],
        }
    ]
    assert len(compiled.projection_sha256) == 64


def test_plan_compilation_rejects_digest_and_containment_drift(tmp_path: Path) -> None:
    """A linked design digest or task ref cannot silently expand authority."""
    design, plan = write_valid_pair(tmp_path)
    plan.write_text(plan_text("1" * 64), encoding="utf-8")

    with pytest.raises(HarnessError) as digest_mismatch:
        compile_plan(plan)

    assert digest_mismatch.value.code == "design-digest-mismatch"
    plan.write_text(
        plan_text(digest(design.read_text(encoding="utf-8")), "other/file.py"), encoding="utf-8"
    )
    with pytest.raises(HarnessError) as containment:
        compile_plan(plan)

    assert containment.value.code == "plan-containment-failed"


def test_plan_compilation_rejects_dependency_cycles(tmp_path: Path) -> None:
    """The artifact DAG rejects multi-task cycles before producing a projection."""
    design, plan = write_valid_pair(tmp_path)
    contents = plan_text(digest(design.read_text(encoding="utf-8"))).replace(
        "depends_on = []",
        'depends_on = ["HSC-021"]',
    )
    contents = contents.replace(
        "+++\n# Plan",
        '\n[[tasks]]\ntask_id = "HSC-021"\ndepends_on = ["HSC-020"]\n'
        'verification_commands = ["uv run pytest runtime/harness/tests"]\n'
        'scope_slice = "Implement the CLI."\nexecutor_mode = "subagent"\n'
        'parallel_group = "none"\nparallel_policy = "forbidden"\n'
        'delegation_policy = "allowed"\nexecution_profile = "deep"\n'
        'reasoning_profile = "deep"\nisolation = "isolated-worktree"\n'
        'resource_locks = ["runtime-harness"]\nconvergence_required = true\n'
        'review_budget = 1\ntask_review_depth = "full"\n'
        'done_when = ["CLI passes."]\nfailure_policy = "fix_forward"\n'
        'rollback_trigger = ""\nrollback_target = ""\nrollback_verification = ""\n\n'
        "[tasks.scope]\n"
        'impl_file_refs = ["runtime/harness/cli.py"]\n'
        'test_file_refs = ["runtime/harness/tests/test_v3_artifacts.py"]\n'
        "external_impl_file_refs = []\n+++\n# Plan",
    )
    plan.write_text(contents, encoding="utf-8")

    with pytest.raises(HarnessError) as cycle:
        compile_plan(plan)

    assert cycle.value.code == "invalid-artifact-dag"


def test_plan_projection_digest_is_independent_of_toml_key_order(tmp_path: Path) -> None:
    """Metadata insertion order does not influence the normalized authority projection digest."""
    design, plan = write_valid_pair(tmp_path)
    first = compile_plan(plan)
    plan.write_text(
        plan_text(digest(design.read_text(encoding="utf-8"))).replace(
            'artifact_kind = "plan"\ncontract_version = 3',
            'contract_version = 3\nartifact_kind = "plan"',
        ),
        encoding="utf-8",
    )

    second = compile_plan(plan)

    assert first.projection == second.projection
    assert first.projection_sha256 == second.projection_sha256


@pytest.mark.parametrize(
    ("kind", "body", "metadata"),
    [
        (
            "truth-sync",
            "# Truth Sync\n\n## Scope\n",
            'execution_result_ref = "runtime/harness/result.json"\n'
            f'execution_result_sha256 = "{"a" * 64}"\n'
            'ledger_ref = "runtime/harness/ledger.json"\n'
            f'ledger_sha256 = "{"b" * 64}"\n'
            'approval_status = "pending"',
        ),
        (
            "close",
            "# Close\n\n## Decision\n",
            'truth_sync_ref = "runtime/harness/truth.md"\n'
            f'truth_sync_sha256 = "{"c" * 64}"\n'
            'decision = "ready-for-close"\napproval_status = "pending"',
        ),
    ],
)
def test_truth_sync_and_close_share_the_v3_envelope(
    tmp_path: Path, kind: str, body: str, metadata: str
) -> None:
    """The non-plan lifecycle artifacts use the same strict version-3 envelope."""
    artifact_path = tmp_path / f"{kind}.md"
    contents = "\n".join(
        (
            "+++",
            f'artifact_kind = "{kind}"',
            "contract_version = 3",
            metadata,
            "",
            "[scope]",
            "impl_file_refs = []",
            "test_file_refs = []",
            "external_impl_file_refs = []",
            "+++",
            body,
        )
    )
    artifact_path.write_text(contents, encoding="utf-8")

    assert validate_artifact(artifact_path, kind).artifact_kind == kind


def test_cli_emits_complete_namespace_result_without_field_getters(tmp_path: Path) -> None:
    """One CLI invocation validates or compiles the full contract result in process."""
    _, plan = write_valid_pair(tmp_path)
    result = subprocess.run(
        [sys.executable, "-m", "runtime.harness.cli", "plan", "compile", str(plan)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["status"] == "ok"
    assert output["projection"]["artifact_kind"] == "compiled-plan"
    assert set(output["source_digests"]) == {"design_sha256", "plan_sha256"}
