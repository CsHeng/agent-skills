# Codex Subagent User Route Input

## Status

- artifact_kind: user-owned-runtime-routing-input
- decision_ref: CODEX-NATIVE-USER-ROUTE-002
- approval_status: approved
- approved_on: 2026-08-18
- portability: user-specific; do not project provider identifiers into reusable skills, workflow
  plans, neutral envelopes, or stable repository truth
- provenance: Captured from the user's direct instructions in the plan-change thread. This artifact,
  rather than session or log state, is the immutable execution input.

## Baseline

- Leave `agents.default_subagent_model` and `agents.default_subagent_reasoning_effort` absent so each
  unoverridden field inherits from the main session.
- Treat the inherited main profile as the physical baseline. Do not down-route a child below that
  profile merely for cost or latency.
- These routes guide per-spawn selection from `~/.codex/AGENTS.md`; they are not role-file pins and do
  not change task topology, role authority, sandboxing, isolation, or lifecycle gates.

## Role Routes

- reviewer:
  - model_family: `gpt-5.6-sol`
  - minimum_reasoning_effort: `high`
- worker:
  - model_families: `gpt-5.6-terra`, `gpt-5.6-luna`, or `gpt-5.6-sol`
  - minimum_reasoning_effort: `high`
- explorer:
  - model_families: `gpt-5.6-luna` or a stronger available family, currently
    `gpt-5.6-terra` and `gpt-5.6-sol`
  - minimum_reasoning_effort: `medium`

The main agent chooses among each role's allowed families based on task difficulty. Reasoning values
are minimums, never exact pins or ceilings; any supported higher effort, including `max` or `ultra`,
is allowed.

## Override Rules

- Emit no per-spawn override when the inherited main model and reasoning satisfy the selected role
  route and its minimum.
- Emit an effort-only uplift when the inherited model is allowed but its reasoning is below the
  minimum selected for the task.
- Emit model and reasoning together whenever the model changes; never rely on the new model's default
  reasoning effort.
- If a required uplift is unsupported or rejected, do not retry through `[agents]` defaults, omit the
  required fields, or bind below the floor. Return the harness's typed capability result and use only
  an already-approved main-agent fallback for the unchanged task; otherwise require a manual
  decision.
