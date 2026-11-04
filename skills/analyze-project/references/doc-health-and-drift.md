# Document Health And Drift

Read when document health or a concrete drift signal affects the answer's confidence, or when the user requests that assessment. This file owns the health, basis, drift-type, severity, and action labels; apply them to the investigated scope.

## Document Health

- `healthy`: stable docs are largely consistent, cover key project questions, and provide usable operating guidance
- `degraded`: stable docs still guide the reader, but they have gaps, stale areas, or local conflicts
- `untrusted`: stable docs are too incomplete, conflicting, or stale to anchor explanation reliably

## Verification Basis

When a health assessment is relevant, report the basis the investigation actually used if requested or material to confidence:

- `documentation-led`: stable truth is healthy and verification mainly confirms it
- `mixed-verification`: stable truth is degraded but still useful with targeted code or test checks
- `code-reconstruction`: stable truth is untrusted and the answer is rebuilt from implementation evidence

## Drift Types

For an actual drift finding, select the applicable type:

- `doc-code-mismatch`
- `doc-doc-conflict`
- `truth-gap`
- `stage-artifact-pressure`: stage artifacts are exerting pressure on the answer
- `terminology-drift`: repository-local terms, directory names, file names, docs, or code disagree about the same concept
- `search-boundary-drift`: local ignore or search-boundary policy hides, exposes, or describes material differently than stable docs imply
- `stale-operation`

## Severity

- `high`: stable truth is likely misleading, blocked, or unsafe to trust without intervention
- `medium`: stable truth is still useful, but the answer needs review or explicit qualification
- `low`: the issue is limited, localized, or advisory and does not dominate the answer

## Recommended Actions

- `run-organize-docs`
- `needs-decision: user`
- `search-stage-artifacts-explicitly`
