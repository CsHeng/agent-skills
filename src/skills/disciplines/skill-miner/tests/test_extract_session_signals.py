from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract-session-signals.py"


def isolated_env(home: Path) -> dict[str, str]:
    return {
        "HOME": str(home),
        "PATH": os.environ.get("PATH", os.defpath),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPYCACHEPREFIX": str(home / "cache" / "python"),
    }


def run_extract(args: list[str], isolated_home: Path) -> subprocess.CompletedProcess[str]:
    isolated_home.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=True,
        text=True,
        capture_output=True,
        env=isolated_env(isolated_home),
    )


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def pi_header(
    session_id: str,
    cwd: str,
    timestamp: str = "2026-03-01T00:00:00Z",
    **extra: object,
) -> dict[str, object]:
    row: dict[str, object] = {
        "type": "session",
        "version": 3,
        "id": session_id,
        "cwd": cwd,
        "timestamp": timestamp,
    }
    row.update(extra)
    return row


def pi_message(
    entry_id: str,
    parent_id: str | None,
    role: str,
    content: object,
    stop: str | None = None,
    model: str | None = None,
    **extra: object,
) -> dict[str, object]:
    message: dict[str, object] = {
        "role": role,
        "content": content,
        "timestamp": 1710000000000,
    }
    if stop is not None:
        message["stopReason"] = stop
    if model is not None:
        message["model"] = model
        message["provider"] = "test-provider"
    message.update(extra)
    return {
        "id": entry_id,
        "parentId": parent_id,
        "timestamp": "2026-03-01T00:00:01Z",
        "type": "message",
        "message": message,
    }


class ExtractSessionSignalsCliTest(unittest.TestCase):
    def test_shell_wrapped_rg_exit_one_is_search_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / "codex"
            repo_root = root / "repo"
            repo_root.mkdir()

            write_jsonl(
                codex_home / "sessions" / "2026" / "01" / "03" / "rollout-search.jsonl",
                [
                    {
                        "type": "session_meta",
                        "payload": {
                            "cwd": str(repo_root),
                            "id": "codex-search",
                            "timestamp": "2026-01-03T00:00:00Z",
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "call_id": "call-search",
                            "name": "exec_command",
                            "arguments": json.dumps(
                                {
                                    "cmd": "bash -lc 'rg -n \"missing pattern\" README.md -S'",
                                }
                            ),
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "function_call_output",
                            "call_id": "call-search",
                            "output": "Process exited with code 1\nOriginal token count: 0\nOutput:\n",
                        },
                    },
                ],
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--scope",
                    "all",
                    "--repo-root",
                    str(repo_root),
                    "--codex-home",
                    str(codex_home),
                    "--sources",
                    "codex",
                    "--format",
                    "json",
                    "--limit",
                    "0",
                ],
                check=True,
                text=True,
                capture_output=True,
                env=isolated_env(root / "isolated-home"),
            )

            counts = json.loads(result.stdout)["counts"]
            self.assertEqual(counts["search_no_match"], 1)
            self.assertNotIn("failure_other_nonzero", counts)

    def test_json_output_aggregates_multiple_homes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_one = root / "codex-one"
            codex_two = root / "codex-two"
            claude_one = root / "claude-one"
            repo_root = root / "repo"
            repo_root.mkdir()

            write_jsonl(
                codex_one / "sessions" / "2026" / "01" / "01" / "rollout-a.jsonl",
                [
                    {
                        "type": "session_meta",
                        "payload": {
                            "cwd": str(repo_root),
                            "id": "codex-a",
                            "timestamp": "2026-01-01T00:00:00Z",
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "user",
                            "content": [{"text": "只分析，不要直接改"}],
                        },
                    },
                ],
            )
            write_jsonl(
                codex_two / "sessions" / "2026" / "01" / "02" / "rollout-b.jsonl",
                [
                    {
                        "type": "session_meta",
                        "payload": {
                            "cwd": str(repo_root),
                            "id": "codex-b",
                            "timestamp": "2026-01-02T00:00:00Z",
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "user",
                            "content": [{"text": "给我直接 command"}],
                        },
                    },
                ],
            )
            write_jsonl(
                claude_one / "projects" / "fixture.jsonl",
                [
                    {
                        "type": "user",
                        "cwd": str(repo_root),
                        "sessionId": "claude-a",
                        "message": {"content": [{"text": "不要猜，先查 runtime log"}]},
                    }
                ],
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--scope",
                    "all",
                    "--repo-root",
                    str(repo_root),
                    "--codex-home",
                    str(codex_one),
                    "--codex-home",
                    str(codex_two),
                    "--claude-home",
                    str(claude_one),
                    "--sources",
                    "codex,claude",
                    "--format",
                    "json",
                    "--limit",
                    "0",
                ],
                check=True,
                text=True,
                capture_output=True,
                env=isolated_env(root / "isolated-home"),
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["counts"]["sessions_codex"], 2)
            self.assertEqual(payload["counts"]["sessions_claude"], 1)
            self.assertEqual(payload["counts"]["user_analysis_only"], 1)
            self.assertEqual(payload["counts"]["user_command_requested"], 1)
            self.assertEqual(payload["counts"]["user_runtime_evidence"], 1)
            self.assertEqual(payload["codex_homes"], [str(codex_one), str(codex_two)])
            self.assertEqual(payload["claude_homes"], [str(claude_one)])

    def test_grok_home_prompt_and_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            grok_home = root / "grok"
            repo_root = root / "repo"
            repo_root.mkdir()
            from urllib.parse import quote

            workspace = grok_home / "sessions" / quote(str(repo_root), safe="")
            session_id = "019f0000-aaaa-bbbb-cccc-ddddeeeeffff"
            session_dir = workspace / session_id
            session_dir.mkdir(parents=True)

            write_jsonl(
                workspace / "prompt_history.jsonl",
                [
                    {
                        "timestamp": "2026-07-25T11:00:00Z",
                        "session_id": session_id,
                        "prompt": "只分析，不要直接改 PVC",
                        "is_bash": False,
                    },
                    {
                        "timestamp": "2026-07-25T11:05:00Z",
                        "session_id": session_id,
                        "prompt": "不对，应该是完整改名一次切完",
                        "is_bash": False,
                    },
                ],
            )
            write_jsonl(
                session_dir / "events.jsonl",
                [
                    {
                        "ts": "2026-07-25T11:01:00Z",
                        "type": "tool_completed",
                        "tool_name": "run_terminal_command",
                        "duration_ms": 12,
                        "outcome": "error",
                    },
                    {
                        "ts": "2026-07-25T11:06:00Z",
                        "type": "turn_ended",
                        "outcome": "completed",
                    },
                ],
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--scope",
                    "current",
                    "--repo-root",
                    str(repo_root),
                    "--grok-home",
                    str(grok_home),
                    "--sources",
                    "grok",
                    "--format",
                    "json",
                    "--limit",
                    "0",
                ],
                check=True,
                text=True,
                capture_output=True,
                env=isolated_env(root / "isolated-home"),
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["counts"]["sessions_grok"], 1)
            self.assertEqual(payload["counts"]["user_analysis_only"], 1)
            self.assertEqual(payload["counts"]["user_correction"], 1)
            self.assertEqual(payload["event_counts"]["grok_tool_error"], 1)
            self.assertEqual(payload["grok_homes"], [str(grok_home)])

    def test_skill_usage_report_filters_injected_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / "codex"
            repo_root = root / "repo"
            skill_root = root / "sample-skill-pack"
            repo_root.mkdir()
            skill_dir = skill_root / "skills" / "engineering" / "tdd"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: tdd
