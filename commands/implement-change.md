---
description: Execute an approved plan with conditional controller-bound task execution, bounded agent-native review, verification, and typed closeout
argument-hint: "<approved-plan-path>"
allowed-tools: ["Agent", "Read", "Glob", "Grep", "Bash", "Edit", "MultiEdit"]
---

Use `coding:implement-change` and read its installed workflow and repair-loop references completely.

Resolve and validate the approved plan with `skills/_harness-libs/execute-runner.sh`. Require `approval_status: approved`, materialize the task catalog and task ledger, perform the one-time worktree preflight, and execute inside `allowed_touch_set = impl_file_refs + test_file_refs`.

Keep logical topology with `coding:plan-change`: task IDs, dependencies, named groups, policies, semantic profiles, isolation, locks, and approval remain immutable runtime inputs. `coding:implement-change` owns runtime binding to actors, effective concurrency, worktrees, and model policy. Default eligible delegation to approved advice with `semantic-routing`; an explicit `inherit-main` override changes only worker model and reasoning binding, never serial/parallel topology or safety metadata. `allowed` parallel work may serialize with recorded evidence; unavailable `required` parallel work returns a typed capacity stop. Workers cannot delegate recursively, widen scope, integrate peer work, adjudicate review, repair, or decide continuation.

For every task:

1. execute the task slice
2. run its narrow and declared `verification_scope`
3. construct a bounded review brief from the exact task diff and evidence
4. route task-scoped review through `coding:review-change`
5. prefer one reviewer subagent for non-trivial review; allow direct main-agent review for small mechanical changes
6. have the main agent adjudicate candidate findings
7. repair only `accepted` findings
8. run focused verification of accepted repairs and repair-introduced regressions
9. update the task ledger only after review and verification pass

Do not use a semantic review shell runner. Do not let a delegated worker or reviewer edit outside its assignment, delegate recursively, or control lifecycle continuation.

For failures, follow the task's declared `failure_policy`. Default to fix-forward diagnosis and narrow re-verification. Never synthesize rollback code, restore an old release, or widen into plan/design because a verification attempt failed or a failure count increased. Use guarded rollback only when the approved task declares its exact trigger, target, and verification and the trigger is observed.

After all tasks, combine review and verification through the deterministic evaluation gate, resolve the evidence-based recovery route, and return `sync-truth`, `close-change`, or the exact typed stop state. The machine-checkable gate decides continuation; do not ask whether to continue when that state is known.
