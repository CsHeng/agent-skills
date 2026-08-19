# Harness Simplification And Codex-Native Cutover Design

## Status

- design_version: 3
- decision_status: ready_for_plan
- approval_required: true
- approval_status: approved
- approval_basis: Version 1 was explicitly approved on 2026-08-18. After focused review exposed the byte-digest conflict in the requested hard-wrap cleanup, the user explicitly selected HWR-001 option A on 2026-08-18; the prior approval and `$coding:plan-change` request therefore apply to this reviewed version 3 boundary.
- recommended_next_phase: plan
- next_entry: plan-change

## Problem

The repository currently pays for the same harness and skill truth through several parallel representations:

- authored skills live in a category-nested `src/skills/` tree, while a complete root-flat copy is tracked under `skills/` for the two plugin manifests
- fourteen production harness files are copied into each of six generated workflow skills
- lifecycle artifacts store machine fields as Markdown bullets, and Bash code starts a new `awk`, `rg`, `sed`, `sort`, or `jq` process for individual field reads and repeated validation
- compatibility-only public skills and extinct internal-install schema remain in the active contract even though their successor owners are established
- the implemented codex-native binding backend is still described as an experiment and the flag-absent runtime default remains Herdr

The accepted SIM001-SIM004 cuts remove local dead code, but applying them without changing these ownership boundaries would leave the dominant duplication and validation cost intact. The user has explicitly accepted SIM001-SIM004, selected codex-native as the default without the former three-trial comparison gate, authorized compatibility-skill removal, and allowed a breaking cutover.

## Goals

- Apply the accepted SIM001-SIM004 deletions without changing their surviving callers' behavior.
- Make codex-native the flag-absent delegated runtime backend and remove the three-way, three-user-run experimental decision horizon.
- Delete `clean-architecture`, `quality-standards`, and `security-logging`; their established successors remain the only owners.
- Replace the authored/generated full-skill duplication with one canonical flat skill tree consumed directly by both maintained plugin paths.
- Replace six owner-local harness copies with one plugin-level runtime.
- Keep `scripts/check.sh` as thin orchestration while moving lifecycle parsing, validation, state, and business rules out of Shell.
- Replace distributed Markdown key/value storage with a versioned structured contract that is parsed once and remains reviewable in the same Markdown artifact.
- Make ledger transitions consume an immutable compiled projection and artifact digests instead of revalidating the complete plan on every transition.
- Preserve lifecycle authority, human gates, task topology, touch-set checks, external-file evidence, review adjudication, and explicit Herdr selection.
- Resolve HWR-001, then remove every hard wrap inside the explicitly approved Markdown scope with the repository-owned normalizer while preserving Markdown structure and non-whitespace content.

## Non-Goals

- No implementation, plugin reinstall/update, new Codex thread, commit, push, publication, or live provider action during design.
- No compatibility guarantee for retired skill IDs, standalone selective skill installs, legacy plan contract versions, or direct invocation of the old Shell runner paths after cutover.
- No removal of the Herdr backend or `implement-change-via-herdr`; it remains an explicit backend for its distinct terminal and command-job capabilities.
- No change to approved plan topology, delegation authority, isolation, resource locks, touch sets, executable oracles, truth-sync gate, or close gate.
- No rewrite of digest-bound stage history until HWR-001 explicitly selects either byte preservation or full artifact-chain reissuance; formatting-only intent does not by itself make an approved byte identity mutable.
- No generic plugin-runtime loader, multi-language framework, daemon, cache service, or new third-party runtime dependency.
- No edit to `~/.codex/AGENTS.md`; the required exact-name check currently finds no reference to any of the three compatibility skills.

## Change Classification

- request_kind: change-definition
- change_class: C
- design_strength: design-full
- truth_impact: high
- boundary_impact: high
- truth_repair: false
- truth_sync_required: true
- parallel_candidate: false

## Evidence Baseline

