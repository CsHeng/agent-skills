# Decision Lifecycle, Code Simplification, And Durable Prose Plan

## Status

- plan_version: 3
- plan_contract_version: 2
- approval_required: true
- approval_status: approved
- implementation_status: complete
- plan_review_status: passed_v3_delta_review
- implementation_review_status: passed_after_one_bounded_repair
- implementation_verification_status: passed
- implementation_hold: false
- implementation_hold_reason: LCSP-000 rechecked approved plan version 3 at the same clean source baseline and returned `ready_to_implement`; the known truth-sync fixture regression is now declared LCSP-020 work.
- execution_stop_reason: truth_sync_required
- recommended_next_phase: truth-sync
- next_entry: sync-truth

## Upstream Design

- design_ref: 2026-08-18-decision-lifecycle-code-simplification-durable-prose-design.md
- design_version: sha256:991c63bcc621de54926bde75809a4e71525637e842003dbb79e599a1badc0ca3
- design_approval_status: approved
- architecture_decision_ref: LCSP-001-bounded-long-horizon-maintenance-guidance

## Implementation Scope

- target_repository: market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- impl_file_refs:
  - README.md
  - contracts/skills.toml
  - docs/AGENTS.md
  - docs/README.md
  - docs/changelog/design-decisions.md
  - docs/architecture/diagrams/skill-planes.puml
  - docs/architecture/diagrams/skill-trigger-ownership.puml
  - docs/architecture/generated/skill-planes.svg
  - docs/architecture/generated/skill-trigger-ownership.svg
  - src/skills/disciplines/code-simplification
  - src/skills/disciplines/organize-docs
  - src/skills/disciplines/skill-miner/scripts/extract-session-signals.py
  - src/skills/policies/development-standards
  - src/skills/session/use-coding-skills/references/routing.toml
  - src/skills/workflows/sync-truth/SKILL.md
  - src/runtime/harness/contracts.sh
  - src/runtime/harness/plan-runner.sh
  - skills/.source-map.json
  - skills.index.json
  - skills/code-simplification
  - skills/organize-docs
  - skills/development-standards
  - skills/skill-miner
  - skills/use-coding-skills
  - skills/design-change/scripts/harness
  - skills/plan-change/scripts/harness
  - skills/implement-change/scripts/harness
  - skills/review-change/scripts/harness
  - skills/sync-truth
  - skills/close-change/scripts/harness
- test_file_refs:
  - tests/test_skill_routing_contracts.py
  - tests/test_install_target_contracts.py
  - tests/test_maintenance_guidance_contracts.py
  - src/skills/disciplines/skill-miner/tests/test_extract_session_signals.py
  - src/runtime/harness/smoke-test/test-kernel-contracts.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
- verification_commands:
  - `python3 -m unittest tests.test_skill_routing_contracts tests.test_install_target_contracts`
  - `python3 -m unittest tests.test_maintenance_guidance_contracts`
  - `python3 src/skills/disciplines/skill-miner/tests/test_extract_session_signals.py`
  - `bash src/runtime/harness/smoke-test/test-kernel-contracts.sh`
  - `bash src/runtime/harness/smoke-test/test-plan-runner.sh`
  - `bash src/runtime/harness/smoke-test/test-truth-sync-runner.sh`
  - `python3 scripts/generate-skills-index.py`
  - `python3 scripts/flatten-skills.py --target root-flat`
  - `python3 scripts/generate-workflow-diagrams.py`
  - `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`
  - `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`
  - `bash scripts/check.sh`
  - `uvx --with pyyaml python "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .`
  - `rg -n -i 'deepseek|reclaim-code-entropy|superpowers|mattpocock' README.md docs/changelog src/skills skills tests`
  - `git diff --check`

## Work Package Readiness

