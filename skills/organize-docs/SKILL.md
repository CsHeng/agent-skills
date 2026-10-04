---
name: organize-docs
description: "Use for docs organization: README/AGENTS ownership, one-way legacy CLAUDE.md cleanup into AGENTS.md, stable truth roots, docs layout, docs/.ignore, stage artifacts, canonical terminology, search boundaries, and clear Markdown written in its intended form."
---

# Organize Docs

Write or update long-lived project truth after an explicit user request, a user-approved drift follow-up such as an `analyze-project` finding the user asked to fix, or an authorized bounded `sync-truth` handoff backed by current execution evidence. A drift finding by itself is evidence, never mutation approval.

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
- Composed invocation is valid only under an authorized `sync-truth` request, for declared docs-governance predicates and stable truth refs inside the same bounded touch set.
- A Markdown suffix alone is not a docs-governance predicate, and Skill composition never authorizes repository-wide cleanup or prose normalization.

- `README.md` stays human-facing.
- `AGENTS.md` is the maintained AI-facing truth root.
- `CLAUDE.md` is a conditional legacy input, never a separately maintained truth root and never a compatibility surface to recreate. Record the repository root `CLAUDE.md` path type before mutation: absent, regular file, symlink, or an unsafe type.
- When root `CLAUDE.md` is absent, maintain `AGENTS.md` only; do not create `CLAUDE.md` or add a compatibility link.
- When that root path exists and the requested docs work covers it — an explicit legacy-cleanup request, a user-approved drift follow-up naming that path, or an authorized `sync-truth` handoff whose touch set includes it — read [Legacy CLAUDE.md Migration](references/legacy-claude-migration.md) and retire it one way per that reference's path handling; the final state is a valid `AGENTS.md` and no root `CLAUDE.md` path, including a dangling symlink. A docs task whose requested scope does not cover that root path leaves the legacy file untouched and reports it instead.
- The root `CLAUDE.md` migration is bounded to that repository root path; Skill activation never authorizes a repository-wide legacy-file cleanup.
- Stable truth roots and stage artifact roots must be explicit. Repository policy may name an external owner for designs, plans, evaluations and archives; resolve its declared root instead of assuming the invocation repository owns every document. Keep product-required guidance self-contained and do not require the external checkout for standalone product checks.
- Default docs search should avoid stage artifacts when the repository needs that search-boundary.
- Stage artifacts can support history, but they do not become default truth automatically.
- Keep currently effective design or plan prose limited to live goals, authorized discretion, ownership, delivery endpoints, and real pause conditions. Leave superseded gates and historical exemptions in stage history and cite them shortly when needed. Do not copy old exemption lists into every live task, treat document length as a quality gate, or migrate unrelated historical plans unless that cleanup is the requested work.
- When durable decision truth is created, promoted, superseded, compacted, or retired, read [Decision Record Lifecycle](references/decision-record-lifecycle.md) and classify current status together with future value. Do not apply this lifecycle to every docs edit.
- Write stable prose from the current repository state. A reader at `HEAD` must be able to resolve internal references and verify claims without the authoring session, review thread, branch stack, or an uncommitted draft.
- Move change narration, review choreography, temporary phase labels, and historical argument to stage or historical owners unless they are still an exact durable reference. Preserve complete factual propositions, non-obvious rationale, conditions, exceptions, failure modes, and consequences.
- Plan artifact consolidation is optional and never automatic: do it only when the user explicitly asks, or when repository-local search-boundary drift makes scattered plan roots part of the requested docs cleanup. It never rewrites historical prose.
- Canonical terminology must be defined in stable docs when a repository has competing names for the same concept.
- Use `archived` for intentionally retained historical or reference material.
- Use `compat` for compatibility surfaces that target an older, alternate, or constrained version.
- When terminology changes, update docs, paths, tests, and code references together instead of appending corrective notes that leave old terms active.
- Prefer context-appropriate relative file paths and command examples over absolute paths in stable docs.
- For Git projects, when a repo root needs to be made explicit, prefer `cd "$(git rev-parse --show-toplevel)"` before relative commands.

## Writing Stable Docs

Use the intended structure and prose conventions while drafting and revising, rather than relying on a routine restyling pass afterward. Follow repository conventions and the shared `output-styles` baseline for clear language and restrained Markdown; do not create a second formatting policy.

- Organize durable material with real headings, paragraphs, and lists. Use tables or code blocks when they make comparisons or examples easier to use.
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
8. For durable decision work, apply the owner-local lifecycle reference before promoting or retiring truth and preserve stage history by default.
9. When explicitly consolidating plan artifacts, inventory all source plan roots, choose domain-based target directories under the canonical stage root, move files with date-first names such as `YYYY-MM-DD-topic-kind.md`, and update stable-doc and in-file path references after the move while preserving historical content unless a reference is objectively stale because of the move.
10. Write or revise the requested Markdown in its final natural-line form, decomposing genuinely over-broad content at semantic boundaries. Preserved archived originals may be excluded from prose changes; moving history alone does not authorize rewriting its prose.
11. Update stable docs only after explicit user approval, a user-approved drift follow-up (an `analyze-project` finding alone is not approval), or an authorized `sync-truth` handoff with current evidence.

## Validation

Run repository-owned checks relevant to the boundaries affected by the change. Clear prose does not prove that links, ownership, or document placement are correct, and does not replace an existing required check.

When documentation truth boundaries change, run the bundled boundary checker. When inspecting a declared documentation manifest, use the advisory layout checker. Read [Documentation Checks And Repair](references/drift-repair-tools.md) for those invocations; ordinary prose edits do not require an additional formatting pass.

## Repairing Observed Drift

Repair only observed drift within the authorized scope. For a few affected lines, edit them directly; for an authorized mechanical cleanup, use the bundled normalizer described in the linked reference rather than creating another parser. Neither Skill activation nor a failed check authorizes a repo-wide restyling or changes to preserved history.
