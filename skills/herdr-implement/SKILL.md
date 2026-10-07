---
name: herdr-implement
description: "Use when the user asks to hand an established plan to another main coding agent through Herdr for implementation and return it to the current main for review and repair rounds."
---

# Herdr Implement

Manage handoff prompts between two main coding-agent sessions. Main A is the current session; main B implements the established plan. Compose `$herdr` for native terminal and agent operations, `$implement-change` for B's implementation, and `$review-implementation` for A's review. Each main decides how to use its own native subagents; this Skill manages only the main-to-main exchange.

## Inputs And Defaults

- Require the selected coding CLI: `pi`, `codex`, `claude`, `cursor-agent` or `grok`. Accept an unambiguous user-facing alias and resolve its current Herdr support through `$herdr`.
- Use the current conversation's established plan unless the user supplies another. Include conversation-only decisions and any uncommitted context the other session needs; an inaccessible path is not a supplied plan.
- `model` and `thinking` are optional. Preserve the selected CLI's defaults when absent. Resolve explicit overrides through current tool guidance; do not silently substitute a model, discard unsupported thinking or change persistent client settings to force an invocation override. Report an unsupported request for resolution.
- Review defaults on. `rounds` is a positive integer, default `3`. One round is B's implementation or repair followed by A's review, including the first implementation. Internal subagent turns, tests, self-repairs, waits and clarifications do not consume outer rounds. An explicit no-review request uses one implementation return without claiming review.
- Use native skip-permission or allow-all execution for the selected CLI and each main's subagents. Requesting this mode authorizes direct execution of the established task; do not add another plan-approval exchange. Carry any project-specific gate instruction as ordinary handoff context, without a generic permission protocol. Keep the user's actual task and explicit exclusions intact.

## Prepare The Main Sessions

Read the current `$herdr` Skill and satisfy its environment requirements before operating Herdr. That Skill owns Herdr operations and discovery; the selected coding agent's current guidance owns its native launch, permission, model and thinking options. Resolve invocation details from those sources rather than relying on remembered syntax or version-specific mappings.

Use Herdr's existing capabilities to launch, communicate with and observe the main sessions. This workflow's current-checkout and automatic-approval defaults govern the invocation; generic managed-worker defaults do not require a custom bridge, worktree, initialization turn or another permission question.

Default to the current checkout and alternate implementation with review. While B writes and checks, A leaves those files alone. Before A reviews, B settles its writing and write-producing subagents. Choose a worktree only for an actual isolation need or explicit request, using the existing worktree method. A dirty checkout alone does not require isolation or a preliminary commit.

Use a suitable explicitly named pane or create one adjacent pane through `$herdr`, retaining the caller's focus. Start B in the intended working directory with the selected settings and retain its actual identity for subsequent handoffs. Record which pane and agent this invocation created. Never replace unrelated work merely to obtain an available pane.

B is a main session: it owns implementation choices, verification and internal delegation for the supplied plan. A owns the outer handoff loop, its review and the final response. Neither main needs the other's subagent registry. A may also delegate review work; a review evaluator remains read-only.

## Implement, Review And Continue

Send B a compact handoff that invokes `$implement-change`, supplies the plan and necessary rationale, identifies acceptance and existing work to preserve, and requests implementation plus actual verification. Tell B that A will perform `$review-implementation` in this loop and that B may use native subagents with skip permissions. Ensure the named Skills are discoverable by B or supply their essential guidance through readable sources.

An initial prompt can say:

> Use `$implement-change` to implement this established plan directly: [plan and relevant context]. Use native subagents as you judge useful, with skip permissions. Implement and verify, then return changes, checks and unresolved questions for my `$review-implementation`. Settle writing before returning.

Choose coordination through current `$herdr` guidance and the host's available capabilities. When A has useful independent work, submit B's task without immediately waiting and continue that work. Prefer available event notifications that can reach A. A hook that reports B's state does not by itself deliver a message into A's conversation or resume its turn.

Before A ends its current turn in reliance on an asynchronous return, establish how B's result or need for input will reach the intended main session and resume this handoff. Without that supported return path, keep coordination active. When no independent work remains, native waiting is appropriate; observe both completion and requests for attention. Do not substitute repeated status polling for available notifications or require a custom notification service merely to run this workflow.

A notification, ready state or successful process is an observation point, not an accepted result. Read the actual return and changed files before reviewing. A transport timeout does not cancel B or start another implementation; inspect its current state and continue observing when it is still working. Recover any truncated result through the complete-output access supported by current `$herdr` guidance.

When B is blocked, read the question before responding. Resolve routine execution or approval prompts using the selected automatic-approval mode and existing task instructions. Return to the user only for an actual missing decision or unavailable prerequisite; do not blindly answer an unknown dialog.

Review the stable candidate with `$review-implementation`, checking the real diff, acceptance and applicable verification. On follow-up, include earlier findings, B's dispositions and the new changes so review can focus on unresolved issues and affected regressions. If findings need a further implementation turn and rounds remain, send them to the same main B:

> Continue `$implement-change` in this session. This is round N of M. Here are the `$review-implementation` findings and evidence: [findings]. Adjudicate them, repair the supported issues, run affected checks and return the result, explaining any disputed finding.

B judges findings against the plan and evidence; it does not apply every suggestion mechanically. A considers any dispute in the next review. Preserve the original goals and still-valid decisions rather than repeating a full design or audit on every round.

Prefer the same live main sessions throughout. If B exits, use a supported native continuation with its explicit session identity, or clearly describe reconstruction from retained context. Never resume an arbitrary latest session. On A's continuation, reconcile the pending handoff, actual B session and rounds already used before sending more work; a notification does not reset the round budget.

## Finish

Finish when the requested implementation and verification are supported and review has no unresolved supported finding. Report the actual implementation result, review outcome, rounds used and any remaining gap. With review disabled, identify that limit explicitly.

At the round limit, preserve the work and report remaining findings and the exhausted budget. Do not claim success or silently start another round through a replacement agent or local takeover. A genuine missing decision can stop the affected work earlier; ordinary test failures can be repaired within B's implementation turn.

Use `$herdr`'s ownership rules to close only resources created for this invocation after successful completion. Keep unfinished work and useful continuation context. For a reused user pane, preserve that pane and its unrelated state. No commit, worktree deletion or installation is necessary merely to return a result.
