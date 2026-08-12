#!/usr/bin/env python3
"""Deterministic, lower-plane Herdr resource adapter for approved task envelopes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import stat
import subprocess
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Final, cast

JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject = dict[str, JsonValue]

SCHEMA_VERSION: Final = 1
LEASE_SCHEMA_VERSION: Final = 2
MAX_PROMPT_CHARS: Final = 200_000
MAX_COMMAND_OUTPUT_BYTES: Final = 64 * 1024
MAX_EVIDENCE_CHARS: Final = 8 * 1024
MAX_WAIT_SECONDS: Final = 15 * 60
MAX_COMMAND_TIMEOUT_SECONDS: Final = 15 * 60
MAX_COMMAND_ARG_CHARS: Final = 32 * 1024
MAX_SHELL_READINESS_SECONDS: Final = 30
SHELL_POLL_SECONDS: Final = 0.1
SHELL_STABLE_SECONDS: Final = 0.5
LEASE_LOCK_WAIT_SECONDS: Final = 2.0
MAX_AGENT_NAME_CHARS: Final = 32
ROLE_NAMES: Final = ("wolf", "owl", "fox", "otter", "badger", "lynx")
ROLE_RE: Final = re.compile(
    r"^(orchestrator|reviewer|explorer|worker)-[a-z0-9][a-z0-9_-]{0,31}$"
)
SAFE_TOKEN_RE: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}$")
SHA256_RE: Final = re.compile(r"^[0-9a-f]{64}$")
GIT_REVISION_RE: Final = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
SETTLED_STATES: Final = frozenset(
    {"idle", "done", "blocked", "unknown", "stalled", "timeout"}
)
OBSERVED_STATES: Final = frozenset({"busy", *SETTLED_STATES})
HERDR_AGENT_STATES: Final = frozenset({"idle", "working", "done", "blocked", "unknown"})
INTERACTIVE_SHELL_NAMES: Final = frozenset(
    {"sh", "bash", "zsh", "fish", "ksh", "dash", "tcsh", "csh", "nu"}
)
FORBIDDEN_KEY_RE: Final = re.compile(
    r"(?:secret|token|password|api[_-]?key|prompt)", re.IGNORECASE
)
REDACTION_RE: Final = re.compile(
    r"(?i)(?:bearer\s+|token\s*[=:]?\s*|password\s*[=:]\s*|api[_-]?key\s*[=:]\s*)\S+"
)
COMMAND_SENSITIVE_RE: Final = re.compile(
    r"(?i)(?:bearer\s+|token\s*[=:]|password\s*[=:]|api[_-]?key\s*[=:])"
)
COMMAND_SHELL_META_RE: Final = re.compile(r"[`$;|&<>\n\r\x00]")
ALLOWED_EFFORTS: Final = {"low", "medium", "high", "xhigh"}
EXPLORER_EFFORTS: Final = {"low", "medium"}
MODEL_PATTERNS: Final = {
    "codex": re.compile(r"^gpt-5\.6(?:-(?:sol|terra|luna))?$"),
    "grok": re.compile(r"^(?:grok-4\.5|gpt-5\.6(?:-(?:sol|terra|luna))?)$"),
}
NATIVE_ENDPOINTS: Final = {
    "codex": ("native://openai", "native-login/codex"),
    "grok": ("native://grok", "native-login/grok"),
}
SENSITIVE_ENV_NAME_RE: Final = re.compile(
    r"(?:TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY|CREDENTIAL|COOKIE|AUTH|"
    r"^AWS_|^AZURE_|^GOOGLE_|^GITHUB_|^GITLAB_|^OPENAI_|^XAI_|^ANTHROPIC_)",
    re.IGNORECASE,
)
SENSITIVE_ENV_NAMES: Final = frozenset(
    {
        "SSH_AUTH_SOCK",
        "GPG_AGENT_INFO",
        "AWS_PROFILE",
        "AWS_CONFIG_FILE",
        "AWS_SHARED_CREDENTIALS_FILE",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "KUBECONFIG",
    }
)


class AdapterError(Exception):
    """An expected typed adapter stop that must not be repaired by the adapter."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def as_object(value: JsonValue, label: str) -> JsonObject:
    if not isinstance(value, dict):
        raise AdapterError("controller_binding_invalid", f"{label} must be an object")
    return value


