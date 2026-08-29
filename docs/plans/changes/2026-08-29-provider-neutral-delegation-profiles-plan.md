# Provider-Neutral Delegation Profiles Implementation Plan

## Status

- plan_version: 1
- design_ref: `docs/plans/changes/2026-08-29-provider-neutral-delegation-profiles-design.md`
- design_sha256: `369b1144513286b9f6d5cecdbff84674a4dea6780f8f12b307f61708a42ec4cb`
- design_approval_status: approved
- approval_status: approved
- approval_basis: The user explicitly requested creation and approval of this repository's design-change and plan-change artifacts.
- decision_state: approved_waiting_for_implementation_authority
- implementation_authority: approved
- implementation_status: pass
- truth_sync_required: true
- implementation_review_required: true
- plan_review_status: passed_after_repair

## Milestone

Add a small provider-neutral semantic vocabulary and repository-root readiness check to planning, preserve those optional hints during implementation, regenerate install surfaces, and prove that no runtime, provider, model, or scheduler ownership moved into this Skill repository.

## Preconditions

Satisfied:

- The bounded design is approved and its direct design review passed.
- Authored Skill truth is under `src/skills/`.
- `contracts/skills.toml` owns public metadata.
- Root-flat `skills/`, indexes, and diagrams are generated and must not be hand-edited.
- Existing check and generation scripts provide deterministic source/projection evidence.

Pending:

- Repository mutation requires a separate implementation request; artifact approval alone does not authorize execution.
- Commit, push, installation, publication, deployment, and mutation of another repository remain separately unauthorized.

No account, credential, physical, or external service prerequisite blocks repository-local implementation.

## Oracle strategy

Use contract examples and source/projection invariants:

- A small structured semantic-vocabulary reference is the executable source for allowed profile values and required delegation-readiness facts. It explicitly declares itself non-runtime metadata.
- Focused tests parse that reference, require the approved vocabulary, protect `may_spawn_agent` ownership, and reject provider/model/runtime binding fields.
- Existing generation checks prove authored-to-root-flat parity and index determinism.
- Existing prose-wrap and repository checks protect installable Skill quality.
- One bounded implementation review evaluates whether the final diff accidentally creates a controller, concrete route policy, or mandatory delegation gate.

Do not assert large exact prose blocks. The Skill's behavioral obligation is covered by source review and the structured vocabulary; generated copy correctness is covered by repository generators.

## Frozen semantic constants

```text
execution_profile = fast | balanced | deep
reasoning_profile = light | standard | deep
```

Delegation-ready task facts:

```text
repository_owner
write_set
resource_locks
isolation
convergence_owner
verification
done_when
failure_policy
```

These are planning semantics only. No concrete provider, model, thinking level, tool argument, working-directory flag, scheduler limit, retry count, actor binding, attempt, or session state may enter maintained Skill truth.

## Task graph

```text
PDP-100 planning-semantics ─┐
                           ├── PDP-300 generated-contracts ── PDP-400 convergence-review
PDP-200 implementation-hint┘
```

`PDP-100` and `PDP-200` may run in parallel because their authored write sets are disjoint and the semantic constants above are frozen. `PDP-300` is the sole generation owner. `PDP-400` owns stable truth and final review.

## PDP-100 — Add canonical planning semantics and root readiness

**Depends on:** none

**Parallel group:** `authored-skill-semantics`

**Delegation eligibility:** allowed for one repository-local documentation/Skill slice

**Repository owner:** `market-csheng`

**Locks:** `plan-change-authored-source`, `delegation-profile-vocabulary`

**Write set:**

- `src/skills/workflows/plan-change/SKILL.md`
- `src/skills/workflows/plan-change/references/delegation-profiles.toml`

**Work:**

- Add a concise structured reference with `semantic_vocabulary_version = 1`, the two approved enum lists, the required delegation-readiness fact names, and an explicit `runtime_contract = false` declaration.
- Teach `plan-change` to read that reference when delegated or subagent-assisted implementation is explicitly requested.
- Require each task claimed delegation-ready in that context to state profiles, one repository owner, repository-relative write set, locks, isolation, convergence owner, verification, completion evidence, and failure policy.
- Require multi-repository milestones to split writable delegation slices by repository root or keep cross-repository integration parent-owned.
- Preserve existing optional delegation behavior for ordinary plans; absent profiles remain valid when delegation readiness is not being claimed.
- Keep provider/model settings, scheduler mechanics, exact host tool fields, and lifecycle state out of the Skill.

