# Decision Lifecycle, Code Simplification, And Durable Prose Design

## Status

- design_version: 2
- decision_status: ready_for_approval
- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed design and invoked `$coding:plan-change` on 2026-08-18. Approval does not lift the separate implementation hold or waive the required pre-implementation rebaseline.
- implementation_hold: true
- implementation_hold_reason: Unrelated repository work is still changing the shared checkout, including paths that may overlap the provisional harness test surface. Implementation must not start until that work finishes and the pre-implementation rebaseline in this design passes.
- recommended_next_phase: plan
- next_entry: plan-change

## Problem

The repository already distinguishes stable truth from historical stage artifacts and already limits ordinary implementation and review to request-causal cleanup. It does not yet define how a decision's future value controls promotion, retention, supersession, or retirement; it has no direct read-only owner for a deliberate cross-cutting code-simplification audit; and its durable prose rules are split across documentation, implementation, and skill-authoring surfaces without one explicit current-repository-vantage test.

Those gaps matter in long-running agent coding. A stage artifact can be mistaken for current truth, an ordinary implementation request can grow into unrelated debt removal, and comments, prompts, diagnostics, or stable docs can retain authoring-session identifiers, review choreography, or change narration that a later reader cannot resolve at `HEAD`. External techniques can help, but importing their files or workflow authority would duplicate this repository's sovereign harness, activation contracts, documentation boundary, and review/approval gates.

The repository also repeats project-inspiration acknowledgements outside the root human-facing acknowledgement section and carries one third-party-branded example in a distributed helper. These references do not help an activated agent perform its task and should not consume skill context.

## Goals

- Define a repository-neutral decision-record lifecycle that classifies future value without rewriting, quota-archiving, or deleting `docs/plans/` history by default.
- Add one public, read-only `code-simplification` discipline that finds, proves, ranks, and rejects simplification candidates without acquiring mutation or lifecycle authority.
- Absorb only the useful durable-prose rules into current owners for stable documentation, code-adjacent prose, prompts, diagnostics, visible strings, and skill instructions; do not add a second prose or response-style authority.
- Keep every simplification selected for implementation behind the existing `design-change` -> `plan-change` -> `implement-change` -> `review-change` -> `sync-truth` lifecycle.
- Keep inspiration acknowledgements and source links in the repository root `README.md`, use an independent local rewrite, and remove acknowledgement or branded-example noise from distributed skills.
- Preserve source/generator ownership, provider-neutral behavior, deterministic validation, and the current human approval gates.

## Non-Goals

- Do not import, copy, vendor, or translate an upstream `SKILL.md`, script, note tree, lifecycle state machine, prompt, or repository-specific taxonomy verbatim.
- Do not adopt any other external skill beyond the four concerns already selected by the user: decision-record lifecycle, code simplification, durable prose, and authoring-session leakage.
- Do not add a top-level workflow, another router, an automatic refactoring mode, an unattended cleanup loop, a repository-wide debt quota, or a deletion target.
- Do not let `code-simplification` edit files, create plans, write TODOs, spawn breadth agents implicitly, or become part of ordinary implementation review discovery.
- Do not create a new public durable-prose skill. Existing owners are sufficient for the selected rules, and another public entry would add routing and prompt-context cost without a distinct authority boundary.
- Do not retroactively rewrite all existing decision entries, stable docs, comments, tests, prompts, diagnostics, or stage artifacts in the first milestone.
- Do not archive or delete tracked stage artifacts solely because an implemented or rejected idea has low future value. Git history is not a substitute for the repository's explicit retained stage boundary.
- Do not remove normative protocol, standard, dependency, tool, or legally required license references from the surface where they are operationally required.
- Do not start planning or implementation in this design turn, touch the concurrent work, bump the plugin version, reinstall plugins, commit, push, publish, or deploy.

## Change Classification

- request_kind: change-definition
- change_class: C
- design_strength: design-full
- truth_impact: high
- boundary_impact: high
- truth_repair: false
- truth_sync_required: true
- parallel_candidate: false
- recommended_next_phase: design-full

## Boundaries

### Ownership Map