- milestone_objective: Implement the approved smallest-sufficient maintenance boundary: one read-only `code-simplification` public discipline, one future-value-aware decision-record lifecycle with an exact bounded docs predicate, concise durable-prose rules in existing owners, and root-README-only inspiration acknowledgements, while preserving all sovereign lifecycle and source/generated ownership contracts.
- non_goals:
  - Add apply mode, automatic refactoring, periodic cleanup, broad code metrics, quota-driven note archival, or deletion of tracked `docs/plans/` history.
  - Add a public durable-prose or authoring-session-leakage skill, adopt any other external skill, or import upstream files, wording, workflows, scripts, or note layouts.
  - Expand ordinary implementation review into pre-existing simplification discovery or allow a simplification audit to mutate, plan, delegate implicitly, or approve a product tradeoff.
  - Rewrite all historical decisions or prose, introduce exact-sentence Markdown tests, or remove operational standards, dependency references, protocol links, user-supplied targets, or legally required notices.
  - Change lifecycle phases, phase owners, human approval gates, plan contract version, provider-specific model policy, plugin version, external installation state, commits, pushes, publication, or deployment.
- future_phase:
  - Add mechanical simplification scanners only after repeated independent audits prove one advisory candidate class can be detected without deciding deletion.
  - Add a dedicated stable-decision archive or retirement tool only after observable search/navigation ambiguity survives current stable/stage and supersession boundaries.
  - Reconsider a public durable-prose skill only after measured direct-intent routing need or substantial policy duplication across additional owners.
  - Reconsider `code-simplification` activation only after measured over-triggering survives description and negative-boundary repair.
- decision_status: ready_for_review
- oracle_strategy: Use contract tests for public skill metadata, routing ownership, semantic dependency closure, owner-reference wiring, acknowledgement-link placement, and generated projection; an environment-independent metadata-tamper fixture plus model/state-list smoke tests for the docs predicate across kernel, plan validation, and truth-sync composition; source/generated parity checks for root-flat skills, runner bundles, index, and diagrams; bounded semantic review as the declared substitute oracle for decision-matrix and durable-prose meaning. Do not freeze natural-language sentences or keyword collections in unit tests.
- acceptance_oracles:
  - A structured contract test fails before and passes after `code-simplification` exists as a native primary, non-mutating, non-delegating discipline with one owned negative-bounded routing case and router dependency closure.
  - Kernel, plan-runner, and truth-sync smoke tests fail before and pass after `decision-record-lifecycle` is accepted by the shared predicate owner and the plan-side allowlist, activates bounded `organize-docs`, rejects unknown values, and preserves `none` behavior.
  - Under the checkout's default environment, the truth-sync fixture derives a tampered mode that is guaranteed to differ from the recorded parent mode; the existing fail-closed metadata assertion passes without changing external-touch runtime behavior.
  - A focused maintenance-guidance contract test parses owner-relative Markdown links, requires the decision-lifecycle reference to resolve from `organize-docs`, derives acknowledgement URLs from root README rather than duplicating them in test code, and proves those exact links are absent from the stable design log and source/generated skill payloads.
  - Bounded review confirms the independently written decision lifecycle and durable-prose guidance preserve complete propositions, current-`HEAD` resolvability, stable/stage separation, generated-owner ordering, visible-string behavior oracles, and ordinary review causality without duplicating an external workflow.
  - The targeted attribution search over current non-stage human, source, generated, and test surfaces returns the approved project references only in root `README.md`; neutral fixture/example names replace third-party branding, while operational references remain untouched.
  - Regeneration produces the new root-flat skill, changed owner skills, router projection, six runner bundles, skill index, skill-plane and trigger-ownership diagrams deterministically; aggregate checks and plugin validation pass.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Oracle Traceability

| Approved boundary | Executable oracle or declared substitute | Diagnosis owner |
|---|---|---|
| Public simplification authority and route | Structured TOML/routing assertions in `tests/test_skill_routing_contracts.py` | Contract/routing maintainer |
| Predicate identity, plan acceptance, and bounded truth-sync activation | Kernel, plan-runner, and truth-sync smoke tests | Harness maintainer |
| External-touch metadata tamper regression | The truth-sync fixture derives a mode unequal to the recorded parent mode and exercises the existing evidence validator under the default environment | Harness test maintainer |
| Decision-lifecycle owner wiring and acknowledgement placement | `tests/test_maintenance_guidance_contracts.py` parses relative links and derives acknowledgement URLs from root README; it does not duplicate prose or external URL literals | Documentation/skill contract maintainer |
| Future-value dispositions and durable-prose semantic meaning | Mandatory bounded semantic review is the substitute oracle because the rules are human-authored judgment, not a machine schema; exact-sentence and keyword tests are forbidden | Main review adjudicator with `organize-docs` and `development-standards` ownership |
| Visible-string verification policy | Bounded review verifies that the policy requires a surface-owned runtime/snapshot oracle; this milestone changes no application-visible string whose behavior could be executed | Matching future surface owner |
| Authored-owner-before-generated ordering | Generator parity, source map, root-flat comparison, diagram freshness, bundled-harness checks, and aggregate validation | Generator and install-surface maintainers |
| Root-only acknowledgement outcome | Focused structural link-placement test plus final targeted non-stage search | Documentation/skill contract maintainer |