- baseline_revision: `516a5e368046645cb48d4cb119e711e4b4cc2eb7`
- baseline_worktree: clean; local `main` is one commit ahead of `origin/main`
- runtime_duplication: The production harness is fourteen files, 8,150 lines, and 302,665 bytes. The same payload is tracked in each of six generated workflow skills, adding 48,900 repeated lines and 1,815,990 repeated bytes.
- skill_duplication: `src/skills/` contains 141 files and 738,123 bytes; generated `skills/` contains 226 files and 2,558,602 bytes, mostly because it repeats the authored tree and six harness bundles.
- parser_process_cost: Validating `2026-08-17-codex-native-binding-plan.md` took 3.236 seconds and an execution trace observed 264 `awk`, 21 `rg`, 69 `sed`, and 16 `sort` starts.
- ledger_process_cost: Building the task ledger for the same plan took 12.57 seconds; an execution trace observed 908 `awk`, 64 `rg`, 263 `sed`, 48 `sort`, and 82 `jq` starts.
- suite_localization: `test-artifact-dag.sh` completed in 0.89 seconds, while `test-close-runner.sh` had not completed after 130.23 seconds and the diagnostic benchmark was stopped. This is evidence about the current local baseline, not a passing aggregate result.
- repeated_validation: `task-ledger.sh` has six call sites that perform complete execution-grade plan validation before later state or evidence operations, in addition to validation during catalog and ledger construction.
- consumer_evidence: The installed Codex plugin cache contains the complete repository package, including `src/runtime/harness`, and both maintained plugin paths operate on the repository/plugin root rather than an isolated copied skill directory.
- global_wrapper_check: An exact fixed-string search of `~/.codex/AGENTS.md` found no `clean-architecture`, `quality-standards`, or `security-logging` reference.
- hard_wrap_inventory: The repository-owned normalizer scanned 267 Git-visible Markdown files and found 1,222 safe prose-continuation joins across thirteen files. Ten are historical or stage files under `docs/plans/changes/`, one is this design, and two are the authored/generated copies of `sync-truth/SKILL.md` that collapse to one canonical file during the selected skill-tree cutover.
- hard_wrap_digest_conflict: After this design was normalized, twelve files and 967 joins remain. Ten are retained stage-history artifacts and two are the authored/generated `sync-truth/SKILL.md` copies. At least three affected stage artifacts are still byte-identical to SHA-256 values embedded in downstream approval or evidence artifacts: the codex-native binding plan is `c7115414acbf07db3e9c3337ba9f5ca2feef31d2d612a444e69e3ed8777e2b7d`, the user-route input is `21a0c38ecad5d2dce2dda797409747c5622b092ec9ae4aa5a7735a6ef6bcf1df`, and the E2 design is `c5ca7faf092d67c2f0ad104d3f77ea7fe1363c8a5a5feca49d623f227e17707c`. Removing only continuation newlines would change those identities and invalidate their current references.

## Boundaries

### D1: Accepted Dead-Code Cuts

The implementation deletes the following accepted candidates rather than retaining deprecated wrappers:

- SIM001: delete `router.sh` and the router-only smoke assertions. Routing truth remains in the installed routing contract and lifecycle phase contracts.
- SIM002: delete `build_review_read_surface`, `path_is_within_allowed_roots`, `intersect_paths_from_array`, `subtract_paths_from_array`, `intersect_paths_from_surfaces`, and `subtract_paths_from_surfaces`. Active touch-set and external-boundary checks remain.
- SIM003: delete both unused `load_manifest` helpers, `task_is_dependency_free`, and the unused Herdr adapter helpers `result_string`, `command_job_binding`, and `Adapter.command_run_result`.
- SIM004: delete support for category `internal`, `include_internal_runtime_support`, internal target branches, and the obsolete lower-plane `internal` category. Keep negative checks proving no public `_harness-libs` pseudo-skill or retired sibling-runtime reference reappears.

These deletions do not create compatibility shims. Tests must exercise surviving owners and forbidden reintroduction, not the deleted implementation names.

### D2: Codex-Native Is The Default Backend

The runtime binding contract changes `flag_absent_binding_backend` from `herdr` to `codex-native`. An omitted backend selector therefore emits the codex-native schema and applies the existing Codex role-file and capability validation. Herdr requires explicit `--backend herdr` selection or explicit `implement-change-via-herdr` composition.

The former three-way comparison among codex-native, Herdr, and main-agent serial execution and its three-user-run evidence threshold are removed from active README, architecture, skill, and contract truth. Codex-native is recorded as a selected default by explicit user decision; repository truth must not claim that the retired trials were performed. Deterministic codex-native fixtures remain the correctness gate. Main-agent serial execution remains the fallback only when the unchanged approved task and delegation policy already allow it.

