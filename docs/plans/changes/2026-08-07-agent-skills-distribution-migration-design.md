# Agent Skills Hybrid Distribution Design

## Status

Approved design version 3 for retaining the mature Claude Code and Codex plugin marketplaces while presenting `npx skills` as optional long-tail guidance for other coding agents. This version supersedes the collision-enforced version 2 and the earlier full-plugin-retirement and `csheng-*` rename proposal.

## Problem

The repository already has working Claude Code and Codex plugin manifests, local marketplaces, target generation, and installation helpers. Replacing those official distribution paths with generic filesystem installation would discard mature integration that both providers support and recommend for reusable skill bundles.

At the same time, adding a repository-owned installer, path map, update flow, remove flow, symlink policy, coexistence matrix, or duplicate detector for every additional coding agent does not scale. The `skills` CLI and each consumer own those installation decisions. This repository only publishes a portable skill payload and optional `npx skills` guidance; it does not restrict targets, inspect destinations, or promise that independently installed copies coexist.

The current deterministic lifecycle runtime is also exposed as a sibling generated skill named `_harness-libs`. That works only when a host installs the complete flat tree and preserves sibling paths. A user who selects one workflow with `npx skills` receives only that skill directory, so a reference such as `../_harness-libs/plan-runner.sh` is not an independently installable skill contract.

Path wording has drifted between plugin-root variables, skill-root variables, repository-relative paths, and absolute-path placeholders. The Agent Skills specification defines resources relative to the skill directory, but it does not define a host-injected `$SKILL_ROOT` environment variable. Portable skills must distinguish their own installed directory from the target repository without depending on an ambient provider variable.

Claude command docs duplicate lifecycle behavior that now belongs in source skills. Most coding agents do not consume `commands/`, and retaining that surface would keep a second behavior owner even though the Claude plugin itself remains supported.

## Goals

