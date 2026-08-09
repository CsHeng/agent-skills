# Maintenance Contract

This repository keeps reusable coding-agent behavior in a structured source tree and generates flat compatibility surfaces for agent runtimes that expect one skill directory per skill.

## Source And Generated Surfaces

- `src/skills/**/SKILL.md` is the source of truth for model-facing skill behavior.
- `contracts/skills.toml` is the source of truth for skill exposure, category, lifecycle ownership, invocation policy, mutation permission, runtime-support exceptions, and pointers to install-required skill-local runtime contracts.
- `src/skills/session/use-coding-skills/references/routing.toml` is the install-required source for discovery, phase ownership, support routes, review evaluators, composition, and the host-wrapper boundary.
- `src/runtime/harness/` is the non-discoverable source for deterministic lifecycle, artifact-DAG, task-ledger, evaluation, recovery, truth-sync, and close runtime support.
- `skills/` is tracked generated root-flat compatibility output. Do not edit it directly.
- `.dist/claude/` and `.dist/codex/` are ignored, reproducible target-specific flat skill surfaces generated only when needed.
- `skills.index.json` is generated from `contracts/skills.toml`.
- `docs/architecture/diagrams/*.puml` are generated human views of the installed harness routing and implementation workflow contracts.
- Runner-owning generated skills carry a current `scripts/harness/` bundle. Runtime support is never exposed as a separate public skill.

Regenerate generated surfaces with:

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
```

Validate with:

```bash
bash scripts/check.sh
```

## Skill Change Requirements

Any skill addition, deletion, rename, or category change must update:

- `contracts/skills.toml`
- regenerated `skills.index.json`
- regenerated tracked install surface under `skills/`
- README inventory or architecture docs when the visible capability changes
- at least one check or fixture when behavior changes
- `docs/changelog/design-decisions.md` when policy or architecture changes

Do not hand-edit generated PlantUML files. Update the owning routing, lifecycle, workflow-mode, or controller-local contract, regenerate the diagrams, and review the resulting architecture view. See `workflow-orchestration.md` for truth precedence and diagram scope.

`bash scripts/check.sh` generates Claude and Codex surfaces in a temporary directory and validates them there. Generate `.dist/` explicitly only for local packaging or external-consumer inspection; it must stay ignored and untracked.

Claude Code and Codex plugin marketplaces are maintained repository surfaces. Optional `npx skills` use by other agents is consumer-managed guidance only: repository checks do not select targets, inspect destinations or duplicate exposure, guarantee coexistence, or own installation lifecycle operations.

## Lifecycle Authority

- Only `category = "workflow"` may set `lifecycle_owner = true`.
- Exactly one non-lifecycle session skill owns the installed `routing_contract`; direct matches bypass it, while ambiguous multi-stage routing may enter it.
- Lower-plane skills may provide method, policy, checks, or tool support, but they must not approve, execute, or close lifecycle state.
- Mutation-capable skills must require an explicit user request or an approved upstream artifact.
- Manual tools such as `smart-squash` and `git-worktrees` must never be implicitly invoked.
- Intent-gated mutation tools such as `smart-commit` may allow model selection only when their description requires an explicit user request for both semantic diff grouping and local commit creation; generic commit, diff, status, and history-cleanup requests must not match.
- `implement-change` treats an approved plan as one execution unit.
- `plan-change` owns the versioned task DAG, named parallel-batch authorization, delegation eligibility, portable execution/reasoning profiles, isolation, locks, and convergence metadata.
- `implement-change` owns runtime actor and profile binding. It may execute an explicitly approved dependency-frozen batch conditionally, but it must preserve the approved topology and use typed serial fallback, capacity stop, or conflict evidence.
- Delegated writers require isolated worktrees from one dependency-frozen snapshot; shared checkout is read-only, and only the controller may converge a complete group and advance its dependents.
- `implement-change/references/workflow.toml` travels with the installed controller and owns its invocation subgraph; repo-global architecture docs are the maintenance view, not the only runtime copy.
- `use-coding-skills/references/routing.toml` travels with the installed router and owns phase-to-workflow and support-route mapping; host AGENTS files remain user-specific wrappers rather than parallel harness truth.
- Truth-affecting version-2 plans must declare stable truth refs inside the immutable implementation touch set and supported docs-governance predicates; missing legacy scope fails closed with a typed plan route.
- Direct `sync-truth` or `organize-docs` mutation requires an explicit user request. Controller mutation is a separate authority that requires an approved plan plus immutable execution evidence with exact design, plan, task-ledger, review, verification, touch-set, and stable-ref identity.
- `organize-docs` is never implied by a Markdown suffix or truth sync alone. It composes only for a declared supported predicate and remains bounded to the exact stable refs selected by `sync-truth`.
- `close-change` is a read-only judgment gate. It accepts no caller status booleans, requires the exact approved truth artifact when truth sync is required, and terminates at `closed` with no successful self-route or automatic merge, release, cleanup, commit, push, install, or deploy action.

## Review Invariants

- Review is agent-native and tool-agnostic: prefer one reviewer subagent for non-trivial work and allow direct main-agent review for small mechanical changes or unavailable delegation.
- A delegated reviewer receives a bounded review brief, cannot delegate recursively, and returns candidate findings only.
- The review brief contains the approved task slice, exact diff, executable oracles, touch set, and justified supporting files.
- Candidate blockers require qualifying change causality and an explicit approved-contract violation.
- The main agent adjudicates every material candidate; severity or reviewer scope labels alone never authorize repair.
- `review-implementation` is read-only and cannot invoke lifecycle workflows or mutate implementation.
- `implement-change` owns implementation repair: initial bounded review, focused verification, and at most one additional same-slice repair attempt for an incomplete or regressive repair.

## Safety And Evidence

- No unattended execution by default.
- Human approval gates remain authoritative.
- Fresh evidence is required for completion claims.
- Regulated changes must declare a recovery surface and default to fix-forward. Guarded rollback requires an explicit tested trigger, target, and verification; regulated classification alone never authorizes it.
- Repo-owned docs, code, scripts, tests, and skills are durable truth.
- Memories, summaries, logs, sessions, and caches are not durable truth unless explicitly promoted.

## Environment-Specific Content

Generally installed skills may contain personal engineering style and opinionated local-first defaults, but must avoid host-specific paths, private project names, private token names, unguarded OS-specific commands, and required provider-specific model names. Portable routing uses semantic execution/reasoning profiles; provider model names and user-global concurrency defaults remain runtime configuration outside repository truth.
