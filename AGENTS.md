# AGENTS.md

For human-facing project overview and skill inventory, see `README.md`.

## Project

This repository is a local Claude Code and Codex plugin marketplace and plugin source for `coding@csheng`.

The plugin provides nested authored skills under `src/skills/`, one generated root-flat 39-skill payload under `skills/`, a single authored Python lifecycle runtime under `src/runtime/harness/`, and six generated skill-local runtime bundles.

Current plugin identity:
- plugin name: `coding`
- marketplace name: `csheng`
- current version: `1.1.0`

## Repository Layout

- `.claude-plugin/plugin.json`: Claude plugin manifest
- `.claude-plugin/marketplace.json`: Claude local marketplace manifest
- `.codex-plugin/plugin.json`: Codex plugin manifest; keep Claude-only fields such as `hooks` out of this file
- `.codex-marketplace/.agents/plugins/marketplace.json`: Codex local marketplace manifest
- `.codex-marketplace/plugins/coding`: symlink back to this repository root so Codex can consume the expected `./plugins/coding` marketplace source shape without moving the repository
- `src/skills/`: source-of-truth skill tree grouped by workflow/session/discipline/policy/tool/git/review category
- `src/runtime/harness/`: single non-discoverable deterministic lifecycle runtime and tests
- `skills/`: tracked generated root-flat 39-skill payload consumed by both plugin manifests and standalone skill installers
- `skills/<owner>/scripts/harness/`: generated skill-local runtime bundles for the six runtime-owning lifecycle skills
- `contracts/skills.toml`: source-of-truth source mapping, exposure, activation-mode, default-role, runtime ownership, and provider-projection contract keyed by public skill ID
- `contracts/runtime-bundles.toml`: exact production runtime file manifest
- `skills/use-coding-skills/references/routing.toml`: installed semantic trigger-case, discovery, phase-to-owner, review-evaluator, support-route, composition, and host-wrapper contract
- `.dist/`: ignored inert local output boundary; no generator or checker consumes it
- `archived/`: inert historical material outside active plugin discovery and default repository search
- `docs/architecture/workflow-orchestration.md`: canonical maintenance view of lifecycle routing, the installed implementation DAG, and controller-owned repair
- `docs/architecture/diagrams/`: generated PlantUML views of full harness routing, skill planes, activation and trigger ownership, and the controller-local workflow contract; do not edit by hand
- `docs/architecture/generated/`: tracked SVG renderings of those diagrams for human-facing docs; regenerated together with the PlantUML sources by `scripts/generate-workflow-diagrams.py`
- `hooks/`: post-edit validation hooks
- `install.sh`: registers the local marketplace in Claude settings
- `install-codex.sh`: registers this repository as a Codex local marketplace and installs `coding@csheng`

## Sovereign Harness Kernel

Top-level harness authority in this repository is:

- `analyze-project`
- `design-change`
- `plan-change`
- `implement-change`
- `review-change`
- `sync-truth`
- `close-change`

This control plane owns request routing, phase transition, evidence-based recovery routing, parallelization permission, policy injection timing, and completion judgment.

Kernel defaults:
- serial-first execution unless an approved plan defines a dependency-frozen named batch with explicit human approval, safe isolation, disjoint writes and resource locks, and a bounded maximum width
- `plan-change` owns portable task topology, batch authorization, delegation eligibility, and semantic execution/reasoning recommendations; `implement-change` owns runtime actor and model binding without changing that topology
- runtime binding defaults to semantic routing and may honor an explicit `inherit-main` model/reasoning override without changing approved serial/parallel shape; reusable contracts remain provider-neutral
- fix-forward recovery by default; guarded rollback requires an approved exact trigger, tested target, and verification
- human-sovereign approvals at design, plan, truth-sync, and close
- no unattended execution by default
- `design-change` and `plan-change` do not complete on artifact write alone; they require validation and mandatory review before the human gate
- artifact handoff is gated by explicit `approval_status`, not by prose reminders alone
- `review-change` and `implement-change` must return deterministic machine-checkable stop states instead of vague optional continuation
- `implement-change` treats an approved plan as one execution unit and should not stop mid-plan merely because one task completed
- `implement-change` should default to a one-time worktree preflight reminder before first implementation when still in the current checkout

Lower-plane skills support the kernel:
- session plane: `use-coding-skills`, `output-styles`
- truth plane: `analyze-project`, `organize-docs`
- evaluation plane: `review-design`, `review-plan`, and `review-implementation`, coordinated by the coding agent through `review-change`
- policy plane: guideline, standards, security, executable-oracle, and testing skills
- execution-support plane: git/worktree/fetch/registry helpers

