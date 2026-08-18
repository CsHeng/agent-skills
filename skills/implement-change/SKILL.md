---
name: implement-change
description: "Implement an approved plan end to end with runtime actor/model binding, conditional serial or parallel execution, bounded agent-native review, controller-owned repair, and typed close routing."
---

# Implement Change

Run an approved plan as one lifecycle unit and keep control until the next typed boundary.

## Use This Skill When

- the user approved a plan and wants it implemented
- the harness must drive task execution, verification, bounded review, repair, and closeout
- the plan defines a serial path or explicitly approved parallel batch

## Runtime Contract

Before implementation, read completely:

- `references/workflow.toml`
- `references/repair-loop.md`

Resolve both relative to this `SKILL.md`. The cross-skill graph stays acyclic; repair is internal controller state.

The deterministic execution helper is bundled with this skill. Resolve it before changing into the target repository; the assignment below is explicit and does not rely on an ambient variable:

```bash
SKILL_ROOT="/absolute/path/to/implement-change"
RUNNER="$(realpath "$SKILL_ROOT/scripts/harness/execute-runner.sh")"
[[ -f "$RUNNER" ]] || exit 1
```

Before mutation, require an approved execution-grade plan and materialize its immutable task projection:

```bash
bash "$RUNNER" entry-phase
[[ "$(bash "$RUNNER" approval-status "<plan-file>")" == "approved" ]] || exit 1
bash "$RUNNER" validate "<plan-file>"
bash "$RUNNER" mode "<plan-file>"
bash "$RUNNER" allowed-touch-set "<plan-file>"
bash "$RUNNER" allowed-external-touch-set "<plan-file>"
bash "$RUNNER" verification-commands "<plan-file>"
bash "$RUNNER" task-catalog "<plan-file>"
bash "$RUNNER" task-ledger "<plan-file>"
```

Use the remaining runner operations for the one-time worktree preflight, ready-set and runtime binding, controller convergence, evidence-based recovery, final evaluation gate, and machine-checkable execution result. The approved `allowed_touch_set` is exactly the plan's implementation and test refs. Each task's declared `verification_scope` must pass before its ledger state converges.

For an approved task with `external_impl_file_refs`, the main controller alone uses `external-baseline`, `external-prepare`, `external-apply`, and recovery-only `external-cleanup`. Capture the immutable baseline after the task enters `in_progress` and before mutation. `external-prepare` atomically persists a metadata-only `staging` reservation before any raw payload may survive, then stages and promotes that same reservation to `prepared`; replay resumes either checkpoint without widening the ref set. `external-apply` persists after-evidence and completed private-artifact cleanup as one recoverable result. Exact parent state may apply, exact candidate state becomes an idempotent applied checkpoint with parent-directory fsync, and every third state stops with typed baseline drift. Convergence requires the complete applied-and-cleaned chain. A later accepted repair appends the next contiguous intent whose parent is the preceding applied after-state while retaining the original baseline root. Never refresh the baseline, invoke a generic external editor, delegate the write, or synthesize rollback.

## Workflow

1. Confirm plan approval, dependency state, execution continuity, and current checkout/worktree decision.
2. Bind each ready approved task to a main agent or worker, an effective concurrency width, and a runtime model policy. `plan-change` owns task IDs, dependencies, parallel groups, policies, semantic profiles, isolation, locks, and approval; this skill owns only runtime binding and physical execution.
3. Default eligible tasks to their approved delegation advice and `semantic-routing`. Start physical selection from the parent model and reasoning profile. Emit no override when it satisfies the active user or host route, an effort-only uplift when the model remains valid, or model plus explicit effort when the model changes. `inherit-main` preserves the exact approved serial or parallel topology, task IDs, dependencies, isolation, locks, touch sets, and oracles.
4. Execute serially unless the plan explicitly approves a dependency-frozen, conflict-free parallel batch. Effective concurrency is bounded by runtime capacity, ready tasks, approved limits, isolation, write sets, and locks. Record evidence when `allowed` work serializes; return a typed capacity stop when `required` parallel work cannot run.
5. Maintain a task ledger rather than relying on conversation memory. Treat its task topology and safety fields as an immutable projection of the approved plan; a mismatch returns dependency-freeze conflict evidence instead of a binding. Workers use their assigned isolated worktree where required and return evidence only; they cannot delegate recursively, widen scope, integrate peer work, adjudicate review findings, repair, or decide continuation.
6. Verify each worker's actual changed paths and task oracles, then converge a completed batch through this controller before making any dependency on a batch member ready. Count the controller/main actor at most once in a concurrent binding.
7. Construct a bounded review brief containing only the approved task slice, exact repository diff, tests, verification evidence, repository touch set, exact external refs, ordered intent identities, root-before/final-after hashes and metadata, redacted task-specific conformance evidence, and justified supporting files. Never include an external preimage, raw configuration, or staged payload.
8. Route the brief through `review-change`; prefer a reviewer subagent for non-trivial review and permit direct main-agent review for small mechanical changes.
9. Independently adjudicate every material candidate and assign the final disposition.
10. Repair only findings with disposition `accepted`, batching the complete accepted set inside the approved touch set.
11. Rerun affected and declared verification, then perform focused verification review of accepted findings and repair-introduced regressions.
12. When review and verification pass, derive the tail route from the approved plan and immutable execution result. If truth sync is required, invoke `sync-truth` through its approved-controller context, prepare the bounded stable truth update, and stop only at its human approval gate. If truth sync is not required, route directly to `close-change`; otherwise return the exact typed stop.

