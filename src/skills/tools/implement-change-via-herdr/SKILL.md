---
name: implement-change-via-herdr
description: "Execute an already approved delegated implementation task through owned Herdr tabs and panes. Use only when the user explicitly requests $implement-change-via-herdr or asks to run an approved plan through Herdr; this lower-plane adapter requires a runner-issued binding envelope, HERDR_ENV=1, and a caller-supplied Herdr executable."
---

# Implement Change Via Herdr

This is an explicit lower-plane adapter. It consumes the immutable controller-binding envelope created by `implement-change`; it never selects tasks, changes the ledger, converges work, reviews, repairs, or derives a lifecycle tail.

Use the bundled adapter for the bounded agent sequence:

`preflight -> allocate -> shell-ready -> start -> prompt -> wait -> collect -> cleanup`

For a controller-issued long local verification, use the separate ordinary command-job sequence. It shares the controller lease, exact selected-member capacity, and resource-lock ownership, but it never creates or prompts an agent:

`preflight -> allocate -> shell-ready -> command-start -> command-wait -> command-collect -> cleanup`

The command envelope pins an existing non-symlink `cwd`, a literal argv vector (and optional matching literal command), task-or-gate provenance, bounded timeout/output, validated maximum concurrency, exact non-empty resource locks, and a fresh controller nonce. The adapter invokes `pane run` in the owned child pane, observes pane-specific process/output/exit evidence, redacts bounded evidence, and marks `oracle_judgment_required`; exit zero is never a task-success decision. It rejects injected command syntax, invented task or agent fields, foreign cwd, missing or conflicting locks, unbounded waits/output, and ledger mutation.

Pass a caller-owned fake-safe Herdr executable explicitly during tests and local trials. The adapter rejects symlinks and shims, so live runs pass the resolved real Herdr binary. It requires `HERDR_ENV=1`, exact caller context IDs, an approved matching repository and worktree, a fresh envelope nonce, and an enforceable per-CLI delegated capability profile. It validates the live caller hierarchy, blanks sensitive child environment names, uses exact native argument vectors, keeps child resources background and run-owned, bounds waits and evidence, and persists owner-only atomic state below `<repo-root>/.herdr-runs/`.

For parallel execution, the envelope also carries the controller-issued batch identity, effective width, and exact selected task membership. The adapter admits one independent run member per approved task attempt and rejects duplicate attempts, width exhaustion, and foreign controller, plan, workspace, or group access. Each member owns its own lifecycle and cleanup evidence; the controller lease is released only after the final live member is gone.

Read [runtime-contract.md](references/runtime-contract.md) before invoking the script. The executable entry point is:

```text
python3 scripts/herdr-runtime-adapter.py COMMAND --envelope PATH --herdr-executable PATH
```

Supported commands are `preflight`, `allocate`, `shell-ready` (also `shell-readiness` or `ready`), `start`/`run`, `prompt`, `wait`, `collect`, `command-start`/`command-run`, `command-wait`, `command-collect`, `resume`, `recover`, and `cleanup`. The controller remains responsible for task verification, convergence, review invocation, candidate adjudication, repair, and close decisions. The same envelope operation can bind an approved delegated task or, only after ledger convergence, a digested bounded-review brief; the adapter still cannot select either one.