## Approved Architecture Decision

- architecture_decision_ref: LCSP-001-bounded-long-horizon-maintenance-guidance
- decision_fidelity: Implement exactly one new read-only public discipline and one bounded docs predicate. Keep decision lifecycle in `organize-docs`, code-adjacent durable prose in `development-standards`, skill-instruction provenance policy in `skill-authoring.md`, truth-sync authority in `sync-truth`, and acknowledgements in root `README.md`. Do not create another lifecycle, router, prose skill, or apply path.
- reversible_increments:
  - LCSP-000 proves the current repository baseline and exact touch set before mutation; a mismatch exits without changing files.
  - LCSP-010 adds the public audit owner and its structured routing oracle as a separable unit; removing the entry and route restores the prior discovery surface.
  - LCSP-020 adds the decision lifecycle reference and predicate behind existing truth-sync containment; if predicate integration cannot remain exact, retain the direct guidance and stop before enabling composition.
  - LCSP-030 adds owner-local prose and attribution changes without changing public routing or executable behavior; each source remains independently reversible.
  - LCSP-040 regenerates deterministic projections and verifies stable truth after all authored sources converge; projections are never hand-edited.
- upgrade_triggers:
  - Return `needs-design-decision` if rebaseline shows that lifecycle ownership, routing ownership, docs predicate semantics, source/generated boundaries, or the selected one-skill architecture no longer match the approved design.
  - Return `needs-plan-change` if the design remains valid but current files, generators, exact test ownership, task dependencies, or the approved touch set have changed.
  - Do not add automated archival, deletion, apply mode, another public skill, or broader review scope without a new approved design.
- recovery_boundary: Fix forward inside the rebaselined exact touch set. Remove the new route, skill entry, reference, or predicate only when their own focused oracle cannot be satisfied; preserve stage history and all unrelated concurrent work.

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 1. LCSP-000 through LCSP-040 are dependency-ordered and main-owned. The shared contract, documentation, test, and generated surfaces make parallel writer integration costlier than the expected work, and the implementation hold requires one controller to adjudicate the refreshed baseline before any mutation.
- worker_binding_policy: Not applicable; every task uses `executor_mode: main`, delegation is forbidden, and no isolated delegated writer is authorized.
- reviewer_binding_policy: Plan and implementation review may use one bounded read-only reviewer under `review-change`; the main controller adjudicates all candidates and owns any accepted repair.

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C1:
    - question: Has the unrelated concurrent repository work finished, so the controller may perform the final read-only rebaseline and, if it matches this design and plan, begin implementation?
    - applies_to: LCSP-000, LCSP-010, LCSP-020, LCSP-030, LCSP-040
    - resolution: pre_confirmed
    - default_if_unanswered: stop
- runtime_contingencies:
  - X1: If LCSP-000 finds an unowned diff on any planned write ref, preserve it and return `blocked_source_baseline`; do not stage, overwrite, regenerate across, or absorb it.
  - X2: If LCSP-000 finds material authority, lifecycle, routing, predicate, or owner-boundary drift, return `needs-design-decision` before mutation.
  - X3: If LCSP-000 finds only task-order, exact-ref, generator, or oracle drift inside the approved architecture, return `needs-plan-change` before mutation.
  - X4: If a focused or aggregate oracle fails outside causal changed paths, stop and diagnose; repair only accepted in-scope failures and never weaken routing, predicate, stable/stage, attribution, or generated-parity oracles.
