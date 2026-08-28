---
name: implement-change-via-herdr
description: "Use only when the user explicitly asks to execute an approved bounded task with Herdr. Provides semantic handoff guidance; it does not ship an adapter, persist execution state, or own implementation review and repair."
---

# Implement Change Via Herdr

Use Herdr as an optional execution tool for one already approved and independently bounded implementation task.

## Preconditions

- The user explicitly requested Herdr.
- `implement-change` or an equivalent approved implementation context already defines the objective, allowed files, non-goals, verification, and authority boundary.
- The task can be handed off without asking Herdr to choose scope, redesign the change, approve new actions, or decide completion.

If any precondition is missing, return to the calling implementation work instead of inventing a handoff contract.

## Handoff

1. Give Herdr only the bounded objective, allowed surfaces, relevant repository guidance, and required verification.
2. Keep credentials, unrelated conversation, provider configuration, and external state out of the handoff.
3. Ask for changed-file and verification evidence, not lifecycle decisions.
4. Independently inspect the resulting diff and evidence before accepting it.
5. Keep the formal implementation review, candidate adjudication, any accepted repair, and final outcome with the calling implementing agent.

This Skill does not prescribe Herdr commands or workspace layout. It contains no executable adapter, state file, lease, task ledger, actor binding, model binding, retry loop, or resume protocol. Use the Herdr installation's own current documentation for its mechanics.

## Boundaries

- Herdr does not widen the approved task or mutation authority.
- A Herdr result is evidence, not automatic success.
- Do not delegate recursively.
- Do not expose secrets or unrelated repository state.
- Stop with `needs-authority`, `replan`, or `blocked` when the bounded handoff cannot proceed safely.
