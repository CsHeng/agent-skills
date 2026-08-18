# Exact External File Touch Set And Evidence Design

## Status

- design_version: 1
- decision_status: ready_for_approval
- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed design and requested `plan-change` on 2026-08-18.
- recommended_next_phase: plan
- next_entry: plan-change

## Problem

The approved parent-inherited Codex subagent routing plan must update three existing user-owned files under `/Users/csheng/.codex`, but the sovereign harness artifact-DAG intentionally accepts only repository-relative `impl_file_refs` and `test_file_refs`. The implementation preflight therefore stopped before mutation: `execute-runner.sh allowed-touch-set` rejected the absolute user-home refs, and the approved upstream design surface also omitted the plan-change source/projection refs and four focused test refs required by the routing amendment.

Silently treating an absolute path as a repository ref, bypassing `allowed-touch-set`, or performing NSR-040 outside the task ledger would discard immutable scope, changed-path evidence, and controller convergence. The user selected architecture option A: extend the artifact-DAG with an explicit external-file contract rather than execute the host configuration outside harness evidence. The bootstrap repair below requires a repository-only capability unit before a separate harness-governed routing unit; both remain inside the sovereign lifecycle.

## Goals

- Add a second, explicit `external_impl_file_refs` channel for exact existing files while preserving the current repository-only meaning and output of `impl_file_refs`, `test_file_refs`, and `allowed-touch-set`.
- Bind external refs through exact design-to-plan-to-task containment, approved-plan identity, main-controller-only execution, canonical path validation, pre-mutation baseline evidence, a baseline-rooted per-file compare-and-swap mutation broker, ordered write-ahead intent chains with applied checkpoints, task convergence, final execution evidence, truth-sync validation, and close validation.
- Support content-only updates to the three explicitly approved existing Codex-home files without allowing directory surfaces, globs, path aliases, symlinks, caller-visible target creation/deletion/rename, caller-requested ownership or mode changes, or delegated external writes. The only filesystem creation and rename permitted are broker-owned private candidates and exact-target atomic replacement described below.
- Keep external evidence secret-safe: persist paths, digests, file type, size, mode, uid, gid, and changed/unchanged state, but never persist file content or unrelated configuration values.
- Preserve the parent-inherited routing amendment: role files pin neither model nor reasoning, user-owned global instructions own the provider-specific route and minimum reasoning floors, portable task metadata remains provider-neutral, and a rejected required uplift never silently downgrades.
- Preserve all existing plans and backend behavior when `external_impl_file_refs` is absent, including byte-compatible Herdr envelopes and repository-only truth-sync surfaces.
- Bootstrap the capability through a repository-only approved execution unit, then use it from a separately approved routing execution unit; no plan may depend on external-touch metadata or operations that do not exist at its own preflight.

## Non-Goals

- No generic permission to write arbitrary absolute paths, directories, globs, environment-expanded paths, `$HOME`, `~`, repository paths disguised as external refs, or newly created targets.
- No `external_test_file_refs`, external directory snapshots, recursive inventories, remote filesystems, provider APIs, deployments, plugin installation, live Codex trials, or external process orchestration in this milestone.
- No delegated worker, reviewer, explorer, command job, Herdr pane, or Codex-native subagent may mutate an external ref; external-file tasks are serial and main-controller-owned.
- No generic multi-file transaction engine, content backup store, automatic rollback, caller-requested rename/chmod/chown operation, adversarial concurrent-writer guarantee, or general filesystem sandbox. Version 1 does include one narrowly scoped per-file atomic compare-and-swap replacement broker because observer-only evidence cannot prove the authorized writer path.
- No generic Codex file-edit, shell redirection, delegated tool, or third-party editor may mutate an approved external target while an external task is active; the broker is the only external-file mutation surface.
- No raw external-file diff or preimage in task ledgers, execution results, review briefs, logs, or stable truth. Task-specific conformance checks may report only approved keys, redacted hunks, and metadata evidence.
- No provider model identifiers in this reusable design, harness code, skills, neutral envelopes, or stable repository truth; the existing immutable user-route input remains the only stage artifact containing the concrete model matrix.
- No change to lifecycle phase ownership, human approval gates, task DAG authority, topology, isolation, resource locks, truth-sync ownership, close ownership, or Herdr allocation policy.

