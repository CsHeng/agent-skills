# Agent Skills Hybrid Distribution Implementation Plan

## Upstream Design

- design_ref: 2026-08-07-agent-skills-distribution-migration-design.md
- design_version: 3

## Implementation Scope

- target_repository: /Users/csheng/workspace/playground/market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- architecture_decision_ref: ASD-001-hybrid-agent-skills-distribution
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
- verification_scope:
  - Preserve the pre-implementation status of every path outside the approved design surface and compare the final changed-path set with this plan.
  - Prove Claude Code and Codex plugin manifests, marketplaces, installers, and generated targets remain active and valid.
  - Prove public source, contract, routing, generated-directory, frontmatter, and index identities remain unchanged and contain no new `csheng-` prefix.
  - Prove each runner-owning workflow contains a byte-current production harness runtime and can execute it from an unrelated target working directory.
  - Prove all command-only required behavior is owned by active skills before commands are archived.
  - Prove active docs keep provider plugins authoritative for Claude/Codex and present `npx skills` only as optional consumer-managed guidance without repository restrictions, detection, or coexistence guarantees.
  - Run required generators, focused harness smoke tests, provider-native plugin validators, Python contract tests, aggregate repository checks, Markdown whitespace checks, and bounded implementation review.

## Architecture Binding

- architecture_decision_ref: ASD-001-hybrid-agent-skills-distribution
- chosen_option: Retain mature Claude Code and Codex plugins, preserve existing public skill names, publish the same closed standard skill payload, and present `npx skills` only as optional consumer-managed guidance for other agents.
- reversible_increments:
  - Record advisory distribution ownership without changing public names or adding installation enforcement.
  - Close runtime packages and migrate command-only semantics while every existing plugin and command remains active.
  - Validate both plugins, public package closure, and active command adapters before archiving commands.
  - Archive commands and synchronize stable truth only after replacement semantics and distribution checks pass.
- upgrade_triggers:
  - Revisit runtime vendoring when measured generated duplication becomes the dominant repository size or validation cost, or a supported installer can atomically preserve a shared dependency.
  - Add another provider adapter only for a demonstrated required capability that cannot use the portable skill payload and after approving its lifecycle owner and acceptance test.

## Work Package Readiness

- milestone_objective: Deliver a validated hybrid distribution model that keeps Claude Code and Codex plugins, publishes a closed portable skill payload with optional `npx skills` guidance, preserves existing skill names, and retires only the obsolete command surface.
- non_goals:
  - No repository restriction on which agents a consumer selects through `npx skills`.
  - No public skill rename, `csheng-*` alias, provider-specific identity fork, or attempt to solve semantic duplication with naming.
  - No all-agent destination table, arbitrary destination wrapper, or repository-owned long-tail install, update, remove, copy, or symlink implementation.
  - No detection, prevention, cleanup, or coexistence guarantee for consumer-managed installations.
  - No user-global plugin, symlink, copied-skill, or agent-configuration mutation.
  - No generic command read-only-alternative catalog and no replacement scanner for archived `check-secrets.md`.
  - No all-repository `skill-miner` feature change, unrelated documentation repair, commit, push, release, or remote-source verification.
- future_phase:
  - Run `npx skills@latest add CsHeng/agent-skills --list` against the published revision after an explicitly authorized commit and push.
  - Perform any user-global transition or cleanup only when explicitly requested.
  - Revisit generic-only distribution or additional native plugins only when an approved upgrade trigger is observed.
- decision_status: ready_for_review
- oracle_strategy: Contract-first hybrid verification: Python tests for identity stability, semantic graph, generated output, and advisory distribution ownership; Bash smoke tests for deterministic harness behavior and active command adapters; provider-native manifest validation; and arbitrary-working-directory execution.
- acceptance_oracles:
  - Existing public source directories, `name`, `public_id`, cross-skill references, generated directories, and index entries remain identical in naming.
  - Claude and Codex manifests and marketplaces still consume valid generated skill surfaces, and their native validators pass.
  - The generated public distribution contains no `_harness-libs` pseudo-skill and each workflow package is physically closed.
  - Semantic dependency checks prove the documented complete-inventory profile includes every transitive `semantic_requires` target and reject unknown or disallowed edges.
  - Workflow smoke tests assert runner, gate, typed-exit, review, truth-sync, close, and target-repository semantics on active skill surfaces rather than `commands/`.
  - Active command adapters resolve their owner-local bundled runners before the command surface is archived.
  - Active documentation and validation no longer depend on command wrappers but continue to treat provider plugins and installers as supported behavior.
  - README contains the Superpowers acknowledgement and advisory `npx skills` guidance with consumer-owned installation and coexistence choices.
  - Required generation, focused tests, `bash scripts/check.sh`, provider validators, and `git diff --check` pass without unrelated tracked drift.
  - Bounded implementation review leaves no accepted current-slice finding unresolved.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: false

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 1

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval authorizes the complete serial repository change, validation, and bounded review in the current checkout. It does not authorize commit, push, release, remote-source acceptance, plugin installation, `npx skills` execution against the real home directory, or any user-global cleanup.
- runtime_contingencies:
  - X1: If command-parity analysis reveals a required lifecycle authority that cannot be placed in an existing owning skill or direct reference, stop with `needs-plan-change` before archival.
  - X2: If runtime closure cannot be achieved without a separately installed public dependency skill, stop with `needs-design-decision` instead of retaining hidden sibling assumptions.
  - X3: If a task changes a path outside the approved implementation or test surface, stop, preserve the diff, and route to `needs-plan-change` rather than widening scope.
  - X4: If provider-native validation shows that command removal prevents the retained Claude or Codex plugin from loading its skill inventory, stop before archival and route the new provider requirement to `needs-design-decision`.