Planning and ad hoc tooling stay separate: `plan-change` composes `language-decision-tree` only when a task introduces or replaces a persisted implementation boundary, while `tool-decision-tree` owns agent ad hoc command choice and composition. Language guideline skills apply after the implementation language is fixed; `go-guidelines` then selects its CLI-tool or API-service profile as appropriate.

Claude Code and Codex retain their repository-owned plugin marketplaces. Other coding agents may use `npx skills@latest add CsHeng/agent-skills` as optional consumer-managed guidance. Do not restrict selected targets or destinations, inspect duplicate exposure, promise coexistence, or manage external install/update/remove state. The 39 retained public IDs remain stable; `clean-architecture`, `quality-standards`, and `security-logging` are intentionally retired.

## Working Rules

- Keep the sovereign harness kernel as the only top-level authority.
- External workflow skills, including retired or third-party agent harnesses, may provide lower-plane technique guidance only; they must not override this repository's phase routing, approval gates, artifact locations, review defaults, or close judgment.
- Keep reusable behavior agent-agnostic by default. Skills should describe portable workflow contracts, not Codex-only, Claude-only, or UI-only prompt mechanics, unless the file is explicitly scoped to that agent surface.
- Prefer authored `src/skills/` plus direct references for reusable behavior. Keep agent-specific manifests, hooks, and install notes thin.
- Treat `use-coding-skills` as an optional router for ambiguous multi-stage work and session-boundary guidance; directly matched workflow and policy skills do not require it first.
- Keep discovery, phase-to-owner mapping, review evaluator selection, support routes, and host-wrapper limits in the installed `use-coding-skills/references/routing.toml` contract. User- or host-level AGENTS files may keep thin public-skill hints but must not become parallel harness truth.
- Positive trigger boundaries live in each skill's frontmatter `description`; routing trigger cases carry negative boundaries, overlays, and lexical hints, and keep explicit positive overrides only for explicit-invocation cases.
- Keep skills thin and operational.
- Treat `src/skills/`, `src/runtime/harness/`, and the contracts as authored truth. Refresh generated `skills/`; do not edit it by hand.
- Author activation only through `activation_mode` and `default_role` in `contracts/skills.toml`; derive provider metadata through the contract-level projection table, and do not restore per-skill invocation booleans or source-authored Codex invocation policy.
- Keep semantic case ownership, case boundaries, optional overlays, and non-authoritative lexical hints in the installed routing contract; do not duplicate them in host wrappers or prose.
- Prefer explicit validation and deterministic workflows over vague prompt guidance.
- Use `output-styles` as the shared conversational rendering baseline. Select one primary skill to own domain order and treat other matched skills as semantic overlays rather than independent report generators.
- Keep fixed output schemas inside the skill that owns a durable artifact or machine-consumed result; ordinary conversational skills should render only decision-relevant parts of their internal checklist.
- When documenting shell examples, do not teach interpolation of untrusted input.
- For review flows, keep reviewer, main-agent judge, and controller-owned fixer responsibilities separate; the Review System section below owns the detailed review defaults.
- Route review through `review-change` at the harness layer; treat `review-*` skills as lower-plane evaluators.
- Require delegated writers to use isolated worktrees from one dependency-frozen snapshot. Shared checkout is read-only only, and the main controller alone may integrate a batch and advance dependents after group convergence.
- Treat model policy as a runtime binding concern. `semantic-routing`, `inherit-main`, and `runtime-default` may change actor model/reasoning selection but must not change task IDs, dependencies, groups, limits, touch sets, isolation, locks, or oracles.
- Do not assume unattended execution.
- Treat task-ledger execution as lower-plane execution support under `implement-change`, not as a second top-level authority.
- Treat decision discovery as a bounded design-phase clarification loop, not as a new top-level workflow.
- New metadata-based plans should declare work-package readiness, executable oracle strategy, review budget, and subagent readiness before review.
- Design and plan review remain bounded by their human gates. Implementation repair belongs to `implement-change` and normally uses one initial bounded review plus one focused verification review, with at most one additional same-slice repair attempt.

## Documentation Skills

- Use `analyze-project` for read-only project explanation and drift detection.
- Use `sync-truth` when a verified change has real truth impact and stable truth must be updated.
- Use `organize-docs` as lower-plane stable-doc maintenance when truth sync changes docs boundaries or truth roots.

## Documentation Truth Boundary