## Change Classification

- request_kind: change-definition
- change_class: C
- design_strength: design-full
- truth_impact: high
- boundary_impact: high
- truth_repair: false
- truth_sync_required: true
- parallel_candidate: false
- recommended_next_phase: design-full

## Boundaries

### Dual Touch-Set Contract

`impl_file_refs` and `test_file_refs` remain safe repository-relative surfaces and continue to feed the existing `allowed-touch-set` operation unchanged. A new optional `external_impl_file_refs` list may appear under the design `Implementation Surface`, plan `Implementation Scope`, and individual task sections. The plan also declares `external_touch_policy: exact-existing-files-v1` whenever the list is non-empty.

Design-to-plan and plan-to-task containment are exact set comparisons: every plan external ref must be named by the approved design, every task external ref must be named by the plan, and an external ref may not also match any repository touch surface. Empty or absent external lists normalize to `[]` and preserve legacy behavior.

Version 1 accepts only exact existing regular files. It does not interpret prefixes, directories, globs, variables, tildes, or relative paths. The three approved external refs for the routing milestone are declared separately under `Implementation Surface`; reusable skills describe the field semantics without copying those user-specific paths.

### External Path Safety

The external validator requires an absolute path with no control characters or glob metacharacters, rejects trailing separators and path components `.` or `..`, resolves the path with existence required, and requires the declared string to equal the canonical resolved string. It rejects the target when the final file or any resolved path component is a symlink, when the target is not a regular file, when `st_nlink != 1`, or when the canonical target is inside the controller repository. Exact path identity plus a recorded before/after device-and-inode transition, rather than a broad root, is the authorization boundary; rejecting hard links prevents an external path from aliasing a repository inode or another host path.

External tasks must declare `executor_mode: main`, `delegation_policy: forbidden`, `parallel_policy: forbidden`, `parallel_group: none`, `isolation: controller-checkout`, and a non-empty resource lock. Plan validation rejects any external ref on a delegated, concurrent, or isolated-worker task before ledger creation. Backend envelopes never include external refs because no task carrying them is delegable.

Content updates preserve file type, uid, gid, and permission mode. The broker verifies the opened preimage's `st_dev`, `st_ino`, and `st_nlink` against the intent's immediate parent state, copies the validated staged payload into a broker-named private sibling candidate on the target filesystem, applies only the parent-approved metadata, fsyncs it, rechecks the target parent state, atomically replaces the exact approved path, fsyncs the parent directory, and records the new `st_dev`, `st_ino`, and `st_nlink`. The first intent's parent is the immutable baseline; a later repair intent's parent is the preceding applied intent's after-state. Version 1 exposes no create, delete, caller-selected rename, chmod, or chown operation; private sibling creation, metadata preservation on that private candidate, and exact-target atomic replacement are internal broker mechanics and the only authorized inode transition. A plan may impose a stricter task-specific mode or ownership oracle, such as preserving `config.toml` mode `0600`.

### Evidence Helper And Language Boundary

A new standard-library Python helper, `src/runtime/harness/external-touch-evidence.py`, exclusively owns canonical external path validation, content hashing, metadata capture, secure candidate staging, baseline-rooted and immediate-parent-bound per-file replacement, and before/after manifest comparison. Bash remains the established harness orchestration layer: it extracts Markdown fields, performs design/plan/task set containment, invokes the helper with an argument array, persists write-ahead state in the task ledger, and routes typed outcomes. The external path, identity, mutation, and manifest business rules are not reimplemented in Bash.

- implementation_archetype: deterministic exact-file compare-and-swap mutation and evidence helper invoked by the existing Bash harness
- implementation_language: Python 3 standard library for path and manifest semantics; Bash 4+ and `jq` for existing lifecycle orchestration
- language_rationale: Python provides portable `lstat`/`fstat`, `O_NOFOLLOW` where supported, canonical path, mode/uid/gid/device/inode/link-count evidence, streaming SHA-256, atomic replacement/fsync primitives, typed data, and JSON handling without a new dependency, while the repository already requires Python for generators and tests. Moving the whole harness or introducing a standalone service would cost more than this bounded boundary; keeping identity, compare-and-swap, and manifest state in shell would increase quoting, platform, and structured-state risk.

