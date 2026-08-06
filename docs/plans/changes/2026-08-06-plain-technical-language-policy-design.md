# Plain Technical Language Policy Design

## Status

Proposed design for a thin shared language and terminology policy in `output-styles`.

## Problem

The shared output baseline requires concise, actionable, and precise responses, but it does not directly constrain unexplained jargon, synonym drift, vague references, ambiguous noun clusters, or procedural sentence shape. A blanket ASD-STE100 compliance rule would be a larger and different contract: it would require controlled-language validation, could reduce precision in design and review work, and would not fit non-English responses. A blanket rule to read every `CONTEXT.md` file would also create an unbounded and potentially stale truth source.

## Goals

- Add a thin, agent-agnostic language policy to the shared `output-styles` baseline.
- Match the user's language while preserving file-local language and canonical project terminology.
- Prefer plain, direct sentences and active voice when the actor matters.
- Use imperative sentences for procedures, and place prerequisites, conditions, and warnings before the actions they constrain.
- Use one canonical term for each concept, avoid invented synonyms, and obtain task-relevant terminology from applicable repository policy and stable project truth.
- Avoid unexplained jargon, vague references, and ambiguous noun clusters without replacing precise technical terms with vague simple words; define an unfamiliar necessary term on first use.
- Treat ASD-STE100 as inspiration unless strict compliance is explicitly required and validated.

## Non-Goals

- Do not implement an ASD-STE100 dictionary, validator, compliance claim, readability score, or fixed reading-grade gate.
- Do not add a new public skill or a second response-style authority.
- Do not require repository-wide discovery or unconditional reading of files named `CONTEXT.md`.
- Do not simplify established professional terminology, code identifiers, schemas, commands, or fixed machine-consumed output.
- Do not change lifecycle routing, manifests, plugin versions, or architecture boundaries.

## Change Classification

- request_kind: change-definition
- change_class: B
- design_strength: design-lite
- truth_impact: medium
- boundary_impact: low
- recommended_next_phase: design-lite
- truth_sync_required: true
- parallel_candidate: false

## Boundaries

- in_scope:
  - Add the approved language and terminology rules to the source `output-styles` skill.
  - Refresh the generated root-flat compatibility surface.
  - Validate the focused source/generated contract and the aggregate repository checks.
- out_of_scope:
  - Change lower-plane domain policy or domain-specific report schemas.
  - Introduce a generic context-file convention.
  - Rewrite existing documentation to conform to the new policy.
  - Add external dependencies or language-analysis tooling.

## Acceptance Conditions

- The shared baseline distinguishes plain language from vocabulary reduction and preserves exact technical terms when they carry required meaning.
- The shared baseline distinguishes procedural imperative wording from analytical or explanatory wording.
- Conditions and warnings precede the actions they constrain.
- Project terminology comes from task-relevant applicable policy and stable truth; the policy does not require reading every similarly named context file.
- Strict ASD-STE100 compliance is claimed only when explicitly required and validated.
- The generated `skills/output-styles/SKILL.md` matches its source after regeneration.
- `bash scripts/check.sh` passes after the required generators run.

## Recovery Policy

Use fix-forward for wording, generated-surface, or validation defects. No guarded rollback is required because the change is documentation-only, has no runtime state, and can be corrected within the same bounded source and generated surfaces.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - src/skills/session/output-styles/SKILL.md
  - skills/output-styles/SKILL.md
- test_file_refs:
  - scripts/check.sh
  - scripts/flatten-skills.py
