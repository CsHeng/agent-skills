+++
artifact_kind = "design"
contract_version = 3
approval_status = "approved"

[scope]
impl_file_refs = ["scripts", "src/runtime/harness", "skills"]
test_file_refs = ["tests", "src/runtime/harness/tests"]
external_impl_file_refs = []
+++
# Design

Classification record: request_kind = accepted code-simplification audit cleanup (candidates C1–C3); change_class = dead-material removal plus one bounded undocumented-runtime-surface removal inside the already approved PDR-001 distribution boundary; design_strength = design-lite; truth_impact = none required (stable truth already documents the single external-touch staging path and never documents the removed surfaces); boundary_impact = the skill-local harness runtime CLI loses two undocumented subcommands and generated runtime bundles must be refreshed; recommended_next_phase = plan-change after mandatory design review and human design approval.

## Problem

The 2026-08-19 portable-runtime simplification (`42f06e1`) retired two validation lanes from `scripts/check.sh` but left their bodies behind: `scripts/check-fixtures.py`, `scripts/check-review-boundary.sh`, four request fixtures under `tests/fixtures/`, and four expected goldens under `tests/golden/` now have zero callers anywhere in the authored tree, so they validate nothing while still presenting themselves as checkers.

The same migration deleted the `commands/` surface, but `tests/test_command_retirement_contracts.py::test_active_command_adapters_use_owner_local_runners` still early-returns on the missing directory and asserts against deleted Shell runner scripts, passing vacuously and misrepresenting deleted behavior as guarded.

`src/runtime/harness/external_touch.py` carries two parallel pipelines to a `prepared` intent: the documented `declare` → `stage-declared` → `finalize` chain that persists a metadata-only `staging` reservation before any payload bytes survive, and an undocumented one-shot `stage` → `prepare` chain whose `stage_payload` copies raw payload bytes before any reservation exists. `docs/architecture/workflow-orchestration.md` (Optional Exact External Files) and `src/skills/workflows/implement-change/SKILL.md` (external-touch controller procedure) document only the reservation chain, so the one-shot path is a standing code-versus-truth contradiction and doubles the intent-construction code (`declare_intent` versus `prepare_intent` build near-identical twenty-field dicts) while leaving an undocumented bypass of the durable staging checkpoint; the `staging` candidate-schema branch in `validate_evidence_state` itself validates the documented chain's own staging checkpoint and remains after this cut.

## Goals

- G1 (C1): delete `scripts/check-fixtures.py`, `scripts/check-review-boundary.sh`, the four orphaned request fixtures (`read-only-request`, `micro-doc-change`, `regulated-infra-change`, `implicit-smart-commit-request`) and the four matching golden files, leaving no authored reference to either script.
- G2 (C2): collapse external-touch intent creation to the single `declare` → `stage-declared` → `finalize` pipeline: remove `prepare_intent`, remove the `stage` and `prepare` CLI subcommands, retain `stage_payload` as the internal materialization helper behind `stage_declared_payload`, and rewrite the affected tests and the ledger-test fixture helper onto the reservation chain.
- G3 (C3): delete the vacuous `test_active_command_adapters_use_owner_local_runners` test while keeping the live archive-inertness and retirement-disposition guards in the same file.

## Boundaries

### Decisions

DEC-1 (product decision held for the human approval gate): the one-shot `stage`/`prepare` path is removed rather than retained as a recovery or debugging convenience. Rationale: stable truth requires the durable staging reservation before any raw payload may survive, no doc, skill, or controller procedure names the one-shot operations, its only consumers are tests, and retaining it would keep the undocumented bypass and the dual-schema validation branch alive. Recovery and replay remain fully served by the documented chain: replay resumes either the persisted `staging` or `prepared` checkpoint without widening the ref set.

Non-goals: no change to the `prepared`/`applied` intent, baseline, or manifest evidence schemas or to broker compare-and-swap, cleanup, fsync, and replay semantics; no change to ledger schema or compatibility; no restoration of the retired Shell harness, `commands/`, the retired review-language check lane, or any retired skill; no refactor of the deliberate field-by-field task projection in `artifacts.py`/`cli.py` (audit candidate C4 rejected); no test-directory reorganization (audit candidate C5 rejected); no version bump (local development flow).

### Implementation Surface

Authored deletions: `scripts/check-fixtures.py`, `scripts/check-review-boundary.sh`, `tests/fixtures/read-only-request.json`, `tests/fixtures/micro-doc-change.json`, `tests/fixtures/regulated-infra-change.json`, `tests/fixtures/implicit-smart-commit-request.json`, all four `tests/golden/*.expected.json` files, and the vacuous test function in `tests/test_command_retirement_contracts.py`. Authored edits: `src/runtime/harness/external_touch.py` (remove `prepare_intent` and the two CLI subcommands; keep `stage_payload` internal), `tests/test_external_touch_evidence.py` (rewrite the three unit tests and one CLI test onto the reservation chain), and `src/runtime/harness/tests/test_ledger.py` (switch the external-evidence fixture helper from `stage_payload`+`prepare_intent` to `declare_intent`+`stage_declared_payload`+`finalize_intent`). Generated refresh: regenerate the tracked root-flat `skills/` payload so the six skill-local runtime bundles match the edited production runtime; no `skills.index.json` change is expected because skill metadata is untouched.

### Validation

Executable acceptance: a repository search proves no authored reference to `check-fixtures`, `check-review-boundary`, or the removed `stage`/`prepare` external-touch subcommands remains outside `docs/plans/` and changelog history; the rewritten external-touch tests still prove the full reservation chain, baseline-rooted repair chains, idempotent replay, third-state drift rejection, noop rejection, ambiguous-cleanup rejection, and secret-safe output; the ledger tests still converge tasks with complete external evidence built through the reservation chain; `python3 scripts/flatten-skills.py --target root-flat` regenerates bundles; and `bash scripts/check.sh` passes end to end, including bundle parity, contract, Ruff, ty, pytest, and Markdown lanes.

### Recovery Policy

Fix-forward inside this scope: all changes are additive deletions or test rewrites in tracked authored files, recoverable by ordinary Git history; no persisted data, ledger, or external file is touched, so no guarded rollback trigger is declared. If bundle regeneration fails, restore the immediately preceding generated tree and retry; never hand-edit generated `skills/` content.
