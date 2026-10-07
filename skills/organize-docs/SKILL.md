---
name: organize-docs
description: "Use for docs organization: README/AGENTS ownership, one-way legacy CLAUDE.md cleanup into AGENTS.md, stable truth roots, docs layout, docs/.ignore, stage artifacts, canonical terminology, search boundaries, and clear Markdown written in its intended form."
---

# Organize Docs

Maintain a concise account of project intent, decisions, and current behavior within the requested documentation work or the documentation scope of an authorized owning workflow. A drift finding by itself is evidence, never mutation approval. Code and observed runtime establish what the product currently does; documentation and diagrams explain that behavior and the intent behind it. Keep intended changes distinct from implemented facts and synchronize the explanation after implementation.

## Use This Skill When

- the user wants to reorganize or update `README.md`, `AGENTS.md`, existing legacy `CLAUDE.md`, or stable docs
- the repository needs explicit stable truth roots and stage artifact roots
- default docs search needs a local search-boundary policy such as `docs/.ignore`
- scattered plan, draft, or execution-note roots should be consolidated into one stage-artifact tree
- stable docs, paths, tests, or code need canonical terminology alignment
- user-approved drift follow-up from `analyze-project` points to stable doc maintenance

## Do Not Use This Skill When

- the user primarily wants a read-only project-state explanation
- `analyze-project` should be the default query path
- the task is just local git, worktree, or execution status

## Core Rules

- Direct invocation still requires explicit user intent or a user-approved drift follow-up; implicit native matching alone never authorizes mutation.
- Composed invocation uses the owning workflow's existing documentation authority and bounded touch set, including `sync-truth` handoffs. Apply it only to relevant documentation-governance work; composition grants no new mutation scope.
- A Markdown suffix alone is not a docs-governance predicate, and Skill composition never authorizes repository-wide cleanup or prose normalization.

- `README.md` stays human-facing.
- `AGENTS.md` is the maintained AI-facing truth root.
- `CLAUDE.md` is a conditional legacy input, never a separately maintained truth root and never a compatibility surface to recreate. Record the repository root `CLAUDE.md` path type before mutation: absent, regular file, symlink, or an unsafe type.
- When root `CLAUDE.md` is absent, maintain `AGENTS.md` only; do not create `CLAUDE.md` or add a compatibility link.
- When that root path exists and the requested docs work covers it — an explicit legacy-cleanup request, a user-approved drift follow-up naming that path, or an authorized owning workflow's documentation scope that includes it — read [Legacy CLAUDE.md Migration](references/legacy-claude-migration.md) and retire it one way per that reference's path handling; the final state is a valid `AGENTS.md` and no root `CLAUDE.md` path, including a dangling symlink. A docs task whose requested scope does not cover that root path leaves the legacy file untouched and reports it instead.
- The root `CLAUDE.md` migration is bounded to that repository root path; Skill activation never authorizes a repository-wide legacy-file cleanup.
- Stable truth roots and stage artifact roots must be explicit. Repository policy may name an external owner for designs, plans, evaluations and archives; resolve its declared root instead of assuming the invocation repository owns every document. Keep product-required guidance self-contained and do not require the external checkout for standalone product checks.
- Default docs search should avoid stage artifacts when the repository needs that search-boundary.
- Stage artifacts can support useful history, but they do not become current implementation truth or require permanent retention. During authorized cleanup, delete material with no remaining decision, operational, or reference value and repair affected links; do not create an archive or retention proof merely to avoid deletion.
- Keep currently effective design or plan prose limited to live goals, authorized discretion, ownership, delivery endpoints, and real pause conditions. Leave superseded gates and historical exemptions in stage history and cite them shortly when needed. Do not copy old exemption lists into every live task, treat document length as a quality gate, or migrate unrelated historical plans unless that cleanup is the requested work.
- When durable decision truth is created, promoted, superseded, compacted, or retired, read [Decision Record Lifecycle](references/decision-record-lifecycle.md) and classify current status together with future value. Do not apply this lifecycle to every docs edit.
- Write stable prose from the current repository state. A reader at `HEAD` must be able to resolve internal references and verify claims without the authoring session, review thread, branch stack, or an uncommitted draft.
- Remove obsolete change narration, review choreography, and temporary phase labels from active docs. Retain historical explanation only where it still helps a reader understand a decision or obligation; preserve the conditions, exceptions, and consequences of surviving claims without keeping every old sentence.
- Plan artifact consolidation is optional: do it when requested or when scattered plan roots are part of the authorized cleanup. Move, summarize, or delete according to remaining value and scope; an explicitly retained historical original may be left unchanged.
- Canonical terminology must be defined in stable docs when a repository has competing names for the same concept.
- Use `archived` for intentionally retained historical or reference material.
- Use `compat` for compatibility surfaces that target an older, alternate, or constrained version.
- When terminology changes, update docs, paths, tests, and code references together instead of appending corrective notes that leave old terms active.
- Prefer context-appropriate relative file paths and command examples over absolute paths in stable docs.
- For Git projects, when a repo root needs to be made explicit, prefer `cd "$(git rev-parse --show-toplevel)"` before relative commands.

