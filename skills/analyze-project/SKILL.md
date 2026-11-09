---
name: analyze-project
description: "Answer read-only project-state questions from current repository truth, from a local fact to requested broad orientation or a truth audit. Expand investigation when evidence is insufficient; not for implementation or code review. Supply bounded project evidence to a more specific domain diagnosis."
---

# Analyze Project

Answer the actual project question from sufficient current evidence, scaling both the investigation and the answer to the scope asked.

## Select The Scope

- For a local fact, identify the relevant `project`, follow applicable scoped instructions, read the stable owner that can answer the question, and verify the specific claim from code, configuration, or commands when needed.
- When ownership is unclear, stable sources conflict, or evidence is insufficient, expand along that gap: inspect the relevant repository maps, README/AGENTS, ignore rules, or implementation, and state uncertainty. When documentation is poor, reconstruct from code for the asked question only.
- For explicitly requested broad orientation or a full truth audit, map the relevant stable truth and search boundaries before drawing conclusions, and use [Full Project Truth Audit](references/full-audit-output.md).

When another Skill owns the response (implementation, docs reorganization, change review, or a runtime, infrastructure, security, or other domain diagnosis), contribute only project facts, confidence, and drift evidence.

## Investigate And Answer

1. Bound the question and the project. Honor the most specific applicable project instructions, and use `docs/AGENTS.md`, `AGENTS.md`, `docs/README.md`, and `README.md` to locate the truth owner.
2. Separate stable truth from stage history before searching. Search stage history when requested or when a gap stable truth cannot answer needs it, and say so when used. Check ignore rules and generated or ignored paths before concluding something is absent.
3. Read enough stable evidence to support the answer and verify targeted claims read-only. Escalate when contradictions or missing facts prevent a reliable conclusion.
4. When document health or drift affects confidence or is requested, read [Document Health And Drift](references/doc-health-and-drift.md) and classify the affected scope.
5. Give the conclusion, relevant evidence, and any material limitation once. Read [Output Contract](references/output-contract.md) when reporting a broader truth map, drift, or a requested audit.

## Boundaries

- Use `project` as the analysis unit, and keep terminology repository-local unless an applicable stable owner defines a wider convention.
- Preserve the subject and limits of each claim: file existence, documented intent, current implementation, observed runtime behavior, and inferred cause are different evidence.
- Keep this Skill read-only; document reorganization or other mutation needs its own authorized request.
