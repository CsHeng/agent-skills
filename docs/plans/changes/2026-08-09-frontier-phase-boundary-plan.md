# Frontier And Phase-Boundary Interaction Implementation Plan

## Upstream Design

- design_ref: 2026-08-09-frontier-phase-boundary-design.md
- design_version: 1

## Implementation Scope

- target_repository: /Users/csheng/workspace/playground/market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
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
- verification_scope:
  - Preserve the pre-implementation status of every path outside the approved source, generated projection, and focused test surfaces.
  - Add a red focused semantic contract before changing either source skill behavior.
  - Implement only dependency-aware Frontier rounds and the ordered provider-neutral Phase-boundary tree.
  - Keep `routing.toml`, lifecycle contracts, runtime harness code, manifests, install targets, and unrelated skills byte-for-byte unchanged.
  - Regenerate the required root-flat surface from `src/skills` and verify exact parity for the six affected source and generated files.
  - Run the focused oracle, repository-required generators, sovereign harness smoke tests, aggregate check, whitespace validation, and bounded implementation review.

## Work Package Readiness

- milestone_objective: Replace explicit stress-test one-question interaction with dependency-aware Frontier rounds and add one ordered provider-neutral Phase-boundary decision tree without changing lifecycle or routing ownership.
- non_goals:
  - No questionnaire, wizard, provider invocation projection, human skill catalog, prototype, `wait-what`, or other Matt v1.2 idea.
  - No new public skill, lifecycle phase, trigger case, activation mode, provider command, fixed context-window threshold, or unattended execution path.
  - No automatic fact-finding subagent dispatch and no change to `design-change` agent permissions.
  - No runtime harness, manifest, install-target, plugin-version, recovery-routing, or parallel-execution change.
- future_phase:
  - All other ideas from the preceding Matt v1.2 analysis remain outside this work package and receive no implied follow-up authorization.
- decision_status: ready_for_review
- oracle_strategy: Scenario and semantic-contract TDD over the two Markdown behavior contracts, followed by deterministic source/generated parity, aggregate repository validation, sovereign harness smoke tests, and bounded agent-native review; avoid nondeterministic model-output snapshots.
- acceptance_oracles:
  - The new focused test fails on the current one-question-at-a-time rule and absent phase-boundary reference for only the intended reasons before source implementation.
  - The focused test then passes for Frontier prerequisite ordering, complete currently unblocked rounds, stable `Q*` IDs, recommendation and tradeoff fields, evidence-owned facts, recomputation, explicit sequential preference, and bounded completion.
  - The focused test passes for the ordered phase-boundary branches continue, discard irrelevant context, portable handoff, policy-permitted delegation, and compact fallback; it also verifies phase-only timing, first-applicable semantics, no fixed token threshold, and the direct source pointer.
  - The existing `session-boundary-handoff` trigger case remains owned by `use-coding-skills`, with no edit to `routing.toml`.
  - Each affected generated root-flat `SKILL.md` or reference file is byte-identical to its source counterpart after regeneration.
  - Required generators, the sovereign harness smoke suite, `bash scripts/check.sh`, and `git diff --check` pass without unrelated tracked drift.
  - Bounded implementation review leaves no accepted current-slice finding unresolved.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 1

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval authorizes the complete serial red-green source edit, root-flat regeneration, declared validation, and bounded implementation review in the current checkout; it does not authorize a commit, push, plugin installation, external distribution, or any idea outside the two approved behaviors.
- runtime_contingencies:
  - X1: Stop and diagnose if a required generator changes tracked content outside the six approved generated or source skill paths and the focused test file.
  - X2: Stop with `needs-plan-change` if either behavior requires changing `routing.toml`, lifecycle contracts, runtime harness code, agent permissions, or another public skill.
  - X3: Stop and preserve evidence if focused or aggregate validation fails for a cause that cannot be repaired inside the approved touch set.
- planned_stop_points:
  - none