- planned_stop_points:
  - none
- task_ordering_rationale: Freeze and adjudicate the baseline before any write; add the new public owner with its structured routing oracle; add decision lifecycle and predicate semantics with state-list smoke coverage; then apply prose, attribution, and stable-truth changes; regenerate and run broad checks only after all authored sources converge.

## LCSP-000 Rebaseline Result

- prior_result: needs-plan-change
- result: ready_to_implement
- observed_head: 3ffad008f2fc76193b643e3263d4ce5aea380fc0
- checkout: `/Users/csheng/workspace/playground/market-csheng` on `main`, using the approved current-checkout controller path
- status_classification: All planned source, test, and generated refs are clean. The only worktree entries are the untracked design and plan artifacts for this change. All known subagents are completed.
- intervening_change_classification: Commits `1639e8f` and `3ffad00` added external-touch evidence and Codex routing/cachebuster changes. The new `code-simplification` ID and `decision-record-lifecycle` predicate remain absent; the approved architecture and ownership boundaries still hold.
- passing_evidence: Approved design digest and version-3 plan validation pass; contract validation passes; the source/test/generated refs remain clean at `3ffad008f2fc76193b643e3263d4ce5aea380fc0`; all known subagents are completed; the worktree preflight requires no additional reminder; the new skill and predicate IDs remain absent before their planned red-green tasks.
- prior_blocking_evidence: `bash src/runtime/harness/smoke-test/test-truth-sync-runner.sh` failed at `after metadata not preserved from the parent should fail closed`. The test creates its parent under umask `022`, producing mode `0644`, then assigns tampered `after.mode = "0644"`, so the evidence is unchanged. The same test passes under umask `077`, confirming fixture drift rather than a missing runtime mode check.
- resolved_plan_delta: Plan version 3 authorizes a smallest-slice fixture correction that derives a mode guaranteed to differ from the recorded parent mode, retains the existing fail-closed assertion, reruns it under the default environment, and keeps all external-touch runtime behavior outside this change.
- plan_resolution: Incorporated into LCSP-020 in plan version 3 without adding files, changing the DAG, or widening runtime behavior.

## Recovery

- default_failure_policy: fix_forward
- baseline_boundary: LCSP-000 is zero-mutation and uses `stop_and_diagnose`; it cannot repair drift by adopting or discarding another task's work.
- source_boundary: After rebaseline, change only the approved task refs and preserve every unrelated tracked or untracked path.
- oracle_boundary: Add structured behavior or contract oracles before their implementation; do not delete or weaken assertions, broaden exact predicate acceptance, or replace semantic review with phrase snapshots to obtain a pass.
- docs_boundary: Keep `docs/plans/` as retained stage history, update only declared stable truth, and transfer every unique durable fact before compacting any stable decision entry.
- generated_boundary: Repair authored source or generator causes, then regenerate. Do not patch root-flat skills, bundled harness files, PlantUML, SVG, or the skill index by hand.
- attribution_boundary: Restore missing operational or legally required references at their owner; remove only inspiration acknowledgements and branded examples that the approved design assigns to root README.
- external_boundary: Plugin install/update, commit, push, publication, deployment, provider actions, and close are not recovery actions under this plan.
- guarded_rollback: none

## Task 1: Rebaseline and freeze the implementation boundary

- task_id: LCSP-000
- depends_on:
  - none
- scope_slice: After C1 is explicitly confirmed and immediately before any implementation write, capture the current `HEAD`, branch, `git status --short`, applicable repository instructions, contracts, routing, affected owner skills, harness predicate sources, generators, and focused tests. Classify every changed path; compare all approved architecture assumptions and provisional refs with the current baseline; emit a refreshed exact touch-set and worktree decision or a typed stop.
- impl_file_refs:
  - none
- test_file_refs:
  - none
- verification_scope:
  - Confirm the approved design still validates and its digest, architecture decision, lifecycle owners, activation modes, stable/stage boundary, and implementation hold match this plan.
  - Confirm every planned write ref is clean or belongs to an explicitly completed baseline; identify all source/generated projections that the current generators will actually change.
  - Confirm the current plan-runner still validates version-2 metadata and that no current predicate, routing, or test owner has moved.
  - Produce `ready_to_implement`, `blocked_source_baseline`, `needs-design-decision`, or `needs-plan-change`; only `ready_to_implement` permits LCSP-010.
