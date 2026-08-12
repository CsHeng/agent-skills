#!/usr/bin/env python3
"""Deterministic, lower-plane Herdr resource adapter for approved task envelopes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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
MAX_PROMPT_CHARS: Final = 200_000
MAX_COMMAND_OUTPUT_BYTES: Final = 64 * 1024
MAX_EVIDENCE_CHARS: Final = 8 * 1024
MAX_WAIT_SECONDS: Final = 15 * 60
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
FORBIDDEN_KEY_RE: Final = re.compile(
    r"(?:secret|token|password|api[_-]?key|prompt)", re.IGNORECASE
)
REDACTION_RE: Final = re.compile(
    r"(?i)(?:bearer\s+|token\s+|password\s*[=:]\s*|api[_-]?key\s*[=:]\s*)\S+"
)
EFFORT_RANK: Final = {"low": 0, "medium": 1, "high": 2, "xhigh": 3}
WORKER_BASELINES: Final = {"codex": "xhigh", "grok": "high"}
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
        if value_at(lease, "schema_version") != SCHEMA_VERSION:
            raise ValueError("schema")
        if string_at(lease, "artifact_kind") != "herdr-execution-lease":
            raise ValueError("kind")
        if string_at(lease, "lease_state") not in allowed_states:
            raise ValueError("state")
        if string_at(lease, "repository") != str(repository):
            raise ValueError("repository")
        if string_at(lease, "git_common_dir_sha256") != git_common_dir_key(common_dir):
            raise ValueError("git common directory")
        require_sha256(string_at(lease, "plan_sha256"), "lease plan_sha256")
        require_sha256(string_at(lease, "run_nonce_sha256"), "lease run_nonce_sha256")
        string_at(lease, "run_id")
        string_at(lease, "workspace_id")
        string_at(lease, "controller_id")
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


def validate_released_lease(path: Path, repository: Path, common_dir: Path) -> None:
    """Allow replacing only a complete released lease for this Git identity."""
    validate_lease_file(
        path,
        repository,
        common_dir,
        allowed_states=frozenset({"released"}),
    )


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
    if effort not in EFFORT_RANK:
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
    baseline = WORKER_BASELINES[kind]
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
        if EFFORT_RANK[effort] >= EFFORT_RANK[baseline]:
            raise AdapterError(
                "delegated_capability_unavailable",
                "semantic-routing explorer effort must be strictly below its worker baseline",
            )
        return {
            "status": "downgraded",
            "model_policy": policy,
            "reasoning_effort": effort,
            "worker_baseline": baseline,
            "relative_to": "worker-default",
        }
    return {
        "status": "explicit-policy-exception",
        "model_policy": policy,
        "reasoning_effort": effort,
        "worker_baseline": baseline,
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
    del role
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
    if write_refs and git_dir(checkout) == git_common_directory(checkout):
        raise AdapterError(
            "controller_binding_capability_mismatch",
            "writer checkout must be an isolated worktree",
        )
    if string_at(task, "status") != "ready":
        raise AdapterError(
            "controller_binding_task_not_ready", "selected task is not ready"
        )
    expected_cwd = ensure_directory(checkout, "checkout")
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
        self.profile = native_agent_profile(
            self.role, self.physical, self.controller, self.checkout
        )
        self.context = caller_context(self.physical)
        self.run_root = self.repo / ".herdr-runs"
        self.run_dir = self.run_root / self.run_id
        self.state_path = self.run_dir / "state.json"
        self.lease_path = self.run_root / "lease.json"
        self.lease_identity: JsonObject = {
            "run_id": self.run_id,
            "repository": str(self.repo),
            "workspace_id": self.context["workspace_id"],
            "controller_id": string_at(self.controller, "controller_id"),
            "git_common_dir_sha256": git_common_dir_key(self.common_dir),
            "plan_sha256": string_at(self.provenance, "plan_sha256"),
            "run_nonce_sha256": hashlib.sha256(
                string_at(self.controller, "run_nonce").encode()
            ).hexdigest(),
        }

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
        try:
            lock.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise AdapterError(
                "adapter_state_busy", "repository lease is being updated"
            ) from exc
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
                "repository lease no longer belongs to this run",
            ) from exc

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
                "run ID or repository lease already exists; use resume or cleanup",
            )
        if self.lease_path.exists() or self.lease_path.is_symlink():
            validate_released_lease(self.lease_path, self.repo, self.common_dir)
        live_caller = self.validate_caller_resources()
        with self.lease_lock():
            if self.state_path.exists():
                raise AdapterError(
                    "herdr_execution_conflict",
                    "run ID or repository lease already exists; use resume or cleanup",
                )
            if self.lease_path.exists() or self.lease_path.is_symlink():
                validate_released_lease(self.lease_path, self.repo, self.common_dir)
            lease: JsonObject = {
                "schema_version": SCHEMA_VERSION,
                "artifact_kind": "herdr-execution-lease",
                "lease_state": "active",
                **self.lease_identity,
            }
            self.write_json(self.lease_path, lease)
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
            },
            "caller_context": live_caller,
            "task": {
                "task_id": string_at(self.task, "task_id"),
                "attempt": value_at(self.task, "attempt"),
                "runtime_role": self.role,
                "touch_set": list_at(self.task, "touch_set"),
                "oracle_refs": list_at(self.task, "oracle_refs"),
            },
            "physical_binding": {
                "terminal_backend": string_at(self.physical, "terminal_backend"),
                "agent_kind": string_at(self.physical, "agent_kind"),
                "agent_name": string_at(self.physical, "agent_name"),
                "model": string_at(self.physical, "model"),
                "reasoning_effort": string_at(self.physical, "reasoning_effort"),
                "permission_mode": string_at(self.physical, "permission_mode"),
                "sandbox_mode": string_at(self.physical, "sandbox_mode"),
                "capability_profile": string_at(self.physical, "capability_profile"),
                "control_plane_endpoint": string_at(
                    self.physical, "control_plane_endpoint"
                ),
                "credential_ref": string_at(self.physical, "credential_ref"),
                "checkout_path": str(self.checkout),
                "explorer_downgrade": self.explorer_downgrade(),
                "model_policy": string_at(self.controller, "model_policy"),
                "profile_id": string_at(self.profile, "profile_id"),
                "native_argv_sha256": digest_json(
                    value_at(self.profile, "native_args")
                ),
                "environment_policy": string_at(self.profile, "environment_policy"),
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
            "prompt_submitted": False,
            "events": [],
            "evidence": [],
        }
        self.save_state(state)
        return self.output(state)

    def explorer_downgrade(self) -> JsonObject:
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
        resources["agent_name"] = string_at(self.physical, "agent_name")
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
            self.update_lease_state("cleanup-pending")

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
        state = self.state()
        if state.get("phase") != "allocated":
            raise AdapterError(
                "adapter_state_invalid", "start requires allocated state"
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
        try:
            response = self.command(
                [
                    "agent",
                    "start",
                    agent_name,
                    "--kind",
                    string_at(self.physical, "agent_kind"),
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
        result = result_object(response)
        agent = result_entity(response, "agent")
        kind = string_at(self.physical, "agent_kind")
        if (
            agent.get("agent") != kind
            or agent.get("name") != agent_name
            or agent.get("pane_id") != child_pane_id
            or agent.get("tab_id") != resources.get("owned_tab_id")
            or agent.get("workspace_id") != self.context["workspace_id"]
            or agent.get("terminal_id") != child.get("terminal_id")
        ):
            self.mark_cleanup_pending(state, "agent_identity_mismatch")
            raise AdapterError(
                "herdr_identity_mismatch", "started agent identity differs"
            )
        argv = result.get("argv")
        if argv != [kind, *native_args]:
            self.mark_cleanup_pending(state, "agent_argv_mismatch")
            raise AdapterError(
                "delegated_capability_unavailable",
                "Herdr did not start the exact validated native argv",
            )
        process_info = self.pane_process_info(child_pane_id)
        processes = process_info.get("foreground_processes")
        matching_process: JsonObject | None = None
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
            self.mark_cleanup_pending(state, "agent_process_mismatch")
            raise AdapterError(
                "herdr_identity_mismatch", "started agent process cannot be proven"
            )
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
        return self.output(state)

    def prompt(self, prompt: str) -> JsonObject:
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
        return self.output(state)

    def wait(self, timeout_seconds: int) -> JsonObject:
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
        return self.output(state)

    def collect(self) -> JsonObject:
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
        if state.get("agent_state") in {"blocked", "unknown", "stalled", "timeout"}:
            state["lease_state"] = "cleanup-pending"
        self.save_state(state)
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
        if state.get("physical_binding_sha256") != digest_json(
            cast(JsonValue, self.physical)
        ):
            raise AdapterError("restart_mismatch", "physical binding changed")
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
        allowed_lease_states = (
            frozenset({"released"})
            if expected_lease_state == "released"
            else frozenset({"active", "cleanup-pending"})
        )
        with self.lease_lock():
            lease = self.owned_lease(allowed_lease_states)
            if lease.get("lease_state") != expected_lease_state:
                raise AdapterError(
                    "restart_mismatch", "lease state differs from adapter state"
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
        if lease_state not in {"cleanup-pending", "released"}:
            raise AdapterError(
                "adapter_state_invalid", f"unsupported lease state: {lease_state}"
            )
        allowed = (
            frozenset({"active", "cleanup-pending"})
            if lease_state == "cleanup-pending"
            else frozenset({"active", "cleanup-pending", "released"})
        )
        with self.lease_lock():
            lease = self.owned_lease(allowed)
            lease["lease_state"] = lease_state
            self.write_json(self.lease_path, lease)

    def release_lease(self) -> None:
        self.update_lease_state("released")


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument(
        "command",
        choices=(
            "preflight",
            "allocate",
            "start",
            "prompt",
            "wait",
            "collect",
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
        elif args.command == "start":
            result = adapter.start()
        elif args.command == "prompt":
            if not isinstance(args.prompt, str):
                raise AdapterError("prompt_invalid", "--prompt is required")
            result = adapter.prompt(args.prompt)
        elif args.command == "wait":
            result = adapter.wait(args.timeout_seconds)
        elif args.command == "collect":
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
