# Code Simplification Intent Evidence Design

## Status

- design_version: 1
- change_class: B
- design_depth: design-lite
- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this design, its implementation plan, and repository-local implementation on 2026-08-29.
- decision_state: approved
- truth_impact: medium
- truth_sync_required: true
- review_required: true
- review_status: passed_after_repair
- recommended_next_phase: implement the approved plan

## Objective

Strengthen `code-simplification` so an audit whose removal argument depends materially on low or absent consumption distinguishes an owned concept from the exact representation proposed for removal. An unconsumed field, helper, object member, or projection must not be treated as deletion proof when current evidence cannot distinguish redundant representation from incomplete wiring or retained compatibility intent.

The change remains a read-only audit-semantic refinement. It does not turn `code-simplification` into a correctness reviewer, design workflow, implementation workflow, or repository-wide dead-code scanner.

## Current truth and problem

`src/skills/disciplines/code-simplification/SKILL.md` already requires behavior mapping, consumer evidence, rationale, history, compatibility analysis, trust-boundary preservation, and one of four dispositions: `recommend-design`, `reject`, `defer-for-evidence`, or `no-safe-cut`.

`src/skills/disciplines/code-simplification/references/candidate-evidence.md` already requires identity, ownership, responsibility, consumers, compatibility, rationale, history, deletion proof, net reduction, and a decisive oracle. It correctly says that few callers or passing unit tests do not prove a surface safe to remove.

The remaining gap is field-level intent classification. Current guidance does not force an auditor to state whether a proposed cut removes:

- an owned semantic concept or behavior;
- one representation of a concept that remains owned elsewhere; or
- repetitive syntax that still directly implements retained behavior.

It also does not force an explicit interpretation of non-consumption. An unconsumed representation can mean confirmed redundancy, implementation incompleteness, retained compatibility, generated ownership, reserved but currently approved intent, or unresolved evidence. Without that distinction, an audit can first overstate safe removal and later overcorrect by treating every representation of a useful concept as necessary.

## Selected boundary

Add a mandatory concept-and-representation evidence gate to the authored `code-simplification` Skill and its candidate-evidence reference.

For each candidate whose removal argument depends materially on low or absent consumption, the audit must establish:

1. **Concept responsibility**: the behavior, policy, compatibility promise, persisted meaning, or operational responsibility associated with the candidate, and its current owner if one exists.
2. **Representation responsibility and owner**: what the exact field, helper, member, adapter, projection, or syntax contributes independently of the broader concept, and which authored, generated, schema, public, persisted, migration, or compatibility authority owns that exact representation.
3. **Representation requirement**: whether approved current truth requires that exact representation, merely requires the broader concept, or provides no current requirement.
4. **Liveness interpretation**: whether the absence of a consumer is confirmed redundancy, evidence of incomplete wiring, retained compatibility or migration intent, or unresolved.
5. **Candidate granularity**: whether every item grouped in the candidate has the same concept owner, representation owner and role, consumer evidence, decisive oracle, and disposition.

The gate refines evidence and disposition selection. It does not add a new workflow state or a new public disposition vocabulary.

## Decision rules

### Confirmed redundant representation

A representation may proceed to `recommend-design` only when evidence shows that:

- the broader concept remains correctly implemented or owned without the representation;
- no approved current contract requires the exact representation;
- production, test, generated, dynamic, public, persisted, migration, and compatibility consumers have been checked as applicable;
- deletion does not conceal an implementation defect or remove required observability, recovery, validation, security, or audit behavior; and
- executable or substitute evidence supports both retained concept behavior and the compatibility conclusion at the declared confidence; unresolved external or persisted compatibility evidence requires `defer-for-evidence`.

A concept-level requirement does not protect every implementation field. For example, a routing concept may remain valid while an unused model object returned alongside the consumed route strings is redundant.

### Evidence of incomplete wiring

When approved current truth requires the exact representation or names it as the canonical policy source, but implementation has no consumer or enforcer, the item is not a behavior-preserving simplification candidate. The audit must not recommend deletion merely to make current code internally consistent.

Use `reject` when evidence positively shows that removal would erase an owned requirement. Use `defer-for-evidence` only when evidence cannot establish whether the exact representation is required, who owns it, or which representation is canonical. The audit may name that unresolved ownership or requirement question but must not investigate or prescribe a design repair.

### Historical or speculative intent

Historical presence, an old plan, a suggestive field name, or a useful surrounding concept does not by itself make the exact representation required. The auditor must reconcile historical rationale with current stable truth, consumers, compatibility policy, and current ownership.

Speculative future utility does not block a safe cut. Conversely, lack of first-party callers does not defeat an external or persisted compatibility commitment.

### Candidate splitting

A candidate must be split when grouped fields or helpers have different concept owners, different representation responsibilities, different consumers, different compatibility risk, different decisive oracles, or different dispositions. Shared location or a shared motivation such as “unused metadata” is insufficient reason to bundle them.