## Writing Stable Docs

Use the intended structure and prose conventions while drafting and revising, rather than relying on a routine restyling pass afterward. Follow repository conventions and the shared `output-styles` baseline for clear language and restrained Markdown; do not create a second formatting policy.

- Use a relationship, flow, or state diagram when it explains ownership, transitions, or dependencies more clearly than procedural prose. Keep the accompanying text to purpose, important constraints, and exceptions; do not narrate every node and edge again.
- Use headings, paragraphs, lists, tables, and code examples for the information that is clearer in those forms. A diagram is an explanation, not a second executable contract or a required artifact for every change.
- Keep each natural paragraph or list item on one physical line. This is a searchability rule, not a fixed column width: `rg` and `grep` must match a complete statement without reconstructing adjacent lines.
- When a line becomes unwieldy, split at real semantic boundaries into separate paragraphs, bullets, numbered steps, headings, or table rows. Preserve conditions, exceptions, rationale, failure modes, and consequences when splitting.
- Do not hard-wrap prose to a fixed column. Markdown syntax, tables, code blocks, frontmatter, and intentional hard breaks may require separate lines.

## Workflow

1. Assess the current doc layout: `README.md`, `AGENTS.md`, the recorded initial root `CLAUDE.md` path type, `docs/`, and local docs policy files.
2. Classify stable truth roots versus stage artifact roots using repository-local policy first.
3. Preserve or establish docs-local search-boundary files such as `docs/.ignore` when default search should exclude history.
4. Keep human-facing guidance in `README.md` and AI-operational rules in `AGENTS.md`.
5. Apply the linked one-way root `CLAUDE.md` migration only when the recorded initial state shows that path already existed and the requested scope covers that repository root; never create it for a repository that lacked it and never recreate a compatibility link.
6. Align canonical terminology across stable docs, path names, test names, and code references when the task is terminology cleanup.
7. Move or summarize content into stable docs domains without treating plans, drafts, or other stage artifacts as default truth.
8. For durable decision work, retain the rationale and obligations that still matter under the owner-local lifecycle; obsolete history may be deleted within the authorized cleanup.
9. When consolidating plan artifacts, inspect the source roots in scope, retain useful material under the repository's canonical stage layout, and repair references after moves or deletions. Do not require historical copies or content manifests for material that no longer serves a purpose.
10. Write the requested Markdown in its final natural-line form. Prefer a concise diagram for relationships or flow, and decompose remaining prose at semantic boundaries. Exclude retained originals and unrelated history from mechanical restyling.
11. Update stable docs only when the user request or approved change scope covers those edits, whether invoked directly or through an owning workflow such as `sync-truth`. A drift finding alone is not approval; factual updates need current evidence.

## Validation

Run repository-owned checks relevant to the boundaries affected by the change. Clear prose does not prove that links, ownership, or document placement are correct, and does not replace an existing required check.

Check syntax, paths, links, declared structure, and executable examples where relevant. Review prose and diagram meaning against current code, observed behavior, and the intended change; do not freeze their wording, nodes, or layout with content hashes or literal-text tests. Implementation evidence validates behavior, while documentation is updated to explain the result.

When documentation truth boundaries change, run the bundled boundary checker. When inspecting a declared documentation manifest, use the advisory layout checker. Read [Documentation Checks And Repair](references/drift-repair-tools.md) for those invocations; ordinary prose edits do not require an additional formatting pass.

## Repairing Observed Drift

Repair only observed drift within the authorized scope. For a few affected lines, edit them directly; for an authorized mechanical cleanup, use the bundled normalizer described in the linked reference rather than creating another parser. Neither Skill activation nor a failed check authorizes a repo-wide restyling or changes to preserved history.