description: Test-driven development.
---

# TDD
""",
                encoding="utf-8",
            )

            write_jsonl(
                codex_home / "sessions" / "2026" / "01" / "04" / "rollout-skills.jsonl",
                [
                    {
                        "type": "session_meta",
                        "payload": {
                            "cwd": str(repo_root),
                            "id": "codex-skills",
                            "timestamp": "2026-01-04T00:00:00Z",
                            "base_instructions": {
                                "text": "### Available skills\n- sample-skill-pack:tdd " + ("x" * 1200)
                            },
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "user",
                            "content": [{"text": "$sample-skill-pack:tdd"}],
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "call_id": "call-skill",
                            "name": "exec_command",
                            "arguments": json.dumps(
                                {
                                    "cmd": f"sed -n '1,120p' {skill_dir / 'SKILL.md'}",
                                }
                            ),
                        },
                    },
                ],
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--scope",
                    "all",
                    "--repo-root",
                    str(repo_root),
                    "--codex-home",
                    str(codex_home),
                    "--sources",
                    "codex",
                    "--format",
                    "json",
                    "--limit",
                    "10",
                    "--skill-usage-root",
                    str(skill_root),
                    "--skill-usage-prefix",
                    "sample-skill-pack",
                ],
                check=True,
                text=True,
                capture_output=True,
                env=isolated_env(root / "isolated-home"),
            )

            usage = json.loads(result.stdout)["skill_usage"]
            self.assertEqual(usage["inventory_total"], 1)
            self.assertEqual(usage["records"], 2)
            self.assertEqual(usage["sessions"], 1)
            self.assertEqual(usage["by_category"]["user_explicit"], 1)
            self.assertEqual(usage["by_category"]["skill_load"], 1)
            self.assertEqual(usage["by_skill"]["tdd"], 2)
            self.assertEqual(usage["by_skill_session"]["tdd"], 1)

    def test_codex_usage_separates_evidence_and_inferred_activation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / "codex"
            repo_root = root / "repo"
            skill_root = root / "bundle"
            repo_root.mkdir()
            skill_dir = skill_root / "skills" / "engineering" / "tdd"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: tdd
description: Test-driven development.
---

# TDD
""",
                encoding="utf-8",
            )

            explicit_rows = [
                {
                    "type": "session_meta",
                    "payload": {
                        "cwd": str(repo_root),
                        "id": "codex-explicit",
                        "timestamp": "2026-01-04T00:00:00Z",
                        "base_instructions": {
                            "text": "### Available skills\n- coding:tdd " + ("x" * 1200)
                        },
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"text": "Please use $coding:tdd."}],
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"text": "I am using coding:tdd."}],
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "call_id": "load-explicit",
                        "name": "exec_command",
                        "arguments": json.dumps(
                            {"cmd": f"sed -n '1,120p' {skill_dir / 'SKILL.md'}"}
                        ),
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "function_call_output",
                        "call_id": "load-explicit",
                        "output": f"loaded {skill_dir / 'SKILL.md'}",
                    },
                },
            ]
            inferred_rows = [
                {
                    "type": "session_meta",
                    "payload": {
                        "cwd": str(repo_root),
                        "id": "codex-inferred",
                        "timestamp": "2026-01-05T00:00:00Z",
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"text": "I selected coding:tdd for this task."}],
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "call_id": "load-inferred",
                        "name": "exec_command",
                        "arguments": json.dumps(
                            {"cmd": f"sed -n '1,120p' {skill_dir / 'SKILL.md'}"}
                        ),
                    },
                },
            ]
            write_jsonl(
                codex_home / "sessions" / "2026" / "01" / "04" / "rollout-explicit.jsonl",
                explicit_rows,
            )
            write_jsonl(
                codex_home / "sessions" / "2026" / "01" / "05" / "rollout-inferred.jsonl",
                inferred_rows,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--scope",
                    "all",
                    "--repo-root",
                    str(repo_root),
                    "--codex-home",
                    str(codex_home),
                    "--sources",
                    "codex",
                    "--format",
                    "json",
                    "--skill-usage-only",
                    "--skill-usage-root",
                    str(skill_root),
                    "--skill-usage-prefix",
                    "coding",
                    "--skill-usage-include-output",
                ],
                check=True,
                text=True,
                capture_output=True,
                env=isolated_env(root / "isolated-home"),
            )

            usage = json.loads(result.stdout)["skill_usage"]
            self.assertEqual(usage["records"], 6)
            self.assertEqual(usage["by_category"]["user_explicit"], 1)
            self.assertEqual(usage["by_category"]["assistant_reference"], 2)
            self.assertEqual(usage["by_category"]["skill_load"], 2)
            self.assertEqual(usage["by_category"]["tool_output"], 1)
            self.assertEqual(
                usage["model_activation_summary"],
                {
                    "explicit_request_with_load": 1,
                    "heuristic_inferred": 1,
                    "skill_load_upper_bound": 2,
                },
            )
            self.assertEqual(usage["examples"], [])

    def test_claude_wrapped_tool_payloads_are_not_user_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude_home = root / "claude"
            repo_root = root / "repo"
            skill_root = root / "bundle"
            repo_root.mkdir()
            skill_dir = skill_root / "skills" / "engineering" / "tdd"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: tdd
