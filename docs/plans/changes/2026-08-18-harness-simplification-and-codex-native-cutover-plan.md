# Harness Simplification And Codex-Native Cutover Plan

## Status

- plan_version: 2
- plan_contract_version: 2
- approval_required: true
- approval_status: approved
- implementation_status: completed
- implementation_review_status: passed_after_bounded_repair
- implementation_verification_status: passed
- plan_review_status: passed_after_two_bounded_reviews
- recommended_next_phase: truth_sync
- next_entry: sync-truth

## Upstream Design

- design_ref: 2026-08-18-harness-simplification-and-codex-native-cutover-design.md
- design_version: sha256:6b5d74e31b39d288251dcfdf73af2bf94d11114543103b367a13af89cd367251
- design_approval_status: approved
- architecture_decision_ref: HSC-001-canonical-plugin-runtime
- boundary_decision_ref: HWR-001-option-a

## Implementation Scope

- target_repository: market-csheng
- execution_cwd: /Users/csheng/workspace/playground/market-csheng
- plan_contract_version: 2
- parallel_execution_approved: false
- truth_sync_required: true
- impl_file_refs:
  - AGENTS.md
  - README.md
  - pyproject.toml
  - uv.lock
  - contracts/markdown-prose.toml
  - contracts/skills.toml
  - contracts/install-targets.toml
  - contracts/lifecycle.toml
  - docs/architecture
  - docs/changelog/design-decisions.md
  - hooks/pre-commit
  - runtime/harness
  - scripts/check.sh
  - scripts/check-contracts.py
  - scripts/check-install-surface.py
  - scripts/flatten-skills.py
  - scripts/generate-skills-index.py
  - scripts/generate-workflow-diagrams.py
  - scripts/install.sh
  - scripts/skill_activation.py
  - skills
  - skills.index.json
  - src/runtime/harness
  - src/skills
- test_file_refs:
  - runtime/harness/tests
  - src/runtime/harness/smoke-test
  - tests
- verification_commands:
  - `bash "$DESIGN_RUNNER" validate docs/plans/changes/2026-08-18-harness-simplification-and-codex-native-cutover-design.md`
  - `bash "$PLAN_RUNNER" validate docs/plans/changes/2026-08-18-harness-simplification-and-codex-native-cutover-plan.md`
  - `UV_CACHE_DIR="$HOME/.cache/uv/market-csheng-harness" UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv-projects/market-csheng-harness" uv lock --check`
  - `bash -n scripts/check.sh hooks/pre-commit`
  - `bash scripts/check.sh`
  - `claude plugin validate .`
  - `UV_CACHE_DIR="$HOME/.cache/uv/market-csheng-harness" uvx --with pyyaml python "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .`
  - `test -f "$HOME/.codex/AGENTS.md" && ! rg -n -F -e 'clean-architecture' -e 'quality-standards' -e 'security-logging' "$HOME/.codex/AGENTS.md"`
  - `git diff --check`

## Work Package Readiness

- milestone_objective: Replace the duplicated source/generated skill surfaces and six copied Shell harness runtimes with one canonical 39-skill tree and one standard-library Python lifecycle runtime, make codex-native the flag-absent backend, remove SIM001-SIM004 and the three compatibility skills, reduce `scripts/check.sh` to thin serial orchestration, and enforce zero hard wraps outside ten exact digest-bound stage-history exceptions.
- non_goals:
  - Preserve retired skill IDs, legacy artifact contract versions, selective standalone lifecycle-skill execution, `.dist` install surfaces, or direct use of old Shell runner paths.
  - Remove the explicit Herdr backend, change its schema-version-1 wire behavior, weaken main-agent fallback rules, or operate any live Herdr or Codex child session.
  - Reissue or edit the ten immutable stage-history artifacts, update their embedded digests, or add directory/glob-based Markdown exclusions.
  - Change lifecycle phase authority, human approval gates, approved task topology, touch-set ownership, review adjudication, truth-sync ownership, or close semantics.
  - Add a generic runtime framework, daemon, cache service, provider-specific package, third-party harness runtime dependency, or compatibility parser.
  - Reformat or lint-clean unrelated pre-existing Python scripts and tests merely to make a new repository-wide style gate green.
  - Install or update either plugin, start a new Codex thread, commit, push, publish, deploy, mutate external providers, or edit `~/.codex/AGENTS.md`.
  - Delete, expose, inspect as project input, or normalize the existing ignored `.dist/` directory merely because its generators and supported install-surface contract are retired.
- future_phase:
  - Design a separate packaging artifact only if a concrete supported consumer requires standalone lifecycle-skill closure after the plugin-only cutover.
  - Reconsider categorized physical skill directories only if a maintained provider supports recursive discovery with equivalent metadata semantics.
  - Profile Python startup only if post-cutover measurement identifies it as material; do not add a daemon or Go binary pre-emptively.
  - Reissue digest-bound stage history only under a separately reviewed and explicitly approved artifact-chain migration.