- planned_stop_points:
  - none
- task_ordering_rationale: Advisory ownership and unchanged identities are recorded first. Runtime closure and command parity then make each installed workflow independently usable. Both plugin surfaces and active command adapters pass before command archival. Stable docs and final convergence run last so they describe verified behavior rather than intent.

## Task 1: Establish the advisory hybrid distribution contract

- task_id: HYB-010
- depends_on:
  - none
- scope_slice: Preserve current identities and plugin targets, make the maintained and advisory distribution ownership explicit in machine checks, and remove repository-owned installation restrictions or detection.
- architecture_decision_ref: ASD-001-hybrid-agent-skills-distribution
- reversible_increments:
  - Add failing fixtures for unchanged identities, retained provider targets, advisory long-tail ownership, and absence of repository enforcement.
  - Extend existing contracts and validators without changing generated public bytes.
- upgrade_triggers:
  - Return to design if a future maintained provider surface requires repository-owned installation lifecycle or compatibility enforcement.
- impl_file_refs:
  - contracts
  - install-codex.sh
  - scripts
  - src/skills
- test_file_refs:
  - scripts
  - tests
- verification_scope:
  - Capture `git status --short` before mutation and record the dependency-frozen baseline.
  - Add red tests that prohibit `csheng-*` renames, require Claude/Codex/root-flat targets to remain, and require the long-tail policy to remain advisory and consumer-owned.
  - Keep `contracts/install-targets.toml`; update descriptions or contract metadata so Claude, Codex, and root-flat remain distinct generated targets sharing one authored inventory.
  - Reject contract fields, scripts, installer branches, or tests that maintain an agent allowlist, destination policy, duplicate detector, or coexistence gate.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - distribution-contract
- task_review_depth: focused
- done_when:
  - Existing public identities and all three current generated targets remain represented without a prefix migration.
  - Long-tail installation is explicitly advisory and consumer-owned, with no destination or coexistence enforcement.
  - The Codex installer contains no duplicate-exposure preflight.
  - Focused contract tests pass while generated public names remain unchanged.
- failure_policy: fix_forward
- [ ] Add identity-retention, provider-target, and advisory-ownership fixtures.
- [ ] Extend distribution contracts without renaming skills or removing plugin targets.
- [ ] Remove repository-owned destination and duplicate-exposure enforcement.

## Task 2: Close runtime packages and absorb command semantics

- task_id: HYB-020
- depends_on:
  - HYB-010
- scope_slice: Move deterministic harness runtime out of skill discovery, bundle production runtime into each runner-owning workflow, declare semantic requirements, and migrate every required command-only behavior into its durable skill owner.
- architecture_decision_ref: ASD-001-hybrid-agent-skills-distribution
- reversible_increments:
  - Move production runtime and repository smoke tests to the non-discoverable runtime root without removing active commands.
  - Add runtime bundling and parity checks to all generated targets.
  - Convert command-control assertions to active skill/runtime assertions and prove semantic parity before HYB-030 archives commands.
- upgrade_triggers:
  - Stop with `needs-plan-change` if command parity requires a new top-level lifecycle owner or a public scanner skill.
  - Return to design under X2 if a runner-owning workflow cannot be physically closed without a separately installed dependency skill.
- impl_file_refs:
  - contracts/skills.toml
  - commands
  - scripts
  - src/runtime
  - src/skills
- test_file_refs:
  - scripts
  - tests
  - src/runtime/harness/smoke-test
  - src/skills/_internal/_harness-libs/smoke-test