- task_ordering_rationale: Establish the executable semantic contract first, implement the two source-owned behaviors second, then regenerate and verify the complete bounded projection so execution has one red-green-converge path and no mid-plan approval stop.

## Task 1: Add the failing session-interaction semantic contract

- task_id: SIB-010
- depends_on:
  - none
- scope_slice: Add one focused Python contract test that captures the approved Frontier-round and Phase-boundary semantics before changing their source Markdown.
- impl_file_refs:
  - none
- test_file_refs:
  - tests/test_session_interaction_contracts.py
- verification_scope:
  - Capture `git status --short` before writing and preserve the two approved stage artifacts plus every unrelated path.
  - Add a focused standard-library `unittest` file that reads only the source skill files and routing contract needed for these two behaviors.
  - Assert semantic headings, stable labels, dependency and branch order, direct reference reachability, routing-owner preservation, and absence of the contradictory one-question default or a fixed token threshold without snapshotting complete prose.
  - Run `python3 tests/test_session_interaction_contracts.py` and require a red result caused only by the current one-question rule and missing phase-boundary source/reference pointer.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - session-interaction-oracle
- task_review_depth: focused
- done_when:
  - The test describes both approved behaviors and no out-of-scope skill or lifecycle behavior.
  - The current source produces the expected narrow red evidence instead of syntax, import, path, or unrelated routing failures.
  - No source skill, generated skill, contract, runtime, manifest, or existing test file changes in this task.
- failure_policy: fix_forward
- [ ] Add the focused semantic contract test.
- [ ] Run it red and record the intended failure evidence.

## Task 2: Implement the two source interaction contracts

- task_id: SIB-020
- depends_on:
  - SIB-010
- scope_slice: Replace the explicit stress-test sequential default with Frontier rounds and add the provider-neutral Phase-boundary decision-tree reference plus its direct `use-coding-skills` pointer.
- impl_file_refs:
  - src/skills/workflows/design-change/references/stress-test-mode.md
  - src/skills/session/use-coding-skills/SKILL.md
  - src/skills/session/use-coding-skills/references/phase-boundary-decision-tree.md
- test_file_refs:
  - tests/test_session_interaction_contracts.py
- verification_scope:
  - Edit only the three source-owned paths declared for this task; do not hand-edit generated `skills/` files.
  - Keep stress-test activation explicitly user-requested, ask the whole currently unblocked decision frontier per round, retain recommendation and tradeoff content, inspect facts directly, recompute after answers, respect an explicit one-at-a-time preference, and preserve the existing completion summary.
  - Define the Phase-boundary tree with ordered first-applicable branches for continue, discard, portable handoff, policy-permitted delegation, and compact fallback; keep it phase-boundary-only, provider-neutral, and free of fixed token limits.
  - Point `use-coding-skills` directly to the new reference while reusing its existing compact-payload priorities and leaving `routing.toml` unchanged.
  - Run `python3 tests/test_session_interaction_contracts.py` and `git diff --check`.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - source-skill-interaction-contracts
- task_review_depth: focused
- done_when:
  - Every approved Frontier-round semantic is present without automatic delegation or a new top-level workflow.
  - Every approved Phase-boundary branch and ordering rule is present without provider commands, hard-coded context size, or duplicate compact-payload instructions.
  - The focused semantic contract passes and `routing.toml` remains byte-for-byte unchanged.
- failure_policy: fix_forward
- [ ] Implement Frontier rounds in the explicit stress-test reference.
- [ ] Add and link the Phase-boundary decision-tree reference.
- [ ] Run the focused green oracle and whitespace check.

## Task 3: Regenerate, validate, and review the bounded projection

- task_id: SIB-030
- depends_on:
  - SIB-020