description: Test-driven development.
---

# TDD
""",
                encoding="utf-8",
            )
            common = {
                "cwd": str(repo_root),
                "sessionId": "claude-wrappers",
                "timestamp": "2026-01-06T00:00:00Z",
            }
            write_jsonl(
                claude_home / "projects" / "fixture.jsonl",
                [
                    {
                        **common,
                        "type": "user",
                        "message": {
                            "role": "user",
                            "content": [{"type": "text", "text": "Use $coding:tdd."}],
                        },
                    },
                    {
                        **common,
                        "type": "user",
                        "message": {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "content": f"loaded {skill_dir / 'SKILL.md'}",
                                }
                            ],
                        },
                        "toolUseResult": f"loaded {skill_dir / 'SKILL.md'}",
                    },
                    {
                        **common,
                        "type": "user",
                        "message": {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_use",
                                    "name": "Read",
                                    "input": {"file_path": str(skill_dir / "SKILL.md")},
                                }
                            ],
                        },
                    },
                    {
                        **common,
                        "type": "user",
                        "hook": {"output": f"checked {skill_dir / 'SKILL.md'}"},
                    },
                ],
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--scope",
                    "all",
                    "--repo-root",
                    str(repo_root),
                    "--claude-home",
                    str(claude_home),
                    "--sources",
                    "claude",
                    "--format",
                    "json",
                    "--limit",
                    "0",
                    "--skill-usage-only",
                    "--skill-usage-root",
                    str(skill_root),
                    "--skill-usage-prefix",
                    "coding",
                    "--skill-usage-include-output",
                ],
                check=True,
                text=True,
                capture_output=True,
                env=isolated_env(root / "isolated-home"),
            )

            usage = json.loads(result.stdout)["skill_usage"]
            self.assertEqual(usage["by_category"]["user_explicit"], 1)
            self.assertEqual(usage["by_category"]["tool_output"], 3)
            self.assertEqual(usage["records"], 4)

    def test_usage_ignores_unknown_skill_loads_and_maps_flat_public_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / "codex"
            repo_root = root / "repo"
            skill_root = repo_root / "src" / "skills"
            skill_dir = skill_root / "disciplines" / "tdd"
            repo_root.mkdir()
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: tdd
description: Test-driven development.
---

# TDD
""",
                encoding="utf-8",
            )
            installed_root = root / "installed" / "coding" / "skills"
            current_load = installed_root / "tdd" / "SKILL.md"
            foreign_load = installed_root / "foreign-skill" / "SKILL.md"
            write_jsonl(
                codex_home / "sessions" / "2026" / "01" / "06" / "fixture.jsonl",
                [
                    {
                        "type": "session_meta",
                        "payload": {
                            "cwd": str(repo_root),
                            "id": "flat-loads",
                            "timestamp": "2026-01-06T00:00:00Z",
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "call_id": "current-load",
                            "name": "exec_command",
                            "arguments": json.dumps(
                                {"cmd": f"sed -n '1,120p' {current_load}"}
                            ),
                        },
                    },
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "call_id": "foreign-load",
                            "name": "exec_command",
                            "arguments": json.dumps(
                                {"cmd": f"sed -n '1,120p' {foreign_load}"}
                            ),
                        },
                    },
                ],
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--scope",
                    "all",
                    "--repo-root",
                    str(repo_root),
                    "--codex-home",
                    str(codex_home),
                    "--sources",
                    "codex",
                    "--format",
                    "json",
                    "--limit",
                    "0",
                    "--skill-usage-only",
                    "--skill-usage-root",
                    str(skill_root),
                    "--skill-usage-prefix",
                    "coding",
                ],
                check=True,
                text=True,
                capture_output=True,
                env=isolated_env(root / "isolated-home"),
            )

            usage = json.loads(result.stdout)["skill_usage"]
            self.assertEqual(usage["records"], 1)
            self.assertEqual(usage["by_category"], {"skill_load": 1})
            self.assertEqual(usage["by_skill"], {"tdd": 1})
            self.assertNotIn("(repo)", usage["by_skill"])

    def test_all_scope_uses_all_homes_but_current_contract_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_root = root / "repo"
            other_repo = root / "other-repo"
            codex_one = root / "codex-one"
            codex_two = root / "codex-two"
            repo_root.mkdir()
            other_repo.mkdir()
            skill_dir = repo_root / "src" / "skills" / "disciplines" / "tdd"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: tdd
