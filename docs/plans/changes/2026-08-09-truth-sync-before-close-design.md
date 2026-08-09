# Truth Sync Before Close Design

## Status

- design_version: 1
- decision_status: approved
- recommended_next_phase: design-full

## Problem

The harness currently permits `close-change` to accept caller-supplied review, verification, and truth-sync booleans. A caller can therefore assert `truth_sync_completed: true` without proving an approved truth-sync artifact, and an approved close decision returns `next_entry: close-change`, creating a machine-readable self-loop. The observed Drone session exercised both defects: the first close was approved from a supplied boolean before the later truth-sync artifact existed, and the close gate was then invoked repeatedly around truth-sync approval.

The lifecycle already places `sync-truth` before `close`, but `implement-change` may stop after code, verification, and review and leave the user to invoke downstream skills manually. This makes implementation completion ambiguous and can present a close approval point before stable truth reflects the verified behavior. Automatically running all of `organize-docs` would avoid one manual step but would also widen ordinary truth updates into repository-wide documentation governance without evidence that layout, search boundaries, terminology, or Markdown structure require it.

## Goals

- Define implementation completion so a truth-affecting approved work package includes stable truth synchronization before it can become close-ready.
- Preserve `implement-change` as the one execution controller, `sync-truth` as the truth mutation and approval owner, and `close-change` as a read-only final gate.
- Let an approved plan authorize its declared truth-sync mutations without requiring a second skill invocation before the truth-sync human gate.
- Require `close-change` to derive review, verification, truth-sync requirement, artifact identity, and truth-sync completion from an approved plan plus immutable execution evidence instead of accepting caller assertions.
- Return one terminal close result after all required evidence and approvals pass; never route an approved close back to `close-change`.
- Keep `organize-docs` conditional and bounded to changes that actually affect documentation organization, truth roots, search boundaries, stage-artifact placement, canonical terminology, or prose structure.
- Preserve explicit human sovereignty: truth-sync output must be inspectable before approval, and no merge, release, cleanup, commit, push, install, or deploy action is implied by a close judgment.

## Non-Goals

- Do not merge `sync-truth` or `organize-docs` behavior into `close-change`.
- Do not add a new public closeout skill, lifecycle controller, phase owner, provider command, background service, or recursive cross-skill loop.
- Do not make `organize-docs` a default post-implementation pass or authorize repository-wide Markdown normalization during ordinary truth sync.
- Do not remove the design, plan, truth-sync, or close human gates or infer approval from review and verification.
- Do not make `close-change` perform merge, release, cleanup, commit, push, install, deploy, rollback, or destructive workspace mutation.
- Do not broaden an approved plan's touch set when stable truth refs were omitted; return a typed planning stop before truth mutation instead.
- Do not change implementation review ownership, repair budgets, parallel execution, model routing, worktree isolation, or recovery-policy semantics.

## Change Classification

- request_kind: change-definition
- change_class: C
- design_strength: design-full
- truth_impact: high
- boundary_impact: high
- recommended_next_phase: design-full
- truth_sync_required: true
- parallel_candidate: false

## Boundaries

- in_scope:
  - Make the approved plan declare the stable truth mutation surface required by a truth-affecting work package.
  - Make `implement-change` distinguish implementation tasks complete, truth-sync pending, close-ready, and terminal close states.
  - Permit controller-routed `sync-truth` mutation under an approved plan while preserving explicit approval of the resulting truth-sync artifact.
  - Make `sync-truth` conditionally compose `organize-docs` only when a declared or observed docs-governance predicate is true inside the approved touch set.
  - Replace caller-supplied review, verification, truth-sync requirement, and truth-sync completion at close with approved-plan and artifact-derived evidence.
  - Replace the successful close self-route with an explicit terminal state.
  - Update focused runtime smoke tests, contract validation, source skills, generated root-flat surfaces, stable workflow truth, architecture diagrams, and the design-decision changelog.
- out_of_scope:
  - Automatically fix missing stable truth scope after plan approval.
  - Treat every changed Markdown file as evidence that `organize-docs` is required.
  - Change direct user invocation of `sync-truth`; explicit truth-maintenance requests remain valid.
  - Execute external close actions or claim that an approved close judgment proves merge, release, cleanup, commit, push, install, or deploy completion.

## Architecture Decision

