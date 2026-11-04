# Split And Merge Cases

Read this when two groups touch one file, a hunk-level split is requested, files are already staged, or `MERGE_HEAD` exists.

## Shared Files

A pathspec commit takes the working-tree content of each named path, so every unstaged change in a named path is committed with it, and the recipe cannot split one path at hunk level. When two groups touch the same file, whichever group commits first takes that file's entire current working-tree content, and the second group has nothing left for it. Assign a shared file to one owning group and state that limitation to the user, or use the hunk-level split below when the user explicitly needs one.

## Hunk-Level Split

A hunk-level split needs an index commit. Stage exactly that group's hunks with `git add -p`, confirm with `git status` that nothing else is staged, run a bare `git commit`, and verify the resulting tree. A bare `git commit` records the entire index, so it is correct only while the index holds exactly that group; when another group already has staged changes, commit the staged group first or set it aside with `git stash --staged` before hunk-staging. Pair `git add -p` with a bare commit; a pathspec commit records the whole working-tree content of the named paths and ignores staged hunks.

## Partial Staging

When some files are already staged, each path-scoped commit carries only its own group and staged changes in other paths stay staged. A whole-index `git commit` applies to the hunk-level split above and the pending merge below.

## Pending Merge

When `MERGE_HEAD` exists (for example after an authorized `merge --no-commit`), Git rejects a pathspec commit, so the grouping recipe cannot split the merge. Confirm that the index holds only the complete, verified merge result, then record it with one whole-index `git commit`, which keeps the authorized merge topology. When the user also asked for grouped commits, report that a pending merge commits as one unit.
