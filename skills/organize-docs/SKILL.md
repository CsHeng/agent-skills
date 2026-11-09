---
name: organize-docs
description: "Use for docs organization: README/AGENTS ownership, one-way legacy CLAUDE.md cleanup into AGENTS.md, stable truth roots, docs layout, docs/.ignore, stage artifacts, canonical terminology, search boundaries, and clear Markdown and diagrams written in their intended form. Recording already verified behavior without restructuring belongs to sync-truth."
---

# Organize Docs

Maintain a concise account of project intent, decisions, and current behavior within the requested documentation work or the documentation scope of an authorized owning workflow. Edit docs only under the request or approved scope; drift findings feed that decision. Apply `development-standards` Maintainability for how code behavior and document intent relate.

## Use This Skill When

- the user wants to reorganize `README.md`, `AGENTS.md`, existing legacy `CLAUDE.md`, or stable docs, or change what each document owns
- the repository needs explicit stable truth roots and stage artifact roots
- default docs search needs a local search-boundary policy such as `docs/.ignore`
- scattered plan, draft, or execution-note roots are to be consolidated into one stage-artifact tree, when requested or part of the authorized cleanup
- stable docs, paths, tests, or code need canonical terminology alignment
- user-approved drift follow-up from `analyze-project` points to stable doc maintenance

Read-only project-state explanation and local git or worktree status go to `analyze-project`; recording already verified behavior without changing ownership or structure goes to `sync-truth`.

## Rules

- Treat a task as docs governance when it changes document ownership, truth roots, layout, search boundaries, or terminology, and keep cleanup to the authorized touch set. Mutate on explicit user intent, a user-approved drift follow-up, or the owning workflow's existing documentation authority (including `sync-truth` handoffs).
- `README.md` explains the project to people and to agents that read it first; `AGENTS.md` is the maintained AI-facing truth root; `CLAUDE.md` is a legacy input that migrates into `AGENTS.md`. Write both in the positive register of `skill-authoring/references/instruction-content.md`: the situation, then the action or the owner, with a negative clause only to exclude a case and name its receiver.
- Record the repository root `CLAUDE.md` path type (absent, regular file, symlink, unsafe type) before mutation. When the requested scope covers an existing root `CLAUDE.md` (an explicit legacy-cleanup request, a user-approved drift follow-up naming that path, or an authorized owning workflow's documentation scope), follow [Legacy CLAUDE.md Migration](references/legacy-claude-migration.md); the final state is a valid `AGENTS.md` and no root `CLAUDE.md` path, including a dangling symlink. Otherwise maintain `AGENTS.md` only and report an uncovered legacy file.
- Keep stable truth roots and stage artifact roots explicit. When repository policy names an external owner for designs, plans, evaluations, or archives, resolve its declared root; keep product-required guidance self-contained so standalone product checks do not need the external checkout.
- Keep default docs search free of stage artifacts when the repository needs that search boundary.
- Treat stage artifacts as history: keep them while a decision, operation, or reference needs them; otherwise delete them during authorized cleanup and repair affected links.
- Keep live design and plan prose to goals, authorized discretion, ownership, delivery endpoints, and pause conditions, and cite superseded gates shortly from stage history. Migrate historical plans only when cleanup is the request.
- When an authorized change creates, promotes, supersedes, compacts, or retires durable decision truth, read [Decision Record Lifecycle](references/decision-record-lifecycle.md) and classify current status together with future value.
- When consolidating plan artifacts, inspect the source roots in scope, keep useful material under the repository's canonical stage layout, and repair references after moves or deletions; an explicitly retained historical original may stay unchanged.
- When a repository has competing names for one concept, define the canonical term in stable docs, and update docs, paths, tests, and code references together.
- Name intentionally retained historical or reference material `archived`, and compatibility surfaces targeting an older, alternate, or constrained version `compat`.
- When authoring or revising Markdown prose or diagrams, read [Writing Stable Docs](references/writing-stable-docs.md).

## Workflow

1. Assess the current layout: `README.md`, `AGENTS.md`, the recorded root `CLAUDE.md` path type, `docs/`, and local docs policy files such as `docs/.ignore`; classify stable truth roots versus stage artifact roots using repository-local policy first.
2. Apply the rules above to the requested work, moving or summarizing content into stable docs domains with plans, drafts, and other stage artifacts kept as history.
3. Write the requested Markdown in its final form following Writing Stable Docs.
4. Validate as below.

## Validation

Run repository-owned checks for the boundaries affected by the change; review prose and diagram meaning against current code, observed behavior, and the intended change, since link and path checks cover links, ownership, and placement. When documentation truth boundaries change, run the bundled boundary checker; when inspecting a declared documentation manifest, use the advisory layout checker; for an authorized mechanical wrapping repair of existing prose, use the bundled normalizer. Read [Documentation Checks And Repair](references/drift-repair-tools.md) for those invocations. For a few affected lines, edit directly; repair only observed drift within the authorized scope and leave preserved history unchanged.