- architecture_decision_id: TSC-001-evidence-bound-pre-close-truth
- decision_status: selected
- decision_horizon: The current sovereign harness contract epoch, until external close actions require a separately approved execution owner.
- demand_evidence: A real session produced an approved close from an unproven truth-sync boolean, then created a pending truth-sync artifact and re-entered close multiple times; current runtime code also returns the successful close entry to itself.
- scarce_resource: Human approval attention and trustworthy lifecycle evidence; users should review one prepared truth state instead of manually discovering and repairing phase-order mistakes.
- hard_requirements:
  - The public invocation graph remains acyclic and retains one owner per lifecycle phase.
  - Repository mutation requires explicit user intent or an approved upstream artifact.
  - Truth-sync approval remains artifact-backed and human-sovereign.
  - Close remains read-only and cannot manufacture upstream evidence.
  - Approved task and truth touch sets remain immutable during execution.

### Options

- status_quo: Keep explicit downstream skill invocations, caller-supplied booleans, and `close -> close`. Rejected because it allows false-positive closure, exposes phase mechanics to the user, and encodes a successful self-loop.
- smallest_sufficient: Keep existing owners, make the approved implementation unit advance through required truth sync, conditionally compose docs governance, bind close to the approved artifact, and return a terminal close state. Selected because it repairs evidence and ordering without adding another controller or moving mutation into close.
- structural_investment: Add a public `closeout-change` controller or merge truth sync and docs organization into `close-change`. Rejected because it duplicates lifecycle authority, creates close-to-truth back edges or a new top-level owner, obscures mutation permissions, and raises recurring routing and review cost.

### Ownership And Economics

- marginal_tradeoff: The selected option adds plan metadata, artifact binding, typed states, and focused tests, but removes repeated user turns, caller-trusted truth booleans, and successful close recursion without the larger cost of a new orchestration surface.
- opportunity_cost: The change consumes one design, plan, runtime, generated-surface, and stable-doc update cycle; the alternative would leave approval integrity dependent on agent discipline and continue producing confusing closeout sessions.
- owner_and_incentives: `plan-change` owns the approved stable truth surface, `implement-change` owns continuous phase progression, `sync-truth` owns stable truth mutation and its human gate, conditional `organize-docs` owns docs-governance technique only, and `close-change` owns the final read-only judgment and terminal result.
- comparative_advantage: Existing workflow owners already carry the required contracts and bundled runtime; extending their explicit handoffs has lower lifecycle and discovery cost than introducing a new closeout controller.
- chosen_option: Evidence-bound pre-close truth synchronization with conditional docs governance and terminal close.
- upgrade_trigger: Reconsider a separate external-action owner only if merge, release, or cleanup execution needs durable state, resumability, and recovery semantics that cannot remain an explicit human action after close approval.
- recovery_and_oracle: Fix forward inside the approved repository-local touch set; prove artifact-derived truth status, conditional docs composition, absence of successful close recursion, generated parity, and aggregate harness validity with deterministic tests.

## Lifecycle Contract

### Prepared Close Sequence

- `implement-change` may report task execution complete after task convergence, verification, and bounded review, but it may report `ready_for_close` only after required truth sync is complete and approved.
- When `truth_sync_required: true`, the approved execution unit routes directly to `sync-truth` and prepares the minimum stable truth updates inside the approved touch set before presenting the truth-sync human gate.
- A plan with required truth impact must declare non-empty stable truth refs. Missing or out-of-touch-set refs return `truth_sync_scope_required` to `plan-change`; they never fall through to close and never authorize opportunistic docs mutation.
- The approved design and plan plus immutable execution result are authoritative for `truth_sync_required`, review status, verification status, design identity, plan identity, and allowed truth refs. Close callers cannot supply or override those values.
- `sync-truth` creates or updates its artifact with a pending approval state, records the verified stable truth refs, and stops for explicit human approval.
- The same explicit user message may approve the prepared truth-sync artifact and request a close mode, but close evaluation starts only after the approval has been recorded and revalidated.
- `close-change` consumes the approved plan and immutable execution result, derives the current review, verification, and truth-sync requirement, and validates either a derived `truth_sync_required: false` or one approved truth-sync artifact whose exact `approved_design_ref`, `approved_plan_ref`, `review_gate_ref`, `verification_ref`, and stable truth refs match that evidence package.
- Any caller-provided status hint is non-authoritative and a mismatch with derived evidence fails closed; a caller cannot bypass truth sync by supplying `truth_sync_required: false` or `truth_sync_completed: true`.
- An approved close returns `terminal_state: closed`, `next_entry: null`, and the selected close mode as judgment metadata. A blocked close returns exactly one owning route such as `sync-truth`, `implement-change`, or `plan-change`.
- The phase engine treats `close` as terminal after an approved close result instead of resolving it to itself.

