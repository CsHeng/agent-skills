# Full Project Truth Audit

Use this reference when the user requests comprehensive project orientation or a full truth audit. A local question or incomplete documentation can require deeper investigation of one gap without requiring this broader report.

## Audit Concerns

Choose the concerns relevant to the requested audit and cover them once. These are information responsibilities, not mandatory headings or a fixed presentation order:

- Project purpose, scope, current conclusion and the facts that define it.
- Stable truth roots, stage artifact roots, root reference files, document health and verification basis.
- Repository-local terminology that affects architecture, operation, lifecycle, compatibility or status.
- Search boundaries, controlling ignore files and any explicit historical or generated search path used.
- Ownership, dependency direction, control/data paths and other relevant architecture boundaries.
- Validated entrypoints, commands and operating conditions.
- Implemented, in-progress, planned, unverified and out-of-scope work that materially affects current state.
- Actual gaps or drift, using the responsibilities in [Output Contract](output-contract.md).

Apply the shared `output-styles` baseline. Combine related concerns or omit inapplicable sections; do not manufacture empty sections to fill a template. If missing evidence affects a requested conclusion, state the gap rather than omit the limitation. Keep each finding understandable with the evidence needed to verify it.

## Required Truth-Map Information

For a requested complete truth map, identify the analyzed scope, stable truth roots and root reference files with precise source references, stage roots, search policy used, and whether historical stage material influenced the answer. Describe document health as `healthy`, `degraded` or `untrusted`, and the verification basis as `documentation-led`, `mixed verification` or `code reconstruction`.

Those facts may share a compact paragraph, list or table. Distinguish observation, inference and judgment when it matters, but do not require epistemic labels or one heading per field.

## Drift Evidence

Emit drift only when it exists. Preserve each finding's stable label, type, severity, summary, stable-source evidence, verification evidence and allowed recommended action as defined in [Output Contract](output-contract.md). Stable finding IDs support follow-up; they are not a general numbering scheme for the answer.
