---
name: git-worktrees
description: "Use for git worktree workflows: create, compare, merge back, clean up, repair worktrees, or isolate feature branches."
---

# Git Worktrees

Create and manage agent-friendly git worktrees without scattering directories or losing spec and plan context.

## Core Policy

- Follow repository-local instructions first. If the repo already defines a worktree location or workflow, use it.
- If the repo has no explicit preference, default to `./.agents/worktrees/<branch-slug>/`.
- Never silently fall back to a parent directory or a home-directory location.
- Before creating a repo-local worktree, verify the directory is ignored by both Git and search tooling.
- If ignore coverage is missing, ambiguous, or inconsistent, stop and ask the user to confirm how to proceed, except during an explicitly requested isolated coding-agent handoff that uses the bounded local-exclude setup below.

## Preflight

Run these checks before creating, comparing, merging, or cleaning up worktrees:

```bash
git rev-parse --show-toplevel
git worktree list --porcelain
git status --short
```

Translate the user request into one of these modes:

| Mode | Use When |
|------|----------|
| Create/List | Starting isolated implementation work or inspecting existing worktrees |
| Compare | Reviewing differences between current worktree, another worktree, or a branch |
| Merge | Pulling selected changes from a worktree or branch into the current branch |
| Cleanup | Removing finished worktrees, pruning stale metadata, or repairing links |

If the request is ambiguous, ask one precise question before proceeding.

## Context Preservation for Spec and Plan Work

Before creating a worktree for design, spec, or implementation work, explicitly gather the files that define the task context:

```bash
fd -a AGENTS.md .
fd -a README.md .
fd -a '.*(design|spec|plan).*\.md$' docs specs .agents . 2>/dev/null
```

Then inspect their status:

```bash
git status --short -- <relevant-context-files...>
```

Apply these rules:

- If relevant design, spec, or plan files are committed on the starting branch, creating the worktree is safe.
- If relevant files are modified, staged, or untracked, stop and explain that the new worktree will not automatically include those changes.
- When stopping for this reason, list the exact context files and tell the user they need to commit them first or explicitly choose another transfer method.
- When proceeding, explicitly mention the context files that must be reviewed again inside the worktree session.

Do not assume the new worktree inherits uncommitted planning files.

For an explicitly requested isolated coding-agent handoff, an exact bounded prompt or bridge plan payload is an approved context-transfer mechanism. Do not require an untracked or modified design/plan artifact to be committed when its exact bytes and hash are transferred and the recipient is forbidden to edit it. Still stop when uncommitted source or configuration state is required in the recipient filesystem and cannot be transferred without changing semantics.

## Path Policy

When the repository does not define its own location, use this default path:

```text
./.agents/worktrees/<branch-slug>/
```

Before creating the worktree:

```bash
git check-ignore -q .agents/worktrees
```

Then verify search-ignore coverage:

```bash
if [ -f .ignore ]; then
  rg -n '^\./?\.agents/worktrees/?$|^\.agents/worktrees/?$' .ignore
elif [ -f .rgignore ]; then
  rg -n '^\./?\.agents/worktrees/?$|^\.agents/worktrees/?$' .rgignore
elif [ -f .fdignore ]; then
  rg -n '^\./?\.agents/worktrees/?$|^\.agents/worktrees/?$' .fdignore
else
  echo "No search ignore file found"
fi
```

Rules:

- `git check-ignore` must succeed for `.agents/worktrees`.
- If the repository uses `.ignore`, `.rgignore`, or `.fdignore`, the chosen file should also ignore `.agents/worktrees`.
- If there is no search-ignore file at all, ask the user whether to add one or accept search noise.
- Do not create nested worktrees elsewhere inside the repository unless the repository explicitly opted in.

### Isolated handoff local-exclude setup

An explicit isolated coding-agent handoff authorizes local, untracked ignore setup for its temporary linked worktree. When `.agents/worktrees/` is not already ignored:

1. Resolve the repository's actual local exclude file with `git rev-parse --git-path info/exclude`.
2. Refuse a symlink, directory, or path outside the repository's Git common directory.
3. Append exactly `.agents/worktrees/` once; do not edit tracked `.gitignore`, `.ignore`, `.rgignore`, or `.fdignore` merely to launch the handoff.
4. Verify `git check-ignore` and a hidden `rg --files` or equivalent search inventory both exclude a disposable path beneath `.agents/worktrees/`.

This is setup metadata, not project truth, and it must not enter the implementation diff. If the local exclude cannot be changed or verified safely, stop; do not invent a parent-directory or home-directory worktree location.

## Create or List Worktrees

### List

Use:

```bash
git worktree list --porcelain
```

Present a concise summary with:

- worktree path
- checked-out branch or detached commit
- whether the path is under `./.agents/worktrees/`

### Create

