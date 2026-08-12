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
bash "$RUNNER" verification-commands "<plan-file>"
bash "$RUNNER" task-catalog "<plan-file>"
bash "$RUNNER" task-ledger "<plan-file>"
```

Use the remaining runner operations for the one-time worktree preflight, ready-set and runtime binding, controller convergence, evidence-based recovery, final evaluation gate, and machine-checkable execution result. The approved `allowed_touch_set` is exactly the plan's implementation and test refs. Each task's declared `verification_scope` must pass before its ledger state converges.

## Workflow

1. Confirm plan approval, dependency state, execution continuity, and current checkout/worktree decision.
2. Bind each ready approved task to a main agent or worker, an effective concurrency width, and a runtime model policy. `plan-change` owns task IDs, dependencies, parallel groups, policies, semantic profiles, isolation, locks, and approval; this skill owns only runtime binding and physical execution.
3. Default eligible tasks to their approved delegation advice and `semantic-routing`. An explicit `inherit-main` override makes a worker inherit the main agent's model and reasoning settings; it preserves the exact approved serial or parallel topology, task IDs, dependencies, isolation, locks, touch sets, and oracles.
4. Execute serially unless the plan explicitly approves a dependency-frozen, conflict-free parallel batch. Effective concurrency is bounded by runtime capacity, ready tasks, approved limits, isolation, write sets, and locks. Record evidence when `allowed` work serializes; return a typed capacity stop when `required` parallel work cannot run.
5. Maintain a task ledger rather than relying on conversation memory. Treat its task topology and safety fields as an immutable projection of the approved plan; a mismatch returns dependency-freeze conflict evidence instead of a binding. Workers use their assigned isolated worktree where required and return evidence only; they cannot delegate recursively, widen scope, integrate peer work, adjudicate review findings, repair, or decide continuation.
6. Verify each worker's actual changed paths and task oracles, then converge a completed batch through this controller before making any dependency on a batch member ready. Count the controller/main actor at most once in a concurrent binding.
7. Construct a bounded review brief containing only the approved task slice, exact diff, tests, verification evidence, touch set, and justified supporting files.
8. Route the brief through `review-change`; prefer a reviewer subagent for non-trivial review and permit direct main-agent review for small mechanical changes.
9. Independently adjudicate every material candidate and assign the final disposition.
10. Repair only findings with disposition `accepted`, batching the complete accepted set inside the approved touch set.
11. Rerun affected and declared verification, then perform focused verification review of accepted findings and repair-introduced regressions.
12. When review and verification pass, derive the tail route from the approved plan and immutable execution result. If truth sync is required, invoke `sync-truth` through its approved-controller context, prepare the bounded stable truth update, and stop only at its human approval gate. If truth sync is not required, route directly to `close-change`; otherwise return the exact typed stop.

After every task is converged, record `task-complete`, `truth-sync-pending`, or `ready-for-close` in the execution result rather than relying on conversation state. A required truth-sync route is continuous controller work under the approved plan and does not require the user to invoke another skill. Return the pending truth approval gate, close entry, or exact typed stop directly; do not insert a confirmation question when the evidence already determines continuation.

## Herdr Runtime Binding Overlay

An explicit `implement-change-via-herdr` request is a lower-plane adapter composition, not a second
lifecycle controller. Keep the initiating main agent as the sole `orchestrator`; it is never launched
again in a Herdr child pane. Derive runtime roles from the approved task and gate context: a bounded
review brief uses a `reviewer`, a pure `fast`/`light`/`shared-read-only` search or factual-confirmation
task may use an `explorer`, and every other delegated task is a `worker`. A reviewer is read-only and
returns candidate findings only; reviewers and workers must not delegate recursively. An explorer is
bounded read-only and reports evidence and open questions instead of synthesizing a design. A writer
uses only its assigned isolated, task-scoped worktree.

At runtime, `implement-change` binds each actor to concrete CLI, model, reasoning effort, permission mode,
sandbox mode, checkout or worktree, Herdr workspace/tab/pane/agent IDs, and corresponding
evidence. These physical bindings are runtime evidence and must not rewrite the approved task IDs,
dependencies, serial or parallel DAG topology, delegation policy, isolation, locks, touch set, or
oracles. `semantic-routing` is the default; an explicit `inherit-main` or `runtime-default` choice
may change model or reasoning binding only and must be recorded without changing topology. Herdr
owns only resources created by the current adapter run and cannot choose tasks or grant external authority.

Use `controller-binding-envelope` with `binding_kind=delegated-task` only for one ledger-selected
ready task. After every task has converged, the same controller operation may use
`binding_kind=bounded-review` with an independently hashed review brief to bind the reviewer; that
path cannot reopen task selection or mutate the ledger. Pin Codex and Grok through their native
argument profiles, sanitize sensitive child environment names, target live agents by pane ID, and
retain opaque terminal and available agent-session identities as runtime evidence. Under
`semantic-routing`, explorer effort must be a known strict downgrade; `inherit-main` and
`runtime-default` are recorded exceptions rather than inferred downgrades.

The main controller alone validates changed paths and oracles, converges batches, adjudicates review findings,
repairs accepted findings, continues the approved plan, and routes truth sync or close. No
delegated actor may integrate peer work, widen scope, push, deploy, invoke provider actions, repair,
decide continuation, sync truth, or close.

## Repair Ownership

- This skill is the only implementation repair owner.
- Reviewers return candidate evidence; they do not edit, continue, or decide scope.
- Severity, reviewer confidence, or a reviewer scope label is never sufficient repair authority.
- Only `accepted` findings may be repaired.
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