description: Test-driven development.
---

# TDD
""",
                encoding="utf-8",
            )
            (skill_dir / "agents").mkdir()
            (skill_dir / "agents" / "openai.yaml").write_text(
                """interface:
  display_name: TDD
""",
                encoding="utf-8",
            )
            contracts = repo_root / "contracts"
            contracts.mkdir()
            contract = contracts / "skills.toml"
            contract.write_text(
                """[activation_modes.native]
codex_allow_implicit_invocation = true
claude_effective_visibility = "default-visible"

[skills.tdd]
source = "src/skills/disciplines/tdd"
public_id = "tdd"
category = "discipline"
install = ["claude", "codex", "root-flat"]
activation_mode = "native"
default_role = "primary"
""",
                encoding="utf-8",
            )

            for home, cwd, session_id, day in (
                (codex_one, repo_root, "current-repo", "07"),
                (codex_two, other_repo, "other-repo", "08"),
            ):
                write_jsonl(
                    home / "sessions" / "2026" / "01" / day / f"{session_id}.jsonl",
                    [
                        {
                            "type": "session_meta",
                            "payload": {
                                "cwd": str(cwd),
                                "id": session_id,
                                "timestamp": f"2026-01-{day}T00:00:00Z",
                            },
                        },
                        {
                            "type": "response_item",
                            "payload": {
                                "type": "message",
                                "role": "user",
                                "content": [{"text": "Use $coding:tdd."}],
                            },
                        },
                    ],
                )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--scope",
                    "all",
                    "--repo-root",
                    str(repo_root),
                    "--codex-home",
                    str(codex_one),
                    "--codex-home",
                    str(codex_two),
                    "--sources",
                    "codex",
                    "--format",
                    "json",
                    "--limit",
                    "0",
                    "--skill-usage-only",
                    "--skill-usage-root",
                    str(repo_root / "src" / "skills"),
                    "--skill-usage-prefix",
                    "coding",
                    "--skill-usage-contract",
                    str(contract),
                ],
                check=True,
                text=True,
                capture_output=True,
                env=isolated_env(root / "isolated-home"),
            )

            usage = json.loads(result.stdout)["skill_usage"]
            self.assertEqual(usage["inventory_total"], 1)
            self.assertEqual(usage["inventory_by_activation_mode"], {"native": 1})
            self.assertEqual(usage["inventory_by_default_role"], {"primary": 1})
            self.assertEqual(usage["records"], 2)
            self.assertEqual(usage["sessions"], 2)
            inventory = usage["inventory"][0]
            self.assertTrue(inventory["declared_implicit_invocation"])
            self.assertFalse(inventory["disable_model_invocation"])
            self.assertEqual(inventory["activation_mode"], "native")
            self.assertEqual(inventory["default_role"], "primary")
            self.assertTrue(inventory["codex_allow_implicit_invocation"])
            self.assertEqual(inventory["codex_policy_source"], "contract-derived")
            self.assertEqual(inventory["claude_model_visibility"], "default-visible")
            self.assertEqual(
                inventory["claude_policy_source"], "contract-effective-state"
            )


class PiExtractSessionSignalsTest(unittest.TestCase):
    def test_pi_sources_scope_homes_and_formats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            isolated = root / "isolated-home"
            repo = root / "repo"
            other = root / "other"
            repo.mkdir()
            other.mkdir()
            default_pi = isolated / ".pi" / "agent"
            write_jsonl(
                default_pi / "sessions" / "default.jsonl",
                [
                    pi_header("sid-default", str(repo)),
                    pi_message(
                        "d1",
                        None,
                        "user",
                        [{"type": "text", "text": "只分析，不要直接改"}],
                    ),
                ],
            )

            default_payload = json.loads(
                run_extract(
                    [
                        "--scope",
                        "current",
                        "--repo-root",
                        str(repo),
                        "--format",
                        "json",
                        "--limit",
                        "0",
                    ],
                    isolated,
                ).stdout
            )
            self.assertIn("pi", default_payload["sources"])
            self.assertEqual(default_payload["counts"]["sessions_pi"], 1)
            self.assertEqual(default_payload["pi_homes"], [str(default_pi)])
            self.assertEqual(default_payload["counts"]["user_analysis_only"], 1)

            home_a = root / "pi-a"
            home_b = root / "pi-b"
            home_c = root / "pi-c"
            write_jsonl(
                home_a / "sessions" / "a.jsonl",
                [
                    pi_header("sid-a", str(repo)),
                    pi_message("a1", None, "user", "给我直接 command"),
                ],
            )
            write_jsonl(
                home_b / "sessions" / "b.jsonl",
                [
                    pi_header("sid-b", str(other), timestamp="2026-03-02T00:00:00Z"),
                    pi_message("b1", None, "user", "不对，错了"),
                ],
            )
            write_jsonl(
                home_c / "sessions" / "nested" / "c.jsonl",
                [
                    pi_header("sid-c", str(repo)),
                    pi_message("c1", None, "user", "先不处理"),
                ],
            )
            home_flags = [
                "--pi-home",
                str(home_a),
                "--pi-home",
                f"{home_b},{home_c}",
                "--sources",
                "pi",
                "--repo-root",
                str(repo),
                "--format",
                "json",
                "--limit",
                "0",
            ]
            current = json.loads(
                run_extract(["--scope", "current", *home_flags], isolated).stdout
            )
            self.assertEqual(current["counts"]["sessions_pi"], 2)
            self.assertEqual(
                current["pi_homes"], [str(home_a), str(home_b), str(home_c)]
            )
            self.assertEqual(current["counts"]["user_command_requested"], 1)
            self.assertEqual(current["counts"]["user_scope_rejected"], 1)
            self.assertNotIn("user_correction", current["counts"])

            all_scope = json.loads(
                run_extract(["--scope", "all", *home_flags], isolated).stdout
            )
            self.assertEqual(all_scope["counts"]["sessions_pi"], 3)
            self.assertEqual(all_scope["counts"]["user_correction"], 1)

            markdown = run_extract(
                [
                    "--scope",
                    "current",
                    "--pi-home",
                    str(home_a),
                    "--sources",
                    "pi",
                    "--repo-root",
                    str(repo),
                    "--format",
                    "markdown",
                    "--limit",
                    "0",
                ],
                isolated,
            ).stdout
            self.assertIn("pi_homes:", markdown)
            self.assertIn("pi_sessions:", markdown)

    def test_pi_unscopable_malformed_cycles_and_incomplete_are_visible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            isolated = root / "isolated-home"
            repo = root / "repo"
            other = root / "other"
            repo.mkdir()
            other.mkdir()
            pi_home = root / "pi"
            write_jsonl(
                pi_home / "sessions" / "dict-version.jsonl",
                [
                    {
                        "type": "session",
                        "version": {"major": 3},
                        "id": "dict-version",
                        "cwd": str(repo),
                        "timestamp": "2026-03-01T00:00:00Z",
                    }
                ],
            )
            v1 = pi_header("v1", str(repo))
            v1["version"] = 1
            write_jsonl(pi_home / "sessions" / "v1.jsonl", [v1])
            write_jsonl(
                pi_home / "sessions" / "missing-cwd.jsonl",
                [
                    {
                        "type": "session",
                        "version": 3,
                        "id": "no-cwd",
                        "timestamp": "2026-03-01T00:00:00Z",
                    },
                    pi_message("n1", None, "user", "只分析，不要直接改"),
                ],
            )
            write_jsonl(
                pi_home / "sessions" / "missing-header.jsonl",
                [
                    pi_message("h1", None, "user", "只分析，不要直接改"),
                ],
            )
            (pi_home / "sessions" / "bad-line.jsonl").parent.mkdir(parents=True, exist_ok=True)
            (pi_home / "sessions" / "bad-line.jsonl").write_text(
                json.dumps(pi_header("bad-line", str(repo)))
                + "\nnot json\n"
                + json.dumps(pi_message("bl1", None, "user", "给我直接 command"))
                + "\n"
            )
            write_jsonl(
                pi_home / "sessions" / "cycle.jsonl",
                [
                    pi_header("cycle", str(repo)),
                    pi_message("c1", "c2", "user", "先不处理"),
                    pi_message("c2", "c1", "assistant", "loop", stop="stop"),
                ],
            )
            write_jsonl(
                pi_home / "sessions" / "bad-parent.jsonl",
                [
                    pi_header("bad-parent", str(repo)),
                    {
                        "id": "p1",
                        "parentId": ["not-a-string"],
                        "timestamp": "2026-03-01T00:00:01Z",
                        "type": "message",
                        "message": {
                            "role": "user",
                            "content": "不对，错了",
                            "timestamp": 1710000000000,
                        },
                    },
                ],
            )
            write_jsonl(
                pi_home / "sessions" / "foreign.jsonl",
                [
                    pi_header("foreign", str(other)),
                    pi_message("f1", None, "user", "只分析，不要直接改"),
                ],
            )

            payload = json.loads(
                run_extract(
                    [
                        "--scope",
                        "current",
                        "--repo-root",
                        str(repo),
                        "--pi-home",
                        str(pi_home),
                        "--sources",
                        "pi",
                        "--format",
                        "json",
                        "--limit",
                        "0",
                    ],
                    isolated,
                ).stdout
            )
            limitations = " ".join(payload["limitations"])
            events = payload["event_counts"]
            self.assertGreaterEqual(events.get("pi_unscopable", 0), 1)
            self.assertGreaterEqual(events.get("pi_unsupported_version", 0), 1)
            self.assertGreaterEqual(events.get("pi_incomplete_ancestor", 0), 2)
            self.assertGreaterEqual(events.get("pi_malformed_line", 0), 1)
            self.assertIn("unscopable incomplete Pi input", limitations)
            self.assertIn("incomplete ancestors", limitations)
            self.assertEqual(payload["counts"].get("user_analysis_only", 0), 0)
            self.assertEqual(payload["counts"]["user_scope_rejected"], 1)
            self.assertEqual(payload["counts"]["user_correction"], 1)
            self.assertEqual(payload["counts"]["user_command_requested"], 1)
            self.assertGreaterEqual(payload["counts"]["sessions_pi"], 3)

    def test_pi_branch_compaction_fork_stops_and_injection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            isolated = root / "isolated-home"
            repo = root / "repo"
            repo.mkdir()
            pi_home = root / "pi"
            write_jsonl(
                pi_home / "sessions" / "branch.jsonl",
                [
                    pi_header("branch", str(repo)),
                    pi_message("e1", None, "user", "只分析，不要直接改"),
                    pi_message("e2", "e1", "assistant", "on A", stop="toolUse"),
                    pi_message("e3", "e2", "user", "给我直接 command"),
                    pi_message("e4", "e1", "user", "不是这个repo"),
                    pi_message("e5", "e4", "assistant", "on B", stop="stop"),
                ],
            )
            write_jsonl(
                pi_home / "sessions" / "compact-fork.jsonl",
                [
                    pi_header("compact", str(repo), parentSession="other-uuid"),
                    pi_message("k1", None, "user", "只分析，不要直接改"),
                    pi_message("k2", "k1", "assistant", "done", stop="stop"),
                    {
                        "id": "k3",
                        "parentId": "k2",
                        "timestamp": "2026-03-01T00:00:02Z",
                        "type": "compaction",
                        "summary": "只分析，不要直接改",
                        "retainedTail": [
                            pi_message("k1", None, "user", "只分析，不要直接改")["message"],
                            pi_message("k2", "k1", "assistant", "done", stop="stop")["message"],
                        ],
                    },
                    pi_message("k4", "k3", "user", "继续"),
                ],
            )
            write_jsonl(
                pi_home / "sessions" / "stops-inject.jsonl",
                [
                    pi_header("stops", str(repo)),
                    pi_message(
                        "s1",
                        None,
                        "user",
                        "<skill name=\"tdd\">injected $coding:tdd FAKESECRET_skill</skill>\n确认",
                    ),
                    pi_message("s2", "s1", "assistant", "a", stop="stop", model="actual-model-b"),
                    pi_message("s3", "s2", "assistant", "b", stop="toolUse"),
                    pi_message("s4", "s3", "assistant", "c", stop="error"),
                    pi_message("s5", "s4", "assistant", "d", stop="aborted"),
                    pi_message("s6", "s5", "assistant", "e", stop="length"),
                    pi_message("s7", "s6", "user", "继续"),
                    {
                        "id": "s8",
                        "parentId": "s7",
                        "timestamp": "2026-03-01T00:00:03Z",
                        "type": "model_change",
                        "provider": "test-provider",
                        "modelId": "changed-model-a",
                    },
                    {
                        "id": "s9",
                        "parentId": "s8",
                        "timestamp": "2026-03-01T00:00:04Z",
                        "type": "message",
                        "message": {
                            "role": "toolResult",
                            "toolName": "read",
                            "toolCallId": "call-1",
                            "isError": True,
                            "content": [
                                {
                                    "type": "text",
                                    "text": "invalid upstream design",
                                }
                            ],
                        },
                    },
                ],
            )

            payload = json.loads(
                run_extract(
                    [
                        "--scope",
                        "current",
                        "--repo-root",
                        str(repo),
                        "--pi-home",
                        str(pi_home),
                        "--sources",
                        "pi",
                        "--format",
                        "json",
                        "--limit",
                        "3",
                    ],
                    isolated,
                ).stdout
            )
            counts = payload["counts"]
            events = payload["event_counts"]
            limitations = " ".join(payload["limitations"])
            stdout = json.dumps(payload)
            self.assertEqual(counts["user_wrong_target"], 1)
            self.assertEqual(counts["user_analysis_only"], 2)
            self.assertNotIn("user_command_requested", counts)
            self.assertEqual(events["pi_compaction"], 1)
            self.assertEqual(events["pi_unmerged_leaves"], 1)
            self.assertEqual(events["pi_parent_session_unfollowed"], 1)
            self.assertIn("parentSession not followed", limitations)
            self.assertIn("not merged", limitations)
            self.assertEqual(events["pi_stop_stop"], 3)
            self.assertEqual(events["pi_stop_toolUse"], 1)
            self.assertEqual(events["pi_stop_error"], 1)
            self.assertEqual(events["pi_stop_aborted"], 1)
            self.assertEqual(events["pi_stop_length"], 1)
            self.assertEqual(events["pi_continuation_candidate"], 1)
            self.assertEqual(events["pi_model_change"], 1)
            self.assertEqual(events["pi_assistant_model"], 1)
            self.assertEqual(events["pi_assistant_model:actual-model-b"], 1)
            self.assertEqual(events["pi_model_change:changed-model-a"], 1)
            self.assertEqual(counts["user_approval_gate"], 1)
            self.assertEqual(counts["failure_review_artifact_invalid"], 1)
            self.assertNotIn("FAKESECRET_skill", stdout)
            recs = " ".join(payload["recommendations"])
            self.assertIn("investigate existing authority", recs)
            self.assertIn("never infer commit", recs)
            self.assertNotIn("consume existing confirmation as write/commit authority", recs)
            self.assertIn("do not use a lower-plane reviewer protocol", recs)
            self.assertNotIn("provider=test-provider", stdout)
            example_blob = json.dumps(payload["examples"])
            self.assertIn("pi model_change", example_blob)
            self.assertIn("pi assistant_model", example_blob)
            self.assertIn("pi user_approval_gate", example_blob)
            self.assertIn("pi tool_error", example_blob)

    def test_pi_skill_usage_secrets_symlink_and_date_cutoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            isolated = root / "isolated-home"
            repo = root / "repo"
            pi_home = root / "pi"
            skill_root = root / "bundle"
            skill_dir = skill_root / "skills" / "engineering" / "tdd"
            repo.mkdir()
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: tdd
description: Test-driven development.
---

# TDD
""",
                encoding="utf-8",
            )
            long_tail = ("pad " * 80) + "$coding:tdd"
            write_jsonl(
                pi_home / "sessions" / "usage.jsonl",
                [
                    pi_header("usage", str(repo), timestamp="2026-02-01T00:00:00Z"),
                    pi_message(
                        "u1",
                        None,
                        "user",
                        [
                            {
                                "type": "text",
                                "text": long_tail + " API_KEY=\"FAKESECRET_quoted\" Bearer FAKESECRET_bearer",
                            },
                            {
                                "type": "image",
                                "data": "FAKESECRET_image",
                            },
                        ],
                    ),
                    {
                        "id": "u2",
                        "parentId": "u1",
                        "timestamp": "2026-02-01T00:00:02Z",
                        "type": "message",
                        "message": {
                            "role": "assistant",
                            "model": "actual-model-b",
                            "stopReason": "toolUse",
                            "content": [
                                {
                                    "type": "thinking",
                                    "thinking": "FAKESECRET_thinking",
                                },
                                {
                                    "type": "text",
                                    "text": "using coding:tdd",
                                },
                                {
                                    "type": "toolCall",
                                    "id": "call-1",
                                    "name": "read",
                                    "arguments": {
                                        "path": str(skill_dir / "SKILL.md"),
                                        "token": "FAKESECRET_arg",
                                        "cmd": "cat FAKESECRET_arg",
                                    },
                                },
                            ],
                        },
                    },
                    {
                        "id": "u3",
                        "parentId": "u2",
                        "timestamp": "2026-02-01T00:00:03Z",
                        "type": "message",
                        "message": {
                            "role": "toolResult",
                            "toolName": "read",
                            "toolCallId": "call-1",
                            "isError": False,
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"loaded {skill_dir / 'SKILL.md'} FAKESECRET_result",
                                }
                            ],
                        },
                    },
                ],
            )
            write_jsonl(
                pi_home / "sessions" / "usage-new.jsonl",
                [
                    pi_header("usage-new", str(repo), timestamp="2026-04-01T00:00:00Z"),
                    pi_message("n1", None, "user", "$coding:tdd"),
                ],
            )
            outside = root / "outside" / "auth.jsonl"
            write_jsonl(
                outside,
                [
                    pi_header("escaped", str(repo)),
                    pi_message("x1", None, "user", "FAKESECRET_escaped 只分析"),
                ],
            )
            link = pi_home / "sessions" / "escaped.jsonl"
            link.symlink_to(outside)

            common = [
                "--scope",
                "all",
                "--repo-root",
                str(repo),
                "--pi-home",
                str(pi_home),
                "--sources",
                "pi",
                "--format",
                "json",
                "--skill-usage-root",
                str(skill_root),
                "--skill-usage-prefix",
                "coding",
                "--skill-usage-before-date",
                "2026-03-01",
            ]
            hidden = run_extract([*common, "--limit", "0"], isolated)
            shown = run_extract(
                [*common, "--limit", "5", "--skill-usage-include-output"],
                isolated,
            )
            hidden_payload = json.loads(hidden.stdout)
            shown_payload = json.loads(shown.stdout)
            sentinels = (
                "FAKESECRET_thinking",
                "FAKESECRET_image",
                "FAKESECRET_arg",
                "FAKESECRET_result",
                "FAKESECRET_quoted",
                "FAKESECRET_bearer",
                "FAKESECRET_escaped",
            )
            for blob in (hidden.stdout, shown.stdout):
                for sentinel in sentinels:
                    self.assertNotIn(sentinel, blob)
            self.assertEqual(hidden_payload["event_counts"]["pi_escaped_source"], 1)
            self.assertTrue(
                any("escaped the Pi sessions/" in item for item in hidden_payload["limitations"])
            )
            hidden_usage = hidden_payload["skill_usage"]
            self.assertEqual(hidden_usage["by_category"]["user_explicit"], 1)
            self.assertEqual(hidden_usage["by_category"]["assistant_reference"], 1)
            self.assertEqual(hidden_usage["by_category"]["skill_load"], 1)
            self.assertNotIn("tool_output", hidden_usage["by_category"])
            self.assertEqual(hidden_usage["examples"], [])
            shown_usage = shown_payload["skill_usage"]
            self.assertEqual(shown_usage["by_category"]["tool_output"], 1)
            self.assertGreater(len(shown_usage["examples"]), 0)
            usage_text = json.dumps(shown_usage["examples"])
            self.assertIn("pi user_explicit", usage_text)
            self.assertIn("pi skill_load", usage_text)
            self.assertIn("pi tool_output", usage_text)
            self.assertNotIn(str(skill_dir / "SKILL.md"), usage_text)
            self.assertNotIn("cat FAKESECRET_arg", shown.stdout)


    def test_pi_usage_only_reports_limitations_and_ignores_context_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            home = root / "pi"
            skills = root / "skills"
            (skills / "tdd").mkdir(parents=True)
            (skills / "tdd" / "SKILL.md").write_text(
                "---\nname: tdd\ndescription: Test development.\n---\n# TDD\n"
            )
            real_user = pi_message("u", None, "user", "$coding:tdd")
            rows = [pi_header("usage-only", str(repo)), real_user]
            previous = "u"
            for entry_type in ("compaction", "branch_summary", "custom", "custom_message"):
                rows.append({
                    "type": entry_type, "id": entry_type, "parentId": previous,
                    "summary": "$coding:tdd", "content": "$coding:tdd",
                    "retainedTail": [real_user["message"]],
                })
                previous = entry_type
            rows.append(pi_message(
                "last", previous, "user",
                '<skill name="tdd">$coding:tdd SECRET_CONTEXT</skill>\n$coding:tdd',
            ))
            write_jsonl(home / "sessions" / "tree.jsonl", rows)
            write_jsonl(home / "sessions" / "legacy.jsonl", [
                pi_header("legacy", str(repo), version=2),
            ])
            flags = [
                "--repo-root", str(repo), "--pi-home", str(home), "--sources", "pi",
                "--skill-usage-only", "--skill-usage-root", str(skills),
                "--skill-usage-prefix", "coding", "--limit", "1",
            ]
            report = json.loads(run_extract([*flags, "--format", "json"], root / "env").stdout)
            self.assertEqual(report["skill_usage"]["by_category"], {"user_explicit": 2})
            self.assertEqual(len(report["skill_usage"]["examples"]), 1)
            self.assertTrue(report["limitations"])
            markdown = run_extract([*flags, "--format", "markdown"], root / "env").stdout
            self.assertIn("Evidence Limitations", markdown)
            self.assertIn("unsupported_version", markdown)
            self.assertIn("records: 2", markdown)
            self.assertNotIn("SECRET_CONTEXT", markdown)

    def test_pi_usage_evidence_uses_physical_jsonl_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            home = root / "pi"
            skills = root / "skills"
            (skills / "tdd").mkdir(parents=True)
            (skills / "tdd" / "SKILL.md").write_text(
                "---\nname: tdd\ndescription: Test development.\n---\n# TDD\n"
            )
            session = home / "sessions" / "lines.jsonl"
            write_jsonl(session, [
                pi_header("source-lines", str(repo)),
                pi_message("u", None, "user", "$coding:tdd"),
                pi_message("old", "u", "user", "unselected $coding:tdd"),
            ])
            with session.open("a") as stream:
                stream.write("malformed row\n\n")
                stream.write(json.dumps(pi_message("new", "u", "user", "$coding:tdd")) + "\n")
            flags = [
                "--repo-root", str(repo), "--pi-home", str(home), "--sources", "pi",
                "--skill-usage-root", str(skills), "--skill-usage-prefix", "coding",
                "--limit", "10", "--skill-usage-only",
            ]
            report = json.loads(run_extract([*flags, "--format", "json"], root / "env").stdout)
            self.assertEqual([record["line"] for record in report["skill_usage"]["examples"]], [2, 6])
            markdown = run_extract([*flags, "--format", "markdown"], root / "env").stdout
            self.assertIn("lines.jsonl:2", markdown)
            self.assertIn("lines.jsonl:6", markdown)

    def test_pi_missing_home_explicit_exclusion_and_alias_deduplication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            home = root / "pi"
            flags = ["--repo-root", str(repo), "--pi-home", str(home), "--format", "json"]
            missing = json.loads(run_extract([*flags, "--sources", "pi"], root / "env").stdout)
            self.assertEqual(missing["counts"]["sessions_pi"], 0)
            self.assertEqual(missing["limitations"], [])
            session = home / "sessions" / "original.jsonl"
            write_jsonl(session, [
                pi_header("same-file", str(repo)),
                pi_message("u", None, "user", "只分析，不要改"),
            ])
            (session.parent / "alias.jsonl").symlink_to(session)
            included = json.loads(run_extract([*flags, "--sources", "pi"], root / "env").stdout)
            self.assertEqual(included["counts"]["sessions_pi"], 1)
            self.assertEqual(included["counts"]["user_analysis_only"], 1)
            excluded = json.loads(run_extract([*flags, "--sources", "codex"], root / "env").stdout)
            self.assertEqual(excluded["counts"]["sessions_pi"], 0)


if __name__ == "__main__":
    unittest.main()