- failing_oracle_first: Not applicable; this is a read-only baseline and readiness oracle.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: deep
- isolation: shared-read-only
- resource_locks:
  - repository-baseline
- task_review_depth: boundary
- done_when:
  - C1 is recorded as pre-confirmed and the refreshed baseline evidence names the current `HEAD`, checkout, status classification, exact task refs, and source/generated owners.
  - No planned write ref contains an unowned concurrent diff and no material design or plan drift remains.
  - The controller records `ready_to_implement` and the approved checkout/worktree choice before the first mutation.
- failure_policy: stop_and_diagnose

## Task 2: Add the read-only code-simplification owner and routing contract

- task_id: LCSP-010
- depends_on:
  - LCSP-000
- scope_slice: Add `code-simplification` as a thin native primary discipline with `may_mutate_repo = false` and `may_spawn_agent = false`; author an independent evidence-oriented `SKILL.md`, focused candidate-evidence reference, and provider metadata; add the `code-simplification-audit` routing case with explicit ordinary-cleanup, performance, apply, and bounded-review negatives; add the router semantic dependency without changing phase routes.
- impl_file_refs:
  - contracts/skills.toml
  - src/skills/session/use-coding-skills/references/routing.toml
  - src/skills/disciplines/code-simplification
- test_file_refs:
  - tests/test_skill_routing_contracts.py
- verification_scope:
  - Add a structured test that requires the new skill's contract metadata, owned trigger case, negative boundaries, and `use-coding-skills.semantic_requires` edge; run it before source changes and capture the expected failure.
  - After implementation, run `python3 -m unittest tests.test_skill_routing_contracts` and `python3 scripts/check-contracts.py`.
  - Review the new skill semantically for read-only authority, exact audit scope, consumer/compatibility/history evidence, protected trust and durability boundaries, valid `no-safe-cut`, and design-change handoff for apply intent.
- failing_oracle_first: Add the structured public-contract and routing assertions before the skill, contract entry, or routing case; confirm they fail because `code-simplification` is absent, then make the smallest source changes that pass.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - skill-exposure-contract
  - semantic-routing-contract
- task_review_depth: deep
- done_when:
  - The new public skill is the sole direct owner for read-only simplification audit intent and cannot mutate or delegate.
  - Apply, ordinary task cleanup, performance-only, and current-diff review requests remain with their existing owners.
  - Focused contract and routing validation passes without changing lifecycle phase routes.
- failure_policy: fix_forward

## Task 3: Add decision lifecycle and bounded truth-sync composition

- task_id: LCSP-020
- depends_on:
  - LCSP-010
- scope_slice: First repair the existing truth-sync metadata-tamper fixture so its changed mode is derived from and guaranteed to differ from the recorded parent mode under any supported umask, without changing external-touch runtime behavior. Then add the owner-local decision-record lifecycle reference and link it conditionally from `organize-docs`; implement current-state stable-document prose rules there; add `decision-record-lifecycle` to the shared harness predicate owner and plan-side allowlist; update `sync-truth` to name the exact bounded composition case; update local docs truth policy for future-value promotion, negative guardrails, partial/full supersession, and no default stage-history deletion.
- impl_file_refs:
  - docs/AGENTS.md
  - docs/README.md
  - src/skills/disciplines/organize-docs
  - src/skills/workflows/sync-truth/SKILL.md
  - src/runtime/harness/contracts.sh
  - src/runtime/harness/plan-runner.sh
- test_file_refs:
  - src/runtime/harness/smoke-test/test-kernel-contracts.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