The helper exposes deterministic baseline, stage, prepare, apply, and compare operations, type-annotated core functions, explicit domain errors, stable non-zero exits, and JSON on stdout with diagnostics on stderr. It never interprets configuration semantics, logs content, accepts a symlinked identity, writes an undeclared target, or constructs a command string. The controller payload is staged in a run-owned `0700` temporary directory with `0600` files. During apply, the broker alone may create one `O_CREAT|O_EXCL` private sibling candidate whose opaque basename is bound to the persisted intent ID; it copies the validated payload, never accepts a caller-selected sibling path, and exposes no generic rename operation. The ledger may retain the private staging reference, intent ID, sibling basename, and hashes but never the content. After an applied checkpoint, the broker removes the source payload and any still-existing exact broker candidate; abandoned-run cleanup removes only ledger-bound artifacts whose identity and digest match the intent, and refuses ambiguous files.

### Task Ledger And Controller Convergence

The immutable task projection gains `external_impl_file_refs`. Dynamic task state gains `external_touch_baseline`, `external_write_intents`, and `verified_external_changes`; the dynamic fields do not participate in plan-versus-ledger topology drift comparison, while the declared external ref list does.

Before the first external mutation, the controller sets the task in progress and invokes a new runner operation that captures a baseline into the persisted ledger. The baseline binds `schema_version`, approved design and plan SHA-256 values, controller run identity, task ID, sorted exact refs, and per-file SHA-256, size, file type, mode, uid, gid, `st_dev`, `st_ino`, and `st_nlink`. Capture fails before mutation if any declared path is invalid, its metadata is unavailable, the plan/design set differs, or an existing ledger baseline does not exactly match a recapture; an existing baseline is retained rather than silently refreshed.

For each target, the helper first stages a private payload without changing the target. After task-specific parsing and conformance pass on that payload, the controller persists the next write-ahead intent in a per-ref ordered chain. Every intent contains run/task identity, an opaque intent ID, a contiguous sequence number, the exact ref, the immutable baseline root identity, its immediate parent SHA-256/device/inode/link count, candidate SHA-256, preserved metadata, broker staging references, and `state: prepared`. Sequence 1 binds its parent to the baseline; sequence N binds its parent exactly to sequence N-1's applied after-evidence. The controller may prepare no new intent while another intent for that ref is unapplied, and rejects a candidate equal to its immediate parent digest. Only then may the broker apply the intent. If the opened target still matches the recorded immediate parent identity and hash, the broker performs the atomic replacement and returns after-evidence; the controller immediately persists `state: applied`. If interruption occurs after replacement but before the applied marker, replay is idempotent: an exact candidate hash with preserved metadata and the intent-authorized new single-link inode is recorded as applied, the exact immediate parent is safe to apply, and every other state returns typed baseline drift.

At controller convergence, the helper compares current files with the original baseline and every per-ref intent chain. It requires the same canonical refs, contiguous sequence numbers rooted at the immutable baseline, exact parent-to-prior-after linkage, no prepared-but-unapplied intent, preserved type/uid/gid/mode, single-link before/after identities, and current SHA-256/device/inode matching either the baseline for an empty chain or the last applied after-evidence for a non-empty chain. It emits root-before/final-after SHA-256, size, device, inode, link count, applied intent count, and `changed: true|false` based on the final digest versus the baseline; a repair chain may therefore contain multiple applied intents even if its final content returns to the baseline digest. It rejects missing, symlinked, metadata-drifted, uncheckpointed, forked, duplicate, or undeclared evidence. The controller stores the verified manifest in `verified_external_changes` alongside repository `verified_changed_paths`; task completion requires both evidence classes and declared oracles to pass.

The existing `allowed-touch-set` operation remains repository-only. A new `allowed-external-touch-set` operation returns the sorted exact external refs, and the final execution result carries `allowed_external_touch_refs` plus the ledger-embedded external evidence. Truth-sync and close recompute the approved external ref set, verify its equality with the execution result, and validate manifest structure and plan/task binding without rereading current external file contents; later legitimate user edits therefore do not invalidate historical implementation evidence.