### Conditional Organize Docs

- `sync-truth` does not activate `organize-docs` merely because stable truth files are Markdown.
- Compose `organize-docs` only when the approved truth scope or current bounded diff changes README/AGENTS/CLAUDE ownership, stable truth roots, docs search boundaries, stage-artifact placement, canonical terminology across surfaces, or Markdown prose structure governed by that skill.
- When the predicate is false, `sync-truth` updates the minimum stable facts and runs only repository-owned focused documentation checks required by the approved plan.
- When the predicate is true, `organize-docs` remains a lower-plane component under `sync-truth`; it cannot advance approval or close state and cannot widen beyond the approved truth touch set.

### Controller Mutation Authorization

- Direct public invocation remains guarded by explicit user request for both `sync-truth` and `organize-docs`.
- Controller-routed invocation is a separate authorization path: `implement-change` may invoke `sync-truth` only with an approved plan, resolved design, immutable execution result, declared stable truth refs, and the exact allowed touch set.
- The skill contract records both permitted mutation authorities: direct explicit user intent or an approved upstream plan. Neither authority implies the other, and controller invocation without the complete context fails closed.
- `sync-truth` may compose `organize-docs` without another user turn only when the approved plan authorizes the same truth refs, a declared docs-governance predicate matches, and the composed work remains inside the same immutable touch set.
- Direct `$organize-docs` behavior remains unchanged; no controller handoff makes it generally implicit or permits native matching to mutate docs without explicit intent.

## Approval Contract

- Design and plan approvals remain separate upstream gates.
- Truth-sync mutation is authorized by an approved plan whose touch set includes the declared stable truth refs; the resulting artifact remains pending until the user explicitly approves its content.
- Public direct truth-maintenance mutation still requires explicit user intent; automatic pre-close mutation is valid only through the approved-plan controller context and is not a general implicit invocation permission.
- Close approval is evaluated only after truth-sync approval when truth sync is required. A single explicit `approve and close` instruction may satisfy both gates only when the complete prepared truth artifact and close mode are already visible and unambiguous.
- Review and verification never imply truth-sync or close approval.
- Direct premature `$close-change` invocation returns the current owning phase without asking the user to approve an incomplete close package.

## Acceptance Conditions

- Focused tests reproduce the current false-positive by showing that a free `truth_sync_completed=true` can approve close, then fail until close requires a real approved artifact.
- Plan validation rejects truth-affecting work packages with missing stable truth refs and execution rejects truth refs outside the approved touch set.
- Execute-runner evidence distinguishes task completion, truth-sync pending, ready-for-close, and terminal close without relying on conversation state.
- A required truth-sync route is deterministic after passing implementation review and verification and does not require the user to invoke another skill before the truth-sync human gate.
- A caller cannot override an approved plan's derived truth-sync requirement, review status, verification status, design identity, plan identity, or allowed stable truth refs.
- A required plan plus a caller-supplied false truth flag still requires truth sync, and a pending, missing, invalid, mismatched, or unapproved truth-sync artifact blocks close with the correct owning route.
- Artifact validation rejects mismatched design, plan, review, verification, or stable truth refs rather than checking only that those keys are present.
- An approved matching truth-sync artifact allows one close decision whose terminal result has no self-referential `next_entry`.
- `resolve_next_phase` or its successor cannot produce `close -> close` for an approved close result.
- Tests prove `organize-docs` remains inactive for a simple stable-fact update and activates only for each declared docs-governance predicate inside the approved touch set.
- Contract and runtime tests prove direct explicit mutation and controller-approved mutation are distinct accepted authorities, while incomplete controller context and out-of-touch-set docs composition fail closed.
- Source workflow skills, contracts, bundled runtime, root-flat generated skills, stable architecture truth, generated diagrams, and changelog describe the same ownership and terminal semantics.
- Required generators, sovereign harness smoke tests, `bash scripts/check.sh`, and `git diff --check` pass with no unrelated tracked drift.
- Bounded implementation review leaves no accepted current-slice finding unresolved.

