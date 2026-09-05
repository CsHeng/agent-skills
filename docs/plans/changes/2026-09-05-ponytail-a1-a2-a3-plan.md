# Selective Ponytail Adoption Implementation Plan: A1, A2, A3

## Status and authorization

- Design: [A1, A2, A3 design](2026-09-05-ponytail-a1-a2-a3-design.md).
- Plan state: `ready_for_approval`.
- Scope basis: the user selected A1, A2, and A3 and explicitly requested design and planning. The detailed design and plan are pending user approval; implementation is not authorized.
- Milestone: refine capability search in `development-standards`, caller-aware bug-fix inspection in `implement-change`, and optional agent Skill evaluation guidance in `testing-strategy`, preserving the 39-Skill semantic-only distribution.
- Independent plan review: required for write-set coherence, factual task dependencies, substitute-versus-runtime evidence, and external-execution authority. Budget: one read-only evaluation and at most one focused in-scope repair.
- Plan review status: `pass`. The independent read-only plan evaluation returned no candidate findings; the parent checked its task, write-set, oracle, and authority conclusions against the approved planning scope and accepted the verdict. No repair was required.
- Implementation status: not started.

## Confirmation and prerequisites

| ID | Clearance | Status |
| --- | --- | --- |
| C1 | A1-A3 are the selected scope, with no Ponytail hooks, new public Skills, or runtime framework | Established by the user request and companion design |
| C2 | Approve the detailed design and plan and authorize the listed repository-local implementation | Pending user decision; no source or generated mutation before clearance |
| C3 | Public IDs, authored owners, generated projection, verification commands, and stage-doc boundary are known | Verified against current repository truth at `bdf4e9c` |
| C4 | Live model evaluation, external credentials, installation, publication, or consumer settings changes are needed for this milestone | No; these actions are explicitly excluded |

There is no known account, login, license, paid-service, hardware, or external-repository prerequisite. Before implementation, re-read the approved pair and `git status --short`; preserve these uncommitted planning artifacts and any newer user changes. Confirm that Python 3 and the repository-owned `uv` toolchain can run the existing checks. An unavailable toolchain is a reported verification blocker, not permission to install or change the environment silently.

Approval of this plan does not authorize commit, push, installation, release, destructive history changes, external data transmission, or modification of another repository. Do not run Ponytail, clone additional benchmark fixtures, call an external model for an efficacy trial, or change globally installed instructions to complete this milestone.

## Frozen decisions and non-goals

- A1 is a candidate-search heuristic subject to approved contracts, repository conventions, deployment fit, trust, and lifecycle cost, not a fixed solution ranking or a shortest-code mandate.
- A2 applies to relevant shared-behavior bug fixes. Shared invariants may justify shared fixes; differing caller contracts and unresolved public/dynamic consumers must not be erased by simplification.
- A3 is one optional provider-neutral reference linked from the existing testing Skill, not an executable benchmark, required lifecycle gate, result schema, new fixture corpus, or measured-improvement claim.
- Keep frontmatter, public IDs, routing, roles, permissions, `semantic_requires`, generators, tests, plugin manifests, installers, hook code, architecture docs, and other Skills unchanged.
- Preserve existing library-selection exceptions, scope guards, error handling, oracle integrity, environment isolation, and conditional review rules.
- Future live evaluations or new tools require a separately bounded package; they are not deferred acceptance work for this plan.

## Oracle strategy and acceptance trace

The protected boundary is authored semantic guidance plus its portable generated distribution. The implementing agent owns acceptance, diagnosis, review adjudication, and repair.

