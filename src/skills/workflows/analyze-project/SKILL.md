---
name: analyze-project
description: "Answer read-only project-state questions from current repository truth, from a local fact to requested broad orientation or a truth audit. Expand investigation when evidence is insufficient; not for implementation or code review. Supply bounded project evidence to a more specific domain diagnosis."
---

# Analyze Project

Answer the actual project question from sufficient current evidence, without turning every local query into a full audit.

## Select The Scope

- For a local fact, identify the relevant `project`, follow applicable scoped instructions, and read the stable owner that can answer the question. Verify the specific claim from code, configuration, or commands when needed. Do not automatically inventory all terminology or read every root document.
- If ownership is unclear, stable sources conflict, or evidence is insufficient, expand only along that gap: inspect the relevant repository maps, README/AGENTS, ignore rules, or implementation. State uncertainty rather than guessing. Poor documentation may justify code reconstruction, but does not itself authorize a full-project report.
- For explicitly requested broad orientation or a full truth audit, map the relevant stable truth and search boundaries before drawing conclusions. Use [Full Project Truth Audit](references/full-audit-output.md) for the comprehensive branch, not for routine local questions.

A request to implement, reorganize docs, or review a change belongs to its matching Skill. For runtime/infrastructure/security or another domain diagnosis, contribute bounded project-truth evidence to that primary owner rather than emitting a second report.

## Investigate And Answer

1. Bound the question and the project. Honor the most specific applicable project instructions; use `docs/AGENTS.md`, `AGENTS.md`, `docs/README.md`, and `README.md` as needed to locate the truth owner, not as a fixed reading list for every query.
2. Separate stable truth from stage history before searching. Observe applicable ignore/search policy; a default search miss does not prove hidden, generated, or ignored material absent.
3. Read enough stable evidence to support the answer and perform targeted read-only verification. Escalate investigation when contradictions or missing facts actually prevent a reliable conclusion.
4. When document health or drift affects confidence or is requested, read [Document Health And Drift](references/doc-health-and-drift.md). Classify health and verification basis for that affected scope; do not require a whole-repository classification for an unrelated local fact.
5. Give the conclusion, relevant evidence, and any material limitation once. Use `output-styles`; read [Output Contract](references/output-contract.md) when reporting a broader truth map, drift, or a requested audit. A direct local answer needs no extra report template.
6. Stop after answering. Document reorganization or other mutation requires its own authorized request; this Skill remains read-only.

## Protected Boundaries

- Use `project`, not `workspace`, as the analysis unit. Keep terminology repository-local unless an applicable stable owner defines a wider convention.
- Keep stable truth and stage artifacts distinct. Search stage history only when explicitly requested or needed to resolve a gap that stable truth cannot answer; make that use visible rather than silently promoting history to current truth.
- Preserve the subject and limits of each claim. File existence, documented intent, current implementation, observed runtime behavior, and inferred cause are different evidence.
- Use `fact`, `inferred`, `judgment`, and `uncertain` when confidence matters. Give evidence provenance (`documented`, `code`, `runtime`, or `external`) only when useful.
- Prefer project-relative references with exact starting lines. Use external paths when the evidence necessarily lives outside the project; do not imply those external files apply to every project.
- Keep references and output proportional to the question. Internal investigation as well as final rendering must scale with scope; do not do an unrequested full audit and merely shorten its answer.
- If another primary Skill owns the response, contribute only relevant project facts, confidence, and drift evidence. Do not concatenate report templates or take mutation authority from that composition.