| Concern | Durable owner | Authority boundary |
|---|---|---|
| Decision-record creation, promotion, supersession, and retirement policy | `organize-docs`, composed by `sync-truth` only through a declared predicate | Documentation judgment only; it cannot widen the approved stable-truth touch set or replace the truth-sync gate |
| Cross-cutting simplification discovery | New `code-simplification` discipline | Read-only evidence and ranked dispositions; it cannot mutate, plan, review an implementation slice, or approve a product tradeoff |
| Stable-document prose | `organize-docs` | Current-state documentation rules inside explicitly requested or approved refs |
| Comments, JSDoc/docstrings, prompts, diagnostics, help text, and visible strings | `development-standards` | Conditional implementation policy; the lifecycle owner still controls mutation, tests, review, and close |
| Skill and agent-instruction prose | `development-standards/references/skill-authoring.md` | Thin operational instructions and provenance placement; no second routing or lifecycle contract |
| Transient conversational rendering | Existing `output-styles` | Unchanged; it remains the response baseline and is not made responsible for persisted artifact cleanup |
| Project acknowledgements and inspiration links | Root `README.md` | Human-facing attribution only; no provenance prose in activated skill payloads |

### Decision-Record Lifecycle

`organize-docs` gains an owner-local reference for decision-record lifecycle. The reference applies when creating, promoting, superseding, compacting, or retiring a durable decision record; it does not make every documentation edit a decision audit.

The lifecycle uses current status and future value together:

| Current status | Future-value test | Local disposition |
|---|---|---|
| Proposed | The decision is not yet implemented or rejected | Keep it as a stage artifact. A proposal is never archived or promoted merely to satisfy a quota. |
| Implemented | Future maintainers need the boundary, rationale, consequences, compatibility obligation, or reconsideration trigger | Promote or update the minimum durable truth in the stable decision owner and keep the stage artifact as historical evidence. |
| Implemented | Only one-time execution mechanics remain useful | Leave the detail in stage history and do not promote it. Compact an already-stable record only after every unique durable fact has another current owner. |
| Rejected | The alternative remains tempting, risky, or likely to recur | Retain a concise stable negative guardrail with the rejection reason and observable reconsideration trigger. |
| Rejected | The alternative is obsolete and no longer prevents a plausible mistake | Do not promote it to stable truth. Leave an existing tracked stage artifact in history unless a separately approved cleanup proves deletion is safe and useful. |
| Superseded or removed | A newer owner fully covers every surviving behavior and decision fact | Transfer unique rationale, material alternatives, consequences, verification gaps, compatibility facts, and reintroduction triggers; repair inbound links; then compact or retire the old stable entry. |
| Partially superseded | Any public, persisted, wire, migration, compatibility, safety, or independently current negative decision survives | Keep the old and new owners cross-linked. Do not claim full supersession. |

A newly written or materially updated stable decision records the current decision and status, the constraint it resolves, material alternatives and discard reasons, consequences, the responsible owner, an observable reconsideration trigger, and any supersession links. Existing entries are migrated only when touched for a real decision update; this milestone does not manufacture a full-log rewrite.

The harness gains the exact docs-governance predicate `decision-record-lifecycle`. An approved plan declares it only when truth sync must create, promote, supersede, compact, or retire stable decision truth. The predicate activates bounded `organize-docs` composition for declared stable refs; it does not activate for a simple stable fact update, and it never makes `docs/plans/` a stable-truth ref.

### Code-Simplification Discipline

The new public contract is:

```toml
[skills.code-simplification]
source = "src/skills/disciplines/code-simplification"
public_id = "code-simplification"
category = "discipline"
install = ["claude", "codex", "root-flat"]
lifecycle_owner = false
activation_mode = "native"
default_role = "primary"
may_mutate_repo = false
may_spawn_agent = false
```

It owns one semantic routing case, `code-simplification-audit`. The skill frontmatter owns the positive boundary: use it for an explicit read-only request to find, prove, compare, or rank codebase simplification candidates. The routing case rejects ordinary task-local cleanup, performance tuning, implementation/apply requests, and bounded current-diff review. `use-coding-skills.semantic_requires` gains the new public ID because the installed router must resolve the case; lifecycle phase routes do not change.

The first milestone surveys only the user-declared repository or subsystem scope and returns a small number of well-supported candidates. Useful candidate classes are unconsumed surfaces, duplicated representations of one fact, speculative generality, extra indirection or packages, duplicated lifecycle state, misplaced defenses, hand-rolled infrastructure with a lower-cost maintained owner, support residue, and added-then-abandoned behavior. Static scanners and text search produce leads, not deletion proof.

