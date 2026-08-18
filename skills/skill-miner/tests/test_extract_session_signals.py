from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract-session-signals.py"


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


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


if __name__ == "__main__":
    unittest.main()
