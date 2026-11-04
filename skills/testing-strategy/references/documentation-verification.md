# Documentation Verification

Read this when a change or audit touches Markdown, prompt or instruction files, or generated documentation and diagrams.

Apply the code-is-behavior rule in `development-standards`: documents and diagrams describe human intent or explain behavior, and they are updated when implementation changes. Explicit user requirements remain binding regardless of where they were recorded.

## Match The Tool To The Property It Checks

- Human-authored prose: review plus Markdown or prose linting, link checking, and documentation builds where applicable.
- Frontmatter, schemas, command identifiers, paths, and other machine-readable fields embedded in Markdown: validate the structured field when an actual consumer or repository boundary depends on it; formatting preference alone does not make it a contract.
- Executable examples: compile or run the example through the real interface.
- Generated documentation and diagrams: regenerate with the owned tool and inspect the result. Existing generation and parity checks verify the tool's operation.
- Prompt or instruction Markdown: test observable consumer behavior with an evaluation or integration scenario when that evidence is worth its cost. An offline fixture proves loading or workflow mechanics; offline scenario review can expose contradictions. Neither establishes that a live model follows the instruction or improves behavior or economic outcomes. Efficacy measurement uses [Agent Skill Evaluation](agent-skill-evaluation.md).

Ordinary Skill editing needs no live experiment, and maintenance checks establish packaging hygiene.

## Prose Assertions

Prose, keywords, headings, layout, and diagram nodes or edges are not a test interface, including when a model reads them. When a real machine-consumed contract needs enforcement, validate its owned structured source or consuming behavior.

When auditing an existing suite, classify each Markdown assertion by its consumer or protected boundary. Delete prose snapshots, retain applicable syntax, link, schema, executable-example, generated-surface, and consumer-behavior checks, and keep behavior evidence in the suite that owns the behavior.