### Security And Review Boundary

External baselines and execution results contain hashes and metadata only. They do not contain file contents, raw TOML, unrelated settings, credentials, environment values, or recursive directory inventories. Task-specific verification for sensitive files reports only named keys, presence/absence, approved values, redacted hunks, and preserved metadata.

The implementation review brief includes exact external refs, ordered write-intent/applied identity, root-before/final-after hashes, mode/uid/gid/device/inode/link-count evidence, task-specific redacted conformance output, and the repository diff. A reviewer remains read-only, receives no general external-read authority, and cannot request raw sensitive preimages or staged candidates. The main controller alone adjudicates findings and repairs accepted issues inside the combined repository and exact-external touch sets, and any accepted external repair appends a new intent whose immediate parent is the prior applied after-state while retaining the same immutable baseline root.

### Compatibility And Lifecycle

Plans without `external_impl_file_refs` retain the current repository-only validation, task projection semantics, runner CLI output, truth-sync binding, and close route. The Herdr `schema_version: 1` projection and Codex-native delegated envelope remain unchanged because external tasks cannot be delegated and external fields are excluded from backend-neutral task projections.

The blocked parent-inherited routing plan is not resumed directly. After this design is approved, execution proceeds through two independently approved units. Bootstrap unit E1 is repository-only and implements, reviews, truth-syncs, and closes the external-touch capability using the current repository `allowed-touch-set`; it declares no external refs and never calls an operation that does not exist at its own preflight. Routing unit E2 is created only after E1's generated runner and stable truth converge; E2 carries the routing amendment plus the three exact user files, and its preflight must pass the newly available `allowed-touch-set`, `allowed-external-touch-set`, immutable task projection, mandatory plan review, and human plan gate. A one-plan ledger migration is explicitly rejected because it would mutate the approved task projection and validator semantics mid-execution.

## Architecture Decision

- architecture_decision_id: EXACT-EXTERNAL-TOUCH-001
- decision_status: selected
- decision_horizon: Bootstrap the exact-file capability in one repository-only execution unit, then support the current three-file Codex-home content update and future equivalent same-user exact-existing-file tasks without enabling directory targets, caller-visible arbitrary creation/deletion/rename, caller-selected metadata, delegated, remote, or adversarial-concurrency semantics.
- demand_evidence: The current approved routing plan deterministically fails `allowed-touch-set` before mutation because it requires three explicitly authorized user-home files that cannot be represented by the repository-only artifact-DAG.
- scarce_resource: The controlling constraint is trustworthy mutation authority and resumable evidence, not filesystem throughput. The change must preserve the repository path invariant while avoiding an untracked host-side exception.
- hard_requirements:
  - exact human-approved file identities bound by approved design, plan, task, and hashes
  - fail-closed canonical path and symlink handling
  - main-controller-only serial writes with no delegated or provider authority expansion
  - secret-safe before/after evidence and deterministic resume behavior
  - unchanged repository touch-set semantics and backend wire compatibility for legacy plans
- options:
  - status quo: keep the artifact-DAG repository-only and reject the combined plan. Discarded because the user explicitly selected integrated external-file execution and the required host configuration would remain outside immutable task evidence.
  - smallest sufficient: bootstrap a separate exact-existing-file channel, a focused Python compare-and-swap helper, ledger-bound baseline plus write-ahead/applied state, and optional execution-result fields while leaving repository touch logic intact; then consume it from a second approved plan. Selected because it satisfies the observed three-file demand with a narrow fail-closed and executable contract.
  - structural investment: build a generic external filesystem transaction engine with allowed roots, directory snapshots, create/delete/rename, rollback storage, delegated sandboxes, and hostile-concurrency protection. Deferred because no current demand justifies its implementation, recovery, security, and portability cost.