## Output contract refinement

The existing compact candidate record remains authoritative. For candidates materially based on non-consumption, the record must make these facts easy to find:

- concept responsibility and owner;
- exact representation responsibility and its authored, generated, schema, public, persisted, migration, or compatibility owner;
- evidence that the exact representation is required, redundant, or unresolved;
- interpretation of absent consumption;
- evidence that every grouped item shares one decisive oracle and disposition.

These facts may be rendered as short fields or prose. No machine-readable candidate schema, validator, ledger, or mandatory artifact format is introduced.

## Scope

In scope:

- authored semantic guidance in `src/skills/disciplines/code-simplification/SKILL.md`;
- the detailed evidence matrix and candidate record in `src/skills/disciplines/code-simplification/references/candidate-evidence.md`;
- generated root-flat projections of those authored files;
- repository-owned generation and validation.

Out of scope:

- changes to `review-change`, `review-design`, `review-plan`, `review-implementation`, `design-change`, `plan-change`, `implement-change`, or `testing-strategy`;
- a generic dead-code detector, linter, AST scanner, or repository-wide audit command;
- a new disposition, workflow state, runtime contract, artifact validator, mutable ledger, or lifecycle gate;
- changes to Skill activation, routing, frontmatter descriptions, public IDs, contracts, indexes, or provider metadata;
- applying any simplification candidate to `pi-extensions` or another repository;
- commit, push, installation, publication, or deployment.

## Stable and generated truth

Authored truth remains under `src/skills/`. The exact generated projections remain under `skills/` and must be regenerated rather than edited by hand.

This change refines one Skill's maintained semantic contract but does not change repository architecture, installation topology, Skill composition, or public discovery. No stable `docs/architecture/` update is required. This design and its implementation plan remain stage artifacts under `docs/plans/changes/`.

## Oracle strategy

The protected boundary is semantic audit guidance. Human-authored instruction prose is verified through bounded review, generated-source parity, Markdown checks, and repository checks rather than exact-sentence or keyword tests.

No new prose snapshot or keyword-presence test should be added. A test is warranted only if implementation introduces a new machine-readable structural source, which this design does not require.

Acceptance evidence:

- The authored Skill explicitly distinguishes concept responsibility from exact representation responsibility and ownership before recommending removal based on non-consumption.
- The reference requires an explicit liveness interpretation and prevents unresolved incomplete-wiring evidence from becoming a deletion recommendation.
- Candidate splitting is required when bundled items do not share ownership, consumer evidence, oracle, and disposition.
- Existing four dispositions, read-only authority, audit scope, compatibility safeguards, and design handoff remain unchanged.
- Root-flat generated copies exactly match authored truth.
- No unrelated Skill, contract, route, index, provider metadata, or architecture document changes.
- Repository generation commands, `bash scripts/check.sh`, and `git diff --check` pass.

## Recovery

Use fix-forward recovery within the two authored Skill files and their generated projections. If the new gate causes broad mandatory templates, machine validation, lifecycle coupling, or systematic deferral of candidates with decisive evidence, narrow the prose while preserving the concept-versus-representation distinction.

If implementation demonstrates that a new disposition or cross-workflow handoff contract is necessary, stop with `needs_design_decision` rather than expanding this design.

## Implementation surface

Expected authored files:

- `src/skills/disciplines/code-simplification/SKILL.md`
- `src/skills/disciplines/code-simplification/references/candidate-evidence.md`

Expected generated files:

- `skills/code-simplification/SKILL.md`
- `skills/code-simplification/references/candidate-evidence.md`

No change is expected in `contracts/skills.toml`, `skills.index.json`, generated diagrams, `agents/openai.yaml`, or another Skill.

## Review decision

A bounded review is required because this change alters when a public audit Skill may recommend deletion or defer for evidence. Review must stay limited to this artifact, the two current authored Skill files, their generated ownership contract, and the originating code-simplification stage history needed to verify semantic continuity.

Independent `review-design` evaluation initially returned five causally bound candidates. The design objective and mandatory gate were aligned explicitly to non-consumption-based candidates; exact representation ownership was added; incomplete-wiring disposition was separated from repair choice; compatibility proof was corrected to allow decisive substitute evidence without false certainty; and generated projection synchronization is now explicit.

The focused repair preserves the requested narrow scope and existing disposition vocabulary while preventing both unsafe removal and concept-level overprotection. Re-evaluation found no remaining material scope, ownership, evidence, compatibility, oracle, generated-truth, or workflow-boundary issue. `review_status = passed_after_repair`.

## Approval

`approval_status = approved`. The user explicitly approved this design, its implementation plan, and repository-local implementation on 2026-08-29. Commit, push, installation, publication, deployment, application of simplification candidates, and mutation of another repository remain separately unauthorized.