Every reported candidate contains:

- a stable candidate ID, class, exact scope, and current owner
- production, test, documentation, generated, dynamic-entrypoint, public API, persisted-data, wire-format, migration, and compatibility consumer evidence as applicable
- the exact proposed cut or collapse, the observable behavior that would be lost, and whether that loss is a product decision
- the rationale or history that currently protects the surface, including evidence that defeats or preserves it
- net maintenance reduction after replacement glue, tests, docs, generated artifacts, and dependency lifecycle are counted
- confidence, risk, the smallest decisive executable oracle, and one disposition: `recommend-design`, `reject`, `defer-for-evidence`, or `no-safe-cut`

The audit preserves trust, authentication, authorization, security, accessibility, data-loss, durable compatibility, and quiescence boundaries unless an explicit product decision changes them. It identifies generated, vendored, migration, fixture, public-package, and dynamic-loader surfaces before classifying consumers, and it judges the authored owner rather than proposing edits to a projection. Finding no safe cut is a successful result.

If the user wants a reported cut applied, the audit returns its evidence as bounded input to `design-change`. It does not switch itself into apply mode, add TODOs, write a proposal artifact, or enter planning. `review-implementation` remains causality-bound to the approved task diff and cannot invoke this discipline to turn pre-existing debt into repair scope.

### Durable Prose And Authoring-Session Leakage

No new prose skill is added. The selected rules are independently restated at the existing owner boundaries:

- `organize-docs` requires stable prose to stand at the current repository state, routes change stories to stage or historical owners, and excludes untargeted stage and archived material from modernization.
- `development-standards` applies the same durable-artifact test to comments, JSDoc/docstrings, prompts, diagnostics, help text, examples, configuration comments, and model- or user-visible strings.
- `skill-authoring.md` keeps activated instructions focused on behavior, scope, authority, and verification; inspiration acknowledgements belong to the package's human-facing attribution surface rather than runtime prompt context.

Before trimming or rewriting a passage, the owner preserves every relevant actor and action, condition, timing and ordering rule, modality, negative guarantee and exception, ownership transfer, side effect, failure mode, and consequence. Smaller word count is not success if a complete proposition or non-obvious rationale is lost. Comments retain non-obvious contracts and rationale but do not narrate control flow that the code already expresses.

The current-state test is: a reader at `HEAD`, without the authoring session, review thread, branch stack, or uncommitted draft, can resolve every internal reference and verify every claim. Dead design or audit labels, review choreography, reviewer-addressed argument, temporary phase names, hedged planning residue, and current-state change narration are removed or restated as durable facts. Exact committed decision, issue, postmortem, standard, or measured-evidence references remain when they still own useful context.

Owner prose changes before generated projections. A prompt, diagnostic, help string, or model/user-visible sentence is behavior: wording changes need the narrow snapshot, contract test, or runtime oracle owned by that surface. The prose policy never authorizes repository-wide normalization through a task that touched one sentence.

### Attribution Boundary

The root `README.md` remains the sole human-facing acknowledgement owner. Implementation adds the two approved research references there, beside the existing Superpowers acknowledgement, and states that the local material is independently rewritten and subordinate to repository contracts. The exact references are:

- `https://github.com/deepseek-ai/deepseek-harness/tree/master/.agents/skills`
- `https://github.com/Yevanchen/reclaim-code-entropy/blob/main/skills/reclaim-code-entropy/SKILL.md`

No upstream project name, URL, acknowledgement paragraph, copied header, or provenance note is added to the new or modified `SKILL.md` files or their references. The duplicate inspiration sentence in `docs/changelog/design-decisions.md` is removed without deleting the decision facts it accompanies. The third-party-branded `skill-miner` CLI example and its fixture names become neutral examples. Operational standards, libraries, protocol references, user-supplied target URLs, and legally required notices are outside this attribution-only cleanup.

### Source And Generated Surfaces

All authored behavior lives under `src/skills/`, `contracts/skills.toml`, the installed routing contract, stable documentation, and harness source. The tracked root-flat `skills/`, `skills.index.json`, provider metadata, PlantUML sources, and SVGs are regenerated; they are never edited by hand. The new skill uses a thin `SKILL.md`, an owner-local evidence reference, and generated provider metadata.