1. Derive the target branch name from the user request.
2. Normalize the path slug from the branch name.
3. Resolve the branch source:
   - existing local branch
   - remote tracking branch
   - new branch from an explicit base
4. Refuse to create if the target path already exists and is not already a valid worktree.
5. Use plain `git worktree add` by default unless the repository explicitly requires another mode.

Common command patterns:

```bash
# Existing local branch
git worktree add ./.agents/worktrees/<slug> <branch>

# Existing remote branch
git worktree add --track -b <branch> ./.agents/worktrees/<slug> origin/<branch>

# New branch from explicit base
git worktree add -b <branch> ./.agents/worktrees/<slug> <base>
```

After creation:

```bash
git -C ./.agents/worktrees/<slug> status --short
```

If the user is about to execute work immediately, mention the exact `cd` path and the context files that should be opened first.

## Compare Worktrees or Branches

Pick the smallest useful comparison:

| Need | Preferred Command |
|------|-------------------|
| Branch summary | `git diff --stat <branch-a>..<branch-b> -- <paths...>` |
| Single file across worktrees | `diff -u <worktree-a>/<path> <worktree-b>/<path>` |
| Directory overview | `diff -rq <worktree-a>/<dir> <worktree-b>/<dir>` |
| Current worktree vs branch | `git diff <branch> -- <paths...>` |

Guidelines:

- If only one other worktree exists, compare against it by default and say so.
- If multiple worktrees exist and the source is unclear, ask which one to compare against.
- Prefer `--stat` or directory summary before showing a large diff.
- For binary files or generated output, summarize the difference instead of dumping noise.

## Merge from a Worktree

Start only from a clean or intentionally staged working tree:

```bash
git status --short
```

Choose the narrowest merge strategy that fits the request:

| Strategy | Use When | Command |
|----------|----------|---------|
| Whole file restore | Take the full file from another branch | `git restore --source=<branch> -- <path>` |
| Interactive patch | Take only selected hunks | `git restore -p --source=<branch> -- <path>` |
| Selective cherry-pick | Take one commit with review before commit | `git cherry-pick --no-commit <commit>` |
| Controlled branch merge | Merge the branch but keep commit control | `git merge --no-commit <branch>` |

Merge workflow:

1. Identify the source worktree or branch.
2. Recommend a comparison first if the requested change is not fully specified.
3. Execute the narrowest strategy.
4. Review the result with `git status --short` and, when useful, `git diff --cached`.
5. Commit only after the user is satisfied with the selected changes.

Do not default to a full branch merge when the user asked for selected files or partial changes.

## Cleanup and Repair

Preferred commands:

```bash
# Remove a clean worktree
git worktree remove ./.agents/worktrees/<slug>

# Remove even with uncommitted changes
git worktree remove --force ./.agents/worktrees/<slug>

# Clean stale metadata
git worktree prune

# Repair moved or broken worktree links
git worktree repair
```

Rules:

- Never delete a worktree with `rm -rf`.
- Use `prune` after accidental manual deletion or stale metadata warnings.
- Use `git worktree repair` after moving repository-local worktrees or when links become inconsistent.
- If the worktree still contains active work, confirm before removal. An explicit isolated-handoff cleanup policy counts as confirmation only for resources created by that handoff after verified convergence proves no unique work remains.

## Failure Conditions

Stop and ask the user to confirm when any of these are true:

- the repository already declares a different worktree location
- `.agents/worktrees` is not ignored by Git and the bounded isolated-handoff local-exclude setup does not apply or cannot be verified
- search-ignore coverage is missing or ambiguous and the bounded isolated-handoff local-exclude setup does not apply or cannot be verified
- relevant design, spec, or plan files exist but are not committed and no exact handoff prompt or bridge transfer owns their bytes
- the requested branch, base, or source worktree cannot be resolved uniquely
- the target path already exists but is not a valid worktree

## Examples

### Create an implementation worktree

```text
Use git-worktrees to create an isolated worktree for implementing docs/plans/git-worktrees/2026-04-04-git-worktrees-plan.md on branch feat/git-worktrees.
```

Expected behavior:

- inspect worktree list and current status
- verify `.agents/worktrees` ignore coverage
- verify the plan file is committed or stop if it is not
- create `./.agents/worktrees/feat-git-worktrees/`
- report the exact path plus the context files to reopen there

### Compare a current branch with a worktree

```text
Use git-worktrees to compare the current branch with ./.agents/worktrees/feat-git-worktrees for skills/git-worktrees/SKILL.md.
```

### Merge one file from a worktree

```text
Use git-worktrees to merge only skills/git-worktrees/SKILL.md from ./.agents/worktrees/feat-git-worktrees back into the current branch.
```

### Clean up a finished worktree

```text
Use git-worktrees to remove ./.agents/worktrees/feat-git-worktrees and prune stale metadata.
```
