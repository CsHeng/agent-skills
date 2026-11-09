# AGENTS.md

## Project

This repository authors and distributes the `coding` collection of portable Agent Skills. The Skills are semantic guidance usable by any compatible agent environment.

## Truth And Installation

- `skills/<public-id>/` is the single authored and installable Skill tree. Edit its instructions, resources, scripts, and provider metadata directly.
- `contracts/skills.toml` owns public IDs, activation, roles, permissions, and optional semantic dependencies; each ID resolves to its directory under `skills/`.
- The installed routing references own the scope contract between neighboring Skills (clusters and handoffs in `routing.toml`) and the session selection rules in `routing.md`, including direct-match bypass and one-primary-response composition.
- `tests/fixtures/selection-probes.toml` holds uninstalled paired selection probes for discovery audits; checks validate its identifiers; behavioral comparisons evaluate model behavior.
- `docs/architecture/` contains stable architecture truth.
- Shared boundaries, all new designs/plans and retained evaluations belong to `$AGENT_ARCHITECTURE_DIR/docs/`; historical commands belong to its `archived/agent-skills/commands/` tree.
- Resolve the three source roots and `TMPDIR` from this repository's mise configuration; retained runtime and temporary artifacts belong under `$TMPDIR/skills/`, and cross-repository maintenance resolves checkout layout from that configuration. Standalone product checks and runtime work independently of the architecture checkout.
- Use the project environment and supported entrypoints described in `README.md#project-environment`; `mise.toml` owns ordinary development context, while the standalone check works independently of mise and personal global configuration. Re-establish target context when crossing projects and preserve caller-owned run isolation; `mise.toml` owns environment values.
- Global discovery uses an independent installed copy, directly or through host links to that copy. An explicitly authorized install/update owns installed Skill mutations; source edits, Git updates, and checks leave installed Skills unchanged.
- Provider plugin manifests are optional packaging surfaces. Their installed content follows the same source/installation separation; workflow authority remains with the active coding agent and applicable instructions.

## Instruction Scope

- Harness-global instructions own persistent user preferences and thin compaction/recovery reminders. Keep those preferences in harness-global instructions; project records own task-specific permissions, and Skills own lifecycle procedures.
- Project `AGENTS.md` owns repository policy. The project's current design, plan, or approval summary records the task's effective objective, delivery endpoint, authorized actions and targets, exclusions, and unresolved decisions; explicit approval grants authority, and those records document it.
- Skills own portable workflow and domain methods, including how to maintain and reconcile those project records. Session summaries support recall; trusted approvals and project records own authority and the live plan.
- Keep this ownership split when changing guidance here. Update harness-global files only within separately approved scope. Keep superseded task restrictions in history and current gates aligned with current approvals.

## Skill Composition

- Apply directly matched Skills directly; `skills-routing` is an optional entry. Its method references may be read independently for a relevant unresolved choice.
- The active coding agent owns request interpretation, Skill selection, sequencing, evidence judgment, optional review, finding adjudication, and the final response.
- Review is conditional on an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. A standalone `review-change` starts from the supplied bounded target and reviews that target.
- Review evaluators are read-only. The calling design, planning, or implementing agent adjudicates findings and authorizes accepted repairs; bounded implementation, verification execution, diagnosis, and repair labor may be delegated when the host and applicable policy permit it. Final acceptance and continuation decisions remain with the calling agent.
- Skills preserve user and repository authorization boundaries. Commit, push, publication, deployment, destructive history changes, and external mutation require their own authorization.

## Working Rules

- Keep Skills provider-neutral and self-contained under the standard Agent Skills directory shape.
- Keep frontmatter descriptions precise enough for native discovery. For a change to a description, admission boundary, or neighboring handoff, apply `skills/skill-authoring/` and update the scope contract before the summaries that restate it.
- Store only real semantic dependencies in `semantic_requires`; do not add executable workflow contracts, artifact validators, task graph compilers, mutable ledgers, replay logic, provider adapters, or prompt-space lifecycle gates.
- Keep the public inventory in `contracts/skills.toml`; change IDs only as part of an authorized rename, consolidation, or retirement, updating discovery, the scope contract, probes, and references together, and report installed copies or host global entries that still name the old ID. Maintain portable resource closure within each Skill directory.
- Use an existing installation manager, preferably `npx skills`, for cross-platform installation and explicit refresh. Preserve unrelated installed Skills, verify ownership before replacing existing paths, and remove retired owned IDs explicitly; preserve the shared discovery root and unrelated entries.
- Preserve unrelated working-tree changes when editing source.

## Validation

Choose checks for the changed surface after a cohesive group of edits:

- Skill instructions, references, or inventory: `mise exec -- python3 scripts/check-contracts.py` and `mise exec -- python3 scripts/check-install-surface.py` cover discovery, contracts, and resource closure. Use applicable prose/link checks for changed documentation.
- Executable scripts or validators: run their focused tests and relevant syntax, lint, or type checks. Keep unchanged evidence after a repair unless its inputs or behavior were affected.
- Diagram sources or rendering: regenerate affected projections with their owned renderer and check those outputs. Use prose checks for ordinary prose changes.
- `mise run check` is the full product check for relevant broad impact or explicit delivery acceptance. The main agent coordinates it and any standalone check at integration or delivery; workers normally return their relevant local results.

For optional Codex plugin metadata changes, also run the repository-independent plugin validator. Installation, version bump, commit, push, publication, and consumer-state mutation require separate authorization.