- verification_scope:
  - Move production harness Shell sources to `src/runtime/harness/` and repository smoke tests to `src/runtime/harness/smoke-test/`; leave no public `SKILL.md` for runtime support.
  - Declare runtime ownership for `design-change`, `plan-change`, `implement-change`, `review-change`, `sync-truth`, and `close-change` without changing their public identities.
  - Make Claude, Codex, and root-flat generation copy byte-current production runtime, excluding smoke tests and provider metadata, into each owner at `scripts/harness/`.
  - Replace sibling `_harness-libs` resolution in reusable skills with skill-relative resources and self-locating scripts; explicitly bind `SKILL_ROOT` only where prose must resolve an installed helper before changing directories.
  - Keep `${CLAUDE_PLUGIN_ROOT}` only inside the retained Claude-specific adapter and hook, never in portable skill instructions.
  - While commands remain active, update the five runner-resolving command adapters to their owner-local `skills/<owner>/scripts/harness/` paths and execute those entry points before archival.
  - Compare every command doc with its owner: merge runner, gate, typed-exit, and execution-continuity behavior into six workflow owners; preserve target-repository scoping in `smart-commit`; prove thin wrapper commands redundant; and mark `check-secrets` archive-only.
  - Declare and validate direct `semantic_requires` edges plus the complete-inventory profile without adding installer dependency resolution.
  - Run harness smoke tests against the source runtime and representative generated bundles from unrelated working directories.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - harness-runtime
  - lifecycle-semantics
  - generated-targets
- task_review_depth: deep
- done_when:
  - Runtime support is non-discoverable source material and no public pseudo-skill exists.
  - Every runner-owning workflow contains a current local production runtime in all temporary generated targets and resolves it without a provider root or sibling skill.
  - All required command-only behavior has one active skill owner, with executable smoke assertions on that active surface.
  - The complete-inventory semantic profile is closed and selective-install caveats are machine-readable.
  - Focused runtime, semantic, and lifecycle smoke suites pass from unrelated working directories.
- failure_policy: fix_forward
- [ ] Move runtime ownership and add deterministic bundle generation for every retained target.
- [ ] Replace provider/sibling path assumptions with the approved skill-root contract.
- [ ] Absorb required command semantics into unchanged public skill identities.
- [ ] Add semantic dependency validation and pass focused smoke tests.

## Task 3: Pass the pre-archive hybrid distribution gate

- task_id: HYB-025
- depends_on:
  - HYB-020
- scope_slice: Generate the exact shared payload, validate both retained plugins and active command adapters, and review the replacement surface before commands are archived.
- architecture_decision_ref: ASD-001-hybrid-agent-skills-distribution
- reversible_increments:
  - Regenerate tracked `skills/` and `skills.index.json` while commands remain active.
  - Pass offline distribution, plugin, semantic, runtime, and arbitrary-working-directory checks.
  - Execute active command adapters against owner-local bundled runners, then review the replacement slice before authorizing command archival.
- upgrade_triggers:
  - Return to design under X4 if retained plugin loading depends on the command surface.
- impl_file_refs:
  - .claude-plugin
  - .codex-marketplace
  - .codex-plugin
  - scripts
  - skills
  - skills.index.json
- test_file_refs:
  - scripts
  - tests
  - src/runtime/harness/smoke-test
- verification_scope:
  - Regenerate tracked `skills/` and `skills.index.json`, then prove exact source, contract, bundle, and unchanged-name parity with no runtime pseudo-skill.
  - Generate and validate temporary Claude and Codex target surfaces using repository checks, `claude plugin validate --strict .`, and the official local Codex plugin validator required by AGENTS.md.
  - Execute the five active command adapters' owner-local runner paths and representative bundled runners from an unrelated target working directory.
  - Route the HYB-010 through HYB-025 diff, focused oracles, plugin validation, and command-adapter evidence through bounded `review-change` with `review-implementation`; repair only accepted in-scope findings and rerun affected checks.
  - Treat a passing HYB-025 review and provider/package gate as a hard dependency for HYB-030. X1, X2, or X4 stops before archival.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - generated-distribution
  - plugin-validation
  - command-adapter-parity
- task_review_depth: deep
- done_when:
  - The tracked shared payload and index are fresh, physically closed, semantically complete as a full profile, and retain all current public names.
  - Claude Code and Codex plugin surfaces pass repository and provider-native validation.
  - All active command adapters resolve and execute owner-local bundled runners before archival.
  - Replacement-slice implementation review passes with no accepted finding unresolved before command archival.