### Implementation Hold And Pre-Implementation Rebaseline

This design was classified against `main` at `4f81b9fa4580e06b0b55ec35e63f05d149f3b2b0` while unrelated work was active in the shared checkout. At design time, `src/runtime/harness/plan-runner.sh` and `src/runtime/harness/smoke-test/test-plan-runner.sh` already overlap the provisional decision-predicate surface. Those edits belong to the concurrent work and must not be overwritten, staged, reformatted, or treated as part of this change.

Implementation remains held until the user confirms that the other work is finished. Immediately before implementation, the controller must:

1. Capture the new `HEAD`, branch, `git status --short`, and applicable `AGENTS.md` files; classify every remaining changed path as current-task, completed baseline, unrelated live work, or blocker.
2. Re-read `contracts/skills.toml`, the installed routing contract, the affected owner skills, harness predicate contracts, generators, and focused tests from the new baseline.
3. Compare the new baseline with every design assumption, routing owner, activation mode, docs predicate, source/generated boundary, and provisional implementation ref in this artifact.
4. Recompute the exact plan touch set and task DAG. Do not begin while any planned write ref has an unowned concurrent diff.
5. Return to `design-change` and repeat design review for a material authority, lifecycle, predicate, routing, or owner-boundary change. For task ordering, exact touch-set, or oracle drift that leaves this design intact, amend and re-review the plan before execution.
6. Run the normal one-time worktree preflight and choose a safe checkout only after the refreshed plan is approved. A clean or fully classified baseline is evidence; it is not permission to implement without the plan gate.

## Architecture Decision Economics

- architecture_decision_id: LCSP-001-bounded-long-horizon-maintenance-guidance
- decision_status: selected
- decision_horizon: The current sovereign-harness and docs-truth-boundary epoch, until measured routing or maintenance evidence triggers a separately approved change.
- current_demand: Long-running agent work needs durable decisions and prose without letting broad cleanup escape the approved task, and maintainers need an explicit way to ask for simplification evidence before committing to a product or architecture change.
- constrained_resource: Model discovery context, reviewer attention, stable-truth signal, and maintainer capacity to keep public skills, routing cases, harness predicates, generated surfaces, and tests aligned.
- hard_requirements: One lifecycle owner per request; no direct simplification mutation; stable truth and stage history remain distinct; source owners precede projections; attribution does not consume activated skill context; external ideas remain lower-plane techniques.

### Options

- status_quo: Keep the current scattered rules and handle each request ad hoc. Rejected because no owner can perform a broad simplification audit without colliding with task-local scope, and decision promotion or prose cleanup would continue to depend on session judgment.
- selected_smallest_sufficient: Add one read-only public simplification discipline, one owner-local decision lifecycle reference plus one bounded docs predicate, and concise durable-prose clauses in existing owners; centralize acknowledgements in the root README. This adds the minimum new discovery surface while preserving current lifecycle and documentation authority.
- structural_investment: Import a full external note lifecycle, automatic archive/delete mechanics, apply-capable simplification workflow, separate prose and leakage skills, periodic audits, and broad linters. Rejected because it duplicates repository contracts, increases prompt and validation surface, and would authorize premature mutation or history cleanup.

### Lifecycle Tradeoff And Upgrade Triggers

- marginal_tradeoff: One public skill and one harness predicate add contract, routing, generated-surface, and test cost. Keeping durable prose inside existing owners avoids a second new public skill and offsets context growth.
- opportunity_cost: This milestone consumes review and maintenance attention that could otherwise slim existing skills; the scope is therefore limited to one audit owner, one decision reference, and short owner-local prose rules.
- owner_and_cost_bearer: `code-simplification` owns candidate evidence; `organize-docs` owns decision and stable-doc judgment; `development-standards` owns persisted code-adjacent prose policy; `sync-truth` owns mutation gating; repository maintainers bear routing, generator, and test upkeep.
- comparative_advantage: The discipline can survey beyond one task without mutating, while lifecycle workflows remain better positioned to approve, implement, verify, and synchronize a selected cut.
- upgrade_trigger_archive_mechanics: Introduce a separate stable-decision archive layout or mechanical retirement tool only after the active decision corpus creates observable navigation or search ambiguity that the stable/stage boundary and supersession links cannot resolve.
- upgrade_trigger_simplification_tooling: Add structural scripts only after repeated independent audits demonstrate the same mechanically detectable candidate class and a scanner can remain advisory rather than decide deletion.
- upgrade_trigger_prose_skill: Reconsider a public durable-prose skill only if the same substantial policy must be duplicated across additional owners or measured routing repeatedly needs a direct prose-audit intent that current owners cannot express.
- downgrade_trigger: If the new simplification description repeatedly captures ordinary refactors or implementation review, narrow it or make it explicit; do not compensate with a second router.
- recovery_boundary: Remove the new public entry, route, reference, and predicate and regenerate if their contracts cannot be made deterministic. Existing lifecycle data and stage artifacts require no rollback because the milestone adds guidance and gates rather than migrating repository state.