After every task is converged, record `task-complete`, `truth-sync-pending`, or `ready-for-close` in the execution result rather than relying on conversation state. A required truth-sync route is continuous controller work under the approved plan and does not require the user to invoke another skill. Return the pending truth approval gate, close entry, or exact typed stop directly; do not insert a confirmation question when the evidence already determines continuation.

## Runtime Binding Backends

Runtime binding is a backend concern layered under this controller. The runner's `controller-binding-envelope` operation builds one backend-neutral core — controller identity and nonce, plan and ledger digests, binding kind, the immutable task projection or hashed review brief, derived runtime role, semantic profiles, isolation, touch set, resource locks, batch provenance, and model policy — and projects it onto a selected backend with `--backend codex-native` or `--backend herdr` (the flag-absent default stays `herdr` and its `schema_version: 1` wire shape is byte-compatible for the existing adapter). The neutral core is the only part reusable contracts may reference; backend extensions carry runtime evidence only. No backend may rewrite approved task IDs, dependencies, DAG topology, delegation policy, isolation, locks, touch sets, or oracles: `plan-change` keeps topology authority, and this controller keeps binding authority.

Derive runtime roles from the approved task and gate context regardless of backend: a bounded review brief uses a `reviewer`, a pure `fast`/`light`/`shared-read-only` search or factual-confirmation task with no implementation or test write refs may use an `explorer`, and every other delegated task is a `worker`. A reviewer is read-only and returns candidate findings only. An explorer is bounded read-only and reports evidence and open questions instead of synthesizing a design; its authority is independent of physical model or effort, so a stronger parent profile or minimum uplift never expands its scope and there is no physical reasoning ceiling in the portable role contract. A writer uses only its assigned isolated, task-scoped worktree. Reviewers and workers must not delegate recursively. For mixed search-and-judgment work, bind only explicit explorer task IDs to the explorer role and return their bounded facts to the main-owned synthesis task.

`semantic-routing` is the default model policy. The parent session is the physical baseline, while user or host instructions own concrete role families and minimum-only reasoning policy. `inherit-main` or `runtime-default` may change only binding resolution evidence and must not change topology. If a required semantic uplift is unsupported, return `controller_binding_required_uplift_unsupported`; never retry through `[agents]` defaults, omit required fields, or bind below the active minimum.

### Codex-Native Backend

`--backend codex-native` emits a `schema_version: 2` envelope (neutral core plus a codex extension) and binds delegated actors through Codex Multi-Agent V2 role agent files. Role files are user-owned and never tracked in this repository: the runner resolves `<repo>/.codex/agents/<role>.toml` ahead of `~/.codex/agents/<role>.toml` (or `$CODEX_HOME/agents/`), rejects symlinked role files, and validates the selected file before any emission. Every role file must pin neither model nor reasoning effort. Reviewer and explorer files pin a read-only sandbox; the worker file for tasks with write refs declares a workspace-write sandbox whose writes are bounded by the per-spawn working directory pointed at the assigned isolated worktree. A delegated task without write refs must bind a read-only sandbox on the shared checkout.

Every model policy spawns through the validated role agent file; no policy path emits a binding without it. The Codex extension binds the parent reasoning effort and active minimum reasoning effort, and pre-emission validation requires any explicit or default effective effort to be at least both values. `semantic-routing` may use parent inheritance, effort-only uplift, or model-plus-explicit-effort uplift. A model-only override is invalid because it would silently use the new model's default effort. `inherit-main` emits no per-spawn values. `runtime-default` emits no per-spawn values and records `agents-defaults` when either corresponding default is configured or `parent-inherit` when both are absent. Only resolution evidence differs; task topology and authority do not.

Pre-emission validation returns distinct typed capability stops instead of degraded bindings: multi-agent support disabled, a configured `agents.max_depth` other than 1 (an unconfigured depth is recorded as residual instruction-only enforcement evidence), a missing, unparsable, or required-field-omitting role file, any forbidden model or effort pin, a writable reviewer or explorer sandbox, an isolation conflict with the task, a model-only semantic override, an unsupported required uplift, and missing per-spawn working-directory support for a delegated writer. Supported runtime efforts above a user minimum, including `max` or `ultra` where the selected model supports them, are not role-contract errors. `binding_kind=command-job` is not available on this backend; long local verification stays with the main controller or the Herdr command-job path. On a required-uplift stop, use main-agent execution only when the unchanged task already permits that fallback; otherwise return a manual decision without downgrading.

### Herdr Backend Overlay