Herdr's explicit `schema_version: 1` projection and adapter behavior remain protected. The intentional default change updates only flag-absent expectations; explicit Herdr contract tests must remain semantically unchanged except for paths caused by the runtime move.

### D3: Compatibility Skill Removal

Delete the three compatibility-only public entries and their generated output:

- `clean-architecture`; successor `architecture-patterns`
- `quality-standards`; successor `development-standards`
- `security-logging`; successor `logging-standards`

After deletion, remove now-unused `superseded_by` graph validation and the `helper` default role. Tests retain assertions that the successor skills own the underlying architecture, development-quality, and logging guidance. Routing, indexes, diagrams, and prose must contain no active reference to the retired IDs. A pre-implementation and final read-only exact-name check of `~/.codex/AGENTS.md` must still return no match; external user configuration is not part of the write surface.

### D4: Canonical Flat Skill Source

Promote `skills/` from a generated projection to the sole authored skill-content tree. Move each surviving source directory from its category path under `src/skills/` to `skills/<public-id>/`, then delete `src/skills/`. Logical planes and categories remain contract metadata; they no longer force a second physical copy of every skill.

The `[skills.<id>]` table key becomes the canonical public ID and directory name. Remove redundant `source`, `public_id`, and `install` fields: every retained skill is consumed by both maintained plugins, and the current contract confirms all 42 entries have the same `claude`, `codex`, and `root-flat` target list. After the three compatibility deletions, the exact canonical set is 39 skills.

Codex `policy.allow_implicit_invocation` remains derived from `activation_mode`, not independently authored. A small in-place metadata projection updates only that generated policy block in `skills/<id>/agents/openai.yaml`; the interface fields and skill content remain authored. Contract validation proves the block is current. `skills.index.json` and architecture diagrams remain generated views.

Delete root-flat source maps, `.dist` target generation, `flatten-skills.py`, `check-install-surface.py`, and `contracts/install-targets.toml`. Remove the obsolete semantic-install profile and target arrays. Both plugin manifests continue consuming the canonical `skills/` directory in the repository package, so no copied install surface is needed for validation.

### D5: One Plugin-Level Harness Runtime

Move the canonical harness from `src/runtime/harness/` to `runtime/harness/`. Runner-owning skills resolve the shared root from their own location:

```text
skills/<owner>/ -> ../.. -> runtime/harness/
```

The six workflow skills no longer contain or generate `scripts/harness/` copies, and `runtime_bundle = "harness"` is removed. Package validation proves that both maintained plugin roots contain `skills/` and `runtime/harness/`, that all runner references resolve inside the same package, and that no skill-local harness copy exists.

This is a deliberate distribution cutover. Claude and Codex plugin installation remain supported because they install the complete plugin root. Standalone or selective installation of an individual lifecycle skill, including the previous advisory `npx skills` route, is no longer a supported executable harness path and is removed from active documentation and contracts. This narrower product boundary buys a single runtime owner without inventing symlinks, loaders, or install-time mutation.

### D6: Structured Lifecycle Artifacts

New lifecycle artifacts use contract version 3. Machine-consumed metadata lives in one TOML front-matter block at the start of the Markdown file; narrative sections remain ordinary Markdown for human review. A plan uses arrays and tables, including `[[tasks]]`, instead of repeated `section + key` bullet lookups. Design and truth-sync artifacts use the same envelope convention with artifact-specific schemas.

The runtime accepts exactly one front-matter block, parses it with Python's standard-library `tomllib`, validates the declared artifact kind and version, and reads the Markdown body only for required human-facing sections. It does not offer a field-at-a-time extraction command. One invocation reads each artifact once and produces one typed in-memory model and, where required, one normalized JSON projection.

Legacy contract versions remain historical evidence but are not accepted by the post-cutover runtime. No dual parser, warning period, migration command, or automatic rewrite is retained. The approved plan that implements this change is executed by the pre-cutover installed harness; after plugin refresh, newly authored artifacts use version 3.

### D7: Python Owns Parsing, Validation, And State

The shared runtime becomes a standard-library Python CLI and internal package. It owns artifact schema validation, artifact-DAG checks, classification and phase rules, task-ledger construction and transitions, recovery routing, truth-sync and close decisions, binding-envelope construction, and external-touch evidence. Shell owns only thin repository orchestration such as `scripts/check.sh` and hooks that invoke the Python entry point.

