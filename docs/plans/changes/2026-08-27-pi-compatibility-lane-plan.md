+++
artifact_kind = "plan"
contract_version = 4
design_ref = "2026-08-27-pi-compatibility-lane-design.md"
design_sha256 = "db708aa9b53ba5754123b6a4b48da0e1714b7d497a8037ae31662157597139e7"
approval_status = "approved"
truth_sync_required = false
stable_truth_refs = []
default_runtime_model_policy = "inherit-main"
parallel_execution_approved = false

[scope]
impl_file_refs = [".pi/settings.json", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi"]
test_file_refs = ["integrations/pi/tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "PI-010"
depends_on = []
verification_commands = ["python3 src/skills/disciplines/organize-docs/scripts/normalize-markdown-prose.py --root . --immutable-manifest contracts/markdown-prose.toml --mode check", "node --experimental-strip-types --test integrations/pi/tests/provider.test.ts", "git diff --check -- docs/plans/2026-08-27-agent-skills-pi-handoff.md integrations/pi"]
scope_slice = "Correct the P0 handoff facts and Markdown defects, then create the trusted project-local Pi settings, private package, Ante Responses provider adapter, provider tests, and boundary README without changing any existing runtime or generated skill payload."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["pi-integration-source", "pi-handoff-stage-artifact"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["The handoff says 40 generated skills and passes the repository Markdown prose rule.", "Project-local Pi settings select exactly one extension path, one generated skill root, the Ante provider, and the four gateway-advertised model-cycle IDs without storing a key or base URL.", "The package registers no provider without both Ante variables and registers only the four gateway-advertised GPT-5.5/5.6 model IDs when both variables are present.", "No credential value, automatic model switch, trust decision, resource discovery hook, tool interception, or lifecycle implementation exists in the source."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = [".pi/settings.json", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi/package.json", "integrations/pi/README.md", "integrations/pi/extensions/csheng-workflow/provider.ts"]
test_file_refs = ["integrations/pi/tests/provider.test.ts"]
external_impl_file_refs = []

[[tasks]]
task_id = "PI-020"
depends_on = ["PI-010"]
verification_commands = ["node --experimental-strip-types --test integrations/pi/tests/*.test.ts", "git diff --check -- integrations/pi"]
scope_slice = "Implement P2 observation-only session aggregation, current-branch replay, opt-in sanitized JSONL persistence, public Pi event hooks, status, completion notification, and deterministic P3 tests."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["pi-integration-source", "pi-session-state-schema", "pi-telemetry-schema"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["A low-level retry or compaction increments one settled run rather than emitting premature completion, and only `agent_settled` finalizes the record.", "Replay selects the latest valid custom record from an explicitly supplied current branch and ignores malformed, foreign, and off-branch test entries.", "Telemetry contains aggregate timing, provider/model, turn/tool/error counts, and outcome but no prompt, tool input, tool output, API key, or absolute session path.", "The extension registers observation hooks and a status command without returning a `tool_call` policy result or changing active tools, model, trust, resources, or system prompt."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["integrations/pi/README.md", "integrations/pi/extensions/csheng-workflow/index.ts", "integrations/pi/extensions/csheng-workflow/state.ts", "integrations/pi/extensions/csheng-workflow/telemetry.ts"]
test_file_refs = ["integrations/pi/tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "PI-030"
depends_on = ["PI-020"]
verification_commands = ["node --experimental-strip-types --test integrations/pi/tests/*.test.ts", "printf '%s\\n' '{\"id\":\"commands\",\"type\":\"get_commands\"}' | pi --mode rpc --offline --approve --no-session --no-tools | jq -e 'select(.id == \"commands\" and .success == true) | ([.data.commands[] | select(.source == \"skill\") | .name] as $skills | ($skills | length) == 40 and ($skills | unique | length) == 40 and ([.data.commands[] | select(.name == \"csheng-status\")] | length) == 1)'"]
scope_slice = "Complete P3 by trusting the repository-local Pi settings, loading the exact extension through Pi's public runtime with no model call, and proving its single configured skill path exposes 40 unique skill commands, then repair only defects inside the observational package."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "balanced"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["pi-integration-source", "pi-rpc-smoke", "generated-skill-read"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["Pi 0.84.2 loads the project-local extension in offline RPC mode without startup errors or a model request.", "RPC returns exactly 40 distinct `skill:*` commands from the one configured `skills/` root and no duplicate public ID.", "All deterministic integration tests pass after the runtime smoke."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = ["integrations/pi"]
test_file_refs = ["integrations/pi/tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "PI-040"
depends_on = ["PI-030"]
verification_commands = ["bash -n integrations/pi/scripts/run-field-probes.sh", "bash integrations/pi/scripts/run-field-probes.sh", "pi --approve --list-models ante", "git status --short"]
scope_slice = "Use the explicitly authorized trusted project settings to verify the four Ante Responses models without copying the credential, run one minimal connectivity smoke per model, and collect at least five read-only P4 repository probes with explicit tool and model selection plus opt-in ignored telemetry."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "standard"
isolation = "controller-checkout"
resource_locks = ["pi-project-settings", "ante-api-quota", "pi-field-telemetry"]
convergence_required = true
review_budget = 1
task_review_depth = "focused"
done_when = ["Pi's effective catalogue lists `ante/gpt-5.5`, `ante/gpt-5.6-sol`, `ante/gpt-5.6-terra`, and `ante/gpt-5.6-luna` and no configured unavailable Pro or duplicate alias entry.", "Each configured model completes one bounded OpenAI Responses request through Pi without credential output.", "At least five read-only probes return their declared factual oracle, use no mutation-capable tool, and produce sanitized aggregate records under `.dist/pi-experiment/runs`.", "Tracked repository state contains only the approved P0-P3 source, tests, project settings, and artifacts; telemetry remains ignored and the global Pi configuration remains unchanged."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = [".pi/settings.json", "integrations/pi/README.md", "integrations/pi/scripts/run-field-probes.sh"]
test_file_refs = ["integrations/pi/tests"]
external_impl_file_refs = []

[[tasks]]
task_id = "PI-050"
depends_on = ["PI-040"]
verification_commands = ["bash scripts/check.sh", "git diff --check"]
scope_slice = "Run aggregate repository acceptance and one bounded implementation review over the complete observational lane; repair only accepted findings that remain inside the approved source, tests, and P0 handoff correction."
executor_mode = "main"
parallel_group = "none"
parallel_policy = "forbidden"
delegation_policy = "forbidden"
execution_profile = "deep"
reasoning_profile = "deep"
isolation = "controller-checkout"
resource_locks = ["repository-acceptance", "pi-integration-source", "pi-session-state-schema", "pi-telemetry-schema"]
convergence_required = true
review_budget = 1
task_review_depth = "full"
done_when = ["The repository aggregate check and `git diff --check` pass from the converged tree.", "A bounded review finds no introduced secret-handling, state-replay, telemetry, provider-catalog, public-Pi-API, or scope-boundary defect.", "No generated skill, legacy runtime, contract, plugin manifest, stable architecture document, commit, push, publish, or release is changed."]
failure_policy = "fix_forward"
rollback_trigger = ""
rollback_target = ""
rollback_verification = ""

[tasks.scope]
impl_file_refs = [".pi/settings.json", "docs/plans/2026-08-27-agent-skills-pi-handoff.md", "integrations/pi"]
test_file_refs = ["integrations/pi/tests"]
external_impl_file_refs = []
+++
# Plan

## Implementation

The plan executes `PI-010` through `PI-050` serially because every slice uses the same controller checkout and later evidence depends on the earlier package shape. `PI-010` establishes P0 plus the trusted project settings and provider boundary, `PI-020` implements observation and deterministic state, `PI-030` proves P3 against the installed Pi runtime, `PI-040` enters P4 through the repository-local configuration and read-only API-backed probes, and `PI-050` performs aggregate acceptance and bounded review. No parallel batch or subagent is declared.

Architecture decision reference: `PI-COMPAT-001`. Reversible increments are package/provider, state/telemetry, no-model runtime smoke, local live field sample, and final acceptance. The observable upgrade trigger remains five valid P4 records with no authority or secrecy violation; this plan does not pre-authorize P5 or P6 implementation.

Persisted implementation decisions: `PI-010` creates an `extension-package` in TypeScript because Pi's public extension API, package loader, and type contracts are TypeScript-native; `PI-020` extends that same TypeScript boundary so parsing, state validation, and telemetry rules stay in one implementation language. `PI-040` adds a small Bash 4-compatible `shell-orchestration` runner because its complete responsibility is a linear sequence of existing Pi, Git, and jq commands with exact assertions; it owns no parsing schema, persistent state, retry policy, or reusable workflow rule.

## Work Package Readiness

- `milestone_objective`: deliver and validate one observation-only Pi compatibility lane through P3 and collect the first bounded P4 field sample.
- `non_goals`: all P5/P6 tool gates, artifact/lifecycle/review behavior, runtime removal, model routing, parallelism, regulated work, plugin release, commit, push, publish, and stable architecture supersession.
- `future_phase`: P5 may design explicit modes plus mechanical gates and a micro slice after the P4 trigger; P6 may design the standard lifecycle, artifact/review verdict contract, and bounded repair only after P5's gate/state contract is proven.
- `decision_status`: `ready_for_review`.
- `oracle_strategy`: pure example and negative tests for provider/state/telemetry contracts, public Pi no-model RPC probes for load and discovery, exact gateway catalogue evidence, bounded live Responses probes, read-only factual task oracles, and repository aggregate acceptance.
- `acceptance_oracles`: every task's exact verification commands and `done_when` evidence plus one final bounded implementation review.
- `execution_continuity`: `continuous_after_plan_approval`.
- `max_review_batches`: `2`, one direct design/plan boundary review before approval and one implementation review with at most one same-slice repair verification.
- `subagent_ready`: `false`; the plan is deliberately main-agent serial, and current collaboration policy also disallows delegation.

## Execution Continuity

- `execution_mode`: `continuous_after_plan_approval`.
- `confirmation_clearance`: `C1` is `pre_confirmed` by the user's 2026-08-27 message for P0-P4 repository changes, trusted project-local Pi configuration, use of the existing mise Ante credential without disclosure, bounded API cost, and no push; `C2` is `deferred_not_in_scope` for P5/P6 implementation.
- `runtime_contingencies`: `X1` stops on any credential or sensitive payload exposure; `X2` stops if the gateway's Responses behavior is incompatible with Pi's public transport; `X3` stops on tracked mutation outside the approved refs or any mutation from a read-only field probe; `X4` stops if completing the slice requires tool gates, lifecycle authority, an unavailable model, or other scope expansion.
- `planned_stop_points`: none before the completed P4 sample and final acceptance unless an `X*` contingency is observed.
- `task_ordering_rationale`: clear factual documentation and provider contracts before stateful hooks, prove deterministic behavior before loading Pi, prove offline trusted-project load/discovery before consuming API quota, then run aggregate acceptance on the converged source.

Expected continuous range after approval: `E1 = PI-010..PI-050`.

## Recovery

`default_failure_policy: fix_forward`. Repository implementation failures retain their smallest reproducer and are repaired only inside the active task scope. `PI-040` remains fix-forward for an ordinary reproducible integration defect, but `X1` through `X4` stop the run because retrying a provider incompatibility, credential concern, unexpected mutation, or unexplained quota failure could compound risk; no contingency authorizes blind repeated API calls. The existing harness and global Pi configuration remain unchanged. `--no-approve` bypasses the project-local configuration during diagnosis; no automatic rollback or source deletion is part of this plan.

## Truth Sync Handoff

`truth_sync_required: false`, `stable_truth_refs: []`, and docs-governance predicates: `none`. This is an explicitly experimental lane whose component README and stage handoff are changed in the implementation itself; stable workflow truth and generated diagrams remain unchanged until P4 evidence justifies a separately approved supersession.
