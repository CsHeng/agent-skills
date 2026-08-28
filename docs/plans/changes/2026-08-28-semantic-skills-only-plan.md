+++
artifact_kind = "plan"
contract_version = 4
design_ref = "2026-08-28-pi-extensions-repository-split-design.md"
design_sha256 = "c8ea2626ea6cb19821e8bfab10f55f4ec8c988290c4d239b8b2ae0b840673d77"
approval_status = "approved"
truth_sync_required = true
stable_truth_refs = ["AGENTS.md", "README.md", "docs/architecture/install-surface.md", "docs/architecture/invocation-contract.md", "docs/architecture/maintenance-contract.md", "docs/architecture/workflow-orchestration.md"]
default_runtime_model_policy = "semantic-routing"
parallel_execution_approved = false

[scope]
impl_file_refs = [".pi", "AGENTS.md", "README.md", "contracts", "docs/architecture", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi", "scripts", "skills.index.json", "src/runtime/harness", "src/skills", "skills"]
test_file_refs = ["tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "ASK-100"
depends_on = []
verification_commands = ["python3 scripts/generate-skills-index.py", "python3 scripts/flatten-skills.py --target root-flat", "python3 -m pytest tests/test_semantic_skill_contracts.py tests/test_skill_workflow_contracts.py tests/test_skill_routing_contracts.py tests/test_skill_activation_contracts.py -q", "python3 scripts/check-contracts.py", "git diff --check -- contracts src/skills skills tests/test_semantic_skill_contracts.py tests/test_skill_workflow_contracts.py tests/test_skill_routing_contracts.py tests/test_skill_activation_contracts.py"]
scope_slice = "Recast the workflow Skills and repository-owned declarative contracts as provider-neutral semantic guidance. Preserve design, plan, implementation, review, truth-sync, and close meaning; make each formal design, plan, and implementation Skill semantically require one bounded review handoff before accepting its result; remove claims that a host will enforce the sequence, artifact schema, actor binding, attempts, replay, or continuation."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["semantic-workflow-skills", "skill-routing-contract", "skill-inventory", "generated-skill-payload"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["Every public Skill remains usable through the standard Agent Skills surface in an arbitrary compatible agent with no extension or runtime installed.", "Formal design-change, plan-change, and implement-change each describe exactly one bounded review-change child before their own semantic result is accepted.", "Ordinary non-formal work does not acquire a review merely from repository policy, and standalone review-change accepts a bounded target without synthesizing upstream design, plan, or implementation.", "Review evaluators remain read-only, the active implementing agent owns any accepted repair, and no review response can recursively invoke a lifecycle or widen scope.", "Contracts describe Skill identity, discovery, composition, semantic triggers, optional overlays, artifact guidance, and generated distribution only; they do not claim host-level enforcement.", "No Skill locates a repository sibling, calls a bundled validator, mutates a ledger, binds a physical model or actor, schedules a follow-up, or assumes Pi, Codex, Claude, or another specific harness.", "The 40 public IDs, authored-to-generated parity, frontmatter descriptions, activation projection, and standalone reference closure remain intact."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["contracts/lifecycle.toml", "contracts/skills.toml", "contracts/workflow-modes.toml", "skills.index.json", "src/skills", "skills"]
test_file_refs = ["tests/test_semantic_skill_contracts.py", "tests/test_skill_workflow_contracts.py", "tests/test_skill_routing_contracts.py", "tests/test_skill_activation_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "ASK-200"
depends_on = ["ASK-100"]
verification_commands = ["test ! -e integrations/pi", "test ! -e src/runtime/harness", "test ! -e scripts/generate-pi-contracts.py", "test ! -e contracts/runtime-bundles.toml", "if find skills -path '*/scripts/harness' -print -quit | grep -q .; then exit 1; fi", "python3 -m pytest tests/test_runtime_distribution_contracts.py tests/test_command_retirement_contracts.py tests/test_check_orchestration.py tests/test_install_target_contracts.py -q", "python3 scripts/check-contracts.py", "python3 scripts/check-install-surface.py", "git diff --check -- .pi contracts integrations scripts src/runtime skills tests"]
scope_slice = "Delete every executable host and harness surface from this repository: the Pi package and probes, project Pi settings, Python artifact and ledger runtime, runtime-bundle inventory, lifecycle projection generator, generated Skill-local harness payloads, and their runtime tests. Retain and narrow only static repository conformance checks for authored Skills, contracts, references, and generated output."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["host-surface-removal", "runtime-removal", "distribution-generator", "aggregate-check", "static-contract-checks"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["The maintained tree has no integrations/pi, src/runtime/harness, project Pi settings, Pi contract generator, runtime-bundle inventory, or generated scripts/harness payload.", "No Python, TypeScript, Shell, hook, or generated resource in the repository validates workflow artifacts, compiles task DAGs, mutates task ledgers, enforces attempts, drives replay, or acts as a live controller.", "Remaining scripts are limited to repository-static concerns such as TOML and JSON parseability, Skill inventory and reference closure, generated payload parity, plugin metadata, docs generation, Markdown, lint, types, and tests.", "Static checks do not import a removed runtime, invoke Pi, locate an extension repository, inspect user settings, or promise behavioral conformance for a host.", "Retirement and distribution tests assert the absence of executable runtime payloads without re-encoding host lifecycle behavior as a new checker."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = [".pi", "contracts/runtime-bundles.toml", "integrations/pi", "scripts/check-contracts.py", "scripts/check-install-surface.py", "scripts/check.sh", "scripts/generate-pi-contracts.py", "scripts/skill_distribution.py", "src/runtime/harness", "skills"]
test_file_refs = ["tests/test_check_orchestration.py", "tests/test_command_retirement_contracts.py", "tests/test_install_target_contracts.py", "tests/test_runtime_distribution_contracts.py"]
external_impl_file_refs = []

[[tasks]]
task_id = "ASK-300"
depends_on = ["ASK-200"]
verification_commands = ["python3 scripts/generate-skills-index.py", "python3 scripts/flatten-skills.py --target root-flat", "python3 scripts/generate-workflow-diagrams.py", "python3 -m pytest tests/test_standalone_check.py -q", "bash scripts/check.sh", "uvx --with pyyaml python /home/csheng/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .", "if rg -n 'integrations/pi|src/runtime/harness|generate-pi-contracts|runtime-bundles|codingHarness|workflowHarness|pi-extensions' AGENTS.md README.md contracts docs/architecture scripts src/skills skills tests; then exit 1; fi", "git diff --check"]
scope_slice = "Regenerate the root-flat Skill payload and semantic diagrams, rewrite stable truth and the prior host handoff as provider-neutral repository documentation, author a repository-static standalone probe with focused tests, and converge the aggregate check after runtime removal. Describe contracts as authoring and distribution truth, not as a protocol consumed by a harness."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["stable-project-truth", "semantic-diagrams", "generated-skill-payload", "plugin-metadata", "repository-acceptance"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["AGENTS and README describe only an authored Skill collection, generated portable payload, declarative authoring contracts, static conformance checks, and optional provider plugin manifests.", "Stable architecture docs describe semantic Skill composition and artifact guidance without assigning mechanical lifecycle behavior to this repository or advertising a maintained host.", "The previous active host handoff is either reduced to an explicitly historical stage note or otherwise removed from active guidance without deleting unrelated stage history.", "Generated diagrams visualize Skill roles and composition only; no diagram or generator contains a controller state machine, live task DAG enforcement, actor binding, attempt loop, or provider adapter.", "The standalone probe copies only the maintained repository surface into a controller-owned disposable directory, excludes Git metadata, stage history, local state, caches, and removed host/runtime paths, and runs generated checks plus the aggregate check from that copy.", "The standalone probe points Pi configuration variables at an empty disposable directory, places a failing Pi shim before the normal PATH, rejects maintained absolute workspace, user-settings, sibling, or removed-runtime paths, emits only redacted command status and digests, and always cleans up.", "Focused tests prove copy selection, environment isolation, failing-Pi behavior, redaction, failure propagation, and cleanup without adding workflow artifact, DAG, ledger, or lifecycle validation.", "The aggregate check passes without Pi, the removed runtime, user settings, or another checkout, and optional plugin validation still passes.", "Maintained source, stable docs, scripts, generated Skills, and tests contain no extension-repository path, host settings namespace, or removed runtime path."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["AGENTS.md", "README.md", "contracts", "docs/architecture", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "scripts", "skills.index.json", "src/skills", "skills"]
test_file_refs = ["tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "ASK-400"
depends_on = ["ASK-300"]
verification_commands = ["bash scripts/check.sh", "python3 scripts/generate-skills-index.py --check", "python3 scripts/flatten-skills.py --target root-flat --check", "python3 scripts/generate-workflow-diagrams.py --check", "python3 scripts/run-standalone-check.py", "if rg -n 'integrations/pi|src/runtime/harness|generate-pi-contracts|runtime-bundles|codingHarness|workflowHarness|pi-extensions' AGENTS.md README.md contracts docs/architecture scripts src/skills skills tests; then exit 1; fi", "if find skills -path '*/scripts/harness' -print -quit | grep -q .; then exit 1; fi", "git diff --check"]
scope_slice = "Prove the repository from its own public and maintained boundaries, then run the single formal implementation review over the converged diff. Admit at most one focused same-slice repair for an accepted causally bound finding and rerun the owning oracle plus aggregate checks."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["repository-acceptance", "implementation-review", "generated-skill-payload", "stable-project-truth"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["The standalone probe succeeds from its disposable copy, proves that Pi invocation would fail, exposes only an empty disposable Pi configuration directory, and neither locates a sibling checkout nor reads user settings.", "The generated 40-Skill payload exactly matches authored source and every public Skill is self-contained under the standard Agent Skills directory contract.", "Static contracts and routing data are useful to authors and agents but are neither executable workflow enforcement nor a required interface for a host.", "No maintained test composes this repository with an extension, and no forbidden host or runtime residue remains outside inert stage history.", "The formal implementation-stage review returns pass or receives one focused accepted same-slice repair followed by focused and aggregate verification, including another standalone-probe run.", "No commit, push, publication, release, plugin installation, consumer-state mutation, or deletion of unrelated historical artifacts occurs."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = [".pi", "AGENTS.md", "README.md", "contracts", "docs/architecture", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi", "scripts", "skills.index.json", "src/runtime/harness", "src/skills", "skills"]
test_file_refs = ["tests"]
external_impl_file_refs = []
+++
# Plan

## Implementation

Execute `ASK-100` through `ASK-400` serially, but start only after the separately validated local harness cutover has passed and its predecessor remains recoverable. `ASK-100` makes the Skills and contracts purely semantic; `ASK-200` removes executable host and runtime surfaces; `ASK-300` regenerates portable output and stable truth; `ASK-400` proves repository-only acceptance and performs the single formal implementation review.

Architecture decision reference: `PI-EXT-002`, limited in this plan to the semantic repository side. The repository does not import, inspect, test, install, configure, or name its replacement product. The one-time migration controller carries predecessor cutover evidence between two separately validated plans; no source file, contract, fixture, build command, or release artifact crosses that boundary.

That controller evidence is `E0`, a one-time canonical JSON attestation held outside both repositories. Its closed version-1 schema contains only `kind = predecessor-cutover-attestation`, the migration run ID, controller nonce, this consumer plan digest, the immediately preceding cutover execution-result digest, terminal outcome, an exact neutral probe-result map, `predecessor_source_recoverable`, and the attestation digest. It contains no repository path, package name, Skill ID, settings content, or reusable product contract. The exact probe keys are `unique_instance`, `pass_through`, `managed_activation`, `graph_admission`, `formal_design_review`, `formal_planning_review`, `formal_implementation_review`, `nonformal_review_skipped`, `standalone_review`, `generic_review_fallback`, `replay_resume`, `settlement`, and `extension_off`; every value and the terminal outcome must be `pass`.

No new persisted implementation boundary is introduced here, so language selection is not reopened. Existing Python remains appropriate only for deterministic repository generation and static conformance scripts. Those scripts may parse repository-owned TOML, JSON, Markdown, and filesystem structure but cannot become an artifact validator, task graph compiler, mutable ledger, live controller, provider adapter, or external settings broker.

`review_budget = 1` is a ceiling for one accepted focused repair on a task slice, not a per-task review mandate. The planned implicit implementation review occurs once at `ASK-400` over the converged diff. The approved design has passed its focused review, and this plan receives one mandatory plan review before approval.

## Work Package Readiness

- `milestone_objective`: leave a self-contained portable collection of 40 semantic Agent Skills with authoring contracts, generated distribution, static conformance, and optional provider plugin manifests, and remove every live host or harness capability.
- `non_goals`: implementing or testing an extension, sharing a harness contract, preserving runtime compatibility, changing public Skill IDs, changing plugin release versions, installing consumer state, deleting unrelated history, commit, push, publication, or deployment.
- `future_phase`: evolve semantic Skill content and repository-static authoring contracts independently; any future host integration belongs to that host's own repository and design.
- `decision_status`: `ready_for_approval_with_predecessor_evidence`; architecture is resolved, and execution has one closed machine-observable precondition: a valid fresh `E0` proves cutover and the exact behavioral probe set passed while this source remains recoverable.
- `oracle_strategy`: source/generated parity tests, reference-closure and trigger-case contract tests, characterization of the 40-ID distribution, negative tests for runtime residue, static docs and diagram checks, Python lint/type/test lanes for retained generators and the repository-static probe only, plugin manifest validation, forbidden dependency scans, and a disposable-copy aggregate run with Pi and user settings unavailable.
- `acceptance_oracles`: each task's exact commands and `done_when` predicates, followed by one bounded implementation review of the converged semantic-only diff.
- `max_review_batches`: `2`; one plan review before approval and one formal implementation review at `ASK-400`. A focused repair remains inside its current batch.
- `subagent_ready`: `false`; generated Skills, contracts, stable docs, diagrams, and aggregate checks overlap heavily, and the current checkout already contains the migration baseline, so one serial main actor owns convergence.

## Execution Continuity

- `execution_mode`: `pending_confirmation_and_predecessor_evidence`.
- `confirmation_clearance`: `C0` is the user's approval of this exact plan digest. It authorizes only repository-local mutation inside declared refs and no user settings, other repository, installation, remote, commit, push, publication, or deployment.
- `expected_continuous_range`: after `C0` and predecessor evidence `E0`, `E1 = ASK-100..ASK-400`. Task completion is a progress marker rather than a human checkpoint.
- `predecessor_evidence`: the controller recomputes the canonical `E0` digest, requires the exact version-1 fields and probe keys above, binds the consumer digest to this plan and the run ID and nonce to the current approved migration, verifies that the producer digest is the immediately preceding terminal cutover result, and confirms before any mutation that this checkout still contains the predecessor source slated for removal. `E0` is consumed once in controller state and is never copied into this repository.
- `runtime_contingencies`: `X1` stops if a retained public Skill needs executable runtime behavior to remain coherent; `X2` stops if removing host contracts would change a public Skill ID or standard installation surface; `X3` stops if static generation cannot be separated from live artifact or ledger validation; `X4` stops on unrelated user-change conflict, generated-surface drift after one focused repair, cross-repository dependency, repeated repair, or work beyond declared scope; `X0 = predecessor_evidence_unavailable` stops before `ASK-100` with no repository mutation when `E0` is missing, malformed, digest-invalid, bound to another run or plan, not the immediate terminal predecessor, contains a non-pass predicate, has already been consumed, or the predecessor source is no longer recoverable.
- `planned_stop_points`: `C0` plus the automated `E0` predecessor evidence gate. After both are satisfied, no ordinary task boundary requests another approval unless an `X*` condition requires design or scope change.
- `task_ordering_rationale`: make semantic content coherent before deleting its old runtime, remove executable surfaces before rewriting stable truth, generate only from the final authored boundary, and review the converged repository rather than reviewing temporary mixed states.

## Recovery

`default_failure_policy: fix_forward`. Preserve the current working tree and the smallest failing source, generated, or documentation case. Repair only the causally owning task, regenerate the exact owned surfaces, rerun focused verification, and then rerun the aggregate check. One accepted implementation finding may receive one same-slice repair; repeated, plan-expanding, or public-ID-changing failure stops through the matching `X*` condition.

`X0` is a pre-execution stop rather than a repair path. The controller preserves only redacted attestation diagnostics, does not inspect another checkout or user settings to synthesize missing evidence, and performs no repository mutation. Resuming requires a fresh valid one-time `E0` bound to the same approved plan and migration run.

The predecessor source remains available until repository-only acceptance passes, but it is not restored as an active package or runtime by this plan. Recovery does not edit user settings, another repository, consumer links, or provider state; destructively reset the working tree; delete unrelated stage history; commit; push; publish; deploy; or recreate a host adapter inside this repository.

## Truth Sync Handoff

`truth_sync_required: true`. Stable truth targets are `AGENTS.md`, `README.md`, `docs/architecture/install-surface.md`, `docs/architecture/invocation-contract.md`, `docs/architecture/maintenance-contract.md`, and `docs/architecture/workflow-orchestration.md`. They must distinguish authored source, generated portable Skills, repository-private semantic contracts, static checks, and optional provider plugin manifests without claiming host enforcement or a maintained runtime.

Truth-sync predicates are `semantic-only-ownership`, `standard-skill-surface`, `contract-non-executability`, `static-check-boundary`, `generated-payload-closure`, `provider-neutral-review-semantics`, `no-host-installation`, and `stage-history-subordination`. Historical stage artifacts may describe the migration, but maintained source, stable docs, tests, and generators may not depend on or advertise the separated host product.