- decision_status: ready_for_review
- oracle_strategy: Use characterization and golden tests for legacy-current lifecycle invariants and explicit Herdr envelopes, contract-version-3 schema tests for new artifacts, model/state-transition tests for DAG and ledger behavior, contract tests for canonical skill and plugin surfaces, parser instrumentation for one-read and no-field-subprocess guarantees, language-tooling checks for the Python runtime and thin Shell entrypoints, and semantic-fingerprint plus exact-digest checks for Markdown normalization.
- acceptance_oracles:
  - Every currently enforced lifecycle state, typed stop, approval gate, touch-set rule, external-evidence rule, review budget, truth-sync route, and close decision is captured before the old Shell implementation is deleted and passes against the Python replacement unless the approved design explicitly changes it.
  - Version-3 design, plan, truth-sync, close, task, and ledger fixtures parse once through one TOML front-matter block, reject malformed or duplicate metadata, and expose no field-at-a-time extraction interface.
  - Ledger initialization parses and validates linked artifacts once, records normalized projections and digests atomically, and later transitions check ledger plus artifact digests without reparsing or fully validating the plan.
  - Flag-absent binding output equals explicit codex-native output, explicit Herdr remains schema-version-1 compatible, and main-agent fallback remains available only where the approved unchanged task already permits it.
  - The canonical package contains exactly 39 skills and one `runtime/harness`; `src/skills`, `src/runtime/harness`, skill-local `scripts/harness`, `.dist` generation, compatibility skills, helper/supersession schema, internal install schema, and retired generator paths are absent.
  - `scripts/check.sh` invokes each owned checker or generator once and one pytest discovery lane, while runtime operations spawn no field-at-a-time `awk`, `rg`, `sed`, `sort`, or `jq` helpers.
  - The Markdown checker reports zero non-exempt hard wraps, validates all ten immutable exception digests, rejects implicit enrollment or digest refresh, and leaves every exception byte-identical.
  - Focused tests, aggregate validation, both plugin package checks, the official Codex plugin validator, the exact external compatibility-ID search, and `git diff --check` pass without retries or weakened assertions.
- execution_continuity: continuous_after_plan_approval
- max_review_batches: 2
- subagent_ready: true

## Baseline Tooling Evidence

- python_runtime: Python 3.14.7 is currently available; the runtime contract requires Python 3.11 or newer because it uses standard-library `tomllib`.
- development_tools: uv 0.12.5, Ruff, ty, and pytest are currently available through the configured local toolchain.
- pytest_scope: Unscoped `pytest -q` currently collects the same `test_extract_session_signals` module from both `src/skills` and generated `skills`, causing an import-file mismatch. Explicit collection of `tests` plus the generated skill test path passes; `pyproject.toml` must therefore own deterministic test roots, and the final canonical-tree cutover removes the duplicate physical module.
- ruff_scope: A current full `scripts tests` Ruff format/check reports unrelated legacy formatting and lint debt. This plan gates the new `runtime/harness` Python boundary with Ruff and ty and relies on existing focused behavior tests for modified legacy scripts; it does not authorize repository-wide Python reformatting.
- ty_scope: A current whole-`scripts` ty run cannot resolve sibling `skill_activation` imports under default module roots. The new typed gate is limited to the package-owned `runtime/harness`; existing scripts remain covered by compilation, contract tests, and aggregate execution unless separately migrated into the typed package.

## Approved Architecture Decision

- architecture_decision_ref: HSC-001-canonical-plugin-runtime
- decision_fidelity: Implement the selected breaking whole-plugin cutover: `skills/` becomes the sole authored content tree, `runtime/harness/` becomes the sole lifecycle runtime, Python owns structured parsing/state/business rules, Shell owns only short orchestration, and neither legacy artifact parsing nor copied runtime closure survives.
- reversible_increments:
  - HSC-010 captures current behavior and establishes the development toolchain without changing runtime selection.
  - HSC-020 through HSC-040 build and verify the new Python runtime while the old Shell runtime remains the active pre-cutover path.
  - HSC-050 performs the one atomic source/runtime cutover only after the Python replacement passes its focused equivalence and intentional-change oracles.
  - HSC-060 simplifies aggregate validation after the new ownership boundary exists, and HSC-070 converges stable truth, generated views, and Markdown structure once against the final tree.
  - HSC-080 is read-only final verification and review; it may route an accepted failure to its owning earlier task but may not widen the plan.
- upgrade_triggers:
  - Return `needs-design-decision` if a required lifecycle invariant cannot be represented by the version-3 Python model without changing authority or accepted behavior.
  - Return `needs-design-decision` if either maintained plugin cannot resolve one package-level runtime without restoring copied bundles or install-time mutation.
  - Return `needs-design-decision` if explicit Herdr schema-version-1 compatibility cannot survive the shared-runtime and Python cutover.
  - Return `needs-plan-change` if implementation requires a repository path outside this plan, a historical stage-artifact mutation, an external write outside the five C0 tool-cache prefixes, or a new third-party runtime dependency.

## Approved Hard-Wrap Decision

