# Analyze Project Output Contract

Read this reference when the requested truth map, audit, or material drift needs reporting guidance. Use `output-styles` as the shared rendering baseline; this contract adds project-analysis semantics. When the user's primary intent is broad project orientation or truth mapping, `analyze-project` owns the domain order and conclusion.

## Answer The Requested Scope

Answer the requested question directly, with enough detail to explain the evidence and any material uncertainty.

1. Lead with one conclusion that answers the user's actual question.
2. Emit only the relevant facts, boundaries, status, operating guidance, or gaps.
3. Include a compact scope, document-health, or verification-basis line when it changes how the conclusion should be trusted.
4. Include drift signals when drift exists and affects the answer or warrants a follow-up.
5. Stop after the last useful action, risk, or unresolved point.

Choose the analysis concerns the question or evidence gap needs: project scope, truth roots, terminology, search boundaries, architecture, operations, status, and drift are available concerns. A comprehensive project orientation, complete truth map, or audit covering most axes is for an explicit user request; read [Full Project Truth Audit](full-audit-output.md) for its semantic sections.

## Evidence

- Distinguish directly observed evidence from derived interpretations, recommendations, and unresolved behavior when the difference affects the answer. Explain the distinction in prose, or use the labels `fact`, `inferred`, `judgment`, and `uncertain` when they help the reader.
- Give evidence provenance as `documented`, `code`, `runtime`, or `external` when it affects confidence or conflict resolution.
- Use paths relative to the selected project root, with external paths only when the evidence necessarily lives outside that project or the user requests absolute paths; mark external files as not necessarily applying to every project.
- Give file references an exact start line in `path:line` form.
- Keep one or two short references with the claim or in one compact evidence bullet, and use a nested reference list for larger evidence sets.

## Drift Signals

Report drift only when it exists. Give each finding a short stable label such as `D1`, `D2`, and cover its type, severity, summary, stable-source evidence, verification evidence, and recommended action, using the labels in `doc-health-and-drift.md`. Stable labels support follow-up within the findings.

A compact rendering:

```md
- `D1` · `medium` · `doc-code-mismatch`: the operating guide names the retired command, while code and tests use the current entrypoint. → `run-organize-docs`
  - evidence: `docs/operations.md:18`; `scripts/run-current.sh:9`; `tests/test_entrypoint.py:21`
```