The CLI exposes lifecycle namespaces rather than field getters, for example `design validate`, `plan validate`, `ledger init`, `execute bind`, `truth-sync evaluate`, and `close evaluate`. Exact command spelling is fixed in planning, but each operation must cross the Python boundary once. Reusable rules must not be split between Shell and Python.

Ledger initialization compiles the approved plan and linked design into an immutable normalized projection and records both SHA-256 digests. Later state transitions load and validate the ledger once, hash the referenced artifacts, and compare those digests. They do not parse or fully validate the plan again. Digest drift returns a typed stop requiring a new compiled ledger; it never silently refreshes authority.

`scripts/check.sh` remains the aggregate entry point because serial gate orchestration is an appropriate Shell responsibility. It performs repository preflight, invokes each generator/checker once, and runs one Python test discovery entry. The twelve Shell smoke tests are replaced by in-process Python unit, contract, state-machine, and CLI boundary tests; a small Shell test remains only where Shell behavior itself is the subject.

### D8: Authority And Failure Invariants

The cutover changes representation and implementation language, not authority. The Python model must preserve:

- one sovereign lifecycle owner per phase and explicit human approvals
- plan-owned topology and implementation-controller-owned runtime binding
- exact task states, ready-set rules, convergence ownership, and review budget
- repository and external touch-set validation
- immutable evidence digests and atomic ledger replacement
- explicit fix-forward versus guarded-rollback semantics
- typed capability, drift, recovery, review, truth-sync, and close stops
- secret-safe external evidence and no new external mutation authority

No test may weaken an exact error, state, permission, or boundary assertion merely to make the new implementation pass.

## Decision Discovery

### HWR-001: Byte-Digest-Bound Stage History

- decision_status: selected
- question: Should repository-wide hard-wrap removal preserve approved stage artifacts byte-for-byte, or reissue every affected artifact chain under new digests?
- evidence: The normalizer finds continuation joins in retained `docs/plans/changes/` history. Current bytes of the codex-native binding plan, user-route input, and E2 design exactly match SHA-256 identities embedded in downstream plan, review, verification, or truth-sync evidence. Normalization would therefore change approval identity even when semantic and structure fingerprints remain stable.
- option_a_recommended: Enforce zero hard wraps on active and mutable Markdown, including the canonical skill tree and every artifact created or materially revised by this change, while preserving existing `docs/plans/` history byte-for-byte through an explicit immutable-history exclusion in the checker.
- option_b_full_reissuance: Normalize all affected stage history, create a complete old-digest-to-new-digest migration record, rebuild every transitive design, plan, input, review, verification, truth-sync, close, and ledger reference, and obtain new approval for each reissued chain before treating it as authoritative.
- rejected_implicit_choice: Do not silently rewrite digest values in place, claim semantic fingerprints preserve byte identity, or reinterpret the current request as retroactive approval of every downstream artifact chain.
- resolution: option_a_selected_by_user_on_2026-08-18
- implementation_requirement: Add a repository-owned immutable Markdown exception manifest containing only the ten currently affected stage-history files and each file's approved pre-change SHA-256. The normalizer and aggregate check may skip an exception only while its repository-relative path and digest match exactly; all other Git-visible Markdown, including this design, its execution plan, newly created stage artifacts, stable docs, and canonical skill content, remains in the zero-hard-wrap scope.

### D9: Markdown Hard-Wrap Removal

The selected option preserves the ten existing affected stage-history artifacts byte-for-byte and removes hard wraps from every other Git-visible Markdown file. `contracts/markdown-prose.toml` owns the narrow immutable exception manifest as exact repository-relative path and SHA-256 pairs; it is not a glob, directory exclusion, or general permission for wrapped stage prose. A missing path, unexpected type, digest mismatch, duplicate entry, path outside `docs/plans/`, or manifest entry that no longer contains a hard-wrap finding is a deterministic failure rather than a silent skip.

Run the `organize-docs` bundled normalizer after the canonical skill-tree move and semantic edits are complete, so the deleted source/generated duplicate is not normalized twice and newly written Markdown is included. The task may only remove prose continuation newlines classified by the tool and must preserve frontmatter, headings, tables, fenced and indented code, list structure, blockquote structure, reference definitions, HTML-only lines, explicit hard breaks, file mode, and all non-whitespace content.