| ID | Acceptance condition | Task owner | Evidence |
| --- | --- | --- | --- |
| AC1 | A1 makes capability search explicit without overriding contracts, established dependencies, or security-sensitive library choices | T100 | Complete source diff review using design scenarios S1-S2 |
| AC2 | A2 distinguishes shared root causes from caller-specific behavior and unresolved consumer evidence without expanding scope | T110 | Complete source diff review using S3-S4 and existing reproducer/authority rules |
| AC3 | A3 covers comparator selection, contamination, activation evidence, independent acceptance, bounded repeat accounting, claims, and authority | T120 | Read the entire new reference and its conditional link against S5-S8 |
| AC4 | No new capability, metadata, host integration, automatic evaluation, or unrelated write is introduced | T200 | Worktree/allowlist inspection and existing structural contracts |
| AC5 | All four generated counterparts match authored truth, the new reference resolves locally, and the 39 public IDs and other projections stay unchanged | T200 | Repository generators, root-flat parity and reference checks, and final diff inspection |
| AC6 | Required maintenance checks pass and no accepted material implementation-review finding remains | T200, T300, T310 | Command outcomes, reviewer candidates, parent adjudication, and any repair recheck |
| AC7 | Closeout distinguishes maintenance verification from unmeasured behavior or economic benefits | T400 | Evidence-backed final response; no live-efficacy claim |

Use S1-S8 from the companion design as a bounded semantic review matrix. Their expected decisions are not sentence snapshots, keyword assertions, automated agent tests, or statistical evidence. Existing executable checks prove inventory, parseability, reference closure, portability, generated parity, and repository health; they do not prove that an agent follows the prose.

Do not add tests over policy sentences or weaken any existing oracle. If implementation unexpectedly needs a machine-readable contract, new test framework, executable fixture, or runtime evaluation, stop for a design/scope decision instead of changing this plan implicitly.

## Allowed implementation writes

Authored writes:

- `src/skills/policies/development-standards/SKILL.md`
- `src/skills/workflows/implement-change/SKILL.md`
- `src/skills/disciplines/testing-strategy/SKILL.md`
- `src/skills/disciplines/testing-strategy/references/agent-skill-evaluation.md` (new)

Generated-only content changes:

- `skills/development-standards/SKILL.md`
- `skills/implement-change/SKILL.md`
- `skills/testing-strategy/SKILL.md`
- `skills/testing-strategy/references/agent-skill-evaluation.md` (new)

The standard generators may rewrite their owned output while producing no content difference outside those four generated files. In particular, expect no changes to `skills.index.json`, `skills/.source-map.json`, projected metadata, or architecture diagrams. Diagnose unexpected changes and retain unrelated work; do not hand-edit projections or accept a broader diff automatically.

The two current design/plan documents are stage artifacts created by the present request, not implementation outputs. No further plan-state ledger, completion file, or stable-doc migration is required; report implementation evidence in the final response unless the user requests a durable execution record.

## Tasks and factual dependencies

### T100: A1 capability-search guidance

- Predecessor: C2 implementation clearance. No dependency on T110 or T120.
- Read: approved design A1, `development-standards` in full, and directly relevant existing policy as needed to avoid contradictions.
- Write: `src/skills/policies/development-standards/SKILL.md` only.
- Change: refine Dependency Selection with the bounded search order, its prerequisite of understanding the requirement/current code, and its contract-aware stopping rule. Preserve existing lifecycle-cost comparison and maintained-library exceptions. Do not add the ladder elsewhere.
- Completion: AC1 holds for S1-S2; the frontmatter and unrelated policy remain unchanged; no new universal dependency or activation requirement appears.
- Verification: inspect the exact authored diff and read the resulting Dependency Selection together with Scoped Implementation and Compatibility And Migration. Record S1-S2 outcomes as semantic review evidence, not executed-agent behavior.
- Failure policy: fix wording in the same file; a requirement to alter another policy owner returns `needs_design_decision`.

### T110: A2 caller-aware fix inspection

- Predecessor: C2 implementation clearance. No dependency on T100 or T120.
- Read: approved design A2, `implement-change` in full, and its current reproducer, scope, and outcome rules.
- Write: `src/skills/workflows/implement-change/SKILL.md` only.
- Change: refine the initial inspection and, only as necessary, the adjacent verification guidance to inspect relevant caller contracts, identify the owning invariant, distinguish shared from caller-specific fixes, and select affected-path regression evidence. Retain bounded search, explicit uncertainty, and existing authority/outcome semantics.
- Completion: AC2 holds for S3-S4; no blanket repository scan, one-test-per-caller quota, automatic simplification audit, new lifecycle gate, or new outcome is introduced.
- Verification: inspect the exact authored diff and read the resulting steps with Preconditions, Review Adjudication, and Outcomes. Record S3-S4 outcomes as semantic evidence.
- Failure policy: fix within the authored workflow file; a broader product or authority change returns `needs_design_decision` or `needs-authority` as applicable.

