# Testing Strategy Layering And Suite Audit Implementation Plan

## Upstream Design

- design_ref: 2026-07-28-testing-strategy-layering-design.md
- design_version: 1

## Implementation Scope

- target_repository: /Users/csheng/workspace/playground/market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- impl_file_refs:
  - src/skills/disciplines/testing-strategy/SKILL.md
  - src/skills/disciplines/testing-strategy/references/ci-config.md
  - src/skills/disciplines/testing-strategy/references/test-layering-and-suite-audit.md
  - skills/testing-strategy/SKILL.md
  - skills/testing-strategy/references/ci-config.md
  - skills/testing-strategy/references/test-layering-and-suite-audit.md
- test_file_refs:
  - src/skills/disciplines/testing-strategy/references/test-layering-and-suite-audit.md
  - skills/testing-strategy/references/test-layering-and-suite-audit.md
- verification_scope:
  - Validate the source skill structure and all direct Markdown references.
  - Prove deterministic source-to-root-flat generation and exact parity for `testing-strategy`.
  - Run the complete `market-csheng` aggregate check and Markdown whitespace validation.
  - Forward-test the generated skill against representative homelab suite cases without modifying any homelab repository.
  - Route the exact implementation diff through bounded agent-native implementation review.
  - Prove every pre-existing unrelated dirty path in `market-csheng` is byte-for-byte unchanged.

## Work Package Readiness

- milestone_objective: Make `coding:testing-strategy` a reviewed, source-first oracle for classifying existing tests by protected boundary, evidence class, execution lane, environment, and diagnosis owner before it is used to guide homelab test remediation.
- non_goals:
  - Modify or fully audit homelab repository tests in this milestone.
  - Repair the known-bad token or treat it as a preserved contract.
  - Add universal line-count, coverage, suite-size, or pyramid-ratio thresholds.
  - Add brittle automated assertions over skill prose.
  - Modify the skill manifest, public id, workflow DAG, command surface, or unrelated `organize-docs` work.
- future_phase:
  - Use the reviewed generated skill for a read-only inventory and classification of all test entry points across `homelab-infra`, `homelab-platform`, `homelab-operations`, and `homelab-dotfiles`.
  - Publish one shared audit and coordination ledger with protected boundary, current evidence class, lane, environment, owner, oracle quality, disposition, replacement oracle, rationale, producer and consumers, external dependencies, and parallel eligibility.
  - Create one independently approved repo-local `plan-change` artifact for each repository with accepted changes; do not create an empty plan for a repository whose audit result is `keep`.
  - Mark repo-local plans parallel-safe only after the ledger freezes dependencies and proves they do not write the same contract or require another plan's output; otherwise declare exact inter-plan dependencies.
  - Use subagents only for bounded review or dependency-frozen execution slices declared ready by the owning repo plan.
- decision_status: ready_for_review
- oracle_strategy: Use a meta-oracle composed of the approved classification contract, deterministic source-generation checks, and an independent scenario-based forward-test; deliberately avoid exact-prose unit tests because they would protect wording rather than consumer behavior.
- acceptance_oracles:
  - A pre-change scenario review demonstrates that the current skill does not require an explicit evidence-class versus lane split, suite-audit disposition, or subprocess allowlist decision.
  - The revised source skill and reference classify representative large, mixed-owner, prose-snapshot, source-reimplementation, and environment-inheritance cases using the approved fields and smallest-sufficient-layer rule.
  - Skill validation, direct-link validation, root-flat generation, source/generated parity, `bash scripts/check.sh`, and `git diff --check` pass.
  - A fresh bounded reviewer applying the generated skill reaches the expected type of decision without relying on file-length thresholds or exact wording.
  - A bounded implementation review leaves no accepted finding unresolved and every unrelated dirty path retains its baseline content hash and status.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval of this plan authorizes TSL-010 through TSL-040 as one serial `market-csheng` change in the current checkout, with no homelab writes, no worktree creation, no commit, no push, and no global installed-skill refresh.
- runtime_contingencies:
  - X1: Stop and diagnose if a generator changes any path outside the approved `testing-strategy` surface or changes the content or status of a pre-existing unrelated dirty path.
  - X2: Stop and diagnose if aggregate validation fails and the failure cannot be causally localized to the approved skill slice without changing unrelated work.
  - X3: Stop with `needs-design-decision` if representative cases cannot be classified without introducing a universal size threshold, a single false hierarchy, or ownership outside `testing-strategy`.
  - X4: Stop with `needs-plan-change` if meaningful behavioral verification would require a new persisted evaluation framework or changes outside the approved implementation surface.
- planned_stop_points:
  - none
