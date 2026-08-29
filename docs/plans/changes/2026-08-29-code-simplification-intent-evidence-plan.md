# Code Simplification Intent Evidence Implementation Plan

## Status

- plan_version: 1
- design_ref: `docs/plans/changes/2026-08-29-code-simplification-intent-evidence-design.md`
- design_sha256: `eb8a93cf9874b2d43e98e32a59b8a3651270bbb1d6e00a7da4d0ad561ca69e02`
- design_approval_status: approved
- approval_status: approved
- approval_basis: The user explicitly approved both repository designs, both implementation plans, and implementation using subagents where the repository boundary permits on 2026-08-29.
- decision_state: approved
- implementation_authority: granted
- implementation_status: non_convergent
- verification_status: passed
- truth_sync_status: completed
- implementation_review_status: non_convergent
- truth_sync_required: true
- implementation_review_required: true
- plan_review_required: true
- plan_review_status: passed_after_repair

## Milestone

Refine only the authored `code-simplification` audit semantics and candidate-evidence reference so non-consumption-based removal arguments distinguish concept responsibility from exact representation responsibility, ownership, and liveness. Regenerate the root-flat projection and prove that no review workflow, runtime contract, public ID, activation metadata, or unrelated Skill changes.

## Preconditions and authority

Satisfied:

- The user bounded the requested `agent-skills` work to recommendation #1: strengthen `code-simplification` intent evidence only.
- Authored Skill truth is under `src/skills/`; root-flat `skills/` is generated.
- The current disposition vocabulary and generated ownership contract are known.
- No account, credential, network service, license, hardware, or external repository prerequisite is required.

Execution prerequisites satisfied:

- The user approved the referenced design and this plan.
- The user separately authorized the bounded repository-local implementation.
- Repository mutation beyond these two stage artifacts requires a later explicit implementation request after design and plan approval.

Approval and implementation do not authorize commit, push, installation, publication, deployment, or mutation of `pi-extensions` or another repository.

## Frozen design decisions

- The new gate applies when a candidate's removal argument depends materially on low or absent consumption; it is not a universal mandatory template for every simplification candidate.
- The gate distinguishes concept responsibility and owner from exact representation responsibility and owner.
- Non-consumption is classified as confirmed redundancy, incomplete wiring, retained compatibility or migration intent, or unresolved evidence.
- Decisive evidence that removal erases an owned exact requirement yields `reject`; uncertainty about exact representation requirement, ownership, or canonical status yields `defer-for-evidence`.
- Historical or speculative intent is evidence to reconcile, not automatic retention authority.
- Grouped items must share concept owner, representation owner and responsibility, consumers, compatibility risk, decisive oracle, and disposition.
- Existing dispositions, read-only authority, design handoff, frontmatter description, public ID, routing, and activation remain unchanged.
- No machine-readable candidate schema, validator, ledger, scanner, or prose snapshot test is introduced.

## Oracle strategy

The protected boundary is human-authored semantic guidance distributed through an exact generated projection.

Use:

- bounded source review for semantic completeness and non-expansion;
- authored-to-generated exact parity as the distribution oracle;
- existing contract, install-surface, Markdown, lint, and type gates;
- one bounded implementation review over the exact diff.

Do not add exact-sentence, heading, keyword-presence, or keyword-absence tests for the Markdown. No new automated test is expected unless implementation unexpectedly introduces a machine-readable structural source, which would require `needs_design_decision` under the approved design.

## Acceptance trace

| Acceptance ID | Requirement | Implementation owner | Oracle |
| --- | --- | --- | --- |
| CSI-A1 | Non-consumption-based candidates distinguish concept from exact representation | `CSI-100` | Complete authored diff review |
| CSI-A2 | Exact representation owner and requirement are explicit | `CSI-100` | Candidate-evidence matrix and record review |
| CSI-A3 | Redundancy, incomplete wiring, compatibility intent, and unresolved evidence select the existing dispositions consistently | `CSI-100` | Four bounded review scenarios in this plan, reinspected after any repair |
| CSI-A4 | Heterogeneous bundled candidates must split | `CSI-100` | Authored Skill and reference review |
| CSI-A5 | No other Skill, public metadata, runtime, or workflow contract changes | `CSI-200` | Diff allowlist plus repository checks |
| CSI-A6 | Generated root-flat copy exactly matches authored truth | `CSI-200` | Repository generators and `bash scripts/check.sh` |
| CSI-A7 | No material implementation-review finding remains | `CSI-300` | One bounded `review-implementation` evaluation and adjudication |

## Task graph

```text
CSI-100 authored intent evidence
    |
CSI-200 generated projection and repository verification
    |
CSI-300 bounded implementation review and convergence
```

The work is intentionally serial. The two authored files express one semantic rule and should be edited together. Generation has one owner, and review starts only after authored and generated surfaces converge.

## CSI-100 — Implement concept-versus-representation intent evidence