An explicit `implement-change-via-herdr` request is a lower-plane adapter composition, not a second lifecycle controller. Keep the initiating main agent as the sole `orchestrator`; it is never launched again in a Herdr child pane. At runtime, this controller binds each actor to concrete CLI, model, reasoning effort, permission mode, sandbox mode, checkout or worktree, Herdr workspace/tab/pane/agent IDs, and corresponding evidence; these physical bindings are runtime evidence under the same neutral core. Herdr owns only resources created by the current adapter run and cannot choose tasks or grant external authority.

Use `controller-binding-envelope` with `binding_kind=delegated-task` only for one ledger-selected ready task. After every task has converged, the same controller operation may use `binding_kind=bounded-review` with an independently hashed review brief to bind the reviewer; that path cannot reopen task selection or mutate the ledger. Pin Codex and Grok through their native argument profiles, sanitize sensitive child environment names, target live agents by pane ID, and retain opaque terminal and available agent-session identities as runtime evidence. Under `semantic-routing`, apply the absolute low-default/medium-ceiling explorer rule. `inherit-main` and `runtime-default` may change model or reasoning binding only when the resulting explorer remains at or below that ceiling; otherwise return the typed capability result or use the approved main fallback.

For long local verification commands, the controller may issue a separate `binding_kind=command-job` envelope only for an approved task or gate. It pins the exact checkout cwd, literal argv/command, provenance, bounded timeout/output, validated maximum concurrency, and exact task resource locks. The Herdr adapter runs it with `pane run` in an owned non-agent pane, shares lease/member capacity and lock ownership with delegated work, and returns redacted process/output/exit evidence. Ordinary command jobs have no agent lifecycle and never claim task success from exit zero; the main controller retains oracle judgment.

The main controller alone validates changed paths and oracles, converges batches, adjudicates review findings, repairs accepted findings, continues the approved plan, and routes truth sync or close. No delegated actor may integrate peer work, widen scope, push, deploy, invoke provider actions, repair, decide continuation, sync truth, or close.

## Repair Ownership

- This skill is the only implementation repair owner.
- Reviewers return candidate evidence; they do not edit, continue, or decide scope.
- Severity, reviewer confidence, or a reviewer scope label is never sufficient repair authority.
- Only `accepted` findings may be repaired.
- An accepted external-file repair stays with the main controller and appends one parent-linked broker intent inside the same exact ref set; review never grants wider read or write authority.
- `pre_existing`, `unrelated`, low-confidence, out-of-scope, and future-phase findings never enter local repair.
- One initial bounded review and one focused verification review are the normal path.
- One additional repair attempt is allowed only when focused verification proves the accepted repair is incomplete or introduced a regression in the same bounded slice.
- A repeated finding after that, scope expansion, plan/design change, new authority, or unavailable external evidence exits with the matching typed state instead of more edits.

## Recovery Policy

- Read each task's `failure_policy` before mutation. The approved task policy and the user's latest explicit recovery directive outrank generic workflow-mode labels.
- `fix_forward` is the default: preserve backups or snapshots, diagnose the observed failure, repair inside the approved touch set, rerun the narrow oracle, and continue toward cutover.
- `stop_and_diagnose` preserves current state and evidence and stops further mutation; it does not restore old state.
- `guarded_rollback` is allowed only when the approved task declares an exact trigger, target, and rollback verification, the trigger is observed, safe forward repair is unavailable, and rollback is tested and safer.
- Never synthesize rollback functions, error traps, restore steps, release reversion, or automatic rollback because a change is classified as regulated or because verification failed.
- Treat HA, VRRP, failover, retained data, and previous releases as recovery surfaces, not implicit instructions to restore the old release.
- Failure count is diagnostic evidence only. Replan only when evidence proves the task graph or touch set is insufficient; redesign only when evidence proves the approved boundary is invalid.

## Execution Continuity

- `continuous_after_plan_approval`: continue without new questions unless a declared runtime contingency is observed.
- `pre_confirmation_required`: resolve the named `C*` items before mutation.
- `not_ready`: stop and route to the declared design or plan entry.
- Runtime contingencies are reactive evidence conditions, not routine checkpoints.
- Do not reopen plan-approved decisions unless live evidence contradicts the plan.

## Resume And Completion

- After interruption or compaction, recheck the latest user request, task ledger, worktree, and last completed write/deploy step.
- Verification does not imply that a write, install, deploy, commit, or push completed.
- Treat delegated review output as a claim to adjudicate, not an authoritative instruction.
- Do not claim completion without fresh verification from the current execution turn.

## Operating Rules

- Serial-first and no unattended expansion are defaults. Conditional parallelism never authorizes undeclared work, shared writable checkouts, or new authority.
- The approved plan is the atomic execution unit; do not stop while ready in-scope tasks remain.
- Prefer red-green or a narrow reproducer for non-trivial behavior changes.
- Diagnose reproducible root cause before repair.
- Never allow a delegated worker or reviewer to delegate recursively or invoke this controller.
- Report known gate states directly instead of hedging or asking whether to continue.