- boundary_decision_ref: HWR-001-option-a
- selected_scope: All Git-visible Markdown remains subject to the normalizer except ten exact existing stage-history files whose repository-relative paths and SHA-256 values are declared in `contracts/markdown-prose.toml`.
- immutable_exception_policy: An exception is valid only while its path is an existing regular Git-visible file under `docs/plans/`, its digest matches exactly, and the scanner still finds the legacy wrap being preserved. No glob, directory exclusion, implicit enrollment, write-mode update, or digest refresh is permitted.
- mutable_artifact_policy: This design, this plan, any later artifact created by the change, stable docs, canonical skills, and every non-manifest Markdown file must reach zero findings.
- exact_exception_baseline:
  - `1e7d9b4e66d3716bb12d7b201bd73415e335510b627384cb0dda760981a889c6 docs/plans/changes/2026-08-11-implement-change-via-herdr-design.md`
  - `e3c2fcfdf0601ba6a212a3a927fdc58fddda1f35fabe709497220643de842147 docs/plans/changes/2026-08-11-implement-change-via-herdr-plan.md`
  - `cfe01da87bbfb9ecb3072dad7710d3303c5d5a88b19ce931ebb1787cdf2704ad docs/plans/changes/2026-08-12-herdr-batch-utilization-and-explorer-cost-plan.md`
  - `c7115414acbf07db3e9c3337ba9f5ca2feef31d2d612a444e69e3ed8777e2b7d docs/plans/changes/2026-08-17-codex-native-binding-plan.md`
  - `a7697435d7cbf952fe3f94bef9ade87ea75d4ff46f5ad9fff4f460110eb993eb docs/plans/changes/2026-08-17-codex-native-binding-truth-sync.md`
  - `21a0c38ecad5d2dce2dda797409747c5622b092ec9ae4aa5a7735a6ef6bcf1df docs/plans/changes/2026-08-18-codex-subagent-user-route-input.md`
  - `658e2d7fe83480f405c57fd79333c505c4e251fe1aad234aa07eea727aaf8d1d docs/plans/changes/2026-08-18-decision-lifecycle-code-simplification-durable-prose-truth-sync.md`
  - `c5ca7faf092d67c2f0ad104d3f77ea7fe1363c8a5a5feca49d623f227e17707c docs/plans/changes/2026-08-18-parent-inherited-codex-subagent-routing-e2-design.md`
  - `b1b3c8100c9b65c7ca2cc77fbce3f9c8c8b551ec5520cae2f0e6783501f62b6e docs/plans/changes/2026-08-18-parent-inherited-codex-subagent-routing-e2-plan.md`
  - `9d8ab0f01debdfd3dd2c9898bbbbd9062641f2d7fe5316a4c66904d48200909e docs/plans/changes/2026-08-18-parent-inherited-codex-subagent-routing-plan.md`

## Runtime Binding

- default_model_policy: semantic-routing
- allowed_model_policies:
  - semantic-routing
  - inherit-main
  - runtime-default
- effective_concurrency: 1; HSC-010 through HSC-080 execute serially because they share the same source/runtime cutover boundary and later tasks consume exact outputs from earlier tasks.
- worker_binding_policy: The user's approval explicitly authorizes one `gpt-5.6-terra` worker at reasoning effort `high` for HSC-010 through HSC-070 in one task-scoped isolated worktree. The controller owns path verification, integration, ledger convergence, repair, HSC-080, and the tail route.
- reviewer_binding_policy: The mandatory plan and implementation reviews may use the standard bounded reviewer path, but reviewers remain read-only candidate finders and the main controller owns adjudication and any repair.

## Execution Continuity

- execution_mode: continuous_after_plan_approval
- confirmation_clearance:
  - C0: Approval authorizes HSC-010 through HSC-080 as one continuous repository-local implementation unit, including tracked file creation, moves, edits, and deletions inside the declared touch set; read-only verification of the three retired names in `~/.codex/AGENTS.md`; and ephemeral tooling writes only below `$HOME/.cache/uv/market-csheng-harness`, `$HOME/.cache/uv-projects/market-csheng-harness`, `$HOME/.cache/ruff/market-csheng-harness`, `$HOME/.cache/python/market-csheng-harness`, and `$HOME/.cache/pytest/market-csheng-harness`. It does not authorize any other external write, editing `~/.codex/AGENTS.md`, touching `.dist/`, plugin install/update, a new Codex thread, live Codex or Herdr spawning, commit, push, publication, deploy, provider action, truth-sync approval, or close approval.
- runtime_contingencies:
  - X1: If preflight finds unexplained overlapping user changes in any declared implementation or test ref, preserve them and return `blocked_source_baseline` before mutation.
  - X2: If the characterization matrix reveals an uncaptured authority or state invariant, or the Python model cannot preserve an invariant without changing the approved design, retain both implementations before cutover and return `needs-design-decision`.
  - X3: If either maintained plugin package cannot resolve the shared runtime from its installed root, stop before deleting copied bundles and return `needs-design-decision` with the exact package-resolution evidence.
  - X4: If any immutable Markdown exception is missing, changed, no longer a regular Git-visible file, or digest-mismatched, stop before normalization with `immutable_history_drift`; do not refresh the manifest.
  - X5: If an implementation need escapes the approved repository touch set or requires an external write outside the five exact C0 tooling-cache prefixes, return `needs-plan-change` before that mutation.
- planned_stop_points:
  - none inside HSC-010 through HSC-080; successful implementation, implementation review, and verification route to the separate truth-sync approval gate.
- task_ordering_rationale: Freeze current behavior and toolchain first; build the replacement parser, lifecycle model, and backend binding behind a non-active path; perform the source/runtime cutover only after focused equivalence passes; simplify aggregate validation against the new owners; then update stable truth, normalize mutable Markdown, regenerate views, and run one complete final gate.

## Implementation Language

