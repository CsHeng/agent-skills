# AGENTS.md

## Project

This repository authors and distributes the `coding` collection of portable Agent Skills. The Skills are semantic guidance usable by any compatible agent environment; this repository does not provide or require a workflow engine.

## Truth And Installation

- `skills/<public-id>/` is the single authored and installable Skill tree. Edit its instructions, resources, scripts, and provider metadata directly.
- `contracts/skills.toml` owns public IDs, activation, roles, permissions, and optional semantic dependencies; each ID resolves to its directory under `skills/`.
- The installed routing reference owns native trigger cases, direct-match bypass, support routes, and one-primary-response composition; it defines no runtime mode or lifecycle.
- `docs/architecture/` contains stable architecture truth.
- Shared boundaries, all new designs/plans and retained evaluations belong to `$AGENT_ARCHITECTURE_DIR/docs/`; historical commands belong to its `archived/agent-skills/commands/` tree. Do not create product-local evolution records.
- Resolve the three source roots and `AGENT_TMP_ROOT` from this repository's mise configuration; retained runtime and temporary artifacts belong under `$AGENT_TMP_ROOT/skills/`, and cross-repository maintenance must not guess checkout layout. Standalone product checks and runtime never require the architecture checkout.
- Global discovery uses an independent installed copy, directly or through host links to that copy. Source edits, Git updates, and checks must not update installed Skills; an explicitly authorized install/update owns that mutation.
- Provider plugin manifests are optional packaging surfaces. Their installed content follows the same source/installation separation and grants no workflow authority.

## Instruction Scope

- Harness-global instructions own persistent user preferences and thin compaction/recovery reminders. Do not rely only on a task-loaded Skill to retain those preferences, and do not put task-specific permissions or lifecycle procedures in global instructions.
- Project `AGENTS.md` owns repository policy. The project's current design, plan, or approval summary records the task's effective objective, delivery endpoint, authorized actions and targets, exclusions, and unresolved decisions; those records document explicit approval rather than grant it.
- Skills own portable workflow and domain methods, including how to maintain and reconcile those project records. Session summaries are recall, not another approval source or a parallel live plan.
- Keep this ownership split when changing guidance here. A Skill edit does not authorize editing harness-global files; update those files only within separately approved scope. Keep superseded task restrictions in history rather than as contradictory current gates.

## Skill Composition

- Directly matched Skills do not require the optional `skills-routing` entry. Its method references may be read independently for a relevant unresolved choice.
- The active coding agent owns request interpretation, Skill selection, sequencing, evidence judgment, optional review, finding adjudication, and the final response.
- Review is conditional on an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. A standalone `review-change` starts from the supplied bounded target and does not synthesize upstream work.
- Review evaluators are read-only. The calling design, planning, or implementing agent adjudicates findings and authorizes accepted repairs; bounded implementation, verification execution, diagnosis, and repair labor may be delegated when the host and applicable policy permit it. Final acceptance and continuation decisions remain with the calling agent.
- Skills preserve user and repository authorization boundaries. They never imply commit, push, publication, deployment, destructive history changes, or external mutation.

## Working Rules

- Keep Skills provider-neutral and self-contained under the standard Agent Skills directory shape.
- Keep frontmatter descriptions precise enough for native discovery.
- Store only real semantic dependencies in `semantic_requires`; do not add executable workflow contracts, artifact validators, task graph compilers, mutable ledgers, replay logic, provider adapters, or prompt-space lifecycle gates.
- Keep the public inventory in `contracts/skills.toml`; change IDs only as part of an authorized rename, consolidation, or retirement, updating discovery and references together. Maintain portable resource closure within each Skill directory.
- Use an existing installation manager, preferably `npx skills`, for cross-platform installation and explicit refresh. Preserve unrelated installed Skills, verify ownership before replacing existing paths, and remove retired owned IDs explicitly; never mirror-delete the shared discovery root.
- Use `apply_patch` for source edits and preserve unrelated working-tree changes.

## Validation

After changing Skills, contracts, tests, or architecture docs, run:

```bash
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

For optional Codex plugin metadata changes, also run the repository-independent plugin validator. No install, version bump, commit, push, publication, or consumer-state mutation is implied by validation.
