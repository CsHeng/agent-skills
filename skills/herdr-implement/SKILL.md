---
name: herdr-implement
description: "Use when the user asks to hand an established plan to another main coding agent through Herdr for implementation and return it to the current main for review and repair rounds."
---

# Herdr Implement

Manage handoff prompts between two main coding-agent sessions. Main A is the current session; main B implements the established plan. Compose `$herdr` for native terminal and agent operations, `$implement-change` for B's implementation, and `$review-implementation` for A's review. Each main decides how to use its own native subagents; this Skill manages only the main-to-main exchange.

## Inputs And Defaults

- Require the selected coding CLI: `pi`, `codex`, `claude`, `cursor-agent` or `grok`. Accept an unambiguous user-facing alias; Herdr's kind for Cursor Agent is `cursor`.
- Use the current conversation's established plan unless the user supplies another. Include conversation-only decisions and any uncommitted context the other session needs; an inaccessible path is not a supplied plan.
- `model` and `thinking` are optional. Omit their native options when absent, preserving the selected CLI's defaults. Read the selected client's entry in [CLI Options](references/cli-options.md) and verify current help when needed. Do not silently substitute an explicit model or discard unsupported thinking.
- Review defaults on. `rounds` is a positive integer, default `3`. One round is B's implementation or repair followed by A's review, including the first implementation. Internal subagent turns, tests, self-repairs, waits and clarifications do not consume outer rounds. An explicit no-review request uses one implementation return without claiming review.
- Use native skip-permission or allow-all execution for the selected CLI and each main's subagents. Requesting this mode authorizes direct execution of the established task; do not add another plan-approval exchange. Carry any project-specific gate instruction as ordinary handoff context, without a generic permission protocol. Keep the user's actual task and explicit exclusions intact.

## Prepare The Main Sessions

Read `$herdr` and verify its environment requirement before control commands. If its installed Skill is unavailable, obtain the tool guidance from `herdr --skill`. Use the installed CLI's command help and returned identifiers, not guessed pane IDs or controls.

This main-to-main mode uses native `agent start`, `prompt`, `wait`, `get` and `read`. Its current-checkout and automatic-approval defaults govern this invocation; generic managed-worker handoff defaults do not add a bridge, mandatory worktree, session-ID initialization turn or another permission question.

Default to the current checkout and alternate implementation with review. While B writes and checks, A leaves those files alone. Before A reviews, B settles its writing and write-producing subagents. Choose a worktree only for an actual isolation need or explicit request, using the existing worktree method. A dirty checkout alone does not require isolation or a preliminary commit.

Use a suitable explicitly named pane or create one adjacent pane through `$herdr`, retaining the caller's focus. Start B with a useful unique name, the intended cwd and the selected native options. Record which pane and agent this invocation created. Never replace unrelated work merely to obtain an available pane.

B is a main session: it owns implementation choices, verification and internal delegation for the supplied plan. A owns the outer handoff loop, its review and the final response. Neither main needs the other's subagent registry. A may also delegate review work; a review evaluator remains read-only.

## Implement, Review And Continue

Send B a compact handoff that invokes `$implement-change`, supplies the plan and necessary rationale, identifies acceptance and existing work to preserve, and requests implementation plus actual verification. Tell B that A will perform `$review-implementation` in this loop and that B may use native subagents with skip permissions. Ensure the named Skills are discoverable by B or supply their essential guidance through readable sources.

An initial prompt can say:

> Use `$implement-change` to implement this established plan directly: [plan and relevant context]. Use native subagents as you judge useful, with skip permissions. Implement and verify, then return changes, checks and unresolved questions for my `$review-implementation`. Settle writing before returning.

Wait and inspect through `$herdr`. An idle/done state or successful process is an observation point, not an accepted result. Read the actual return and changed files. A transport timeout does not cancel B or start another implementation; inspect its current state and continue waiting when it is still working. If terminal history truncates the result, use `$herdr`'s full-result-file fallback.

When B is blocked, read the question before responding. Resolve routine execution or approval prompts using the selected automatic-approval mode and existing task instructions. Return to the user only for an actual missing decision or unavailable prerequisite; do not blindly answer an unknown dialog.

Review the stable candidate with `$review-implementation`, checking the real diff, acceptance and applicable verification. On follow-up, include earlier findings, B's dispositions and the new changes so review can focus on unresolved issues and affected regressions. If findings need a further implementation turn and rounds remain, send them to the same main B:

> Continue `$implement-change` in this session. This is round N of M. Here are the `$review-implementation` findings and evidence: [findings]. Adjudicate them, repair the supported issues, run affected checks and return the result, explaining any disputed finding.

B judges findings against the plan and evidence; it does not apply every suggestion mechanically. A considers any dispute in the next review. Preserve the original goals and still-valid decisions rather than repeating a full design or audit on every round.

Prefer the same live main sessions throughout. If B exits, use a supported native continuation with its explicit session identity, or clearly describe reconstruction from retained context. Never resume an arbitrary latest session. A remains active while coordinating; this Skill does not promise to wake an ended conversation.

## Finish

Finish when the requested implementation and verification are supported and review has no unresolved supported finding. Report the actual implementation result, review outcome, rounds used and any remaining gap. With review disabled, identify that limit explicitly.

At the round limit, preserve the work and report remaining findings and the exhausted budget. Do not claim success or silently start another round through a replacement agent or local takeover. A genuine missing decision can stop the affected work earlier; ordinary test failures can be repaired within B's implementation turn.

Use `$herdr`'s ownership rules to close only resources created for this invocation after successful completion. Keep unfinished work and useful continuation context. For a reused user pane, preserve that pane and its unrelated state. No commit, worktree deletion or installation is necessary merely to return a result.
