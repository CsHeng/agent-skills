"""Version-4 ledger admission, attempt, path, and durability tests."""

from __future__ import annotations

import errno
import json
import os
import stat
from pathlib import Path

import pytest

from runtime.harness import ledger as ledger_runtime
from runtime.harness.artifacts import HarnessError
from runtime.harness.ledger import (
    Ledger,
    assert_task_touch_set,
    initialize_ledger,
    record_review,
    record_verification,
    transition,
    write_ledger,
)
from runtime.harness.tests.test_v3_artifacts import write_valid_pair as write_v3_pair
from runtime.harness.tests.test_v4_artifacts import (
    batch_text,
    parallel_tasks,
    task_text,
    write_pair,
)


def initialized_v4(tmp_path: Path) -> Ledger:
    """Create one initialized serial version-4 ledger."""
    _, plan = write_pair(tmp_path)
    return initialize_ledger(plan)


def task(ledger: Ledger, task_id: str = "V4-010") -> dict[str, object]:
    """Return one mutable test projection from a ledger."""
    tasks = ledger.data["tasks"]
    assert isinstance(tasks, list)
    for entry in tasks:
        if isinstance(entry, dict) and entry.get("task_id") == task_id:
            return entry
    raise AssertionError(f"missing task {task_id}")


def test_version_3_initialization_is_rejected_after_refresh(tmp_path: Path) -> None:
    """Version 3 remains parseable but cannot initialize new mutable authority."""
    _, plan = write_v3_pair(tmp_path)

    with pytest.raises(HarnessError) as captured:
        initialize_ledger(plan)

    assert captured.value.code == "legacy-ledger-read-only"


def test_version_4_initialization_uses_ledger_version_4(tmp_path: Path) -> None:
    """New plans initialize only the version-4 ledger shape."""
    ledger = initialized_v4(tmp_path)

    assert ledger.data["ledger_version"] == 4
    assert ledger.data["artifact_contract_version"] == 4
    assert ledger.data["admissions"] == []
    assert task(ledger)["attempt_history"] == []


def test_transition_cannot_bypass_ledger_admission(tmp_path: Path) -> None:
    """A ready version-4 task enters progress only through admission."""
    ledger = initialized_v4(tmp_path)

    with pytest.raises(HarnessError) as captured:
        transition(ledger, "V4-010", "in-progress")

    assert captured.value.code == "ledger-admission-required"
    admitted = ledger_runtime.admit_ready(ledger, ("V4-010",), capacity=1)
    provenance = task(admitted)["batch_provenance"]
    assert task(admitted)["status"] == "in-progress"
    assert isinstance(provenance, dict)
    assert provenance["kind"] == "serial"
    assert provenance["task_ids"] == ["V4-010"]


def test_independent_serial_task_cannot_join_an_active_admission(tmp_path: Path) -> None:
    """Serial-first authority permits only one active admission at a time."""
    task_tables = "\n\n".join(
        (
            task_text(
                "V4-010",
                impl_refs='["src/a.py"]',
                test_refs='["tests/test_a.py"]',
                resource_locks='["lock-a"]',
            ),
            task_text(
                "V4-020",
                impl_refs='["src/b.py"]',
                test_refs='["tests/test_b.py"]',
                resource_locks='["lock-b"]',
            ),
        )
    )
    _, plan = write_pair(tmp_path, task_tables=task_tables)
    ledger = initialize_ledger(plan)
    active = ledger_runtime.admit_ready(ledger, ("V4-010",), capacity=1)

    with pytest.raises(HarnessError) as captured:
        ledger_runtime.admit_ready(active, ("V4-020",), capacity=1)

    assert captured.value.code == "active-admission-conflict"


def write_parallel_plan(tmp_path: Path, *, policy: str = "required") -> Path:
    """Write one two-task version-4 parallel plan."""
    task_tables = parallel_tasks().replace(
        'parallel_policy = "required"', f'parallel_policy = "{policy}"'
    )
    _, plan = write_pair(
        tmp_path,
        task_tables=task_tables,
        parallel_execution_approved=True,
        batch_tables=batch_text(),
    )
    return plan


def test_required_batch_stops_when_capacity_is_unavailable(tmp_path: Path) -> None:
    """Required parallelism cannot silently serialize."""
    ledger = initialize_ledger(write_parallel_plan(tmp_path))

    with pytest.raises(HarnessError) as captured:
        ledger_runtime.admit_ready(ledger, ("V4-010", "V4-020"), capacity=1)

    assert captured.value.code == "parallel-capacity-required"