**Depends on:** approved design and plan

**Execution:** serial, repository-local

**Repository owner:** `agent-skills`

**Locks:** `code-simplification-authored-semantics`

**Write set:**

- `src/skills/disciplines/code-simplification/SKILL.md`
- `src/skills/disciplines/code-simplification/references/candidate-evidence.md`

**Work:**

- Add a concise mandatory evidence step for candidates materially justified by low or absent consumption.
- Require the auditor to name the broader concept responsibility and owner separately from the exact representation responsibility and its authored, generated, schema, public, persisted, migration, or compatibility owner.
- Require evidence that approved current truth needs the exact representation, only the broader concept, or neither.
- Require an explicit liveness interpretation: confirmed redundancy, incomplete wiring, retained compatibility or migration intent, or unresolved evidence.
- Clarify disposition selection without adding dispositions:
  - confirmed redundant representation may proceed to `recommend-design` only after retained behavior and compatibility evidence;
  - an exact owned requirement that deletion would erase yields `reject`;
  - unresolved exact requirement, owner, canonical representation, or external compatibility evidence yields `defer-for-evidence`;
  - no bounded safe reduction remains `no-safe-cut`.
- State that historical plans, names, or useful surrounding concepts do not automatically require an exact representation, while absence of first-party callers does not defeat external or persisted compatibility.
- Require candidate splitting when grouped items do not share both ownership levels, representation role, consumers, compatibility risk, decisive oracle, and disposition.
- Extend the evidence matrix and compact candidate record with these facts while preserving concise output and avoiding a universal template for candidates not based on non-consumption.
- Preserve read-only authority, scope boundaries, trust and durability safeguards, handoff to `design-change`, existing output order, and all current disposition names.
- Do not change Skill frontmatter, provider metadata, activation, routing, dependencies, or another Skill.

**Focused inspection:**

```bash
python3 - <<'PY'
from pathlib import Path
paths = [
    Path('src/skills/disciplines/code-simplification/SKILL.md'),
    Path('src/skills/disciplines/code-simplification/references/candidate-evidence.md'),
]
for path in paths:
    assert path.is_file(), path
    assert path.read_text(encoding='utf-8').strip(), path
PY
git diff --check -- src/skills/disciplines/code-simplification
```

The script checks file integrity only. Semantic acceptance comes from complete diff review rather than keyword assertions.

**Done when:**

- `CSI-A1` through `CSI-A4` are visibly satisfied in authored truth.
- A representation of a retained concept can be removed without implying removal of that concept when evidence is decisive.
- A required but unconsumed exact representation cannot be misreported as safe deletion.
- The Skill still performs a simplification audit rather than diagnosing or repairing implementation incompleteness.

**Failure policy:** fix forward within the two authored files. Stop with `needs_design_decision` if implementation requires a new disposition, cross-workflow contract, structured schema, or mandatory artifact.

## CSI-200 — Regenerate distribution surfaces and verify scope

**Depends on:** `CSI-100`

**Execution:** serial, parent-owned generation

**Repository owner:** `agent-skills`

**Locks:** `skills-root-flat-generation`, `repository-validation`

**Authored write set:** none beyond changes already made by `CSI-100`

**Expected generated write set:**

- `skills/code-simplification/SKILL.md`
- `skills/code-simplification/references/candidate-evidence.md`

**Expected unchanged generated and contract surfaces:**

- `skills/code-simplification/agents/openai.yaml`
- `skills/.source-map.json`
- `skills.index.json`
- generated diagrams
- `contracts/skills.toml`

**Work:**

- Run every repository-required generator from authored truth in the required order.
- Confirm only the two root-flat Markdown projections change.
- Inspect the full diff for accidental prose normalization, unrelated Skill churn, frontmatter changes, routing changes, index changes, or generated ownership violations.
- Run complete repository validation.