- failure_policy: fix_forward
- [ ] Generate and prove the shared payload plus both plugin surfaces.
- [ ] Execute active command adapters and unrelated-working-directory bundled runners.
- [ ] Review and repair the replacement slice before command archival.

## Task 4: Archive commands and retire active command references

- task_id: HYB-030
- depends_on:
  - HYB-025
- scope_slice: Retire only the active Claude command wrappers, preserve inert command history, and remove active command discovery/check dependencies while leaving final stable-truth synchronization to HYB-040.
- architecture_decision_ref: ASD-001-hybrid-agent-skills-distribution
- reversible_increments:
  - Record command parity and the retained provider-adapter inventory before moving files.
  - Move command docs under `archived/commands/` while leaving every provider manifest, marketplace, installer, and hook active.
  - Remove active command discovery and check references only after archive structure and provider surfaces are checked.
- upgrade_triggers:
  - Stop under X4 if command removal prevents either retained plugin from discovering or loading the generated skill inventory.
- impl_file_refs:
  - .claude-plugin
  - .codex-marketplace
  - .codex-plugin
  - .gitignore
  - .ignore
  - archived
  - commands
  - hooks
  - install-codex.sh
  - install.sh
  - scripts/install.sh
- test_file_refs:
  - scripts
  - tests
  - src/runtime/harness/smoke-test
- verification_scope:
  - Move all `commands/*.md` to `archived/commands/` only after HYB-020 parity checks and the HYB-025 hybrid distribution gate pass.
  - Keep Claude/Codex manifests, marketplace files and symlink, top-level installers, `scripts/install.sh`, Claude post-edit hook/checkers, and repository Git hooks active.
  - Add the archive search boundary and historical-status note; ensure archived commands are absent from active discovery, routing, validation, and plugin component claims.
  - Update active checks and smoke tests so they validate sovereign skill/runtime surfaces rather than active command wrappers.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: balanced
- reasoning_profile: standard
- isolation: controller-checkout
- resource_locks:
  - command-archive
  - provider-adapters
- task_review_depth: deep
- done_when:
  - No active top-level command wrapper remains, and `archived/commands/` is inert and absent from active discovery.
  - Claude Code and Codex manifests, marketplaces, installers, and hooks remain active and documented.
  - Focused archive, provider-retention, and command-discovery tests pass without claiming stable truth is synchronized yet.
- failure_policy: fix_forward
- [ ] Archive command history only after semantic and distribution parity.
- [ ] Remove command wrappers from active checks and discovery while retaining both plugin surfaces.
- [ ] Leave stable truth synchronization and README acknowledgement to verified HYB-040 evidence.

## Task 5: Converge and review the hybrid distribution

- task_id: HYB-040
- depends_on:
  - HYB-030
- scope_slice: Regenerate every tracked derived surface, run complete repository and provider validation, complete bounded implementation review, synchronize stable truth from verified evidence, and stop at the explicit truth-sync human gate.
- architecture_decision_ref: ASD-001-hybrid-agent-skills-distribution
- reversible_increments:
  - Regenerate tracked public skills, index, and diagrams from source and inspect the exact changed paths.
  - Pass complete offline and provider-native validation before final review.
  - Complete bounded review and rerun only affected plus aggregate oracles after accepted repairs.
- upgrade_triggers:
  - Return to design under X4 if provider evidence invalidates the approved hybrid boundary.
- impl_file_refs:
  - .claude-plugin
  - .codex-marketplace
  - .codex-plugin
  - AGENTS.md
  - README.md
  - docs/AGENTS.md
  - docs/README.md
  - docs/architecture
  - docs/changelog/design-decisions.md
  - docs/quickstart.md
  - scripts
  - skills
  - skills.index.json
- test_file_refs:
  - scripts
  - tests
  - src/runtime/harness/smoke-test
- verification_scope:
  - Run `python3 scripts/generate-skills-index.py`, `python3 scripts/flatten-skills.py --target root-flat`, and `python3 scripts/generate-workflow-diagrams.py`; inspect that existing public names remain, no runtime pseudo-skill exists, and diagrams show retained plugins without active commands.
  - Run all Python unit tests, all moved harness smoke tests, the command-retirement replacements for the sovereign command-surface suites, repository Git-hook checks, `bash scripts/check.sh`, and `git diff --check`.
  - Run `claude plugin validate --strict .` and `uvx --with pyyaml python "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .` without installing either plugin.
  - Compare final `git status --short` and changed paths with the approved touch set, then route the HYB-030 and HYB-040 diff plus prior HYB-025 evidence through bounded `review-change` with `review-implementation`.
  - Repair only accepted causally linked findings inside the approved surface, rerun affected checks, and perform one focused verification review.
  - After review repair, rerun aggregate checks, both provider validators, active-reference scans, and unrelated-working-directory runner execution.
  - Use `sync-truth` after verified implementation to rewrite README, AGENTS, quickstart, install-surface, maintenance, orchestration, invocation, state-machine, docs-boundary, and decision-history truth for the maintained plugins, advisory consumer-owned `npx skills` guidance, runtime closure, and command retirement.
  - Add the README Superpowers acknowledgement and stable portability rationale linking Agent Skills, `skills`, mattpocock/skills, Codex documentation, and Superpowers.
  - Create and validate a truth-sync artifact in the pending approval state, then stop at its explicit human gate before close.
  - Report focused evidence separately from any unrelated pre-existing full-suite failure; do not modify real plugin or skill installations.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - generated-distribution
  - plugin-validation
  - advisory-distribution-truth