- marginal_tradeoff: The selected option adds one helper, optional metadata, per-file broker state, evidence validation across plan/ledger/truth-sync/review surfaces, and one extra approved bootstrap unit; in return it eliminates an untracked exception, provides crash-resumable exact-file writes, and avoids weakening repository containment. Each additional filesystem capability would add disproportionate authorization and recovery cost.
- opportunity_cost: This work delays the parent-inherited routing implementation and plan-metadata slimming, but the routing plan cannot execute safely until the touch-set boundary is explicit.
- owner_and_incentives: `plan-change` owns exact declared refs and main-only task policy; `implement-change` owns baseline capture, mutation sequencing, convergence, and evidence; the Python helper owns path/manifest semantics; `review-change` owns the bounded review brief; `sync-truth` and `close-change` verify immutable evidence; the user owns and explicitly authorizes the external files.
- comparative_advantage: The existing Bash harness already owns lifecycle and artifact-DAG orchestration, while Python's standard library has the lowest-cost portable ownership of filesystem metadata and deterministic JSON. The main controller prepares task-specific candidate content, but only the broker may replace an approved target and neither surface may choose or widen the target set.
- chosen_option: Two-stage rollout of dual repository/external touch channels with exact-existing-file-v1 semantics, a ledger-bound Python compare-and-swap broker, and per-file baseline-rooted write-ahead/applied intent chains.
- upgrade_trigger:
  - any requirement for caller-visible target creation/deletion/rename, caller-selected chmod/chown, or authorization of a directory or glob requires a new design; broker-owned private candidate creation, metadata preservation, cleanup, and exact-target atomic replacement remain inside this version
  - any delegated or parallel external writer requires a real filesystem sandbox and new isolation model
  - any hostile or concurrent same-path writer requirement triggers an atomic compare-and-swap/openat implementation, preferably in a single-purpose Go helper
  - repeated demand across unrelated repositories may justify a versioned generic external-touch schema only after at least three distinct approved use cases
- recovery_and_oracle: Before mutation, invalid refs, hard links, identity mismatch, missing intent, or baseline drift stop with typed evidence and no write. After a partial approved edit, idempotent intent replay distinguishes original, already-applied, and conflicting states; recovery is fix-forward inside the same exact file set and automatic rollback is forbidden. Contract, state-transition, broker unit, compatibility, and sensitive-output tests protect the boundary.

## Oracle Strategy

- protected_boundary: Exact external-file authorization, immutable design/plan/task containment, safe path identity, content-only evidence, controller convergence, and backward-compatible repository-only execution.
- oracle_owner: Artifact-DAG and task-ledger tests own structural containment; Python unit tests own path and manifest semantics; execute/truth-sync/close smoke tests own lifecycle evidence; workflow contract tests own skill instructions; unchanged Herdr golden tests own backend compatibility.
- selected_methods:
  - contract tests for design-plan-task external set containment, required policy fields, actor restrictions, and optional-field backward compatibility
  - model/state-transition tests for the two-unit bootstrap boundary, baseline capture order, immutable task projection, baseline-rooted multi-intent parent linkage, prepared/applied replay, partial interruption, convergence, final execution result, truth-sync validation, and close routing
  - table-driven Python unit tests for valid regular files, non-canonical aliases, final and ancestor symlinks, hard links, directories, missing targets, glob/control characters, repository overlap, content drift, metadata drift, device/inode transitions, exact-target broker enforcement, deterministic sort/order, and secret-free JSON
  - characterization/golden tests proving `allowed-touch-set`, legacy task projections, Herdr envelopes, and plans without external refs remain semantically or byte compatible as applicable
  - targeted metadata-only conformance for the three Codex-home files; no live Codex or provider probe in CI
- discarded_methods: Directory snapshots are excessive and leak sibling metadata; raw golden file contents risk secrets; live filesystem watchers and chaos add no value for the trusted same-user local threat model; automatic rollback would require storing sensitive preimages.
- oracle_change_policy: Any relaxation from exact file to prefix/directory matching, any symlink allowance, any removal of main-only execution, any content emission, or any downgrade from exact hash/metadata comparison requires explicit design review and cannot be an implementation repair.

## Acceptance Conditions

