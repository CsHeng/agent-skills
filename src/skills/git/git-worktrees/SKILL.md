---
name: git-worktrees
description: "Use for explicit Git worktree operations: create or isolate, list, compare, integrate, clean up, or repair. Read only the selected operation's guidance; ordinary current-checkout work does not require worktree setup."
---

# Git Worktrees

Manage the requested worktree operation without losing user work or task context.

## When Isolation Is Needed

For ordinary implementation, reuse the current checkout unless an explicit request, applicable repository rule, required branch state, or concrete conflict calls for isolation. Task-local uncommitted documents and unrelated non-overlapping edits do not require a worktree or a preliminary commit. `implement-change` owns the checkout/concurrency judgment; this Skill owns the selected worktree operation, not a universal clean-tree gate.

A confirmed concurrent writer matters when writes or shared resources conflict. Dirty state, timestamps, or the mere presence of an agent process are not enough; do not audit the workstation to rule out hypothetical concurrency. Respect an explicit worktree request without requiring evidence that the user could not work in place.

## Choose The Operation

Establish the repository and existing worktrees with read-only checks:

```bash
git rev-parse --show-toplevel
git worktree list --porcelain
git status --short
```

If the requested operation, branch, base, or target is ambiguous, resolve that specific question before mutation. Read only the reference for the selected operation:

| Operation | Read when needed |
| --- | --- |
| List | Use the listing below; no creation preflight is required. |
| Create or isolated handoff | [Creation And Context](references/create-and-context.md) |
| Compare branches or worktrees | [Comparison](references/compare.md) |
| Integrate selected changes | [Integration](references/integrate.md) |
| Remove, prune, or repair | [Cleanup And Repair](references/cleanup-and-repair.md) |

Do not load every reference up front. List and Compare do not require a new location, ignore setup, or context transfer.

## Host-Managed Task Workspaces

A host that provides isolated task workspaces under an approved execution contract does not thereby ask the model to activate this Skill or perform duplicate creation/cleanup. Use this Skill for an explicit Git worktree operation. Keep needed input versions and environment separate: parent dirty state does not prohibit implementation or another dispatch, while a normal new checkout does not automatically inherit uncommitted input. Do not require automatic commit/stash to begin. Same-task continuation can reuse one workspace; final disposition belongs to the authorized owner, not a process-exit shortcut.

## Shared Boundaries

- Follow applicable repository instructions. A repository-defined worktree location takes precedence; only when no policy exists, default new worktrees to `./.agents/worktrees/<branch-slug>/`. A different declared location is not itself a reason to stop.
- Resolve the actual target once and use it throughout the selected operation. Never silently substitute a parent-directory, home-directory, or default path. If the request and policy cannot be reconciled safely, ask about that conflict.
- Worktree creation, integration, deletion, and history changes require their applicable authority. Listing or comparing does not grant mutation, and implementation authority does not imply commits or cleanup of user worktrees.
- Protect modified, staged, untracked, ignored, and uniquely committed work. A clean status alone does not prove that removal is safe. Preserve required task context and local overrides explicitly; a new worktree does not inherit uncommitted state.
- Never delete worktrees with `rm -rf` or use force as a default. Stop rather than lose work, invent a transfer mechanism, or widen authority.

## List

```bash
git worktree list --porcelain
```

Report each actual path and checked-out branch or detached commit, with relevant locked/prunable state. A location comparison may be useful when a repository policy is already known; do not require creation-path validation merely to list existing worktrees.
