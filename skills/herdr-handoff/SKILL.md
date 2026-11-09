---
name: herdr-handoff
description: "Use when the user asks to hand an established plan to another main coding agent through Herdr, in a new or existing session with a named or inherited agent, model, and thinking level, which then owns the work through delivery. Returning the result to the current main for review rounds belongs to herdr-delegate; plain pane or command control belongs to herdr."
---

# Herdr Handoff

Transfer an established plan to another main coding-agent session: main A is the current session and main B receives the plan and owns it to completion. Compose `$herdr` for terminal and agent operations and `$implement-change` for B's work. Use this Skill directly for a one-way handoff; `herdr-delegate` reuses its preparation when A keeps review and acceptance.

## Inputs And Defaults

- Target: a new session in an adjacent pane, or an existing agent or pane the user names.
- Agent, model, and thinking level: when the user names none, inherit A's own combination, the same CLI, provider and model, and thinking level. Resolve A's actual current values from the host rather than from configuration defaults, and report a value that cannot be resolved instead of guessing. An explicit agent, model, or thinking choice replaces only that part; resolve it through the selected CLI's current options and report an unsupported request instead of substituting another model or changing persistent client settings. These settings describe B's main invocation only; B's native subagents keep their configured routing unless the user selects otherwise for them.
- Plan: the current conversation's established plan unless the user supplies another.
- Permissions: use the selected CLI's native skip-permission or allow-all mode. Requesting a handoff authorizes direct execution of the established task, so no plan-approval exchange is added; project-specific gate instructions travel with the plan.

## Make The Records Self-Contained

B must be able to finish from accessible records alone, because a one-way handoff has no return path for clarification. Before handing off, write into the plan, design, or another accessible project record whatever B needs that lives only in this conversation: decisions and their rationale, user-fixed constraints, essential facts discovered so far, and the current authority for commit, push, publication, or other gated actions. Follow the fresh-main handoff guidance in `references/delivery-and-delegation.md` of `plan-change`. An inaccessible path or an unrecorded conversation decision is not a supplied plan.

## Prepare Main B

Read the current `$herdr` Skill and satisfy its environment requirements. It owns Herdr operations and discovery; the selected coding agent's current guidance owns its launch, permission, model, and thinking options.

Default to the current checkout. Use a worktree for an actual isolation need or explicit request through `references/worktree-isolation.md` in `implement-change`.

Use the named existing session, or create one adjacent pane through `$herdr` while keeping the caller's focus. Start B in the intended working directory with the resolved agent, model, thinking level, and permission mode, give it a useful unique name, and record which pane and agent this invocation created or reused.

## Hand Off

Send B a compact brief that invokes `$implement-change`, points to the plan records, and states ownership:

> Use `$implement-change` to implement this established plan: [plan reference]. The plan and its linked records hold the outcome, rationale, constraints, and current authority. You own implementation, verification, any review the plan or project policy requires (your native subagents may perform it), repair, and the gated actions the plan authorizes. Record the terminal status in the plan and report the result in this session. Your main model and thinking settings apply to this session only; subagents keep their configured routing.

When `herdr-delegate` composes this Skill, it replaces the ownership sentence with its own: B returns for A's review, and A keeps acceptance and gated actions.

Confirm that B accepted the prompt and started working. A blocked startup or an approval prompt is resolved with the permission mode and the plan; return to the user only for an actual missing decision.

## Finish

Report the target pane and agent name, B's session identity where the CLI exposes one, the agent, model, and thinking level used and whether each was inherited, and the plan reference. A one-way handoff ends here: A does not wait for B, subscribe to its completion, or review its result, and B's pane stays open for the user. No commit, worktree deletion, or installation is needed to complete the handoff.