**Verification:**

```bash
python3 - <<'PY'
from pathlib import Path
import tomllib
path = Path('src/skills/workflows/plan-change/references/delegation-profiles.toml')
with path.open('rb') as handle:
    data = tomllib.load(handle)
assert data['semantic_vocabulary_version'] == 1
assert data['execution_profiles'] == ['fast', 'balanced', 'deep']
assert data['reasoning_profiles'] == ['light', 'standard', 'deep']
assert data['runtime_contract'] is False
PY
git diff --check -- src/skills/workflows/plan-change
```

**Done when:**

- One Skill-visible reference owns the canonical words without defining runtime tool arguments.
- `plan-change` makes single-root readiness explicit only when delegated execution is requested or readiness is claimed.
- A normal serial plan remains valid without the optional fields.

**Failure policy:** fix forward. If the task needs a concrete consumer schema or parser, stop with `needs_design_decision`.

## PDP-200 — Preserve optional profiles in implementation semantics

**Depends on:** none

**Parallel group:** `authored-skill-semantics`

**Delegation eligibility:** allowed for one repository-local documentation/Skill slice

**Repository owner:** `market-csheng`

**Locks:** `implement-change-authored-source`

**Write set:**

- `src/skills/workflows/implement-change/SKILL.md`

**Work:**

- In preconditions and execution guidance, tell the active agent to preserve approved repository ownership, isolation, locks, write set, and optional execution/reasoning profiles when it chooses a compatible delegation mechanism.
- State that profiles are hints rather than authority: no host mapping is required, missing values do not block implementation, and the active agent may retain the task.
- Preserve parent ownership of scope, invocation, verification judgment, review adjudication, repair, continuation, and final response.
- Do not name Pi, an extension, model family, provider, tool schema, or concrete thinking level.
- Keep current review and single-repair policy unchanged.

**Verification:**

```bash
rg -n 'execution_profile|reasoning_profile|repository|write set|convergence' src/skills/workflows/implement-change/SKILL.md
git diff --check -- src/skills/workflows/implement-change/SKILL.md
```

The `rg` command is inspection evidence only; final acceptance comes from the complete repository checks and review, not exact prose matching.

**Done when:**

- The implementation owner preserves optional semantic hints when delegating but neither requires delegation nor interprets concrete routes.
- Existing authority and repair boundaries are unchanged.

**Failure policy:** fix forward. Any need to make host behavior mandatory returns to design.

## PDP-300 — Protect ownership and regenerate projections

**Depends on:** `PDP-100`, `PDP-200`

**Execution:** serial, parent-owned generation slice

**Repository owner:** `market-csheng`

**Locks:** `skills-generated-projection`, `semantic-contract-tests`

**Authored write set:**

- `tests/test_skill_workflow_contracts.py`
- `tests/test_semantic_skill_contracts.py`
- an optional focused fixture under `tests/fixtures/delegation-profiles/` if the existing tests cannot express the example without prose snapshots

**Generated write set:**

- `skills/plan-change/`
- `skills/implement-change/`
- `skills.index.json`
- generated routing or trigger diagrams only when repository generation legitimately changes them

**Work:**

- Add a focused test that parses the semantic reference and proves exact approved enum values, required readiness facts, and `runtime_contract = false`.
- Protect public metadata ownership: `plan-change` remains `may_spawn_agent = false`; `implement-change` retains its current optional agent capability and explicit mutation authority.
- Protect provider neutrality structurally by rejecting forbidden runtime-binding keys in the reference and concrete model/provider terminology in the newly maintained semantic surfaces.
- If an example fixture is necessary, keep it explicitly non-normative and demonstrate one single-repository ready task plus two per-repository slices for a multi-repository milestone.
- Run repository-owned generators from authored sources. Never edit root-flat Skills or indexes manually.
- Inspect generated diffs to ensure only intended Skill projections changed.

**Verification:**

