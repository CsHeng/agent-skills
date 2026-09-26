---
name: organize-docs
description: "Use for docs organization: README/AGENTS ownership, one-way legacy CLAUDE.md cleanup into AGENTS.md, stable truth roots, docs layout, docs/.ignore, stage artifacts, canonical terminology, search boundaries, and Markdown prose wrapping."
---

# Organize Docs

Write or update long-lived project truth after an explicit user request, an explicit drift follow-up from `analyze-project`, or an authorized bounded `sync-truth` handoff backed by current execution evidence.

## Use This Skill When

- the user wants to reorganize or update `README.md`, `AGENTS.md`, existing legacy `CLAUDE.md`, or stable docs
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
- Composed invocation is valid only under an authorized `sync-truth` request, for declared docs-governance predicates and stable truth refs inside the same bounded touch set.
- A Markdown suffix alone is not a docs-governance predicate, and Skill composition never authorizes repository-wide cleanup or prose normalization.

- `README.md` stays human-facing.
- `AGENTS.md` is the maintained AI-facing truth root.
- `CLAUDE.md` is a conditional legacy input, never a separately maintained truth root and never a compatibility surface to recreate.
- Record the repository root `CLAUDE.md` path type before mutation: absent, regular file, symlink, or an unsafe type.
- When root `CLAUDE.md` is absent, maintain `AGENTS.md` only; do not create `CLAUDE.md` or add a compatibility link.
- When root `CLAUDE.md` exists, read [Legacy CLAUDE.md Migration](references/legacy-claude-migration.md) and retire it one way: unlink symlinks directly without modifying their targets; rename or merge regular-file guidance into `AGENTS.md` before removing the legacy path. The final state is a valid `AGENTS.md` and no root `CLAUDE.md` path, including a dangling symlink.
- The root `CLAUDE.md` migration is bounded to that repository root path; Skill activation never authorizes a repository-wide legacy-file cleanup.
- Stable truth roots and stage artifact roots must be explicit. Repository policy may name an external owner for designs, plans, evaluations and archives; resolve its declared root instead of assuming the invocation repository owns every document. Keep product-required guidance self-contained and do not require the external checkout for standalone product checks.
- Default docs search should avoid stage artifacts when the repository needs that search-boundary.
- Stage artifacts can support history, but they do not become default truth automatically.
- Keep currently effective design or plan prose limited to live goals, authorized discretion, ownership, delivery endpoints, and real pause conditions. Leave superseded gates and historical exemptions in stage history and cite them shortly when needed. Do not copy old exemption lists into every live task, treat document length as a quality gate, or migrate unrelated historical plans unless that cleanup is the requested work.
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

1. Assess the current doc layout: `README.md`, `AGENTS.md`, the recorded initial root `CLAUDE.md` path type, `docs/`, and local docs policy files.
2. Classify stable truth roots versus stage artifact roots using repository-local policy first.
3. Preserve or establish docs-local search-boundary files such as `docs/.ignore` when default search should exclude history.
4. Keep human-facing guidance in `README.md` and AI-operational rules in `AGENTS.md`.
5. Apply the linked one-way root `CLAUDE.md` migration only when the recorded initial state shows that path already existed; never create it for a repository that lacked it and never recreate a compatibility link.
6. Align canonical terminology across stable docs, path names, test names, and code references when the task is terminology cleanup.
7. Move or summarize content into stable docs domains without treating plans, drafts, or other stage artifacts as default truth.
8. For durable decision work, apply the owner-local lifecycle reference before promoting or retiring truth and preserve stage history by default.
9. When explicitly consolidating plan artifacts, inventory all source plan roots, choose domain-based target directories under the canonical stage root, move files with date-first names, and update references after the move.
10. Normalize active Markdown prose in the requested scope with the bundled processing workflow, then decompose genuinely over-broad content at semantic boundaries. Preserved archived originals may be excluded; moving history alone does not authorize rewriting its prose.
11. Update stable docs only after explicit user approval, explicit drift follow-up from `analyze-project`, or an approved-plan `sync-truth` handoff with current evidence.

## Markdown Prose Processing

Use the bundled normalizer instead of recreating a temporary parser. It scans Git-visible Markdown, including tracked and untracked files while excluding ignored/cache material and symlinks. Use repeatable `--exclude <literal-repository-relative-prefix>` for explicitly preserved history, for example `--exclude archived`; active files remain checked. Optional `--immutable-manifest` compatibility remains available for projects that deliberately retain pinned originals, but neither local history nor hash locks are required.

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

### Manifest Mode For Declared Documentation Layouts

When a repository declares its documentation placement in a machine-readable manifest instead of prose, resolve the bundled layout checker the same way and point it at that manifest:

```bash
ORGANIZE_DOCS_SKILL_ROOT="/absolute/path/to/organize-docs"
LAYOUT_CHECKER="$(realpath "$ORGANIZE_DOCS_SKILL_ROOT/scripts/check-documentation-layout.py")"
cd "$(git rev-parse --show-toplevel)"
python3 "$LAYOUT_CHECKER" --root . --manifest testing/documentation-layout.json
```

- The manifest is the placement authority: declared roots and their material classes, required indexes, stage-bundle shape, archive class shape, link-resolution scope, relocation manifests, and named exception classes.
- Implemented capabilities are `declared-roots`, `stage-shape`, `archive-shape`, `root-shape`, `index-closure`, `link-resolution`, and `migration-conservation`; the manifest maps them to its own gate identifiers.
- One installed implementation serves every repository, so no checker copy is vendored into a documentation tree and no repository needs another repository's checkout at runtime.
- A violation is repair or an explicit declared exception with a reason; never silence a finding by narrowing the scan or deleting the assertion underneath it.
- Archived and staged scopes report unresolved links as named exemptions rather than failures, because retained historical bodies are not rewritten to satisfy a gate.
- Exit status is `0` on pass, `1` on undeclared violations, and `2` on an unusable manifest or missing checker.