The final check reports zero hard wraps outside the exact digest-bound manifest and independently verifies that all ten exception files retain their approved bytes. Any new finding outside the approved implementation surface returns `needs_plan_change` rather than widening the touch set. The checker must never rewrite, refresh, or auto-enroll an immutable exception.

## Architecture Decision Economics

- architecture_decision_id: HSC-001-canonical-plugin-runtime
- decision_status: selected
- decision_horizon: The maintained local Claude and Codex plugin distribution model; reconsider only when a supported consumer requires standalone skill closure or a provider can consume categorized skill sources directly.
- demand_evidence: Six identical runtime bundles add 48,900 tracked generated lines; the complete skill tree is authored and tracked twice; representative plan validation and ledger initialization start hundreds of subprocesses and take 3.236 and 12.57 seconds respectively.
- scarce_resource: Maintainer review bandwidth, deterministic validation time, generated-diff signal, and correctness capacity for a stateful lifecycle engine implemented in Shell.
- hard_requirements:
  - both maintained plugin paths remain installable from the repository root
  - activation metadata remains contract-derived
  - artifact, ledger, touch-set, and lifecycle authority remain deterministic
  - no new third-party runtime dependency
  - no unsupported standalone-runtime promise after centralization
- options:
  - status_quo: Keep nested authored skills, generated root-flat copies, six harness bundles, Markdown bullet parsing, and Bash state transitions. Rejected because it preserves the measured dominant costs and continues to reward compatibility and projection growth.
  - smallest_local_patch: Keep both skill trees and the Shell state machine, but add one Python Markdown parser and stop selected duplicate validations. Rejected because it leaves two content owners, six runtime copies, and splits lifecycle rules across Shell and Python; it treats the current symptoms without restoring a clear ownership boundary.
  - selected_structural_cutover: One authored flat skill tree, one plugin-level Python runtime, TOML-front-matter artifact contracts, and ledger digest checks after one-time compilation. Selected because the current plugin package already supplies the whole-root boundary and Python/tomllib is already a repository prerequisite.
  - larger_framework: Add a generic runtime plugin system, external schema framework, persistent cache, daemon, or provider-specific packages. Rejected because there is one repository owner and no measured need for distribution or runtime coordination beyond a local CLI.
- marginal_tradeoff: The one-time path and artifact-format cutover is broad, but it removes both recurring full-tree generation and the highest-cost process topology. Keeping the old format or standalone closure would retain most of the cost and require dual-path maintenance.
- opportunity_cost: The migration consumes a full reviewed implementation milestone and delays smaller policy work; that cost is bounded by refusing a compatibility period, generic framework, or historical-artifact rewrite.
- owner_and_incentives: `contracts/skills.toml` owns exposure and activation; `skills/` owns skill content; `runtime/harness/` owns lifecycle execution; plugin manifests own whole-package distribution; `scripts/check.sh` owns only aggregate sequencing. Maintainers receive and bear the simplification cost at the same boundaries.
- comparative_advantage: Python's standard library owns structured parsing, validation, JSON/TOML data, state transitions, and testable modules at lower lifecycle cost; Shell remains best for short environment and command orchestration; the plugin providers already own package delivery.
- chosen_option: A breaking whole-plugin cutover to a canonical flat skill tree and one Python harness runtime, with codex-native as the default backend.
- upgrade_trigger:
  - A concrete supported standalone-skill consumer triggers a separately designed packaging artifact, not renewed checked-in runtime copies.
  - A provider-supported recursive skill root with equivalent metadata semantics can trigger restoration of categorized physical directories without a generated full-tree projection.
  - A measured Python startup bottleneck after subprocess elimination can trigger profiling; it does not justify a daemon or Go binary in advance.
- recovery_and_oracle: The cutover lands only after source and installed-package contract tests, v3 artifact/state fixtures, explicit Herdr compatibility fixtures, codex-default fixtures, and aggregate validation pass. Before merge, failure keeps the old surface intact; after merge, recovery is a normal revert of the repository change followed by a separately authorized plugin refresh.

## Language Decision

- implementation_archetype: Local lifecycle contract compiler and state-machine CLI distributed inside the plugin package.
- implementation_language: Python 3 using only the standard library.
- language_rationale: The repository already requires Python and uses `tomllib`; the boundary is dominated by structured parsing, validation, JSON, hashing, atomic file replacement, and state-machine tests. It needs neither a separately released binary nor concurrent network service behavior. Shell is retained only for short orchestration, consistent with its established boundary.
- tooling_contract: `pyproject.toml` owns the Python version and Ruff, ty, and pytest configuration; `uv.lock` pins development-only validation tools. The installed harness runtime itself imports only the Python standard library and has no third-party runtime dependency.

