---
name: organize-docs
description: "Use for docs organization: README/AGENTS/CLAUDE split, stable truth roots, docs layout, docs/.ignore, stage artifacts, canonical terminology, search boundaries, and Markdown prose wrapping."
---

# Organize Docs

Write or update long-lived project truth after an explicit user request, an explicit drift follow-up from `analyze-project`, or a bounded `sync-truth` handoff backed by an approved plan and current execution evidence.

## Use This Skill When

- the user wants to reorganize or update `README.md`, `AGENTS.md`, `CLAUDE.md`, or stable docs
- the repository needs explicit stable truth roots and stage artifact roots
- default docs search needs a local search-boundary policy such as `docs/.ignore`
- scattered plan, draft, or execution-note roots should be consolidated into one stage-artifact tree
- stable docs, paths, tests, or code need canonical terminology alignment
- drift follow-up from `analyze-project` points to stable doc maintenance

## Do Not Use This Skill When

- the user primarily wants a read-only project-state explanation
- `analyze-project` should be the default query path
- the task is just local git, worktree, or execution status

## Core Rules

- Direct invocation still requires explicit user intent or explicit drift follow-up; implicit native matching alone never authorizes mutation.
- Controller invocation is valid only under `sync-truth`, for declared docs-governance predicates and stable truth refs inside the same immutable approved touch set.
- A Markdown suffix alone is not a docs-governance predicate, and Skill composition never authorizes repository-wide cleanup or prose normalization.

- `README.md` stays human-facing.
- `AGENTS.md` stays AI-facing.
- `CLAUDE.md` remains a symlink to `AGENTS.md`.
- Stable truth roots and stage artifact roots must be explicit.
- Default docs search should avoid stage artifacts when the repository needs that search-boundary.
- Stage artifacts can support history, but they do not become default truth automatically.
- When durable decision truth is created, promoted, superseded, compacted, or retired, read [Decision Record Lifecycle](references/decision-record-lifecycle.md) and classify current status together with future value. Do not apply this lifecycle to every docs edit.
- Write stable prose from the current repository state. A reader at `HEAD` must be able to resolve internal references and verify claims without the authoring session, review thread, branch stack, or an uncommitted draft.
- Move change narration, review choreography, temporary phase labels, and historical argument to stage or historical owners unless they are still an exact durable reference. Preserve complete factual propositions, non-obvious rationale, conditions, exceptions, failure modes, and consequences.
- Plan artifact consolidation is optional. Do it only when the user explicitly asks, or when repository-local search-boundary drift makes scattered plan roots part of the requested docs cleanup.
- When consolidating plan artifacts, organize final paths by durable domain rather than source harness, and use date-first names such as `YYYY-MM-DD-topic-kind.md`.
- After moving plan artifacts, update stable-doc references and in-file path references to the new paths. Preserve historical content unless a path reference is objectively stale because of the move.
- Canonical terminology must be defined in stable docs when a repository has competing names for the same concept.
- Use `archived` for intentionally retained historical or reference material.
- Use `compat` for compatibility surfaces that target an older, alternate, or constrained version.
- When terminology changes, update docs, paths, tests, and code references together instead of appending corrective notes that leave old terms active.
- Prefer context-appropriate relative file paths and command examples over absolute paths in stable docs.
- For Git projects, when a repo root needs to be made explicit, prefer `cd "$(git rev-parse --show-toplevel)"` before relative commands.
- Do not hard-wrap Markdown prose to a fixed column. Keep each natural paragraph or list item on one physical line unless Markdown syntax, tables, code blocks, frontmatter, or intentional hard breaks require separate lines.
- Keep each searchable statement or contract on one physical line so `rg` and `grep` can match it without reconstructing adjacent lines.
- When a natural line becomes unwieldy, rewrite the content into multiple complete paragraphs, bullets, numbered steps, headings, or table rows at semantic boundaries. Do not insert fixed-column newlines inside one paragraph or list item.

## Workflow

1. Assess the current doc layout: `README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/`, and local docs policy files.
2. Classify stable truth roots versus stage artifact roots using repository-local policy first.
3. Preserve or establish docs-local search-boundary files such as `docs/.ignore` when default search should exclude history.
4. Keep human-facing guidance in `README.md` and AI-operational rules in `AGENTS.md`.
5. Align canonical terminology across stable docs, path names, test names, and code references when the task is terminology cleanup.
6. Move or summarize content into stable docs domains without treating plans, drafts, or other stage artifacts as default truth.
7. For durable decision work, apply the owner-local lifecycle reference before promoting or retiring truth and preserve stage history by default.
8. When explicitly consolidating plan artifacts, inventory all source plan roots, choose domain-based target directories under the canonical stage root, move files with date-first names, and update references after the move.
9. Normalize Markdown prose wrapping with the bundled processing workflow: unwrap fixed-width paragraphs and list-item continuations across stable, stage, and archived docs that are in the requested scope, then decompose genuinely over-broad content at semantic boundaries.
10. Update stable docs only after explicit user approval, explicit drift follow-up from `analyze-project`, or an approved-plan `sync-truth` handoff with current evidence.

## Markdown Prose Processing

Use the bundled normalizer instead of recreating a temporary parser. It scans Git-visible Markdown, including tracked and untracked files while excluding ignored/cache material and symlinks.

Resolve the installed tool and target repository once:

```bash
ORGANIZE_DOCS_SKILL_ROOT="/absolute/path/to/organize-docs"
MARKDOWN_PROSE_TOOL="$(realpath "$ORGANIZE_DOCS_SKILL_ROOT/scripts/normalize-markdown-prose.py")"
REPO_ROOT="$(git rev-parse --show-toplevel)"
```

Run the workflow in order:

```bash
python3 "$MARKDOWN_PROSE_TOOL" --root "$REPO_ROOT" --mode count
python3 "$MARKDOWN_PROSE_TOOL" --root "$REPO_ROOT" --mode preview
python3 "$MARKDOWN_PROSE_TOOL" --root "$REPO_ROOT" --mode write
python3 "$MARKDOWN_PROSE_TOOL" --root "$REPO_ROOT" --mode check
```

- `count` establishes scope without dumping candidates.
- `preview` shows bounded `current || continuation` pairs without mutation.
- `write` removes only continuation newlines and aborts if non-whitespace Markdown prose content or fence, heading, table, or list structure changes.
- `check` fails if any natural paragraph, list item, or blockquote still spans physical lines.
- After mechanical normalization, inspect genuinely long lines. Split unrelated claims into real Markdown blocks with blank lines or list markers; never reintroduce column-based wrapping.

## Validation

- When docs truth boundaries are part of the change, resolve the checker from this skill directory before switching to the target repository:

```bash
ORGANIZE_DOCS_SKILL_ROOT="/absolute/path/to/organize-docs"
CHECK_DOC_BOUNDARIES="$(realpath "$ORGANIZE_DOCS_SKILL_ROOT/scripts/check-doc-boundaries.sh")"
cd "$(git rev-parse --show-toplevel)"
bash "$CHECK_DOC_BOUNDARIES"
```

`ORGANIZE_DOCS_SKILL_ROOT` is the directory that contains this `SKILL.md`. Do not use a target-repository relative path for bundled skill scripts; target repositories do not own them.

The checker calls the same bundled normalizer in `check` mode, so detection and rewriting cannot drift. It preserves symlinks, fenced and indented code blocks, frontmatter, Markdown tables, headings, reference definitions, HTML-only lines, thematic breaks, and intentional hard breaks.
