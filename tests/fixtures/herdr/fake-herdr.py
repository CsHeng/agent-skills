#!/usr/bin/env python3
"""Deterministic Herdr 0.8 protocol fixture; never opens a live Herdr socket."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
from pathlib import Path


def log_path() -> Path | None:
    value = os.environ.get("HERDR_FIXTURE_LOG")
    return Path(value) if value else None


def prior_calls() -> list[list[str]]:
    path = log_path()
    if path is None or not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def log_call(argv: list[str]) -> None:
    path = log_path()
    if path is not None:
        with path.open("a", encoding="utf-8") as stream:
            json.dump(argv, stream, separators=(",", ":"))
            stream.write("\n")


def result(value: dict[str, object]) -> None:
    print(json.dumps({"id": "fixture", "result": value}, separators=(",", ":")))


def scenario() -> str:
    return os.environ.get("HERDR_FIXTURE_SCENARIO", "done")


def was_called(prefix: list[str]) -> bool:
    return any(call[: len(prefix)] == prefix for call in prior_calls())


def selected_kind() -> str:
    for call in reversed(prior_calls()):
        if call[:2] == ["agent", "start"]:
            return call[call.index("--kind") + 1]
    return "codex"


def agent_state() -> str:
    if not was_called(["agent", "prompt"]):
        return "idle"
    selected = scenario()
    if selected == "busy":
        return "working"
    if selected in {"idle", "done", "blocked", "unknown"}:
        return selected
    return "done"


def owned_tab_id() -> str:
    return os.environ.get("HERDR_FIXTURE_OWNED_TAB_ID", "w-main:t-run")


def root_pane_id() -> str:
    return os.environ.get("HERDR_FIXTURE_ROOT_PANE_ID", "w-main:p-root")


def child_pane_id() -> str:
    return os.environ.get("HERDR_FIXTURE_CHILD_PANE_ID", "w-main:p-child")


def command_run_call() -> list[str] | None:
    for call in reversed(prior_calls()):
        if call[:2] == ["pane", "run"]:
            return call
    return None


def command_marker() -> str:
    call = command_run_call()
    if call is None:
        return ""
    command = call[3] if len(call) > 3 else ""
    match = re.search(r"(?P<left>HBU040_)\s+(?P<right>[a-f0-9]+_DONE:)", command)
    return f"{match.group('left')}{match.group('right')}" if match else ""


def command_start_marker() -> str:
    call = command_run_call()
    if call is None:
        return ""
    command = call[3] if len(call) > 3 else ""
    match = re.search(r"(?P<left>HBU040_)\s+(?P<right>[a-f0-9]+_START:)", command)
    return f"{match.group('left')}{match.group('right')}" if match else ""


def pane(
    pane_id: str,
    tab_id: str,
    terminal_id: str,
    *,
    agent: bool = False,
) -> dict[str, object]:
    value: dict[str, object] = {
        "agent_status": agent_state() if agent else "unknown",
        "cwd": os.environ.get("HERDR_FIXTURE_CWD", "/fixture/repo"),
        "focused": False,
        "foreground_cwd": os.environ.get("HERDR_FIXTURE_CWD", "/fixture/repo"),
        "pane_id": pane_id,
        "revision": 1,
        "tab_id": tab_id,
        "terminal_id": terminal_id,
        "workspace_id": os.environ.get("HERDR_WORKSPACE_ID", "w-main"),
    }
    if agent:
        kind = selected_kind()
        value.update(
            {
                "agent": kind,
                "agent_session": {
                    "agent": kind,
                    "kind": "id",
                    "source": f"herdr:{kind}",
                    "value": "agent-session-run",
                },
                "interactive_ready": True,
                "name": os.environ.get("HERDR_FIXTURE_AGENT_NAME"),
            }
        )
    return value


def main() -> int:
    argv = sys.argv[1:]
    log_call(argv)
    if os.environ.get("HERDR_FIXTURE_SENTINEL"):
        Path(os.environ["HERDR_FIXTURE_SENTINEL"]).write_text(
            "fixture-used\n", encoding="utf-8"
        )
    workspace_id = os.environ.get("HERDR_WORKSPACE_ID", "w-main")
    caller_tab = os.environ.get("HERDR_TAB_ID", "w-main:t-main")
    caller_pane = os.environ.get("HERDR_PANE_ID", "w-main:p-main")
    if argv[:2] == ["workspace", "get"]:
        result(
            {
                "type": "workspace_info",
                "workspace": {
                    "workspace_id": argv[2],
                    "active_tab_id": caller_tab,
                    "pane_count": 3,
                    "tab_count": 2,
                },
            }
        )
    elif argv[:2] == ["tab", "create"]:
        result(
            {
                "type": "tab_created",
                "tab": {
                    "workspace_id": workspace_id,
                    "tab_id": owned_tab_id(),
                    "label": "fixture-run",
                    "pane_count": 1,
                },
                "root_pane": pane(root_pane_id(), owned_tab_id(), "term-root"),
            }
        )
    elif argv[:2] == ["tab", "get"]:
        tab_id = argv[2]
        result(
            {
                "type": "tab_info",
                "tab": {
                    "workspace_id": workspace_id,
                    "tab_id": tab_id,
                    "label": "caller" if tab_id == caller_tab else "fixture-run",
                    "pane_count": 1 if tab_id == caller_tab else 2,
                },
            }
        )
    elif argv[:2] == ["pane", "split"]:
        result(
            {
                "type": "pane_info",
                "pane": pane(child_pane_id(), owned_tab_id(), "term-child"),
            }
        )
    elif argv[:2] == ["pane", "get"]:
        pane_id = argv[2]
        if pane_id == caller_pane:
            selected = pane(caller_pane, caller_tab, "term-main", agent=True)
            selected["name"] = "orchestrator-fixture"
            if os.environ.get("HERDR_FIXTURE_CONTEXT_MISMATCH") == "tab":
                selected["tab_id"] = "w-main:t-other"
        elif pane_id == root_pane_id():
            selected = pane(pane_id, owned_tab_id(), "term-root")
        else:
            selected = pane(
                pane_id,
                owned_tab_id(),
                "term-child",
                agent=was_called(["agent", "start"]),
            )
        result({"type": "pane_info", "pane": selected})
    elif argv[:2] == ["pane", "process-info"]:
        pane_id = argv[argv.index("--pane") + 1]
        if scenario() == "late-poll-shell" and pane_id == child_pane_id():
            time.sleep(1.1)
        failure_target = os.environ.get("HERDR_FIXTURE_PROCESS_INFO_FAILURE")
        if failure_target == pane_id:
            print("fixture process-info failure", file=sys.stderr)
            return 1
        shell_pid = 101 if pane_id == root_pane_id() else 102
        processes: list[dict[str, object]] = [
            {
                "argv": ["-zsh"],
                "argv0": "zsh",
                "cmdline": "-zsh",
                "name": "zsh",
                "pid": shell_pid,
            }
        ]
        if pane_id == child_pane_id() and scenario() in {
            "agent_pane_busy",
            "pane_busy",
        } and not was_called(["agent", "start"]):
            processes = [
                {
                    "argv": ["codex"],
                    "argv0": "codex",
                    "cmdline": "codex --existing-turn",
                    "name": "codex",
                    "pid": 202,
                }
            ]
        elif pane_id == child_pane_id() and (
            scenario() in {
                "non-available-shell",
                "shell-unavailable",
                "reviewer-no-shell",
            }
            and not was_called(["agent", "start"])
            or scenario() == "late-shell"
            and len(
                [
                    call
                    for call in prior_calls()
                    if call[:2] == ["pane", "process-info"]
                ]
            )
            <= 7
        ):
            processes = [
                {
                    "argv": ["login"],
                    "argv0": "login",
                    "cmdline": "login",
                    "name": "login",
                    "pid": 202,
                }
            ]
        elif pane_id == child_pane_id() and was_called(["agent", "start"]):
            start = next(
                call
                for call in reversed(prior_calls())
                if call[:2] == ["agent", "start"]
            )
            kind = start[start.index("--kind") + 1]
            native = start[start.index("--") + 1 :]
            processes = [
                {
                    "argv": [kind, *native],
                    "argv0": kind,
                    "cmdline": "fixture-agent",
                    "name": kind,
                    "pid": 202,
                }
            ]
        elif pane_id == child_pane_id() and command_run_call() is not None and scenario() in {"command-running", "command_running", "long-command"}:
            run_call = command_run_call()
            assert run_call is not None
            command_argv = shlex.split(run_call[3])
            processes = [
                {
                    "argv": command_argv,
                    "argv0": command_argv[0],
                    "cmdline": " ".join(command_argv),
                    "name": command_argv[0],
                    "pid": 303,
                }
            ]
        result(
            {
                "type": "pane_process_info",
                "process_info": {
                    "pane_id": pane_id,
                    "shell_pid": shell_pid,
                    "foreground_processes": processes,
                },
            }
        )
    elif argv[:2] == ["pane", "list"]:
        panes: list[dict[str, object]] = []
        if not was_called(["tab", "close", owned_tab_id()]):
            if not was_called(["pane", "close", root_pane_id()]):
                panes.append(pane(root_pane_id(), owned_tab_id(), "term-root"))
            if not was_called(["pane", "close", child_pane_id()]):
                panes.append(
                    pane(
                        child_pane_id(),
                        owned_tab_id(),
                        "term-child",
                        agent=was_called(["agent", "start"]),
                    )
                )
            if scenario() == "mixed":
                unowned = pane("w-main:p-unowned", owned_tab_id(), "term-unowned")
                unowned["agent"] = "claude"
                unowned["name"] = "unowned-agent"
                panes.append(unowned)
        result({"type": "pane_list", "panes": panes})
    elif argv[:2] == ["pane", "run"]:
        if len(argv) != 4:
            print("legacy pane run flags are unsupported", file=sys.stderr)
            return 1
    elif argv[:2] == ["pane", "wait-output"]:
        match_value = argv[argv.index("--match") + 1]
        if scenario() in {"command-timeout", "command_timeout"} and match_value == command_marker():
            print("timeout", file=sys.stderr)
            return 1
        print()
    elif argv[:2] == ["agent", "start"]:
        kind = argv[argv.index("--kind") + 1]
        native = argv[argv.index("--") + 1 :]
        selected = pane(child_pane_id(), owned_tab_id(), "term-child", agent=True)
        selected["agent"] = kind
        selected["name"] = argv[2]
        selected.pop("agent_session", None)
        selected["agent_status"] = "idle"
        result(
            {
                "type": "agent_started",
                "agent": selected,
                "argv": [kind, *native],
            }
        )
    elif argv[:2] == ["agent", "prompt"]:
        if scenario() == "stalled":
            print("agent_prompt_stalled", file=sys.stderr)
            return 1
        selected = pane(child_pane_id(), owned_tab_id(), "term-child", agent=True)
        selected["agent_status"] = "working"
        result({"type": "agent_prompted", "agent": selected})
    elif argv[:2] == ["agent", "wait"]:
        if scenario() == "timeout":
            print("timeout", file=sys.stderr)
            return 1
        result(
            {
                "type": "agent_info",
                "agent": pane(
                    child_pane_id(), owned_tab_id(), "term-child", agent=True
                ),
            }
        )
    elif argv[:2] == ["agent", "get"]:
        result(
            {
                "type": "agent_info",
                "agent": pane(
                    child_pane_id(), owned_tab_id(), "term-child", agent=True
                ),
            }
        )
    elif argv[:2] == ["agent", "read"]:
        print("fixture completion evidence")
    elif argv[:2] == ["pane", "read"]:
        exit_code = 7 if scenario() in {"command-nonzero", "command_nonzero"} else 0
        command_output = "🙂🙂" if scenario() == "command-unicode" else "fixture command output token=fixture-secret"
        print(
            f"{command_output}\n"
            f"{command_start_marker()}303:PID\n{command_marker()}{exit_code}:END"
        )
    elif argv[:2] == ["pane", "close"]:
        result({"type": "pane_closed", "pane_id": argv[2]})
    elif argv[:2] == ["tab", "close"]:
        result({"type": "tab_closed", "tab_id": argv[2]})
    else:
        print(json.dumps({"error": f"unsupported fixture argv: {argv}"}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