### T120: A3 optional evaluation reference

- Predecessor: C2 implementation clearance. No dependency on T100 or T110; the approved A3 design supplies its complete boundary.
- Read: approved design A3, `testing-strategy` in full, and its existing documentation-verification, oracle-integrity, and environment-isolation policies.
- Write: `src/skills/disciplines/testing-strategy/SKILL.md` and `src/skills/disciplines/testing-strategy/references/agent-skill-evaluation.md` only.
- Change: add the focused reference described by A3 and a conditional relative link from Documentation And Markdown Verification. Keep the method provider-neutral, self-contained, optional, and independent of stage artifacts or an external Ponytail installation.
- Completion: AC3 holds for S5-S8; current-bundle versus candidate comparison is primary for incremental changes; contamination/uncertainty, independent quality requirements, failed-attempt accounting, budget, data exposure, and authority are explicit. No efficacy claim or requirement to run a model follows from editing a Skill.
- Verification: read the complete reference and follow its local link; inspect the diff for unintended frontmatter, dependency, runtime, vendor-command, or evaluation-runner changes. Record S5-S8 outcomes as semantic evidence.
- Failure policy: fix reference/link prose within the same two authored files; executable evaluation or a structured evidence contract returns `needs_design_decision` and requires new authority.

### T200: parent-owned integration, regeneration, and verification