- implementation_archetype: Local lifecycle contract compiler and state-machine CLI with thin repository Shell orchestration.
- implementation_language: Python 3 standard-library runtime; Bash only for bounded environment discovery and serial command orchestration.
- language_rationale: TOML parsing, typed validation, JSON projection, hashing, state transitions, and atomic persistence require one testable structured-data owner, while the repository already ships Python and `tomllib`. Shell remains appropriate only for the short `scripts/check.sh` and hook entrypoints; no lifecycle business rule may remain split across languages.
- tooling_contract: `pyproject.toml` is the configuration source of truth, `uv.lock` pins development-only Ruff, ty, and pytest tooling, `UV_CACHE_DIR`, `UV_PROJECT_ENVIRONMENT`, `RUFF_CACHE_DIR`, `PYTHONPYCACHEPREFIX`, and pytest `cache_dir` bind ephemeral state to the five exact C0 prefixes, and the installed harness imports only the Python standard library.

## Recovery

- default_failure_policy: fix_forward
- source_boundary: Capture the initial tracked and untracked baseline, preserve unrelated user work, and mutate only declared refs. Do not use reset, checkout-discard, generated hand edits, or historical digest refresh as repair.
- pre_cutover_boundary: Keep `src/runtime/harness` and the current source/generated skill path active until HSC-020 through HSC-040 pass focused characterization and intentional-change oracles.
- cutover_boundary: HSC-050 is one coherent repository transition; fix failures forward until exactly one skill source and one runtime owner remain. Do not retain symlinks, dual parsers, copied bundles, aliases, or compatibility skills as an unowned fallback.
- oracle_boundary: Golden, model, permission, touch-set, typed-stop, digest, and explicit-Herdr assertions may be added or translated but not weakened, broadened, or bulk-updated to fit implementation output.
- immutable_history_boundary: The ten HWR-001 files are read-only evidence. Any byte change stops normalization and must be restored to the manifest digest before work continues; changing the manifest requires a new design decision.
- external_boundary: Only the five C0 tool-cache prefixes may receive ephemeral validation state. Plugin installation, plugin cache refresh, new-thread acceptance, any other external write, commit, push, publication, provider mutation, truth-sync approval, and close are separate lifecycle actions and are not recovery mechanisms.
- guarded_rollback: none

## Task 1: Freeze legacy behavior and establish the Python development contract

- task_id: HSC-010
- depends_on:
  - none
- scope_slice: Capture readable characterization fixtures for every current harness phase, valid and invalid artifact-DAG edge, task-ledger state transition, touch-set and external-evidence boundary, recovery route, truth-sync and close decision, and explicit Herdr binding envelope before any old implementation is removed; add the repository Python toolchain contract and a focused test harness that invokes the current Shell owners as the baseline oracle.
- impl_file_refs:
  - pyproject.toml
  - uv.lock
- test_file_refs:
  - runtime/harness/tests
- verification_scope:
  - Prove every one of the twelve existing `src/runtime/harness/smoke-test/test-*.sh` suites has an explicit fixture or model assertion owner; record intentional design changes separately from legacy-current invariants.
  - Capture explicit Herdr schema-version-1 envelopes across binding kinds and model policies before changing runtime code; fixtures become immutable review surfaces after capture.
  - Capture current valid and invalid design, plan, ledger, review, recovery, truth-sync, close, touch-set, and external-evidence outputs with exact typed states and errors rather than existence-only assertions.
  - Configure Python 3.11-or-newer, Ruff, ty, deterministic pytest roots, and pytest's cache directory through `pyproject.toml`; pin development tools in `uv.lock`; keep runtime dependencies empty and bind all uv, environment, Ruff, Python bytecode, and pytest cache state to the five exact C0 prefixes.
  - Run the characterization lane against the current Shell implementation, `uv lock --check`, focused Ruff/ty checks for the new harness test code, and `git diff --check` with every applicable cache environment variable explicit.
- failing_oracle_first: Add the complete owner matrix and fixture assertions first; fail the task if any current smoke assertion or boundary lacks a named destination before capturing or consolidating it.
- implementation_archetype: Test and migration harness for a local CLI rewrite.
- implementation_language: Python 3 for fixtures and tests; existing Bash is invoked read-only as the legacy oracle.
- language_rationale: Python can compare structured outputs and exact state tables without reproducing the field-by-field process topology being retired; the production runtime remains unchanged in this task.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: allowed
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - harness-characterization-baseline
  - python-toolchain-contract
- task_review_depth: full
- done_when:
  - The characterization owner matrix covers every old smoke suite and every design-preserved invariant, and the baseline lane passes against the untouched active Shell runtime.
  - Intentional changes are visibly excluded from byte-compatibility expectations: artifact contract v3, codex-native flag-absent default, retired compatibility/schema surfaces, and the package/runtime cutover.
  - `pyproject.toml` and `uv.lock` provide reproducible development tooling while the production dependency set remains standard-library-only.
- failure_policy: fix_forward

## Task 2: Implement version-3 artifact parsing, validation, and DAG compilation

- task_id: HSC-020
- depends_on:
  - HSC-010
- scope_slice: Create the non-active `runtime/harness` Python CLI and package for one-pass TOML-front-matter parsing, typed design/plan/truth-sync/close schemas, safe repository refs, artifact-DAG validation, plan task compilation, and normalized JSON projection; expose lifecycle namespace commands rather than scalar field getters.
- impl_file_refs:
  - runtime/harness
- test_file_refs:
  - runtime/harness/tests
