# Design Decisions

## 2026-08-09 - Evidence-Bound Truth Sync Before Terminal Close

### Failure Mode

`close-change` could be approved before a truth-affecting implementation synchronized stable project truth, after which the controller discovered missing documentation and routed backward. Close eligibility also depended on caller-supplied status flags, successful close routed to itself, and documentation organization could appear to be an unconditional part of truth sync.

### Change

- Require truth-affecting version-2 plans to declare bounded stable truth refs and structured docs-governance predicates.
- Bind execution evidence to the exact approved design and plan, canonical converged task ledger, review and verification references, allowed touch set, and stable truth refs.
- Continue passing truth-affecting implementation into controller-authorized `sync-truth` preparation before close and stop at one explicit human truth approval gate.
- Keep direct mutation authority distinct from approved-controller authority and compose `organize-docs` only for a declared supported predicate inside the same stable truth touch set.
- Make `close-change` derive eligibility from exact artifacts, reject caller status overrides, and return terminal `closed` with no successful self-route.

### Operational Impact

- Implemented behavior and stable documentation converge before close approval, so close never needs to discover missing truth and route backward.
- Simple stable-fact updates do not trigger repository-wide docs organization; only the declared bounded governance need activates it.
- Close remains judgment-only and does not imply merge, release, cleanup, commit, push, plugin install, distribution, or deploy.

## 2026-08-07 - Native Provider Plugins And Advisory Agent Skills Distribution

### Failure Mode

Extending repository-owned install, update, removal, symlink, destination, duplicate-detection, and coexistence logic to every coding agent would make the project responsible for unstable external layouts. At the same time, the generated `_harness-libs` pseudo-skill made individual workflow installation depend on a sibling directory, and Claude-only command wrappers duplicated behavior already owned by public skills.

### Change

- Keep the maintained Claude Code and Codex marketplace/plugin paths.
- Keep all public skill names unchanged and publish the generated root `skills/` tree as the shared portable payload.
- Present `npx skills@latest add CsHeng/agent-skills` only as optional consumer-managed guidance for other agents.
- Do not restrict selected agents, scopes, destinations, or copy/symlink modes; do not detect duplicate exposure or guarantee coexistence.
- Move deterministic runtime source to non-discoverable `src/runtime/harness/` and bundle it into each runner-owning skill at `scripts/harness/`.
- Retire the active Claude command surface after its durable behavior is absorbed into public skills, retaining only inert history outside discovery.

### Operational Impact