## Oracle Strategy

- protected_boundary: Read-only simplification ownership, exact routing and activation metadata, bounded decision-lifecycle composition, stable/stage separation, complete durable propositions, root-only inspiration acknowledgements in distributed behavior, and source-before-generated ownership.
- oracle_owner: Contract tests own public skill metadata and routing; harness smoke tests own the docs predicate; focused prose and attribution tests own selected clauses and placement; generator checks own install surfaces and diagrams; review owns boundary coherence.
- selected_methods:
  - Add focused contract tests proving `code-simplification` is native, primary, non-mutating, non-delegating, owns its case, is reachable from the router, and rejects apply/review/ordinary-cleanup scope.
  - Extend kernel, plan-runner, and truth-sync smoke tests so `decision-record-lifecycle` is supported, activates only its declared bounded component, rejects unknown predicates, and preserves `none` behavior.
  - Add focused assertions for decision lifecycle dispositions, durable-prose current-state and complete-proposition rules, generated-owner ordering, visible-string verification, and lifecycle handoff.
  - Verify acknowledgement references are present in the root README and absent from source and generated skill instruction payloads; verify the duplicate stable-doc acknowledgement and branded distributed example are gone.
  - Regenerate the skill index, root-flat payload, routing/plane diagrams, and runner-owner harness bundles, then run aggregate and provider metadata checks.
- discarded_methods: Repository-wide deletion counts, generic complexity thresholds, automatic dead-code deletion, full prose golden snapshots, fixed reading grades, live provider runs, and wholesale historical-doc rewrites do not prove the selected boundaries.
- oracle_change_policy: Any apply-capable simplification mode, automatic decision deletion, stage-history migration, public prose skill, new lifecycle owner, or relaxed attribution placement requires a new design review rather than implementation repair.

## Acceptance Conditions

- An explicit read-only simplification request selects `code-simplification`; an ordinary implementation, task-local orphan cleanup, performance audit, apply request, or bounded implementation review does not.
- The simplification result can recommend, reject, defer, or report no safe cut, and every recommendation carries consumer, ownership, compatibility, behavior-loss, risk, and oracle evidence sufficient for a later design decision.
- A selected simplification cannot mutate until it passes the existing design, plan, implementation, review, truth-sync, and human approval contracts.
- `decision-record-lifecycle` is a supported exact predicate and cannot widen stable refs, promote `docs/plans/`, or activate for `none`.
- Proposed, implemented, rejected, superseded, and partially superseded decisions follow the future-value matrix without quota-driven archival or deletion.
- Stable decisions written or materially changed after this milestone name current authority, meaningful alternatives, consequences, owner, and observable reconsideration trigger; untouched historical entries are not rewritten just for conformity.
- Durable prose preserves complete factual propositions and non-obvious rationale while removing or restating unresolvable authoring-session references, review choreography, change narration, control-flow restatement, and unsupported hedges.
- Stage and archived artifacts remain outside default prose modernization; generated prose changes begin at the authored owner; model- or user-visible wording changes have a matching behavior oracle.
- The new and modified skill payloads contain no inspiration acknowledgement or upstream provenance text. Root `README.md` contains the approved source links and independent-rewrite statement, and the duplicate stable-doc acknowledgement is removed.
- Current operational external references and legally required notices remain at their owned point of use.
- The source tree, contract, routing case, semantic dependency closure, generated metadata, root-flat skill, skill index, PlantUML, SVG, and harness bundles agree.
- Pre-implementation rebaseline finds no unowned overlap. Material baseline drift returns to design; plan-only drift is amended and reviewed before execution.

## Validation