- verification_scope:
  - Replace only the fixed truth-sync tampered mode with a deterministic alternate selected from the recorded parent mode; run the unmodified fail-closed assertion under the default environment and confirm it passes before adding predicate expectations. Do not modify external-touch evidence code or weaken any metadata check.
  - Extend the kernel predicate sequence, plan-side accepted/rejected predicate fixtures, and truth-sync bounded-composition loop before changing source; confirm each new case fails for the expected unsupported-predicate reason.
  - After implementation, run the three focused smoke tests and confirm `none`, unknown-value rejection, stable-ref containment, and simple-fact behavior remain unchanged.
  - Review the decision matrix semantically: proposals stay stage-only; implemented high-future-value decisions promote minimum durable truth; recurring rejected alternatives may become stable negative guardrails; full supersession requires fact transfer and link repair; partial supersession stays linked.
- failing_oracle_first: Preserve the observed default-environment failure as the fixture-regression reproducer, correct only the tamper value, and confirm the existing external-touch assertion passes. Then add `decision-record-lifecycle` to the shared expected sequence and valid plan/truth-sync fixtures, confirm current sources reject it, and update only the two predicate owners and the documentation owners required by the design.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - docs-governance-contract
  - stable-docs-boundary
  - external-touch-test-fixture
- task_review_depth: deep
- done_when:
  - The new predicate is accepted identically by plan validation and truth-sync runtime composition and remains bounded to approved stable refs.
  - The truth-sync smoke test passes with the default umask because its tampered mode differs from the recorded parent mode, while the runtime evidence validator remains unchanged.
  - `organize-docs`, `sync-truth`, `docs/AGENTS.md`, and `docs/README.md` agree on future-value classification, stable/stage ownership, and supersession safety.
  - All focused predicate smoke tests pass without widening truth sync or rewriting stage artifacts.
- failure_policy: fix_forward

## Task 4: Absorb durable prose and centralize acknowledgements

- task_id: LCSP-030
- depends_on:
  - LCSP-020
- scope_slice: Add concise independently written current-`HEAD`, complete-proposition, owner-first, and visible-string verification rules to `development-standards` and `skill-authoring.md`; place both approved inspiration references and the independent-rewrite statement in root `README.md`; remove the duplicate acknowledgement from the stable design log; record the implemented local architecture decision without external provenance; neutralize the branded `skill-miner` CLI example and fixtures; remove the test-only external acknowledgement URL assertion without replacing it with a prose snapshot.
- impl_file_refs:
  - README.md
  - docs/changelog/design-decisions.md
  - src/skills/policies/development-standards
  - src/skills/disciplines/skill-miner/scripts/extract-session-signals.py
- test_file_refs:
  - tests/test_install_target_contracts.py
  - tests/test_maintenance_guidance_contracts.py
  - src/skills/disciplines/skill-miner/tests/test_extract_session_signals.py
- verification_scope:
  - Run the install-target and skill-miner tests after neutralizing examples and removing only the acknowledgement-specific URL assertion; preserve all structured distribution, provider, and usage-classification assertions.
  - Add `tests/test_maintenance_guidance_contracts.py` before attribution edits. Parse owner-relative Markdown links and derive the root acknowledgement URL set at runtime; do not embed external project URLs or natural-language policy sentences in the test. Confirm the pre-change stable design log violates the placement contract, then make the owner changes that pass.
  - Run a source-only attribution search over `README.md`, `docs/changelog`, `src/skills`, and tests; expected non-stage inspiration acknowledgement hits are confined to root README. LCSP-040 repeats the search against generated `skills` after regeneration.
  - Use bounded semantic review and `git diff --check` for prose meaning; do not add exact sentence, keyword-set, heading, or absence tests for Markdown guidance.
  - Confirm operational standards, protocol/dependency references, user-supplied URLs, and legally required notices remain at their owners.
- failing_oracle_first: Add the structural owner-link and acknowledgement-placement test before the attribution edits and confirm the stable design log duplicates root acknowledgement links. Natural-language rule meaning still uses bounded semantic review rather than phrase-level tests.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - durable-prose-policy
  - root-acknowledgements
  - skill-miner-fixtures
- task_review_depth: deep
- done_when:
  - Durable prose rules preserve all factual clauses and current owners while removing authoring-session narration from current-state surfaces.
  - Activated source skills contain no inspiration acknowledgement or upstream provenance text, and root README is the sole current human-facing acknowledgement owner.
  - Neutral examples preserve `skill-miner` behavior and focused tests pass without a new prose oracle.
- failure_policy: fix_forward