- Retain the Claude Code and Codex plugin marketplaces, manifests, target generation, and installation helpers as two explicitly owned provider exceptions.
- Present `npx skills@latest` as optional guidance for Claude/Codex-external agents without adding repository-owned install, update, remove, path, symlink, coexistence, or duplicate-detection adapters.
- Keep existing public skill names unchanged; do not add a `csheng-` prefix solely for collision avoidance.
- Keep `src/skills/`, machine contracts, generation, runtime behavior, and repository validation owned here.
- Make every public skill physically self-contained, including any scripts, references, assets, or lifecycle runtime it requires, and make cross-skill semantic dependencies explicit.
- Establish one portable path contract based on relative skill resources and self-locating scripts, without requiring ambient `$PLUGIN_ROOT` or `$SKILL_ROOT` variables in reusable skills.
- Merge still-required command-only lifecycle behavior into the owning workflow skills before archiving `commands/`.
- Add an explicit README acknowledgement that early harness ideas were influenced by [Superpowers](https://github.com/obra/superpowers).
- Preserve deterministic repository checks for the authored and generated skill payload without making external CLI destination behavior a repository gate.

## Non-Goals

- Do not replace the Claude Code or Codex plugin installation paths with `npx skills`.
- Do not prohibit consumers from selecting any `npx skills` target; provider-plugin recommendations are guidance, not enforcement.
- Do not detect, prevent, or guarantee coexistence between plugin-installed, copied, or symlinked skill instances.
- Do not invent or maintain a parallel all-agent destination matrix or an arbitrary destination wrapper around `npx skills`.
- Do not rename public skills, fork plugin and generic identities, or use naming differences to conceal semantically duplicate installations.
- Do not maintain a list of read-only alternatives for arbitrary shell commands.
- Do not claim that the `skills` CLI resolves semantic dependencies or that every arbitrary single-skill selection is a complete harness installation.
- Do not make `npx skills@latest` or another network call part of every offline aggregate repository check.
- Do not update workstation-global skill state, plugin registries, or agent configuration during implementation.
- Do not include the separately proposed all-repository `skill-miner` behavior change or unrelated homelab documentation repair in this migration.

## Change Classification

- request_kind: change-definition
- change_class: C
- design_strength: design-full
- truth_impact: high
- boundary_impact: high
- recommended_next_phase: design-full
- truth_sync_required: true
- parallel_candidate: false

## Research Basis

- The [Agent Skills specification](https://agentskills.io/specification) defines a skill as a directory containing `SKILL.md` plus optional `scripts/`, `references/`, and `assets/`; it requires the frontmatter name to match the parent directory and resolves file references from the skill directory.
- The current [Codex skill documentation](https://developers.openai.com/codex/skills) says Codex scans repository and user `.agents/skills`, follows symlinked skill folders, does not merge same-named skills, and prefers plugins for reusable distribution.
- The current [skills CLI](https://github.com/vercel-labs/skills) exposes agent, global, and copy options but no arbitrary destination option. In symlink mode it first copies into canonical `.agents/skills`; in copy mode it writes directly to the selected agent's configured destination. Some agents still use `.agents/skills` as that direct destination.
- [mattpocock/skills](https://github.com/mattpocock/skills) uses `npx skills@latest`, relative links such as `scripts/...`, and bundled resources. Its reusable skills do not establish a universal `$SKILL_ROOT` or `$PLUGIN_ROOT` environment contract.
- [obra/superpowers](https://github.com/obra/superpowers) prefers official plugin installation where a harness provides it, including Claude Code and Codex, and documents separate installation per harness rather than one shared local-skill path.
- These upstreams are distribution and portability references, not lifecycle authorities. This repository keeps its own approval, review, artifact, recovery, and close contracts.

## Boundaries

- in_scope:
  - Retain and validate `.claude-plugin/`, `.codex-plugin/`, `.codex-marketplace/`, `install.sh`, `install-codex.sh`, and their supporting provider-specific code.
  - Keep the generated root `skills/` tree as the shared public payload used by plugin manifests, local authoring exposure, and `npx skills` discovery.
  - Keep `npx skills` guidance advisory and leave target selection, destination resolution, duplicate exposure, and cleanup to the consumer and upstream CLI.
  - Move deterministic harness runtime source out of the discoverable skill inventory and bundle a closed runtime copy inside each workflow skill that executes a runner.
  - Validate every generated public skill as a self-contained installation unit.
  - Integrate command-only lifecycle semantics into owning workflow skills, then archive all command docs.
  - Retain Claude-specific hooks as provider adapter behavior while keeping provider-root variables out of reusable skills.
  - Rewrite active installation, maintenance, architecture, quickstart, and repository-agent documentation around the three-lane hybrid model.
  - Credit Superpowers in README and record both community references in the stable portability rationale.
- out_of_scope:
  - Modify user-global installations or validate against live user agent sessions.
  - Add provider-specific plugin packages for agents other than Claude Code and Codex.
  - Preserve active deprecated commands or create a replacement scanner for `check-secrets.md`.
  - Detect, reject, clean up, or guarantee coexistence for consumer-managed installations.
  - Change lifecycle approval semantics, review budgets, recovery policy, or controller ownership except where command-only text must move to its existing owner.

## Architecture Decision

- architecture_decision_id: ASD-001-hybrid-agent-skills-distribution
- decision_status: selected
- decision_horizon: The next public distribution boundary, until Claude Code or Codex deprecates its plugin path, or the `skills` CLI provides an enforceable non-overlapping destination/profile contract.
- current_demand: The repository must retain mature official integration for Claude Code and Codex while serving additional coding agents without maintaining one installation lifecycle per provider.
- constrained_resource: Maintainer capacity for provider-specific packaging and path churn beyond the two mature plugin surfaces.
- hard_requirements:
  - Preserve the repository-owned sovereign lifecycle, review, artifact, and recovery contracts.
  - Keep Claude Code and Codex plugin installation first-class.
  - Avoid making claims about the safety or coexistence of consumer-managed installations.
  - Keep every installed skill's physical resources and executable runtime inside its own directory.
  - Avoid user-global mutation during repository validation.

### Options

- status_quo: Keep only Claude Code and Codex plugin coverage plus workstation-specific local symlink guidance. Rejected because it leaves all additional coding-agent installation paths with consumers and provides no tested portable distribution lane.
- full_generic_replacement: Retire both plugins, publish renamed `csheng-*` skills, and use `npx skills` for every agent. Rejected because it discards mature official plugin lifecycle, introduces an unnecessary breaking rename, and can still create duplicate semantic capabilities across host discovery paths.
- selected_structural_option: Keep Claude Code and Codex plugins as bounded maintained exceptions, publish unchanged portable skill identities through the shared generated payload, and document `npx skills` only as an optional consumer-managed long-tail installation mechanism.
- deferred_option: Add and maintain native plugin packaging for every supported coding agent. Deferred because it recreates the unbounded provider-maintenance cost this change is meant to avoid.

### Economics And Ownership

- marginal_tradeoff: Maintaining two provider adapters costs more than one generic distribution, but preserves official lifecycle and avoids shifting Claude/Codex users onto a weaker local-file installation path. The long tail remains outsourced to the external CLI.
- opportunity_cost: The repository must keep two plugin validation paths and cannot guarantee how optional external installations interact, but avoids a repository-wide public rename and avoids maintaining dozens of provider destinations.
- repository_owner: Owns authored skills, the two plugin adapters, semantic dependency metadata, generation, bundled-runtime parity, offline checks, and stable documentation.
- skills_cli_owner: Owns agent detection, destination selection, project/global semantics, copy or symlink behavior, installed-state tracking, update, and removal for long-tail installations it creates.
- consumer_owner: Owns selecting agents and scopes, accepting the destination and copy/symlink behavior shown by `npx skills`, resolving duplicate exposure, and cleaning up consumer-managed installations.
- cost_bearer: Repository maintainers bear the two mature plugin surfaces and shared payload checks; the external CLI project bears long-tail provider-path churn; consumers bear installation and coexistence choices.
- comparative_advantage: Claude Code and Codex own their plugin lifecycle, the external CLI tracks broad agent destinations, and this repository alone owns harness semantics and package closure.

### Reversible Increments And Triggers

- reversible_increments:
  - Record the advisory hybrid distribution contract without changing public names or removing any active surface.
  - Close runtime packaging and prove command semantic parity while plugins and commands remain active.
  - Prove both plugin surfaces and the closed standard skill payload before archiving commands.
- executable_oracle: Offline contract/generation checks, provider-native manifest validation, public inventory and self-contained-package validation, active command adapter execution, and arbitrary-working-directory bundled-runner execution.
- recovery_boundary: Fix forward inside repository source, generated output, tests, commands, and docs. Stop before command archival if plugin validation, runtime closure, or active command parity fails.
- upgrade_triggers:
  - Revisit a generic-only model if Claude Code or Codex removes plugin support or official guidance stops preferring plugins for reusable bundles.
  - Revisit runtime vendoring when measured generated duplication becomes the dominant repository size or validation cost, or when all supported installers can preserve a verified shared dependency atomically.
  - Add another provider plugin only when a demonstrated required capability cannot be delivered through the standard portable payload and its lifecycle owner and acceptance test are explicitly approved.

## Decisions

### Distribution Lanes

Claude Code uses `.claude-plugin/`, its marketplace manifest, and the existing Claude installation flow. Codex uses `.codex-plugin/`, `.codex-marketplace/`, and the existing Codex installation flow. These are first-class maintained exceptions, not deprecated compatibility shims.

Other coding agents may use `npx skills@latest` against `CsHeng/agent-skills`. The minimal guidance delegates agent, scope, and copy/symlink choices to the upstream CLI and consumer:

```bash
npx skills@latest add CsHeng/agent-skills
```

The repository does not wrap, constrain, preflight, or inspect this command. It does not maintain an agent allowlist or destination matrix and does not infer coexistence from `--global`, `--copy`, symlink mode, or any resolved path.

### Consumer-Managed Installation Boundary

Claude Code and Codex plugin installation remain the maintained repository paths for those providers. `npx skills` is separate advisory guidance, not a third repository-owned installer contract.

- The repository does not reject any agent, scope, destination, copy mode, symlink mode, or duplicate exposure selected by the consumer.
- The repository does not inspect existing user-global or project-local skill state before provider plugin installation.
- The repository does not promise that two active copies are deduplicated, merged, ordered, or conflict-free.
- The consumer and upstream CLI own installation state, coexistence decisions, update, removal, and cleanup.
- Documentation may warn that multiple installations can expose duplicate capabilities, but warnings are informational and never an enforced gate.

### Public Naming

All source directories, frontmatter names, contract `public_id` values, generated directories, routing references, and docs retain their current names. Plugin surfaces may render a provider namespace such as `coding:plan-change`, but that host presentation is not a second portable skill identity.

Public names are not prefixed to solve hypothetical overlap. Consumers choose which same-purpose skills to install; a future prefix still requires a separately approved identity migration.

### Skill Root Contract

The term `skill root` means the installed directory that contains the activated `SKILL.md`. It is a path concept, not a guaranteed environment variable.

- `SKILL.md` links and resource references use paths relative to that skill root and do not traverse to sibling skills.
- Bundled executables locate their own directory with language-native mechanisms such as `BASH_SOURCE`, `$0`, or `__file__`, then resolve sibling resources from there.
- Instructions name the target repository separately and derive it from repository context such as `git rev-parse --show-toplevel` when Git is required.
- When an agent must turn a bundled relative resource into an absolute command path before changing directories, it may explicitly bind a local `SKILL_ROOT` value to the activated skill directory. No instruction may assume the host exported `$SKILL_ROOT`.
- `$CLAUDE_PLUGIN_ROOT` may remain inside the Claude-specific adapter and hook. `$PLUGIN_ROOT`, `$CLAUDE_PLUGIN_ROOT`, and other provider roots are forbidden in reusable skill instructions.
- Acceptance executes bundled helpers from an unrelated target working directory so accidental repository-relative lookup fails.

### Runtime Closure

The source runtime moves from `src/skills/_internal/_harness-libs/` to a non-discoverable `src/runtime/harness/` ownership root. Its smoke tests remain repository tests and are excluded from published skill packages.

Each workflow that invokes deterministic lifecycle tooling declares a runtime bundle in `contracts/skills.toml`. Generation copies the required production harness runtime under that skill's `scripts/harness/` directory. The workflow invokes its local copy using the skill-root contract. Generated duplication is accepted in exchange for independent installation and deterministic closure; authored runtime truth remains singular.

The generator rejects a published skill that references a physical resource outside its own generated directory or whose bundled runtime is stale. `_harness-libs` is removed from public discovery and from `skills.index.json`, while both plugin manifests continue to consume the resulting closed `skills/` tree.

### Semantic Composition

Physical closure and semantic composition are separate contracts. `contracts/skills.toml` declares direct `semantic_requires` edges for mandatory cross-skill behavior, and validation rejects unknown targets, invalid cycles, or stale routing references.

The supported sovereign harness profile installs the complete public inventory. Selective long-tail installation is supported only when the consumer installs the declared transitive semantic closure; leaf skills with no mandatory dependency remain valid individual selections. The generated index exposes direct and transitive requirements without pretending that `npx skills` resolves them.

### Command Retirement

Before archival, compare every `commands/*.md` file with its owning skill:

- Merge unique lifecycle schemas, runner invocation, gate, typed-exit, and execution-continuity behavior from the sovereign workflow commands into their existing skill owners or direct references.
- Confirm `analyze-project` and the three lower-plane review commands contain no unique required behavior before archival.
- Preserve any still-required target-repository scoping from `smart-commit.md` in `smart-commit`.
- Archive `check-secrets.md` without creating a replacement because a command-doc prompt is not an adequate scanner contract.

Move command history under `archived/commands/`. The Claude plugin remains active as a skill plugin, but its slash-command compatibility surface is retired. Active routers, docs, diagrams, checks, and smoke tests must not load or assert archived commands.

### Provider Adapter Retention

Keep `.claude-plugin/`, `.codex-plugin/`, `.codex-marketplace/`, `install.sh`, `install-codex.sh`, `scripts/install.sh`, Claude post-edit hooks, repository Git hooks, and target-specific temporary generation active. Provider-only variables remain confined to those adapters.

Validation must continue generating Claude and Codex install surfaces in temporary directories. The tracked root `skills/` projection remains shared payload truth and is refreshed from `src/skills/`; it is not edited by hand.

### Validation Layers

Offline aggregate validation remains authoritative for source/contract bijection, unchanged public identities, Agent Skills frontmatter, cross-skill references, generated freshness, bundled-resource closure, script syntax, plugin manifests, smoke tests, diagrams, and active-doc drift.

External `npx skills` installation behavior is not an implementation or release gate. Repository validation proves the standard skill directory shape, generated inventory, semantic metadata, and physical closure that optional external consumers receive; upstream destination behavior remains outside repository acceptance.

### Transition And Documentation

There is no public-name migration. Existing Claude plugin users remain on the Claude plugin, and existing Codex plugin users remain on the Codex plugin.

Active docs distinguish maintained provider plugins from optional consumer-managed installation. They may describe duplicate exposure as a user consideration, but they do not require cleanup, run detection, or provide an uninstaller.

README presents two maintained plugin lanes plus optional `npx skills` guidance for other agents. It makes consumer ownership and the absence of coexistence guarantees explicit, and credits Superpowers as an early source of harness inspiration while preserving local contract authority.

## Acceptance Conditions

- Claude Code and Codex manifests, marketplaces, installers, and generated temporary target surfaces remain active and pass their existing plus provider-native validation.
- No public source directory, frontmatter name, contract ID, generated directory, or routing reference receives a `csheng-` prefix.
- Repository-owned generation and index checks expose the intended unchanged public inventory and never expose a runtime-support pseudo-skill; any external `npx skills --list` exercise is optional informational evidence outside implementation and release acceptance.
- Installing one workflow skill alone includes every runner and physical library it needs within that skill directory.
- The complete-inventory harness profile satisfies every declared transitive `semantic_requires` edge.
- A representative bundled helper succeeds from a target working directory unrelated to the repository or installed skill path.
- Reusable skill content has no assumed `$PLUGIN_ROOT`, `$CLAUDE_PLUGIN_ROOT`, or ambient `$SKILL_ROOT`; any `SKILL_ROOT` shell variable is visibly assigned before use.
- `commands/` no longer exists as an active top-level surface; retained history is under `archived/commands/` and absent from active docs and checks.
- README documents the maintained plugin lanes, advisory `npx skills` usage, consumer-owned coexistence, unchanged public names, and Superpowers acknowledgement.
- Generated index and architecture diagrams reflect plugin retention, command retirement, runtime closure, and long-tail distribution.
- Required generators, focused harness smoke tests, plugin validators, `bash scripts/check.sh`, and `git diff --check` pass with no unrelated tracked drift.

## Recovery Policy

Use fix-forward for source, generator, runtime-bundle, provider-adapter, command-adapter, documentation, or validation defects. Implementation does not mutate installed user state. If plugin validation, physical closure, or command parity cannot be achieved within the declared model, stop before command archival. External CLI destination behavior is not a stop condition. Commit, push, release, remote-source verification, and user-global cleanup require separate explicit authority.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: plan-change

The user explicitly selected the hybrid distribution, retained Claude Code and Codex as plugin exceptions, rejected the `csheng-*` rename, and clarified that `npx skills` is advisory only: the repository neither restricts nor detects installations and makes no coexistence promise.

## Design Review

- required_entry: review-change
- review_component: review-design
- review_depth: boundary
- review_status: passed
- max_review_batches: 2
- review_evidence: Bounded version 3 review accepted one blocker: an external `npx skills@latest --list` exercise still appeared as required acceptance despite the advisory ownership boundary. Acceptance now relies only on repository-owned generation and index validation; external CLI exercises are optional informational evidence. Focused verification review passed with no remaining candidate finding.

## Implementation Surface

- impl_file_refs:
  - .claude-plugin
  - .codex-marketplace
  - .codex-plugin
  - .gitignore
  - .ignore
  - AGENTS.md
  - README.md
  - archived
  - commands
  - contracts
  - docs/AGENTS.md
  - docs/README.md
  - docs/architecture
  - docs/changelog/design-decisions.md
  - docs/quickstart.md
  - hooks
  - install-codex.sh
  - install.sh
  - scripts
  - skills
  - skills.index.json
  - src/runtime
  - src/skills
- test_file_refs:
  - scripts
  - tests
  - src/runtime/harness/smoke-test
  - src/skills/_internal/_harness-libs/smoke-test