- verification_scope:
  - Cover one and only one front-matter block, exact artifact kind and version 3, required human-facing Markdown sections, nested task arrays/tables, enum validation, duplicate keys or blocks, malformed TOML, unsafe refs, design-to-plan containment, truth-sync scope, and artifact-DAG identity.
  - Instrument reads so each CLI operation proves each artifact is opened and parsed once; expose no command or import path that returns arbitrary `section + key` values.
  - Compile a validated plan into one stable normalized projection whose digest is independent of dictionary insertion order but sensitive to every authority-bearing field.
  - Reject legacy artifact versions through a typed unsupported-contract stop; do not add a compatibility parser, warning path, or automatic migration.
  - Run focused pytest, Ruff, ty, CLI subprocess tests, and `git diff --check` without selecting the new runtime as active.
- failing_oracle_first: Add version-3 happy-path, malformed-front-matter, legacy-rejection, containment, one-read instrumentation, and normalized-projection cases before implementing the parser and compiler.
- implementation_archetype: Local contract compiler CLI and internal package.
- implementation_language: Python 3 standard library.
- language_rationale: `tomllib`, dataclasses or typed immutable records, pathlib, json, and hashlib provide the required structured parsing and deterministic projection without a runtime dependency or per-field subprocess.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: allowed
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - harness-artifact-contract
- task_review_depth: full
- done_when:
  - The version-3 artifact model is the only code path in the new runtime and all schema, containment, DAG, legacy-rejection, and one-read tests pass.
  - One CLI process produces a complete typed result or normalized projection without invoking `awk`, `rg`, `sed`, `sort`, or `jq` for field extraction.
  - The current active Shell harness remains untouched and usable for executing this version-2 plan.
- failure_policy: fix_forward

## Task 3: Implement ledger, lifecycle, recovery, and evidence state machines

- task_id: HSC-030
- depends_on:
  - HSC-020
- scope_slice: Implement immutable ledger initialization, atomic state transitions, ready-set and convergence rules, touch-set enforcement, external-touch evidence, review evaluation, recovery routing, truth-sync eligibility, close eligibility, classification, and phase routing in the Python runtime using the HSC-010 characterization models and HSC-020 compiled artifact projection.
- impl_file_refs:
  - runtime/harness
- test_file_refs:
  - runtime/harness/tests
  - tests/test_external_touch_evidence.py
- verification_scope:
  - Exercise the complete task-state graph, dependency readiness, retry and repair attempts, batch provenance, conflict and capacity stops, review budget, verification evidence, truth-sync routing, terminal close, and invalid transition rejection as table-driven or model/state-transition tests.
  - Prove ledger initialization stores the exact design and plan digests plus the immutable normalized task projection and replaces ledger files atomically with file and parent-directory durability checks.
  - Prove every later transition reads and validates the ledger once, hashes linked artifacts, compares stored digests, and never invokes plan parsing or full plan validation; digest drift returns the owning typed stop.
  - Preserve repository and exact-external touch-set rules, metadata-only evidence, secret redaction, parent-linked external intents, ownership and mode checks, and no new external mutation authority.
  - Run focused pytest, Ruff, ty, state-model coverage, failure-injection cases for atomic writes, and `git diff --check` while the old runtime remains active.
- failing_oracle_first: Port the transition, touch-set, evidence, truth-sync, and close characterization tables first; add spies that fail if a post-init transition calls artifact parsing or a field subprocess.
- implementation_archetype: Local persistent state-machine CLI.
- implementation_language: Python 3 standard library.
- language_rationale: One typed in-process state model can own validation and atomic persistence without splitting business rules across Shell, jq, and multiple process scans.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: allowed
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - harness-ledger-state
  - harness-external-evidence
- task_review_depth: full
- done_when:
  - Every design-preserved lifecycle and external-evidence invariant has a passing Python model or contract oracle with the same exact accepted state or typed stop.
  - Ledger transitions prove digest-only artifact checks after initialization and no complete plan parse or validation occurs on the transition path.
  - Atomic-write failure cases preserve the last valid ledger and do not silently advance authority.
- failure_policy: fix_forward

## Task 4: Implement binding projection and select codex-native as the default

- task_id: HSC-040
- depends_on:
  - HSC-030
- scope_slice: Implement backend-neutral binding-envelope construction in Python, make flag-absent selection identical to explicit `codex-native`, keep explicit `herdr` as a schema-version-1 projection, preserve allowed main-agent fallback, and remove the unused Herdr adapter helpers accepted as SIM003 without changing live-resource authority.
- impl_file_refs:
  - runtime/harness
  - src/skills/tools/implement-change-via-herdr/scripts/herdr-runtime-adapter.py
- test_file_refs:
  - runtime/harness/tests
  - tests/test_implement_change_via_herdr_contracts.py
  - tests/fixtures/herdr
- verification_scope:
  - Assert flag-absent and explicit codex-native envelopes are equal across task and review bindings, role-file capability validation, all model policies, isolation, touch-set, lock, batch, and fallback conditions.
  - Compare explicit Herdr output byte-for-byte with the HSC-010 golden schema-version-1 fixtures and run the existing fake-Herdr contract suite without semantic weakening or live Herdr access.
  - Preserve distinct typed stops for unavailable required capability, invalid role files, forbidden reviewer or explorer writes, writer isolation, unsupported command-job combinations, depth or feature mismatch, and no-downgrade model policy.
  - Delete `result_string`, `command_job_binding`, and `Adapter.command_run_result`; retain tests for the surviving adapter paths rather than assertions on deleted helper names.
  - Prove neither reusable plan metadata nor the neutral core gains provider model identifiers and no runtime path writes user-owned Codex configuration.
  - Run focused binding and adapter pytest, Ruff, ty, fake-Herdr tests, subprocess-boundary checks, and `git diff --check`.