- task_ordering_rationale: Establish the audit semantics in source first, map those semantics to CI lanes second, generate and validate the public surface third, and only then use the generated skill for a bounded forward-test and implementation review.

## Task 1: Define the source classification and audit contract

- task_id: TSL-010
- depends_on:
  - none
- scope_slice: Revise the source `SKILL.md` and add one detailed audit reference that defines orthogonal classification fields, smallest-sufficient-layer placement, independent-oracle quality, suite split criteria, environment isolation, audit dispositions, and an actionable output schema.
- impl_file_refs:
  - src/skills/disciplines/testing-strategy/SKILL.md
  - src/skills/disciplines/testing-strategy/references/test-layering-and-suite-audit.md
- test_file_refs:
  - src/skills/disciplines/testing-strategy/references/test-layering-and-suite-audit.md
- verification_scope:
  - Before any mutation, capture `git status --short` and content hashes for every pre-existing dirty path under `organize-docs` and `tests/test_markdown_prose_wrap.py`.
  - Capture the current skill response to a bounded representative scenario set and record the missing or ambiguous classification fields as manual red evidence.
  - Run the skill-creator quick validator against `src/skills/disciplines/testing-strategy`.
  - Check that every reference linked by the source skill exists and that the new reference is directly linked from `SKILL.md`.
  - Review the source diff for preserved oracle-integrity, documentation, red-green, fixture, and output-contract guidance.
- executor_mode: main
- task_review_depth: boundary
- done_when:
  - The pre-change status and content-hash baseline for every unrelated dirty path exists before the first source edit.
  - The source skill tells the agent to classify by protected boundary, real dependency and authority scope, oracle, lane, and diagnosis owner rather than framework, path, name, or length.
  - The reference distinguishes primary evidence class, execution lane, and cross-cutting quality tags.
  - The reference defines `keep`, `refactor`, `replace`, `delete`, `split`, and `move-lane` with evidence requirements.
  - Length remains a diagnostic signal, and split decisions are tied to mixed boundaries, fixtures, authority, lanes, or diagnosis owners.
  - Source reimplementation, same-source tautologies, prose snapshots, and broad environment inheritance receive explicit replacement guidance.
  - No exact-sentence or keyword test is introduced for the natural-language skill.
- failure_policy: fix_forward

## Task 2: Define lane placement and environment authority

- task_id: TSL-020
- depends_on:
  - TSL-010
- scope_slice: Revise the capability-based CI reference so the semantic evidence classes map explicitly to `fast`, `merge`, `release`, and `runtime` lanes without collapsing test type, cost, dependency, or authority into one label.
- impl_file_refs:
  - src/skills/disciplines/testing-strategy/SKILL.md
  - src/skills/disciplines/testing-strategy/references/ci-config.md
- test_file_refs:
  - src/skills/disciplines/testing-strategy/references/test-layering-and-suite-audit.md
- verification_scope:
  - Validate that lane selection records the project-owned command, protected boundary, dependency and environment, expected duration, authority, diagnosis owner, and promotion effect.
  - Confirm current-state checks remain separate from base-comparison compatibility checks and deployed runtime evidence.
  - Confirm subprocess guidance starts from an explicit environment allowlist and defines the narrow justified exception for ambient-environment tests.
  - Rerun source skill validation and direct-link checks.
- executor_mode: main
- task_review_depth: boundary
- done_when:
  - The CI reference explains that evidence class does not mechanically determine one lane.
  - Fast evidence precedes expensive evidence, while merge, release, and runtime gates have explicit entry and authority criteria.
  - Production credentials, state, hardware, or deployment authority are never inherited merely because a test runner can access them.
  - The reference remains vendor-neutral and contains no universal numeric threshold.
- failure_policy: fix_forward

## Task 3: Generate and validate the root-flat surface

- task_id: TSL-030
- depends_on:
  - TSL-020
- scope_slice: Regenerate the tracked root-flat `testing-strategy` projection, prove exact source/generated parity, and run the complete deterministic repository validation while preserving unrelated dirty work.
- impl_file_refs:
  - skills/testing-strategy/SKILL.md
  - skills/testing-strategy/references/ci-config.md
  - skills/testing-strategy/references/test-layering-and-suite-audit.md
- test_file_refs:
  - skills/testing-strategy/references/test-layering-and-suite-audit.md
- verification_scope:
  - Reuse the pre-mutation status and content-hash baseline captured by TSL-010 for every pre-existing dirty path under `organize-docs` and `tests/test_markdown_prose_wrap.py`.
  - Run `python3 scripts/generate-skills-index.py`, `python3 scripts/flatten-skills.py --target root-flat`, and `python3 scripts/generate-workflow-diagrams.py`.
  - Require `diff -qr src/skills/disciplines/testing-strategy skills/testing-strategy` to report no difference.
  - Run `bash scripts/check.sh` and `git diff --check`.
  - Compare the final changed-path set with the approved touch set and compare every unrelated baseline hash and status.
