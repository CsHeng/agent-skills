# Document Health And Drift

Read when document health or a concrete drift signal affects the answer's confidence, or when the user requests that assessment. Apply classifications to the investigated scope; do not require a whole-project health audit for a local fact whose evidence is sufficient.

## Document Health

- `healthy`: stable docs are largely consistent, cover key project questions, and provide usable operating guidance
- `degraded`: stable docs still guide the reader, but they have gaps, stale areas, or local conflicts
- `untrusted`: stable docs are too incomplete, conflicting, or stale to anchor explanation reliably

## Basis Used For The Run

When a health assessment is relevant, pick the basis supported by the actual investigation and report it when requested or material to confidence:

- `documentation-led`
- `mixed verification`
- `code reconstruction`

## Drift Types

For an actual drift finding, select the applicable type below. Do not manufacture findings or expand the investigation merely to populate every category.

- `doc_code_mismatch`
- `doc_doc_conflict`
- `truth_gap`
- `stage_artifact_pressure` — use this drift label when stage artifacts are exerting pressure on the answer
- `terminology_drift` — use this drift label when repository-local terms, directory names, file names, docs, or code disagree about the same concept
- `search_boundary_drift` — use this drift label when local ignore/search-boundary policy hides, exposes, or describes material differently than stable docs imply
- `stale_operation`

## Allowed Recommended Actions

- `run-organize-docs`
- `ask-human`
- `search-stage-artifacts-explicitly`

## Allowed Severity Values

- `high` — stable truth is likely misleading, blocked, or unsafe to trust without intervention
- `medium` — stable truth is still useful, but the answer needs review or explicit qualification
- `low` — the issue is limited, localized, or advisory and does not dominate the answer

## Basis Selection Guidance

- use `documentation-led` when stable truth is healthy and verification mainly confirms it
- use `mixed verification` when stable truth is degraded but still useful with targeted code or test checks
- use `code reconstruction` when stable truth is untrusted and the answer must be rebuilt from implementation evidence