## Oracle Strategy

- protected_boundary: Public skill exposure, plugin package closure, artifact schema and DAG, task-ledger state machine, touch-set authority, runtime backend selection, external evidence, and lifecycle gates.
- behavior_status: Existing lifecycle behavior is legacy-current and must be characterized; the skill IDs, distribution boundary, artifact format, and default backend listed above are intentional breaking changes.
- oracle_owner: Python harness tests own runtime semantics; contract tests own skill and plugin surfaces; explicit backend fixtures own envelope behavior; generator checks own metadata, index, and diagrams.
- selected_methods:
  - Characterization fixtures preserve current valid/invalid lifecycle invariants and typed stops before the Shell implementation is deleted.
  - Contract-version-3 fixtures cover design, plan, task, external touch, truth-sync, and close schemas, including malformed or duplicate front matter.
  - Model/state-transition tests cover ready-set order, dependency completion, conflicts, retries, convergence, review, truth sync, and close decisions.
  - Golden/contract tests keep explicit Herdr schema-version-1 envelopes stable and make flag-absent output equal explicit codex-native output.
  - Package-surface tests prove the exact 39-skill set, derived Codex policy, absent compatibility IDs, one shared runtime, and no skill-local runtime bundle.
  - Instrumented parser tests prove each artifact is read once per validation or compilation and that ledger transitions perform digest checks without invoking artifact parsing.
  - A subprocess-boundary test proves harness operations launch no field-at-a-time `awk`, `rg`, `sed`, `sort`, or `jq` helpers.
  - The repository-owned Markdown normalizer supplies count, bounded preview, semantics-preserving write, exact immutable-exception digest verification, and a final zero-finding result outside those exceptions; review verifies that its mutable-file diff contains only removed continuation newlines.
- discarded_methods: Wall-clock-only thresholds, broad snapshots of generated trees, live Codex/Herdr runs, historical plan migration, and test weakening do not prove the selected boundaries.
- oracle_change_policy: Deleting or relaxing lifecycle, touch-set, state, approval, backend, or evidence assertions requires a new reviewed design decision, not implementation repair.

## Acceptance Conditions

- SIM001-SIM004 named code and schema are absent, and surviving owner tests pass.
- `clean-architecture`, `quality-standards`, and `security-logging` are absent from the active contract, canonical skills, routing/index/diagram output, and stable docs; their successor-owner tests remain.
- An exact read-only search of `~/.codex/AGENTS.md` still finds none of the three retired IDs, and that external file remains unmodified.
- An omitted runtime backend selector is identical to explicit `codex-native`; explicit `herdr` retains its schema-version-1 contract.
- No active truth requires three user-run trials or describes delegated execution as awaiting the former comparison. No truth claims those trials occurred.
- `skills/` is the only authored skill-content tree; `src/skills/`, root-flat source maps, target flattening, and redundant per-skill source/public/install fields are absent.
- Both maintained plugin packages expose the same canonical 39-skill tree and package-level `runtime/harness/`; no workflow skill contains `scripts/harness/`.
- Active install documentation supports whole Claude/Codex plugins only and does not advertise the retired standalone `npx skills` executable-harness route.
- New artifacts use one version-3 TOML front-matter contract plus human Markdown; legacy versions are rejected without a retained compatibility parser.
- Plan compilation reads and validates the plan and linked design once, emits a normalized immutable projection, and stores their digests in the ledger.
- Every later ledger transition validates the ledger and artifact digests but performs no complete plan parse or validation; drift returns a typed stop.
- Harness parsing, validation, lifecycle state, binding, and evidence rules have one Python owner. Shell scripts contain only bounded orchestration and no structured lifecycle parsing or state mutation.
- The aggregate check invokes each checker/generator once and one in-process Python test discovery lane; it does not hide failures with retries, parallelism, or reduced assertions.
- Stable docs, contracts, skill content, generated metadata/index/diagrams, and tests agree on the new source, runtime, artifact, compatibility, and backend boundaries.
- The Markdown checker reports `files_with_hard_wrap=0` and `join_count=0` outside the ten exact immutable exceptions, every exception still matches its manifest SHA-256, and no unlisted stage or newly created artifact is exempt. Normalization changes no code block, table, frontmatter, explicit hard break, Markdown structure, file mode, or non-whitespace content.