- executor_mode: main
- task_review_depth: focused
- done_when:
  - The root-flat surface is generated rather than hand-edited and exactly matches source.
  - The index and workflow generators produce no unrelated tracked drift.
  - The aggregate check and whitespace check pass.
  - Only the six approved `testing-strategy` paths are added or modified by this milestone.
  - Every pre-existing unrelated dirty file is byte-for-byte unchanged and retains its original tracked or untracked status.
- failure_policy: stop_and_diagnose

## Task 4: Forward-test and review the revised skill

- task_id: TSL-040
- depends_on:
  - TSL-030
- scope_slice: Apply the generated skill to a bounded representative homelab scenario set, then route the exact skill diff and verification evidence through mandatory agent-native implementation review.
- impl_file_refs:
  - src/skills/disciplines/testing-strategy/SKILL.md
  - src/skills/disciplines/testing-strategy/references/ci-config.md
  - src/skills/disciplines/testing-strategy/references/test-layering-and-suite-audit.md
  - skills/testing-strategy/SKILL.md
  - skills/testing-strategy/references/ci-config.md
  - skills/testing-strategy/references/test-layering-and-suite-audit.md
- test_file_refs:
  - src/skills/disciplines/testing-strategy/references/test-layering-and-suite-audit.md
  - skills/testing-strategy/references/test-layering-and-suite-audit.md
- verification_scope:
  - Forward-test the generated skill against the 6,608-line platform cross-repository module, the 1,419-line focused RouterOS module, operations subprocess tests that copy the ambient environment, natural-language Markdown snapshots, and a test that repeats its source transformation.
  - Require the response to explain why size alone is not a verdict, identify mixed diagnosis owners where present, choose the smallest sufficient replacement oracle, assign one primary evidence class and one lane, and distinguish deletion from splitting or refactoring.
  - Require the handoff to propose one shared audit and dependency ledger followed by repo-local plans only for repositories with accepted changes, with parallel eligibility based on frozen cross-repository dependencies rather than common motivation.
  - Run `review-change` with `review-implementation` over only the approved diff, design, plan, forward-test result, aggregate evidence, and directly relevant current skill files.
  - Adjudicate all candidate findings and allow at most two total review batches.
- executor_mode: main
- task_review_depth: full
- done_when:
  - The forward-test classifies each case through the approved fields and does not rely on line-count limits, exact prose, blanket test growth, or full environment inheritance.
  - The generated skill recommends a later read-only audit and dependency ledger before repository mutation, then independently approved repo-local plans only for repositories with accepted changes.
  - Review verdict is `pass`, or every accepted in-scope finding is repaired and reverified within the review budget.
  - No homelab repository, unrelated `market-csheng` file, commit, remote, or global installed skill is changed.
- failure_policy: fix_forward

## Review Gate

- required_entry: review-change
- required_mode: review-only
- review_component: review-plan
- review_depth: boundary
- max_review_batches: 2
- review_status: passed
- review_evidence: Batch 1 produced RP-001, which was accepted and repaired by adding the shared audit ledger, independently approved repo-local plans, dependency-frozen parallel eligibility, and no-empty-plan rule; batch 2 found no remaining candidates and passed.
- supporting_files:
  - 2026-07-28-testing-strategy-layering-design.md: approved behavior, phase boundary, non-goals, and implementation surface.
  - src/skills/disciplines/testing-strategy/SKILL.md: current skill behavior being revised.
  - src/skills/disciplines/testing-strategy/references/ci-config.md: current lane and environment guidance being revised.
  - AGENTS.md: source/generated ownership, validation, review, and unrelated-work preservation rules.
  - src/skills/workflows/plan-change/SKILL.md: readiness, continuity, recovery, and human-gate requirements.
- pass_condition: The plan is a bounded serial source-first skill milestone with independent behavioral evidence, exact generated-surface verification, protected unrelated work, and an explicit later shared audit ledger plus dependency-frozen repo-local remediation boundary.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

## Recovery

- default_failure_policy: fix_forward
- recovery_evidence:
  - The pre-change Git status, content hashes for unrelated dirty paths, and source/generated parity result provide exact preservation evidence.
  - All intended changes are limited to six declared skill paths and remain uncommitted, so failed in-scope edits can be repaired with `apply_patch` without touching unrelated work.
  - If a stop contingency triggers, preserve the current diff and command evidence, make no homelab or remote change, and return the typed stop to `plan-change` or `design-change` as declared.
