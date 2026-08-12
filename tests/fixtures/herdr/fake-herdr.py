#!/usr/bin/env python3
"""Deterministic Herdr 0.8 protocol fixture; never opens a live Herdr socket."""

from __future__ import annotations

import json
import os
import sys
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
                    "tab_id": "w-main:t-run",
                    "label": "fixture-run",
                    "pane_count": 1,
                },
                "root_pane": pane("w-main:p-root", "w-main:t-run", "term-root"),
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
                "pane": pane("w-main:p-child", "w-main:t-run", "term-child"),
            }
        )
    elif argv[:2] == ["pane", "get"]:
        pane_id = argv[2]
        if pane_id == caller_pane:
            selected = pane(caller_pane, caller_tab, "term-main", agent=True)
            selected["name"] = "orchestrator-fixture"
            if os.environ.get("HERDR_FIXTURE_CONTEXT_MISMATCH") == "tab":
                selected["tab_id"] = "w-main:t-other"
        elif pane_id == "w-main:p-root":
            selected = pane(pane_id, "w-main:t-run", "term-root")
        else:
            selected = pane(
                pane_id,
                "w-main:t-run",
                "term-child",
                agent=was_called(["agent", "start"]),
            )
        result({"type": "pane_info", "pane": selected})
    elif argv[:2] == ["pane", "process-info"]:
        pane_id = argv[argv.index("--pane") + 1]
        failure_target = os.environ.get("HERDR_FIXTURE_PROCESS_INFO_FAILURE")
        if failure_target == pane_id:
            print("fixture process-info failure", file=sys.stderr)
            return 1
        shell_pid = 101 if pane_id == "w-main:p-root" else 102
        processes: list[dict[str, object]] = [
            {
                "argv": ["-zsh"],
                "argv0": "zsh",
                "cmdline": "-zsh",
                "name": "zsh",
                "pid": shell_pid,
            }
        ]
        if pane_id == "w-main:p-child" and was_called(["agent", "start"]):
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
        if not was_called(["tab", "close", "w-main:t-run"]):
            if not was_called(["pane", "close", "w-main:p-root"]):
                panes.append(pane("w-main:p-root", "w-main:t-run", "term-root"))
            if not was_called(["pane", "close", "w-main:p-child"]):
                panes.append(
                    pane(
                        "w-main:p-child",
                        "w-main:t-run",
                        "term-child",
                        agent=was_called(["agent", "start"]),
                    )
                )
            if scenario() == "mixed":
                unowned = pane("w-main:p-unowned", "w-main:t-run", "term-unowned")
                unowned["agent"] = "claude"
                unowned["name"] = "unowned-agent"
                panes.append(unowned)
        result({"type": "pane_list", "panes": panes})
    elif argv[:2] == ["agent", "start"]:
        kind = argv[argv.index("--kind") + 1]
        native = argv[argv.index("--") + 1 :]
        selected = pane("w-main:p-child", "w-main:t-run", "term-child", agent=True)
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
        selected = pane("w-main:p-child", "w-main:t-run", "term-child", agent=True)
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
                    "w-main:p-child", "w-main:t-run", "term-child", agent=True
                ),
            }
        )
    elif argv[:2] == ["agent", "get"]:
        result(
            {
                "type": "agent_info",
                "agent": pane(
                    "w-main:p-child", "w-main:t-run", "term-child", agent=True
                ),
            }
        )
    elif argv[:2] == ["agent", "read"]:
        print("fixture completion evidence")
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