- failing_oracle_first: Change the flag-absent expectation to codex-native, retain explicit Herdr goldens, and add forbidden-helper and capability-stop cases before implementing the new default and deleting helpers.
- implementation_archetype: Backend-neutral local binding projection inside the lifecycle CLI.
- implementation_language: Python 3 standard library.
- language_rationale: Binding construction is structured validation and projection owned by the same runtime state model; the existing Python Herdr adapter remains a separate explicit terminal-resource adapter.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: allowed
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - runtime-binding-contract
  - herdr-adapter-contract
- task_review_depth: full
- done_when:
  - Omitted backend selection is exactly codex-native, explicit Herdr remains byte-compatible, and all fallback or capability decisions remain controller-owned and typed.
  - The accepted unused Herdr helpers are absent and the unchanged surviving adapter behavior passes its fake-safe test suite.
  - The new runtime has no field subprocesses or provider-specific authority leakage.
- failure_policy: fix_forward

## Task 5: Perform the atomic canonical-skill and shared-runtime cutover

- task_id: HSC-050
- depends_on:
  - HSC-040
- scope_slice: Promote the 39 surviving root-flat `skills/<id>` directories to the sole authored skill tree, point every lifecycle owner at the package-level Python CLI, move runtime ownership exclusively to `runtime/harness`, simplify exposure and activation contracts, delete copied/generated/compatibility/internal surfaces, and apply SIM001-SIM004 as deletions with negative reintroduction guards.
- impl_file_refs:
  - contracts/skills.toml
  - contracts/install-targets.toml
  - contracts/lifecycle.toml
  - runtime/harness
  - scripts/check-contracts.py
  - scripts/check-install-surface.py
  - scripts/flatten-skills.py
  - scripts/generate-skills-index.py
  - scripts/generate-workflow-diagrams.py
  - scripts/install.sh
  - scripts/skill_activation.py
  - skills
  - skills.index.json
  - src/runtime/harness
  - src/skills
- test_file_refs:
  - runtime/harness/tests
  - src/runtime/harness/smoke-test
  - tests
- verification_scope:
  - Preserve each surviving skill's authored content and resources while moving it from the categorized source path; derive directory/public identity from the `[skills.<id>]` table key and retain only activation, role, semantic, plane, and provider-projection metadata that still has an owner.
  - Delete `clean-architecture`, `quality-standards`, and `security-logging`; remove `helper`, `superseded_by`, redundant `source`, `public_id`, `install`, target arrays, semantic-install profiles, `runtime_bundle`, internal category handling, and `include_internal_runtime_support`.
  - Delete `src/skills`, `src/runtime/harness`, six `skills/*/scripts/harness` bundles, `.source-map.json`, `contracts/install-targets.toml`, `scripts/flatten-skills.py`, `scripts/check-install-surface.py`, and `scripts/install.sh`; retain no symlink or compatibility wrapper.
  - Apply SIM001 by deleting `router.sh` and router-only tests; SIM002 by proving the six dead artifact-DAG set helpers are absent; SIM003 by deleting both unused `load_manifest` helpers and `task_is_dependency_free` in addition to HSC-040's adapter cuts; SIM004 by deleting internal install schema and branches.
  - Update lifecycle skill instructions to resolve `../../runtime/harness/cli.py` from their package root and invoke one Python process per operation; prove both complete plugin roots contain the same 39 skills and shared runtime with no skill-local copy.
  - Keep Codex invocation policy derived from `activation_mode` through an in-place `agents/openai.yaml` projection check; regenerate only metadata/index/diagram views, never a second content tree.
  - Run focused skill exposure, activation, routing, successor-ownership, package-closure, shared-runtime resolution, forbidden-path, and exact-39-set tests plus the new runtime suite before declaring the cutover coherent.
- failing_oracle_first: Rewrite package and contract tests to the approved single-source/single-runtime boundary first, including exact forbidden paths and IDs; require the pre-cutover tree to fail those intentional-change tests while the HSC-010 behavior matrix remains green.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: allowed
- execution_profile: deep
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - canonical-skill-tree
  - shared-runtime-cutover
  - plugin-package-contract
- task_review_depth: full
- done_when:
  - Exactly one authored 39-skill tree and one package-level Python runtime remain, both maintained plugin roots resolve them, and no retired source, bundle, compatibility skill, internal schema, or generator path survives.
  - SIM001-SIM004 names and implementations are absent, while surviving owner and negative reintroduction tests pass.
  - All lifecycle skills call the shared CLI once per operation and the repository contains no business-rule compatibility wrapper.
- failure_policy: fix_forward

## Task 6: Reduce the aggregate checker to thin serial orchestration

- task_id: HSC-060
- depends_on:
  - HSC-050
- scope_slice: Rewrite `scripts/check.sh` and the pre-commit hook around the final ownership graph: deterministic repository preflight, one call per contract/index/diagram or package checker, one Ruff lane, one ty lane, one pytest discovery lane, one Markdown check, and no generated install-surface or per-smoke-test loop.
- impl_file_refs:
  - hooks/pre-commit
  - scripts/check.sh
  - scripts/check-contracts.py
  - scripts/generate-skills-index.py
  - scripts/generate-workflow-diagrams.py
  - scripts/skill_activation.py