- A legacy approved plan with no external refs produces the same repository `allowed-touch-set`, passes existing task-ledger and truth-sync checks, and emits byte-compatible Herdr envelopes.
- A design, plan, or task that places an absolute path in `impl_file_refs` or `test_file_refs` still fails; an external path is accepted only through `external_impl_file_refs` with `external_touch_policy: exact-existing-files-v1`.
- Design-to-plan and plan-to-task external containment are exact, deterministic, and fail closed; the three current Codex-home refs appear in `allowed-external-touch-set` and nowhere in the repository touch set.
- Plan validation rejects external refs on subagent, parallel, command-job, isolated-worktree, or missing-lock tasks.
- Baseline capture rejects missing, non-regular, non-canonical, symlinked, hard-linked, repository-overlapping, or metadata-inaccessible targets before mutation and stores only the approved hashes and metadata, including device/inode/link count.
- No external target changes without a persisted prepared intent, broker validation of the opened immediate-parent identity and hash, an exact candidate hash, broker-owned private sibling creation, atomic replacement, and an applied checkpoint; generic external editors are forbidden by the active task contract.
- Controller convergence rejects missing baseline, changed external ref sets, symlink or hard-link replacement, type/uid/gid/mode drift, broken or forked intent chains, missing or duplicate sequence numbers, prepared-only state, current identity mismatch, malformed manifests, and undeclared evidence; accepted brokered content changes are recorded separately from repository changed paths.
- Execution result, truth-sync, and close validation bind the exact external ref set and embedded verified evidence to the approved design, plan, ledger, and task IDs without requiring current user files to remain frozen forever.
- External evidence and review briefs contain no file content or unrelated configuration values; the user-route model identifiers remain only in the approved user-specific routing input and final user-owned instructions.
- Bootstrap E1 can preflight and complete with the old repository-only channel; only after E1 converges may routing E2 materialize both channels, run NSR tasks serially, broker edits to the three approved external files in its final external task, and stop at the later truth-sync approval gate.
- Source-owned skills and runtime remain authoritative; root-flat skills and all six runner-owner harness bundles regenerate deterministically from source.

## Validation

- Add Python unit tests for the helper's capture/stage/prepare/apply/compare core, baseline-rooted multi-intent chains, broker-owned sibling creation and cleanup, atomic replacement, replay states, and CLI error contract using temporary files and directories outside the repository.
- Extend artifact-DAG and plan-runner smoke tests with valid dual-channel fixtures plus absolute-in-repo-field, design mismatch, task mismatch, directory, glob, symlink, repository-overlap, and invalid-actor rejection cases.
- Extend task-ledger and execute-runner smoke tests with repository-only bootstrap, external baseline capture, single- and multi-intent prepared/applied chains, crash windows before and after sibling creation and replacement, ledger-bound cleanup, conflicting drift, convergence, immutable projection drift, verified external evidence, execution-result binding, and legacy-plan compatibility.
- Extend truth-sync and close smoke tests so external evidence is matched exactly while stable truth refs remain repository-only.
- Extend workflow and runtime-distribution contract tests for the new helper, generated bundles, plan/implement/review/sync instructions, provider neutrality, and unchanged Herdr semantics.
- Run `python3 -m unittest`, targeted helper tests, Bash syntax checks, all affected harness smoke tests, `python3 scripts/generate-skills-index.py`, `python3 scripts/flatten-skills.py --target root-flat`, sovereign harness checks, `bash scripts/check.sh` after truth sync, and `git diff --check`.
- Do not run live provider, Codex subagent, Herdr, plugin install, commit, push, or external user-file mutation while validating this design.

## Recovery

- Default recovery is fix-forward inside the approved repository refs and exact external file refs.
- Before each mutation, any path, set, approval, canonicalization, hard-link, ownership, mode, type, device/inode, immediate-parent hash, candidate hash, or baseline-root mismatch returns typed evidence and leaves the target untouched by that intent.
- If interruption occurs before apply, retain the original baseline and latest prepared intent; replay validates and reuses or safely removes only its own ledger-bound private artifacts. If interruption occurs after atomic replacement but before the applied marker, replay compares the exact candidate hash and authorized parent-to-child identity transition and records the marker without rewriting. Do not recapture a new baseline that hides the partial change.
- If an external target changes independently after baseline capture and matches neither its baseline when no intent exists nor the latest intent's immediate parent or candidate digest, stop with `external_touch_baseline_drift`; do not attribute it to the controller or synthesize an applied checkpoint.
- If content repair cannot converge without new refs, metadata changes, deletion, restoration from sensitive preimages, or broader authority, return `needs-plan-change` or `needs-design-decision`; do not widen the list or synthesize rollback.
- No automatic rollback is defined. The exact preimage hashes are evidence, not recoverable content, and user files remain owned by the user.

