---
name: herdr-delegate
description: "Use when the user asks to hand an established plan to another main coding agent through Herdr for implementation and return it to the current main for review and repair rounds. A one-way handoff that the other main finishes on its own belongs to herdr-handoff."
---

# Herdr Delegate

Delegate implementation to another main coding-agent session while the current session keeps review and acceptance: main A is the current session, main B implements the established plan. Compose `herdr-handoff` to select or start B, `$implement-change` for B's implementation, and `$review-implementation` for A's review. Each main decides how to use its own native subagents; this Skill manages only the main-to-main exchange.

## Inputs And Defaults

- Target, agent, model, thinking level, plan, and permission mode follow `herdr-handoff`, including inheriting A's own combination when the user names none.
- Review defaults on with `rounds` a positive integer, default `3`. One round is B's implementation or repair followed by A's review. The budget limits the Herdr exchange, not completion of the task; internal subagent turns, tests, self-repairs, waits, and clarifications are inside a round. An explicit no-review request uses one implementation return and says review was skipped.

## Prepare Main B

Follow `herdr-handoff` to make the records accessible to B and to select or start B, with ownership retained by A: B returns its result for review, and A keeps review, acceptance, the final response, and the plan's gated actions such as commit, push, and publication. Conversation-only context may also travel in the handoff, because B can ask before returning.

Default to the current checkout and alternate implementation with review: while B writes and checks, A leaves those files alone; before A reviews, B settles its writing and write-producing subagents. During delegated rounds B owns implementation choices, verification, and internal delegation as a main session; A owns the outer loop, its review, and the final response.

## Implement, Review And Continue

Send B a compact handoff that invokes `$implement-change`, supplies the plan and rationale, distinguishes binding outcome acceptance, exclusions, and user-fixed checks from revisable candidate proof methods, names existing work to preserve, and requests implementation plus verification. State that A will run `$review-implementation`, that B may use native subagents with skip permissions, and that any main model or thinking settings are main-only. Make the named Skills discoverable by B or supply their essential guidance through readable sources.

> Use `$implement-change` to implement this established plan directly: [plan and relevant context]. Required outcome acceptance, exclusions, and explicit user-fixed checks bind; candidate local proof lanes in `plan.md` are revisable means. Update `plan.md` only on authority or decision changes or terminal handoff summaries. Any selected CLI, model, and thinking settings apply to this main session only; subagents use their native configured routing. [Include any explicitly requested subagent override and its scope.] Implement and verify, then return changes, checks, and unresolved questions for my `$review-implementation`. Settle writing before returning.

When A has useful independent work, submit B's task without waiting and continue; when none remains, wait natively and observe both completion and requests for attention. Before ending a turn in reliance on an asynchronous return, establish how B's result or question will reach this session; without a supported return path, keep coordination active. A notification, ready state, or successful process is an observation point: read the actual return and changed files before reviewing. A transport timeout leaves B running; inspect its state and keep observing. Recover a truncated result through `$herdr`'s complete-output access.

When B is blocked, read the question. Resolve routine execution or approval prompts with the automatic-approval mode and existing task instructions; return to the user only for an actual missing decision or unavailable prerequisite.

Review the settled candidate with `$review-implementation` against the real diff, acceptance, and verification; on follow-up include earlier findings, B's dispositions, and the new changes. A narrow deterministic repair whose direct check passes closes the round on A's own verification. When rounds keep finding defects inside supporting test, fixture, or simulation code rather than product behavior, A evaluates deleting or simplifying that mechanism before dispatching another iteration. When supported findings need another implementation turn and rounds remain, send them to the same B:

> Continue `$implement-change` in this session. This is round N of M. Here are the `$review-implementation` findings and evidence: [findings]. Adjudicate them, repair the supported issues, run affected checks, and return the result, explaining any disputed finding.

B judges findings against the plan and evidence; A considers any dispute in the next review. Prefer the same live sessions throughout. If B exits, use a supported native continuation with its explicit session identity or describe reconstruction from retained context. On A's continuation, reconcile the pending handoff, the actual B session, and rounds already used; a notification does not reset the budget.

## Finish

Finish when the requested implementation and verification are supported and review has no unresolved supported finding. Report the implementation result, review coverage, rounds used, any takeover by A, and any remaining gap; with review disabled, say so.

At the round limit, end the exchange with B and assess the remaining work. For supported, recoverable findings within the existing scope and authority, A takes over with `$implement-change` to finish and verify, honoring any explicit instruction forbidding takeover; replacing B does not reset the budget. Before A writes, settle B and its subagents and reconcile the actual changes, unresolved findings, and evidence; A then owns implementation and adjudication, verifies the changed candidate, and obtains independent review when the implementation policy requires it. A genuine blocker, missing decision, or material plan or design change stops the affected work with progress preserved and the obstacle reported; ordinary repairable defects remain implementation work after the budget.

Close only resources created for this invocation after successful completion, following `$herdr`'s ownership rules, and keep a reused user pane and its unrelated state. No commit, worktree deletion, or installation is needed to return a result.