## Validation

- Run design and plan artifact validation plus bounded `review-design` and `review-plan` gates.
- Add red-green focused smoke coverage for plan truth scope, execute continuation, truth artifact binding, conditional docs composition, blocked routes, and terminal close.
- Run `bash src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh`, `bash src/runtime/harness/smoke-test/test-design-runner.sh`, `bash src/runtime/harness/smoke-test/test-plan-runner.sh`, `bash src/runtime/harness/smoke-test/test-design-plan-skill-control.sh`, `bash src/runtime/harness/smoke-test/test-agent-native-review.sh`, `bash src/runtime/harness/smoke-test/test-artifact-dag.sh`, `bash src/runtime/harness/smoke-test/test-recovery-routing.sh`, `bash src/runtime/harness/smoke-test/test-execute-runner.sh`, and `bash src/runtime/harness/smoke-test/test-review-execute-skill-control.sh`.
- Run focused close and truth-sync smoke tests, repository generators, root-flat parity checks, architecture diagram generation, aggregate validation, and whitespace validation.
- Route the exact implementation diff and declared evidence through bounded `review-change` with `review-implementation`.

## Recovery Policy

- default_failure_policy: fix_forward
- recovery_surface: Preserve the pre-implementation Git state and repair only inside the approved source, contract, runtime, tests, generated projections, and stable documentation surfaces.
- guarded_rollback: not_required
- stop_conditions:
  - Stop with `needs-design-decision` if preserving the acyclic public invocation graph requires a new lifecycle owner or makes `close-change` mutation-capable.
  - Stop with `needs-plan-change` if automatic truth sync cannot be bounded by the approved stable truth refs and touch set.
  - Stop with `manual-decision-required` if existing approved artifacts cannot be supported without silently treating an unproven boolean as truth evidence.

## Review Gate

- required_entry: review-change
- review_component: review-design
- actor_role: delegated
- review_status: passed
- candidate_findings:
  - accepted: Bind truth-sync requirement and artifact identity to the approved plan and immutable execution evidence; reject caller overrides and mismatched refs.
  - accepted: Define controller-only mutation authorization for automatic sync-truth and conditional organize-docs while retaining explicit-request guards for public direct entry.
- review_evidence: Initial delegated boundary review found two current-design authorization and evidence-binding gaps; both were accepted and repaired. Focused verification review passed with no remaining candidate finding and confirmed approved-plan evidence derivation, caller-override rejection, distinct direct versus controller mutation authority, and immutable touch-set preservation.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed design and requested `plan-change` on 2026-08-09.
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - contracts/skills.toml
  - contracts/workflow-modes.toml
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/workflows/sync-truth/SKILL.md
  - src/skills/workflows/close-change/SKILL.md
  - src/skills/disciplines/organize-docs/SKILL.md
  - src/runtime/harness/contracts.sh
  - src/runtime/harness/artifact-dag.sh
  - src/runtime/harness/plan-runner.sh
  - src/runtime/harness/execute-runner.sh
  - src/runtime/harness/evaluation-gate.sh
  - src/runtime/harness/truth-sync-runner.sh
  - src/runtime/harness/close-runner.sh
  - src/runtime/harness/phase-engine.sh
  - docs/architecture/workflow-orchestration.md
  - docs/architecture/harness-state-machine.md
  - docs/architecture/maintenance-contract.md
  - docs/changelog/design-decisions.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills
  - skills.index.json
- test_file_refs:
  - scripts/check-contracts.py
  - scripts/check.sh
  - scripts/generate-skills-index.py
  - scripts/flatten-skills.py
  - scripts/generate-workflow-diagrams.py
  - tests
  - src/runtime/harness/smoke-test/test-kernel-contracts.sh
  - src/runtime/harness/smoke-test/test-kernel-phase.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
  - src/runtime/harness/smoke-test/test-close-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-plan-skill-control.sh
  - src/runtime/harness/smoke-test/test-agent-native-review.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - src/runtime/harness/smoke-test/test-review-execute-skill-control.sh
