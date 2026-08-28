# AGENTS.md

## Project

This repository authors and distributes the `coding` collection of 40 portable Agent Skills. The Skills are semantic guidance usable by any compatible agent environment; this repository does not provide or require a workflow engine.

## Truth And Generated Surfaces

- `src/skills/` is authored Skill truth.
- `contracts/skills.toml`, `contracts/lifecycle.toml`, `contracts/workflow-modes.toml`, and the installed routing reference are declarative authoring and composition guidance.
- `skills/` and `skills.index.json` are tracked generated output; do not edit them by hand.
- `docs/architecture/` contains stable architecture truth.
- `docs/plans/` is stage history and is excluded from default documentation search by `docs/.ignore`.
- Provider plugin manifests are optional distribution surfaces, not workflow authority.

## Workflow Semantics

- Directly matched Skills do not require the optional `use-coding-skills` router.
- Formal `design-change`, `plan-change`, and `implement-change` each invoke `review-change` exactly once before accepting their semantic result.
- Informal work does not acquire automatic review. A standalone `review-change` starts from the supplied bounded target and does not synthesize upstream lifecycle work.
- Review evaluators are read-only. The calling design, planning, or implementing agent adjudicates findings and owns any accepted repair.
- Skills preserve user and repository authorization boundaries. They never imply commit, push, publication, deployment, destructive history changes, or external mutation.

## Working Rules

- Keep Skills provider-neutral and self-contained under the standard Agent Skills directory shape.
- Keep frontmatter descriptions precise enough for native discovery.
- Store optional composition in `semantic_requires`; do not add executable workflow contracts, artifact validators, task graph compilers, mutable ledgers, replay logic, or provider adapters.
- Preserve all 40 public IDs and authored-to-generated parity.
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