- scope_slice: Refresh the generated root-flat counterparts, execute all declared repository and sovereign-harness validation, and complete bounded implementation review.
- impl_file_refs:
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
- verification_scope:
  - Run `python3 scripts/generate-skills-index.py`, `python3 scripts/flatten-skills.py --target root-flat`, and `python3 scripts/generate-workflow-diagrams.py` in the required order.
  - Require byte parity for the source/generated stress-test reference, `use-coding-skills/SKILL.md`, and Phase-boundary reference with `cmp -s` checks.
  - Run `python3 tests/test_session_interaction_contracts.py`.
  - Run `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`, `bash src/runtime/harness/smoke-test/test-design-runner.sh`, `bash src/runtime/harness/smoke-test/test-plan-runner.sh`, `bash src/runtime/harness/smoke-test/test-design-plan-skill-control.sh`, `bash src/runtime/harness/smoke-test/test-agent-native-review.sh`, `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`, `bash src/runtime/harness/smoke-test/test-recovery-routing.sh`, `bash src/runtime/harness/smoke-test/test-execute-runner.sh`, and `bash src/runtime/harness/smoke-test/test-review-execute-skill-control.sh`.
  - Run `bash scripts/check.sh` and `git diff --check`.
  - Compare final changed paths with the approved implementation and test surface; generated index and diagrams must remain unchanged unless their owning contracts actually require a deterministic refresh.
  - Route the exact implementation diff, focused oracle, declared touch set, and justified validation dependencies through `review-change` with `review-implementation`; repair only accepted in-scope findings and rerun the focused oracle plus affected checks.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - generated-root-flat-surface
- task_review_depth: focused
- done_when:
  - The three generated root-flat files match their source counterparts byte-for-byte and no unapproved generated path changes remain.
  - Focused tests, sovereign harness smoke tests, aggregate validation, and whitespace validation pass.
  - The final implementation diff contains only the approved two behavior changes, their focused test, deterministic projections, and approved lifecycle artifacts.
  - Bounded implementation review passes with no accepted current-slice finding unresolved and truth-sync routing is reported for the changed skill truth.
- failure_policy: fix_forward
- [ ] Regenerate required public surfaces.
- [ ] Run focused, harness, aggregate, parity, and whitespace validation.
- [ ] Complete bounded implementation review and repair only accepted in-scope findings.

## Review Gate

- required_entry: review-change
- required_mode: review-only
- review_component: review-plan
- review_depth: boundary
- max_review_batches: 2
- review_status: passed
- review_evidence: One delegated bounded review validated the complete new plan against the approved two-item design record, current stress-test and session-router sources, unchanged routing ownership, and repository policy. It returned `verdict: pass` with no candidate findings: the serial red-green-converge DAG, version-2 metadata, touch sets, semantic oracles, execution continuity, authority boundaries, and fix-forward recovery were complete and internally consistent.
- supporting_files:
  - 2026-08-09-frontier-phase-boundary-design.md: approved two-item goals, non-goals, behavior contracts, acceptance conditions, and implementation surface.
  - src/skills/workflows/design-change/references/stress-test-mode.md: current explicit stress-test behavior and the sequential rule being replaced.
  - src/skills/session/use-coding-skills/SKILL.md: current session-boundary owner and compact-payload priorities.
  - src/skills/session/use-coding-skills/references/routing.toml: existing `session-boundary-handoff` ownership that must remain unchanged.
  - AGENTS.md: source/generated ownership, mandatory validation, review, and human-gate policy.
- pass_condition: The plan remains one serial red-green-converge work package limited to Frontier rounds and the Phase-boundary tree, with executable semantic oracles, exact touch sets, complete repository validation, fix-forward recovery, and no new lifecycle or routing authority.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Recovery

- default_failure_policy: fix_forward
- recovery_evidence:
  - The pre-implementation Git status and exact final changed-path comparison preserve unrelated-work evidence.
  - The changed behavior contracts, test, and generated projections are repository-local text and Python files, so defects can be repaired inside the declared touch set and rerun through the focused oracle before aggregate validation.
  - No live state, credentials, destructive writes, cutover, or rollback target is involved.
