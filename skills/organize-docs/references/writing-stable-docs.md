# Writing Stable Docs

Use this reference when authoring or revising Markdown prose or diagrams in stable docs.

## Current-State Prose

Apply `development-standards` Maintainability for writing persisted prose from the current repository state and removing change narration, review choreography, and temporary phase labels. Keep historical explanation only where it still helps a reader understand a decision or obligation, and preserve the conditions, exceptions, and consequences of surviving claims.

## Structure And Form

Use the intended structure and prose conventions while drafting and revising. Follow repository conventions and the shared `output-styles` baseline for clear language and restrained Markdown.

- Use a relationship, flow, or state diagram when it explains ownership, transitions, or dependencies more clearly than procedural prose, and keep the accompanying text to purpose, important constraints, and exceptions. A diagram explains the subject; executable contracts have their own owners, and each change calls for the artifacts that help explain it. When a PlantUML diagram is crowded or its rendered output is hard to read, read [PlantUML Layout](plantuml-layout.md).
- Use headings, paragraphs, lists, tables, and code examples for the information that is clearer in those forms.
- Write each natural paragraph or list item on one physical line, splitting at semantic boundaries. This is a searchability rule: `rg` and `grep` must match a complete statement on one line.
- When a line becomes unwieldy, split into separate paragraphs, bullets, numbered steps, headings, or table rows at real semantic boundaries, preserving conditions, exceptions, rationale, failure modes, and consequences. Markdown syntax, tables, code blocks, frontmatter, and intentional hard breaks may need separate lines.

## Self-Describing Sources

A self-describing source ships with the code and prints its own reference: CLI `--help` output, task-runner listings such as `mise tasks` or `make help`, configuration schemas, and generated API references. That source owns the reference and stays current with the code it describes.

- Where a reader needs the reference, name the command or link the file.
- When the reference lacks something users need, such as option combinations, defaults, or the meaning of output markers, revise the source itself: the help text, task description, or schema. The owning code carries the fix, and documents gain it by pointing to the source.
- Keep in documents what spans more than one surface: purpose, a quick start that strings commands into a workflow, rationale, and platform caveats.
- When a published medium needs the full listing without the runtime, generate it from the source through a repository-owned step.
- During cleanup, treat a hand-copied listing as drift: move content unique to the copy into the source, then delete the copy.

## Paths And Commands

Prefer context-appropriate relative file paths and command examples over absolute paths. For Git projects, when the repository root needs to be explicit, use `cd "$(git rev-parse --show-toplevel)"` before relative commands.

## Retained Originals

Exclude retained originals and unrelated history from mechanical restyling; the repair commands in `drift-repair-tools.md` take path exclusions for this.
