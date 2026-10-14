# Agent Skills: coding

This repository authors portable semantic coding Skills in one installable tree. The collection guides agents through analysis, design, planning, implementation, review, documentation, policy, testing, tools, and Git work. Generic workflows do not depend on a particular agent product; named tool Skills declare the tools they require.

## Layout

- `skills/<public-id>/`: authored instructions, references, scripts, assets, and provider metadata; also the portable installation unit
- `contracts/skills.toml`: public ID, activation, role, permission, and semantic-composition inventory
- `contracts/install-targets.toml`: installation and optional plugin boundaries
- `skills/skills-routing/references/routing.toml`: installed trigger and composition guidance
- `docs/architecture/`: stable maintenance truth
- Evolution material is maintained under `$AGENT_ARCHITECTURE_DIR/docs/plans/skills/` and `docs/evaluations/skills/`; inert originals live in that repository's `archived/agent-skills/`. Product checks and installation do not need that checkout.

The local `mise.toml` declares `AGENT_ARCHITECTURE_DIR`, `AGENT_SKILLS_DIR`, and `PI_EXTENSIONS_DIR`. Use those resolved roots for cross-repository maintenance; `.mise.local.toml.example` documents layout overrides. Shared ownership and vocabulary live at `$AGENT_ARCHITECTURE_DIR/docs/architecture/repository-boundaries.md`.

The repository contains no workflow engine, artifact validator, task graph compiler, mutable task ledger, replay system, provider adapter, or user-settings integration. Compatible agent environments may use the Skills independently and may implement their own mechanics without consuming these private authoring contracts.

## Skill Composition

The collection includes semantic capabilities for repository analysis, change design, planning, implementation, review, truth maintenance, and completion judgment. These are independently selected Skills, not fixed phases of a repository-owned workflow.

The active coding agent selects one primary response owner and any useful overlays. Review is conditional on explicit intent, an applicable repository or approved-scope rule, or evidence-backed risk. A direct review request needs only its supplied bounded target, and review evaluators never mutate the target.

`skills-routing` is the single entry for unresolved Skill, tool, language, verification, and simplification choices, with each method loaded from its own reference only when needed. Clearly matched tasks enter their owning Skill directly.

[herdr-implement](skills/herdr-implement/SKILL.md) handles an explicit request to implement through Herdr: the selected external CLI runs as another main session, implements with `implement-change`, and returns changes for the current session's `review-implementation`. Requests such as “Use herdr-implement with agent=pi to implement this plan” use native Skill discovery. Herdr and its external `herdr` Skill must be installed separately; this collection does not bundle them.

## Maintain And Check

```bash
bash scripts/render-diagrams.sh
bash scripts/check.sh
```

For a repository-only acceptance run from a disposable copy:

```bash
python3 scripts/run-standalone-check.py
```

## Local Use

Use `npx skills` to install from this checkout or the remote repository; see the [quickstart](docs/quickstart.md) for installation, explicit refresh, and removal. Installed Skills are independent copies: editing this repository, pulling Git changes, and running checks do not change global behavior. Agent-specific links may point to the installed copy, but must not expose the active development checkout.

## Project Environment

Use `mise run check` or `mise exec -- <command>` for this checkout's development context, including commands launched from subdirectories. `mise.toml` binds this repository's own source root to the current checkout and evaluates [`scripts/checkout-env.sh`](scripts/checkout-env.sh). The independently supported `bash scripts/check.sh` sources the same helper without requiring mise, a sibling repository, or personal global configuration.

The helper places `UV_PROJECT_ENVIRONMENT` and pytest's cache under `${XDG_CACHE_HOME:-$HOME/.cache}`, keyed by a SHA-256 digest of the checkout's physical path so distinct worktrees do not share mutable state. It uses the platform's `sha256sum` or `shasum -a 256`. `PYTEST_ADDOPTS` retains caller options and appends the project cache setting, so direct `mise exec -- uv run pytest` also avoids a shared global pytest state directory. uv's package cache keeps its native/caller default; Ruff respects an existing `RUFF_CACHE_DIR` and otherwise uses the external cache root's `ruff/` directory. Normal Python entrypoints suppress bytecode writes. The helper selects paths; it does not recreate or delete environments.

An explicit nonempty caller `TMPDIR` takes precedence over global mise defaults; otherwise mise uses the global value or `~/tmp/agent-arch`. A standalone check without mise keeps the caller's native temporary-directory behavior. Shared retained-artifact placement remains governed by the workspace contract, not by cache settings. Crossing projects requires entering the target context; merely changing cwd or using `uv --project` does not remove inherited project environment paths.

Keep one active discovery path per tool and public ID. Optional Claude and Codex plugins use their managed installed copies and their own explicit update lifecycle. The repository's `install.sh` and `install-codex.sh` are plugin-registration helpers, not general Skill-copy installers.

## Acknowledgements

The collection builds on the open [Agent Skills specification](https://agentskills.io/) and ideas from the broader open-source agent tooling community.
