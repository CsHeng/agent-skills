"""Validate exact external files and emit secret-safe filesystem evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

SCHEMA_VERSION = 1
HASH_CHUNK_BYTES = 1024 * 1024
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
GLOB_CHARACTERS = frozenset("*?[]{}")


class ExternalTouchError(RuntimeError):
    """Raised when an external-touch invariant fails."""

    def __init__(self, code: str, message: str, *, exit_code: int = 2) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


def _require_token(value: str, field: str) -> None:
    if not TOKEN_PATTERN.fullmatch(value):
        raise ExternalTouchError(
            "external_touch_invalid_context",
            f"{field} must be a portable non-empty token",
        )


def _require_sha256(value: str, field: str) -> None:
    if not SHA256_PATTERN.fullmatch(value):
        raise ExternalTouchError(
            "external_touch_invalid_context",
            f"{field} must be a lowercase SHA-256 digest",
        )


def _has_forbidden_path_character(value: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in value) or any(
        character in GLOB_CHARACTERS for character in value
    )


def _walk_has_symlink(path: Path) -> bool:
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        if current.is_symlink():
            return True
    return False


def _canonical_existing_regular_file(repo_root: Path, declared_ref: str) -> Path:
    if not declared_ref or not os.path.isabs(declared_ref):
        raise ExternalTouchError("external_touch_invalid_path", "external ref must be absolute")
    if declared_ref.endswith(os.sep) or _has_forbidden_path_character(declared_ref):
        raise ExternalTouchError(
            "external_touch_invalid_path",
            "external ref contains a forbidden character or trailing separator",
        )
    if any(component in {".", ".."} for component in declared_ref.split(os.sep)):
        raise ExternalTouchError(
            "external_touch_invalid_path", "external ref contains a dot component"
        )

    declared_path = Path(declared_ref)
    try:
        canonical_path = declared_path.resolve(strict=True)
    except (FileNotFoundError, NotADirectoryError, OSError) as exc:
        raise ExternalTouchError(
            "external_touch_missing_target", "external target does not exist"
        ) from exc

    if str(canonical_path) != declared_ref or _walk_has_symlink(declared_path):
        raise ExternalTouchError(
            "external_touch_noncanonical_path",
            "external ref must equal its symlink-free canonical path",
        )

    try:
        file_stat = os.lstat(canonical_path)
    except OSError as exc:
        raise ExternalTouchError(
            "external_touch_metadata_unavailable",
            "external target metadata is unavailable",
        ) from exc
    if not stat.S_ISREG(file_stat.st_mode):
        raise ExternalTouchError(
            "external_touch_not_regular", "external target must be a regular file"
        )
    if file_stat.st_nlink != 1:
        raise ExternalTouchError(
            "external_touch_hardlink_rejected",
            "external target must have exactly one hard link",
        )

    canonical_repo = repo_root.resolve(strict=True)
    if canonical_path == canonical_repo or canonical_repo in canonical_path.parents:
        raise ExternalTouchError(
            "external_touch_repository_overlap",
            "external target must remain outside the controller repository",
        )
    return canonical_path


def _hash_open_file(file_descriptor: int) -> str:
    digest = hashlib.sha256()
    os.lseek(file_descriptor, 0, os.SEEK_SET)
    while True:
        chunk = os.read(file_descriptor, HASH_CHUNK_BYTES)
        if not chunk:
            break
        digest.update(chunk)
    return digest.hexdigest()


def capture_file_evidence(repo_root: Path, declared_ref: str) -> dict[str, object]:
    """Capture hash and identity evidence for one exact external regular file."""

    canonical_path = _canonical_existing_regular_file(repo_root, declared_ref)
    open_flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        open_flags |= os.O_NOFOLLOW
    try:
        file_descriptor = os.open(canonical_path, open_flags)
    except OSError as exc:
        raise ExternalTouchError(
            "external_touch_open_failed", "external target could not be opened safely"
        ) from exc

    try:
        file_stat = os.fstat(file_descriptor)
        path_stat = os.lstat(canonical_path)
        if not stat.S_ISREG(file_stat.st_mode) or file_stat.st_nlink != 1:
            raise ExternalTouchError(
                "external_touch_identity_drift",
                "opened target is no longer a single-link regular file",
                exit_code=3,
            )
        if (file_stat.st_dev, file_stat.st_ino) != (path_stat.st_dev, path_stat.st_ino):
            raise ExternalTouchError(
                "external_touch_identity_drift",
                "opened target identity differs from the declared path",
                exit_code=3,
            )
        sha256 = _hash_open_file(file_descriptor)
    finally:
        os.close(file_descriptor)

    return {
        "ref": str(canonical_path),
        "sha256": sha256,
        "size": file_stat.st_size,
        "file_type": "regular",
        "mode": f"{stat.S_IMODE(file_stat.st_mode):04o}",
        "uid": file_stat.st_uid,
        "gid": file_stat.st_gid,
        "st_dev": file_stat.st_dev,
        "st_ino": file_stat.st_ino,
        "st_nlink": file_stat.st_nlink,
    }


def capture_baseline(
    *,
    repo_root: Path,
    refs: Sequence[str],
    run_id: str,
    task_id: str,
    design_sha256: str,
    plan_sha256: str,
) -> dict[str, object]:
    """Capture an immutable, content-free baseline for sorted exact refs."""

    _require_token(run_id, "run_id")
    _require_token(task_id, "task_id")
    _require_sha256(design_sha256, "design_sha256")
    _require_sha256(plan_sha256, "plan_sha256")
    normalized_refs = sorted(set(refs))
    if not normalized_refs or len(normalized_refs) != len(refs):
        raise ExternalTouchError(
            "external_touch_invalid_ref_set",
            "external refs must be non-empty and unique",
        )

    evidence = [capture_file_evidence(repo_root, ref) for ref in normalized_refs]
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "task_id": task_id,
        "design_sha256": design_sha256,
        "plan_sha256": plan_sha256,
        "refs": evidence,
    }


def _capture_private_file(path: Path) -> dict[str, object]:
    try:
        file_stat = os.lstat(path)
    except OSError as exc:
        raise ExternalTouchError(
            "external_touch_staged_payload_missing", "staged payload is unavailable"
        ) from exc
    if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(file_stat.st_mode):
        raise ExternalTouchError(
            "external_touch_staged_payload_invalid",
            "staged payload must be a non-symlink regular file",
        )
    if file_stat.st_nlink != 1:
        raise ExternalTouchError(
            "external_touch_staged_payload_invalid",
            "staged payload must have exactly one hard link",
        )
    open_flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        open_flags |= os.O_NOFOLLOW
    try:
        file_descriptor = os.open(path, open_flags)
    except OSError as exc:
        raise ExternalTouchError(
            "external_touch_staged_payload_invalid",
            "staged payload could not be opened safely",
        ) from exc
    try:
        opened_stat = os.fstat(file_descriptor)
        if (opened_stat.st_dev, opened_stat.st_ino) != (
            file_stat.st_dev,
            file_stat.st_ino,
        ):
            raise ExternalTouchError(
                "external_touch_staged_payload_invalid",
                "staged payload identity changed while opening",
            )
        sha256 = _hash_open_file(file_descriptor)
    finally:
        os.close(file_descriptor)
    return {
        "path": str(path),
        "sha256": sha256,
        "size": opened_stat.st_size,
        "mode": f"{stat.S_IMODE(opened_stat.st_mode):04o}",
        "uid": opened_stat.st_uid,
        "gid": opened_stat.st_gid,
        "st_dev": opened_stat.st_dev,
        "st_ino": opened_stat.st_ino,
        "st_nlink": opened_stat.st_nlink,
    }


def _validate_run_dir(run_dir: Path) -> Path:
    try:
        canonical_dir = run_dir.resolve(strict=True)
        directory_stat = os.lstat(canonical_dir)
    except OSError as exc:
        raise ExternalTouchError(
            "external_touch_run_dir_invalid", "run directory is unavailable"
        ) from exc
    if str(canonical_dir) != str(run_dir) or stat.S_ISLNK(directory_stat.st_mode):
        raise ExternalTouchError(
            "external_touch_run_dir_invalid",
            "run directory must be a canonical non-symlink path",
        )
    if not stat.S_ISDIR(directory_stat.st_mode):
        raise ExternalTouchError(
            "external_touch_run_dir_invalid", "run directory must be a directory"
        )
    if stat.S_IMODE(directory_stat.st_mode) != 0o700 or directory_stat.st_uid != os.getuid():
        raise ExternalTouchError(
            "external_touch_run_dir_invalid",
            "run directory must be owned by the current user with mode 0700",
        )
    return canonical_dir


def stage_payload(*, run_dir: Path, intent_id: str, source_file: Path) -> dict[str, object]:
    """Copy candidate content into a private, run-owned staging file."""

    _require_token(intent_id, "intent_id")
    canonical_run_dir = _validate_run_dir(run_dir)
    source_path = source_file.resolve(strict=True)
    source_evidence = _capture_private_file(source_path)
    payload_dir = canonical_run_dir / "payloads"
    if payload_dir.exists():
        _validate_run_dir(payload_dir)
    else:
        payload_dir.mkdir(mode=0o700)
    staged_path = payload_dir / f"{intent_id}.payload"
    open_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        open_flags |= os.O_NOFOLLOW
    try:
        destination_fd = os.open(staged_path, open_flags, 0o600)
    except OSError as exc:
        raise ExternalTouchError(
            "external_touch_stage_exists", "private staged payload already exists"
        ) from exc
    try:
        with (
            source_path.open("rb") as source_handle,
            os.fdopen(destination_fd, "wb", closefd=False) as destination_handle,
        ):
            shutil.copyfileobj(source_handle, destination_handle, HASH_CHUNK_BYTES)
            destination_handle.flush()
        os.fchmod(destination_fd, 0o600)
        os.fsync(destination_fd)
    finally:
        os.close(destination_fd)
    staged_evidence = _capture_private_file(staged_path)
    if staged_evidence["sha256"] != source_evidence["sha256"]:
        raise ExternalTouchError(
            "external_touch_stage_mismatch",
            "staged payload hash differs from its source",
        )
    staged_evidence["run_dir"] = str(canonical_run_dir)
    return staged_evidence


def _declared_staged_path(run_dir: Path, intent_id: str) -> tuple[Path, Path]:
    canonical_run_dir = _validate_run_dir(run_dir)
    payload_dir = canonical_run_dir / "payloads"
    if payload_dir.exists():
        _validate_run_dir(payload_dir)
    else:
        payload_dir.mkdir(mode=0o700)
        _fsync_directory(canonical_run_dir)
    return canonical_run_dir, payload_dir / f"{intent_id}.payload"


def declare_intent(
    *,
    repo_root: Path,
    baseline: Mapping[str, object],
    intents: Sequence[Mapping[str, object]],
    ref: str,
    intent_id: str,
    run_dir: Path,
    source_file: Path,
) -> dict[str, object]:
    """Declare a ledger-persistable staging reservation before copying payload bytes."""

    _require_token(intent_id, "intent_id")
    baseline_ref = _baseline_ref(baseline, ref)
    chain = _intent_chain(baseline_ref, intents, ref, require_applied=True, require_cleanup=True)
    if any(intent.get("intent_id") == intent_id for intent in intents):
        raise ExternalTouchError(
            "external_touch_duplicate_intent", "intent ID must be globally unique"
        )
    parent = dict(cast(Mapping[str, object], chain[-1]["after"])) if chain else dict(baseline_ref)
    current = capture_file_evidence(repo_root, ref)
    if not _evidence_equal(current, parent):
        raise ExternalTouchError(
            "external_touch_baseline_drift",
            "target no longer matches the immediate parent",
            exit_code=3,
        )
    source_path = source_file.resolve(strict=True)
    source_evidence = _capture_private_file(source_path)
    if source_evidence["sha256"] == parent["sha256"]:
        raise ExternalTouchError(
            "external_touch_noop_candidate",
            "candidate content must differ from its immediate parent",
        )
    canonical_run_dir, staged_path = _declared_staged_path(run_dir, intent_id)
    run_id = cast(str, baseline.get("run_id", ""))
    task_id = cast(str, baseline.get("task_id", ""))
    _require_token(run_id, "run_id")
    _require_token(task_id, "task_id")
    candidate_path = _broker_candidate_path(
        run_id=run_id, task_id=task_id, ref=ref, intent_id=intent_id
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "task_id": task_id,
        "intent_id": intent_id,
        "sequence": len(chain) + 1,
        "ref": ref,
        "root_baseline": dict(baseline_ref),
        "parent": parent,
        "candidate": {
            "path": str(staged_path),
            "run_dir": str(canonical_run_dir),
            "sha256": source_evidence["sha256"],
            "size": source_evidence["size"],
        },
        "preserved_metadata": {
            field: parent[field] for field in ("file_type", "mode", "uid", "gid")
        },
        "broker_candidate_basename": candidate_path.name,
        "broker_candidate_path": str(candidate_path),
        "state": "staging",
        "after": None,
        "cleanup": None,
    }


def stage_declared_payload(*, intent: Mapping[str, object], source_file: Path) -> dict[str, object]:
    """Materialize or replay the exact private payload reserved by a staging intent."""

    if intent.get("state") != "staging":
        raise ExternalTouchError(
            "external_touch_intent_state_invalid", "staging requires a staging intent"
        )
    candidate = cast(Mapping[str, object], intent.get("candidate", {}))
    intent_id = cast(str, intent.get("intent_id", ""))
    _require_token(intent_id, "intent_id")
    canonical_run_dir, expected_path = _declared_staged_path(
        Path(cast(str, candidate.get("run_dir", ""))), intent_id
    )
    if Path(cast(str, candidate.get("path", ""))) != expected_path:
        raise ExternalTouchError(
            "external_touch_stage_path_invalid",
            "staging intent path is not derived from its run and intent identity",
        )
    source_path = source_file.resolve(strict=True)
    source_evidence = _capture_private_file(source_path)
    if source_evidence.get("sha256") != candidate.get("sha256") or source_evidence.get(
        "size"
    ) != candidate.get("size"):
        raise ExternalTouchError(
            "external_touch_stage_mismatch",
            "source payload differs from the persisted staging reservation",
            exit_code=3,
        )
    if os.path.lexists(expected_path):
        staged_evidence = _capture_private_file(expected_path)
        if (
            staged_evidence.get("sha256") != candidate.get("sha256")
            or staged_evidence.get("size") != candidate.get("size")
            or staged_evidence.get("mode") != "0600"
            or staged_evidence.get("uid") != os.getuid()
        ):
            raise ExternalTouchError(
                "external_touch_stage_mismatch",
                "existing staged payload differs from its ledger reservation",
                exit_code=3,
            )
    else:
        staged_evidence = stage_payload(
            run_dir=canonical_run_dir,
            intent_id=intent_id,
            source_file=source_path,
        )
    staged_evidence["run_dir"] = str(canonical_run_dir)
    return staged_evidence


def finalize_intent(
    *, intent: Mapping[str, object], staged_payload: Mapping[str, object]
) -> dict[str, object]:
    """Promote a staging reservation to the prepared write-ahead checkpoint."""

    if intent.get("state") != "staging":
        raise ExternalTouchError(
            "external_touch_intent_state_invalid", "finalize requires a staging intent"
        )
    declared = cast(Mapping[str, object], intent.get("candidate", {}))
    for field in ("path", "run_dir", "sha256", "size"):
        if staged_payload.get(field) != declared.get(field):
            raise ExternalTouchError(
                "external_touch_stage_mismatch",
                "staged evidence differs from its ledger reservation",
                exit_code=3,
            )
    if staged_payload.get("mode") != "0600" or staged_payload.get("uid") != os.getuid():
        raise ExternalTouchError(
            "external_touch_staged_payload_invalid",
            "staged payload must be current-user owned with mode 0600",
        )
    result = dict(intent)
    result.update(candidate=dict(staged_payload), state="prepared")
    return result


def _evidence_equal(
    left: Mapping[str, object], right: Mapping[str, object], *, include_ref: bool = True
) -> bool:
    fields = [
        "sha256",
        "size",
        "file_type",
        "mode",
        "uid",
        "gid",
        "st_dev",
        "st_ino",
        "st_nlink",
    ]
    if include_ref:
        fields.append("ref")
    return all(left.get(field) == right.get(field) for field in fields)


def _baseline_ref(baseline: Mapping[str, object], ref: str) -> dict[str, object]:
    refs = cast(Sequence[Mapping[str, object]], baseline.get("refs", []))
    matching = [dict(item) for item in refs if item.get("ref") == ref]
    if len(matching) != 1:
        raise ExternalTouchError(
            "external_touch_ref_not_in_baseline",
            "external ref must appear exactly once in the baseline",
        )
    return matching[0]


def _intent_chain(
    baseline_ref: Mapping[str, object],
    intents: Sequence[Mapping[str, object]],
    ref: str,
    *,
    require_applied: bool,
    require_cleanup: bool = False,
) -> list[dict[str, object]]:
    selected = [dict(intent) for intent in intents if intent.get("ref") == ref]
    try:
        selected.sort(key=lambda item: int(cast(int, item.get("sequence", 0))))
    except (TypeError, ValueError) as exc:
        raise ExternalTouchError(
            "external_touch_intent_chain_invalid", "intent sequence must be an integer"
        ) from exc
    expected_parent = dict(baseline_ref)
    for sequence, intent in enumerate(selected, start=1):
        if intent.get("sequence") != sequence:
            raise ExternalTouchError(
                "external_touch_intent_chain_invalid",
                "intent sequence must be contiguous and start at one",
            )
        root = cast(Mapping[str, object], intent.get("root_baseline", {}))
        parent = cast(Mapping[str, object], intent.get("parent", {}))
        if not _evidence_equal(root, baseline_ref) or not _evidence_equal(parent, expected_parent):
            raise ExternalTouchError(
                "external_touch_intent_chain_invalid",
                "intent root or immediate parent does not match the chain",
            )
        if require_applied and intent.get("state") != "applied":
            raise ExternalTouchError(
                "external_touch_intent_not_applied",
                "convergence requires every intent to be applied",
            )
        if (
            require_cleanup
            and intent.get("state") == "applied"
            and (
                intent.get("cleanup")
                != {
                    "state": "completed",
                    "staged_path_absent": True,
                    "broker_candidate_path_absent": True,
                }
            )
        ):
            raise ExternalTouchError(
                "external_touch_cleanup_incomplete",
                "convergence requires completed private-artifact cleanup",
            )
        if intent.get("state") == "applied":
            after = cast(Mapping[str, object], intent.get("after", {}))
            if not after:
                raise ExternalTouchError(
                    "external_touch_intent_chain_invalid",
                    "applied intent is missing after evidence",
                )
            expected_parent = dict(after)
        elif sequence != len(selected):
            raise ExternalTouchError(
                "external_touch_intent_chain_invalid",
                "only the final intent may remain prepared",
            )
    return selected


def _broker_candidate_path(*, run_id: str, task_id: str, ref: str, intent_id: str) -> Path:
    opaque_id = hashlib.sha256(f"{run_id}\0{task_id}\0{ref}\0{intent_id}".encode()).hexdigest()[:24]
    return Path(ref).parent / f".codex-external-touch-{opaque_id}.tmp"


def _candidate_matches_target(current: Mapping[str, object], intent: Mapping[str, object]) -> bool:
    candidate = cast(Mapping[str, object], intent.get("candidate", {}))
    parent = cast(Mapping[str, object], intent.get("parent", {}))
    metadata = cast(Mapping[str, object], intent.get("preserved_metadata", {}))
    return (
        current.get("ref") == intent.get("ref")
        and current.get("sha256") == candidate.get("sha256")
        and current.get("size") == candidate.get("size")
        and current.get("file_type") == metadata.get("file_type")
        and current.get("mode") == metadata.get("mode")
        and current.get("uid") == metadata.get("uid")
        and current.get("gid") == metadata.get("gid")
        and current.get("st_nlink") == 1
        and current.get("st_dev") == parent.get("st_dev")
        and current.get("st_ino") != parent.get("st_ino")
    )


def _copy_broker_candidate(
    *, staged_path: Path, candidate_path: Path, parent: Mapping[str, object]
) -> None:
    open_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        open_flags |= os.O_NOFOLLOW
    try:
        destination_fd = os.open(candidate_path, open_flags, 0o600)
    except FileExistsError:
        return
    except OSError as exc:
        raise ExternalTouchError(
            "external_touch_broker_create_failed",
            "broker could not create its private sibling candidate",
            exit_code=4,
        ) from exc
    try:
        with (
            staged_path.open("rb") as source_handle,
            os.fdopen(destination_fd, "wb", closefd=False) as destination_handle,
        ):
            shutil.copyfileobj(source_handle, destination_handle, HASH_CHUNK_BYTES)
            destination_handle.flush()
        os.fchmod(destination_fd, int(cast(str, parent["mode"]), 8))
        candidate_stat = os.fstat(destination_fd)
        expected_uid = cast(int, parent["uid"])
        expected_gid = cast(int, parent["gid"])
        if (candidate_stat.st_uid, candidate_stat.st_gid) != (
            expected_uid,
            expected_gid,
        ):
            os.fchown(destination_fd, expected_uid, expected_gid)
        os.fsync(destination_fd)
    except OSError as exc:
        raise ExternalTouchError(
            "external_touch_broker_write_failed",
            "broker could not prepare its private sibling candidate",
            exit_code=4,
        ) from exc
    finally:
        os.close(destination_fd)


def _fsync_directory(directory: Path) -> None:
    open_flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        open_flags |= os.O_DIRECTORY
    directory_fd = os.open(directory, open_flags)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _fsync_file(path: Path) -> None:
    open_flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        open_flags |= os.O_NOFOLLOW
    file_descriptor = os.open(path, open_flags)
    try:
        os.fsync(file_descriptor)
    finally:
        os.close(file_descriptor)


def durable_replace_file(*, staged_file: Path, destination_file: Path) -> dict[str, object]:
    """Durably replace one same-directory state file and fsync both barriers."""

    if not staged_file.is_absolute() or not destination_file.is_absolute():
        raise ExternalTouchError(
            "external_touch_state_path_invalid", "state paths must be absolute"
        )
    if staged_file.parent != destination_file.parent:
        raise ExternalTouchError(
            "external_touch_state_path_invalid",
            "durable state replacement requires one parent directory",
        )
    staged_stat = os.lstat(staged_file)
    if stat.S_ISLNK(staged_stat.st_mode) or not stat.S_ISREG(staged_stat.st_mode):
        raise ExternalTouchError(
            "external_touch_state_path_invalid",
            "staged state must be a non-symlink regular file",
        )
    _fsync_file(staged_file)
    os.replace(staged_file, destination_file)
    _fsync_directory(destination_file.parent)
    return {"state": "replaced", "destination": str(destination_file)}


def apply_intent(*, repo_root: Path, intent: Mapping[str, object]) -> dict[str, object]:
    """Apply or idempotently replay one prepared compare-and-swap intent."""

    if intent.get("state") not in {"prepared", "applied"}:
        raise ExternalTouchError(
            "external_touch_intent_state_invalid", "intent state is unsupported"
        )
    ref = cast(str, intent.get("ref", ""))
    parent = cast(Mapping[str, object], intent.get("parent", {}))
    candidate = cast(Mapping[str, object], intent.get("candidate", {}))
    current = capture_file_evidence(repo_root, ref)
    if _candidate_matches_target(current, intent):
        _fsync_directory(Path(ref).parent)
        result = dict(intent)
        result.update(state="applied", after=current, replay_state="already_applied")
        return result
    if not _evidence_equal(current, parent):
        raise ExternalTouchError(
            "external_touch_baseline_drift",
            "target matches neither the immediate parent nor candidate",
            exit_code=3,
        )

    staged_path = Path(cast(str, candidate.get("path", "")))
    staged_evidence = _capture_private_file(staged_path)
    if staged_evidence.get("sha256") != candidate.get("sha256") or staged_evidence.get(
        "size"
    ) != candidate.get("size"):
        raise ExternalTouchError(
            "external_touch_stage_mismatch",
            "staged payload changed before broker apply",
            exit_code=3,
        )
    expected_candidate_path = _broker_candidate_path(
        run_id=cast(str, intent.get("run_id", "")),
        task_id=cast(str, intent.get("task_id", "")),
        ref=ref,
        intent_id=cast(str, intent.get("intent_id", "")),
    )
    candidate_path = Path(cast(str, intent.get("broker_candidate_path", "")))
    if candidate_path != expected_candidate_path:
        raise ExternalTouchError(
            "external_touch_broker_path_invalid",
            "broker candidate path is not derived from the prepared intent",
        )
    _copy_broker_candidate(staged_path=staged_path, candidate_path=candidate_path, parent=parent)
    broker_evidence = _capture_private_file(candidate_path)
    metadata = cast(Mapping[str, object], intent.get("preserved_metadata", {}))
    if not (
        broker_evidence.get("sha256") == candidate.get("sha256")
        and broker_evidence.get("size") == candidate.get("size")
        and broker_evidence.get("mode") == metadata.get("mode")
        and broker_evidence.get("uid") == metadata.get("uid")
        and broker_evidence.get("gid") == metadata.get("gid")
    ):
        raise ExternalTouchError(
            "external_touch_broker_candidate_ambiguous",
            "broker candidate does not match the prepared intent",
            exit_code=4,
        )
    current = capture_file_evidence(repo_root, ref)
    if not _evidence_equal(current, parent):
        raise ExternalTouchError(
            "external_touch_baseline_drift",
            "target changed before atomic replacement",
            exit_code=3,
        )
    os.replace(candidate_path, Path(ref))
    _fsync_directory(Path(ref).parent)
    after = capture_file_evidence(repo_root, ref)
    if not _candidate_matches_target(after, intent):
        raise ExternalTouchError(
            "external_touch_broker_verification_failed",
            "replaced target does not match the prepared intent",
            exit_code=4,
        )
    result = dict(intent)
    result.update(state="applied", after=after, replay_state="applied_now")
    return result


def _remove_exact_private_file(path: Path, sha256: object) -> bool:
    if not path.exists():
        return False
    try:
        evidence = _capture_private_file(path)
    except ExternalTouchError as exc:
        raise ExternalTouchError(
            "external_touch_cleanup_ambiguous",
            "cleanup target is not the exact ledger-bound private file",
            exit_code=5,
        ) from exc
    if evidence.get("sha256") != sha256:
        raise ExternalTouchError(
            "external_touch_cleanup_ambiguous",
            "cleanup target hash differs from the ledger-bound candidate",
            exit_code=5,
        )
    path.unlink()
    _fsync_directory(path.parent)
    return True


def cleanup_intent(
    *, intent: Mapping[str, object], allow_prepared: bool = False
) -> dict[str, object]:
    """Remove only exact private files bound to an applied or abandoned intent."""

    if intent.get("state") != "applied" and not (
        allow_prepared and intent.get("state") == "prepared"
    ):
        raise ExternalTouchError(
            "external_touch_cleanup_state_invalid",
            "cleanup requires an applied intent or explicit prepared cleanup",
            exit_code=5,
        )
    candidate = cast(Mapping[str, object], intent.get("candidate", {}))
    sha256 = candidate.get("sha256")
    staged_path = Path(cast(str, candidate.get("path", "")))
    broker_path = Path(cast(str, intent.get("broker_candidate_path", "")))
    intent_id = cast(str, intent.get("intent_id", ""))
    run_id = cast(str, intent.get("run_id", ""))
    task_id = cast(str, intent.get("task_id", ""))
    ref = cast(str, intent.get("ref", ""))
    try:
        _require_token(intent_id, "intent_id")
        _require_token(run_id, "run_id")
        _require_token(task_id, "task_id")
        canonical_run_dir = _validate_run_dir(Path(cast(str, candidate.get("run_dir", ""))))
    except ExternalTouchError as exc:
        raise ExternalTouchError(
            "external_touch_cleanup_ambiguous",
            "staged cleanup run directory is not ledger-bound private state",
            exit_code=5,
        ) from exc
    if staged_path != canonical_run_dir / "payloads" / f"{intent_id}.payload":
        raise ExternalTouchError(
            "external_touch_cleanup_ambiguous",
            "staged cleanup path is not derived from the intent identity",
            exit_code=5,
        )
    expected_broker_path = _broker_candidate_path(
        run_id=run_id, task_id=task_id, ref=ref, intent_id=intent_id
    )
    if broker_path != expected_broker_path:
        raise ExternalTouchError(
            "external_touch_cleanup_ambiguous",
            "broker cleanup path is not derived from the intent identity",
            exit_code=5,
        )
    removed = []
    for private_path in (staged_path, broker_path):
        if _remove_exact_private_file(private_path, sha256):
            removed.append(str(private_path))
    return {
        "state": "completed",
        "removed": removed,
        "staged_path_absent": not os.path.lexists(staged_path),
        "broker_candidate_path_absent": not os.path.lexists(broker_path),
    }


def apply_and_cleanup_intent(*, repo_root: Path, intent: Mapping[str, object]) -> dict[str, object]:
    """Apply/replay one intent and checkpoint completed cleanup in one result."""

    applied = apply_intent(repo_root=repo_root, intent=intent)
    cleanup = cleanup_intent(intent=applied)
    if not cleanup["staged_path_absent"] or not cleanup["broker_candidate_path_absent"]:
        raise ExternalTouchError(
            "external_touch_cleanup_incomplete",
            "private artifacts remain after apply cleanup",
            exit_code=5,
        )
    result = dict(applied)
    result["cleanup"] = {
        "state": "completed",
        "staged_path_absent": True,
        "broker_candidate_path_absent": True,
    }
    return result


def _validate_cleanup_absent(intent: Mapping[str, object]) -> None:
    candidate = cast(Mapping[str, object], intent.get("candidate", {}))
    staged_path = Path(cast(str, candidate.get("path", "")))
    broker_path = Path(cast(str, intent.get("broker_candidate_path", "")))
    if os.path.lexists(staged_path) or os.path.lexists(broker_path):
        raise ExternalTouchError(
            "external_touch_cleanup_incomplete",
            "ledger-bound private artifacts remain on disk",
            exit_code=5,
        )


def validate_evidence_state(
    *,
    baseline: Mapping[str, object],
    intents: Sequence[Mapping[str, object]],
    expected_task_id: str,
    expected_run_id: str,
    expected_design_sha256: str,
    expected_plan_sha256: str,
    expected_refs: Sequence[str],
    require_applied: bool,
    require_cleanup: bool,
    check_cleanup_paths: bool,
) -> dict[str, object]:
    """Validate strict metadata-only baseline and intent-chain bindings."""

    baseline_keys = {
        "schema_version",
        "run_id",
        "task_id",
        "design_sha256",
        "plan_sha256",
        "refs",
    }
    if set(baseline) != baseline_keys or baseline.get("schema_version") != SCHEMA_VERSION:
        raise ExternalTouchError("external_touch_evidence_invalid", "baseline schema is not exact")
    if (
        baseline.get("task_id") != expected_task_id
        or baseline.get("run_id") != expected_run_id
        or baseline.get("design_sha256") != expected_design_sha256
        or baseline.get("plan_sha256") != expected_plan_sha256
    ):
        raise ExternalTouchError(
            "external_touch_evidence_binding_invalid",
            "baseline identity differs from the approved execution context",
        )
    refs = cast(Sequence[Mapping[str, object]], baseline.get("refs", []))
    normalized_refs = sorted(expected_refs)
    if sorted(cast(str, item.get("ref", "")) for item in refs) != normalized_refs:
        raise ExternalTouchError(
            "external_touch_evidence_binding_invalid",
            "baseline refs differ from the approved task refs",
        )
    file_keys = {
        "ref",
        "sha256",
        "size",
        "file_type",
        "mode",
        "uid",
        "gid",
        "st_dev",
        "st_ino",
        "st_nlink",
    }
    for evidence in refs:
        if (
            set(evidence) != file_keys
            or evidence.get("file_type") != "regular"
            or evidence.get("st_nlink") != 1
            or not SHA256_PATTERN.fullmatch(cast(str, evidence.get("sha256", "")))
        ):
            raise ExternalTouchError(
                "external_touch_evidence_invalid", "file evidence schema is invalid"
            )
    intent_ids = [intent.get("intent_id") for intent in intents]
    if len(intent_ids) != len(set(cast(Sequence[object], intent_ids))):
        raise ExternalTouchError(
            "external_touch_duplicate_intent", "intent IDs must be globally unique"
        )
    known_refs = set(normalized_refs)
    if any(intent.get("ref") not in known_refs for intent in intents):
        raise ExternalTouchError(
            "external_touch_undeclared_evidence",
            "intent references a file outside the approved baseline",
        )
    for baseline_ref in refs:
        ref = cast(str, baseline_ref.get("ref", ""))
        chain = _intent_chain(
            baseline_ref,
            intents,
            ref,
            require_applied=require_applied,
            require_cleanup=require_cleanup,
        )
        for intent in chain:
            state = intent.get("state")
            expected_keys = {
                "schema_version",
                "run_id",
                "task_id",
                "intent_id",
                "sequence",
                "ref",
                "root_baseline",
                "parent",
                "candidate",
                "preserved_metadata",
                "broker_candidate_basename",
                "broker_candidate_path",
                "state",
                "after",
                "cleanup",
            }
            if state == "applied":
                expected_keys.add("replay_state")
            if set(intent) != expected_keys:
                raise ExternalTouchError(
                    "external_touch_evidence_invalid", "intent schema is not exact"
                )
            if (
                intent.get("schema_version") != SCHEMA_VERSION
                or intent.get("run_id") != expected_run_id
                or intent.get("task_id") != expected_task_id
            ):
                raise ExternalTouchError(
                    "external_touch_evidence_binding_invalid",
                    "intent identity differs from its baseline",
                )
            candidate = cast(Mapping[str, object], intent.get("candidate", {}))
            candidate_keys = {
                "path",
                "run_dir",
                "sha256",
                "size",
                "mode",
                "uid",
                "gid",
                "st_dev",
                "st_ino",
                "st_nlink",
            }
            if state != "staging" and set(candidate) != candidate_keys:
                raise ExternalTouchError(
                    "external_touch_evidence_invalid", "candidate schema is not exact"
                )
            if state == "staging" and set(candidate) != {
                "path",
                "run_dir",
                "sha256",
                "size",
            }:
                raise ExternalTouchError(
                    "external_touch_evidence_invalid",
                    "staging candidate schema is not exact",
                )
            if not SHA256_PATTERN.fullmatch(cast(str, candidate.get("sha256", ""))):
                raise ExternalTouchError(
                    "external_touch_evidence_invalid", "candidate hash is invalid"
                )
            parent = cast(Mapping[str, object], intent.get("parent", {}))
            metadata = cast(Mapping[str, object], intent.get("preserved_metadata", {}))
            if metadata != {
                field: parent.get(field) for field in ("file_type", "mode", "uid", "gid")
            }:
                raise ExternalTouchError(
                    "external_touch_evidence_invalid",
                    "preserved metadata differs from the immediate parent",
                )
            expected_broker_path = _broker_candidate_path(
                run_id=expected_run_id,
                task_id=expected_task_id,
                ref=ref,
                intent_id=cast(str, intent.get("intent_id", "")),
            )
            if (
                intent.get("broker_candidate_path") != str(expected_broker_path)
                or intent.get("broker_candidate_basename") != expected_broker_path.name
            ):
                raise ExternalTouchError(
                    "external_touch_evidence_binding_invalid",
                    "broker path differs from the intent identity",
                )
            if state == "applied":
                after = cast(Mapping[str, object], intent.get("after", {}))
                if set(after) != file_keys or not _candidate_matches_target(after, intent):
                    raise ExternalTouchError(
                        "external_touch_evidence_invalid",
                        "after evidence differs from candidate and parent metadata",
                    )
            elif intent.get("after") is not None or intent.get("cleanup") is not None:
                raise ExternalTouchError(
                    "external_touch_evidence_invalid",
                    "unapplied intent contains terminal evidence",
                )
            if check_cleanup_paths and state == "applied":
                _validate_cleanup_absent(intent)
    return {"state": "valid", "intent_count": len(intents)}


def compare_manifest(
    *,
    repo_root: Path,
    baseline: Mapping[str, object],
    intents: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Verify current external files against baseline-rooted applied chains."""

    refs = cast(Sequence[Mapping[str, object]], baseline.get("refs", []))
    known_refs = {cast(str, item.get("ref", "")) for item in refs}
    if any(intent.get("ref") not in known_refs for intent in intents):
        raise ExternalTouchError(
            "external_touch_undeclared_evidence",
            "intent references a file outside the baseline",
        )
    results: list[dict[str, object]] = []
    for baseline_ref in refs:
        ref = cast(str, baseline_ref.get("ref", ""))
        chain = _intent_chain(
            baseline_ref,
            intents,
            ref,
            require_applied=True,
            require_cleanup=True,
        )
        for intent in chain:
            _validate_cleanup_absent(intent)
        expected = cast(Mapping[str, object], chain[-1]["after"]) if chain else baseline_ref
        current = capture_file_evidence(repo_root, ref)
        if not _evidence_equal(current, expected):
            raise ExternalTouchError(
                "external_touch_baseline_drift",
                "current target does not match converged external evidence",
                exit_code=3,
            )
        results.append(
            {
                "ref": ref,
                "changed": current.get("sha256") != baseline_ref.get("sha256"),
                "applied_intent_count": len(chain),
                "before": dict(baseline_ref),
                "after": current,
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": baseline.get("run_id"),
        "task_id": baseline.get("task_id"),
        "design_sha256": baseline.get("design_sha256"),
        "plan_sha256": baseline.get("plan_sha256"),
        "refs": results,
    }


def _read_json_object(path: Path, field: str) -> dict[str, object]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExternalTouchError(
            "external_touch_json_invalid", f"{field} is not readable valid JSON"
        ) from exc
    if not isinstance(parsed, dict):
        raise ExternalTouchError(
            "external_touch_json_invalid", f"{field} must contain a JSON object"
        )
    return cast(dict[str, object], parsed)


def _read_json_list(path: Path, field: str) -> list[dict[str, object]]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExternalTouchError(
            "external_touch_json_invalid", f"{field} is not readable valid JSON"
        ) from exc
    if not isinstance(parsed, list) or not all(isinstance(item, dict) for item in parsed):
        raise ExternalTouchError(
            "external_touch_json_invalid", f"{field} must contain a JSON object array"
        )
    return cast(list[dict[str, object]], parsed)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    baseline_parser = subparsers.add_parser("baseline")
    baseline_parser.add_argument("--repo-root", type=Path, required=True)
    baseline_parser.add_argument("--run-id", required=True)
    baseline_parser.add_argument("--task-id", required=True)
    baseline_parser.add_argument("--design-sha256", required=True)
    baseline_parser.add_argument("--plan-sha256", required=True)
    baseline_parser.add_argument("--ref", action="append", required=True)

    declare_parser = subparsers.add_parser("declare")
    declare_parser.add_argument("--repo-root", type=Path, required=True)
    declare_parser.add_argument("--baseline-file", type=Path, required=True)
    declare_parser.add_argument("--intents-file", type=Path, required=True)
    declare_parser.add_argument("--ref", required=True)
    declare_parser.add_argument("--intent-id", required=True)
    declare_parser.add_argument("--run-dir", type=Path, required=True)
    declare_parser.add_argument("--source-file", type=Path, required=True)

    stage_declared_parser = subparsers.add_parser("stage-declared")
    stage_declared_parser.add_argument("--intent-file", type=Path, required=True)
    stage_declared_parser.add_argument("--source-file", type=Path, required=True)

    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--intent-file", type=Path, required=True)
    finalize_parser.add_argument("--staged-file", type=Path, required=True)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--repo-root", type=Path, required=True)
    apply_parser.add_argument("--intent-file", type=Path, required=True)

    apply_cleanup_parser = subparsers.add_parser("apply-and-cleanup")
    apply_cleanup_parser.add_argument("--repo-root", type=Path, required=True)
    apply_cleanup_parser.add_argument("--intent-file", type=Path, required=True)

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--repo-root", type=Path, required=True)
    compare_parser.add_argument("--baseline-file", type=Path, required=True)
    compare_parser.add_argument("--intents-file", type=Path, required=True)

    cleanup_parser = subparsers.add_parser("cleanup")
    cleanup_parser.add_argument("--intent-file", type=Path, required=True)
    cleanup_parser.add_argument("--allow-prepared", action="store_true")

    validate_parser = subparsers.add_parser("validate-state")
    validate_parser.add_argument("--baseline-file", type=Path, required=True)
    validate_parser.add_argument("--intents-file", type=Path, required=True)
    validate_parser.add_argument("--expected-task-id", required=True)
    validate_parser.add_argument("--expected-run-id", required=True)
    validate_parser.add_argument("--expected-design-sha256", required=True)
    validate_parser.add_argument("--expected-plan-sha256", required=True)
    validate_parser.add_argument("--expected-ref", action="append", required=True)
    validate_parser.add_argument("--require-applied", action="store_true")
    validate_parser.add_argument("--require-cleanup", action="store_true")
    validate_parser.add_argument("--check-cleanup-paths", action="store_true")

    durable_replace_parser = subparsers.add_parser("durable-replace")
    durable_replace_parser.add_argument("--staged-file", type=Path, required=True)
    durable_replace_parser.add_argument("--destination-file", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the helper CLI and emit deterministic JSON on stdout."""

    arguments = _build_parser().parse_args(argv)
    try:
        if arguments.operation == "baseline":
            result = capture_baseline(
                repo_root=arguments.repo_root,
                refs=arguments.ref,
                run_id=arguments.run_id,
                task_id=arguments.task_id,
                design_sha256=arguments.design_sha256,
                plan_sha256=arguments.plan_sha256,
            )
        elif arguments.operation == "declare":
            result = declare_intent(
                repo_root=arguments.repo_root,
                baseline=_read_json_object(arguments.baseline_file, "baseline-file"),
                intents=_read_json_list(arguments.intents_file, "intents-file"),
                ref=arguments.ref,
                intent_id=arguments.intent_id,
                run_dir=arguments.run_dir,
                source_file=arguments.source_file,
            )
        elif arguments.operation == "stage-declared":
            result = stage_declared_payload(
                intent=_read_json_object(arguments.intent_file, "intent-file"),
                source_file=arguments.source_file,
            )
        elif arguments.operation == "finalize":
            result = finalize_intent(
                intent=_read_json_object(arguments.intent_file, "intent-file"),
                staged_payload=_read_json_object(arguments.staged_file, "staged-file"),
            )
        elif arguments.operation == "apply":
            result = apply_intent(
                repo_root=arguments.repo_root,
                intent=_read_json_object(arguments.intent_file, "intent-file"),
            )
        elif arguments.operation == "apply-and-cleanup":
            result = apply_and_cleanup_intent(
                repo_root=arguments.repo_root,
                intent=_read_json_object(arguments.intent_file, "intent-file"),
            )
        elif arguments.operation == "compare":
            result = compare_manifest(
                repo_root=arguments.repo_root,
                baseline=_read_json_object(arguments.baseline_file, "baseline-file"),
                intents=_read_json_list(arguments.intents_file, "intents-file"),
            )
        elif arguments.operation == "cleanup":
            result = cleanup_intent(
                intent=_read_json_object(arguments.intent_file, "intent-file"),
                allow_prepared=arguments.allow_prepared,
            )
        elif arguments.operation == "validate-state":
            result = validate_evidence_state(
                baseline=_read_json_object(arguments.baseline_file, "baseline-file"),
                intents=_read_json_list(arguments.intents_file, "intents-file"),
                expected_task_id=arguments.expected_task_id,
                expected_run_id=arguments.expected_run_id,
                expected_design_sha256=arguments.expected_design_sha256,
                expected_plan_sha256=arguments.expected_plan_sha256,
                expected_refs=arguments.expected_ref,
                require_applied=arguments.require_applied,
                require_cleanup=arguments.require_cleanup,
                check_cleanup_paths=arguments.check_cleanup_paths,
            )
        elif arguments.operation == "durable-replace":
            result = durable_replace_file(
                staged_file=arguments.staged_file,
                destination_file=arguments.destination_file,
            )
        else:  # pragma: no cover - argparse owns operation validation
            raise ExternalTouchError(
                "external_touch_unknown_operation", "unsupported helper operation"
            )
    except ExternalTouchError as exc:
        print(f"external_touch_error:{exc.code}:{exc}", file=sys.stderr)
        return exc.exit_code

    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
