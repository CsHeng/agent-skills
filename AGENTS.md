# AGENTS.md

## Project

This repository authors and distributes the `coding` collection of 39 portable Agent Skills. The Skills are semantic guidance usable by any compatible agent environment; this repository does not provide or require a workflow engine.

## Truth And Generated Surfaces

- `src/skills/` is authored Skill truth.
- `contracts/skills.toml` owns public IDs, authored sources, discovery projection, roles, permissions, and optional semantic dependencies.
- The installed routing reference owns native trigger cases, direct-match bypass, support routes, and one-primary-response composition; it defines no runtime mode or lifecycle.
- `skills/` and `skills.index.json` are tracked generated output; do not edit them by hand.
- `docs/architecture/` contains stable architecture truth.
- `docs/plans/` is stage history and is excluded from default documentation search by `docs/.ignore`.
- Provider plugin manifests are optional distribution surfaces, not workflow authority.

## Skill Composition

- Directly matched Skills do not require the optional `use-coding-skills` router.
- The active coding agent owns request interpretation, Skill selection, sequencing, evidence judgment, optional review, finding adjudication, and the final response.
- Review is conditional on an explicit request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. A standalone `review-change` starts from the supplied bounded target and does not synthesize upstream work.
- Review evaluators are read-only. The calling design, planning, or implementing agent adjudicates findings and owns any accepted repair.
- Skills preserve user and repository authorization boundaries. They never imply commit, push, publication, deployment, destructive history changes, or external mutation.

## Working Rules

- Keep Skills provider-neutral and self-contained under the standard Agent Skills directory shape.
- Keep frontmatter descriptions precise enough for native discovery.
- Store only real semantic dependencies in `semantic_requires`; do not add executable workflow contracts, artifact validators, task graph compilers, mutable ledgers, replay logic, provider adapters, or prompt-space lifecycle gates.
- Preserve all 39 public IDs and authored-to-generated parity.
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