- test_file_refs:
  - runtime/harness/tests
  - tests
- verification_scope:
  - Replace the twelve Shell smoke-test entrypoints with in-process pytest modules that own their migrated assertions; retain a Shell-specific test only for `scripts/check.sh` and hook quoting, strict mode, interpreter, exit propagation, and exact command sequencing.
  - Assert each checker and generator is invoked once, pytest discovery occurs once, no retry or background parallelism masks failure, and the first failed owned gate returns its exit status with a clear label.
  - Retain `.dist/` in `.gitignore` as an inert local cache/output boundary while removing every generator, contract, and validation branch that creates or consumes it; do not enumerate, delete, expose, or normalize its existing local contents.
  - Export the five exact C0 cache locations inside `scripts/check.sh` before invoking uv, Ruff, Python, or pytest; the script may not write a repository-local `.venv`, `.ruff_cache`, `.pytest_cache`, `__pycache__`, or unrelated external cache path.
  - Trace representative design validation, plan validation, ledger initialization, one ledger transition, and close evaluation to prove no field-at-a-time `awk`, `rg`, `sed`, `sort`, or `jq` child process is launched.
  - Run `bash -n`, ShellCheck when available, the focused check-orchestration test, one full pytest discovery, Ruff, ty, and `git diff --check`.
- failing_oracle_first: Add a fake-command-path orchestration test that records argv and counts invocations, plus subprocess-spy tests for representative runtime operations, before simplifying `scripts/check.sh` or deleting the looped smoke entrypoints.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: allowed
- execution_profile: balanced
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - aggregate-check-contract
  - repository-test-discovery
- task_review_depth: full
- done_when:
  - `scripts/check.sh` is bounded Shell orchestration with no structured parsing, state transition, target generation, retry, hidden parallelism, or loop over independent smoke scripts.
  - All migrated runtime assertions execute through one pytest discovery lane and focused checks prove exact command count and failure propagation.
  - The aggregate path performs no duplicate full plan validation during ledger transitions and no field subprocess parsing.
- failure_policy: fix_forward

## Task 7: Converge stable truth, generated views, and mutable Markdown

- task_id: HSC-070
- depends_on:
  - HSC-060
- scope_slice: Materialize the HWR-001 immutable exception manifest and optional normalizer interface, normalize every non-exempt Git-visible Markdown file after semantic edits, update stable repository and architecture truth for the canonical skill/runtime/default-backend boundaries, remove retired compatibility/trial/standalone-install claims, and regenerate the skill index plus PlantUML and SVG views once.
- impl_file_refs:
  - AGENTS.md
  - README.md
  - contracts/markdown-prose.toml
  - docs/architecture
  - docs/changelog/design-decisions.md
  - scripts/generate-skills-index.py
  - scripts/generate-workflow-diagrams.py
  - skills
  - skills.index.json
- test_file_refs:
  - tests/test_markdown_prose_wrap.py
  - tests
- verification_scope:
  - Add an optional `--immutable-manifest` normalizer argument whose default remains full Git-visible scanning; validate exact path/digest/type/visibility/under-`docs/plans` constraints and refuse write-mode enrollment or digest refresh.
  - Populate exactly the ten HWR-001 path-and-digest records from this plan; assert each listed file still contains a preserved legacy finding and every listed digest matches before and after all normalization.
  - Run `count`, bounded `preview`, `write`, and `check` with the manifest only after the canonical tree exists; require zero findings outside exceptions and unchanged semantic/structure fingerprints for every rewritten file.
  - Keep this design, this plan, new artifacts, stable docs, and all canonical skills outside the exception manifest; manually decompose genuinely over-broad prose at semantic boundaries without fixed-column wrapping.
  - Remove active claims that codex-native is experimental, three user trials are required, compatibility IDs remain, `src/skills` is canonical, runtime bundles are copied, `.dist` is generated, or `npx skills` supplies a supported executable harness.
  - Update AGENTS validation commands, README layout/install guidance, architecture source/runtime/invocation/workflow truth, decision log, index, PlantUML, and SVGs from final contracts; do not edit generated diagrams by hand.
  - Re-run exact fixed-string searches over active truth and the read-only `~/.codex/AGENTS.md` check, the Markdown checker, generator checks, and `git diff --check`.
- failing_oracle_first: Add manifest-validation, digest-drift, implicit-enrollment, unlisted-new-artifact, and zero-non-exempt-finding tests before adding exception support or running write mode.
- executor_mode: subagent
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: allowed
- execution_profile: balanced
- reasoning_profile: deep
- isolation: isolated-worktree
- resource_locks:
  - stable-truth-convergence
  - markdown-prose-contract
  - generated-architecture-views
- task_review_depth: full
- done_when:
  - Stable truth and generated views agree on the exact 39-skill canonical tree, one shared Python runtime, codex-native default, explicit Herdr path, retired compatibility/install surfaces, and thin aggregate checker.
  - The normalizer reports zero non-exempt findings, all ten exception digests remain exact, and no new or modified Markdown artifact is exempt.
  - No active source or stable truth contains the retired three-trial decision horizon or advertises unsupported standalone executable-harness installation.
- failure_policy: fix_forward

## Task 8: Run complete offline acceptance and bounded implementation review

- task_id: HSC-080
- depends_on:
  - HSC-070
