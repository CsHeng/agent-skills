from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = (
    ROOT
    / "src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py"
)
FAKE_HERDR = ROOT / "tests/fixtures/herdr/fake-herdr.py"
SKILLS_CONTRACT = ROOT / "contracts/skills.toml"
ROUTING_CONTRACT = ROOT / "src/skills/session/use-coding-skills/references/routing.toml"
PLAN_SKILL = ROOT / "src/skills/workflows/plan-change/SKILL.md"
IMPLEMENT_SKILL = ROOT / "src/skills/workflows/implement-change/SKILL.md"


class HerdrAdapterContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "README").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "README"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "-c",
                "user.email=fixture@example.invalid",
                "-c",
                "user.name=fixture",
                "commit",
                "-qm",
                "fixture",
            ],
            check=True,
        )
        self.run_dir = self.repo / ".herdr-runs" / "run-k7"
        self.run_dir.mkdir(parents=True)
        self.log = Path(self.temp_dir.name) / "argv.jsonl"
        self.sentinel = Path(self.temp_dir.name) / "live-context-touched"
        revision = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True
        ).strip()
        self.envelope = {
            "schema_version": 1,
            "artifact_kind": "controller-binding-envelope",
            "controller": {
                "controller_id": "controller-k7",
                "run_id": "run-k7",
                "run_nonce": "nonce-fresh-k7",
                "model_policy": "semantic-routing",
            },
            "provenance": {
                "canonical_repository": str(self.repo.resolve()),
                "repository_revision": revision,
                "plan_ref": "docs/plans/approved.md",
                "plan_sha256": "a" * 64,
                "ledger_ref": "docs/plans/ledger.json",
                "ledger_sha256": "b" * 64,
            },
            "task": {
                "task_id": "T02",
                "attempt": 1,
                "runtime_role": "explorer",
                "scope_slice": "bounded search",
                "touch_set": [],
                "oracle_refs": ["python -m unittest"],
                "status": "ready",
                "executor_mode": "subagent",
                "delegation_policy": "preferred",
                "execution_profile": "fast",
                "reasoning_profile": "light",
                "isolation": "shared-read-only",
            },
            "physical_binding": {
                "terminal_backend": "herdr",
                "agent_kind": "codex",
                "agent_name": "explorer-otter-1e-tt02-a1",
                "model": "gpt-5.6-luna",
                "reasoning_effort": "low",
                "permission_mode": "never",
                "sandbox_mode": "read-only",
                "capability_profile": "delegated-read-only",
                "control_plane_endpoint": "native://openai",
                "credential_ref": "native-login/codex",
                "workspace_id": "w-main",
                "tab_id": "w-main:t-main",
                "pane_id": "w-main:p-main",
                "checkout_path": str(self.repo.resolve()),
            },
            "authority": {
                "adapter_capabilities": [
                    "consume-binding",
                    "manage-run-owned-terminal-resources",
                    "persist-adapter-state",
                ],
                "denied_capabilities": [
                    "select-task",
                    "mutate-task-ledger",
                    "converge-task",
                    "invoke-review",
                    "adjudicate-findings",
                    "repair-implementation",
                    "derive-lifecycle-tail",
                ],
            },
        }
        self.envelope_path = self.run_dir / "controller-binding.json"
        self.envelope_path.write_text(json.dumps(self.envelope), encoding="utf-8")
        self.envelope_path.chmod(0o600)
        self.env = {
            **os.environ,
            "HERDR_ENV": "1",
            "HERDR_WORKSPACE_ID": "w-main",
            "HERDR_TAB_ID": "w-main:t-main",
            "HERDR_PANE_ID": "w-main:p-main",
            "HERDR_FIXTURE_LOG": str(self.log),
            "HERDR_FIXTURE_AGENT_NAME": "explorer-otter-1e-tt02-a1",
            "HERDR_FIXTURE_SENTINEL": str(self.sentinel),
        }

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def invoke(
        self,
        command: str,
        *extra: str,
        env: dict[str, str] | None = None,
        executable: Path | None = None,
    ) -> dict[str, object]:
        completed = subprocess.run(
            [
                sys.executable,
                str(ADAPTER),
                command,
                "--envelope",
                str(self.envelope_path),
                "--herdr-executable",
                str(executable or FAKE_HERDR),
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
            env=env or self.env,
        )
        result = json.loads(completed.stdout)
        result["returncode"] = completed.returncode
        return result

    def test_executable_symlink_is_rejected_before_fixture(self) -> None:
        shim = Path(self.temp_dir.name) / "herdr-shim"
        shim.symlink_to(FAKE_HERDR)
        result = self.invoke("preflight", executable=shim)
        self.assertEqual(result["error"]["code"], "herdr_executable_invalid")
        self.assertFalse(self.log.exists())

    def test_controller_lease_admits_members_and_rejects_legacy_state(self) -> None:
        self.assertEqual(self.invoke("preflight")["returncode"], 0)
        lease = json.loads((self.repo / ".herdr-runs" / "lease.json").read_text())
        self.assertEqual(lease["schema_version"], 2)
        self.assertEqual(lease["artifact_kind"], "herdr-controller-lease")
        self.assertEqual([member["task_id"] for member in lease["members"]], ["T02"])
        self.assertEqual(lease["selected_task_ids"], ["T02"])

        probe = type(self)(self._testMethodName)
        probe.setUp()
        try:
            legacy = copy.deepcopy(lease)
            legacy["schema_version"] = 1
            legacy["artifact_kind"] = "herdr-execution-lease"
            (probe.repo / ".herdr-runs" / "lease.json").write_text(json.dumps(legacy), encoding="utf-8")
            (probe.repo / ".herdr-runs" / "lease.json").chmod(0o600)
            self.assertEqual(probe.invoke("preflight")["error"]["code"], "herdr_execution_conflict")
            self.assertFalse(probe.log.exists())
        finally:
            probe.tearDown()

    def test_shell_readiness_busy_and_unavailable_are_typed_and_start_once(self) -> None:
        busy = type(self)(self._testMethodName)
        busy.setUp()
        try:
            busy.env["HERDR_FIXTURE_SCENARIO"] = "agent_pane_busy"
            for command in ("preflight", "allocate"):
                self.assertEqual(busy.invoke(command)["returncode"], 0)
            result = busy.invoke("shell-ready", "--timeout-seconds", "1")
            self.assertEqual(result["error"]["code"], "agent_pane_busy")
            self.assertFalse(any(json.loads(line)[:2] == ["agent", "start"] for line in busy.log.read_text().splitlines()))
        finally:
            busy.tearDown()

        unavailable = type(self)(self._testMethodName)
        unavailable.setUp()
        try:
            unavailable.env["HERDR_FIXTURE_SCENARIO"] = "non-available-shell"
            for command in ("preflight", "allocate"):
                self.assertEqual(unavailable.invoke(command)["returncode"], 0)
            result = unavailable.invoke("shell-ready", "--timeout-seconds", "1")
            self.assertEqual(result["error"]["code"], "shell_readiness_deadline")
            state = json.loads((unavailable.run_dir / "state.json").read_text())
            self.assertEqual(state["phase"], "cleanup-pending")
            self.assertEqual(state["shell_readiness"]["state"], "deadline")
        finally:
            unavailable.tearDown()

        late = type(self)(self._testMethodName)
        late.setUp()
        try:
            late.env["HERDR_FIXTURE_SCENARIO"] = "late-shell"
            for command in ("preflight", "allocate"):
                self.assertEqual(late.invoke(command)["returncode"], 0)
            result = late.invoke("shell-ready", "--timeout-seconds", "1")
            self.assertEqual(result["error"]["code"], "shell_readiness_deadline")
        finally:
            late.tearDown()

        late_poll = type(self)(self._testMethodName)
        late_poll.setUp()
        try:
            late_poll.env["HERDR_FIXTURE_SCENARIO"] = "late-poll-shell"
            for command in ("preflight", "allocate"):
                self.assertEqual(late_poll.invoke(command)["returncode"], 0)
            result = late_poll.invoke("shell-ready", "--timeout-seconds", "1")
            self.assertEqual(result["error"]["code"], "shell_readiness_deadline")
        finally:
            late_poll.tearDown()

    def test_full_fake_protocol_persists_bounded_owner_state(self) -> None:
        self.assertEqual(self.invoke("preflight")["returncode"], 0)
        self.assertEqual(self.invoke("allocate")["returncode"], 0)
        self.assertEqual(self.invoke("start")["returncode"], 0)
        secret_prompt = "inspect only; token=never-persist-this"
        self.assertEqual(
            self.invoke("prompt", "--prompt", secret_prompt)["returncode"], 0
        )
        self.assertEqual(self.invoke("wait", "--timeout-seconds", "2")["returncode"], 0)
        self.assertEqual(self.invoke("collect")["returncode"], 0)
        self.assertEqual(self.invoke("cleanup")["returncode"], 0)
        state = json.loads((self.run_dir / "state.json").read_text(encoding="utf-8"))
        serialized = json.dumps(state)
        self.assertNotIn(secret_prompt, serialized)
        self.assertNotIn("never-persist-this", serialized)
        self.assertEqual(state["phase"], "released")
        self.assertEqual(
            json.loads((self.repo / ".herdr-runs" / "lease.json").read_text())[
                "lease_state"
            ],
            "released",
        )
        calls = [
            json.loads(line)
            for line in self.log.read_text(encoding="utf-8").splitlines()
        ]
        self.assertTrue(
            any(
                call[:4] == ["tab", "create", "--workspace", "w-main"]
                and "--no-focus" in call
                for call in calls
            )
        )
        tab_call = next(call for call in calls if call[:2] == ["tab", "create"])
        blanked = [
            tab_call[index + 1]
            for index, value in enumerate(tab_call[:-1])
            if value == "--env"
        ]
        self.assertTrue(blanked)
        self.assertTrue(all(value.endswith("=") for value in blanked))
        self.assertTrue(
            any(call[:2] == ["agent", "start"] and "--" in call for call in calls)
        )
        start_call = next(call for call in calls if call[:2] == ["agent", "start"])
        native_args = start_call[start_call.index("--") + 1 :]
        self.assertIn("--ask-for-approval", native_args)
        self.assertIn("--sandbox", native_args)
        self.assertIn("agents.enabled=false", native_args)
        self.assertNotIn("--reasoning-effort", native_args)
        self.assertNotIn("--permission-mode", native_args)
        self.assertNotIn("--sandbox-mode", native_args)
        prompt_calls = [call for call in calls if call[:2] == ["agent", "prompt"]]
        self.assertEqual(len(prompt_calls), 1)
        self.assertEqual(prompt_calls[0][2], "w-main:p-child")
        self.assertIn("--wait", prompt_calls[0])
        self.assertNotIn("--no-wait", prompt_calls[0])
        read_call = next(call for call in calls if call[:2] == ["agent", "read"])
        self.assertEqual(read_call[-2:], ["--format", "text"])
        self.assertTrue(self.sentinel.exists())

    def test_missing_environment_is_zero_mutation_and_does_not_run_fixture(
        self,
    ) -> None:
        env = {key: value for key, value in self.env.items() if key != "HERDR_ENV"}
        result = self.invoke("preflight", env=env)
        self.assertEqual(result["returncode"], 2)
        self.assertEqual(result["error"]["code"], "herdr_environment_required")
        self.assertFalse(self.log.exists())
        self.assertFalse((self.repo / ".herdr-runs" / "lease.json").exists())

    def test_prompt_is_single_submit_and_restart_digest_mismatch_is_typed(self) -> None:
        for command in ("preflight", "allocate", "start"):
            self.assertEqual(self.invoke(command)["returncode"], 0)
        self.assertEqual(self.invoke("prompt", "--prompt", "once")["returncode"], 0)
        second = self.invoke("prompt", "--prompt", "twice")
        self.assertEqual(second["error"]["code"], "prompt_already_submitted")
        self.envelope["provenance"]["plan_sha256"] = "c" * 64
        self.envelope_path.write_text(json.dumps(self.envelope), encoding="utf-8")
        resumed = self.invoke("resume")
        self.assertEqual(resumed["returncode"], 2)
        self.assertEqual(resumed["error"]["code"], "restart_mismatch")

    def test_mixed_tab_closes_only_owned_child_and_retains_residue(self) -> None:
        self.env["HERDR_FIXTURE_SCENARIO"] = "mixed"
        for command in ("preflight", "allocate", "start", "prompt"):
            args = ("--prompt", "bounded") if command == "prompt" else ()
            self.assertEqual(self.invoke(command, *args)["returncode"], 0)
        result = self.invoke("cleanup")
        self.assertEqual(result["returncode"], 0)
        state = json.loads((self.run_dir / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["lease_state"], "released")
        self.assertEqual(state["phase"], "cleanup-pending")
        self.assertTrue(state["cleanup_residue"])
        calls = [
            json.loads(line)
            for line in self.log.read_text(encoding="utf-8").splitlines()
        ]
        self.assertFalse(any(call[:2] == ["tab", "close"] for call in calls))
        self.assertIn(["pane", "close", "w-main:p-child"], calls)

    def test_all_bounded_agent_observations_and_cleanup_lease_states(self) -> None:
        expected = {"busy", "idle", "done", "blocked", "unknown"}
        for observation in expected:
            probe = type(self)(self._testMethodName)
            probe.setUp()
            try:
                probe.env["HERDR_FIXTURE_SCENARIO"] = observation
                for command in ("preflight", "allocate", "start", "prompt", "wait"):
                    args = ("--prompt", "bounded") if command == "prompt" else ()
                    result = probe.invoke(command, *args)
                    self.assertEqual(result["returncode"], 0, observation)
                state = json.loads(
                    (probe.run_dir / "state.json").read_text(encoding="utf-8")
                )
                self.assertEqual(state["agent_state"], observation)
                if observation == "busy":
                    blocked_collect = probe.invoke("collect")
                    self.assertEqual(blocked_collect["error"]["code"], "agent_busy")
                cleanup = probe.invoke("cleanup")
                self.assertEqual(cleanup["returncode"], 0, observation)
            finally:
                probe.tearDown()

    def test_prompt_stall_and_wait_timeout_are_typed_cleanup_pending_states(
        self,
    ) -> None:
        stalled = type(self)(self._testMethodName)
        stalled.setUp()
        try:
            stalled.env["HERDR_FIXTURE_SCENARIO"] = "stalled"
            for command in ("preflight", "allocate", "start"):
                self.assertEqual(stalled.invoke(command)["returncode"], 0)
            result = stalled.invoke("prompt", "--prompt", "bounded")
            self.assertEqual(result["error"]["code"], "agent_prompt_stalled")
            state = json.loads(
                (stalled.run_dir / "state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(state["phase"], "cleanup-pending")
        finally:
            stalled.tearDown()

        timed_out = type(self)(self._testMethodName)
        timed_out.setUp()
        try:
            for command in ("preflight", "allocate", "start"):
                self.assertEqual(timed_out.invoke(command)["returncode"], 0)
            self.assertEqual(
                timed_out.invoke("prompt", "--prompt", "bounded")["returncode"], 0
            )
            timed_out.env["HERDR_FIXTURE_SCENARIO"] = "timeout"
            result = timed_out.invoke("wait", "--timeout-seconds", "1")
            self.assertEqual(result["error"]["code"], "agent_timeout")
            state = json.loads(
                (timed_out.run_dir / "state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(state["lease_state"], "cleanup-pending")
        finally:
            timed_out.tearDown()

    def test_grok_binding_and_absolute_explorer_cost_are_runtime_evidence(self) -> None:
        self.envelope["physical_binding"]["agent_kind"] = "grok"
        self.envelope["physical_binding"]["reasoning_effort"] = "medium"
        self.envelope["physical_binding"]["model"] = "grok-4.5"
        self.envelope["physical_binding"]["control_plane_endpoint"] = "native://grok"
        self.envelope["physical_binding"]["credential_ref"] = "native-login/grok"
        self.envelope_path.write_text(json.dumps(self.envelope), encoding="utf-8")
        self.assertEqual(self.invoke("preflight")["returncode"], 0)
        state = json.loads((self.run_dir / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(
            state["physical_binding"]["explorer_cost"]["status"], "absolute-low-cost"
        )
        self.assertEqual(state["physical_binding"]["explorer_cost"]["default_effort"], "low")
        self.assertEqual(state["physical_binding"]["explorer_cost"]["max_effort"], "medium")
        for command in ("allocate", "start"):
            self.assertEqual(self.invoke(command)["returncode"], 0)
        calls = [
            json.loads(line)
            for line in self.log.read_text(encoding="utf-8").splitlines()
        ]
        starts = [call for call in calls if call[:2] == ["agent", "start"]]
        self.assertEqual(starts[0][starts[0].index("--kind") + 1], "grok")
        native_args = starts[0][starts[0].index("--") + 1 :]
        self.assertIn("--reasoning-effort", native_args)
        self.assertIn("--permission-mode", native_args)
        self.assertIn("--disable-web-search", native_args)
        self.assertIn("--no-subagents", native_args)
        self.assertIn("Read,Grep,Glob", native_args)

        for disallowed_effort in ("high", "xhigh"):
            codex = type(self)(self._testMethodName)
            codex.setUp()
            try:
                codex.envelope["physical_binding"]["reasoning_effort"] = disallowed_effort
                codex.envelope_path.write_text(
                    json.dumps(codex.envelope), encoding="utf-8"
                )
                result = codex.invoke("preflight")
                self.assertEqual(
                    result["error"]["code"], "delegated_capability_unavailable"
                )
            finally:
                codex.tearDown()

    def test_all_model_policies_preserve_the_absolute_explorer_ceiling(self) -> None:
        for policy in ("inherit-main", "runtime-default"):
            probe = type(self)(self._testMethodName)
            probe.setUp()
            try:
                probe.envelope["controller"]["model_policy"] = policy
                probe.envelope["physical_binding"]["reasoning_effort"] = "medium"
                probe.envelope_path.write_text(
                    json.dumps(probe.envelope), encoding="utf-8"
                )
                self.assertEqual(probe.invoke("preflight")["returncode"], 0)
                state = json.loads(
                    (probe.run_dir / "state.json").read_text(encoding="utf-8")
                )
                evidence = state["physical_binding"]["explorer_cost"]
                self.assertEqual(evidence["status"], "absolute-low-cost")
                self.assertEqual(evidence["model_policy"], policy)
                probe.envelope["physical_binding"]["reasoning_effort"] = "high"
                probe.envelope_path.write_text(
                    json.dumps(probe.envelope), encoding="utf-8"
                )
                self.assertEqual(
                    probe.invoke("preflight")["error"]["code"],
                    "delegated_capability_unavailable",
                )
            finally:
                probe.tearDown()

    def test_reviewer_requires_codex_sol_high_and_uses_read_only_profile(self) -> None:
        module_spec = importlib.util.spec_from_file_location("herdr_adapter", ADAPTER)
        self.assertIsNotNone(module_spec)
        assert module_spec is not None and module_spec.loader is not None
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        self.envelope["task"].update(
            {
                "task_id": "implementation-review",
                "runtime_role": "reviewer",
                "scope_slice": "bounded implementation review",
                "execution_profile": "deep",
                "reasoning_profile": "deep",
            }
        )
        name = module.derive_agent_name(
            "reviewer", "run-k7", "implementation-review", 1
        )
        self.envelope["physical_binding"].update(
            {
                "agent_name": name,
                "model": "gpt-5.6-sol",
                "reasoning_effort": "high",
            }
        )
        self.env["HERDR_FIXTURE_AGENT_NAME"] = name
        self.envelope_path.write_text(json.dumps(self.envelope), encoding="utf-8")
        self.assertEqual(self.invoke("preflight")["returncode"], 0)
        self.assertEqual(self.invoke("allocate")["returncode"], 0)
        self.assertEqual(self.invoke("start")["returncode"], 0)
        state = json.loads((self.run_dir / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["task"]["runtime_role"], "reviewer")
        self.assertEqual(
            state["physical_binding"]["profile_id"], "codex-delegated-read-only-v1"
        )

    def test_writer_profiles_require_isolated_worktrees_and_native_cli_args(
        self,
    ) -> None:
        module_spec = importlib.util.spec_from_file_location("herdr_adapter", ADAPTER)
        self.assertIsNotNone(module_spec)
        assert module_spec is not None and module_spec.loader is not None
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        cases = (
            (
                "codex",
                "gpt-5.6-luna",
                "xhigh",
                "native://openai",
                "native-login/codex",
            ),
            ("grok", "grok-4.5", "high", "native://grok", "native-login/grok"),
        )
        for kind, model, effort, endpoint, credential_ref in cases:
            probe = type(self)(self._testMethodName)
            probe.setUp()
            try:
                worktree = Path(probe.temp_dir.name) / f"writer-{kind}"
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(probe.repo),
                        "worktree",
                        "add",
                        "--detach",
                        str(worktree),
                        "HEAD",
                    ],
                    check=True,
                    capture_output=True,
                )
                probe.envelope["task"].update(
                    {
                        "runtime_role": "worker",
                        "touch_set": ["src/example.py"],
                        "execution_profile": "balanced",
                        "reasoning_profile": "standard",
                        "isolation": "isolated-worktree",
                    }
                )
                name = module.derive_agent_name("worker", "run-k7", "T02", 1)
                probe.envelope["physical_binding"].update(
                    {
                        "agent_kind": kind,
                        "agent_name": name,
                        "model": model,
                        "reasoning_effort": effort,
                        "permission_mode": "always-approve",
                        "sandbox_mode": "workspace-write",
                        "capability_profile": "delegated-local-writer",
                        "control_plane_endpoint": endpoint,
                        "credential_ref": credential_ref,
                        "checkout_path": str(worktree.resolve()),
                    }
                )
                probe.env["HERDR_FIXTURE_AGENT_NAME"] = name
                probe.env["HERDR_FIXTURE_CWD"] = str(worktree.resolve())
                probe.envelope_path.write_text(
                    json.dumps(probe.envelope), encoding="utf-8"
                )
                for command in ("preflight", "allocate", "start"):
                    self.assertEqual(probe.invoke(command)["returncode"], 0, kind)
                calls = [
                    json.loads(line)
                    for line in probe.log.read_text(encoding="utf-8").splitlines()
                ]
                start = next(call for call in calls if call[:2] == ["agent", "start"])
                native = start[start.index("--") + 1 :]
                self.assertIn("workspace-write", native)
                if kind == "codex":
                    self.assertIn("--ask-for-approval", native)
                    self.assertNotIn("--permission-mode", native)
                else:
                    self.assertIn("acceptEdits", native)
                    self.assertIn("Bash,Read,Write,Edit,Grep,Glob", native)
            finally:
                probe.tearDown()

    def test_live_caller_tab_hierarchy_mismatch_stops_before_lease(self) -> None:
        self.env["HERDR_FIXTURE_CONTEXT_MISMATCH"] = "tab"
        result = self.invoke("preflight")
        self.assertEqual(result["error"]["code"], "caller_context_mismatch")
        self.assertFalse((self.repo / ".herdr-runs" / "lease.json").exists())

    def test_cleanup_revalidates_persisted_caller_terminal_identity(self) -> None:
        self.assertEqual(self.invoke("preflight")["returncode"], 0)
        state_path = self.run_dir / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["caller_context"]["terminal_id"] = "term-recycled"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        state_path.chmod(0o600)
        before = hashlib.sha256(
            (self.repo / ".herdr-runs" / "lease.json").read_bytes()
        ).hexdigest()

        result = self.invoke("cleanup")

        self.assertEqual(result["error"]["code"], "cleanup_identity_mismatch")
        self.assertEqual(
            before,
            hashlib.sha256(
                (self.repo / ".herdr-runs" / "lease.json").read_bytes()
            ).hexdigest(),
        )
        calls = [
            json.loads(line)
            for line in self.log.read_text(encoding="utf-8").splitlines()
        ]
        self.assertFalse(any(call[:2] == ["pane", "list"] for call in calls))
        self.assertFalse(any(call[:2] == ["pane", "close"] for call in calls))
        self.assertFalse(any(call[:2] == ["tab", "close"] for call in calls))

    def test_allocate_persists_tab_before_root_process_identity_failure(self) -> None:
        self.assertEqual(self.invoke("preflight")["returncode"], 0)
        self.env["HERDR_FIXTURE_PROCESS_INFO_FAILURE"] = "w-main:p-root"

        result = self.invoke("allocate")

        self.assertEqual(result["error"]["code"], "herdr_command_failed")
        state = json.loads((self.run_dir / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "cleanup-pending")
        self.assertEqual(state["lease_state"], "cleanup-pending")
        self.assertEqual(state["resources"]["owned_tab_id"], "w-main:t-run")
        self.assertEqual(
            state["resources"]["owned_panes"],
            [
                {
                    "pane_id": "w-main:p-root",
                    "terminal_id": "term-root",
                    "kind": "root",
                    "owned": True,
                    "closed": False,
                }
            ],
        )
        self.assertEqual(
            json.loads((self.repo / ".herdr-runs" / "lease.json").read_text())[
                "lease_state"
            ],
            "cleanup-pending",
        )

    def test_stale_run_cannot_overwrite_a_replaced_repository_lease(self) -> None:
        self.assertEqual(self.invoke("preflight")["returncode"], 0)
        lease_path = self.repo / ".herdr-runs" / "lease.json"
        replacement = json.loads(lease_path.read_text(encoding="utf-8"))
        replacement.update(
            {
                "run_id": "new-owner",
                "controller_id": "new-controller",
                "run_nonce_sha256": "f" * 64,
            }
        )
        lease_path.write_text(json.dumps(replacement), encoding="utf-8")
        lease_path.chmod(0o600)
        before = hashlib.sha256(lease_path.read_bytes()).hexdigest()
        result = self.invoke("cleanup")
        self.assertEqual(result["error"]["code"], "lease_ownership_mismatch")
        self.assertEqual(before, hashlib.sha256(lease_path.read_bytes()).hexdigest())

    def test_lease_conflict_context_and_capability_fail_before_fixture(self) -> None:
        self.assertEqual(self.invoke("preflight")["returncode"], 0)
        conflict = self.invoke("preflight")
        self.assertEqual(conflict["error"]["code"], "herdr_execution_conflict")
        mismatch_env = {
            key: value for key, value in self.env.items() if key != "HERDR_PANE_ID"
        }
        mismatch = self.invoke("resume", env=mismatch_env)
        self.assertEqual(mismatch["error"]["code"], "caller_context_mismatch")

        fresh = type(self)(self._testMethodName)
        fresh.setUp()
        try:
            fresh.envelope["physical_binding"]["sandbox_mode"] = "workspace-write"
            fresh.envelope_path.write_text(json.dumps(fresh.envelope), encoding="utf-8")
            capability = fresh.invoke("preflight")
            self.assertEqual(
                capability["error"]["code"], "controller_binding_capability_mismatch"
            )
            self.assertFalse(fresh.log.exists())
        finally:
            fresh.tearDown()

    def test_owner_only_state_and_precise_run_root(self) -> None:
        self.assertEqual(self.invoke("preflight")["returncode"], 0)
        state_mode = stat.S_IMODE((self.run_dir / "state.json").stat().st_mode)
        lease_mode = stat.S_IMODE(
            (self.repo / ".herdr-runs" / "lease.json").stat().st_mode
        )
        self.assertEqual(state_mode, 0o600)
        self.assertEqual(lease_mode, 0o600)
        self.assertEqual((self.repo / ".herdr-runs").name, ".herdr-runs")

    def test_envelope_identity_mode_location_and_name_are_bound_before_mutation(
        self,
    ) -> None:
        mismatch = type(self)(self._testMethodName)
        mismatch.setUp()
        try:
            mismatch.envelope["physical_binding"]["agent_name"] = "explorer-owl-k7"
            mismatch.envelope_path.write_text(
                json.dumps(mismatch.envelope), encoding="utf-8"
            )
            result = mismatch.invoke("preflight")
            self.assertEqual(result["error"]["code"], "controller_binding_invalid")
            self.assertFalse(mismatch.log.exists())
        finally:
            mismatch.tearDown()

        for mode_case in ("mode", "symlink", "location"):
            probe = type(self)(self._testMethodName)
            probe.setUp()
            try:
                if mode_case == "mode":
                    probe.envelope_path.chmod(0o644)
                elif mode_case == "symlink":
                    target = Path(probe.temp_dir.name) / "envelope-target.json"
                    target.write_text(json.dumps(probe.envelope), encoding="utf-8")
                    target.chmod(0o600)
                    probe.envelope_path.unlink()
                    probe.envelope_path.symlink_to(target)
                else:
                    wrong = (
                        probe.repo / ".herdr-runs" / "wrong" / "controller-binding.json"
                    )
                    wrong.parent.mkdir(parents=True)
                    wrong.write_text(json.dumps(probe.envelope), encoding="utf-8")
                    wrong.chmod(0o600)
                    probe.envelope_path = wrong
                result = probe.invoke("preflight")
                self.assertEqual(
                    result["error"]["code"], "controller_binding_invalid", mode_case
                )
                self.assertFalse(probe.log.exists(), mode_case)
                self.assertFalse(
                    (probe.repo / ".herdr-runs" / "lease.json").exists(), mode_case
                )
            finally:
                probe.tearDown()

        module_spec = importlib.util.spec_from_file_location("herdr_adapter", ADAPTER)
        self.assertIsNotNone(module_spec)
        assert module_spec is not None and module_spec.loader is not None
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        derived = module.derive_agent_name("worker", "r" * 128, "task" * 128, 123)
        self.assertLessEqual(len(derived), 32)
        self.assertTrue(derived.startswith("worker-"))

    def test_released_lease_can_be_replaced_but_stale_or_mismatched_cannot(
        self,
    ) -> None:
        for command in (
            "preflight",
            "allocate",
            "start",
            "prompt",
            "wait",
            "collect",
            "cleanup",
        ):
            args = ("--prompt", "bounded") if command == "prompt" else ()
            self.assertEqual(self.invoke(command, *args)["returncode"], 0)
        self.envelope["controller"]["run_id"] = "run-k8"
        self.envelope["physical_binding"]["agent_name"] = "explorer-otter-23-tt02-a1"
        self.run_dir = self.repo / ".herdr-runs" / "run-k8"
        self.run_dir.mkdir(parents=True)
        self.envelope_path = self.run_dir / "controller-binding.json"
        self.envelope_path.write_text(json.dumps(self.envelope), encoding="utf-8")
        self.envelope_path.chmod(0o600)
        self.env["HERDR_FIXTURE_AGENT_NAME"] = "explorer-otter-23-tt02-a1"
        self.assertEqual(self.invoke("preflight")["returncode"], 0)

        stale = type(self)(self._testMethodName)
        stale.setUp()
        try:
            common_key = hashlib.sha256(
                str((stale.repo / ".git").resolve()).encode()
            ).hexdigest()
            lease = {
                "schema_version": 1,
                "artifact_kind": "herdr-execution-lease",
                "run_id": "old-run",
                "lease_state": "released",
                "repository": str(stale.repo.resolve()),
                "workspace_id": "w-main",
                "controller_id": "old-controller",
                "git_common_dir_sha256": "0" * 64
                if common_key != "0" * 64
                else "1" * 64,
                "plan_sha256": "a" * 64,
                "run_nonce_sha256": "b" * 64,
            }
            (stale.repo / ".herdr-runs" / "lease.json").write_text(
                json.dumps(lease), encoding="utf-8"
            )
            (stale.repo / ".herdr-runs" / "lease.json").chmod(0o600)
            result = stale.invoke("preflight")
            self.assertEqual(result["error"]["code"], "herdr_execution_conflict")
            self.assertFalse(stale.log.exists())
        finally:
            stale.tearDown()

    def prepare_command_job(self) -> None:
        self.envelope["controller"]["binding_kind"] = "command-job"
        self.envelope["task"].update(
            {
                "executor_mode": "main",
                "touch_set": [],
                "resource_locks": ["verification-a"],
            }
        )
        self.envelope["physical_binding"] = {
            key: self.envelope["physical_binding"][key]
            for key in ("terminal_backend", "workspace_id", "tab_id", "pane_id", "checkout_path")
        }
        self.envelope["command_job"] = {
            "cwd": str(self.repo.resolve()),
            "argv": ["printf", "ok"],
            "command": "printf ok",
            "timeout_seconds": 30,
            "max_concurrency": 1,
            "output_bound_bytes": 4096,
            "resource_locks": ["verification-a"],
            "provenance": {"kind": "task", "task_id": "T02"},
        }
        self.envelope["authority"]["denied_capabilities"].append("claim-task-success")
        self.envelope_path.write_text(json.dumps(self.envelope), encoding="utf-8")
        self.envelope_path.chmod(0o600)
        self.env["HERDR_FIXTURE_CWD"] = str(self.repo.resolve())

    def test_command_job_is_separate_pane_run_and_returns_oracle_evidence(self) -> None:
        self.prepare_command_job()
        for command in ("preflight", "allocate", "start", "wait", "collect"):
            result = self.invoke(command, "--timeout-seconds", "2")
            self.assertEqual(result["returncode"], 0, command)
        state = json.loads((self.run_dir / "state.json").read_text(encoding="utf-8"))
        evidence = state["evidence"][0]
        self.assertEqual(state["binding_kind"], "command-job")
        self.assertEqual(evidence["exit_code"], 0)
        self.assertIsInstance(evidence["process"]["pid"], int)
        self.assertEqual(
            evidence["process"]["argv_sha256"],
            hashlib.sha256(b'["printf","ok"]').hexdigest(),
        )
        self.assertTrue(evidence["oracle_judgment_required"])
        self.assertFalse(evidence["task_success_claim"])
        self.assertNotIn("fixture-secret", json.dumps(state))
        self.assertNotIn("fixture-password", json.dumps(state))
        calls = [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]
        run_calls = [call for call in calls if call[:2] == ["pane", "run"]]
        self.assertEqual(len(run_calls), 1)
        self.assertEqual(len(run_calls[0]), 4)
        self.assertEqual(run_calls[0][2], "w-main:p-child")
        self.assertTrue(run_calls[0][3].startswith("/bin/sh -c "))
        self.assertNotIn("--pane", run_calls[0][3])
        self.assertNotIn("--cwd", run_calls[0][3])
        self.assertFalse(any(call[:2] == ["pane", "run"] and len(call) != 4 for call in calls))
        wait_calls = [call for call in calls if call[:2] == ["pane", "wait-output"]]
        self.assertEqual(wait_calls[0][2], "w-main:p-child")
        self.assertIn("--match", wait_calls[0])
        self.assertFalse(any(call[:2] == ["agent", "start"] for call in calls))
        self.assertFalse(any(call[:2] == ["agent", "prompt"] for call in calls))
        self.assertEqual(self.invoke("cleanup")["returncode"], 0)

    def test_command_gate_capacity_admits_only_the_controller_issued_width(self) -> None:
        first = self
        first.prepare_command_job()
        first.envelope["task"]["resource_locks"] = ["verification-a", "verification-b"]
        first.envelope["command_job"].update(
            {
                "max_concurrency": 2,
                "provenance": {"kind": "gate", "gate_id": "gate-a"},
            }
        )
        first.envelope_path.write_text(json.dumps(first.envelope), encoding="utf-8")
        self.assertEqual(first.invoke("preflight")["returncode"], 0)

        second = type(self)(self._testMethodName)
        second.setUp()
        try:
            second.repo = first.repo
            second.run_dir = first.repo / ".herdr-runs" / "run-k8"
            second.run_dir.mkdir(parents=True)
            second.envelope = copy.deepcopy(first.envelope)
            second.envelope["controller"].update({"run_id": "run-k8", "run_nonce": "nonce-fresh-k8"})
            second.envelope["command_job"].update(
                {
                    "resource_locks": ["verification-b"],
                    "provenance": {"kind": "gate", "gate_id": "gate-b"},
                }
            )
            second.envelope_path = second.run_dir / "controller-binding.json"
            second.envelope_path.write_text(json.dumps(second.envelope), encoding="utf-8")
            second.envelope_path.chmod(0o600)
            self.assertEqual(second.invoke("preflight")["returncode"], 0)

            third = type(self)(self._testMethodName)
            third.setUp()
            try:
                third.repo = first.repo
                third.run_dir = first.repo / ".herdr-runs" / "run-k9"
                third.run_dir.mkdir(parents=True)
                third.envelope = copy.deepcopy(first.envelope)
                third.envelope["controller"].update({"run_id": "run-k9", "run_nonce": "nonce-fresh-k9"})
                third.envelope["command_job"].update(
                    {
                        "resource_locks": ["verification-c"],
                        "provenance": {"kind": "gate", "gate_id": "gate-c"},
                    }
                )
                third.envelope["task"]["resource_locks"].append("verification-c")
                third.envelope_path = third.run_dir / "controller-binding.json"
                third.envelope_path.write_text(json.dumps(third.envelope), encoding="utf-8")
                third.envelope_path.chmod(0o600)
                self.assertEqual(third.invoke("preflight")["error"]["code"], "batch_width_exhausted")
            finally:
                third.tearDown()
        finally:
            second.tearDown()

    def test_command_job_rejects_injection_foreign_cwd_and_missing_locks(self) -> None:
        for mutation, expected in (
            (
                lambda envelope: envelope["command_job"].update(
                    {"command": "printf ok; touch injected"}
                ),
                "controller_binding_invalid",
            ),
            (
                lambda envelope: envelope["command_job"].update({"cwd": "/tmp"}),
                "controller_binding_cwd_mismatch",
            ),
            (
                lambda envelope: envelope["command_job"].update({"resource_locks": []}),
                "resource_lock_required",
            ),
            (
                lambda envelope: envelope["command_job"].update(
                    {"argv": ["printf", "ok; touch injected"]}
                ),
                "controller_binding_invalid",
            ),
            (
                lambda envelope: envelope["command_job"].update(
                    {"task_success_claim": True}
                ),
                "controller_binding_invalid",
            ),
            (
                lambda envelope: envelope["authority"]["denied_capabilities"].remove(
                    "claim-task-success"
                ),
                "controller_binding_authority_denied",
            ),
        ):
            probe = type(self)(self._testMethodName)
            probe.setUp()
            try:
                probe.prepare_command_job()
                mutation(probe.envelope)
                probe.envelope_path.write_text(json.dumps(probe.envelope), encoding="utf-8")
                result = probe.invoke("preflight")
                self.assertEqual(result["error"]["code"], expected)
                self.assertFalse(probe.log.exists())
            finally:
                probe.tearDown()

    def test_command_job_nonzero_and_timeout_remain_controller_evidence(self) -> None:
        nonzero = type(self)(self._testMethodName)
        nonzero.setUp()
        try:
            nonzero.prepare_command_job()
            nonzero.env["HERDR_FIXTURE_SCENARIO"] = "command-nonzero"
            for command in ("preflight", "allocate", "start", "wait", "collect"):
                result = nonzero.invoke(command, "--timeout-seconds", "2")
                self.assertEqual(result["returncode"], 0, command)
            state = json.loads((nonzero.run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["evidence"][0]["exit_code"], 7)
            self.assertFalse(state["evidence"][0]["task_success_claim"])
        finally:
            nonzero.tearDown()

        timed_out = type(self)(self._testMethodName)
        timed_out.setUp()
        try:
            timed_out.prepare_command_job()
            timed_out.env["HERDR_FIXTURE_SCENARIO"] = "command-timeout"
            for command in ("preflight", "allocate"):
                self.assertEqual(timed_out.invoke(command)["returncode"], 0)
            result = timed_out.invoke("start")
            self.assertEqual(result["error"]["code"], "command_timeout")
            state = json.loads((timed_out.run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["phase"], "cleanup-pending")
            self.assertEqual(state["lease_state"], "cleanup-pending")
        finally:
            timed_out.tearDown()

    def test_command_output_bound_is_bytes_and_preserves_valid_utf8(self) -> None:
        self.prepare_command_job()
        self.envelope["command_job"]["output_bound_bytes"] = 5
        self.envelope_path.write_text(json.dumps(self.envelope), encoding="utf-8")
        self.env["HERDR_FIXTURE_SCENARIO"] = "command-unicode"
        for command in ("preflight", "allocate", "start", "collect"):
            result = self.invoke(command)
            self.assertEqual(result["returncode"], 0, command)
        state = json.loads((self.run_dir / "state.json").read_text(encoding="utf-8"))
        preview = state["evidence"][0]["output_preview"]
        self.assertLessEqual(len(preview.encode("utf-8")), 5)
        preview.encode("utf-8").decode("utf-8")

class HerdrWorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        with SKILLS_CONTRACT.open("rb") as handle:
            self.contract = tomllib.load(handle)
        with ROUTING_CONTRACT.open("rb") as handle:
            self.routing = tomllib.load(handle)
        self.plan_text = PLAN_SKILL.read_text(encoding="utf-8")
        self.implement_text = IMPLEMENT_SKILL.read_text(encoding="utf-8")

    def test_manifest_is_an_explicit_non_lifecycle_overlay(self) -> None:
        manifest = self.contract["skills"]["implement-change-via-herdr"]
        self.assertEqual(
            {
                "source": "src/skills/tools/implement-change-via-herdr",
                "public_id": "implement-change-via-herdr",
                "category": "tool",
                "install": ["claude", "codex", "root-flat"],
                "lifecycle_owner": False,
                "activation_mode": "explicit",
                "default_role": "overlay",
                "may_mutate_repo": True,
                "may_spawn_agent": True,
                "requires_explicit_user_request": True,
                "requires_approved_plan": True,
                "semantic_requires": ["implement-change"],
            },
            manifest,
        )
        self.assertNotIn("runtime_bundle", manifest)
        self.assertIn(
            "implement-change-via-herdr",
            self.contract["skills"]["use-coding-skills"]["semantic_requires"],
        )
        self.assertTrue(self.contract["skills"]["implement-change"]["lifecycle_owner"])

    def test_explicit_route_composes_controller_and_preserves_phase_routes(
        self,
    ) -> None:
        phase_routes = self.routing["phase_routes"]
        self.assertEqual("implement-change", phase_routes["execute"])
        self.assertEqual("implement-change", phase_routes["verify"])
        explicit = [
            case
            for case in self.routing["trigger_cases"]
            if case["id"] == "explicit-via-herdr-approved-plan-execution"
        ]
        self.assertEqual(1, len(explicit))
        case = explicit[0]
        self.assertEqual("implement-change-via-herdr", case["owner"])
        self.assertNotIn("overlays", case)
        self.assertTrue(
            any("implement-change-via-herdr" in value for value in case["positive"])
        )
        self.assertTrue(
            any("ordinary controller runtime" in value for value in case["negative"])
        )
        self.assertTrue(any("choose tasks" in value for value in case["negative"]))

    def test_plan_keeps_provider_neutral_profiles_and_cheap_explorer_boundary(
        self,
    ) -> None:
        for field in (
            "execution_profile",
            "reasoning_profile",
            "semantic-routing",
            "inherit-main",
            "runtime-default",
        ):
            self.assertIn(field, self.plan_text)
        for phrase in (
            "pure repository search and factual confirmation",
            "execution_profile: fast",
            "reasoning_profile: light",
            "isolation: shared-read-only",
            "deeper synthesis",
            "not an explorer",
        ):
            self.assertIn(phrase, self.plan_text)
        for provider_name in ("Codex", "Grok", "Claude", "Herdr"):
            self.assertNotIn(provider_name, self.plan_text)

    def test_implementation_binding_and_one_controller_boundaries_are_explicit(
        self,
    ) -> None:
        for role in ("orchestrator", "reviewer", "explorer", "worker"):
            self.assertIn(role, self.implement_text)
        for binding in (
            "concrete CLI",
            "model",
            "reasoning effort",
            "permission mode",
            "sandbox mode",
            "worktree",
            "Herdr workspace/tab/pane/agent IDs",
            "runtime evidence",
            "approved task IDs",
            "DAG topology",
            "inherit-main",
            "runtime-default",
        ):
            self.assertIn(binding, self.implement_text)
        for boundary in (
            "candidate findings only",
            "must not delegate recursively",
            "bounded read-only",
            "isolated, task-scoped worktree",
            "main controller alone",
            "converges batches",
            "adjudicates review",
            "repairs accepted findings",
            "continues the approved plan",
            "routes truth sync or close",
            "external authority",
        ):
            self.assertIn(boundary, self.implement_text)
        self.assertNotIn("lifecycle_owner = true", self.implement_text)


if __name__ == "__main__":
    unittest.main()
