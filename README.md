# Agent Skills: coding

This repository authors portable semantic coding Skills in one installable tree. The collection guides agents through analysis, design, planning, implementation, review, documentation, policy, testing, tools, Git work, and Skill authoring. Generic workflows work across agent products; named tool Skills declare the tools they require.

## Layout

- `skills/<public-id>/`: authored instructions, references, scripts, assets, and provider metadata; also the portable installation unit
- `contracts/skills.toml`: public ID, activation, role, permission, and semantic-composition inventory
- `contracts/install-targets.toml`: installation and optional plugin boundaries
- `skills/skills-routing/references/routing.toml`: installed scope contract of Skill clusters and handoffs between neighboring Skills
- `tests/fixtures/selection-probes.toml`: uninstalled paired selection probes for discovery audits
- `docs/architecture/`: stable maintenance truth
- Evolution material is maintained under `$AGENT_ARCHITECTURE_DIR/docs/plans/skills/` and `docs/evaluations/skills/`; inert originals live in that repository's `archived/agent-skills/`. Product checks and installation work independently of that checkout.

The local `mise.toml` declares `AGENT_ARCHITECTURE_DIR`, `AGENT_SKILLS_DIR`, and `PI_EXTENSIONS_DIR`. Use those resolved roots for cross-repository maintenance; `.mise.local.toml.example` documents layout overrides. Shared ownership and vocabulary live at `$AGENT_ARCHITECTURE_DIR/docs/architecture/repository-boundaries.md`.

Compatible agent environments may use the Skills independently and implement their own mechanics; these authoring contracts remain private to this repository.

## Skill Composition

The collection includes semantic capabilities for repository analysis, change design, planning, implementation, review, truth maintenance, and completion judgment. The active agent selects these Skills independently for the task.

The active coding agent selects one primary response owner and any useful overlays. Review is conditional on explicit intent, an applicable repository or approved-scope rule, or evidence-backed risk. A direct review request needs only its supplied bounded target, and review evaluators examine the target read-only.

`skills-routing` is the single entry for unresolved Skill, tool, language, verification, and simplification choices, with each method loaded from its own reference only when needed. Clearly matched tasks enter their owning Skill directly.

[herdr-handoff](skills/herdr-handoff/SKILL.md) and [herdr-delegate](skills/herdr-delegate/SKILL.md) handle an explicit request to hand an established plan to another main session through Herdr. With `herdr-handoff`, the other main, by default the same agent, model, and thinking level as the current one, implements with `implement-change` and owns the work through delivery. With `herdr-delegate`, it returns changes for the current session's `review-implementation` in bounded rounds. Requests such as “Use herdr-delegate with agent=codex to implement this plan” use native Skill discovery. Install Herdr and its external `herdr` Skill separately.

## Maintain And Check

For Skill instructions, references, or inventory changes, check the authored contracts and resource closure:

```bash
mise exec -- python3 scripts/check-contracts.py
mise exec -- python3 scripts/check-install-surface.py
```

Run focused tests for changed executable behavior. Regenerate diagrams with their owned renderer when their sources or rendering change. Batch related edits before repeating checks and reuse still-applicable results after repair.

For broad product impact or explicit delivery acceptance, use `mise run check` (or the independent `bash scripts/check.sh`). The main agent coordinates full and integration checks; delegated workers normally provide local feedback. For a repository-only acceptance run from a disposable copy:

```bash
python3 scripts/run-standalone-check.py
```

## Project Environment

Use `mise run check` or `mise exec -- <command>` for this checkout's development context, including commands launched from subdirectories. `mise.toml` binds this repository's own source root to the current checkout and evaluates [`scripts/checkout-env.sh`](scripts/checkout-env.sh). The independently supported `bash scripts/check.sh` sources the same helper independently of mise, a sibling repository, and personal global configuration.

The helper places `UV_PROJECT_ENVIRONMENT` and pytest's cache under `${XDG_CACHE_HOME:-$HOME/.cache}`, keyed by a SHA-256 digest of the checkout's physical path so each worktree has isolated mutable state. It uses the platform's `sha256sum` or `shasum -a 256`. `PYTEST_ADDOPTS` retains caller options and appends the project cache setting, so direct `mise exec -- uv run pytest` also avoids a shared global pytest state directory. uv's package cache keeps its native/caller default; Ruff respects an existing `RUFF_CACHE_DIR` and otherwise uses the external cache root's `ruff/` directory. Normal Python entrypoints suppress bytecode writes. The helper selects paths; environment creation and deletion remain separate operations.

An explicit nonempty caller `TMPDIR` takes precedence over global mise defaults; otherwise mise uses the global value or `~/tmp/agent-arch`. A standalone check outside mise keeps the caller's native temporary-directory behavior. The workspace contract governs shared retained-artifact placement; cache settings govern caches. Crossing projects requires entering the target context to replace inherited project environment paths, including when changing cwd or using `uv --project`.

## Local Use

Use `npx skills` to install from this checkout or the remote repository; see the [quickstart](docs/quickstart.md) for installation, explicit refresh, and removal. Installed Skills are independent copies: an explicitly authorized install or refresh updates global behavior. Agent-specific links may point to the installed copy; keep the active development checkout separate from global discovery.

Keep one active discovery path per tool and public ID. Optional Claude and Codex plugins use their managed installed copies and their own explicit update lifecycle. The repository's `install.sh` and `install-codex.sh` are plugin-registration helpers; `npx skills` provides general Skill-copy installation.

## Acknowledgements

The collection builds on the open [Agent Skills specification](https://agentskills.io/) and ideas from the broader open-source agent tooling community.
