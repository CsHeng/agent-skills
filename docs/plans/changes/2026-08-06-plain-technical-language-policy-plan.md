# Plain Technical Language Policy Implementation Plan

## Upstream Design

- design_ref: 2026-08-06-plain-technical-language-policy-design.md
- design_version: 1

## Implementation Scope

- target_repository: /Users/csheng/workspace/playground/market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- impl_file_refs:
  - src/skills/session/output-styles/SKILL.md
  - skills/output-styles/SKILL.md
- test_file_refs:
  - scripts/check.sh
  - scripts/flatten-skills.py
- verification_scope:
  - Preserve the pre-implementation status of all paths outside the approved skill surface.
  - Add the approved thin language and terminology policy to the source `output-styles` baseline without creating another response authority.
  - Regenerate the root-flat surface and require exact source/generated parity for `output-styles`.
  - Run the repository-required generators, aggregate check, Markdown whitespace check, and bounded implementation review.

## Work Package Readiness

- milestone_objective: Add one shared plain technical language policy that reduces ambiguity and terminology drift without weakening technical precision or claiming universal ASD-STE100 compliance.
- non_goals:
  - No ASD-STE100 dictionary, validator, compliance tooling, readability score, or reading-grade gate.
  - No generic `CONTEXT.md` convention or repository-wide context scan.
  - No new public skill, routing change, manifest change, plugin version change, or rewrite of existing documentation.
- future_phase:
  - No follow-up phase is planned for this bounded policy change.
- decision_status: ready_for_review
- oracle_strategy: Docs-only semantic contract inspection plus deterministic source/generated parity and aggregate repository validation; avoid brittle exact-prose tests.
- acceptance_oracles:
  - The source baseline covers language matching, file-local and canonical terminology, plain direct wording, conditional active voice, procedure-only imperative wording, condition-before-action order, unexplained jargon and vague-reference avoidance, precise-term preservation, and validated-only ASD-STE100 compliance claims.
  - The policy does not require unconditional `CONTEXT.md` discovery, vocabulary reduction, or fixed readability scoring.
  - `diff -qr src/skills/session/output-styles skills/output-styles` reports no differences after regeneration.
  - `bash scripts/check.sh` and `git diff --check` pass.
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
  - C0: Approval authorizes the complete serial edit, regeneration, validation, and bounded review in the current checkout; it does not authorize a commit, push, plugin installation, or global skill refresh.
- runtime_contingencies:
  - X1: Stop and diagnose if a required generator changes tracked content outside the approved `output-styles` source and root-flat surfaces.
  - X2: Stop with `needs-plan-change` if satisfying the semantic contract requires a new skill, validator, test framework, or another file outside the approved touch set.
  - X3: Stop and preserve evidence if aggregate validation fails for a cause that cannot be repaired within the approved touch set.
- planned_stop_points:
  - none
- task_ordering_rationale: The source-of-truth policy must change before its generated projection; deterministic regeneration, validation, and review then operate on one converged serial diff.

## Task 1: Add and verify the shared language policy

- task_id: PTL-010
- depends_on:
  - none
- scope_slice: Update the source `output-styles` baseline, refresh its generated root-flat projection, and verify the complete bounded diff.
- impl_file_refs:
  - src/skills/session/output-styles/SKILL.md
  - skills/output-styles/SKILL.md
- test_file_refs:
  - scripts/check.sh
  - scripts/flatten-skills.py
- verification_scope:
  - Capture the pre-implementation `git status --short` and preserve all unrelated paths.
  - Edit only `src/skills/session/output-styles/SKILL.md`; do not hand-edit the generated root-flat file.
  - Run `python3 scripts/generate-skills-index.py`.
  - Run `python3 scripts/flatten-skills.py --target root-flat`.
  - Run `python3 scripts/generate-workflow-diagrams.py`.
  - Run `diff -qr src/skills/session/output-styles skills/output-styles`.
  - Run `bash scripts/check.sh` and `git diff --check`.
  - Compare the final changed paths with the approved touch set and route the exact implementation diff through `review-change` with `review-implementation`.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - output-styles-contract
- task_review_depth: focused
- done_when:
  - The source baseline expresses every approved semantic rule without a second style authority or strict STE claim.
  - The generated root-flat `output-styles` surface exactly matches its source.
  - The declared validation scripts remain byte-for-byte unchanged and serve only as verification dependencies.
  - Required generation and aggregate validation introduce no unrelated tracked drift and pass.
  - Implementation review passes with no accepted finding unresolved.
- failure_policy: fix_forward
- [ ] Add the approved language and terminology rules to the source baseline.
- [ ] Regenerate the root-flat compatibility surface.
- [ ] Run focused and aggregate verification.
- [ ] Complete bounded implementation review and repair only accepted in-scope findings.

## Review Gate

- required_entry: review-change
- required_mode: review-only
- review_component: review-plan
- review_depth: boundary
- max_review_batches: 2
- review_status: passed
- review_evidence: The first bounded review found that `test_file_refs: none` was outside the approved design surface; the accepted finding was repaired by declaring the two approved read-only validation dependencies. Strict validation, design-surface containment, serial ownership, semantic oracles, and continuous execution then passed a focused verification review.
- supporting_files:
  - 2026-08-06-plain-technical-language-policy-design.md: approved goals, non-goals, acceptance conditions, and implementation surface.
  - src/skills/session/output-styles/SKILL.md: current shared response baseline and intended source edit.
  - AGENTS.md: source/generated ownership, validation, review, and human-gate policy.
- pass_condition: The plan remains one bounded serial docs-only task with semantic acceptance evidence, deterministic generation, exact parity, aggregate validation, and no authority to modify unrelated files or external state.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Recovery

- default_failure_policy: fix_forward
- recovery_evidence:
  - The pre-implementation Git status and exact final changed-path comparison preserve unrelated-work evidence.
  - The source and root-flat files are deterministic text surfaces, so defects can be repaired within the declared touch set and revalidated without restoring runtime state.
