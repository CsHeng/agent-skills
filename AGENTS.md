# AGENTS.md

## Project

This repository authors and distributes the `coding` collection of 39 portable Agent Skills. The Skills are semantic guidance usable by any compatible agent environment; this repository does not provide or require a workflow engine.

## Truth And Generated Surfaces

- `src/skills/` is authored Skill truth.
- `contracts/skills.toml` owns public IDs, authored sources, discovery projection, distribution, roles, permissions, and optional semantic dependencies.
- The installed routing reference owns native trigger cases, direct-match bypass, support routes, and one-primary-response composition; it defines no runtime mode or lifecycle.
- `skills/` and `skills.index.json` are tracked generated output; do not edit them by hand.
- `docs/architecture/` contains stable architecture truth.
- Shared boundaries, all new designs/plans and retained evaluations belong to `$AGENT_ARCHITECTURE_DIR/docs/`; historical commands belong to its `archived/skills/` tree. Do not create product-local evolution records.
- Resolve the three source roots and `AGENT_TMP_ROOT` from this repository's mise configuration; retained runtime and temporary artifacts belong under `$AGENT_TMP_ROOT/skills/`, and cross-repository maintenance must not guess checkout layout. Standalone product checks and runtime never require the architecture checkout.
- Provider plugin manifests are optional distribution surfaces, not workflow authority.

## Instruction Scope

- Harness-global instructions own persistent user preferences and thin compaction/recovery reminders. Do not rely only on a task-loaded Skill to retain those preferences, and do not put task-specific permissions or lifecycle procedures in global instructions.
- Project `AGENTS.md` owns repository policy. The project's current design, plan, or approval summary records the task's effective objective, delivery endpoint, authorized actions and targets, exclusions, and unresolved decisions; those records document explicit approval rather than grant it.
- Skills own portable workflow and domain methods, including how to maintain and reconcile those project records. Session summaries are recall, not another approval source or a parallel live plan.
- Keep this ownership split when changing guidance here. A Skill edit does not authorize editing harness-global files; update those files only within separately approved scope. Keep superseded task restrictions in history rather than as contradictory current gates.

## Skill Composition

- Directly matched Skills do not require the optional `use-coding-skills` router.
- The active coding agent owns request interpretation, Skill selection, sequencing, evidence judgment, optional review, finding adjudication, and the final response.
- Review is conditional on an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. A standalone `review-change` starts from the supplied bounded target and does not synthesize upstream work.
- Review evaluators are read-only. The calling design, planning, or implementing agent adjudicates findings and authorizes accepted repairs; bounded implementation, verification execution, diagnosis, and repair labor may be delegated when the host and applicable policy permit it. Final acceptance and continuation decisions remain with the calling agent.
- Skills preserve user and repository authorization boundaries. They never imply commit, push, publication, deployment, destructive history changes, or external mutation.

## Working Rules

- Keep Skills provider-neutral and self-contained under the standard Agent Skills directory shape.
- Keep frontmatter descriptions precise enough for native discovery.
- Store only real semantic dependencies in `semantic_requires`; do not add executable workflow contracts, artifact validators, task graph compilers, mutable ledgers, replay logic, provider adapters, or prompt-space lifecycle gates.
- Preserve all 39 public IDs. Distributed skills keep authored-to-generated parity; undistributed IDs stay contracted and authored but are omitted from `skills/`.
- Use `apply_patch` for source edits and preserve unrelated working-tree changes.

## Validation

After changing Skills, contracts, generators, tests, or architecture docs, run:

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

For optional Codex plugin metadata changes, also run the repository-independent plugin validator. No install, version bump, commit, push, publication, or consumer-state mutation is implied by validation.
