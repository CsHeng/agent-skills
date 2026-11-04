# Writing Stable Docs

Use this reference when authoring or revising Markdown prose or diagrams in stable docs.

## Current-State Prose

Apply `development-standards` Maintainability for writing persisted prose from the current repository state and removing change narration, review choreography, and temporary phase labels. Keep historical explanation only where it still helps a reader understand a decision or obligation, and preserve the conditions, exceptions, and consequences of surviving claims.

## Structure And Form

Use the intended structure and prose conventions while drafting and revising, rather than relying on a routine restyling pass afterward. Follow repository conventions and the shared `output-styles` baseline for clear language and restrained Markdown.

- Use a relationship, flow, or state diagram when it explains ownership, transitions, or dependencies more clearly than procedural prose, and keep the accompanying text to purpose, important constraints, and exceptions. A diagram is an explanation, not a second executable contract or a required artifact for every change.
- Use headings, paragraphs, lists, tables, and code examples for the information that is clearer in those forms.
- Write each natural paragraph or list item on one physical line, splitting at semantic boundaries. This is a searchability rule: `rg` and `grep` must match a complete statement without reconstructing adjacent lines.
- When a line becomes unwieldy, split into separate paragraphs, bullets, numbered steps, headings, or table rows at real semantic boundaries, preserving conditions, exceptions, rationale, failure modes, and consequences. Markdown syntax, tables, code blocks, frontmatter, and intentional hard breaks may need separate lines.

## Paths And Commands

Prefer context-appropriate relative file paths and command examples over absolute paths. For Git projects, when the repository root needs to be explicit, use `cd "$(git rev-parse --show-toplevel)"` before relative commands.

## Retained Originals

Exclude retained originals and unrelated history from mechanical restyling; the repair commands in `drift-repair-tools.md` take path exclusions for this.