def as_string(value: JsonValue, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise AdapterError(
            "controller_binding_invalid", f"{label} must be a non-empty string"
        )
    if "\x00" in value or any(ord(character) < 32 for character in value):
        raise AdapterError(
            "controller_binding_invalid", f"{label} contains control characters"
        )
    return value


def value_at(obj: JsonObject, key: str, label: str | None = None) -> JsonValue:
    if key not in obj:
        raise AdapterError("controller_binding_invalid", f"missing {label or key}")
    return obj[key]


def string_at(obj: JsonObject, key: str, label: str | None = None) -> str:
    return as_string(value_at(obj, key, label), label or key)


def list_at(obj: JsonObject, key: str, label: str | None = None) -> list[JsonValue]:
    value = value_at(obj, key, label)
    if not isinstance(value, list):
        raise AdapterError(
            "controller_binding_invalid", f"{label or key} must be a list"
        )
    return value


def canonical(path: Path) -> Path:
    try:
        return path.resolve(strict=True)
    except OSError as exc:
        raise AdapterError(
            "controller_binding_invalid", f"path cannot be resolved: {path}"
        ) from exc


def ensure_regular_file(path: Path, label: str) -> Path:
    supplied = Path(path)
    if supplied.is_symlink():
        raise AdapterError(
            "controller_binding_invalid", f"{label} must not be a symlink"
        )
    try:
        mode = stat.S_IMODE(supplied.stat().st_mode)
    except OSError as exc:
        raise AdapterError(
            "controller_binding_invalid", f"{label} cannot be inspected"
        ) from exc
    if not supplied.is_file() or mode != 0o600:
        raise AdapterError(
            "controller_binding_invalid",
            f"{label} must be a regular owner-only 0600 file",
        )
    resolved = canonical(supplied)
    if resolved.is_symlink():
        raise AdapterError(
            "controller_binding_invalid", f"{label} must not be a symlink"
        )
    return resolved


def ensure_directory(path: Path, label: str) -> Path:
    resolved = canonical(path)
    if not resolved.is_dir() or resolved.is_symlink():
        raise AdapterError(
            "controller_binding_invalid", f"{label} must be a regular directory"
        )
    return resolved


def parse_json_file(path: Path, label: str) -> JsonObject:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AdapterError(
            "controller_binding_invalid", f"{label} is not valid JSON"
        ) from exc
    return as_object(cast(JsonValue, value), label)


def walk_forbidden_keys(value: JsonValue, path: str = "") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if FORBIDDEN_KEY_RE.search(key):
                raise AdapterError(
                    "controller_binding_invalid",
                    f"forbidden field in envelope: {path}/{key}",
                )
            walk_forbidden_keys(child, f"{path}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_forbidden_keys(child, f"{path}/{index}")


def require_sha256(value: str, label: str) -> None:
    if not SHA256_RE.fullmatch(value):
        raise AdapterError(
            "controller_binding_stale", f"{label} must be a lowercase SHA-256 digest"
        )


def git_common_directory(path: Path) -> Path:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--git-common-dir"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise AdapterError(
            "controller_binding_repository_mismatch",
            f"Git common directory unavailable: {path}",
        ) from exc
    raw = completed.stdout.strip()
    common = Path(raw)
    if not common.is_absolute():
        common = path / common
    return canonical(common)


def git_revision(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise AdapterError(
            "controller_binding_repository_mismatch", "repository revision unavailable"
        ) from exc
    revision = completed.stdout.strip()
    if not GIT_REVISION_RE.fullmatch(revision):
        raise AdapterError(
            "controller_binding_repository_mismatch",
            "repository revision is not a commit SHA",
        )
    return revision


def git_dir(path: Path) -> Path:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise AdapterError(
            "controller_binding_repository_mismatch",
            "checkout Git directory unavailable",
        ) from exc
    git_path = Path(completed.stdout.strip())
    if not git_path.is_absolute():
        git_path = path / git_path
    return canonical(git_path)


def digest_json(value: JsonValue) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def git_common_dir_key(path: Path) -> str:
    return hashlib.sha256(str(path).encode()).hexdigest()


def positive_int(value: JsonValue, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise AdapterError("controller_binding_batch_invalid", f"{label} must be positive")
    return value


def string_list(value: JsonValue, label: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item for item in value
    ):
        raise AdapterError("controller_binding_batch_invalid", f"{label} must be a non-empty string list")
    result = cast(list[str], value)
    if len(set(result)) != len(result):
        raise AdapterError("controller_binding_batch_invalid", f"{label} contains duplicates")
    return result


def batch_provenance(envelope: JsonObject, task: JsonObject) -> JsonObject:
    """Return and validate the runner-issued batch projection.

    HBU-010 emits the projection under both ``batch_provenance`` and
    ``provenance.batch``.  Keeping the adapter tolerant of either location makes
    restart validation explicit while still rejecting a missing projection for a
    named parallel group.
    """
    group = task.get("parallel_group", "none")
    if not isinstance(group, str) or not group:
        raise AdapterError("controller_binding_batch_invalid", "task parallel_group is malformed")
    supplied = envelope.get("batch_provenance")
    nested_supplied: JsonValue | None = None
    provenance_value = envelope.get("provenance")
    if isinstance(provenance_value, dict):
        nested_supplied = provenance_value.get("batch")
    if supplied is None:
        supplied = nested_supplied
    elif nested_supplied is not None and digest_json(cast(JsonValue, supplied)) != digest_json(nested_supplied):
        raise AdapterError(
            "controller_binding_batch_forged",
            "top-level and provenance batch projections differ",
        )
    if supplied is None:
        if group != "none":
            raise AdapterError(
                "controller_binding_batch_required",
                "named parallel task requires controller-issued batch provenance",
            )
        return {
            "batch_id": "none",
            "parallel_group": "none",
            "parallel_policy": "serial",
            "batch_task_ids": [string_at(task, "task_id")],
            "planned_task_ids": [string_at(task, "task_id")],
            "planned_width": 1,
            "plan_max_parallelism": 1,
            "ready_width": 1,
            "ready_task_ids": [string_at(task, "task_id")],
            "ready_frontier_task_ids": [string_at(task, "task_id")],
            "selected_task_ids": [string_at(task, "task_id")],
            "runtime_capacity": 1,
            "actor_capacity": 1,
            "effective_width": 1,
            "limiting_factors": ["serial"],
            "serial_fallback_reason": None,
            "outcome": "serial-fallback",
            "stop_reason": None,
        }
    value = as_object(cast(JsonValue, supplied), "batch provenance")
    required_lists = {
        "batch_task_ids": value.get("batch_task_ids", value.get("task_ids")),
        "planned_task_ids": value.get("planned_task_ids"),
        "ready_task_ids": value.get("ready_task_ids", value.get("ready_frontier_task_ids")),
        "selected_task_ids": value.get("selected_task_ids"),
    }
    result: JsonObject = {}
    for key, candidate in required_lists.items():
        if candidate is None:
            raise AdapterError("controller_binding_batch_invalid", f"batch provenance missing {key}")
        result[key] = string_list(candidate, f"batch provenance {key}")
    for key in (
        "batch_id",
        "parallel_group",
        "parallel_policy",
        "outcome",
    ):
        result[key] = string_at(value, key, f"batch provenance {key}")
    result["stop_reason"] = value.get("stop_reason")
    result["serial_fallback_reason"] = value.get("serial_fallback_reason")
    result["limiting_factors"] = value.get("limiting_factors", [])
    if not isinstance(result["limiting_factors"], list) or not all(
        isinstance(item, str) for item in cast(list[JsonValue], result["limiting_factors"])
    ):
        raise AdapterError("controller_binding_batch_invalid", "batch limiting_factors is malformed")
    for key in (
        "planned_width",
        "plan_max_parallelism",
        "ready_width",
        "runtime_capacity",
        "actor_capacity",
        "effective_width",
    ):
        result[key] = positive_int(value_at(value, key, f"batch provenance {key}"), f"batch provenance {key}")
    if result["batch_id"] != group or result["parallel_group"] != group:
        raise AdapterError("controller_binding_batch_mismatch", "batch identity does not match task group")
    selected = cast(list[str], result["selected_task_ids"])
    if len(selected) > cast(int, result["effective_width"]):
        raise AdapterError("controller_binding_batch_width_exhausted", "selected batch exceeds effective width")
    task_id = string_at(task, "task_id")
    if task_id not in selected:
        raise AdapterError("controller_binding_batch_unselected", f"task is not selected for batch: {task_id}")
    if cast(list[str], result["batch_task_ids"]) != cast(list[str], result["planned_task_ids"]):
        raise AdapterError("controller_binding_batch_invalid", "planned and batch task membership differ")
    return result


def validate_lease_file(
    path: Path,
    repository: Path,
    common_dir: Path,
    *,
    allowed_states: frozenset[str],
    expected_identity: JsonObject | None = None,
) -> JsonObject:
    """Validate a complete owner-only lease and, when supplied, its run identity."""
    if (
        path.is_symlink()
        or not path.is_file()
        or stat.S_IMODE(path.stat().st_mode) != 0o600
    ):
        raise AdapterError(
            "herdr_execution_conflict",
            "existing lease is not an owner-only regular file",
        )
    try:
        lease = parse_json_file(path, "existing lease")
        if value_at(lease, "schema_version") != LEASE_SCHEMA_VERSION:
            raise ValueError("schema")
        if string_at(lease, "artifact_kind") != "herdr-controller-lease":
            raise ValueError("kind")
        if string_at(lease, "lease_state") not in allowed_states:
            raise ValueError("state")
        if string_at(lease, "repository") != str(repository):
            raise ValueError("repository")
        if string_at(lease, "git_common_dir_sha256") != git_common_dir_key(common_dir):
            raise ValueError("git common directory")
        require_sha256(string_at(lease, "plan_sha256"), "lease plan_sha256")
        string_at(lease, "batch_id")
        string_at(lease, "workspace_id")
        string_at(lease, "controller_id")
        effective_width = positive_int(value_at(lease, "effective_width"), "lease effective_width")
        selected_task_ids = string_list(value_at(lease, "selected_task_ids"), "lease selected_task_ids")
        if len(selected_task_ids) > effective_width:
            raise ValueError("selected width")
        lease_locks = lease.get("resource_locks", [])
        if not isinstance(lease_locks, list) or any(not isinstance(lock, str) for lock in lease_locks):
            raise ValueError("lease resource locks")
        if expected_identity is not None and lease_locks != expected_identity.get("resource_locks", lease_locks):
            raise ValueError("lease resource locks mismatch")
        members = value_at(lease, "members")
        if not isinstance(members, list):
            raise TypeError("members")
        for member in members:
            if not isinstance(member, dict):
                raise TypeError("member")
            string_at(member, "member_id")
            string_at(member, "run_id")
            require_sha256(string_at(member, "run_nonce_sha256"), "member run_nonce_sha256")
            string_at(member, "task_id")
            positive_int(member.get("attempt"), "member attempt")
            if member.get("lease_state") not in {"active", "cleanup-pending", "released"}:
                raise ValueError("member state")
            if member.get("task_id") not in selected_task_ids:
                raise ValueError("member selection")
            member_locks = member.get("resource_locks", [])
            if not isinstance(member_locks, list) or any(not isinstance(lock, str) for lock in member_locks):
                raise ValueError("member resource locks")
            if (
                member.get("controller_id") != lease.get("controller_id")
                or member.get("workspace_id") != lease.get("workspace_id")
                or member.get("batch_id") != lease.get("batch_id")
            ):
                raise ValueError("member scope")
        if expected_identity is not None:
            for key, expected in expected_identity.items():
                if lease.get(key) != expected:
                    raise ValueError(f"identity:{key}")
    except (AdapterError, ValueError, TypeError) as exc:
        raise AdapterError(
            "herdr_execution_conflict",
            "existing lease is malformed, stale, active, cleanup-pending, or mismatched",
        ) from exc
    return lease


def derive_agent_name(role: str, run_id: str, task_id: str, attempt: int) -> str:
    if role not in {"reviewer", "explorer", "worker"}:
        raise AdapterError(
            "controller_binding_invalid", f"unsupported delegated role: {role}"
        )
    digest = hashlib.sha256(f"{run_id}:{task_id}:{attempt}".encode()).hexdigest()
    animal = ROLE_NAMES[int(digest[:2], 16) % len(ROLE_NAMES)]
    task_fragment = re.sub(r"[^a-z0-9]+", "-", task_id.lower()).strip("-")[:6] or "task"
    suffix = f"{digest[2:4]}-t{task_fragment}-a{attempt}"
    name = f"{role}-{animal}-{suffix}"[:MAX_AGENT_NAME_CHARS].rstrip("-")
    if not ROLE_RE.fullmatch(name):
        raise AdapterError(
            "controller_binding_invalid", "derived agent name is not valid"
        )
    return name


def model_policy_evidence(
    role: str, physical: JsonObject, controller: JsonObject
) -> JsonObject:
    policy = string_at(controller, "model_policy")
    if policy not in {"semantic-routing", "inherit-main", "runtime-default"}:
        raise AdapterError(
            "controller_binding_invalid", f"unsupported model policy: {policy}"
        )
    kind = string_at(physical, "agent_kind")
    model = string_at(physical, "model")
    effort = string_at(physical, "reasoning_effort").lower()
    if not MODEL_PATTERNS[kind].fullmatch(model):
        raise AdapterError(
            "delegated_capability_unavailable",
            f"unsupported {kind} model for the pinned adapter profile",
        )
    if effort not in ALLOWED_EFFORTS:
        raise AdapterError(
            "delegated_capability_unavailable",
            f"unsupported {kind} reasoning effort: {effort}",
        )
    if role == "reviewer":
        if kind != "codex" or model not in {"gpt-5.6", "gpt-5.6-sol"}:
            raise AdapterError(
                "delegated_capability_unavailable",
                "reviewer requires the pinned Codex SOL profile",
            )
        if effort not in {"high", "xhigh"}:
            raise AdapterError(
                "delegated_capability_unavailable",
                "reviewer requires high or xhigh reasoning",
            )
    if role != "explorer":
        return {"status": "not-applicable", "model_policy": policy}
    if effort not in EXPLORER_EFFORTS:
        raise AdapterError(
            "delegated_capability_unavailable",
            "explorer reasoning is absolutely bounded to low or medium",
        )
    if policy == "semantic-routing":
        if kind == "codex" and model != "gpt-5.6-luna":
            raise AdapterError(
                "delegated_capability_unavailable",
                "semantic-routing Codex explorer requires gpt-5.6-luna",
            )
        if kind == "grok" and model != "grok-4.5":
            raise AdapterError(
                "delegated_capability_unavailable",
                "semantic-routing Grok explorer requires grok-4.5",
            )
        return {
            "status": "absolute-low-cost",
            "model_policy": policy,
            "reasoning_effort": effort,
            "default_effort": "low",
            "max_effort": "medium",
        }
    return {
        "status": "absolute-low-cost",
        "model_policy": policy,
        "reasoning_effort": effort,
        "default_effort": "low",
        "max_effort": "medium",
    }


def native_agent_profile(
    role: str,
    physical: JsonObject,
    controller: JsonObject,
    checkout: Path,
) -> JsonObject:
    """Validate one pinned CLI capability matrix and return exact native argv."""
    kind = string_at(physical, "agent_kind")
    model = string_at(physical, "model")
    effort = string_at(physical, "reasoning_effort").lower()
    permission = string_at(physical, "permission_mode")
    sandbox = string_at(physical, "sandbox_mode")
    endpoint, credential_ref = NATIVE_ENDPOINTS[kind]
    if (
        string_at(physical, "control_plane_endpoint") != endpoint
        or string_at(physical, "credential_ref") != credential_ref
    ):
        raise AdapterError(
            "delegated_capability_unavailable",
            f"{kind} requires its native-login control-plane profile",
        )
    policy_evidence = model_policy_evidence(role, physical, controller)
    capability = string_at(physical, "capability_profile")
    if capability == "delegated-read-only":
        if permission != "never" or sandbox != "read-only":
            raise AdapterError(
                "controller_binding_capability_mismatch",
                "read-only profile requires never/read-only",
            )
    elif permission not in {"never", "always-approve"} or sandbox != "workspace-write":
        raise AdapterError(
            "controller_binding_capability_mismatch",
            "writer profile requires never or always-approve with workspace-write",
        )

    if kind == "codex":
        approval = "never" if permission == "always-approve" else permission
        native_args = [
            "--model",
            model,
            "-c",
            f'model_reasoning_effort="{effort}"',
            "-c",
            "agents.enabled=false",
            "-c",
            'shell_environment_policy.inherit="core"',
            "-c",
            "shell_environment_policy.ignore_default_excludes=false",
            "-c",
            "sandbox_workspace_write.network_access=false",
            "--ask-for-approval",
            approval,
            "--sandbox",
            sandbox,
            "--no-alt-screen",
            "-C",
            str(checkout),
        ]
        profile_id = f"codex-{capability}-v1"
    else:
        grok_permission = {
            "never": "plan" if capability == "delegated-read-only" else "dontAsk",
            "always-approve": "acceptEdits",
        }[permission]
        tools = (
            "Read,Grep,Glob"
            if capability == "delegated-read-only"
            else "Bash,Read,Write,Edit,Grep,Glob"
        )
        native_args = [
            "--model",
            model,
            "--reasoning-effort",
            effort,
            "--permission-mode",
            grok_permission,
            "--sandbox",
            sandbox,
            "--tools",
            tools,
            "--disable-web-search",
            "--no-subagents",
            "--no-memory",
            "--no-alt-screen",
            "--cwd",
            str(checkout),
        ]
        profile_id = f"grok-{capability}-v1"
    return {
        "profile_id": profile_id,
        "native_args": cast(list[JsonValue], native_args),
        "model_policy_evidence": policy_evidence,
        "environment_policy": "blank-sensitive-native-env-v1",
    }


def role_and_capability(
    envelope: JsonObject,
) -> tuple[str, JsonObject, JsonObject, JsonObject, JsonObject, JsonObject]:
    task = as_object(value_at(envelope, "task"), "task")
    physical = as_object(value_at(envelope, "physical_binding"), "physical_binding")
    controller = as_object(value_at(envelope, "controller"), "controller")
    provenance = as_object(value_at(envelope, "provenance"), "provenance")
    authority = as_object(value_at(envelope, "authority"), "authority")
    binding_kind = controller.get("binding_kind", "delegated-task")
    if binding_kind == "command-job":
        validate_command_job_shape(envelope, task, physical)
        denied = list_at(authority, "denied_capabilities")
        required_denied = {
            "select-task",
            "mutate-task-ledger",
            "converge-task",
            "invoke-review",
            "adjudicate-findings",
            "repair-implementation",
            "derive-lifecycle-tail",
            "claim-task-success",
        }
        if not required_denied.issubset({item for item in denied if isinstance(item, str)}):
            raise AdapterError(
                "controller_binding_authority_denied",
                "command-job envelope does not deny lifecycle and oracle authority",
            )
        return "command-job", task, physical, controller, provenance, authority
    if binding_kind not in {"delegated-task", "bounded-review"}:
        raise AdapterError("controller_binding_invalid", f"unsupported binding kind: {binding_kind}")
    task_id = string_at(task, "task_id")
    execution_profile = string_at(task, "execution_profile")
    reasoning_profile = string_at(task, "reasoning_profile")
    isolation = string_at(task, "isolation")
    touch_set = list_at(task, "touch_set")
    if not all(isinstance(item, str) for item in touch_set):
        raise AdapterError(
            "controller_binding_invalid", "task touch_set must contain strings"
        )
    declared_role = task.get("runtime_role")
    if declared_role == "reviewer":
        role = "reviewer"
    elif (
        not touch_set
        and execution_profile == "fast"
        and reasoning_profile == "light"
        and isolation == "shared-read-only"
    ):
        role = "explorer"
    else:
        role = "worker"
    attempt = value_at(task, "attempt")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
        raise AdapterError(
            "controller_binding_invalid", "task attempt must be a positive integer"
        )
    if string_at(physical, "terminal_backend") != "herdr":
        raise AdapterError(
            "controller_binding_invalid", "terminal backend must be herdr"
        )
    agent_kind = string_at(physical, "agent_kind")
    if agent_kind not in {"codex", "grok"}:
        raise AdapterError(
            "controller_binding_invalid", f"unsupported agent kind: {agent_kind}"
        )
    capability = string_at(physical, "capability_profile")
    sandbox = string_at(physical, "sandbox_mode")
    permission = string_at(physical, "permission_mode")
    model_policy = string_at(controller, "model_policy")
    if model_policy not in {"semantic-routing", "inherit-main", "runtime-default"}:
        raise AdapterError(
            "controller_binding_invalid",
            f"unsupported model policy: {model_policy}",
        )
    if capability not in {"delegated-read-only", "delegated-local-writer"}:
        raise AdapterError(
            "delegated_capability_unavailable",
            f"unsupported capability profile: {capability}",
        )
    if role == "reviewer" and touch_set:
        raise AdapterError(
            "controller_binding_capability_mismatch",
            "reviewer cannot have writable refs",
        )
    if touch_set:
        if capability != "delegated-local-writer" or sandbox != "workspace-write":
            raise AdapterError(
                "controller_binding_capability_mismatch",
                "writer requires isolated workspace-write capability",
            )
        if isolation != "isolated-worktree":
            raise AdapterError(
                "controller_binding_capability_mismatch",
                "writer task requires isolated-worktree",
            )
    elif capability != "delegated-read-only" or sandbox != "read-only":
        raise AdapterError(
            "controller_binding_capability_mismatch",
            "read-only task requires read-only capability",
        )
    if permission not in {"never", "always-approve"}:
        raise AdapterError(
            "controller_binding_invalid", f"unsupported permission mode: {permission}"
        )
    if permission == "always-approve" and capability != "delegated-local-writer":
        raise AdapterError(
            "delegated_capability_unavailable", "always-approve is writer-only"
        )
    if not ROLE_RE.fullmatch(string_at(physical, "agent_name")):
        raise AdapterError(
            "controller_binding_invalid",
            "agent name must be role-first and 32 characters or fewer",
        )
    expected_agent_name = derive_agent_name(
        role, string_at(controller, "run_id"), task_id, attempt
    )
    if string_at(physical, "agent_name") != expected_agent_name:
        raise AdapterError(
            "controller_binding_invalid",
            "agent name does not match deterministic task projection",
        )
    if (
        string_at(task, "executor_mode") != "subagent"
        or string_at(task, "delegation_policy") == "forbidden"
    ):
        raise AdapterError(
            "controller_binding_authority_denied", f"task is not delegated: {task_id}"
        )
    denied = list_at(authority, "denied_capabilities")
    required_denied = {
        "select-task",
        "mutate-task-ledger",
        "converge-task",
        "invoke-review",
        "adjudicate-findings",
        "repair-implementation",
        "derive-lifecycle-tail",
    }
    if not required_denied.issubset({item for item in denied if isinstance(item, str)}):
        raise AdapterError(
            "controller_binding_authority_denied",
            "envelope does not deny lifecycle authority",
        )
    return role, task, physical, controller, provenance, authority


def validate_envelope(path: Path) -> tuple[JsonObject, str, Path, Path]:
    envelope_path = ensure_regular_file(path, "envelope")
    envelope = parse_json_file(envelope_path, "envelope")
    walk_forbidden_keys(cast(JsonValue, envelope))
    if (
        value_at(envelope, "schema_version") != SCHEMA_VERSION
        or string_at(envelope, "artifact_kind") != "controller-binding-envelope"
    ):
        raise AdapterError(
            "controller_binding_required",
            "schema-versioned controller binding envelope required",
        )
    role, task, physical, controller, provenance, _ = role_and_capability(envelope)
    for key in ("controller_id", "run_id", "run_nonce"):
        string_at(controller, key)
    run_id = string_at(controller, "run_id")
    run_nonce = string_at(controller, "run_nonce")
    if (
        len(run_id) > 128
        or len(run_nonce) > 256
        or not SAFE_TOKEN_RE.fullmatch(run_id)
        or not SAFE_TOKEN_RE.fullmatch(run_nonce)
    ):
        raise AdapterError(
            "controller_binding_invalid", "run ID or nonce is not a bounded safe token"
        )
    for key in (
        "canonical_repository",
        "repository_revision",
        "plan_sha256",
        "ledger_sha256",
    ):
        string_at(provenance, key)
    require_sha256(string_at(provenance, "plan_sha256"), "plan_sha256")
    require_sha256(string_at(provenance, "ledger_sha256"), "ledger_sha256")
    repo = ensure_directory(
        Path(string_at(provenance, "canonical_repository")), "canonical repository"
    )
    if repo != canonical(Path(string_at(provenance, "canonical_repository"))):
        raise AdapterError(
            "controller_binding_repository_mismatch", "repository path is not canonical"
        )
    expected_envelope_path = repo / ".herdr-runs" / run_id / "controller-binding.json"
    if envelope_path != expected_envelope_path:
        raise AdapterError(
            "controller_binding_invalid",
            "envelope must be the canonical run-owned controller-binding.json",
        )
    checkout = ensure_directory(Path(string_at(physical, "checkout_path")), "checkout")
    if git_common_directory(repo) != git_common_directory(checkout):
        raise AdapterError(
            "controller_binding_repository_mismatch",
            "checkout belongs to another repository",
        )
    if git_revision(repo) != string_at(provenance, "repository_revision"):
        raise AdapterError(
            "controller_binding_stale", "repository revision differs from the envelope"
        )
    if git_revision(checkout) != string_at(provenance, "repository_revision"):
        raise AdapterError(
            "controller_binding_stale", "checkout revision differs from the envelope"
        )
    write_refs = [
        item
        for item in list_at(task, "touch_set")
        if isinstance(item, str) and item not in {"", "none"}
    ]
    if role != "command-job" and write_refs and git_dir(checkout) == git_common_directory(checkout):
        raise AdapterError(
            "controller_binding_capability_mismatch",
            "writer checkout must be an isolated worktree",
        )
    if string_at(task, "status") != "ready":
        raise AdapterError(
            "controller_binding_task_not_ready", "selected task is not ready"
        )
    expected_cwd = ensure_directory(checkout, "checkout")
    if role == "command-job":
        job = validate_command_job_shape(envelope, task, physical)
        command_cwd = ensure_directory(Path(string_at(job, "cwd")), "command cwd")
        if command_cwd != expected_cwd:
            raise AdapterError(
                "controller_binding_cwd_mismatch",
                "command cwd must exactly match the controller-bound checkout",
            )
        if command_cwd != canonical(Path(string_at(physical, "checkout_path"))):
            raise AdapterError(
                "controller_binding_cwd_mismatch",
                "command cwd is not the declared checkout",
            )
    return envelope, run_id, repo, expected_cwd


def caller_context(physical: JsonObject) -> dict[str, str]:
    names = {
        "workspace_id": "HERDR_WORKSPACE_ID",
        "tab_id": "HERDR_TAB_ID",
        "pane_id": "HERDR_PANE_ID",
    }
    context: dict[str, str] = {}
    for field, environment_name in names.items():
        expected = string_at(physical, field)
        actual = os.environ.get(environment_name)
        if actual is None or actual != expected:
            raise AdapterError(
                "caller_context_mismatch",
                f"{environment_name} does not match binding envelope",
            )
        context[field] = actual
    return context


def executable_path(argument: str | None) -> Path:
    if not argument:
        raise AdapterError(
            "herdr_executable_required",
            "caller-supplied --herdr-executable is required",
        )
    candidate = Path(argument)
    if not candidate.is_absolute():
        raise AdapterError(
            "herdr_executable_invalid",
            "Herdr executable must be an explicit absolute path",
        )
    if candidate.is_symlink():
        raise AdapterError(
            "herdr_executable_invalid",
            "Herdr executable must be the real binary, not a shim or symlink",
        )
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise AdapterError(
            "herdr_executable_invalid", "Herdr executable cannot be resolved"
        ) from exc
    mode = resolved.stat().st_mode
    if not stat.S_ISREG(mode) or not os.access(resolved, os.X_OK):
        raise AdapterError(
            "herdr_executable_invalid",
            "Herdr executable must be an executable regular file",
        )
    return resolved


def command_failure(
    completed: subprocess.CompletedProcess[bytes], argv: list[str]
) -> AdapterError:
    stderr = completed.stderr.decode("utf-8", errors="replace")
    bounded = safe_preview(stderr.strip())
    lowered = bounded.lower()
    if "agent_pane_busy" in lowered or "pane_busy" in lowered:
        return AdapterError("agent_pane_busy", "allocated pane is already occupied by an agent")
    if "agent_prompt_stalled" in lowered:
        return AdapterError("agent_prompt_stalled", "Herdr prompt did not change state")
    if "timeout" in lowered or "timed out" in lowered:
        return AdapterError("herdr_command_timeout", f"Herdr {argv[0]} timed out")
    return AdapterError(
        "herdr_command_failed",
        f"Herdr {argv[0]} failed" + (f": {bounded}" if bounded else ""),
    )


def fixture_safe_command(
    executable: Path, argv: list[str], *, timeout_seconds: int = 10
) -> JsonObject:
    if not argv:
        raise AdapterError("herdr_protocol_invalid", "empty Herdr command")
    try:
        completed = subprocess.run(
            [str(executable), *argv],
            check=False,
            capture_output=True,
            text=False,
            timeout=timeout_seconds,
            env={**os.environ, "HERDR_ADAPTER_NO_LIVE_CONTEXT": "1"},
        )
    except subprocess.TimeoutExpired as exc:
        raise AdapterError(
            "herdr_command_timeout", f"Herdr command timed out: {argv[0]}"
        ) from exc
    except OSError as exc:
        raise AdapterError(
            "herdr_unavailable", "caller-supplied Herdr executable could not run"
        ) from exc
    if (
        len(completed.stdout) > MAX_COMMAND_OUTPUT_BYTES
        or len(completed.stderr) > MAX_COMMAND_OUTPUT_BYTES
    ):
        raise AdapterError(
            "herdr_output_bounded", "Herdr output exceeded bounded limit"
        )
    if completed.returncode != 0:
        raise command_failure(completed, argv)
    try:
        decoded = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdapterError(
            "herdr_protocol_invalid", "Herdr executable did not return JSON"
        ) from exc
    response = as_object(cast(JsonValue, decoded), "Herdr response")
    if "error" in response:
        raise AdapterError(
            "herdr_command_failed", "Herdr returned a bounded protocol error"
        )
    return response


def fixture_safe_text_command(
    executable: Path, argv: list[str], *, timeout_seconds: int = 10
) -> str:
    if not argv:
        raise AdapterError("herdr_protocol_invalid", "empty Herdr command")
    try:
        completed = subprocess.run(
            [str(executable), *argv],
            check=False,
            capture_output=True,
            text=False,
            timeout=timeout_seconds,
            env={**os.environ, "HERDR_ADAPTER_NO_LIVE_CONTEXT": "1"},
        )
    except subprocess.TimeoutExpired as exc:
        raise AdapterError(
            "herdr_command_timeout", f"Herdr command timed out: {argv[0]}"
        ) from exc
    except OSError as exc:
        raise AdapterError(
            "herdr_unavailable", "caller-supplied Herdr executable could not run"
        ) from exc
    if (
        len(completed.stdout) > MAX_COMMAND_OUTPUT_BYTES
        or len(completed.stderr) > MAX_COMMAND_OUTPUT_BYTES
    ):
        raise AdapterError(
            "herdr_output_bounded", "Herdr output exceeded bounded limit"
        )
    if completed.returncode != 0:
        raise command_failure(completed, argv)
    try:
        return completed.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AdapterError(
            "herdr_protocol_invalid", "Herdr text output is not UTF-8"
        ) from exc


def result_object(response: JsonObject) -> JsonObject:
    result = response.get("result", response)
    return as_object(result, "Herdr result")


def result_string(response: JsonObject, key: str, label: str | None = None) -> str:
    return as_string(value_at(result_object(response), key, label), label or key)


def result_entity(response: JsonObject, key: str) -> JsonObject:
    return as_object(value_at(result_object(response), key, f"Herdr result {key}"), key)


def result_state(response: JsonObject) -> str:
    result = result_object(response)
    candidate: JsonObject = result
    for key in ("agent", "pane", "tab"):
        nested = result.get(key)
        if isinstance(nested, dict):
            candidate = nested
            break
    value = candidate.get(
        "agent_status", candidate.get("state", result.get("state", "unknown"))
    )
    if not isinstance(value, str) or value not in HERDR_AGENT_STATES:
        return "unknown"
    return "busy" if value == "working" else value


def result_panes(response: JsonObject) -> list[JsonObject]:
    values = result_object(response).get("panes", [])
    if not isinstance(values, list):
        return []
    return [item for item in values if isinstance(item, dict)]


def result_agent_session(response: JsonObject) -> str | None:
    agent = result_entity(response, "agent")
    session = agent.get("agent_session")
    if not isinstance(session, dict):
        return None
    value = session.get("value")
    return value if isinstance(value, str) and value else None


def safe_preview(value: str) -> str:
    redacted = REDACTION_RE.sub("[REDACTED_SECRET]", value)
    return redacted[:MAX_EVIDENCE_CHARS]


def bounded_utf8_preview(value: str, max_bytes: int) -> str:
    """Redact first, then return a valid UTF-8 prefix within an exact byte bound."""
    data = safe_preview(value).encode("utf-8")[:max_bytes]
    while data:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as exc:
            data = data[: exc.start]
    return ""


def command_job_binding(envelope: JsonObject) -> bool:
    controller = envelope.get("controller")
    return isinstance(controller, dict) and controller.get("binding_kind") == "command-job"


def validate_command_job_shape(
    envelope: JsonObject,
    task: JsonObject,
    physical: JsonObject,
) -> JsonObject:
    """Validate an ordinary controller-issued command without granting agent authority."""
    allowed_physical = {
        "checkout_path",
        "pane_id",
        "tab_id",
        "terminal_backend",
        "workspace_id",
    }
    if set(physical) != allowed_physical:
        raise AdapterError(
            "controller_binding_invalid",
            "command-job physical binding must contain only Herdr caller and checkout IDs",
        )
    if string_at(physical, "terminal_backend") != "herdr":
        raise AdapterError("controller_binding_invalid", "command-job terminal backend must be herdr")
    job_value = envelope.get("command_job")
    if not isinstance(job_value, dict):
        raise AdapterError("controller_binding_required", "controller-issued command_job is required")
    job = cast(JsonObject, job_value)
    allowed_job = {
        "argv",
        "command",
        "cwd",
        "max_concurrency",
        "output_bound_bytes",
        "provenance",
        "resource_locks",
        "timeout_seconds",
    }
    if set(job) - allowed_job:
        raise AdapterError("controller_binding_invalid", "command_job contains unknown or authority-expanding fields")
    cwd = string_at(job, "cwd", "command cwd")
    if not cwd.startswith("/"):
        raise AdapterError("controller_binding_invalid", "command cwd must be an absolute path")
    argv_value = job.get("argv")
    if not isinstance(argv_value, list) or not argv_value:
        raise AdapterError("controller_binding_invalid", "command argv must be a non-empty literal vector")
    argv: list[str] = []
    for index, value in enumerate(argv_value):
        if not isinstance(value, str) or not value or len(value) > MAX_COMMAND_ARG_CHARS:
            raise AdapterError("controller_binding_invalid", f"command argv[{index}] is not bounded")
        if any(ord(character) < 32 for character in value) or "\x7f" in value:
            raise AdapterError("controller_binding_invalid", "command argv contains control characters")
        if COMMAND_SHELL_META_RE.search(value):
            raise AdapterError("controller_binding_invalid", "command argv contains shell interpolation or control syntax")
        if COMMAND_SENSITIVE_RE.search(value):
            raise AdapterError("controller_binding_secret", "command argv must not contain credential material")
        argv.append(value)
    command = job.get("command")
    if command is not None:
        if not isinstance(command, str) or not command or len(command) > MAX_COMMAND_ARG_CHARS:
            raise AdapterError("controller_binding_invalid", "command literal is not bounded")
        if COMMAND_SHELL_META_RE.search(command):
            raise AdapterError("controller_binding_invalid", "command literal contains shell interpolation or control syntax")
        if command != " ".join(argv):
            raise AdapterError("controller_binding_invalid", "command literal does not exactly match argv")
    timeout_value = job.get("timeout_seconds")
    if isinstance(timeout_value, bool) or not isinstance(timeout_value, int) or not 1 <= timeout_value <= MAX_COMMAND_TIMEOUT_SECONDS:
        raise AdapterError("command_timeout_invalid", "command timeout is outside the bounded range")
    output_bound = job.get("output_bound_bytes")
    if isinstance(output_bound, bool) or not isinstance(output_bound, int) or not 1 <= output_bound <= MAX_COMMAND_OUTPUT_BYTES:
        raise AdapterError("command_output_bound_invalid", "command output bound is outside the bounded range")
    max_concurrency = job.get("max_concurrency")
    if isinstance(max_concurrency, bool) or not isinstance(max_concurrency, int) or max_concurrency < 1:
        raise AdapterError("command_capacity_invalid", "command max_concurrency must be a positive integer")
    locks = job.get("resource_locks")
    if not isinstance(locks, list) or not locks or any(
        not isinstance(lock, str) or not lock or lock == "none" or any(ord(character) < 32 for character in lock)
        for lock in locks
    ) or len(set(locks)) != len(locks):
        raise AdapterError("resource_lock_required", "command-job requires exact non-empty resource locks")
    task_locks = task.get("resource_locks", [])
    if not isinstance(task_locks, list):
        raise AdapterError("resource_lock_mismatch", "approved task locks are malformed")
    provenance = job.get("provenance")
    if not isinstance(provenance, dict):
        raise AdapterError("controller_binding_required", "command-job task-or-gate provenance is required")
    provenance_kind = provenance.get("kind")
    if provenance_kind not in {"task", "gate"}:
        raise AdapterError("controller_binding_invalid", "command provenance kind must be task or gate")
    if provenance_kind == "task" and provenance.get("task_id") != task.get("task_id"):
        raise AdapterError("controller_binding_invalid", "command provenance task is not the selected task")
    if provenance_kind == "task" and sorted(locks) != sorted(task_locks):
        raise AdapterError("resource_lock_mismatch", "task command locks must exactly match the approved task locks")
    if provenance_kind == "task" and max_concurrency != 1:
        raise AdapterError("command_capacity_invalid", "task command max_concurrency must be one")
    if provenance_kind == "gate":
        gate_id = provenance.get("gate_id")
        if not isinstance(gate_id, str) or not gate_id or any(ord(character) < 32 for character in gate_id):
            raise AdapterError("controller_binding_invalid", "command gate provenance requires a bounded gate ID")
        if any(lock not in task_locks for lock in locks):
            raise AdapterError("resource_lock_mismatch", "gate command locks must be an approved task-lock subset")
        if max_concurrency > len(task_locks):
            raise AdapterError("command_capacity_invalid", "gate command max_concurrency exceeds approved task locks")
    for key in ("task_id", "gate_id"):
        value = provenance.get(key)
        if value is not None and (not isinstance(value, str) or not value or any(ord(character) < 32 for character in value)):
            raise AdapterError("controller_binding_invalid", "command provenance identity is malformed")
    return {
        "cwd": cwd,
        "argv": argv,
        "command": command if isinstance(command, str) else None,
        "timeout_seconds": timeout_value,
        "max_concurrency": max_concurrency,
        "output_bound_bytes": output_bound,
        "resource_locks": list(locks),
        "provenance": cast(JsonObject, provenance),
    }


class Adapter:
    """Own one envelope-bound Herdr run and nothing else."""

    def __init__(self, envelope_path: Path, executable: Path) -> None:
        if os.environ.get("HERDR_ENV") != "1":
            raise AdapterError("herdr_environment_required", "HERDR_ENV=1 is required")
        self.executable = executable_path(str(executable))
        self.envelope, self.run_id, self.repo, self.checkout = validate_envelope(
            envelope_path
        )
        self.common_dir = git_common_directory(self.repo)
        self.role, self.task, self.physical, self.controller, self.provenance, _ = (
            role_and_capability(self.envelope)
        )
        self.binding_kind = string_at(self.controller, "binding_kind", "binding kind") if self.controller.get("binding_kind") is not None else "delegated-task"
        self.command_job: JsonObject | None = (
            validate_command_job_shape(self.envelope, self.task, self.physical)
            if self.binding_kind == "command-job"
            else None
        )
        self.batch = batch_provenance(self.envelope, self.task)
        base_member_id = f"{string_at(self.task, 'task_id')}@{positive_int(value_at(self.task, 'attempt'), 'task attempt')}"
        command_provenance = (
            as_object(value_at(self.command_job, "provenance"), "command provenance")
            if self.command_job is not None
            else None
        )
        if command_provenance is not None and command_provenance.get("kind") == "gate":
            gate_id = string_at(command_provenance, "gate_id", "gate ID")
            gate_digest = hashlib.sha256(gate_id.encode()).hexdigest()[:12]
            self.member_id = f"{base_member_id}:gate:{gate_digest}"
        else:
            self.member_id = base_member_id
        self.profile = (
            {}
            if self.binding_kind == "command-job"
            else native_agent_profile(
                self.role, self.physical, self.controller, self.checkout
            )
        )
        self.context = caller_context(self.physical)
        self.run_root = self.repo / ".herdr-runs"
        self.run_dir = self.run_root / self.run_id
        self.state_path = self.run_dir / "state.json"
        self.lease_path = self.run_root / "lease.json"
        self.lease_identity: JsonObject = {
            "repository": str(self.repo),
            "workspace_id": self.context["workspace_id"],
            "controller_id": string_at(self.controller, "controller_id"),
            "git_common_dir_sha256": git_common_dir_key(self.common_dir),
            "plan_sha256": string_at(self.provenance, "plan_sha256"),
            "batch_id": string_at(self.batch, "batch_id"),
            "parallel_group": string_at(self.batch, "parallel_group"),
            "effective_width": max(
                positive_int(
                    value_at(self.batch, "effective_width"), "batch effective width"
                ),
                (
                    positive_int(
                        value_at(self.command_job, "max_concurrency"),
                        "command max concurrency",
                    )
                    if self.command_job is not None
                    else 1
                ),
            ),
            "selected_task_ids": value_at(self.batch, "selected_task_ids"),
        }

    def member_resource_locks(self) -> list[str]:
        value = self.command_job["resource_locks"] if self.command_job is not None else self.task.get("resource_locks", [])
        return [lock for lock in value if isinstance(lock, str)] if isinstance(value, list) else []

    def command(self, argv: list[str], *, timeout_seconds: int = 10) -> JsonObject:
        return fixture_safe_command(
            self.executable, argv, timeout_seconds=timeout_seconds
        )

    def text_command(self, argv: list[str], *, timeout_seconds: int = 10) -> str:
        return fixture_safe_text_command(
            self.executable, argv, timeout_seconds=timeout_seconds
        )

    @contextmanager
    def lease_lock(self) -> Iterator[None]:
        if self.run_root.is_symlink():
            raise AdapterError(
                "adapter_state_unsafe", "run-state root must not be a symlink"
            )
        self.run_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.run_root, 0o700)
        lock = self.run_root / ".lease.lock"
        deadline = time.monotonic() + LEASE_LOCK_WAIT_SECONDS
        while True:
            try:
                lock.mkdir(mode=0o700)
                break
            except FileExistsError as exc:
                if time.monotonic() >= deadline:
                    raise AdapterError(
                        "adapter_state_busy", "repository lease is being updated"
                    ) from exc
                time.sleep(0.05)
        try:
            yield
        finally:
            lock.rmdir()

    def owned_lease(self, allowed_states: frozenset[str]) -> JsonObject:
        if not self.lease_path.exists() or self.lease_path.is_symlink():
            raise AdapterError(
                "lease_ownership_mismatch", "run-owned repository lease is unavailable"
            )
        try:
            return validate_lease_file(
                self.lease_path,
                self.repo,
                self.common_dir,
                allowed_states=allowed_states,
                expected_identity=self.lease_identity,
            )
        except AdapterError as exc:
            raise AdapterError(
                "lease_ownership_mismatch",
                "controller lease no longer belongs to this controller, plan, workspace, or batch",
            ) from exc

    def lease_member(self, lease: JsonObject) -> JsonObject:
        members = value_at(lease, "members")
        if not isinstance(members, list):
            raise AdapterError("lease_state_invalid", "controller lease members are malformed")
        for member in members:
            if isinstance(member, dict) and member.get("member_id") == self.member_id:
                return member
        raise AdapterError("lease_member_not_found", f"run member is not in the approved batch: {self.member_id}")

    def lease_scope_matches(self, lease: JsonObject) -> bool:
        return all(
            lease.get(key) == value
            for key, value in {
                "controller_id": self.lease_identity["controller_id"],
                "workspace_id": self.lease_identity["workspace_id"],
                "plan_sha256": self.lease_identity["plan_sha256"],
                "batch_id": self.lease_identity["batch_id"],
            }.items()
        ) and (
            lease.get("selected_task_ids") == self.batch.get("selected_task_ids")
            and lease.get("effective_width") == self.lease_identity.get("effective_width")
            and lease.get("parallel_group") == self.batch.get("parallel_group")
        )

    def update_lease_member(self, member_state: str, *, phase: str | None = None) -> None:
        if member_state not in {"active", "cleanup-pending", "released"}:
            raise AdapterError("lease_state_invalid", f"unsupported member state: {member_state}")
        with self.lease_lock():
            lease = self.owned_lease(frozenset({"active", "cleanup-pending", "released"}))
            member = self.lease_member(lease)
            if lease.get("lease_state") == "released":
                if member.get("lease_state") == "released" and member_state == "released":
                    return
                raise AdapterError("lease_state_invalid", "released controller lease has no live member")
            member["lease_state"] = member_state
            if phase is not None:
                member["phase"] = phase
            members = cast(list[JsonValue], value_at(lease, "members"))
            lease["members"] = members
            if any(
                isinstance(item, dict) and item.get("lease_state") == "cleanup-pending"
                for item in members
            ):
                lease["lease_state"] = "cleanup-pending"
            elif any(
                isinstance(item, dict) and item.get("lease_state") == "active"
                for item in members
            ):
                lease["lease_state"] = "active"
            else:
                lease["lease_state"] = "released"
            self.write_json(self.lease_path, lease)

    def touch_lease_member(self, phase: str) -> None:
        with self.lease_lock():
            lease = self.owned_lease(frozenset({"active", "cleanup-pending"}))
            member = self.lease_member(lease)
            if member.get("lease_state") == "active":
                member["phase"] = phase
                self.write_json(self.lease_path, lease)

    def register_member(self) -> None:
        """Atomically admit one approved task attempt into the controller lease."""
        with self.lease_lock():
            if self.lease_path.exists() or self.lease_path.is_symlink():
                try:
                    lease = validate_lease_file(
                        self.lease_path,
                        self.repo,
                        self.common_dir,
                        allowed_states=frozenset({"active", "cleanup-pending", "released"}),
                    )
                except AdapterError as exc:
                    raise AdapterError(
                        "herdr_execution_conflict",
                        "existing lease is malformed or uses a legacy single-run schema",
                    ) from exc
                if not self.lease_scope_matches(lease):
                    if lease.get("controller_id") != self.lease_identity["controller_id"]:
                        raise AdapterError(
                            "herdr_execution_conflict",
                            "another controller owns the workspace-bound Herdr lease",
                        )
                    raise AdapterError(
                        "lease_scope_mismatch",
                        "controller lease is bound to a different plan, workspace, or batch",
                    )
                if lease.get("lease_state") == "released":
                    # A released lease can be reused only when all of its members are
                    # released and the new member is not a duplicate attempt.
                    members = value_at(lease, "members")
                    if not isinstance(members, list) or any(
                        isinstance(item, dict) and item.get("lease_state") != "released"
                        for item in members
                    ):
                        raise AdapterError("herdr_execution_conflict", "lease is not quiescent")
                    # A completed controller lease is a historical record for the
                    # previous execution. Start a fresh admission set while retaining
                    # each prior run's durable state.json evidence.
                    members = []
                    lease["members"] = members
                members_value = value_at(lease, "members")
                members = cast(list[JsonValue], members_value)
                for item in members:
                    if isinstance(item, dict) and item.get("member_id") == self.member_id:
                        raise AdapterError(
                            "duplicate_task_attempt",
                            f"task attempt is already admitted: {self.member_id}",
                        )
                member_locks = set(self.member_resource_locks())
                for item in members:
                    if not isinstance(item, dict) or item.get("lease_state") == "released":
                        continue
                    prior_locks = item.get("resource_locks", [])
                    if isinstance(prior_locks, list) and member_locks.intersection(
                        lock for lock in prior_locks if isinstance(lock, str)
                    ):
                        raise AdapterError(
                            "resource_lock_conflict",
                            "an active controller member already owns one of the exact resource locks",
                        )
                width = positive_int(value_at(lease, "effective_width"), "lease effective_width")
                active_members = [
                    item
                    for item in members
                    if isinstance(item, dict) and item.get("lease_state") != "released"
                ]
                if len(active_members) >= width:
                    raise AdapterError(
                        "batch_width_exhausted",
                        f"effective batch width {width} is exhausted by approved members",
                    )
            else:
                members = []
                lease = {
                    "schema_version": LEASE_SCHEMA_VERSION,
                    "artifact_kind": "herdr-controller-lease",
                    "lease_state": "active",
                    **self.lease_identity,
                    "effective_width": positive_int(
                        value_at(self.lease_identity, "effective_width"), "lease effective_width"
                    ),
                    "selected_task_ids": value_at(self.batch, "selected_task_ids"),
                    "parallel_group": value_at(self.batch, "parallel_group"),
                    "resource_locks": [],
                    "members": members,
                }
            member: JsonObject = {
                "member_id": self.member_id,
                "run_id": self.run_id,
                "run_nonce_sha256": hashlib.sha256(
                    string_at(self.controller, "run_nonce").encode()
                ).hexdigest(),
                "task_id": string_at(self.task, "task_id"),
                "attempt": positive_int(value_at(self.task, "attempt"), "task attempt"),
                "controller_id": self.lease_identity["controller_id"],
                "workspace_id": self.lease_identity["workspace_id"],
                "batch_id": self.lease_identity["batch_id"],
                "lease_state": "active",
                "phase": "preflight",
                "binding_kind": self.binding_kind,
                "resource_locks": self.member_resource_locks(),
            }
            members.append(member)
            lease["members"] = members
            lease["resource_locks"] = sorted(
                {
                    lock
                    for item in members
                    if isinstance(item, dict)
                    for lock in item.get("resource_locks", [])
                    if isinstance(lock, str)
                }
            )
            lease["lease_state"] = "active"
            self.write_json(self.lease_path, lease)

    def lock(self) -> Path:
        if self.run_root.is_symlink() or self.run_dir.is_symlink():
            raise AdapterError(
                "adapter_state_unsafe", "run-state path must not be a symlink"
            )
        self.run_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.run_dir, 0o700)
        lock = self.run_dir / ".state.lock"
        try:
            lock.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise AdapterError(
                "adapter_state_busy", "run state is locked by another writer"
            ) from exc
        return lock

    def write_json(self, path: Path, value: JsonObject) -> None:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(path.parent, 0o700)
        fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        temporary = Path(temporary_name)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(value, stream, sort_keys=True, separators=(",", ":"))
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            os.chmod(path, 0o600)
        except OSError as exc:
            temporary.unlink(missing_ok=True)
            raise AdapterError(
                "adapter_state_write_failed", f"atomic state write failed: {path}"
            ) from exc

    def state(self) -> JsonObject:
        if not self.state_path.exists() or self.state_path.is_symlink():
            raise AdapterError(
                "controller_binding_required", "adapter state does not exist"
            )
        if stat.S_IMODE(self.state_path.stat().st_mode) & 0o077:
            raise AdapterError(
                "adapter_state_unsafe", "adapter state must be owner-only"
            )
        return parse_json_file(self.state_path, "adapter state")

    def save_state(self, state: JsonObject) -> None:
        lock = self.lock()
        try:
            self.write_json(self.state_path, state)
        finally:
            lock.rmdir()

    def output(self, state: JsonObject) -> JsonObject:
        return {"ok": True, "run_id": self.run_id, "state": state}

    def sanitized_env_arguments(self) -> list[str]:
        names = sorted(
            {
                *SENSITIVE_ENV_NAMES,
                *(
                    name
                    for name in os.environ
                    if SENSITIVE_ENV_NAME_RE.search(name) is not None
                ),
            }
        )
        arguments: list[str] = []
        for name in names:
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                arguments.extend(["--env", f"{name}="])
        return arguments

    def validate_caller_resources(self) -> JsonObject:
        workspace = result_entity(
            self.command(["workspace", "get", self.context["workspace_id"]]),
            "workspace",
        )
        tab = result_entity(self.command(["tab", "get", self.context["tab_id"]]), "tab")
        pane = result_entity(
            self.command(["pane", "get", self.context["pane_id"]]), "pane"
        )
        if (
            workspace.get("workspace_id") != self.context["workspace_id"]
            or tab.get("workspace_id") != self.context["workspace_id"]
            or tab.get("tab_id") != self.context["tab_id"]
            or pane.get("workspace_id") != self.context["workspace_id"]
            or pane.get("tab_id") != self.context["tab_id"]
            or pane.get("pane_id") != self.context["pane_id"]
        ):
            raise AdapterError(
                "caller_context_mismatch", "live Herdr caller hierarchy differs"
            )
        terminal_id = pane.get("terminal_id")
        if not isinstance(terminal_id, str) or not terminal_id:
            raise AdapterError(
                "caller_context_mismatch", "caller terminal identity is unavailable"
            )
        caller: JsonObject = {**self.context, "terminal_id": terminal_id}
        session = pane.get("agent_session")
        if isinstance(session, dict) and isinstance(session.get("value"), str):
            caller["agent_session_id"] = session["value"]
        return caller

    def pane_process_info(self, pane_id: str) -> JsonObject:
        return result_entity(
            self.command(["pane", "process-info", "--pane", pane_id]),
            "process_info",
        )

    def owned_pane_record(
        self, pane: JsonObject, *, kind: str, shell_pid: int | None = None
    ) -> JsonObject:
        terminal_id = pane.get("terminal_id")
        pane_id = pane.get("pane_id")
        if (
            not isinstance(terminal_id, str)
            or not terminal_id
            or not isinstance(pane_id, str)
            or not pane_id
            or pane.get("workspace_id") != self.context["workspace_id"]
        ):
            raise AdapterError(
                "herdr_identity_mismatch", "allocated pane identity is incomplete"
            )
        record: JsonObject = {
            "pane_id": pane_id,
            "terminal_id": terminal_id,
            "kind": kind,
            "owned": True,
            "closed": False,
        }
        if shell_pid is not None:
            record["shell_pid"] = shell_pid
        return record

    def persist_allocated_pane(
        self,
        state: JsonObject,
        resources: JsonObject,
        pane: JsonObject,
        *,
        kind: str,
    ) -> JsonObject:
        """Persist opaque allocation identity before fallible identity enrichment."""
        record = self.owned_pane_record(pane, kind=kind)
        panes = cast(list[JsonValue], resources["owned_panes"])
        panes.append(record)
        resources["owned_panes"] = panes
        state["resources"] = resources
        self.save_state(state)
        return record

    def enrich_allocated_pane(self, state: JsonObject, record: JsonObject) -> None:
        record["shell_pid"] = self.shell_pid(string_at(record, "pane_id"))
        self.save_state(state)

    def shell_pid(self, pane_id: str) -> int:
        process_info = self.pane_process_info(pane_id)
        value = process_info.get("shell_pid")
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise AdapterError(
                "herdr_identity_mismatch", "pane shell identity is unavailable"
            )
        return value

    def preflight(self) -> JsonObject:
        if self.run_root.exists() and (
            self.run_root.is_symlink() or not self.run_root.is_dir()
        ):
            raise AdapterError(
                "adapter_state_unsafe", "run-state root must be a real directory"
            )
        if self.run_dir.exists() and (
            self.run_dir.is_symlink() or not self.run_dir.is_dir()
        ):
            raise AdapterError(
                "adapter_state_unsafe", "run directory must be a real directory"
            )
        if self.state_path.is_symlink() or self.lease_path.is_symlink():
            raise AdapterError(
                "adapter_state_unsafe", "run-state files must not be symlinks"
            )
        if self.state_path.exists():
            raise AdapterError(
                "herdr_execution_conflict",
                "this approved task attempt already has adapter state; use resume or cleanup",
            )
        if self.lease_path.exists() or self.lease_path.is_symlink():
            try:
                validate_lease_file(
                    self.lease_path,
                    self.repo,
                    self.common_dir,
                    allowed_states=frozenset({"active", "cleanup-pending", "released"}),
                )
            except AdapterError as exc:
                raise AdapterError(
                    "herdr_execution_conflict",
                    "existing lease is malformed or uses a legacy single-run schema",
                ) from exc
        live_caller = self.validate_caller_resources()
        self.register_member()
        state: JsonObject = {
            "schema_version": SCHEMA_VERSION,
            "artifact_kind": "herdr-adapter-state",
            "run_id": self.run_id,
            "phase": "preflight",
            "lease_state": "active",
            "controller": {
                "controller_id": string_at(self.controller, "controller_id"),
                "run_id": self.run_id,
                "run_nonce_sha256": hashlib.sha256(
                    string_at(self.controller, "run_nonce").encode()
                ).hexdigest(),
            },
            "provenance": {
                "canonical_repository": str(self.repo),
                "repository_revision": string_at(
                    self.provenance, "repository_revision"
                ),
                "plan_sha256": string_at(self.provenance, "plan_sha256"),
                "ledger_sha256": string_at(self.provenance, "ledger_sha256"),
                "batch": self.batch,
            },
            "batch": self.batch,
            "batch_provenance": self.batch,
            "member_id": self.member_id,
            "caller_context": live_caller,
            "task": {
                "task_id": string_at(self.task, "task_id"),
                "attempt": value_at(self.task, "attempt"),
                "runtime_role": self.role,
                "touch_set": list_at(self.task, "touch_set"),
                "oracle_refs": list_at(self.task, "oracle_refs"),
                "resource_locks": self.member_resource_locks(),
            },
            "physical_binding": {
                "terminal_backend": string_at(self.physical, "terminal_backend"),
                **(
                    {
                        "agent_kind": string_at(self.physical, "agent_kind"),
                        "agent_name": string_at(self.physical, "agent_name"),
                        "model": string_at(self.physical, "model"),
                        "reasoning_effort": string_at(self.physical, "reasoning_effort"),
                        "permission_mode": string_at(self.physical, "permission_mode"),
                        "sandbox_mode": string_at(self.physical, "sandbox_mode"),
                        "capability_profile": string_at(self.physical, "capability_profile"),
                        "control_plane_endpoint": string_at(self.physical, "control_plane_endpoint"),
                        "credential_ref": string_at(self.physical, "credential_ref"),
                    }
                    if self.binding_kind != "command-job"
                    else {}
                ),
                "checkout_path": str(self.checkout),
                **(
                    {
                        "explorer_cost": self.explorer_cost(),
                        "model_policy": string_at(self.controller, "model_policy"),
                        "profile_id": string_at(self.profile, "profile_id"),
                        "native_argv_sha256": digest_json(value_at(self.profile, "native_args")),
                        "environment_policy": string_at(self.profile, "environment_policy"),
                    }
                    if self.binding_kind != "command-job"
                    else {}
                ),
            },
            "physical_binding_sha256": digest_json(cast(JsonValue, self.physical)),
            "denied_task_capabilities": [
                "task-tool-network",
                "undeclared-credentials",
                "ssh",
                "provider-actions",
                "commit",
                "push",
                "deploy",
                "destructive-outside-worktree",
            ],
            "resources": {
                "workspace_id": self.context["workspace_id"],
                "caller_tab_id": self.context["tab_id"],
                "caller_pane_id": self.context["pane_id"],
                "owned_tab_id": None,
                "owned_panes": [],
                "agent_name": None,
                "agent_session_id": None,
            },
            "agent_state": "unknown",
            "shell_readiness": "pending",
            "start_attempted": False,
            "prompt_submitted": False,
            "events": [],
            "evidence": [],
        }
        if self.command_job is not None:
            state["binding_kind"] = "command-job"
            state["command_job"] = {
                "cwd": self.command_job["cwd"],
                "argv_sha256": digest_json(cast(JsonValue, self.command_job["argv"])),
                "command_sha256": digest_json(self.command_job.get("command")),
                "timeout_seconds": self.command_job["timeout_seconds"],
                "max_concurrency": self.command_job["max_concurrency"],
                "output_bound_bytes": self.command_job["output_bound_bytes"],
                "resource_locks": self.command_job["resource_locks"],
                "provenance": self.command_job["provenance"],
                "oracle_judgment_required": True,
            }
        self.save_state(state)
        self.touch_lease_member("preflight")
        return self.output(state)

    def explorer_cost(self) -> JsonObject:
        return as_object(
            value_at(self.profile, "model_policy_evidence"),
            "model policy evidence",
        )

    def allocate(self) -> JsonObject:
        state = self.state()
        if state.get("phase") != "preflight":
            raise AdapterError(
                "adapter_state_invalid", "allocate requires preflight state"
            )
        environment_args = self.sanitized_env_arguments()
        tab_response = self.command(
            [
                "tab",
                "create",
                "--workspace",
                self.context["workspace_id"],
                "--cwd",
                str(self.checkout),
                "--label",
                f"herdr-{self.run_id}"[:64],
                "--no-focus",
                *environment_args,
            ]
        )
        tab = result_entity(tab_response, "tab")
        root_pane = result_entity(tab_response, "root_pane")
        tab_id = string_at(tab, "tab_id")
        root_pane_id = string_at(root_pane, "pane_id")
        if (
            tab.get("workspace_id") != self.context["workspace_id"]
            or root_pane.get("workspace_id") != self.context["workspace_id"]
            or root_pane.get("tab_id") != tab_id
        ):
            raise AdapterError(
                "herdr_identity_mismatch", "allocated tab belongs to another workspace"
            )
        resources = as_object(value_at(state, "resources"), "state resources")
        resources["owned_tab_id"] = tab_id
        resources["owned_panes"] = []
        resources["agent_name"] = (
            string_at(self.physical, "agent_name")
            if self.binding_kind != "command-job"
            else None
        )
        state["resources"] = resources
        state["phase"] = "allocated"
        self.event(
            state,
            "allocate",
            {"tab_id": tab_id, "root_pane_id": root_pane_id},
        )
        self.save_state(state)
        try:
            root_record = self.persist_allocated_pane(
                state, resources, root_pane, kind="root"
            )
            self.enrich_allocated_pane(state, root_record)
            pane_response = self.command(
                [
                    "pane",
                    "split",
                    "--pane",
                    root_pane_id,
                    "--direction",
                    "right",
                    "--cwd",
                    str(self.checkout),
                    "--no-focus",
                    *environment_args,
                ]
            )
            child_pane = result_entity(pane_response, "pane")
            string_at(child_pane, "pane_id")
            if (
                child_pane.get("workspace_id") != self.context["workspace_id"]
                or child_pane.get("tab_id") != tab_id
            ):
                raise AdapterError(
                    "herdr_identity_mismatch", "child pane hierarchy differs"
                )
            child_record = self.persist_allocated_pane(
                state, resources, child_pane, kind="child"
            )
            self.enrich_allocated_pane(state, child_record)
        except AdapterError:
            self.mark_cleanup_pending(state, "allocation_failed")
            raise
        return self.output(state)

    def shell_ready(self, timeout_seconds: int = MAX_SHELL_READINESS_SECONDS) -> JsonObject:
        """Prove an allocated pane has an interactive shell before starting an agent."""
        state = self.state()
        if state.get("phase") == "shell-ready":
            return self.output(state)
        if state.get("phase") != "allocated":
            raise AdapterError("adapter_state_invalid", "shell readiness requires allocated state")
        if not 1 <= timeout_seconds <= MAX_SHELL_READINESS_SECONDS:
            raise AdapterError(
                "shell_readiness_timeout_invalid",
                f"shell readiness timeout must be between 1 and {MAX_SHELL_READINESS_SECONDS} seconds",
            )
        _, child = self.active_child(state)
        pane_id = string_at(child, "pane_id")
        deadline = time.monotonic() + timeout_seconds
        attempts = 0
        stable_shell_pid: int | None = None
        stable_shell_since: float | None = None
        last_reason = "interactive shell not available"
        while True:
            attempts += 1
            try:
                process_info = self.pane_process_info(pane_id)
            except AdapterError as exc:
                if exc.code == "agent_pane_busy":
                    state["shell_readiness"] = "blocked"
                    self.mark_cleanup_pending(state, "agent_pane_busy")
                    raise
                last_reason = exc.message
            else:
                processes = process_info.get("foreground_processes")
                shell_pid = process_info.get("shell_pid")
                if isinstance(processes, list) and isinstance(shell_pid, int) and not isinstance(shell_pid, bool):
                    agent_process = any(
                        isinstance(item, dict)
                        and (
                            item.get("name") in {"codex", "grok", "claude"}
                            or item.get("agent") in {"codex", "grok", "claude"}
                        )
                        for item in processes
                    )
                    if agent_process:
                        state["shell_readiness"] = "blocked"
                        self.mark_cleanup_pending(state, "agent_pane_busy")
                        raise AdapterError(
                            "agent_pane_busy",
                            f"allocated pane {pane_id} already has an agent process",
                        )
                    shell = next(
                        (
                            item
                            for item in processes
                            if isinstance(item, dict)
                            and item.get("pid") == shell_pid
                            and (
                                item.get("name") in INTERACTIVE_SHELL_NAMES
                                or item.get("argv0") in INTERACTIVE_SHELL_NAMES
                                or (
                                    isinstance(item.get("argv"), list)
                                    and str(item.get("argv", [""])[0]).lstrip("-")
                                    in INTERACTIVE_SHELL_NAMES
                                )
                            )
                        ),
                        None,
                    )
                    if shell is not None and shell.get("interactive", True) is not False:
                        shell_pid_value = shell.get("pid")
                        if shell_pid_value != stable_shell_pid:
                            stable_shell_pid = cast(int, shell_pid_value)
                            stable_shell_since = time.monotonic()
                            last_reason = "interactive shell has not remained stable across observations"
                        if (
                            stable_shell_since is not None
                            and stable_shell_since + SHELL_STABLE_SECONDS > deadline
                        ):
                            state["shell_readiness"] = {
                                "state": "deadline",
                                "pane_id": pane_id,
                                "attempts": attempts,
                                "timeout_seconds": timeout_seconds,
                                "last_reason": safe_preview(last_reason),
                            }
                            self.mark_cleanup_pending(state, "shell_readiness_deadline")
                            raise AdapterError(
                                "shell_readiness_deadline",
                                f"interactive shell cannot complete its stable interval in pane {pane_id} before the {timeout_seconds}s deadline; inspect or cleanup the owned member",
                            )
                        if (
                            stable_shell_since is not None
                            and time.monotonic() - stable_shell_since < SHELL_STABLE_SECONDS
                        ):
                            if time.monotonic() >= deadline:
                                state["shell_readiness"] = {
                                    "state": "deadline",
                                    "pane_id": pane_id,
                                    "attempts": attempts,
                                    "timeout_seconds": timeout_seconds,
                                    "last_reason": safe_preview(last_reason),
                                }
                                self.mark_cleanup_pending(state, "shell_readiness_deadline")
                                raise AdapterError(
                                    "shell_readiness_deadline",
                                    f"interactive shell was not stable in pane {pane_id} before the {timeout_seconds}s deadline; inspect or cleanup the owned member",
                                )
                            time.sleep(SHELL_POLL_SECONDS)
                            continue
                        child["shell_pid"] = shell_pid_value
                        state["shell_readiness"] = {
                            "state": "ready",
                            "pane_id": pane_id,
                            "shell_pid": shell_pid_value,
                            "attempts": attempts,
                            "timeout_seconds": timeout_seconds,
                        }
                        state["phase"] = "shell-ready"
                        self.event(
                            state,
                            "shell-ready",
                            {"pane_id": pane_id, "shell_pid": shell_pid_value, "attempts": attempts},
                        )
                        self.save_state(state)
                        self.touch_lease_member("shell-ready")
                        return self.output(state)
                    last_reason = "foreground process is not an interactive shell"
                else:
                    last_reason = "pane process information has no shell identity"
            if time.monotonic() >= deadline:
                state["shell_readiness"] = {
                    "state": "deadline",
                    "pane_id": pane_id,
                    "attempts": attempts,
                    "timeout_seconds": timeout_seconds,
                    "last_reason": safe_preview(last_reason),
                }
                self.mark_cleanup_pending(state, "shell_readiness_deadline")
                raise AdapterError(
                    "shell_readiness_deadline",
                    f"interactive shell was not available in pane {pane_id} before the {timeout_seconds}s deadline; inspect or cleanup the owned member",
                )
            time.sleep(SHELL_POLL_SECONDS)

    def event(self, state: JsonObject, action: str, details: JsonObject) -> None:
        events = list_at(state, "events")
        events.append({"action": action, "at": int(time.time()), "details": details})
        state["events"] = events[-64:]

    def mark_cleanup_pending(self, state: JsonObject, reason: str) -> None:
        state["phase"] = "cleanup-pending"
        state["lease_state"] = "cleanup-pending"
        self.event(state, "cleanup-pending", {"reason": reason})
        self.save_state(state)
        if self.lease_path.exists():
            self.update_lease_member("cleanup-pending", phase="cleanup-pending")

    def active_child(self, state: JsonObject) -> tuple[JsonObject, JsonObject]:
        resources = as_object(value_at(state, "resources"), "state resources")
        child = next(
            (
                item
                for item in list_at(resources, "owned_panes")
                if isinstance(item, dict)
                and item.get("kind") == "child"
                and item.get("closed") is False
            ),
            None,
        )
        if child is None:
            raise AdapterError(
                "herdr_identity_mismatch", "owned child pane is unavailable"
            )
        return resources, child

    def validate_agent_response(
        self, state: JsonObject, response: JsonObject
    ) -> JsonObject:
        resources, child = self.active_child(state)
        agent = result_entity(response, "agent")
        expected_session = child.get("agent_session_id")
        observed_session = result_agent_session(response)
        if (
            agent.get("agent") != string_at(self.physical, "agent_kind")
            or agent.get("name") != string_at(self.physical, "agent_name")
            or agent.get("pane_id") != child.get("pane_id")
            or agent.get("terminal_id") != child.get("terminal_id")
            or agent.get("tab_id") != resources.get("owned_tab_id")
            or agent.get("workspace_id") != self.context["workspace_id"]
            or (
                isinstance(expected_session, str)
                and expected_session
                and observed_session != expected_session
            )
        ):
            raise AdapterError(
                "herdr_identity_mismatch", "live agent identity differs from state"
            )
        if observed_session is not None and expected_session is None:
            child["agent_session_id"] = observed_session
            resources["agent_session_id"] = observed_session
            state["resources"] = resources
        return agent

    def start(self) -> JsonObject:
        if self.binding_kind == "command-job":
            return self.command_start()
        state = self.state()
        if state.get("start_attempted") is True:
            raise AdapterError(
                "agent_start_already_attempted",
                "agent startup is single-submit; use resume or cleanup for this member",
            )
        if state.get("phase") == "allocated":
            # Keep the readiness transition explicit in persisted state while
            # allowing callers of the original sequence to converge through it.
            self.shell_ready()
            state = self.state()
        if state.get("phase") != "shell-ready":
            raise AdapterError(
                "adapter_state_invalid", "start requires a proven shell-readiness transition"
            )
        resources = as_object(value_at(state, "resources"), "state resources")
        panes = [
            item for item in list_at(resources, "owned_panes") if isinstance(item, dict)
        ]
        child = next(
            (
                item
                for item in panes
                if item.get("kind") == "child" and item.get("closed") is False
            ),
            None,
        )
        if child is None:
            raise AdapterError(
                "herdr_identity_mismatch", "owned child pane is unavailable"
            )
        agent_name = string_at(self.physical, "agent_name")
        native_values = list_at(self.profile, "native_args")
        if not all(isinstance(value, str) for value in native_values):
            raise AdapterError(
                "delegated_capability_unavailable", "native agent argv is malformed"
            )
        native_args = cast(list[str], native_values)
        child_pane_id = string_at(cast(JsonObject, child), "pane_id")
        state["start_attempted"] = True
        self.event(state, "start-attempt", {"pane_id": child_pane_id, "agent_name": agent_name})
        self.save_state(state)
        kind = string_at(self.physical, "agent_kind")
        argv: JsonValue = None
        matching_process: JsonObject | None = None
        try:
            response = self.command(
                [
                    "agent",
                    "start",
                    agent_name,
                    "--kind",
                    kind,
                    "--pane",
                    child_pane_id,
                    "--timeout",
                    "120000",
                    "--",
                    *native_args,
                ],
                timeout_seconds=125,
            )
        except AdapterError:
            self.mark_cleanup_pending(state, "agent_start_failed")
            raise
        try:
            result = result_object(response)
            agent = result_entity(response, "agent")
            if (
                agent.get("agent") != kind
                or agent.get("name") != agent_name
                or agent.get("pane_id") != child_pane_id
                or agent.get("tab_id") != resources.get("owned_tab_id")
                or agent.get("workspace_id") != self.context["workspace_id"]
                or agent.get("terminal_id") != child.get("terminal_id")
            ):
                raise AdapterError("herdr_identity_mismatch", "started agent identity differs")
            argv = result.get("argv")
            if argv != [kind, *native_args]:
                raise AdapterError(
                    "delegated_capability_unavailable",
                    "Herdr did not start the exact validated native argv",
                )
            process_info = self.pane_process_info(child_pane_id)
            processes = process_info.get("foreground_processes")
            matching_process = None
            if isinstance(processes, list):
                for item in processes:
                    if (
                        isinstance(item, dict)
                        and item.get("name") == kind
                        and item.get("argv") == [kind, *native_args]
                    ):
                        matching_process = item
                        break
            if matching_process is None:
                raise AdapterError("herdr_identity_mismatch", "started agent process cannot be proven")
        except AdapterError:
            self.mark_cleanup_pending(state, "agent_start_identity_failed")
            raise
        session_id = result_agent_session(response)
        state["phase"] = "started"
        state["agent_state"] = result_state(response)
        resources["agent_session_id"] = session_id
        child["agent_kind"] = kind
        child["agent_name"] = agent_name
        child["agent_session_id"] = session_id
        child["agent_argv_sha256"] = digest_json(cast(JsonValue, argv))
        child["agent_pid"] = matching_process.get("pid")
        state["resources"] = resources
        self.event(
            state,
            "start",
            {
                "agent_name": agent_name,
                "agent_session_id": session_id,
                "agent_kind": kind,
            },
        )
        self.save_state(state)
        self.touch_lease_member("started")
        return self.output(state)

    def prompt(self, prompt: str) -> JsonObject:
        if self.binding_kind == "command-job":
            raise AdapterError("command_prompt_denied", "ordinary command jobs have no agent prompt lifecycle")
        state = self.state()
        if state.get("prompt_submitted") is True:
            raise AdapterError(
                "prompt_already_submitted", "one prompt is allowed per attempt"
            )
        if state.get("phase") != "started":
            raise AdapterError("adapter_state_invalid", "prompt requires started state")
        resources, child = self.active_child(state)
        child_pane_id = string_at(child, "pane_id")
        current = self.command(["agent", "get", child_pane_id])
        self.validate_agent_response(state, current)
        current_state = result_state(current)
        if current_state == "busy":
            raise AdapterError(
                "busy_prompt_denied", "cannot submit while agent is busy"
            )
        if not prompt or len(prompt) > MAX_PROMPT_CHARS:
            raise AdapterError("prompt_invalid", "prompt must be bounded and non-empty")
        try:
            response = self.command(
                [
                    "agent",
                    "prompt",
                    child_pane_id,
                    prompt,
                    "--wait",
                    "--until",
                    "working",
                    "--until",
                    "idle",
                    "--until",
                    "done",
                    "--until",
                    "blocked",
                    "--until",
                    "unknown",
                    "--timeout",
                    "5000",
                ],
                timeout_seconds=10,
            )
        except AdapterError as exc:
            state["agent_state"] = (
                "stalled" if exc.code == "herdr_command_timeout" else "unknown"
            )
            self.mark_cleanup_pending(state, "prompt_failed")
            raise AdapterError("agent_prompt_stalled", str(exc)) from exc
        self.validate_agent_response(state, response)
        prompt_observation = result_state(response)
        if prompt_observation in {"unknown", "blocked", "stalled"}:
            state["prompt_submitted"] = True
            state["prompt_sha256"] = hashlib.sha256(prompt.encode()).hexdigest()
            state["agent_state"] = prompt_observation
            self.mark_cleanup_pending(state, "prompt_lifecycle_stalled")
            raise AdapterError(
                "agent_prompt_stalled",
                "agent prompt entered a non-runnable state",
            )
        state["phase"] = "prompted"
        state["prompt_submitted"] = True
        state["prompt_sha256"] = hashlib.sha256(prompt.encode()).hexdigest()
        state["agent_state"] = prompt_observation
        state["resources"] = resources
        self.event(state, "prompt", {"prompt_sha256": state["prompt_sha256"]})
        self.save_state(state)
        self.touch_lease_member("prompted")
        return self.output(state)

    def wait(self, timeout_seconds: int) -> JsonObject:
        if self.binding_kind == "command-job":
            return self.command_wait(timeout_seconds)
        state = self.state()
        if state.get("phase") not in {"prompted", "waiting"}:
            raise AdapterError(
                "adapter_state_invalid", "wait requires a submitted prompt"
            )
        if not 1 <= timeout_seconds <= MAX_WAIT_SECONDS:
            raise AdapterError(
                "wait_timeout_invalid", "wait timeout is outside bounded range"
            )
        try:
            _, child = self.active_child(state)
            response = self.command(
                [
                    "agent",
                    "wait",
                    string_at(child, "pane_id"),
                    "--until",
                    "idle",
                    "--until",
                    "done",
                    "--until",
                    "blocked",
                    "--until",
                    "unknown",
                    "--timeout",
                    str(timeout_seconds * 1000),
                ],
                timeout_seconds=timeout_seconds + 5,
            )
        except AdapterError as exc:
            if exc.code == "herdr_command_timeout":
                state["agent_state"] = "timeout"
                self.mark_cleanup_pending(state, "wait_timeout")
                raise AdapterError(
                    "agent_timeout", "bounded agent wait timed out"
                ) from exc
            state["agent_state"] = "unknown"
            self.save_state(state)
            raise
        self.validate_agent_response(state, response)
        observation = result_state(response)
        if observation not in OBSERVED_STATES:
            observation = "unknown"
        state["phase"] = "waiting"
        state["agent_state"] = observation
        self.event(
            state,
            "wait",
            {"observation": observation, "timeout_seconds": timeout_seconds},
        )
        if observation in {"blocked", "unknown", "stalled", "timeout"}:
            self.mark_cleanup_pending(state, f"agent_{observation}")
        else:
            self.save_state(state)
            self.touch_lease_member("waiting")
        return self.output(state)

    def collect(self) -> JsonObject:
        if self.binding_kind == "command-job":
            return self.command_collect()
        state = self.state()
        if state.get("phase") not in {"waiting", "collected"}:
            raise AdapterError(
                "adapter_state_invalid", "collect requires a wait observation"
            )
        _, child = self.active_child(state)
        child_pane_id = string_at(child, "pane_id")
        get_response = self.command(["agent", "get", child_pane_id])
        self.validate_agent_response(state, get_response)
        observed_state = result_state(get_response)
        if observed_state == "busy":
            raise AdapterError(
                "agent_busy", "cannot collect evidence while agent is busy"
            )
        raw_evidence = self.text_command(
            [
                "agent",
                "read",
                child_pane_id,
                "--source",
                "recent-unwrapped",
                "--lines",
                "80",
                "--format",
                "text",
            ]
        )
        bounded_evidence = safe_preview(raw_evidence)
        claim_value: JsonValue = observed_state in {"idle", "done"}
        evidence: JsonObject = {
            "sha256": hashlib.sha256(raw_evidence.encode()).hexdigest(),
            "bounded_chars": len(bounded_evidence),
            "line_count": min(80, raw_evidence.count("\n") + 1),
            "completion_claim": claim_value,
            "preview_sha256": hashlib.sha256(bounded_evidence.encode()).hexdigest(),
        }
        state["phase"] = "collected"
        state["agent_state"] = observed_state
        state["evidence"] = [evidence]
        self.event(
            state,
            "collect",
            {
                "evidence_sha256": evidence["sha256"],
                "agent_state": state.get("agent_state", "unknown"),
            },
        )
        needs_cleanup = state.get("agent_state") in {"blocked", "unknown", "stalled", "timeout"}
        if needs_cleanup:
            state["lease_state"] = "cleanup-pending"
        self.save_state(state)
        if needs_cleanup:
            self.update_lease_member("cleanup-pending", phase="cleanup-pending")
        else:
            self.touch_lease_member("collected")
        return self.output(state)

    def active_command_child(self, state: JsonObject) -> tuple[JsonObject, JsonObject]:
        if self.binding_kind != "command-job":
            raise AdapterError("adapter_state_invalid", "ordinary command state is unavailable for an agent binding")
        return self.active_child(state)

    def command_run_result(self, response: JsonObject) -> JsonObject:
        result = result_object(response)
        candidate = result.get("command_job", result.get("run", result.get("process", result)))
        if not isinstance(candidate, dict):
            raise AdapterError("herdr_protocol_invalid", "pane run did not return a command observation")
        return cast(JsonObject, candidate)

    def command_markers(self) -> tuple[str, str]:
        nonce = string_at(self.controller, "run_nonce")
        digest = hashlib.sha256(f"{self.run_id}:{nonce}".encode()).hexdigest()[:20]
        return f"HBU040_{digest}_START:", f"HBU040_{digest}_DONE:"

    def command_text(
        self, argv: list[str], start_marker: str, done_marker: str
    ) -> tuple[str, list[str]]:
        if not argv:
            raise AdapterError("controller_binding_invalid", "ordinary command argv is empty")
        command = " ".join(shlex.quote(value) for value in argv)
        start_split = start_marker.index("_") + 1
        done_split = done_marker.index("_") + 1
        body = (
            "printf '\\n%s%s%d%s\\n' "
            f"{shlex.quote(start_marker[:start_split])} {shlex.quote(start_marker[start_split:])} "
            "\"$$\" ':PID'; "
            f"{command}; __hbu_rc=$?; "
            "printf '\\n%s%s%d%s\\n' "
            f"{shlex.quote(done_marker[:done_split])} {shlex.quote(done_marker[done_split:])} "
            "\"$__hbu_rc\" ':END'; exit \"$__hbu_rc\""
        )
        wrapper_argv = ["/bin/sh", "-c", body]
        return " ".join(shlex.quote(value) for value in wrapper_argv), wrapper_argv

    def command_start_pid(self, pane_id: str, marker: str) -> int:
        snapshot = self.text_command(
            [
                "pane", "read", pane_id, "--source", "recent-unwrapped",
                "--lines", "120", "--format", "text",
            ],
            timeout_seconds=10,
        )
        match = re.search(rf"{re.escape(marker)}(\d+):PID", snapshot)
        if match is None:
            raise AdapterError(
                "command_process_missing",
                "pane output did not contain the unique ordinary-command process marker",
            )
        return positive_int(int(match.group(1)), "command process pid")

    def command_exit_code(self, pane_id: str, marker: str) -> int:
        snapshot = self.text_command(
            [
                "pane",
                "read",
                pane_id,
                "--source",
                "recent-unwrapped",
                "--lines",
                "120",
                "--format",
                "text",
            ],
            timeout_seconds=10,
        )
        match = re.search(rf"{re.escape(marker)}(-?\d+):END", snapshot)
        if match is None:
            raise AdapterError(
                "command_exit_missing",
                "pane output did not contain the unique ordinary-command completion marker",
            )
        return int(match.group(1))

    def command_observation(self, state: JsonObject, observation: JsonObject) -> None:
        _, child = self.active_command_child(state)
        pane_id = string_at(child, "pane_id")
        job = self.command_job
        if job is None:
            raise AdapterError("controller_binding_required", "ordinary command projection is unavailable")
        if observation.get("pane_id", pane_id) != pane_id:
            raise AdapterError("herdr_identity_mismatch", "ordinary command observation targets another pane")
        if observation.get("cwd", job["cwd"]) != job["cwd"]:
            raise AdapterError("controller_binding_cwd_mismatch", "ordinary command observation cwd changed")
        expected_argv = job["argv"]
        observed_argv = observation.get("argv", expected_argv)
        if observed_argv != expected_argv:
            raise AdapterError("herdr_identity_mismatch", "pane run did not execute the exact controller argv")
        exit_value = observation.get("exit_code")
        if exit_value is not None and (
            isinstance(exit_value, bool) or not isinstance(exit_value, int) or not -255 <= exit_value <= 255
        ):
            raise AdapterError("herdr_protocol_invalid", "ordinary command exit code is malformed")
        process = observation.get("process")
        if process is not None and not isinstance(process, dict):
            raise AdapterError("herdr_protocol_invalid", "ordinary command process evidence is malformed")
        if isinstance(process, dict):
            process_pane = process.get("pane_id", pane_id)
            if process_pane != pane_id:
                raise AdapterError("herdr_identity_mismatch", "ordinary command process moved panes")
            process_argv = process.get("argv", expected_argv)
            if process_argv != expected_argv:
                raise AdapterError("herdr_identity_mismatch", "ordinary command process argv changed")
            if isinstance(process.get("pid"), bool) or (process.get("pid") is not None and not isinstance(process.get("pid"), int)):
                raise AdapterError("herdr_protocol_invalid", "ordinary command process pid is malformed")
            child["command_pid"] = process.get("pid")
        child["command_argv_sha256"] = digest_json(cast(JsonValue, expected_argv))
        child["command_cwd"] = job["cwd"]
        state["resources"] = as_object(value_at(state, "resources"), "state resources")
        state["command_observation"] = {
            "state": observation.get("state", "exited" if exit_value is not None else "running"),
            "exit_code": exit_value,
            "process": process if isinstance(process, dict) else None,
            "output": safe_preview(str(observation.get("output", ""))) if observation.get("output") is not None else "",
            "stderr": safe_preview(str(observation.get("stderr", ""))) if observation.get("stderr") is not None else "",
        }

    def command_start(self) -> JsonObject:
        state = self.state()
        if state.get("phase") == "allocated":
            self.shell_ready()
            state = self.state()
        if state.get("phase") not in {"shell-ready"}:
            raise AdapterError("adapter_state_invalid", "command start requires a proven shell-readiness transition")
        if state.get("command_started") is True:
            raise AdapterError("command_start_already_attempted", "ordinary command startup is single-submit; use resume or cleanup")
        resources, child = self.active_command_child(state)
        pane_id = string_at(child, "pane_id")
        job = self.command_job
        if job is None:
            raise AdapterError("controller_binding_required", "ordinary command projection is unavailable")
        state["command_started"] = True
        state["phase"] = "command-start-attempted"
        start_marker, marker = self.command_markers()
        command_text, wrapper_argv = self.command_text(
            cast(list[str], job["argv"]), start_marker, marker
        )
        state["command_start_marker"] = start_marker
        state["command_marker"] = marker
        state["command_text_sha256"] = hashlib.sha256(command_text.encode()).hexdigest()
        self.event(
            state,
            "command-start-attempt",
            {"pane_id": pane_id, "argv_sha256": digest_json(cast(JsonValue, job["argv"]))},
        )
        self.save_state(state)
        try:
            timeout_seconds = positive_int(value_at(job, "timeout_seconds"), "command timeout")
            self.text_command(
                ["pane", "run", pane_id, command_text],
                timeout_seconds=10,
            )
            self.text_command(
                [
                    "pane", "wait-output", pane_id, "--match", start_marker,
                    "--source", "recent-unwrapped", "--timeout",
                    str(min(timeout_seconds, 5) * 1000),
                ],
                timeout_seconds=min(timeout_seconds, 5) + 5,
            )
            command_pid = self.command_start_pid(pane_id, start_marker)
            child["command_pid"] = command_pid
            child["command_process_argv_sha256"] = digest_json(
                cast(JsonValue, wrapper_argv)
            )
            state["command_observation"] = {
                "state": "running",
                "exit_code": None,
                "process": {
                    "pane_id": pane_id,
                    "pid": command_pid,
                    "argv": job["argv"],
                    "argv_sha256": digest_json(cast(JsonValue, job["argv"])),
                    "wrapper_argv_sha256": child["command_process_argv_sha256"],
                },
                "output": "",
                "stderr": "",
            }
            state["resources"] = resources
            self.save_state(state)
            self.text_command(
                [
                    "pane",
                    "wait-output",
                    pane_id,
                    "--match",
                    marker,
                    "--source",
                    "recent-unwrapped",
                    "--timeout",
                    str(timeout_seconds * 1000),
                ],
                timeout_seconds=timeout_seconds + 5,
            )
        except AdapterError as exc:
            state["command_state"] = "timeout" if exc.code in {"herdr_command_timeout", "command_timeout"} else "unknown"
            self.mark_cleanup_pending(state, "command_run_failed")
            if exc.code == "herdr_command_timeout":
                raise AdapterError("command_timeout", "bounded ordinary command run timed out") from exc
            raise
        try:
            exit_code = self.command_exit_code(pane_id, marker)
        except AdapterError:
            self.mark_cleanup_pending(state, "command_exit_observation_failed")
            raise
        observation: JsonObject = {
            "pane_id": pane_id,
            "cwd": string_at(job, "cwd"),
            "argv": job["argv"],
            "state": "exited",
            "exit_code": exit_code,
            "process": {
                "pane_id": pane_id,
                "pid": child.get("command_pid"),
                "argv": job["argv"],
                "argv_sha256": digest_json(cast(JsonValue, job["argv"])),
                "wrapper_argv_sha256": child.get("command_process_argv_sha256"),
            },
        }
        try:
            self.command_observation(state, observation)
        except AdapterError:
            self.mark_cleanup_pending(state, "command_identity_failed")
            raise
        state["phase"] = "command-started"
        command_observation = as_object(
            value_at(state, "command_observation"), "command observation"
        )
        state["command_state"] = str(command_observation.get("state", "running"))
        state["resources"] = resources
        self.event(state, "command-start", {"pane_id": pane_id, "state": state["command_state"]})
        self.save_state(state)
        self.touch_lease_member("command-started")
        return self.output(state)

    def command_wait(self, timeout_seconds: int) -> JsonObject:
        state = self.state()
        if state.get("phase") not in {"command-started", "command-waiting"}:
            raise AdapterError("adapter_state_invalid", "command wait requires a submitted command")
        if not 1 <= timeout_seconds <= MAX_COMMAND_TIMEOUT_SECONDS:
            raise AdapterError("command_timeout_invalid", "command wait timeout is outside bounded range")
        _, child = self.active_command_child(state)
        pane_id = string_at(child, "pane_id")
        try:
            process_info = self.pane_process_info(pane_id)
        except AdapterError:
            state["command_state"] = "unknown"
            self.mark_cleanup_pending(state, "command_observation_failed")
            raise
        process_values = process_info.get("foreground_processes", [])
        processes = process_values if isinstance(process_values, list) else []
        command_pid = child.get("command_pid")
        running = isinstance(command_pid, int) and any(
            isinstance(item, dict) and item.get("pid") == command_pid for item in processes
        )
        observation = as_object(state.get("command_observation", {}), "command observation")
        if running:
            observation["state"] = "running"
            state["command_state"] = "running"
        else:
            observation["state"] = "exited"
            state["command_state"] = "exited"
        state["command_observation"] = observation
        state["phase"] = "command-waiting"
        self.event(state, "command-wait", {"pane_id": pane_id, "state": state["command_state"], "timeout_seconds": timeout_seconds})
        self.save_state(state)
        self.touch_lease_member("command-waiting")
        return self.output(state)

    def command_collect(self) -> JsonObject:
        state = self.state()
        if state.get("phase") not in {"command-started", "command-waiting", "command-collected"}:
            raise AdapterError("adapter_state_invalid", "command collect requires an observed command")
        _, child = self.active_command_child(state)
        pane_id = string_at(child, "pane_id")
        raw_output = self.text_command(
            ["pane", "read", pane_id, "--source", "recent-unwrapped", "--lines", "120", "--format", "text"],
            timeout_seconds=10,
        )
        job = self.command_job
        if job is None:
            raise AdapterError("controller_binding_required", "ordinary command projection is unavailable")
        output_bound_bytes = positive_int(
            value_at(job, "output_bound_bytes"), "command output bound"
        )
        bound_output = bounded_utf8_preview(raw_output, output_bound_bytes)
        observation = as_object(state.get("command_observation", {}), "command observation")
        exit_code = observation.get("exit_code")
        process = observation.get("process")
        evidence: JsonObject = {
            "kind": "ordinary-command",
            "pane_id": pane_id,
            "process": process if isinstance(process, dict) else None,
            "process_argv_sha256": child.get("command_argv_sha256"),
            "output_sha256": hashlib.sha256(raw_output.encode()).hexdigest(),
            "output_preview": bound_output,
            "output_bound_bytes": output_bound_bytes,
            "exit_code": exit_code,
            "oracle_judgment_required": True,
            "task_success_claim": False,
        }
        state["phase"] = "command-collected"
        state["command_state"] = "exited" if exit_code is not None else state.get("command_state", "unknown")
        state["evidence"] = [evidence]
        self.event(state, "command-collect", {"pane_id": pane_id, "exit_code": exit_code, "output_sha256": evidence["output_sha256"]})
        self.save_state(state)
        self.touch_lease_member("command-collected")
        return self.output(state)

    def pane_inventory(self) -> list[JsonObject]:
        return result_panes(
            self.command(["pane", "list", "--workspace", self.context["workspace_id"]])
        )

    def pane_record_is_owned(
        self, pane: JsonObject, record: JsonObject, *, require_agent: bool = False
    ) -> bool:
        pane_id = record.get("pane_id")
        if (
            not isinstance(pane_id, str)
            or pane.get("pane_id") != pane_id
            or pane.get("terminal_id") != record.get("terminal_id")
            or pane.get("workspace_id") != self.context["workspace_id"]
        ):
            return False
        expected_shell_pid = record.get("shell_pid")
        if (
            isinstance(expected_shell_pid, bool)
            or not isinstance(expected_shell_pid, int)
            or expected_shell_pid < 1
        ):
            return False
        process_info = self.pane_process_info(pane_id)
        if process_info.get("shell_pid") != expected_shell_pid:
            return False
        processes = process_info.get("foreground_processes")
        if not isinstance(processes, list):
            return False
        command_pid = record.get("command_pid")
        command_digest = record.get("command_process_argv_sha256")
        command_seen = False
        if isinstance(command_pid, int) and isinstance(command_digest, str):
            for process in processes:
                if (
                    isinstance(process, dict)
                    and process.get("pid") == command_pid
                    and isinstance(process.get("argv"), list)
                    and digest_json(cast(JsonValue, process["argv"])) == command_digest
                ):
                    command_seen = True
                    break
        expected_kind = record.get("agent_kind")
        expected_argv_sha256 = record.get("agent_argv_sha256")
        if isinstance(expected_kind, str) and isinstance(expected_argv_sha256, str):
            for process in processes:
                if (
                    not isinstance(process, dict)
                    or process.get("name") != expected_kind
                ):
                    continue
                argv = process.get("argv")
                if (
                    isinstance(argv, list)
                    and digest_json(cast(JsonValue, argv)) == expected_argv_sha256
                ):
                    expected_session = record.get("agent_session_id")
                    observed_session = pane.get("agent_session")
                    if (
                        isinstance(expected_session, str)
                        and expected_session
                        and (
                            not isinstance(observed_session, dict)
                            or observed_session.get("value") != expected_session
                        )
                    ):
                        return False
                    return pane.get("agent") == expected_kind
            if pane.get("agent") is not None:
                return False
            if require_agent:
                return False
        return all(
            isinstance(process, dict)
            and (
                process.get("pid") == expected_shell_pid
                or (command_seen and process.get("pid") == command_pid)
                or (
                    process.get("name") in {"starship", "mise"}
                    and isinstance(process.get("argv"), list)
                    and process.get("argv", [])[:2] == ["starship", "init"]
                )
            )
            for process in processes
        )

    def resume(self) -> JsonObject:
        state = self.state()
        state_controller = as_object(value_at(state, "controller"), "state controller")
        state_provenance = as_object(value_at(state, "provenance"), "state provenance")
        if string_at(state_controller, "run_id") != self.run_id:
            raise AdapterError("restart_mismatch", "run identity changed")
        if (
            string_at(state_controller, "run_nonce_sha256")
            != hashlib.sha256(
                string_at(self.controller, "run_nonce").encode()
            ).hexdigest()
        ):
            raise AdapterError("restart_mismatch", "controller nonce changed")
        if string_at(state_provenance, "canonical_repository") != str(self.repo):
            raise AdapterError("restart_mismatch", "repository identity changed")
        for key in ("repository_revision", "plan_sha256", "ledger_sha256"):
            if string_at(state_provenance, key) != string_at(self.provenance, key):
                raise AdapterError("restart_mismatch", f"{key} changed")
        state_task = as_object(value_at(state, "task"), "state task")
        if string_at(state_task, "task_id") != string_at(
            self.task, "task_id"
        ) or state_task.get("attempt") != self.task.get("attempt"):
            raise AdapterError("restart_mismatch", "task projection changed")
        if state_task.get("resource_locks", []) != self.member_resource_locks():
            raise AdapterError("restart_mismatch", "resource lock projection changed")
        if self.binding_kind == "command-job":
            state_command = as_object(value_at(state, "command_job"), "state command job")
            current_command = self.command_job
            if current_command is None or state_command.get("cwd") != current_command.get("cwd"):
                raise AdapterError("restart_mismatch", "command cwd changed")
            if state_command.get("argv_sha256") != digest_json(cast(JsonValue, current_command["argv"])):
                raise AdapterError("restart_mismatch", "command argv changed")
            if state_command.get("resource_locks") != current_command.get("resource_locks"):
                raise AdapterError("restart_mismatch", "command resource locks changed")
        state_batch = as_object(value_at(state, "batch"), "state batch")
        if digest_json(cast(JsonValue, state_batch)) != digest_json(cast(JsonValue, self.batch)):
            raise AdapterError("restart_mismatch", "batch projection changed")
        if state.get("member_id") != self.member_id:
            raise AdapterError("restart_mismatch", "run-member identity changed")
        if state.get("physical_binding_sha256") != digest_json(
            cast(JsonValue, self.physical)
        ):
            raise AdapterError("restart_mismatch", "physical binding changed")
        readiness = state.get("shell_readiness")
        if state.get("phase") in {"shell-ready", "started", "prompted", "waiting", "collected", "command-start-attempted", "command-started", "command-waiting", "command-collected"} and (
            not isinstance(readiness, dict) or readiness.get("state") != "ready"
        ):
            raise AdapterError("restart_mismatch", "shell-readiness proof is missing")
        resources = as_object(value_at(state, "resources"), "state resources")
        if (
            resources.get("workspace_id") != self.context["workspace_id"]
            or resources.get("caller_tab_id") != self.context["tab_id"]
            or resources.get("caller_pane_id") != self.context["pane_id"]
        ):
            raise AdapterError("restart_mismatch", "caller context changed")
        state_caller = as_object(
            value_at(state, "caller_context"), "state caller context"
        )
        live_caller = self.validate_caller_resources()
        if live_caller != state_caller:
            raise AdapterError("restart_mismatch", "live caller identity changed")
        expected_lease_state = state.get("lease_state")
        allowed_lease_states = frozenset({"active", "cleanup-pending", "released"})
        with self.lease_lock():
            lease = self.owned_lease(allowed_lease_states)
            member = self.lease_member(lease)
            if member.get("lease_state") != expected_lease_state:
                raise AdapterError(
                    "restart_mismatch", "run-member lease state differs from adapter state"
                )
        if state.get("phase") == "released":
            return self.output(state)
        tab_id = resources.get("owned_tab_id")
        if tab_id is None:
            return self.output(state)
        if not isinstance(tab_id, str) or not tab_id:
            raise AdapterError("restart_mismatch", "owned tab identity is malformed")
        tab = result_entity(self.command(["tab", "get", tab_id]), "tab")
        if (
            tab.get("tab_id") != tab_id
            or tab.get("workspace_id") != self.context["workspace_id"]
        ):
            raise AdapterError("restart_mismatch", "owned tab identity changed")
        current = {
            pane.get("pane_id"): pane
            for pane in self.pane_inventory()
            if pane.get("tab_id") == tab_id and isinstance(pane.get("pane_id"), str)
        }
        owned_records = [
            item
            for item in list_at(resources, "owned_panes")
            if isinstance(item, dict) and item.get("closed") is False
        ]
        owned_ids = {item.get("pane_id") for item in owned_records}
        if set(current) != owned_ids:
            raise AdapterError("restart_mismatch", "owned pane inventory changed")
        if any(
            not self.pane_record_is_owned(
                current[item["pane_id"]],
                item,
                require_agent=state.get("phase")
                in {"started", "prompted", "waiting", "collected"},
            )
            for item in owned_records
            if isinstance(item.get("pane_id"), str)
        ):
            raise AdapterError("restart_mismatch", "owned pane identity changed")
        return self.output(state)

    def cleanup(self) -> JsonObject:
        state = self.state()
        state_caller = as_object(
            value_at(state, "caller_context"), "state caller context"
        )
        live_caller = self.validate_caller_resources()
        if live_caller != state_caller:
            raise AdapterError(
                "cleanup_identity_mismatch", "live caller identity changed"
            )
        resources = as_object(value_at(state, "resources"), "state resources")
        tab_id_value = resources.get("owned_tab_id")
        if not isinstance(tab_id_value, str) or not tab_id_value:
            self.release_lease()
            state["lease_state"] = "released"
            state["phase"] = "released"
            self.save_state(state)
            return self.output(state)
        tab_id = tab_id_value
        current_panes = [
            pane for pane in self.pane_inventory() if pane.get("tab_id") == tab_id
        ]
        owned_records = [
            item for item in list_at(resources, "owned_panes") if isinstance(item, dict)
        ]
        owned_ids = {
            item.get("pane_id")
            for item in owned_records
            if isinstance(item.get("pane_id"), str)
        }
        current_by_id = {
            item.get("pane_id"): item
            for item in current_panes
            if isinstance(item.get("pane_id"), str)
        }
        current_ids = set(current_by_id)
        if not current_ids:
            for item in owned_records:
                item["closed"] = True
            resources["owned_panes"] = owned_records
            state["resources"] = resources
            self.release_lease()
            state["phase"] = "released"
            state["lease_state"] = "released"
            self.event(state, "cleanup", {"tab_closed": True, "residue": False})
            self.save_state(state)
            return self.output(state)
        tab = result_entity(self.command(["tab", "get", tab_id]), "tab")
        if (
            tab.get("workspace_id") != self.context["workspace_id"]
            or tab.get("tab_id") != tab_id
        ):
            raise AdapterError(
                "cleanup_identity_mismatch", "owned tab identity cannot be proven"
            )
        current_ids = {
            item.get("pane_id")
            for item in current_panes
            if isinstance(item.get("pane_id"), str)
        }
        unknown_ids = current_ids - owned_ids
        safe_ids = {
            pane_id
            for pane_id, pane in current_by_id.items()
            for record in owned_records
            if record.get("pane_id") == pane_id
            and self.pane_record_is_owned(pane, record)
        }
        ambiguous_ids = (current_ids & owned_ids) - safe_ids
        if not unknown_ids and not ambiguous_ids and current_ids == owned_ids:
            self.command(["tab", "close", tab_id])
            remaining = {
                pane.get("pane_id")
                for pane in self.pane_inventory()
                if pane.get("tab_id") == tab_id
            }
            if remaining & owned_ids:
                raise AdapterError(
                    "cleanup_identity_mismatch", "owned panes remain after tab close"
                )
            for item in owned_records:
                item["closed"] = True
            state["phase"] = "released"
            state["lease_state"] = "released"
            resources["owned_panes"] = owned_records
            state["resources"] = resources
            self.event(state, "cleanup", {"tab_closed": True, "residue": False})
            self.release_lease()
            self.save_state(state)
            return self.output(state)
        residue: list[str] = sorted(str(item) for item in unknown_ids | ambiguous_ids)
        for item in owned_records:
            pane_id = item.get("pane_id")
            if not isinstance(pane_id, str) or pane_id not in current_ids:
                item["closed"] = True
                continue
            if pane_id not in safe_ids:
                continue
            try:
                self.command(["pane", "close", pane_id])
                item["closed"] = True
            except AdapterError:
                residue.append(pane_id)
        still_owned = [
            item
            for item in owned_records
            if item.get("closed") is not True and item.get("pane_id") in current_ids
        ]
        state["phase"] = "cleanup-pending"
        state["lease_state"] = "cleanup-pending" if still_owned else "released"
        resources["owned_panes"] = owned_records
        state["resources"] = resources
        state["cleanup_residue"] = residue + [
            str(item.get("pane_id"))
            for item in still_owned
            if item.get("pane_id") is not None
        ]
        self.event(
            state,
            "cleanup",
            {"tab_closed": False, "residue": bool(state["cleanup_residue"])},
        )
        if not still_owned:
            self.release_lease()
        else:
            self.update_lease_state("cleanup-pending")
        self.save_state(state)
        return self.output(state)

    def update_lease_state(self, lease_state: str) -> None:
        self.update_lease_member(lease_state)

    def release_lease(self) -> None:
        self.update_lease_member("released", phase="released")


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument(
        "command",
        choices=(
            "preflight",
            "allocate",
            "shell-ready",
            "shell-readiness",
            "ready",
            "start",
            "run",
            "command-start",
            "command-run",
            "prompt",
            "wait",
            "command-wait",
            "collect",
            "command-collect",
            "resume",
            "recover",
            "cleanup",
        ),
    )
    argument_parser.add_argument("--envelope", required=True, type=Path)
    argument_parser.add_argument("--herdr-executable", required=True, type=Path)
    argument_parser.add_argument("--prompt", default=None)
    argument_parser.add_argument("--timeout-seconds", type=int, default=60)
    return argument_parser


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        adapter = Adapter(args.envelope, args.herdr_executable)
        if args.command == "preflight":
            result = adapter.preflight()
        elif args.command == "allocate":
            result = adapter.allocate()
        elif args.command in {"shell-ready", "shell-readiness", "ready"}:
            result = adapter.shell_ready(args.timeout_seconds)
        elif args.command in {"start", "run", "command-start", "command-run"}:
            result = adapter.start()
        elif args.command == "prompt":
            if not isinstance(args.prompt, str):
                raise AdapterError("prompt_invalid", "--prompt is required")
            result = adapter.prompt(args.prompt)
        elif args.command in {"wait", "command-wait"}:
            result = adapter.wait(args.timeout_seconds)
        elif args.command in {"collect", "command-collect"}:
            result = adapter.collect()
        elif args.command in {"resume", "recover"}:
            result = adapter.resume()
        else:
            result = adapter.cleanup()
    except AdapterError as exc:
        print(
            json.dumps(
                {"ok": False, "error": {"code": exc.code, "message": exc.message}},
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
