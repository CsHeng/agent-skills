# Amend And Unpushed Context

Read this when the user mentions amend or squash, or the branch is ahead of its upstream and recent commits may touch the same files.

## Unpushed Context

Overlap between recent unpushed commits and the current changes is context, and a new focused commit proceeds either way. Report the overlap when it is relevant:

```bash
if git -C "$TARGET_REPO" rev-parse @{u} >/dev/null 2>&1; then
  git -C "$TARGET_REPO" log @{u}..HEAD --oneline -5
  git -C "$TARGET_REPO" log @{u}..HEAD --name-only --format="" -3 | sort -u
else
  git -C "$TARGET_REPO" log --oneline -5
fi
```

## Amend

An explicit user request to amend is the rewrite authority this skill needs for that one commit. Stage the intended files and scope the amend to those paths too, so pre-existing staging for other work stays out:

```bash
git -C "$TARGET_REPO" add -- <files>
git -C "$TARGET_REPO" commit --amend --no-edit -- <files>
```

Squashing or reorganizing existing history needs its own explicit rewrite authority and is a separate task from this commit workflow.