def test_allowed_batch_serializes_with_ledger_owned_evidence(tmp_path: Path) -> None:
    """Allowed peers may serialize, but the ledger records that decision."""
    ledger = initialize_ledger(write_parallel_plan(tmp_path, policy="allowed"))

    admitted = ledger_runtime.admit_ready(
        ledger,
        ("V4-010", "V4-020"),
        capacity=1,
    )

    first = task(admitted, "V4-010")
    second = task(admitted, "V4-020")
    provenance = first["batch_provenance"]
    assert first["status"] == "in-progress"
    assert second["status"] == "ready"
    assert isinstance(provenance, dict)
    assert provenance["kind"] == "batch"
    assert provenance["serialized"] is True
    assert provenance["admitted_task_ids"] == ["V4-010"]
    assert provenance["approved_task_ids"] == ["V4-010", "V4-020"]

    admitted = record_verification(admitted, "V4-010", "uv run pytest tests", True)
    admitted = transition(admitted, "V4-010", "verified")
    admitted = record_review(admitted, "V4-010", True, "review-1")
    admitted = transition(admitted, "V4-010", "reviewed")
    admitted = transition(admitted, "V4-010", "converged")
    continued = ledger_runtime.admit_ready(admitted, ("V4-020",), capacity=1)
    continued_provenance = task(continued, "V4-020")["batch_provenance"]

    assert task(continued, "V4-020")["status"] == "in-progress"
    assert isinstance(continued_provenance, dict)
    assert continued_provenance["approved_task_ids"] == ["V4-010", "V4-020"]
    assert continued_provenance["parent_admission_id"] == provenance["admission_id"]


def test_rejected_review_archives_complete_attempt_and_clears_eligibility(
    tmp_path: Path,
) -> None:
    """Repair preserves history but no active evidence can leak into the next attempt."""
    ledger = ledger_runtime.admit_ready(initialized_v4(tmp_path), ("V4-010",), capacity=1)
    command = "uv run pytest tests"
    ledger = record_verification(ledger, "V4-010", command, True)
    active_data = json.loads(json.dumps(ledger.data))
    active_task = task(Ledger(active_data))
    active_task["external_evidence"] = [{"attempt": 1, "state": "valid"}]
    ledger = transition(Ledger(active_data), "V4-010", "verified")

    reopened = record_review(ledger, "V4-010", False, "review-1")
    reopened_task = task(reopened)

    assert reopened_task["status"] == "ready"
    assert reopened_task["repair_attempts"] == 1
    assert reopened_task["verification_evidence"] == []
    assert reopened_task["external_evidence"] == []
    assert reopened_task["review"] is None
    assert reopened_task["batch_provenance"] is None
    assert reopened_task["attempt_history"] == [
        {
            "attempt": 1,
            "batch_provenance": task(ledger)["batch_provenance"],
            "external_evidence": [{"attempt": 1, "state": "valid"}],
            "review": {"batch_id": "review-1", "status": "rejected"},
            "verification_evidence": [
                {"attempt": 1, "command": command, "passed": True}
            ],
        }
    ]


@pytest.mark.parametrize(
    "changed_path",
    ("src//runtime.py", "src/../runtime.py", "src\\runtime.py", "src/*.py", "C:/outside.py"),
)
def test_touch_assertion_rejects_unsafe_path_spellings(
    tmp_path: Path, changed_path: str
) -> None:
    """Changed paths pass the same safe-reference validator as artifacts."""
    ledger = ledger_runtime.admit_ready(initialized_v4(tmp_path), ("V4-010",), capacity=1)

    with pytest.raises(HarnessError) as captured:
        assert_task_touch_set(ledger, "V4-010", (changed_path,))

    assert captured.value.code == "unsafe-repository-ref"


def mutated(ledger: Ledger) -> Ledger:
    """Return a distinguishable but projection-valid ledger state."""
    data = json.loads(json.dumps(ledger.data))
    data["lifecycle_state"] = "test-write"
    return Ledger(data)


def test_directory_open_failure_preserves_the_previous_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pre-promotion directory-open failure leaves authority unchanged."""
    ledger_path = tmp_path / "ledger.json"
    original = initialized_v4(tmp_path)
    write_ledger(ledger_path, original)
    before = ledger_path.read_bytes()

    def fail_directory_open(*_args: object, **_kwargs: object) -> int:
        raise OSError("directory open failed")

    monkeypatch.setattr(ledger_runtime.os, "open", fail_directory_open)
    with pytest.raises(HarnessError) as captured:
        write_ledger(ledger_path, mutated(original))

    assert captured.value.code == "ledger-write-failed"
    assert ledger_path.read_bytes() == before


def test_parent_creation_failure_is_a_typed_pre_promotion_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Parent creation failure cannot leak a raw operating-system error."""
    ledger_path = tmp_path / "missing" / "ledger.json"
    ledger = initialized_v4(tmp_path)
    real_mkdir = Path.mkdir

    def fail_target_parent(
        path: Path,
        mode: int = 0o777,
        parents: bool = False,
        exist_ok: bool = False,
    ) -> None:
        if path == ledger_path.parent:
            raise OSError("parent creation failed")
        real_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(Path, "mkdir", fail_target_parent)

    with pytest.raises(HarnessError) as captured:
        write_ledger(ledger_path, ledger)

    assert captured.value.code == "ledger-write-failed"
    assert not ledger_path.exists()