- Repository acceptance covers public identities, semantic requirements, package closure, owner-local runtime, both native plugins, and command retirement. It does not execute or police external installation state.
- Consumers and the upstream CLI own optional external selection, installation, updates, removal, cleanup, duplicates, and coexistence.
- Portable skill resources use skill-relative paths; a universal provider-supplied `$PLUGIN_ROOT` or `$SKILL_ROOT` environment variable is not part of the contract.
- The approach follows the [Agent Skills](https://agentskills.io/) shape and learned from [mattpocock/skills](https://github.com/mattpocock/skills), the [`skills` CLI](https://github.com/vercel-labs/skills), [Codex Skills](https://developers.openai.com/codex/skills/), and [Superpowers](https://github.com/obra/superpowers). Local contracts remain authoritative.

## 2026-08-01 - Repo-Owned Harness Routing And User-Specific Host Wrapper

### Failure Mode

The repo owned lifecycle, mode, skill-exposure, and implementation-controller contracts, but intent-to-skill routing remained partly duplicated in a user-global Codex AGENTS file. That made the installed harness incomplete as a standalone artifact, allowed host routing to drift from `review-change` authority, and left no complete generated sequence for comparing expected and observed routing.

### Change

- Add an install-required `use-coding-skills/references/routing.toml` contract for native-match bypass, ambiguity routing, phase-to-workflow ownership, review evaluators, support routes, composition, and host-wrapper limits.
- Generate `docs/architecture/diagrams/harness-routing-sequence.puml` from the routing contract plus lifecycle and workflow-mode contracts.
- Keep `use-coding-skills` optional: direct specific matches bypass it, while ambiguous multi-stage and explicit routing requests enter it.
- Route implementation review through `review-change`; `review-implementation` remains a bounded evaluator.
- Reduce the user-global Codex AGENTS file to personal preferences, local-home policy, and a thin pointer to the repo-owned routing surface.
- Replace over-broad cross-language prescriptions with a smallest-durable implementation, compatibility, dependency, and temporary-mechanism policy in `development-standards`.

### Operational Impact

- The installed skill surface now carries the routing decisions required to understand the harness without reading host-global state.
- Maintainers can regenerate and inspect one end-to-end sequence to find drift in discovery, mode selection, phase ownership, approval gates, review layering, truth sync, and close.
- Host wrappers can vary by user or runtime without redefining lifecycle behavior.
- Contract validation rejects missing phase routes, non-workflow phase owners, invalid review evaluators, unknown support targets, and multiple routing-contract owners.

## 2026-08-01 - Portable Conditional Parallel Subagent Routing

### Failure Mode

Planning recorded a mostly serial task list, while implementation had no deterministic contract for exposing a complete ready frontier, binding safe tasks to subagents, preserving topology across model choices, or stopping when isolation and runtime capacity were insufficient. This left useful parallelism implicit and encouraged provider-specific routing advice outside the approved plan.

### Change

- Make version-2 plans own the portable task DAG, named dependency-frozen batches, delegation eligibility, semantic execution and reasoning profiles, isolation, write sets, resource locks, batch limits, and convergence tasks.
- Let `implement-change` bind that unchanged topology at runtime through `semantic-routing`, `inherit-main`, or `runtime-default`.
- Validate the public ledger against the approved plan, select only conflict-free ready members, and return typed serial fallback, capacity stop, or parallel-conflict evidence.
- Require isolated worktrees for delegated writers and controller-owned complete-group convergence before external dependents advance.

### Operational Impact

- Execution stays serial-first unless the approved plan and human gate explicitly authorize a safe named batch.
- A user may inherit the main agent's model and reasoning choice without changing whether approved tasks run serially or in parallel.
- Semantic profiles remain vendor-neutral; concrete model names and session concurrency defaults stay in runtime or user configuration.
- Allowed batches degrade conservatively to serial execution, while required batches fail closed when effective capacity is insufficient.

## 2026-07-23 - Allow Intent-Gated Smart Commit Discovery

### Failure Mode

Requiring an explicit `$smart-commit` invocation prevented Codex from selecting the workflow when the user had already asked to group a mixed working tree into focused commits by business domain.

### Change

`smart-commit` is now a model-selectable tool whose description requires both semantic diff grouping and local commit creation intent. Generic commit requests, diff inspection, status reporting, and history cleanup remain outside its trigger boundary, while `requires_explicit_user_request = true` continues to guard repository mutation.

### Operational Impact

- Users may request domain- or business-purpose commit grouping in natural language without naming the skill.
- Once that intent matches, eligible local commits execute automatically after exclusion checks, as before.
- Explicit `$smart-commit` and `/smart-commit` entry points remain supported.
- The workflow still never pushes and still stops for tracked or staged content that appears unsafe to version.

## 2026-07-07 - Structured Source Tree And Generated Install Surfaces

### Failure Mode

The flat skill directory made source ownership, install compatibility, and runtime support look like one undifferentiated surface.

### Change

Skill source moved under `src/skills/`, while the tracked runtime compatibility surface is generated into `skills/` and external install surfaces can be generated into `.dist/claude/` and `.dist/codex/`.

### Operational Impact

- Edit `src/skills/**`, not generated `skills/**`.
- Regenerate the tracked surface with `python3 scripts/flatten-skills.py --target root-flat`.
- Validate with `bash scripts/check.sh`.

## 2026-07-10 - Keep External Install Surfaces Reproducible

### Failure Mode

Tracking `.dist/` duplicated the structured source and root-flat runtime surface, expanded ordinary diffs, and made validation depend on committed packaging output that no current manifest or install path consumes.

### Change

Keep `skills/` as the tracked generated runtime compatibility surface. Ignore `.dist/` and generate Claude and Codex external surfaces only on demand. Aggregate validation now generates those external targets in a temporary directory.

### Operational Impact

- A fresh clone can validate external install surfaces without a pre-existing `.dist/` tree.
- `bash scripts/check.sh` rejects tracked `.dist/` files.
- Packaging or inspection may still run `python3 scripts/flatten-skills.py --target claude` or `--target codex` explicitly.

## 2026-07-07 - External Skill Contracts

### Failure Mode

Putting invocation and exposure rules in prompt text would mix machine-readable governance with model-facing instruction content.

### Change

`contracts/skills.toml` now owns skill source paths, public IDs, categories, lifecycle ownership, install exposure, and mutation guards.

### Operational Impact

- `SKILL.md` files stay prompt content.
- Contract drift is checked by `scripts/check-contracts.py`.
- `skills.index.json` is generated from the contract.

## 2026-07-07 - Remove Provider-Switching Review From Skill Layer

### Failure Mode

Provider-switching review expanded the harness failure surface and could create false confidence from mismatched external reviewer behavior.

### Change

Review is now same-driver by design. Provider switching is out of scope for the skills layer and belongs to a separate router or agent if it is reintroduced later.

### Operational Impact

- Review runners report `review_mode = same-driver`.
- External review reports may be attached as passive evidence.
- Active docs, commands, and skills must not advertise provider-switching review.

## 2026-07-07 - Workflow Modes Before Phase Implementation

### Failure Mode

The design-strength split carried too much routing responsibility.

### Change

`contracts/workflow-modes.toml` defines `read_only`, `micro`, `standard`, `regulated`, and `emergency` modes before phase implementation.

### Operational Impact

- `design-change` remains a phase implementation.
- Workflow mode selection decides whether design, plan, review, rollback, and fresh evidence gates apply.

## 2026-07-10 - Native Skill Composition And Controller-Owned Repair

### Failure Mode

An unconditional session router duplicated Codex native discovery, public names obscured controller/evaluator hierarchy, and installed controller skills could not see the repo-global invocation contract. Detailed repair mechanics also remained in the review component even though the execution workflow was documented as lifecycle owner.

### Change

- Rename `execute-change` to `implement-change` and `review-code-impl` to `review-implementation`.
- Keep `review-implementation` read-only and move implementation repair ownership into `implement-change`.
- Install `references/workflow.toml` and `references/repair-loop.md` with the controller.
- Make `use-coding-skills` optional so workflow and policy skills compose through native description matching.

### Operational Impact

- Contract validation checks installed workflow nodes, edges, cycles, evaluator direction, and unique repair ownership.
- Implementation repair expects convergence within five rounds and stops at ten.
- `agents/openai.yaml` remains product metadata; runtime graph contracts live under directly linked `references/`.
- `docs/architecture/workflow-orchestration.md` is the stable maintenance view of lifecycle, DAG, and repair semantics.
- PlantUML views are generated from the installed controller contract and checked for drift by the aggregate validation path.

## 2026-07-10 - Shared Rendering Baseline And Semantic Output Deltas

### Failure Mode

Domain skills could duplicate generic response-shape rules and expose every internal analysis axis as a mandatory section. In practice, `analyze-project` loaded alongside `output-styles` still produced a low-density eight-section report for a narrow operational question.

### Change

- Make `output-styles` the shared conversational rendering baseline.
- Select one primary skill to own the response's domain order and conclusion.
- Treat other matched skills as semantic overlays rather than independent report generators.
- Make `analyze-project` selectively terse by default and move its comprehensive audit shape into a conditionally loaded reference.

### Operational Impact

- Narrow project-state answers render only relevant facts, boundaries, risks, and actions.
- Full truth maps remain available for explicit comprehensive audit requests.
- Durable artifacts and machine-consumed schemas keep their specialized output contracts.
- Installed skill surfaces carry the same ownership and rendering rules after regeneration.

## 2026-07-11 - Bounded Agent-Native Review

### Failure Mode

External semantic review runners selected a reviewer process, built exhaustive prompts, normalized severity into blocking state, and encouraged repeated repository-wide discovery. Findings did not require a causal link to the current task diff, so moved legacy code and pre-existing adjacent debt could expand an approved implementation plan.

### Change

- Retire external semantic review runners, provider adapters, reviewer schemas, and runner-specific eval/smoke infrastructure.
- Let the current coding agent prefer one reviewer subagent for non-trivial bounded review or review directly for small mechanical work.
- Require a bounded review brief with the approved task slice, exact diff, oracles, touch set, and justified supporting files.
- Require change causality and an approved-contract violation for blocker eligibility.
- Keep final finding disposition and repair authority with the main agent.
- Move deterministic artifact-DAG support under `_harness-libs`.

### Operational Impact

- Review skills remain portable because they describe agent roles without selecting a model, provider, or external reviewer command.
- Moving or renaming unchanged code does not activate pre-existing defects.
- Only main-agent `accepted` findings enter controller-owned repair.
- Normal implementation review uses one initial bounded review and one focused verification review, with at most one additional same-slice repair attempt.
- `test-agent-native-review.sh` and `test-artifact-dag.sh` replace external reviewer-runner smoke coverage.

## 2026-07-26 - Fix-Forward Recovery Policy

### Failure Mode

Regulated mode, plan metadata, infrastructure guidance, and failure-count routing collectively encouraged agents to synthesize rollback machinery for ordinary verification failures. Repeated failures could widen implementation into dependency freeze, plan, and design without evidence that those boundaries were wrong.

### Change

- Replace the regulated rollback requirement with an explicit recovery surface and `fix_forward` default.
- Require every new task to select `fix_forward`, `stop_and_diagnose`, or `guarded_rollback`.
- Permit guarded rollback only with an exact tested trigger, target, and verification.
- Route failure classes by evidence and keep failure count observational; count alone never widens the lifecycle phase.

### Operational Impact

- Backups, snapshots, retained releases, HA peers, and VRRP are recovery evidence rather than rollback authorization.
- Ordinary correctness and deploy-verification failures stay in diagnose, repair, and narrow re-verification.
- Replan requires proof that the task graph or touch set is insufficient; redesign requires proof that the approved boundary is invalid.