## Task 5: Regenerate projections and run integrated verification

- task_id: LCSP-040
- depends_on:
  - LCSP-030
- scope_slice: Regenerate the skill index, root-flat public payload, provider metadata, skill-plane and trigger-ownership PlantUML/SVG views, and all six runner-owner harness bundles from converged authored sources; run focused, aggregate, sovereign-surface, artifact-DAG, plugin, attribution-placement, and whitespace gates; record truth-sync readiness without installing or publishing the plugin.
- impl_file_refs:
  - docs/architecture/diagrams/skill-planes.puml
  - docs/architecture/diagrams/skill-trigger-ownership.puml
  - docs/architecture/generated/skill-planes.svg
  - docs/architecture/generated/skill-trigger-ownership.svg
  - skills/.source-map.json
  - skills.index.json
  - skills/code-simplification
  - skills/organize-docs
  - skills/development-standards
  - skills/skill-miner
  - skills/use-coding-skills
  - skills/design-change/scripts/harness
  - skills/plan-change/scripts/harness
  - skills/implement-change/scripts/harness
  - skills/review-change/scripts/harness
  - skills/sync-truth
  - skills/close-change/scripts/harness
- test_file_refs:
  - none
- verification_scope:
  - Run all top-level verification commands in diagnostic order: focused Python and harness tests, generators, sovereign and artifact-DAG smoke tests, aggregate check, plugin validator, attribution search, and `git diff --check`.
  - Confirm regenerated source maps, provider policy, semantic dependency closure, root-flat references, bundled predicate sources, skill index, and diagrams all resolve the new public ID and predicate from authored truth.
  - Compare final changed paths with the LCSP-000 frozen touch set and reject any undeclared or concurrently introduced path.
- failing_oracle_first: Generation freshness is expected to fail after authored source changes and before regeneration; regenerate once from source, then require check mode and aggregate validation to leave no residual generated diff.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - generated-skill-surface
  - workflow-diagrams
  - harness-bundles
- task_review_depth: deep
- done_when:
  - Every focused and aggregate oracle passes without weakening an assertion or editing a generated artifact by hand.
  - The exact final diff is contained by the frozen plan touch set and excludes unrelated concurrent work.
  - The controller records review and truth-sync readiness; no plugin install, version bump, commit, push, publication, deployment, or close occurs.
- failure_policy: fix_forward

## Truth Sync Handoff

- stable_truth_refs:
  - README.md
  - docs/AGENTS.md
  - docs/README.md
  - docs/changelog/design-decisions.md
- docs_governance_predicates:
  - stable-truth-roots
  - canonical-terminology-across-surfaces
- bootstrap_note: This plan cannot use `decision-record-lifecycle` for its own handoff because the current validator does not recognize that predicate until LCSP-020 executes. The existing `stable-truth-roots` and `canonical-terminology-across-surfaces` predicates govern this bootstrap truth sync; future approved plans may use the new exact predicate.
- handoff_scope: After implementation, convergence, and bounded review pass, synchronize the public skill inventory, stable/stage decision boundary, future-value lifecycle, durable-prose ownership, root-README acknowledgement boundary, and the new local architecture decision. Generated skills and diagrams remain subordinate projections and must converge before truth-sync approval.

## Review Gate

- required_entry: review-change
- review_component: review-plan
- actor_role: delegated
- review_depth: boundary
- review_status: passed
- candidate_findings: none
- review_evidence: Plan version 2 passed after one bounded oracle-coverage repair. The fresh version-3 delta review was limited to the LCSP-000 evidence and LCSP-020 environment-independent fixture correction and returned `PASS: v3 fixture delta is execution-ready`; it found no design-containment, runtime-behavior, touch-set, DAG, red-green, continuity, or approval-gate regression.
- review_budget: One bounded version-3 delta review was consumed. No focused repair review was needed.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved plan version 3 and requested `coding:implement-change` on 2026-08-18.
- next_entry: implement-change
- post_approval_entry: implement-change
- implementation_entry_condition: C1 is pre-confirmed. After version-3 approval, LCSP-000 must recheck the same `HEAD`/worktree boundary and recognize the declared fixture regression as planned LCSP-020 work before any write begins.
