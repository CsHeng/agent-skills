# Comparison

Read only for comparing existing worktrees or branches. No creation location, ignore setup, or uncommitted-context transfer is required for a read-only comparison.

Resolve the requested source and target from `git worktree list --porcelain` or explicit refs. If exactly one other worktree is a reasonable comparison target, state that selection; with multiple plausible sources, ask which one. Use actual registered paths, not the default creation directory.

Choose the smallest useful comparison. In these examples the refs, absolute worktree paths, and repository-relative file/directory inputs have already been resolved:

```bash
# Committed branch summary
git diff --stat "$branch_a..$branch_b" -- "$relative_file"

# Actual filesystem contents, including uncommitted changes in that file
diff -u -- "$worktree_a/$relative_file" "$worktree_b/$relative_file"

# Directory overview
diff -rq -- "$worktree_a/$relative_dir" "$worktree_b/$relative_dir"

# Current working tree compared with a selected branch
git diff "$branch" -- "$relative_file"
```

A branch diff compares committed trees; it does not include another worktree's uncommitted state. Say which boundary the comparison covers. For `diff`, exit 1 means differences and exit greater than 1 means an error; do not mistake an unreadable path for a clean comparison.

Prefer summaries before large diffs. Summarize binary/generated differences rather than dumping noise. Do not restore files, change branches, merge, commit, or remove a worktree as part of a comparison request.