**Verification:**

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
git diff --check
git status --short
```

**Done when:**

- `CSI-A5` and `CSI-A6` pass.
- Authored and root-flat files are byte-for-byte convergent under repository generators.
- No generated file is hand-edited and no unexpected index, diagram, source-map, provider metadata, contract, or unrelated Skill diff remains.
- Full repository checks pass without adding a prose snapshot test.

**Failure policy:** stop and diagnose generator or validation drift. Repair only the authored Skill truth when causally required and regenerate its projections; never patch generated projections directly. Any script, generator, contract, index, provider-metadata, or unrelated source modification requires `needs_plan_change`.

## CSI-300 — Review the exact implementation and converge

**Depends on:** `CSI-200`

**Execution:** serial, parent-owned

**Repository owner:** `agent-skills`

**Locks:** `code-simplification-implementation-review`

**Write set:**

- no planned new file;
- one focused repair may touch only the `CSI-100` authored files and their `CSI-200` generated projections.

**Review brief:**

- objective: strengthen only non-consumption-based concept-versus-representation evidence;
- exact design and this approved plan;
- exact authored and generated diff;
- `bash scripts/check.sh` and generator evidence;
- current generated ownership rules as supporting truth.

**Bounded semantic scenarios:**

- A useful retained concept has an extra unconsumed representation with no exact contract or compatibility owner: the representation may reach `recommend-design` without claiming the concept is removable.
- An exact field is named by current truth as the canonical policy source but has no runtime enforcer: deletion is `reject`, and the audit does not design the missing wiring.
- An old plan or suggestive name implies intent, but current exact ownership and compatibility status cannot be established: the candidate is `defer-for-evidence`, not automatic retention or deletion.
- One “unused metadata” group contains items with different owners, consumers, oracles, or dispositions: the candidate must split.

**Review questions:**

- Does the implementation produce the intended outcome for all four bounded scenarios without encoding them as prose tests?
- Does the implementation prevent both unsafe removal and concept-level overprotection?
- Are concept owner and exact representation owner distinct and useful?
- Are `reject` and `defer-for-evidence` selected by evidence rather than repair speculation?
- Is substitute compatibility evidence allowed without false proof claims?
- Does candidate splitting stay bounded and avoid a mandatory report template?
- Did any review, design, planning, implementation, activation, routing, or runtime authority move?

After any accepted repair, re-read the complete two authored files against all four scenarios before regenerating and rerunning structural checks.

**Verification after review:**

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
git diff --check
```

**Done when:**

- One bounded implementation review completes.
- The implementing agent adjudicates every material candidate.
- At most one focused in-scope repair is applied and all affected plus full checks pass.
- `CSI-A7` passes and no accepted material finding remains.

**Failure policy:** return `non-convergent` if the one focused repair does not converge. Return `needs_design_decision` for a requested new disposition, workflow handoff, validator, or broader Skill change.

## Work-package readiness

- milestone objective: one bounded semantic refinement to `code-simplification`.
- non-goals: all other Skills, runtime mechanics, scanners, schemas, validators, application of simplifications, and external mutation.
- oracle strategy: human semantic review plus generated parity and repository checks.
- review budget: one implementation review and at most one focused repair.
- failure policy: fix forward within the exact authored/generated surface or stop with a typed design decision.
- subagent execution: one bounded worker and reviewer were used within the repository boundary; generation and final verification remained parent-owned.
- parallel policy: serial because authored semantics and generated convergence share one owner.
- prerequisites: design approval, plan approval, and the separate implementation request were satisfied on 2026-08-29.

## Truth-sync handoff

Truth synchronization is limited to regenerating the two tracked root-flat projections from authored source. No stable architecture, README, AGENTS, contract, index, routing, or provider metadata update is expected.

If implementation evidence shows one of those surfaces is genuinely affected, stop with `needs_plan_change` rather than adding it opportunistically.

## Authority boundary

The separate explicit implementation request authorized only the listed authored/generated files and deterministic verification. It did not authorize commit, push, installation, publication, deployment, mutation of another repository, or application of any simplification candidate.

## Review decision

A bounded independent plan review was required because the plan changes public semantic guidance and generated distribution surfaces. Review was limited to this plan, its exact design, current authored Skill files, generated ownership policy, repository generators, and declared checks.

The first evaluation returned four causally bound candidates. One focused repair prohibited generator/script scope expansion, added four bounded semantic review scenarios and mandatory post-repair semantic reinspection, clarified that plan approval freezes scope but does not authorize mutation, and removed an undeclared supporting Skill from the implementation-review brief.

Re-evaluation found no remaining material scope, dependency, oracle, authority, recovery, review-budget, or generated-ownership issue. `plan_review_status = passed_after_repair`.

## Implementation outcome

The authored Skill and candidate-evidence reference now separate concept responsibility and ownership from exact-representation responsibility and ownership, require an explicit liveness classification when non-consumption is material, preserve the four existing dispositions, and split candidates that differ in ownership, consumers, compatibility, decisive oracle, or disposition. The two root-flat projections were regenerated from authored truth.

All required generators, `bash scripts/check.sh`, 101 tests, Markdown checks, authored/generated parity, and `git diff --check` pass. No other Skill, contract, index, diagram, provider metadata, or simplification candidate changed.

The first bounded implementation review accepted and repaired one candidate-splitting issue concerning different decisive oracles. A later bounded re-evaluation found two remaining design-trace gaps: separate concept/representation responsibilities and the explicit four-way liveness classification. Both were repaired in the same authorized authored/generated surfaces and all checks pass, but that was a second focused repair after the plan's one-repair budget. Under `CSI-300`'s frozen failure policy, `implementation_status = non_convergent` even though the current repository content satisfies the approved semantic acceptance criteria. No further mutation is implied.

## Approval

`approval_status = approved`. The user explicitly approved the design, this plan, and repository-local implementation on 2026-08-29. Commit, push, installation, publication, deployment, applying simplification candidates, and mutation of another repository remain unauthorized.
