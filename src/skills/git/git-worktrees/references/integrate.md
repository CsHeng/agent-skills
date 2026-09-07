# Integration

Read only when the user authorizes bringing changes from a worktree or branch into a specific destination. A comparison or creation request does not authorize integration or a commit.

Resolve the actual destination and source, selected paths/commits, and intended change. Inspect destination staged and unstaged work before mutation:

```bash
git -C "$destination_dir" status --short
git -C "$destination_dir" diff
git -C "$destination_dir" diff --cached
```

Proceed only with a clean or intentionally staged state whose contents and overlap are understood. Preserve unrelated work; do not use a reset, stash, or overwrite as an implicit cleanup step. If the selected changes are unclear, compare first using only the needed [Comparison](compare.md) guidance.

Choose the narrowest authorized operation. `source_ref`, `source_commit`, and `relative_file` below are resolved inputs; branch-based commands do not transfer source-worktree uncommitted changes.

```bash
# Whole selected file
git -C "$destination_dir" restore --source="$source_ref" -- "$relative_file"

# Selected hunks; requires an available interactive selection path
git -C "$destination_dir" restore -p --source="$source_ref" -- "$relative_file"

# Selected commit, leaving the result for review rather than committing it
git -C "$destination_dir" cherry-pick --no-commit "$source_commit"

# Whole branch only when that is the authorized scope
git -C "$destination_dir" merge --no-commit --no-ff "$source_ref"
```

These are alternatives. The branch merge uses `--no-ff` because `--no-commit` alone does not pause a fast-forward. Do not substitute a whole-branch merge for selected files or hunks. If needed changes are uncommitted at the source, require an explicit faithful transfer method rather than pretending the branch ref contains them.

On conflict, preserve the state and report conflicting paths. Resolve only within the authorized change; an abort, rollback, or broader merge needs an applicable recovery policy. Do not claim integration succeeded from a partial command result.

Review the resulting status and both staged/unstaged diffs, and run the destination's required verification. Commit only with explicit user authority for the selected result. Do not remove the source worktree merely because integration was requested or a command exited successfully.