- This repository uses a docs truth boundary.
- Long-lived project truth lives in root reference files plus stable `docs/` domains.
- `docs/plans/` is the single stage-artifact root in this repository and should stay out of default docs searches.
- Stable workflow truth belongs in `docs/architecture/workflow-orchestration.md`; generated diagrams remain subordinate to machine contracts.
- Use `docs/.ignore` and `docs/AGENTS.md` as the repository-local contract for docs search behavior.
- Use `rg --no-ignore` only when the user explicitly needs historical context from stage artifacts.

## Review System

`review-design`, `review-plan`, and `review-implementation` are lower-plane review skills used by the top-level `review-change` gate.

Key properties:
- the main coding agent chooses preferred subagent review or direct main-agent review without selecting an external reviewer tool
- a delegated reviewer receives only a bounded review brief and cannot delegate recursively
- review is evidence-based and causality-bound to the current artifact diff or task slice
- reviewers return candidate findings; the main agent adjudicates them before any repair
- `review-implementation` is a read-only evaluator; `implement-change` alone owns implementation repair, mutation, continuation, and typed exits
- `review-design` and `review-plan` default to boundary-focused review: architecture/surface/DAG/oracle/ownership/recovery-policy blockers only
- `review-implementation` reviews only the exact task diff, task tests, declared oracles, and justified direct dependencies
- moving or renaming unchanged code does not activate pre-existing defects
- low-confidence, pre-existing, unrelated, future-phase, and plan-expanding observations cannot become automatic repair
- focused verification checks accepted repairs and repair-introduced regressions without reopening repository-wide discovery

## Prerequisites

Required tools for validation and plugin management:
- `jq` (JSON linting)
- `plantuml` (PlantUML syntax checks and tracked SVG diagram rendering)
- GNU-compatible `realpath` with `--relative-to` support (coreutils on macOS)
- GNU/Homebrew Bash 4 or newer (runtime namerefs, associative arrays, `mapfile`, and syntax checks)
- `claude` CLI with plugin support
- `codex` CLI with plugin support

## Validation

After editing source skills, contracts, scripts, or architecture docs, regenerate and run the aggregate check:

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

`generate-workflow-diagrams.py` refreshes both the PlantUML sources and their tracked SVG renderings; `--check` (also run by `check.sh`) fails when either is stale. The optional pre-commit hook delegates to the same strict aggregate check and never regenerates or stages files.

The aggregate check validates the generated root-flat surface and standalone skill closure, then runs contract, index, diagram, Ruff, ty, pytest, and Markdown lanes once. `.dist/` remains ignored and untouched.

For Codex plugin metadata changes, also run:

```bash
uvx --with pyyaml python "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .
```

For sovereign harness surface changes, run the authored runtime pytest suite and generated standalone-closure checks through `bash scripts/check.sh`.

## Versioning

### Development Workflow (Pre-Release)

During active development before external release:

1. Make code/doc changes
2. Run validation
3. Uninstall and reinstall plugin:

```bash
claude plugin uninstall coding@csheng
claude plugin install coding@csheng
```

4. Restart Claude Code to apply changes

No version bump needed - changes are picked up from the local directory.

### Release Workflow (External Distribution)

When preparing for external release, keep these versions in sync:
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.codex-plugin/plugin.json`

Version bump procedure:

1. Update `.claude-plugin/plugin.json` `version`
2. Update `.claude-plugin/marketplace.json` plugin `version`
3. Update `.codex-plugin/plugin.json` `version`
4. Validate the plugin after the change
5. Update the installed local plugin in Claude and Codex

## Local Update Guide

This project is installed from a local directory marketplace, not a remote registry.

That means:
- the source of truth is this repo
- version bumps are metadata and install/update markers
- Claude does not fetch a remote package for this plugin
- after updating the installed plugin, Claude Code must be restarted to apply changes

Claude marketplace registration:

```bash
./install.sh
```

Plugin install:

```bash
claude plugin install coding@csheng
```

Plugin update after local changes:

```bash
claude plugin marketplace update csheng
claude plugin update coding@csheng
```

Verification:

```bash
claude plugin list
```

Expected result:
- `coding@csheng`
- desired version shown
- `Status: enabled`

After update:
- restart Claude Code to apply changes

Codex marketplace registration:

```bash
./install-codex.sh
```

Codex plugin update after local changes when the plugin install surface is in use:

```bash
uvx --with pyyaml python "$HOME/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py" .
codex plugin add coding@csheng
```

After update:
- start a new Codex thread to pick up refreshed plugin skills and metadata

Optional `npx skills` installations are owned by the consumer and upstream CLI. They do not replace the maintained Claude or Codex plugin paths, and this repository does not constrain or inspect their targets, layout, duplicate exposure, coexistence, update, removal, or cleanup behavior.

## Notes

The repository may also contain user-local `.claude/` state. Do not treat that as plugin source of truth.