- task_review_depth: deep
- done_when:
  - Tracked generated skills, index, diagrams, active docs, both plugin surfaces, and long-tail guidance are fresh and agree with source contracts.
  - All focused, aggregate, and provider-native checks pass with no unapproved changed path.
  - Final evidence proves advisory long-tail ownership, absence of repository enforcement, and unrelated-working-directory runtime execution.
  - Bounded implementation review passes with no accepted finding unresolved.
  - Stable truth matches verified behavior, README contains the Superpowers acknowledgement, and the valid truth-sync artifact is pending explicit human approval.
- failure_policy: fix_forward
- [ ] Regenerate every tracked derived surface and inspect unchanged names plus retained plugins.
- [ ] Run complete offline and provider-native verification.
- [ ] Complete bounded implementation review and focused repair verification if needed.
- [ ] Synchronize stable truth and stop at the truth-sync human approval gate.

## Truth Sync Gate

- required_entry: sync-truth
- approval_required: true
- artifact_status_on_handoff: pending
- next_entry_after_approval: close-change
- stop_condition: Do not enter close-change until the user explicitly approves the generated truth-sync artifact.

## Review Gate

- required_entry: review-change
- required_mode: review-only
- review_component: review-plan
- review_depth: boundary
- max_review_batches: 2
- review_status: passed
- review_evidence: Bounded version 3 plan review accepted three blockers: HYB-010 lacked authority to remove the Codex preflight, HYB-020 referenced the wrong runtime contingency, and stable truth lacked explicit `sync-truth` ownership and a human gate. The plan now includes `install-codex.sh`, maps runtime closure to X2, limits HYB-030 to archive transition, and assigns verified stable-truth updates plus a pending truth-sync artifact and explicit human gate to HYB-040. Focused verification review passed with no remaining candidate finding.
- supporting_files:
  - 2026-08-07-agent-skills-distribution-migration-design.md: approved hybrid goals, non-goals, maintained/advisory distribution ownership, acceptance, recovery, and implementation surface.
  - AGENTS.md: source/generated ownership, lifecycle gates, serial-first execution, review rules, and repository validation requirements.
  - contracts/skills.toml: current public inventory, routing permissions, install targets, and runtime metadata to extend without renaming.
  - contracts/install-targets.toml: retained Claude, Codex, and root-flat generation targets.
  - scripts/flatten-skills.py: current multi-target generator that must produce physically closed packages for every retained target.
  - scripts/check-install-surface.py: current provider-target validator to extend with identity, closure, and retention assertions.
  - scripts/check.sh: aggregate offline validation owner that must remain network-independent.
  - install-codex.sh: retained provider installer with no repository-owned duplicate-exposure enforcement.
  - commands: current command-only semantics and archive source, bounded to parity classification.
  - src/skills/_internal/_harness-libs: current runtime source and smoke tests to relocate and bundle.
- pass_condition: The plan implements ASD-001 through reversible serial increments, keeps both provider plugins and current names, proves physical and semantic closure plus command-adapter parity before archival, and keeps optional `npx skills` guidance consumer-owned without repository restrictions or detection.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change

The user explicitly approved continuous execution of the version 3 advisory-distribution revision on 2026-08-07.

## Recovery

- default_failure_policy: fix_forward
- recovery_evidence:
  - The pre-implementation Git status, dependency-frozen baseline, task-scoped diffs, and final allowed-touch-set comparison preserve unrelated-work evidence.
  - Both provider adapters and commands remain active until identity, runtime, semantic, plugin, and command-adapter checks pass, providing a reversible repository-local increment without authorizing automatic restoration.
  - No repository task invokes `npx skills` installation or inspects user-global skill state; external installation behavior remains consumer-owned.
  - No task declares guarded rollback; any architecture invalidation returns the typed design or plan stop instead of synthesizing a restore path.