- scope_slice: Verify the final repository as one coherent cutover, inspect the exact diff and deleted paths, run every declared local oracle once through its owning lane, validate both plugin package surfaces and the official Codex manifest, perform bounded implementation review, and route only causally accepted findings to their owning prior task.
- impl_file_refs:
  - none
- test_file_refs:
  - none
- verification_scope:
  - Re-run the installed pre-cutover design and plan validators before the old bundle is removed from the active implementation environment, and retain their passing evidence with the immutable plan digest.
  - Run `uv lock --check` and Bash syntax separately, then invoke the simplified `bash scripts/check.sh` exactly once as the sole final owner of Ruff, ty, pytest discovery, repository checker/generator calls, direct package checks, and Markdown checking; afterward run the separate official Claude and Codex plugin validators, exact external-name search, and `git diff --check`.
  - Verify exact changed paths are contained by this plan, all expected deletions occurred, no immutable stage-history path changed, `~/.codex/AGENTS.md` contains none of the three retired IDs, and no unauthorized external write occurred outside the five C0 tool-cache prefixes.
  - Compare final package closure for Claude and Codex, exact 39-skill identity, shared runtime resolution, no skill-local bundles, no `.dist` generation, and no source/generated content duplication.
  - Compare representative parser and ledger subprocess traces with the recorded baseline and require the structural one-process/one-read oracles; wall-clock improvement is evidence but not the acceptance criterion.
  - Route the exact task diff, task tests, declared oracles, and justified direct dependencies through one initial bounded implementation review and at most one focused verification review after accepted repair.
- executor_mode: main
- parallel_group: none
- parallel_policy: forbidden
- delegation_policy: forbidden
- execution_profile: deep
- reasoning_profile: deep
- isolation: controller-checkout
- resource_locks:
  - final-repository-acceptance
- task_review_depth: full
- done_when:
  - Every focused and aggregate oracle passes without retries, test weakening, historical mutation, unauthorized external write outside the five C0 tool-cache prefixes, plugin installation, commit, or push.
  - The main controller adjudicates all review candidates, no accepted finding remains, and implementation verification is recorded as passing.
  - Successful execution returns one immutable result bound to this approved design, plan, task ledger, review, verification, changed paths, and declared stable truth refs, then routes to `sync-truth` rather than close.
- failure_policy: fix_forward

## Truth Sync Handoff

- stable_truth_refs:
  - AGENTS.md
  - README.md
  - contracts/markdown-prose.toml
  - contracts/skills.toml
  - contracts/lifecycle.toml
  - docs/architecture
  - docs/changelog/design-decisions.md
  - skills
  - skills.index.json
- docs_governance_predicates:
  - readme-agents-claude-ownership
  - stable-truth-roots
  - decision-record-lifecycle
  - docs-search-boundaries
  - stage-artifact-placement
  - canonical-terminology-across-surfaces
  - markdown-prose-structure
- handoff_condition: Prepare truth-sync only after HSC-080 records passing implementation review and verification against the exact approved plan and confirms that every stable truth ref is inside the unchanged approved touch set.
- human_gate: Truth-sync approval remains separate; successful implementation does not authorize truth approval, close, commit, push, plugin refresh, or publication.

## Review Gate

- required_entry: review-change
- review_component: review-plan
- actor_role: main
- reviewer_actor_role: delegated
- review_depth: boundary
- review_status: passed_after_two_bounded_reviews
- review_surface: This plan and its exact diff; the approved design; `AGENTS.md` and `docs/AGENTS.md` for lifecycle and stage-history boundaries; `contracts/skills.toml`, `contracts/install-targets.toml`, and `contracts/lifecycle.toml` for current source/runtime/task authority; `scripts/check.sh` for the current aggregate topology; `src/runtime/harness/plan-runner.sh` for version-2 validation; and the repository normalizer plus ten current file hashes for HWR-001.
- candidate_findings: Four high-confidence plan-introduced candidates were accepted: undeclared tooling-cache writes contradicted C0/X5; removing `.dist/` ignore would expose retained local output to the Markdown scanner; final validation duplicated lanes owned by `scripts/check.sh`; and the first cache-authority repair left two HSC-080 assertions forbidding even authorized cache writes.
- adjudication: The plan now binds ephemeral writes to five exact task-specific cache prefixes and forbids all others; retains ignored `.dist/` state outside the touch and scan surfaces while retiring its generators; makes `scripts/check.sh` the sole final owner of Ruff, ty, pytest, repository checker/generator, direct package, and Markdown lanes; and states HSC-080's external-write oracle in terms of unauthorized writes outside C0. No candidate was rejected or deferred.
- review_evidence: The delegated initial review and one focused verification review stayed within the bounded brief. Main-agent verification confirms `.gitignore` is absent from the plan touch set, `.dist/` remains ignored, final validation has one aggregate invocation, all cache-authority statements agree, the version-2 plan validator passes after repair, and the plan adds no hard-wrap finding.
- pass_rationale: The repaired plan is contained by the approved design, has an acyclic serial DAG and executable oracles, preserves immutable history and explicit Herdr compatibility, declares complete local and cache authority, and can run continuously after approval without an internal validation contradiction.
- max_review_batches: 2

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: implement-change
- implementation_entry_condition: Explicit approval of this reviewed plan authorizes continuous HSC-010 through HSC-080 repository-local execution under C0 and the declared X* stops; it does not authorize later truth-sync, close, commit, push, install, new-thread acceptance, or publication gates.
