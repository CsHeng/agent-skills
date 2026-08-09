# Frontier And Phase-Boundary Interaction Design

## Status

Approved design-lite boundary record for the two interaction changes explicitly selected by the user on 2026-08-09.

## Problem

The explicit stress-test path currently asks one decision-changing question at a time even when several questions have no unresolved dependencies, causing unnecessary round trips. The session router also defines what compact handoffs preserve but does not provide an ordered decision tree for choosing whether to continue, discard context, create a portable handoff, delegate an isolated slice, or compact at a completed phase boundary.

## Goals

- Change explicit design or plan stress-testing to ask the complete currently unblocked decision frontier in one numbered round, then recompute the frontier after the user's answers.
- Keep factual discovery with the agent and reserve user questions for decisions that cannot be resolved from repository, runtime, or external evidence.
- Preserve stable question IDs, one recommendation and material tradeoff per question, dependency ordering, and the existing bounded completion rule.
- Add one provider-neutral phase-boundary decision tree owned by `use-coding-skills`, with ordered branches for continue, discard irrelevant context, portable handoff, policy-permitted delegation, and compact fallback.
- Keep existing lifecycle ownership, approval gates, routing cases, and compact-payload priorities unchanged.

## Non-Goals

- Do not add questionnaire, wizard, provider-specific invocation projection, human-facing skill catalog, prototype, or `wait-what` behavior.
- Do not add a public skill, lifecycle phase, trigger-case owner, activation mode, provider command, fixed token threshold, or unattended execution path.
- Do not authorize `design-change` to spawn subagents or make fact-finding delegation the default; the main agent continues to inspect available evidence unless another approved owner explicitly permits delegation.
- Do not change runtime harness scripts, manifests, install targets, plugin versions, review budgets, recovery routing, or implementation parallelism.
- Do not turn the phase-boundary guide into a general context-management framework outside coding sessions.

## Change Classification

- request_kind: change-definition
- change_class: B
- design_strength: design-lite
- truth_impact: medium
- boundary_impact: low
- recommended_next_phase: design-lite
- truth_sync_required: true
- parallel_candidate: false

## Boundaries

- in_scope:
  - Replace the explicit one-question-at-a-time stress-test rule with a dependency-aware frontier-round contract.
  - Add an ordered, provider-neutral phase-boundary reference and point `use-coding-skills` to it.
  - Add focused executable semantic contract tests for both behaviors.
  - Refresh only the corresponding generated root-flat skill projections and run repository-required validation.
- out_of_scope:
  - Change default design discovery when the user did not explicitly request stress-testing.
  - Change semantic trigger ownership in `routing.toml` or lifecycle phase ownership.
  - Add automatic subagent research, model selection, worktree use, or parallel batches.
  - Rewrite stable architecture docs that do not own these interaction details.

## Behavioral Contract

### Frontier Rounds

- A decision question enters the current frontier only when all of its prerequisites are settled.
- One round contains every currently unblocked decision-changing question, with stable `Q*` identifiers, a recommended answer, and its material tradeoff.
- A question that depends on another unresolved answer waits for a later round.
- Facts available from the environment are inspected by the agent and are not converted into user questions.
- After each reply, the agent records resolved decisions, recomputes the frontier, and asks the next round; an explicit user preference for one-at-a-time interaction remains authoritative.
- Stress-testing stops when no unresolved decision-changing question remains, then renders the existing confirmed assumptions, rejected alternatives, open constraints, design or plan changes, and verification or recovery implications.

### Phase-Boundary Tree

- Apply the tree only after a coherent phase completes; mid-phase work continues unless a separately authorized, tightly scoped delegation is available.
- Evaluate branches in this order and take the first applicable result: continue in the current context; discard context that is irrelevant to the next phase; create a portable handoff when context must travel; delegate only when the selected owner and approved execution policy permit it; compact relevant context as the fallback when continuing is no longer viable.
- Treat continue as the only branch that preserves the conversation as a primary source, portable handoff as a portability mechanism rather than a default summary, and compact as the last applicable branch rather than the first reach.
- Reuse the existing compact-payload priorities instead of duplicating them in the new reference.
- Express decisions semantically without provider commands or a fixed token-window threshold.

## Acceptance Conditions

- Focused tests fail against the current one-question rule and missing phase-boundary reference before source implementation.
- Focused tests prove frontier prerequisite ordering, batched unblocked questions, stable question labels, recommendation and tradeoff requirements, evidence-owned facts, recomputation, and bounded completion without requiring model-output snapshots.
- Focused tests prove the phase-boundary branch order, first-applicable semantics, phase-only timing, policy-gated delegation, compact fallback, absence of a fixed token threshold, and a direct pointer from `use-coding-skills`.
- `routing.toml` retains `use-coding-skills` as the existing `session-boundary-handoff` owner and receives no semantic ownership change.
- Generated `skills/design-change` and `skills/use-coding-skills` files match their edited source counterparts after regeneration.
- Repository-required generators, sovereign harness smoke tests, `bash scripts/check.sh`, and `git diff --check` pass without unrelated tracked drift.
- Bounded implementation review leaves no accepted current-slice finding unresolved.

## Recovery Policy

Use fix-forward for wording, contract-test, generated-surface, or validation defects. No guarded rollback is required because the change is repository-local text and test code with no live state; preserve the pre-implementation worktree status, repair inside the approved touch set, and rerun the narrow oracle before aggregate validation.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly limited plan-change to Frontier batch questioning and the Phase-boundary decision tree on 2026-08-09.
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - src/skills/workflows/design-change/references/stress-test-mode.md
  - src/skills/session/use-coding-skills/SKILL.md
  - src/skills/session/use-coding-skills/references/phase-boundary-decision-tree.md
  - skills/design-change/references/stress-test-mode.md
  - skills/use-coding-skills/SKILL.md
  - skills/use-coding-skills/references/phase-boundary-decision-tree.md
- test_file_refs:
  - tests/test_session_interaction_contracts.py
  - scripts/generate-skills-index.py
  - scripts/flatten-skills.py
  - scripts/generate-workflow-diagrams.py
  - scripts/check.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-design-plan-skill-control.sh
  - src/runtime/harness/smoke-test/test-agent-native-review.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-review-execute-skill-control.sh