## Validation

- Validate this design with the installed pre-cutover `design-runner.sh` and run the mandatory bounded `review-change`/`review-design` gate.
- Before implementation deletion, capture characterization results for all current lifecycle invariants and the explicit Herdr envelope.
- Run Python unit, contract, property-style table, state-machine, and CLI tests for the new runtime in one discovery lane.
- Run focused contract tests for skill activation, routing, successor ownership, plugin manifests, canonical directory identity, metadata projection, and forbidden runtime copies.
- Trace representative `plan validate`, `ledger init`, and state-transition commands to prove the one-process and one-read boundaries; record comparative timings without making machine-specific wall time the sole oracle.
- Regenerate `skills.index.json`, PlantUML sources, and tracked SVGs, then run the simplified `bash scripts/check.sh`, the official Codex plugin validator, and `git diff --check`.
- Re-run the exact compatibility-ID search against `~/.codex/AGENTS.md` without editing the file.
- Run the bundled Markdown normalizer with `contracts/markdown-prose.toml` in `count`, `preview`, `write`, and `check` order after semantic edits and generated-output refresh. Inspect the normalization diff independently from semantic changes, require semantic and structure fingerprints to remain unchanged, require zero non-exempt findings, and compare every immutable exception to its pinned SHA-256.
- Compare the final changed paths with the separately approved plan. Do not install/update either plugin, start a new Codex thread, run live providers, commit, push, or publish as part of repository validation.

## Recovery

- Default to fix-forward inside the approved repository touch set.
- Build the new runtime and its characterization oracles before deleting the old runtime. If equivalence or v3 acceptance fails, stop before switching skill paths; do not keep a half-selected dual runtime.
- Treat format or source-tree cutover as one atomic repository boundary. Do not retain aliases, symlinks, dual parsers, copied bundles, or a second source tree as an unowned fallback.
- Artifact digest drift is an expected typed stop resolved by returning to the owning design/plan gate and creating a new ledger, not by refreshing authority in place.
- The change creates no external data migration. After a completed repository cutover, recovery is a normal revert to the last coherent repository revision; updating the installed Claude/Codex plugin to either revision is a separate, explicitly authorized operation.
- Markdown normalization uses atomic per-file replacement and aborts on source drift, fingerprint changes, or immutable-manifest mismatch. Any mutation to a listed stage-history file is an immediate stop and must be restored byte-for-byte before proceeding; the implementation may not refresh its digest or add a new exception as repair. Do not add a legacy wrapping mode or weaken the normalizer.

## Review Gate

- required_entry: review-change
- review_component: review-design
- actor_role: main
- review_depth: boundary
- review_status: passed_after_focused_verification
- review_surface: This design; `AGENTS.md` and `README.md` for repository and distribution promises; `contracts/skills.toml`, `contracts/install-targets.toml`, and `contracts/lifecycle.toml` for current exposure and lifecycle ownership; `scripts/check.sh`, the current harness parser/state sources, and package-surface scripts for the measured ownership boundary; the exact-name result from `~/.codex/AGENTS.md` for the authorized external-reference check.
- candidate_findings: The initial HWR-001 finding was accepted. The user selected option A, and the repair narrows exemption authority to ten exact path-and-digest entries while keeping all new and active Markdown in scope; no accepted finding remains.
- review_evidence: Current file hashes equal the recorded downstream evidence identities, `docs/AGENTS.md` requires retained stage history for traceability, and the repaired boundary forbids glob exclusions, implicit enrollment, digest refresh, or stage-history mutation. The installed design validator passes after repair.
- pass_rationale: The selected boundary preserves immutable approval evidence, provides a deterministic zero-hard-wrap oracle for all mutable Markdown, stays inside the approved repository write surface, and leaves no unresolved design choice.
- review_budget: One initial bounded main-agent design review and, only if an accepted finding changes this design, one focused verification review.

## Human Gate

- approval_required: true
- approval_status: approved
- next_entry: plan-change
- post_approval_entry: plan-change
- implementation_entry_condition: A separately reviewed and explicitly approved execution-grade plan is required before `implement-change` may start.

## Implementation Surface

- impl_file_refs:
  - .gitignore
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
  - scripts/check.sh