## Review Gate

- required_entry: review-change
- review_component: review-design
- actor_role: delegated
- review_depth: boundary
- review_status: passed_after_focused_repair
- candidate_findings: The initial bounded design review returned four blocker candidates and the focused verification returned two causal repair findings. The main adjudication accepted all six: a same-plan bootstrap cycle, observer-only evidence without an authorized writer path, missing device/inode/hard-link identity, no durable partial-edit checkpoint, an unchainable one-intent repair model, and unqualified creation/rename prohibitions that contradicted broker internals.
- review_evidence: The final design splits bootstrap E1 from routing E2; makes a Python compare-and-swap broker the only external mutation path; adds device/inode/link-count and hard-link rejection; defines baseline-rooted, immediate-parent-bound prepared/applied intent chains with idempotent replay; and distinguishes forbidden caller-visible target operations from ledger-bound broker staging, atomic replacement, and cleanup. The main controller verified the exact focused repair against both accepted findings and found no remaining same-slice contradiction; deterministic design validation, provider-neutral scan, and whitespace validation pass.
- review_budget: Consumed one initial bounded design review, one focused verification review, and the single allowed same-slice repair. No further discovery review is authorized before the human gate.

## Human Gate

- approval_required: true
- approval_status: approved
- approval_basis: The user explicitly approved this reviewed design and requested `plan-change` on 2026-08-18 after the bounded review and focused repair passed.
- next_entry: plan-change

## Implementation Surface

- impl_file_refs:
  - src/runtime/harness/artifact-dag.sh
  - src/runtime/harness/plan-runner.sh
  - src/runtime/harness/task-ledger.sh
  - src/runtime/harness/execute-runner.sh
  - src/runtime/harness/truth-sync-runner.sh
  - src/runtime/harness/external-touch-evidence.py
  - src/skills/workflows/plan-change/SKILL.md
  - src/skills/workflows/implement-change/SKILL.md
  - src/skills/workflows/implement-change/references/workflow.toml
  - src/skills/workflows/review-change/SKILL.md
  - src/skills/review-components/review-implementation/SKILL.md
  - src/skills/workflows/sync-truth/SKILL.md
  - docs/architecture/workflow-orchestration.md
  - README.md
  - docs/architecture/diagrams
  - docs/architecture/generated
  - skills/.source-map.json
  - skills.index.json
  - skills/plan-change
  - skills/implement-change
  - skills/review-change
  - skills/review-implementation
  - skills/sync-truth
  - skills/design-change/scripts/harness
  - skills/plan-change/scripts/harness
  - skills/implement-change/scripts/harness
  - skills/review-change/scripts/harness
  - skills/sync-truth/scripts/harness
  - skills/close-change/scripts/harness
- external_impl_file_refs:
  - /Users/csheng/.codex/AGENTS.md
  - /Users/csheng/.codex/config.toml
  - /Users/csheng/.codex/agents/explorer.toml
- test_file_refs:
  - tests/test_external_touch_evidence.py
  - src/runtime/harness/smoke-test/test-artifact-dag.sh
  - src/runtime/harness/smoke-test/test-plan-runner.sh
  - src/runtime/harness/smoke-test/test-task-ledger.sh
  - src/runtime/harness/smoke-test/test-execute-runner.sh
  - src/runtime/harness/smoke-test/test-truth-sync-runner.sh
  - src/runtime/harness/smoke-test/test-close-runner.sh
  - src/runtime/harness/smoke-test/test-sovereign-skill-surface.sh
  - src/runtime/harness/smoke-test/test-recovery-routing.sh
  - tests/test_skill_workflow_contracts.py
  - tests/test_parallel_execution_contracts.py
  - tests/test_implement_change_via_herdr_contracts.py
  - tests/test_runtime_distribution_contracts.py
