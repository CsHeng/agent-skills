#!/usr/bin/env python3
"""Extract skill-improvement signals from Codex, Claude, and Grok history."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import tomllib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote


EXIT_RE = re.compile(r"Process exited with code (\d+)")
DOC_NAMES = {"AGENTS.md", "README.md", "CLAUDE.md"}  # CLAUDE.md is legacy input only.

DOC_OFFLOAD_RE = re.compile(
    r"workflow|validation|troubleshoot|runbook|deploy|commit|skill|agent|"
    r"流程|排障|验证|部署|提交|技能|维护|运行",
    re.I,
)

FAILURE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("pytest_missing", re.compile(r"No module named pytest|Failed to spawn: pytest", re.I)),
    ("pytest_cov_addopts", re.compile(r"unrecognized arguments: --cov|pytest-cov", re.I)),
    ("python_yaml_missing", re.compile(r"No module named ['\"]?yaml|No module named PyYAML", re.I)),
    ("plugin_manifest_missing", re.compile(r"missing `\.codex-plugin/plugin\.json`|missing plugin\.json", re.I)),
    ("zsh_reserved_variable", re.compile(r"read-only variable: (status|path)", re.I)),
    ("rg_needs_pcre2", re.compile(r"look-around.*not supported|enable PCRE2", re.I | re.S)),
    ("path_not_found", re.compile(r"No such file or directory|FileNotFoundError|cannot access|sed: can.t read", re.I)),
    ("not_git_repo", re.compile(r"not a git repository", re.I)),
    ("command_not_found", re.compile(r"command not found", re.I)),
    ("review_artifact_invalid", re.compile(r"run-review\.sh|missing required upstream design|invalid upstream design", re.I)),
    ("permission_boundary", re.compile(r"Permission denied|Operation not permitted|sudo -n|root-owned|sticky", re.I)),
    ("remote_runtime", re.compile(r"timed out|timeout|connection refused|no route to host|100% packet loss", re.I)),
    ("test_assertion", re.compile(r"FAILED .*::|AssertionError|\d+ failed", re.I)),
    ("parse_schema", re.compile(r"parse error|JSON|YAML|jq:", re.I)),
]

USER_SIGNAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("analysis_only", re.compile(r"只分析|先.*分析|不直接改|不要.*改|别.*改|别急.*改")),
    ("wrong_target", re.compile(r"不不不|不是.*(那个|这台|这个|这个repo|这个文件)|另外一台|另外.*repo|你.*看错|搞错")),
    ("scope_rejected", re.compile(r"没必要|别.*提交|不要.*提交|不要.*写|先不处理|这部分先不|别瞎加")),
    ("command_requested", re.compile(r"命令|直接.*命令|怎么.*跑|给我.*command|working command", re.I)),
    ("runtime_evidence", re.compile(r"实际|runtime|线上|现场|不要猜|别猜|log|日志|证据|先查|system log|git log", re.I)),
    ("approval_gate", re.compile(r"^(1|2|yes|yes do it)$|确认|批准|可以提交|只提交", re.I)),
    ("correction", re.compile(r"不对|错了|不应该|应该是|你忘了|失败|报错")),
]

EVENT_NAMES = {
    "turn_aborted",
    "context_compacted",
    "thread_rolled_back",
    "error",
    "task_complete",
}


@dataclass(frozen=True)
class Example:
    source: str
    category: str
    cwd: str
    session_id: str
    file: str
    text: str


@dataclass(frozen=True)
class SkillInventoryEntry:
    name: str
    path: str
    category: str
    disable_model_invocation: bool
    description: str
    declared_implicit_invocation: bool | None
    activation_mode: str
    default_role: str
    codex_allow_implicit_invocation: bool
    codex_policy_source: str
    claude_model_visibility: str
    claude_policy_source: str


@dataclass(frozen=True)
class SkillContractEntry:
    name: str
    source: str
    public_id: str
    category: str
    declared_implicit_invocation: bool | None
    activation_mode: str
    default_role: str
    codex_allow_implicit_invocation: bool | None
    claude_effective_visibility: str


@dataclass(frozen=True)
class SkillUsageRecord:
    source: str
    category: str
    cwd: str
    session_id: str
    file: str
    line: int
    skills: tuple[str, ...]
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mine local agent history for skill-improvement signals.")
    parser.add_argument("--scope", choices=("current", "all"), default="current")
    parser.add_argument("--repo-root", default="")
    parser.add_argument(
        "--codex-home",
        action="append",
        default=None,
        help="Codex home to scan. Repeat for multiple homes; comma-separated values are also accepted.",
    )
    parser.add_argument(
        "--claude-home",
        action="append",
        default=None,
        help="Claude home to scan. Repeat for multiple homes; comma-separated values are also accepted.",
    )
    parser.add_argument(
        "--grok-home",
        action="append",
        default=None,
        help="Grok home to scan (default ~/.grok). Repeat for multiple homes; comma-separated values are also accepted.",
    )
    parser.add_argument(
        "--sources",
        default="codex,codex-memory,claude,claude-memory,grok,context-docs",
        help=(
            "Comma-separated sources: codex,codex-memory,claude,claude-memory,"
            "grok,context-docs."
        ),
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maximum raw examples to emit. Defaults to 0 so session text remains opt-in.",
    )
    parser.add_argument(
        "--skill-usage-root",
        action="append",
        default=None,
        help="Skill bundle or skill root to measure in session history. Repeat for multiple roots.",
    )
    parser.add_argument(
        "--skill-usage-prefix",
        default="",
        help="Skill namespace prefix to count, for example sample-skill-pack.",
    )
    parser.add_argument(
        "--skill-usage-contract",
        default="",
        help="Optional skills.toml contract used to report declared policy separately from provider metadata.",
    )
    parser.add_argument(
        "--skill-usage-before-date",
        default="",
        help="Optional exclusive YYYY-MM-DD cutoff for skill-usage counts.",
    )
    parser.add_argument(
        "--skill-usage-include-output",
        action="store_true",
        help="Include tool output records in skill-usage counts. Default excludes outputs to avoid inventory/listing noise.",
    )
    parser.add_argument(
        "--skill-usage-only",
        action="store_true",
        help="Only emit skill-usage data. Use for fast external-bundle retirement audits.",
    )
    return parser.parse_args()


def resolve_home_args(values: list[str] | None, default: Path) -> list[Path]:
    if not values:
        return [default.expanduser()]

    homes: list[Path] = []
    seen: set[Path] = set()
    for value in values:
        for part in value.split(","):
            stripped = part.strip()
            if not stripped:
                continue
            home = Path(stripped).expanduser()
            if home in seen:
                continue
            seen.add(home)
            homes.append(home)
    return homes or [default.expanduser()]


def git_root(path: Path) -> Path:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return path.resolve()
    return Path(output).resolve()


def is_in_scope(cwd: str, repo_root: Path, scope: str) -> bool:
    if scope == "all":
        return True
    if not cwd or cwd == "(unknown)":
        return False
    try:
        Path(cwd).resolve().relative_to(repo_root)
    except (OSError, ValueError):
        return False
    return True


def flatten_text(value: Any) -> str:
    parts: list[str] = []

    def walk(item: Any) -> None:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, list):
            for child in item:
                walk(child)
        elif isinstance(item, dict):
            for key in ("text", "input_text", "content", "message", "result", "toolUseResult"):
                if key in item:
                    walk(item[key])

    walk(value)
    return "\n".join(part for part in parts if part)


def skip_injected_text(text: str) -> bool:
    return bool(
        ("# AGENTS.md instructions" in text and len(text) > 1000)
        or ("<skill>" in text and "</skill>" in text and len(text) > 100)
        or ("<INSTRUCTIONS>" in text and len(text) > 1000)
        or ("<skills_instructions>" in text and len(text) > 1000)
        or ("### Available skills" in text and len(text) > 1000)
    )


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for raw_line in text[4:end].splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def load_skill_contract(
    contract_path: Path | None,
) -> tuple[dict[Path, SkillContractEntry], dict[str, SkillContractEntry]]:
    if contract_path is None:
        return {}, {}
    resolved_contract = contract_path.expanduser().resolve()
    try:
        with resolved_contract.open("rb") as handle:
            contract = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}, {}

    repo_root = resolved_contract.parent.parent
    mode_projections = contract.get("activation_modes") or {}
    by_source: dict[Path, SkillContractEntry] = {}
    by_name: dict[str, SkillContractEntry] = {}
    for name, raw_entry in (contract.get("skills") or {}).items():
        if not isinstance(raw_entry, dict):
            continue
        source = str(raw_entry.get("source") or "")
        public_id = str(raw_entry.get("public_id") or name)
        declared = raw_entry.get("implicit_invocation")
        if not isinstance(declared, bool):
            declared = None
        activation_mode = str(raw_entry.get("activation_mode") or "")
        mode_projection = (
            mode_projections.get(activation_mode)
            if isinstance(mode_projections, dict)
            else None
        )
        if not isinstance(mode_projection, dict):
            mode_projection = {}
        projected_codex = mode_projection.get("codex_allow_implicit_invocation")
        if not isinstance(projected_codex, bool):
            projected_codex = None
        if declared is None and projected_codex is not None:
            declared = projected_codex
        entry = SkillContractEntry(
            name=str(name),
            source=source,
            public_id=public_id,
            category=str(raw_entry.get("category") or ""),
            declared_implicit_invocation=declared,
            activation_mode=activation_mode,
            default_role=str(raw_entry.get("default_role") or ""),
            codex_allow_implicit_invocation=projected_codex,
            claude_effective_visibility=str(
                mode_projection.get("claude_effective_visibility") or ""
            ),
        )
        by_name[entry.name] = entry
        by_name[entry.public_id] = entry
        if source:
            by_source[(repo_root / source / "SKILL.md").resolve()] = entry
    return by_source, by_name


def read_codex_source_policy(skill_path: Path) -> tuple[bool, str]:
    metadata_path = skill_path.parent / "agents" / "openai.yaml"
    try:
        text = metadata_path.read_text(errors="replace")
    except OSError:
        return True, "provider-default"

    in_policy = False
    policy_indent = 0
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip())
        if stripped == "policy:":
            in_policy = True
            policy_indent = indent
            continue
        if in_policy and indent <= policy_indent:
            in_policy = False
        if in_policy and stripped.startswith("allow_implicit_invocation:"):
            value = stripped.split(":", 1)[1].strip().lower()
            if value in {"true", "false"}:
                return value == "true", "source-metadata"
    return True, "provider-default"


def infer_inventory_category(rel_path: Path) -> str:
    parts = rel_path.parts
    if len(parts) >= 4 and parts[0] == "skills":
        return parts[1]
    if len(parts) >= 3:
        return parts[0]
    return ""


def iter_skill_inventory(
    paths: list[Path],
    contract_path: Path | None = None,
) -> dict[str, SkillInventoryEntry]:
    entries: dict[str, SkillInventoryEntry] = {}
    contract_by_source, contract_by_name = load_skill_contract(contract_path)
    for root in paths:
        expanded_root = root.expanduser().resolve()
        if not expanded_root.exists():
            continue
        inventory_root = expanded_root.parent if expanded_root.name == "SKILL.md" else expanded_root
        candidates = [expanded_root] if expanded_root.name == "SKILL.md" else sorted(expanded_root.rglob("SKILL.md"))
        for path in candidates:
            try:
                text = path.read_text(errors="replace")
            except OSError:
                continue
            metadata = parse_frontmatter(text)
            name = metadata.get("name") or path.parent.name
            try:
                rel_path = path.relative_to(inventory_root)
            except ValueError:
                rel_path = path
            contract_entry = contract_by_source.get(path.resolve()) or contract_by_name.get(name)
            category = (
                contract_entry.category
                if contract_entry is not None and contract_entry.category
                else infer_inventory_category(rel_path)
            )
            disable_model_invocation = (
                metadata.get("disable-model-invocation", "").lower() == "true"
            )
            codex_allow_implicit_invocation, codex_policy_source = read_codex_source_policy(path)
            if (
                contract_entry is not None
                and contract_entry.codex_allow_implicit_invocation is not None
            ):
                codex_allow_implicit_invocation = (
                    contract_entry.codex_allow_implicit_invocation
                )
                codex_policy_source = "contract-derived"
            claude_model_visibility = (
                "disabled" if disable_model_invocation else "default-visible"
            )
            claude_policy_source = (
                "shared-frontmatter" if disable_model_invocation else "provider-default"
            )
            if (
                contract_entry is not None
                and contract_entry.claude_effective_visibility
                and not disable_model_invocation
            ):
                claude_model_visibility = contract_entry.claude_effective_visibility
                claude_policy_source = "contract-effective-state"
            entries[name] = SkillInventoryEntry(
                name=name,
                path=str(rel_path),
                category=category,
                disable_model_invocation=disable_model_invocation,
                description=metadata.get("description", ""),
                declared_implicit_invocation=(
                    contract_entry.declared_implicit_invocation
                    if contract_entry is not None
                    else None
                ),
                activation_mode=contract_entry.activation_mode if contract_entry is not None else "",
                default_role=contract_entry.default_role if contract_entry is not None else "",
                codex_allow_implicit_invocation=codex_allow_implicit_invocation,
                codex_policy_source=codex_policy_source,
                claude_model_visibility=claude_model_visibility,
                claude_policy_source=claude_policy_source,
            )
    return entries


def build_skill_usage_markers(
    skill_prefix: str,
    skill_roots: list[Path],
    inventory: dict[str, SkillInventoryEntry],
) -> tuple[dict[str, tuple[str, ...]], tuple[str, ...]]:
    expanded_roots = [root.expanduser().absolute() for root in skill_roots]
    resolved_roots = [root.resolve() for root in expanded_roots]
    skill_markers: dict[str, tuple[str, ...]] = {}
    for name, entry in inventory.items():
        markers = {
            f"{skill_prefix}:{name}" if skill_prefix else "",
            f"${skill_prefix}:{name}" if skill_prefix else "",
            entry.path,
            f"/{name}/SKILL.md",
        }
        for root in resolved_roots:
            markers.add(str((root / entry.path).resolve()))
        for root in expanded_roots:
            markers.add(str(root / entry.path))
        skill_markers[name] = tuple(marker for marker in sorted(markers) if marker)

    root_markers = {skill_prefix} if skill_prefix else set()
    root_markers.update(str(root) for root in resolved_roots)
    root_markers.update(str(root) for root in expanded_roots)
    return skill_markers, tuple(marker for marker in sorted(root_markers) if marker)


def match_skill_usage_names(
    text: str,
    skill_markers: dict[str, tuple[str, ...]],
    _root_markers: tuple[str, ...],
) -> tuple[str, ...]:
    names: set[str] = set()
    if not text:
        return ()

    for name, markers in skill_markers.items():
        if any(marker and marker in text for marker in markers):
            names.add(name)

    return tuple(sorted(names))


def match_explicit_skill_names(
    text: str,
    skill_prefix: str,
    inventory: dict[str, SkillInventoryEntry],
) -> tuple[str, ...]:
    names: set[str] = set()
    for name in inventory:
        public_name = f"{skill_prefix}:{name}" if skill_prefix else name
        pattern = re.compile(
            rf"(?<![\w:$-])\${re.escape(public_name)}(?![\w-])"
        )
        if pattern.search(text):
            names.add(name)
    return tuple(sorted(names))


def add_skill_usage_record(
    skill_usage_records: list[SkillUsageRecord],
    text: str,
    source: str,
    category: str,
    cwd: str,
    session_id: str,
    file: str,
    line: int,
    skill_markers: dict[str, tuple[str, ...]],
    root_markers: tuple[str, ...],
    skill_prefix: str = "",
    inventory: dict[str, SkillInventoryEntry] | None = None,
    limit_text: int = 300,
) -> None:
    if skip_injected_text(text):
        return
    if category == "user_explicit":
        names = match_explicit_skill_names(text, skill_prefix, inventory or {})
    else:
        names = match_skill_usage_names(text, skill_markers, root_markers)
    if not names:
        return
    skill_usage_records.append(
        SkillUsageRecord(
            source,
            category,
            cwd,
            session_id,
            file,
            line,
            names,
            " ".join(text.split())[:limit_text],
        )
    )


def is_skill_load_call(call_name: str, text: str) -> bool:
    normalized_name = call_name.lower().replace("-", "_")
    return "SKILL.md" in text or normalized_name in {
        "skill",
        "load_skill",
        "read_skill",
    }


def claude_wrapped_tool_payload(obj: dict[str, Any]) -> bool:
    if "toolUseResult" in obj or "hook" in obj:
        return True
    message = obj.get("message") or {}
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return False
    return any(
        isinstance(item, dict)
        and str(item.get("type") or "") in {"tool_result", "tool_use", "hook"}
        for item in content
    )


def claude_text_content(obj: dict[str, Any]) -> str:
    message = obj.get("message") or obj.get("content") or {}
    content = message.get("content") if isinstance(message, dict) else message
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(
        str(item.get("text") or "")
        for item in content
        if isinstance(item, dict) and str(item.get("type") or "text") == "text"
    )


def classify_failure(text: str) -> str:
    for name, pattern in FAILURE_PATTERNS:
        if pattern.search(text):
            return name
    return "other_nonzero"


def unwrap_shell_command(command: str) -> str:
    stripped = command.strip()
    if stripped.startswith("cd ") and "&&" in stripped:
        stripped = stripped.split("&&", 1)[1].strip()
    try:
        parts = shlex.split(stripped)
    except ValueError:
        return stripped
    if len(parts) >= 3 and Path(parts[0]).name in {"bash", "zsh", "sh"}:
        for index, part in enumerate(parts[1:], start=1):
            if "c" in part.lstrip("-") and index + 1 < len(parts):
                return unwrap_shell_command(parts[index + 1])
    return stripped


def is_search_no_match(command: str, output: str, code: int) -> bool:
    stripped = unwrap_shell_command(command)
    tool = stripped.split(maxsplit=1)[0] if stripped else ""
    if tool not in {"rg", "grep", "fd", "find"} or code != 1:
        return False
    error_markers = (
        "error:",
        "No such file or directory",
        "not supported",
        "invalid",
        "regex parse error",
        "permission denied",
    )
    return not any(marker.lower() in output.lower() for marker in error_markers)


def add_example(examples: dict[str, list[Example]], example: Example, limit: int) -> None:
    if limit <= 0:
        return
    bucket = examples[example.category]
    if len(bucket) < limit:
        bucket.append(example)


def iter_jsonl(path: Path) -> Any:
    try:
        with path.open(errors="replace") as handle:
            for line in handle:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def iter_jsonl_with_lines(path: Path) -> Any:
    try:
        with path.open(errors="replace") as handle:
            for line_number, line in enumerate(handle, start=1):
                try:
                    yield line_number, json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def iter_context_doc_paths(repo_root: Path) -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(repo_root), "ls-files", "-z"],
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return sorted(path for path in repo_root.rglob("*") if path.name in DOC_NAMES)

    paths: list[Path] = []
    for raw in output.split(b"\0"):
        if not raw:
            continue
        relative = Path(raw.decode("utf-8", errors="replace"))
        if relative.name in DOC_NAMES:
            paths.append(repo_root / relative)
    return sorted(paths)


def context_doc_reason(path: Path, text: str) -> str:
    lines = text.splitlines()
    line_count = len(lines)
    fence_count = text.count("```") // 2
    workflow_hits = len(DOC_OFFLOAD_RE.findall(text))

    if path.name in {"AGENTS.md", "CLAUDE.md"} and line_count >= 80:
        return "large AI context doc"
    if path.name == "README.md" and line_count >= 160:
        return "large human-facing doc"
    if fence_count >= 4:
        return "many command or code examples"
    if workflow_hits >= 12:
        return "workflow-heavy durable knowledge"
    return ""


def scan_context_docs(
    repo_root: Path,
    counts: Counter[str],
    examples: dict[str, list[Example]],
    limit: int,
) -> None:
    seen_realpaths: set[Path] = set()
    for path in iter_context_doc_paths(repo_root):
        try:
            realpath = path.resolve()
        except OSError:
            continue
        if realpath in seen_realpaths:
            counts["context_doc_symlink_or_duplicate"] += 1
            continue
        seen_realpaths.add(realpath)

        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue

        try:
            rel_path = path.relative_to(repo_root)
        except ValueError:
            rel_path = path
        line_count = text.count("\n") + (1 if text else 0)
        byte_count = len(text.encode("utf-8"))
        counts["context_docs"] += 1
        counts[f"context_doc_name:{path.name}"] += 1
        counts["context_doc_lines"] += line_count
        counts["context_doc_bytes"] += byte_count

        reason = context_doc_reason(path, text)
        if not reason:
            continue
        counts["context_doc_offload_candidate"] += 1
        add_example(
            examples,
            Example(
                "context-doc",
                "context_doc_offload_candidate",
                str(repo_root),
                "",
                str(rel_path),
                f"{rel_path}: {line_count} lines, {byte_count} bytes; {reason}",
            ),
            limit,
        )


def scan_codex_session(
    path: Path,
    repo_root: Path,
    scope: str,
    counts: Counter[str],
    examples: dict[str, list[Example]],
    event_counts: Counter[str],
    limit: int,
) -> None:
    cwd = "(unknown)"
    session_id = ""
    timestamp = ""
    calls: dict[str, tuple[str, dict[str, Any]]] = {}
    pending: list[dict[str, Any]] = []

    for obj in iter_jsonl(path):
        payload = obj.get("payload") or {}
        if obj.get("type") == "session_meta":
            cwd = payload.get("cwd") or cwd
            session_id = payload.get("id") or session_id
            timestamp = payload.get("timestamp") or timestamp
            continue
        pending.append(obj)

    if not is_in_scope(cwd, repo_root, scope):
        return

    counts["sessions_codex"] += 1
    if timestamp:
        counts[f"codex_session_date:{timestamp[:10]}"] += 1

    for obj in pending:
        payload = obj.get("payload") or {}
        obj_type = obj.get("type")
        if obj_type == "event_msg":
            event_type = payload.get("type") or "(unknown)"
            if event_type in EVENT_NAMES:
                event_counts[event_type] += 1
                if event_type == "error":
                    category = "event_error"
                    counts[category] += 1
                    add_example(
                        examples,
                        Example("codex", category, cwd, session_id, path.name, json.dumps(payload, ensure_ascii=False)[:300]),
                        limit,
                    )
            continue

        if obj_type != "response_item":
            continue
        item_type = payload.get("type")
        if item_type == "message" and payload.get("role") == "user":
            text = flatten_text(payload.get("content"))
            if not text or skip_injected_text(text):
                continue
            for name, pattern in USER_SIGNAL_PATTERNS:
                if pattern.search(text.strip()):
                    category = f"user_{name}"
                    counts[category] += 1
                    add_example(examples, Example("codex", category, cwd, session_id, path.name, " ".join(text.split())[:300]), limit)
        elif item_type == "function_call":
            arguments: dict[str, Any] = {}
            try:
                arguments = json.loads(payload.get("arguments") or "{}")
            except json.JSONDecodeError:
                pass
            calls[payload.get("call_id") or ""] = (payload.get("name") or "", arguments)
        elif item_type == "function_call_output":
            raw_output = payload.get("output") or ""
            output = raw_output if isinstance(raw_output, str) else flatten_text(raw_output)
            match = EXIT_RE.search(output)
            if not match or int(match.group(1)) == 0:
                continue
            code = int(match.group(1))
            call_name, arguments = calls.get(payload.get("call_id") or "", ("", {}))
            command = arguments.get("cmd") or arguments.get("command") or call_name
            if is_search_no_match(command, output, code):
                counts["search_no_match"] += 1
                continue
            category = f"failure_{classify_failure(command + chr(10) + output)}"
            counts[category] += 1
            add_example(
                examples,
                Example("codex", category, cwd, session_id, path.name, (command + " | " + " ".join(output.splitlines()[-4:]))[:300]),
                limit,
            )


def scan_claude_session(
    path: Path,
    repo_root: Path,
    scope: str,
    counts: Counter[str],
    examples: dict[str, list[Example]],
    event_counts: Counter[str],
    limit: int,
) -> None:
    objects = list(iter_jsonl(path))
    cwd = "(unknown)"
    session_id = ""
    for obj in objects:
        cwd = obj.get("cwd") or cwd
        session_id = obj.get("sessionId") or session_id
        if cwd != "(unknown)" and session_id:
            break
    if not is_in_scope(cwd, repo_root, scope):
        return

    counts["sessions_claude"] += 1
    for obj in objects:
        obj_type = obj.get("type") or ""
        if obj_type == "user":
            text = flatten_text(obj.get("message") or obj.get("content"))
            if not text or skip_injected_text(text):
                continue
            for name, pattern in USER_SIGNAL_PATTERNS:
                if pattern.search(text.strip()):
                    category = f"user_{name}"
                    counts[category] += 1
                    add_example(examples, Example("claude", category, cwd, session_id, path.name, " ".join(text.split())[:300]), limit)
        blob = json.dumps(obj, ensure_ascii=False)
        if re.search(r'"error"|Permission denied|No such file|command not found|failed|Traceback', blob, re.I):
            category = f"failure_{classify_failure(blob)}"
            counts[category] += 1
            add_example(examples, Example("claude", category, cwd, session_id, path.name, blob[:300]), limit)
        if obj_type in {"error", "summary"}:
            event_counts[f"claude_{obj_type}"] += 1


def grok_workspace_cwd(session_entry_name: str) -> str:
    """Decode Grok sessions/<urlencoded-workspace>/ directory names to a cwd path."""
    return unquote(session_entry_name)


def iter_grok_workspace_dirs(grok_home: Path) -> list[tuple[Path, str]]:
    sessions_root = grok_home / "sessions"
    if not sessions_root.is_dir():
        return []
    workspaces: list[tuple[Path, str]] = []
    for entry in sorted(sessions_root.iterdir()):
        if not entry.is_dir():
            continue
        # Skip non-workspace helpers if any plain names appear without encoding.
        name = entry.name
        if name in {"cache", "tmp"}:
            continue
        cwd = grok_workspace_cwd(name)
        if not cwd.startswith("/"):
            # Encoded paths always start with %2F → "/"; keep absolute only.
            continue
        workspaces.append((entry, cwd))
    return workspaces


def scan_grok_prompt_history(
    path: Path,
    cwd: str,
    counts: Counter[str],
    examples: dict[str, list[Example]],
    event_counts: Counter[str],
    limit: int,
) -> set[str]:
    """Mine Grok repo-level prompt_history.jsonl user prompts. Return session ids seen."""
    session_ids: set[str] = set()
    for obj in iter_jsonl(path):
        if not isinstance(obj, dict):
            continue
        prompt = obj.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            continue
        if obj.get("is_bash") is True:
            event_counts["grok_bash_prompt"] += 1
            continue
        session_id = str(obj.get("session_id") or "")
        if session_id:
            session_ids.add(session_id)
        text = prompt.strip()
        if skip_injected_text(text):
            continue
        for name, pattern in USER_SIGNAL_PATTERNS:
            if pattern.search(text):
                category = f"user_{name}"
                counts[category] += 1
                add_example(
                    examples,
                    Example("grok", category, cwd, session_id, path.name, " ".join(text.split())[:300]),
                    limit,
                )
        timestamp = str(obj.get("timestamp") or "")
        if timestamp:
            counts[f"grok_prompt_date:{timestamp[:10]}"] += 1
    return session_ids


def scan_grok_events(
    path: Path,
    cwd: str,
    session_id: str,
    counts: Counter[str],
    examples: dict[str, list[Example]],
    event_counts: Counter[str],
    limit: int,
) -> None:
    """Mine Grok per-session events.jsonl tool and turn outcomes."""
    for obj in iter_jsonl(path):
        if not isinstance(obj, dict):
            continue
        obj_type = str(obj.get("type") or "")
        if obj_type == "tool_completed":
            outcome = str(obj.get("outcome") or "")
            tool_name = str(obj.get("tool_name") or "")
            if outcome == "error":
                event_counts["grok_tool_error"] += 1
                category = f"failure_{classify_failure(tool_name + ' ' + outcome)}"
                counts[category] += 1
                add_example(
                    examples,
                    Example(
                        "grok",
                        category,
                        cwd,
                        session_id,
                        path.name,
                        f"{tool_name} outcome=error duration_ms={obj.get('duration_ms')}",
                    ),
                    limit,
                )
            elif outcome == "success":
                event_counts["grok_tool_success"] += 1
        elif obj_type == "turn_ended":
            outcome = str(obj.get("outcome") or "")
            event_counts[f"grok_turn_{outcome or 'unknown'}"] += 1
            if outcome in {"cancelled", "error", "failed"}:
                category = "event_error"
                counts[category] += 1
                add_example(
                    examples,
                    Example("grok", category, cwd, session_id, path.name, f"turn_ended outcome={outcome}"),
                    limit,
                )
        elif obj_type == "permission_resolved":
            decision = str(obj.get("decision") or "")
            if decision in {"deny", "denied", "reject", "rejected"}:
                event_counts["grok_permission_denied"] += 1


def scan_grok_home(
    grok_home: Path,
    repo_root: Path,
    scope: str,
    counts: Counter[str],
    examples: dict[str, list[Example]],
    event_counts: Counter[str],
    limit: int,
) -> None:
    for workspace_dir, cwd in iter_grok_workspace_dirs(grok_home):
        if not is_in_scope(cwd, repo_root, scope):
            continue
        seen_sessions: set[str] = set()
        prompt_history = workspace_dir / "prompt_history.jsonl"
        if prompt_history.is_file():
            seen_sessions |= scan_grok_prompt_history(
                prompt_history, cwd, counts, examples, event_counts, limit
            )
        for child in sorted(workspace_dir.iterdir()):
            if not child.is_dir():
                continue
            session_id = child.name
            events = child / "events.jsonl"
            if events.is_file():
                scan_grok_events(events, cwd, session_id, counts, examples, event_counts, limit)
            seen_sessions.add(session_id)
        if seen_sessions:
            counts["sessions_grok"] += len(seen_sessions)
        elif prompt_history.is_file():
            counts["sessions_grok"] += 1


def scan_memory_file(
    path: Path,
    repo_root: Path,
    scope: str,
    counts: Counter[str],
    examples: dict[str, list[Example]],
    limit: int,
) -> None:
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return
    if scope == "current":
        repo_text = str(repo_root)
        encoded_repo = repo_text.replace("/", "-")
        if repo_text in text:
            chunks = re.split(r"(?=^# Task Group:)", text, flags=re.M)
            text = "\n".join(chunk for chunk in chunks if repo_text in chunk)
        elif encoded_repo in str(path):
            pass
        else:
            return
    counts["memory_files"] += 1
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- symptom:"):
            category = "memory_failure_pattern"
            counts[category] += 1
            add_example(examples, Example("memory", category, "(memory)", "", str(path), stripped[:300]), limit)
        elif stripped.startswith("- when the user"):
            category = "memory_user_preference"
            counts[category] += 1
            add_example(examples, Example("memory", category, "(memory)", "", str(path), stripped[:300]), limit)


def scan_codex_skill_usage(
    path: Path,
    repo_root: Path,
    scope: str,
    cutoff_date: str,
    include_output: bool,
    skill_markers: dict[str, tuple[str, ...]],
    root_markers: tuple[str, ...],
    skill_prefix: str,
    inventory: dict[str, SkillInventoryEntry],
    records: list[SkillUsageRecord],
) -> None:
    cwd = "(unknown)"
    session_id = ""
    timestamp = ""
    pending: list[tuple[int, dict[str, Any]]] = []

    for line_number, obj in iter_jsonl_with_lines(path):
        payload = obj.get("payload") or {}
        if obj.get("type") == "session_meta":
            cwd = payload.get("cwd") or cwd
            session_id = payload.get("id") or session_id
            timestamp = payload.get("timestamp") or timestamp
            continue
        pending.append((line_number, obj))

    if cutoff_date and timestamp[:10] >= cutoff_date:
        return
    if not is_in_scope(cwd, repo_root, scope):
        return

    for line_number, obj in pending:
        payload = obj.get("payload") or {}
        if obj.get("type") != "response_item":
            continue
        item_type = payload.get("type")
        if item_type == "message" and payload.get("role") in {"user", "assistant"}:
            role = payload.get("role") or "message"
            text = flatten_text(payload.get("content"))
            add_skill_usage_record(
                records,
                text,
                "codex",
                "user_explicit" if role == "user" else "assistant_reference",
                cwd,
                session_id,
                path.name,
                line_number,
                skill_markers,
                root_markers,
                skill_prefix,
                inventory,
            )
        elif item_type == "function_call":
            arguments: dict[str, Any] = {}
            try:
                arguments = json.loads(payload.get("arguments") or "{}")
            except json.JSONDecodeError:
                pass
            call_name = str(payload.get("name") or "")
            text = json.dumps({"name": call_name, "arguments": arguments}, ensure_ascii=False)
            if not is_skill_load_call(call_name, text):
                continue
            add_skill_usage_record(
                records,
                text,
                "codex",
                "skill_load",
                cwd,
                session_id,
                path.name,
                line_number,
                skill_markers,
                root_markers,
                skill_prefix,
                inventory,
            )
        elif item_type == "function_call_output":
            if not include_output:
                continue
            raw_output = payload.get("output") or ""
            text = raw_output if isinstance(raw_output, str) else flatten_text(raw_output)
            add_skill_usage_record(
                records,
                text,
                "codex",
                "tool_output",
                cwd,
                session_id,
                path.name,
                line_number,
                skill_markers,
                root_markers,
                skill_prefix,
                inventory,
            )


def scan_claude_skill_usage(
    path: Path,
    repo_root: Path,
    scope: str,
    cutoff_date: str,
    include_output: bool,
    skill_markers: dict[str, tuple[str, ...]],
    root_markers: tuple[str, ...],
    skill_prefix: str,
    inventory: dict[str, SkillInventoryEntry],
    records: list[SkillUsageRecord],
) -> None:
    objects = list(iter_jsonl_with_lines(path))
    cwd = "(unknown)"
    session_id = ""
    timestamp = ""
    for _, obj in objects:
        cwd = obj.get("cwd") or cwd
        session_id = obj.get("sessionId") or session_id
        timestamp = obj.get("timestamp") or timestamp
        if cwd != "(unknown)" and session_id and timestamp:
            break

    if cutoff_date and timestamp[:10] >= cutoff_date:
        return
    if not is_in_scope(cwd, repo_root, scope):
        return

    for line_number, obj in objects:
        obj_type = obj.get("type") or ""
        if obj_type == "user":
            if claude_wrapped_tool_payload(obj):
                if not include_output:
                    continue
                category = "tool_output"
                text = json.dumps(obj, ensure_ascii=False)
            else:
                category = "user_explicit"
                text = claude_text_content(obj)
        elif obj_type == "assistant":
            text = claude_text_content(obj)
            if text:
                add_skill_usage_record(
                    records,
                    text,
                    "claude",
                    "assistant_reference",
                    cwd,
                    session_id,
                    path.name,
                    line_number,
                    skill_markers,
                    root_markers,
                    skill_prefix,
                    inventory,
                )
            blob = json.dumps(obj, ensure_ascii=False)
            if claude_wrapped_tool_payload(obj) and is_skill_load_call("", blob):
                add_skill_usage_record(
                    records,
                    blob,
                    "claude",
                    "skill_load",
                    cwd,
                    session_id,
                    path.name,
                    line_number,
                    skill_markers,
                    root_markers,
                    skill_prefix,
                    inventory,
                )
            continue
        elif include_output:
            blob = json.dumps(obj, ensure_ascii=False)
            if "toolUseResult" in blob or "tool_use" in blob or "hook" in blob:
                category = "tool_output"
                text = blob
            else:
                continue
        else:
            continue
        add_skill_usage_record(
            records,
            text,
            "claude",
            category,
            cwd,
            session_id,
            path.name,
            line_number,
            skill_markers,
            root_markers,
            skill_prefix,
            inventory,
        )


def scan_grok_skill_usage(
    path: Path,
    cwd: str,
    session_id: str,
    cutoff_date: str,
    skill_markers: dict[str, tuple[str, ...]],
    root_markers: tuple[str, ...],
    skill_prefix: str,
    inventory: dict[str, SkillInventoryEntry],
    records: list[SkillUsageRecord],
) -> None:
    """Count skill mentions in Grok prompt_history lines."""
    for line_number, obj in iter_jsonl_with_lines(path):
        if not isinstance(obj, dict):
            continue
        if cutoff_date:
            timestamp = str(obj.get("timestamp") or "")
            if timestamp and timestamp[:10] >= cutoff_date:
                continue
        prompt = obj.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            continue
        if obj.get("is_bash") is True:
            continue
        text = prompt.strip()
        if skip_injected_text(text):
            continue
        add_skill_usage_record(
            records,
            text,
            "grok",
            "user_explicit",
            cwd,
            session_id or str(obj.get("session_id") or ""),
            path.name,
            line_number,
            skill_markers,
            root_markers,
            skill_prefix,
            inventory,
        )


def build_skill_usage_report(
    args: argparse.Namespace,
    repo_root: Path,
    sources: set[str],
    codex_homes: list[Path],
    claude_homes: list[Path],
    grok_homes: list[Path] | None = None,
) -> dict[str, Any]:
    skill_roots = [Path(value) for value in args.skill_usage_root or []]
    skill_prefix = args.skill_usage_prefix.strip()
    if not skill_roots and not skill_prefix:
        return {}

    contract_path = (
        Path(args.skill_usage_contract)
        if args.skill_usage_contract.strip()
        else None
    )
    inventory = iter_skill_inventory(skill_roots, contract_path)
    skill_markers, root_markers = build_skill_usage_markers(skill_prefix, skill_roots, inventory)
    records: list[SkillUsageRecord] = []
    grok_homes = grok_homes or []

    if "codex" in sources:
        for codex_home in codex_homes:
            for path in sorted((codex_home / "sessions").rglob("*.jsonl")):
                scan_codex_skill_usage(
                    path,
                    repo_root,
                    args.scope,
                    args.skill_usage_before_date,
                    args.skill_usage_include_output,
                    skill_markers,
                    root_markers,
                    skill_prefix,
                    inventory,
                    records,
                )
    if "claude" in sources:
        for claude_home in claude_homes:
            for path in sorted((claude_home / "projects").rglob("*.jsonl")):
                scan_claude_skill_usage(
                    path,
                    repo_root,
                    args.scope,
                    args.skill_usage_before_date,
                    args.skill_usage_include_output,
                    skill_markers,
                    root_markers,
                    skill_prefix,
                    inventory,
                    records,
                )
    if "grok" in sources:
        for grok_home in grok_homes:
            for workspace_dir, cwd in iter_grok_workspace_dirs(grok_home):
                if not is_in_scope(cwd, repo_root, args.scope):
                    continue
                prompt_history = workspace_dir / "prompt_history.jsonl"
                if prompt_history.is_file():
                    scan_grok_skill_usage(
                        prompt_history,
                        cwd,
                        "",
                        args.skill_usage_before_date,
                        skill_markers,
                        root_markers,
                        skill_prefix,
                        inventory,
                        records,
                    )

    by_category: Counter[str] = Counter()
    by_skill: Counter[str] = Counter()
    by_skill_session: Counter[str] = Counter()
    skill_sessions: dict[str, set[str]] = defaultdict(set)
    session_ids: set[str] = set()

    for record in records:
        by_category[record.category] += 1
        session_key = record.session_id or f"{record.source}:{record.file}"
        session_ids.add(session_key)
        for name in record.skills:
            by_skill[name] += 1
            skill_sessions[name].add(session_key)

    for name, sessions in skill_sessions.items():
        by_skill_session[name] = len(sessions)

    activation_summary: Counter[str] = Counter()
    activation_by_skill: dict[str, Counter[str]] = defaultdict(Counter)
    evidence_by_skill_session: dict[tuple[str, str], set[str]] = defaultdict(set)
    for record in records:
        session_key = record.session_id or f"{record.source}:{record.file}"
        for name in record.skills:
            evidence_by_skill_session[(name, session_key)].add(record.category)
    for (name, _), categories in evidence_by_skill_session.items():
        if "skill_load" not in categories:
            continue
        activation_summary["skill_load_upper_bound"] += 1
        if "user_explicit" in categories:
            activation_category = "explicit_request_with_load"
        else:
            activation_category = "heuristic_inferred"
        activation_summary[activation_category] += 1
        activation_by_skill[name][activation_category] += 1

    inventory_by_category = Counter(entry.category or "(root)" for entry in inventory.values())
    inventory_by_invocation = Counter(
        "disable-model-invocation" if entry.disable_model_invocation else "model-invoked"
        for entry in inventory.values()
    )
    inventory_by_declared_invocation = Counter(
        (
            "declared-implicit"
            if entry.declared_implicit_invocation is True
            else "declared-explicit"
            if entry.declared_implicit_invocation is False
            else "undeclared"
        )
        for entry in inventory.values()
    )
    inventory_by_codex_policy = Counter(
        "allow-implicit" if entry.codex_allow_implicit_invocation else "explicit-only"
        for entry in inventory.values()
    )
    inventory_by_claude_visibility = Counter(
        entry.claude_model_visibility for entry in inventory.values()
    )
    inventory_by_activation_mode = Counter(
        entry.activation_mode or "undeclared" for entry in inventory.values()
    )
    inventory_by_default_role = Counter(
        entry.default_role or "undeclared" for entry in inventory.values()
    )

    return {
        "prefix": skill_prefix,
        "roots": [str(path.expanduser().resolve()) for path in skill_roots],
        "before_date": args.skill_usage_before_date,
        "include_output": args.skill_usage_include_output,
        "inventory_total": len(inventory),
        "inventory_by_category": dict(inventory_by_category),
        "inventory_by_invocation": dict(inventory_by_invocation),
        "inventory_by_declared_invocation": dict(inventory_by_declared_invocation),
        "inventory_by_activation_mode": dict(inventory_by_activation_mode),
        "inventory_by_default_role": dict(inventory_by_default_role),
        "inventory_by_codex_policy": dict(inventory_by_codex_policy),
        "inventory_by_claude_visibility": dict(inventory_by_claude_visibility),
        "records": len(records),
        "sessions": len(session_ids),
        "by_category": dict(by_category),
        "by_skill": dict(by_skill.most_common()),
        "by_skill_session": dict(by_skill_session.most_common()),
        "model_activation_summary": {
            key: activation_summary[key]
            for key in (
                "explicit_request_with_load",
                "heuristic_inferred",
                "skill_load_upper_bound",
            )
        },
        "model_activation_by_skill": {
            name: dict(counts)
            for name, counts in sorted(activation_by_skill.items())
        },
        "inventory": [entry.__dict__ for entry in sorted(inventory.values(), key=lambda item: (item.category, item.name))],
        "examples": [record.__dict__ for record in records[: args.limit if args.limit > 0 else 0]],
    }


def candidate_recommendations(counts: Counter[str]) -> list[str]:
    recommendations: list[str] = []
    if counts["failure_rg_needs_pcre2"]:
        recommendations.append("tool-decision-tree: require rg --pcre2 for lookaround/backreferences and treat rg exit 1 as no-match.")
    if counts["failure_pytest_missing"] or counts["failure_pytest_cov_addopts"]:
        recommendations.append("python-guidelines: preflight pytest dependencies, pytest-cov addopts, and subproject uv environments.")
    if counts["failure_zsh_reserved_variable"]:
        recommendations.append("shell-guidelines: avoid reserved variable names such as status and path in all Shell code.")
    if counts["user_analysis_only"] or counts["user_scope_rejected"]:
        recommendations.append("analyze/execute skills: honor analysis-only and rejected-scope signals before mutating files.")
    if counts["user_approval_gate"] or counts["memory_failure_pattern"]:
        recommendations.append("smart-commit/implement-change: keep explicit approval and completed-write gates machine-checkable.")
    if counts["failure_review_artifact_invalid"]:
        recommendations.append("review-change: validate design_ref/design_version before invoking lower-plane reviewers.")
    if counts["failure_python_yaml_missing"] or counts["failure_plugin_manifest_missing"]:
        recommendations.append("plugin workflows: run validation through uvx --with pyyaml and verify manifests before declaring success.")
    if counts["context_doc_offload_candidate"]:
        recommendations.append("skill-miner/organize-docs: review large or workflow-heavy AGENTS/README docs for skill or reference offload while preserving stable truth summaries.")
    if counts["memory_failure_pattern"] or counts["memory_user_preference"]:
        recommendations.append("skill-miner: extract memory-derived durable facts into repo docs/code/skills, then list corresponding memory cleanup candidates.")
    return recommendations


def print_counter(title: str, counter: Counter[str], prefix: str = "", limit: int = 12) -> None:
    print(f"\n## {title}")
    shown = 0
    for key, value in counter.most_common():
        if value <= 0:
            continue
        if prefix and not key.startswith(prefix):
            continue
        print(f"- {key}: {value}")
        shown += 1
        if shown >= limit:
            break
    if shown == 0:
        print("- none")


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else git_root(Path.cwd())
    sources = {source.strip() for source in args.sources.split(",") if source.strip()}
    codex_homes = resolve_home_args(args.codex_home, Path.home() / ".codex")
    claude_homes = resolve_home_args(args.claude_home, Path.home() / ".claude")
    grok_homes = resolve_home_args(args.grok_home, Path.home() / ".grok")
    counts: Counter[str] = Counter()
    event_counts: Counter[str] = Counter()
    examples: dict[str, list[Example]] = defaultdict(list)

    if args.skill_usage_only:
        return {
            "scope": args.scope,
            "repo_root": str(repo_root),
            "sources": sorted(sources),
            "codex_homes": [str(path) for path in codex_homes],
            "claude_homes": [str(path) for path in claude_homes],
            "grok_homes": [str(path) for path in grok_homes],
            "counts": {},
            "event_counts": {},
            "recommendations": [],
            "examples": {},
            "skill_usage": build_skill_usage_report(
                args, repo_root, sources, codex_homes, claude_homes, grok_homes
            ),
        }

    if "codex" in sources:
        for codex_home in codex_homes:
            for path in sorted((codex_home / "sessions").rglob("*.jsonl")):
                scan_codex_session(path, repo_root, args.scope, counts, examples, event_counts, args.limit)
    if "claude" in sources:
        for claude_home in claude_homes:
            for path in sorted((claude_home / "projects").rglob("*.jsonl")):
                scan_claude_session(path, repo_root, args.scope, counts, examples, event_counts, args.limit)
    if "grok" in sources:
        for grok_home in grok_homes:
            scan_grok_home(grok_home, repo_root, args.scope, counts, examples, event_counts, args.limit)
    if "codex-memory" in sources:
        for codex_home in codex_homes:
            memory_path = codex_home / "memories" / "MEMORY.md"
            if memory_path.exists():
                scan_memory_file(memory_path, repo_root, args.scope, counts, examples, args.limit)
    if "claude-memory" in sources:
        for claude_home in claude_homes:
            memory_paths = set(claude_home.rglob("memory/*.md")) | set(claude_home.rglob("MEMORY.md"))
            for path in sorted(memory_paths):
                scan_memory_file(path, repo_root, args.scope, counts, examples, args.limit)
    if "context-docs" in sources:
        scan_context_docs(repo_root, counts, examples, args.limit)

    skill_usage = build_skill_usage_report(
        args, repo_root, sources, codex_homes, claude_homes, grok_homes
    )

    for key in ("sessions_codex", "sessions_claude", "sessions_grok", "memory_files", "context_docs"):
        counts[key] += 0

    serialized_examples = {
        category: [example.__dict__ for example in items]
        for category, items in sorted(examples.items())
    }
    return {
        "scope": args.scope,
        "repo_root": str(repo_root),
        "sources": sorted(sources),
        "codex_homes": [str(path) for path in codex_homes],
        "claude_homes": [str(path) for path in claude_homes],
        "grok_homes": [str(path) for path in grok_homes],
        "counts": dict(counts),
        "event_counts": dict(event_counts),
        "recommendations": candidate_recommendations(counts),
        "examples": serialized_examples,
        "skill_usage": skill_usage,
    }


def print_markdown_report(report: dict[str, Any], limit: int) -> None:
    counts = Counter(report["counts"])
    event_counts = Counter(report["event_counts"])

    print("# Skill Mining Report")
    print(f"- scope: {report['scope']}")
    print(f"- repo_root: {report['repo_root']}")
    print(f"- sources: {','.join(report['sources'])}")
    print(f"- codex_homes: {','.join(report['codex_homes'])}")
    print(f"- claude_homes: {','.join(report['claude_homes'])}")
    print(f"- grok_homes: {','.join(report.get('grok_homes') or [])}")
    print(f"- codex_sessions: {counts['sessions_codex']}")
    print(f"- claude_sessions: {counts['sessions_claude']}")
    print(f"- grok_sessions: {counts['sessions_grok']}")
    print(f"- memory_files: {counts['memory_files']}")
    print(f"- context_docs: {counts['context_docs']}")

    print_counter("Failure Signatures", counts, "failure_")
    print_counter("User Signals", counts, "user_")
    print_counter("Session Events", event_counts)
    print_counter("Memory Signals", counts, "memory_")
    print_counter("Project Context Signals", counts, "context_")

    skill_usage = report.get("skill_usage") or {}
    if skill_usage:
        print("\n## Skill Usage")
        print(f"- prefix: {skill_usage['prefix']}")
        print(f"- roots: {','.join(skill_usage['roots'])}")
        if skill_usage["before_date"]:
            print(f"- before_date: {skill_usage['before_date']}")
        print(f"- include_output: {skill_usage['include_output']}")
        print(f"- inventory_total: {skill_usage['inventory_total']}")
        print(f"- records: {skill_usage['records']}")
        print(f"- sessions: {skill_usage['sessions']}")
        print("- inventory_by_category:")
        for key, value in Counter(skill_usage["inventory_by_category"]).most_common():
            print(f"  - {key}: {value}")
        print("- inventory_by_invocation:")
        for key, value in Counter(skill_usage["inventory_by_invocation"]).most_common():
            print(f"  - {key}: {value}")
        print("- inventory_by_declared_invocation:")
        for key, value in Counter(skill_usage["inventory_by_declared_invocation"]).most_common():
            print(f"  - {key}: {value}")
        print("- inventory_by_activation_mode:")
        for key, value in Counter(skill_usage["inventory_by_activation_mode"]).most_common():
            print(f"  - {key}: {value}")
        print("- inventory_by_default_role:")
        for key, value in Counter(skill_usage["inventory_by_default_role"]).most_common():
            print(f"  - {key}: {value}")
        print("- inventory_by_codex_policy:")
        for key, value in Counter(skill_usage["inventory_by_codex_policy"]).most_common():
            print(f"  - {key}: {value}")
        print("- inventory_by_claude_visibility:")
        for key, value in Counter(skill_usage["inventory_by_claude_visibility"]).most_common():
            print(f"  - {key}: {value}")
        print("- by_category:")
        for key, value in Counter(skill_usage["by_category"]).most_common():
            print(f"  - {key}: {value}")
        print("- model_activation_summary:")
        for key, value in skill_usage["model_activation_summary"].items():
            print(f"  - {key}: {value}")
        print("- by_skill_sessions:")
        for key, value in Counter(skill_usage["by_skill_session"]).most_common(20):
            print(f"  - {key}: {value}")
        if limit > 0:
            print("- examples:")
            for example in skill_usage["examples"][:limit]:
                skills = ",".join(example["skills"])
                print(
                    f"  - [{example['source']}] {example['category']} skills={skills} "
                    f"cwd={example['cwd']} session={example['session_id']} "
                    f"file={example['file']}:{example['line']}"
                )
                print(f"    {example['text']}")

    print("\n## Candidate Recommendations")
    recommendations = report["recommendations"]
    if recommendations:
        for recommendation in recommendations:
            print(f"- {recommendation}")
    else:
        print("- none")

    print("\n## Examples")
    for category, items in report["examples"].items():
        print(f"\n### {category}")
        for example in items[:limit]:
            print(f"- [{example['source']}] cwd={example['cwd']} session={example['session_id']} file={example['file']}")
            print(f"  {example['text']}")


def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    print_markdown_report(report, args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