- Validate this artifact with the bundled `design-runner.sh`, then route it through `review-change` using `review-design` at boundary depth.
- During implementation, run focused Python contract tests for routing, install/attribution, skill behavior, and neutralized skill-miner fixtures.
- Run `bash src/runtime/harness/smoke-test/test-kernel-contracts.sh`, `bash src/runtime/harness/smoke-test/test-plan-runner.sh`, and `bash src/runtime/harness/smoke-test/test-truth-sync-runner.sh` for the new predicate.
- Regenerate with `python3 scripts/generate-skills-index.py`, `python3 scripts/flatten-skills.py --target root-flat`, and `python3 scripts/generate-workflow-diagrams.py`.
- Run `bash scripts/check.sh`, `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`, `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`, provider plugin metadata validation, and `git diff --check` after the final generated and stable-truth sync.
- Compare final changed paths with the rebaselined approved plan. Do not run live providers, install/update plugins, commit, push, publish, deploy, or modify unrelated concurrent work as validation.

## Recovery

- Default to fix-forward inside the rebaselined approved touch set.
- If routing over-triggers, narrow the description and negative case before changing activation mode; if it still collides after focused evidence, stop for a design decision.
- If the new predicate cannot remain exact and bounded, keep decision lifecycle as direct documentation guidance and stop before enabling controller composition.
- If durable-prose trimming loses a factual clause, restore the complete proposition from the authored owner and rerun the narrow surface oracle; do not restore authoring-session narration as rationale.
- If generated outputs drift, repair the source contract or generator and regenerate; do not patch generated skills or diagrams.
- If rebaseline finds concurrent overlap or material contract drift, make no implementation mutation. Preserve the other work and return to the appropriate design or plan gate.
- No guarded rollback is required: this milestone creates no external state or data migration, and every approved repository edit has a deterministic source owner and fix-forward oracle.

## Review Gate

- required_entry: review-change
- review_component: review-design
- actor_role: delegated
- review_depth: boundary
- review_status: passed
- candidate_findings: The delegated reviewer raised one candidate that the implementation surface omitted a truth-sync predicate consumer. The main adjudication rejected it as `rejected_insufficient_evidence`: `truth-sync-runner.sh` sources `execute-runner.sh`, which sources `phase-engine.sh`, which sources `contracts.sh`; the runtime uses `is_valid_docs_governance_predicate` and `HARNESS_DOCS_GOVERNANCE_PREDICATES` from that declared source owner, while `plan-runner.sh` owns its separate plan-side allowlist. Both source owners and the truth-sync smoke oracle are already in the design surface.
- review_evidence: The design artifact passed the bundled validator and whitespace validation. The main controller sourced `truth-sync-runner.sh` and confirmed that its live predicate function and array resolve from `contracts.sh`, so no runtime source edit is missing. With the candidate rejected, the bounded goals, ownership, routing, oracle, recovery, attribution, and rebaseline boundaries have no accepted finding.
- review_budget: Consumed one initial bounded delegated design review. No accepted finding required repair or a focused verification review.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed design and invoked `$coding:plan-change` on 2026-08-18. Implementation remains separately gated by an approved plan and the pre-implementation rebaseline.
- next_entry: plan-change
- post_approval_entry: plan-change
- implementation_entry_condition: A separately approved plan plus the completed pre-implementation rebaseline are required before `implement-change` may start.

## Implementation Surface

- impl_file_refs:
  - README.md
  - contracts/skills.toml
  - docs/AGENTS.md
  - docs/README.md
  - docs/changelog/design-decisions.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - src/skills/disciplines/code-simplification
  - src/skills/disciplines/organize-docs
  - src/skills/disciplines/skill-miner/scripts/extract-session-signals.py
  - src/skills/policies/development-standards
  - src/skills/session/use-coding-skills/references/routing.toml
  - src/skills/workflows/sync-truth/SKILL.md
  - src/runtime/harness/contracts.sh
  - src/runtime/harness/plan-runner.sh
  - skills
  - skills.index.json
- test_file_refs:
  - tests/test_maintenance_guidance_contracts.py
  - tests/test_skill_routing_contracts.py
  - tests/test_install_target_contracts.py
  - src/skills/disciplines/skill-miner/tests/test_extract_session_signals.py
  - src/runtime/harness/smoke-test/test-kernel-contracts.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - scripts/check.sh