```bash
uv run pytest tests/test_skill_workflow_contracts.py tests/test_semantic_skill_contracts.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-skills-index.py
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
git diff --check
```

**Done when:**

- Tests fail for enum drift, runtime-contract ownership, or `plan-change` spawn authority drift.
- Generated `skills/plan-change/` includes the reference and both generated Skills match authored truth.
- Generated indexes are deterministic and no unrelated projection churn remains.

**Failure policy:** stop and diagnose unexpected generator churn. Do not repair generated files directly.

## PDP-400 — Synchronize stable truth, verify, and review

**Depends on:** `PDP-300`

**Execution:** serial, parent-owned

**Repository owner:** `market-csheng`

**Locks:** `stable-skill-composition-truth`, `implementation-review`

**Write set:**

- `docs/architecture/skill-composition.md`
- only another stable doc that is proven stale by the implemented behavior

**Work:**

- Document that plans may carry optional provider-neutral delegation profiles and single-repository readiness while all concrete binding, scheduling, process, and session mechanics remain host-owned.
- Keep concrete consumer repository and model names out of stable architecture truth.
- Run full repository verification from a cleanly generated tree.
- Perform one bounded implementation review against the approved design and this plan.
- Adjudicate all material findings in the implementing agent. Apply at most one focused in-scope repair and rerun affected plus full declared checks without a second review.

**Verification:**

```bash
bash scripts/check.sh
git diff --check
git status --short
```

**Done when:**

- Stable docs match implemented semantic ownership.
- Full checks pass after generation.
- No accepted implementation-review finding remains.
- The final diff contains only authored sources, intended generated projections, tests, stable truth, and these stage artifacts.

**Failure policy:** one focused fix-forward repair. Return `non-convergent` if it does not converge, and return `needs_design_decision` if review shows a runtime or adapter dependency.

## Cross-repository coordination

A compatible runtime repository may independently accept camelCase projections of the same semantic words, but this implementation does not read, import, test, write, release, or install that repository. No task here mutates `pi-extensions`, and no check depends on it being present.

The active parent agent remains the only semantic bridge. Interoperability evidence can be gathered after both independent implementations, but it is not a build or merge gate for this repository.

## Authority boundary

Plan approval validates the repository-local authored, generated, test, and documentation task order described above; it does not authorize execution. A separate implementation request is required. Neither artifact approval nor implementation authority by itself authorizes:

- mutation of `pi-extensions` or another repository;
- installation into Codex, Claude, Pi, or another user directory;
- external service calls or provider/model changes;
- commit, push, publication, or deployment;
- new lifecycle, review, scheduler, or runtime contracts.

## Review decision

A bounded plan review was required because the plan changes two workflow Skills, adds durable semantic vocabulary, and regenerates distribution surfaces. Review was limited to this plan, its exact approved design, current Skill ownership contracts, generation/check scripts, and stable composition truth.

Direct `review-plan` evaluation initially found one medium execution-oracle defect: `PDP-300` named a nonexistent `scripts/generate.sh` and left generator discovery to the implementing agent. The finding was accepted. The plan now names the three repository-owned generation commands exposed by current scripts and retains `bash scripts/check.sh` as the complete parity gate.

The focused repair resolved the finding. Re-evaluation returned `pass`; no scope, dependency, authority, oracle, generated-truth, or recovery finding remains.

## Approval and implementation outcome

`approval_status = approved`. The user explicitly approved all pending plan and implementation authority in the implementation request. Repository-local implementation completed with outcome `pass`.

Verification evidence:

- `bash scripts/check.sh`: 99 tests passed with contract, generated-surface, install-surface, index, diagram, Ruff, ty, and Markdown gates.
- Authored `plan-change` and `implement-change` semantics regenerated deterministically to root-flat Skills.
- The structured vocabulary remains `runtime_contract = false`, `plan-change` remains non-spawning, and no concrete provider/model route entered maintained Skill truth.

Bounded implementation review returned `pass`. The diff preserves provider neutrality, single-repository writable slices, active-parent convergence ownership, generated-source ownership, optional profile defaults, and existing implementation/review authority. No accepted finding or repair remains.

No commit, push, installation, publication, deployment, or mutation of another repository was performed.
