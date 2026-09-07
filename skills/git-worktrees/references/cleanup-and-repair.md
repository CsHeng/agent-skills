# Cleanup And Repair

Read only for an explicitly requested removal, metadata prune, or link repair. Use actual paths from the worktree registry or an explicitly identified moved location, not a guessed default directory. Cleanup does not require creation ignore setup.

## Preserve Work Before Removal

Establish the exact target and applicable cleanup authority. Inspect its filesystem work and refs:

```bash
git worktree list --porcelain
git -C "$worktree_dir" status --short
git -C "$worktree_dir" status --ignored --short
git -C "$worktree_dir" diff
git -C "$worktree_dir" diff --cached
git -C "$worktree_dir" rev-parse HEAD
```

Inspect modified, staged, untracked, ignored, and required local override/context files. Do not expose secret contents in the report. Verify any preservation/transfer before deletion; ignored files may be lost even when Git considers a worktree clean.

Check whether target commits remain reachable through the intended retained branch/ref, including a detached HEAD:

```bash
git -C "$worktree_dir" log --oneline "$retained_ref..HEAD"
```

Resolve `retained_ref` from the actual integration/preservation decision, not a guessed branch name. A nonempty result needs evidence that the unique work is safely retained elsewhere or explicit disposition authority; an empty result does not cover uncommitted or ignored files. Squash/cherry-pick integration may need content evidence because commit ancestry differs. Stop when retention or integration evidence is insufficient.

A user-approved isolated-handoff cleanup policy covers only that handoff's own resources after verified convergence establishes that no unique work remains. It does not authorize deleting unrelated worktrees or branches. Active work, locked worktrees, or unclear ownership require a specific decision before removal.

## Remove

After authority and preservation checks pass:

```bash
git worktree remove -- "$worktree_dir"
```

Do not automatically retry with `--force`. A failure may reveal work or locks the preflight missed; diagnose it and obtain the needed explicit disposition. Never use `rm -rf` to delete a worktree, and do not delete its branch as an implied follow-up.

## Prune Or Repair Metadata

Prune only when stale metadata or a known accidental deletion is the actual target. Preview all affected entries:

```bash
git worktree prune --dry-run --verbose
```

Verify listed paths are truly stale, not temporarily inaccessible mounts, moved directories, or resources still in use. Locked entries and missing preservation evidence are not reasons to force deletion. With authority for the previewed set, execute and inspect the resulting registry:

```bash
git worktree prune --verbose
git worktree list --porcelain
```

For a moved or broken worktree link, resolve the correct repository and actual moved path, then use the targeted repair rather than pruning valid work:

```bash
git worktree repair -- "$worktree_dir"
git -C "$worktree_dir" status --short
git worktree list --porcelain
```

Stop if the repository/target relationship cannot be established. Neither repair nor prune authorizes removing filesystem work. After any successful cleanup, report what was actually removed or repaired and which retained-work evidence was checked.
