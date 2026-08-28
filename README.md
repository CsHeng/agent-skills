# Agent Skills: coding

This repository is the authored source and generated portable payload for a collection of 40 semantic coding Skills. The collection guides agents through analysis, design, planning, implementation, review, documentation, policy, testing, tools, and Git work without depending on a particular agent product.

## Layout

- `src/skills/`: nested authored source
- `skills/`: generated root-flat distribution
- `contracts/skills.toml`: public ID, source, discovery, role, permission, and semantic-composition inventory
- `contracts/lifecycle.toml` and `contracts/workflow-modes.toml`: non-executable semantic guidance
- `skills/use-coding-skills/references/routing.toml`: installed trigger and composition guidance
- `docs/architecture/`: stable maintenance truth
- `docs/plans/`: stage artifacts, excluded from default docs search

The repository contains no workflow engine, artifact validator, task graph compiler, mutable task ledger, replay system, provider adapter, or user-settings integration. Compatible agent environments may use the Skills independently and may implement their own mechanics without consuming these private authoring contracts.

## Workflow Skills

The primary semantic workflow Skills are `analyze-project`, `design-change`, `plan-change`, `implement-change`, `review-change`, `sync-truth`, and `close-change`.

Formal design, planning, and implementation each include one bounded review through `review-change`. Informal work is not automatically reviewed. A direct review request needs only its supplied bounded target, and review evaluators never mutate the target.

## Generate And Check

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

For a repository-only acceptance run from a disposable copy:

```bash
python3 scripts/run-standalone-check.py
```

## Local Use

The recommended installation is a local Git checkout plus one child symlink per public Skill from `skills/<public-id>` into the agent environment's standard Skill discovery root. Keep one active discovery path per public ID. Optional Claude and Codex plugin manifests remain compatibility surfaces with their own installation lifecycle.

## Acknowledgements

The collection builds on the open [Agent Skills specification](https://agentskills.io/) and ideas from the broader open-source agent tooling community.