- Predecessors: the completed authored outputs from T100, T110, and T120. All three are required because the distribution generator reads the complete authored Skill tree and the integration review checks their combined semantics.
- Owner: active implementing agent; this synthesis, verification, and continuation decision is not delegated.
- Write: only the four generated counterparts listed above, through repository-owned generators.
- Integration: re-read the three changed Skill sections together. Ensure A1's selection bias does not override A2's caller contracts and A3 measures acceptance rather than rewarding code omission. Inspect every changed path, frontmatter field, and new reference against the allowlist.
- Run from the repository root, in this order:

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
git diff --check
git diff --name-status
git status --short
```

- Evidence: preserve command outcomes and relevant failures, inspect both tracked changes and untracked new reference files, confirm exact authored/generated parity and reference closure, and confirm that the index, diagrams, metadata, public IDs, and other Skills have no task-caused content change. New generated files do not appear in ordinary `git diff` until tracked, so the status/untracked inspection is required.
- Completion: AC4-AC5 and the maintenance-check portion of AC6 pass without changing tests or weakening verification.
- Failure policy: diagnose and fix the owning authored source, regenerate, and rerun the affected plus declared gates. Unrelated/pre-existing failures remain explicit blockers or separately reported limitations, not silent scope expansion or a false pass.

### T300: one bounded implementation review

- Predecessor: T200's integrated exact diff, S1-S8 semantic evidence, and verification outcomes. The reviewer needs this converged target, not incomplete individual slices.
- Owner: one read-only `review-change` evaluation, optionally using `review-implementation`; the parent supplies the approved pair, exact authored/generated changes, accepted non-goals, and current evidence.
- Write: none.
- Focus: unauthorized scope reduction or expansion, unsafe capability substitution, conflated caller contracts, accidental mandatory evaluation or host integration, missing evidence/authority constraints, and distribution parity. Review excludes unrelated existing debt.
- Budget: one implementation evaluation for the converged milestone. It is justified by the specific semantic risks in this plan, not a new universal review rule.
- Completion: candidate findings and one bounded verdict are returned to the parent. Review success does not authorize implementation, installation, or publication.

### T310: parent adjudication and bounded repair

- Predecessor: T300's candidate findings; adjudication is a parent-owned decision, not a hard predecessor between worker tasks.
- Write: only the four authored and four generated paths already authorized, and only for accepted causally related findings.
- Action: adjudicate every material candidate. If none is accepted, make no repair. Otherwise apply at most one focused same-slice repair, regenerate affected projections, rerun S1-S8 as relevant and the full T200 checks, and inspect the final allowlist. Do not request a second review or start an unbounded repair loop.
- Completion: no accepted in-scope finding remains and the declared verification passes. A failure to converge is reported as `non-convergent`; new scope or a changed design requires an explicit decision.

### T400: parent-owned truth check and closeout

- Predecessor: T310's disposition and final verification evidence, or T300 adjudication with no accepted repair.
- Write: none required.
- Action: confirm that authored Skills and their generated projections contain the durable guidance and that architecture, discovery, routing, and installation boundaries remain unchanged. Do not promote stage history into stable architecture truth.
- Evidence: report changed files, check outcomes, S1-S8 semantic review, implementation-review verdict/adjudication, repair status, and any blocker. Explicitly state that live behavioral/economic efficacy was not evaluated.
- Completion: AC6-AC7 hold. No commit, push, install, publication, or consumer-state mutation is implied.

## Execution ranges and delegation policy

- E1: after C2, T100, T110, and T120 are independent authored slices. Their displayed order is not a dependency. The active implementing agent can perform these small prose edits in any order; shared motivation does not justify serial predecessor edges.
- E2: T200 joins the actual authored outputs, performs parent-owned integration, generates the shared distribution once, and verifies the combined change.
- E3: T300 receives the converged target; T310 and T400 retain adjudication, repair, continuation, and the final response in the parent.

Delegated implementation was not requested. This plan does not claim delegation-ready worker packages (`subagent_ready: false`); execution and reasoning profiles are therefore not assigned. The default is parent-retained editing, not a required concurrency capability. Any later authorized delegation must freeze one repository owner (`agent-skills`), exact disjoint authored write sets, resource/isolation boundaries, verification and convergence ownership, and any requested semantic profiles before assigning workers. Workers must not regenerate the shared `skills/` tree or change settings. Ordinary independent slices use a flat batch, and lack of delegation capacity leaves execution in the parent rather than changing scope.

T200, T310, T400, review adjudication, and authority decisions are never delegated. The dependencies above describe factual artifacts and decisions; they do not prescribe a host task graph, worktree layout, actor binding, replay record, or task ledger.

## Recovery and stop conditions

| ID | Trigger | Required response |
| --- | --- | --- |
| X1 | An authored rule, local reference, or generated counterpart is wrong within the approved eight-file surface | `fix_forward` in the authored owner, regenerate, and rerun the affected plus declared checks |
| X2 | Implementation requires changing contracts, public IDs, other Skills, tests, generators, hooks, architecture ownership, or adding a benchmark runtime | Stop with `needs_design_decision` or `replan`; do not silently extend the allowlist |
| X3 | Verification depends on unavailable tools, credentials, network access, or external authority | Preserve evidence and report the blocker; no unapproved installation, settings mutation, or substitute success claim |
| X4 | Regeneration changes unrelated output, or the worktree contains conflicting user edits | Diagnose ownership and preserve unrelated changes; stop for clarification where separation is unsafe |
| X5 | Accepted findings remain after the one focused implementation repair | Report `non-convergent` without another review/repair cycle or implicit redesign |
| X6 | Someone asks to claim saved lines/tokens, improved safety, or faster work without a controlled trial | Report the evidence limit; a real evaluation is separately scoped and authorized |

No destructive cleanup, history rewrite, or guarded rollback is justified. If no in-scope forward repair is safe, stop and preserve the current evidence.

## Planning verification and approval record

This section records checks of the design/plan artifacts, not execution of T100-T400.

- Design/plan artifact verification: `bash scripts/check.sh` passed, including contracts, root-flat/install/index/diagram checks, Ruff, ty, all 98 tests, and Markdown normalization checks. The parent confirmed that only the two stage artifacts were added and their reciprocal local links resolve. These are maintenance checks of current repository state, not evidence that T100-T400 or an agent efficacy trial ran.
- Independent design review and parent adjudication: `pass`, no material candidates and no repair; recorded in the companion design.
- Independent plan review and parent adjudication: `pass`, no candidates and no repair. The two evaluations were independent and read-only; approval remains with the user.
- Approval status: pending user approval of the resulting pair.
- Implementation authority: not granted; source and generated files remain unchanged by this planning task.
