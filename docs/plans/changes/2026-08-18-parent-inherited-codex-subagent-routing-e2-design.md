# Parent-Inherited Codex Subagent Routing E2 Design

## Status

- design_version: 1
- decision_status: ready_for_approval
- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly issued `approve all` on 2026-08-18 after E1 closed; mandatory bounded design review and focused verification passed.
- recommended_next_phase: plan
- next_entry: plan-change

## Problem

The approved parent-inherited Codex subagent routing plan stopped at preflight because the harness
had no exact external-file channel. E1 has now added, verified, truth-synchronized, and closed that
capability. E2 must rematerialize the routing change against the closed capability contract rather
than resume or amend the blocked plan. The E2 design also needs to declare the native role fixtures
that the earlier design omitted.

## Goals

- Make the main session model and reasoning the normal physical baseline for Codex-native
  subagents, with portable task metadata describing difficulty rather than a physical ceiling.
- Permit no override, effort-only uplift, or model-plus-explicit-effort uplift, while rejecting a
  model-only override and any silent downgrade after a required uplift is unsupported.
- Remove model and effort pins from native role files; keep sandbox and behavioral authority there.
- Route concrete role families and minimum-only reasoning floors from the user-owned global
  `AGENTS.md`; leave both `[agents]` default keys absent.
- Apply the three exact user-home content changes only through the E1 broker and retain
  metadata-only evidence.

## Non-Goals

- No change to task topology, lifecycle authority, role permissions, recursion, Herdr allocation,
  provider wire schemas, plugin installation, commit, push, publication, or live subagent trial.
- No provider identifiers in reusable skills, runtime code, generated contracts, or stable
  repository truth; they remain in the approved user-route input and user-owned instructions.
- No reasoning ceiling or cost-only down-routing below the inherited parent or declared floor.

## Change Classification

- request_kind: change-definition
- change_class: B
- design_strength: design-lite
- truth_impact: high
- boundary_impact: medium
- truth_repair: false
- recommended_next_phase: plan

## Boundaries

The existing Codex-native backend remains authoritative for binding evidence. `semantic-routing`
starts from the parent profile and emits only the uplift needed by the user route: no values when
inheritance suffices, effort only when the model remains valid, and model plus explicit effort when
the model changes. A rejected required uplift returns
`controller_binding_required_uplift_unsupported`; it may use only an already-approved unchanged-task
main fallback and never retries through `[agents]` defaults or below the required floor.

The provider-specific route is bound to
`docs/plans/changes/2026-08-18-codex-subagent-user-route-input.md` at
`sha256:21a0c38ecad5d2dce2dda797409747c5622b092ec9ae4aa5a7735a6ef6bcf1df`.
The plan, NSR-040 task, execution evidence, and candidate verification must preserve that exact ref
and digest; any mismatch stops before external baseline capture or mutation.

Role files contain only sandbox and developer-instruction boundaries. Reviewer, worker, and
explorer reject either model or effort pins. Explorer remains a factual, read-only, no-recursion,
main-synthesis role; stronger physical execution never expands that authority. The immutable
user-route input owns concrete provider choices. The three user-home targets are exact existing
regular files and may be mutated only by the E1 prepared/applied compare-and-swap broker under a
serial main-owned task.

Repository source owners remain `src/runtime/harness/` and `src/skills/`; root-flat skills, indexes,
bundled runners, PlantUML, and SVGs are generated projections. Stable docs and diagrams change only
in the truth-sync phase after implementation review.

## Acceptance Conditions

- Valid native reviewer, worker, and explorer files have no `model` or
  `model_reasoning_effort`; either pin produces the generic typed stop before output mutation.
- Native routing accepts parent inheritance, effort-only uplift, model-plus-effort uplift, and all
  runtime-supported efforts above the floor including `max` and `ultra`; model-only input fails.
- Runtime-default evidence distinguishes `[agents]` defaults from parent inheritance when the two
  defaults are absent; required-uplift rejection never removes fields or downgrades.
- Herdr envelopes, topology, locks, isolation, and explorer authority remain unchanged.
- User config parses with both subagent default keys absent; every native role file is pin-free;
  `config.toml` retains mode `0600`; global instructions encode the approved minimum-only route.
- Secret-safe structural comparisons prove `config.toml` changes only the two named `[agents]`
  defaults, `explorer.toml` changes only its effort pin and low-cost description, and `AGENTS.md`
  changes only one explicitly delimited routing block. All unrelated TOML keys and text remain
  byte-identical without being emitted into evidence or review artifacts.
- Source and generated surfaces reproduce deterministically; focused, sovereign, aggregate, and
  whitespace checks pass; a new Codex session remains the separate runtime-acceptance boundary.

## Validation

- Add failing fixture and runner oracles before behavior changes, then run focused native binding,
  workflow, topology, and unchanged Herdr tests.
- Regenerate indexes, root-flat skills, bundled runners, diagrams, and SVGs from source owners.
- Broker user-home edits from validated private candidates; verify TOML and named policy predicates
  plus the allowed-field/block structural diff without emitting unrelated content.
- Run the sovereign harness suite, aggregate check, `git diff --check`, bounded implementation
  review, truth-sync validation, and close validation.

## Recovery

- Fix forward only inside the declared repository and exact external refs.
- Stop before mutation on design, plan, input digest, path identity, ownership, mode, baseline, or
  compare-and-swap drift. Never recapture an external baseline to hide drift.
- Escalate to design or plan change if the neutral envelope, topology, Herdr contract, or touch set
  must expand. Do not weaken tests or synthesize a lower runtime binding.

## Review Gate

- required_entry: review-change
- review_component: review-design
- actor_role: delegated
- review_depth: boundary
- review_status: passed_after_focused_repair
- review_evidence: The bounded reviewer found an unbound route-input digest and an insufficient unrelated-content preservation oracle. The accepted focused repair binds the exact input ref and SHA-256 through plan, task, and execution evidence and requires secret-safe structural comparisons that preserve every unrelated key and text byte. Focused verification returned PASS.
- review_budget: One bounded design review and one focused verification review were consumed; the causal same-slice repair passed.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user's explicit `approve all` instruction binds this reviewed design on 2026-08-18.
- next_entry: plan-change

## Implementation Surface

- input_file_refs:
  - docs/plans/changes/2026-08-18-codex-subagent-user-route-input.md
- impl_file_refs:
  - src/runtime/harness/execute-runner.sh
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - docs/architecture/workflow-orchestration.md
  - README.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills.index.json
  - skills/plan-change
  - skills/implement-change
  - skills/design-change/scripts/harness/execute-runner.sh
  - skills/plan-change/scripts/harness/execute-runner.sh
  - skills/implement-change/scripts/harness/execute-runner.sh
  - skills/review-change/scripts/harness/execute-runner.sh
  - skills/sync-truth/scripts/harness/execute-runner.sh
  - skills/close-change/scripts/harness/execute-runner.sh
- external_impl_file_refs:
  - /Users/csheng/.codex/AGENTS.md
  - /Users/csheng/.codex/config.toml
  - /Users/csheng/.codex/agents/explorer.toml
- test_file_refs:
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-design-runner.sh
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - tests/fixtures/codex-agents
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
  - tests/test_implement_change_via_herdr_contracts.py