def test_predecessor_snapshot_failure_is_a_typed_pre_promotion_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A predecessor read race leaves its directory entry unchanged and fails typed."""
    ledger_path = tmp_path / "ledger.json"
    original = initialized_v4(tmp_path)
    write_ledger(ledger_path, original)
    before = ledger_path.read_bytes()
    real_read_bytes = Path.read_bytes

    def fail_target_read(path: Path) -> bytes:
        if path == ledger_path:
            raise OSError("predecessor snapshot failed")
        return real_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", fail_target_read)

    with pytest.raises(HarnessError) as captured:
        write_ledger(ledger_path, mutated(original))

    assert captured.value.code == "ledger-write-failed"
    monkeypatch.undo()
    assert ledger_path.read_bytes() == before


def test_failed_stat_probe_cannot_erase_an_existing_predecessor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A suppressed existence probe cannot downgrade an existing predecessor to absent."""
    ledger_path = tmp_path / "ledger.json"
    original = initialized_v4(tmp_path)
    write_ledger(ledger_path, original)
    before = ledger_path.read_bytes()
    real_stat = Path.stat
    real_fsync = os.fsync
    directory_calls = 0

    def hide_target(
        path: Path, *, follow_symlinks: bool = True
    ) -> os.stat_result:
        if path.name == ledger_path.name:
            raise FileNotFoundError(
                errno.ENOENT, "suppressed predecessor stat failure", path
            )
        return real_stat(path, follow_symlinks=follow_symlinks)

    def fail_first_directory_fsync(descriptor: int) -> None:
        nonlocal directory_calls
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            directory_calls += 1
            if directory_calls == 1:
                raise OSError("promotion barrier failed")
        real_fsync(descriptor)

    monkeypatch.setattr(Path, "stat", hide_target)
    monkeypatch.setattr(ledger_runtime.os, "fsync", fail_first_directory_fsync)

    with pytest.raises(HarnessError) as captured:
        write_ledger(ledger_path, mutated(original))

    assert captured.value.code == "ledger-write-failed"
    monkeypatch.undo()
    assert ledger_path.read_bytes() == before


def test_post_promotion_failure_reports_only_after_confirmed_restoration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One failed directory barrier restores and durably confirms the predecessor."""
    ledger_path = tmp_path / "ledger.json"
    original = initialized_v4(tmp_path)
    write_ledger(ledger_path, original)
    before = ledger_path.read_bytes()
    real_fsync = os.fsync
    directory_calls = 0

    def fail_first_directory_fsync(descriptor: int) -> None:
        nonlocal directory_calls
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            directory_calls += 1
            if directory_calls == 1:
                raise OSError("promotion barrier failed")
        real_fsync(descriptor)

    monkeypatch.setattr(ledger_runtime.os, "fsync", fail_first_directory_fsync)
    with pytest.raises(HarnessError) as captured:
        write_ledger(ledger_path, mutated(original))

    assert captured.value.code == "ledger-write-failed"
    assert ledger_path.read_bytes() == before


def test_unconfirmed_restoration_returns_durability_unknown_and_keeps_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unprovable post-promotion outcome forbids blind retry."""
    ledger_path = tmp_path / "ledger.json"
    original = initialized_v4(tmp_path)
    write_ledger(ledger_path, original)
    real_fsync = os.fsync

    def fail_directory_fsync(descriptor: int) -> None:
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError("directory durability unknown")
        real_fsync(descriptor)

    monkeypatch.setattr(ledger_runtime.os, "fsync", fail_directory_fsync)
    with pytest.raises(HarnessError) as captured:
        write_ledger(ledger_path, mutated(original))

    assert captured.value.code == "ledger-durability-unknown"
    assert list(tmp_path.glob(".ledger.json.recovery.*"))


def test_committed_write_is_not_reported_failed_when_recovery_cleanup_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recovery cleanup cannot turn a durably promoted ledger into retryable failure."""
    ledger_path = tmp_path / "ledger.json"
    original = initialized_v4(tmp_path)
    write_ledger(ledger_path, original)
    real_unlink = Path.unlink

    def fail_recovery_unlink(path: Path, missing_ok: bool = False) -> None:
        if path.name.startswith(".ledger.json.recovery."):
            raise OSError("recovery cleanup failed")
        real_unlink(path, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", fail_recovery_unlink)

    write_ledger(ledger_path, mutated(original))

    assert json.loads(ledger_path.read_text(encoding="utf-8"))["lifecycle_state"] == "test-write"
    assert list(tmp_path.glob(".ledger.json.recovery.*"))
