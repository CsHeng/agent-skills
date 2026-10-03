---
name: smart-squash
description: "Use to reorganize, squash, or clean up unpushed commits by business logic after read-only preflight and explicit rewrite approval."
---

# Smart Squash

Reorganize a branch's unpushed commits by business logic. This skill only rewrites local history: it never pushes and never rewrites commits that are already on a remote.

## Scope

This skill handles batch cleanup of unpushed commits. A request to create new commits from working-tree changes belongs to `smart-commit`. Rewriting changes every affected commit SHA, so treat it as a destructive local operation: present the proposed result and get explicit user approval before running any rebase.

## Target Repository Binding

Bind the target repository before any Git inspection or rewrite. The target repository is the Git root for the user's invocation working directory or an explicit user-supplied repository path, not the repository that stores this skill.

```bash
INVOCATION_CWD="$(pwd -P)"
TARGET_REPO="$(git -C "$INVOCATION_CWD" rev-parse --show-toplevel)"
printf 'Target repository: %s\n' "$TARGET_REPO"
```

Rules:
- Run every Git command as `git -C "$TARGET_REPO" ...`.
- Never use the plugin repository as the implicit target repository just because this skill file is loaded from there.
- The plugin repository is a valid target only when the invocation working directory resolves to it or the user explicitly selects it.
- If the resolved `TARGET_REPO` conflicts with the user's stated path, stop before running `git log`, `git diff`, `git rebase`, or any history rewrite.

## Workflow

### Phase 1: Read-Only Preflight

Validate repository state before any operation:

```bash
git -C "$TARGET_REPO" rev-parse --git-dir          # validate repository
git -C "$TARGET_REPO" status --short               # must be clean

# Refuse when a rebase or merge is already in progress
GIT_DIR=$(git -C "$TARGET_REPO" rev-parse --git-dir)
if [ -d "$GIT_DIR/rebase-merge" ] || [ -f "$GIT_DIR/MERGE_HEAD" ]; then
  echo "ERROR: repository is in rebase or merge state"
  exit 1
fi
```

A clean working tree is required; uncommitted changes are not part of the rewrite. Ask the user to commit, stash, or otherwise preserve them before proceeding, and never discard them to clear the tree.

Determine the range to rewrite, defaulting to unpushed commits:

```bash
RANGE_ARGS=()
RANGE_LABEL=""

# If upstream exists: use @{u}..HEAD
if git -C "$TARGET_REPO" rev-parse @{u} >/dev/null 2>&1; then
  RANGE_LABEL="@{u}..HEAD"
  RANGE_ARGS=("$RANGE_LABEL")
  BASE_COMMIT=$(git -C "$TARGET_REPO" merge-base @{u} HEAD)
else
  # No upstream: prompt user for range
  echo "No upstream branch detected. Select commit range:"
  echo "  1. Recent N commits (default: 10)"
  echo "  2. From specific commit/tag"
  echo "  3. All commits in current branch"
  read -r choice
  case $choice in
    1) read -r -p "Number of commits: " N; N="${N:-10}"; RANGE_LABEL="HEAD~$N..HEAD"; RANGE_ARGS=("$RANGE_LABEL"); BASE_COMMIT="HEAD~$N" ;;
    2) read -r -p "From commit/tag: " FROM; RANGE_LABEL="$FROM..HEAD"; RANGE_ARGS=("$RANGE_LABEL"); BASE_COMMIT="$FROM" ;;
    3) RANGE_LABEL="--root"; RANGE_ARGS=("--root"); BASE_COMMIT=$(git -C "$TARGET_REPO" rev-list --max-parents=0 HEAD) ;;
  esac
fi
```

Check whether other local branches reference commits in the range, since rewriting will strand them or require rebasing:

```bash
git -C "$TARGET_REPO" for-each-ref --format='%(refname:short)' refs/heads/ | while read -r branch; do
  if [ "$branch" != "$(git -C "$TARGET_REPO" branch --show-current)" ]; then
    git -C "$TARGET_REPO" log --oneline HEAD ^"$branch" 2>/dev/null
  fi
done
```

Report the actual preflight findings and their consequences: clean or dirty tree, rebase or merge in progress, the selected range and its commit count, and any other branch that references the commits. State facts and risks directly; do not wrap them in a fixed severity panel or checkmark template.

### Phase 2: Analyze and Group Commits

List the commits oldest-first with their subjects and changed files, and record the original count:

```bash
git -C "$TARGET_REPO" log "${RANGE_ARGS[@]}" --format="%H|%s" --reverse

# For each commit, list the files it touches
git -C "$TARGET_REPO" log "${RANGE_ARGS[@]}" --format="%H" --reverse | while read -r commit; do
  git -C "$TARGET_REPO" show --name-only --format="" "$commit"
done

ORIGINAL_COUNT=$(git -C "$TARGET_REPO" log "${RANGE_ARGS[@]}" --oneline | wc -l)
```

Group commits that serve the same change, in priority order:
1. Same scope: consecutive commits with the same conventional-commit scope.
2. Same files: commits touching the same file set.
3. Same type with overlapping files.
4. Ambiguous cases: present them to the user for a grouping decision instead of guessing.

Grouping rules:
- Merge consecutive related commits first.
- Non-consecutive related commits may merge, which can require reordering.
- Preserve real dependencies (for example, schema before code).
- Keep independent commits separate.

### Phase 3: Propose the Rebase Plan

For each group, decide the resulting commit:
- A single commit keeps its original message.
- A group of commits uses the first commit's message as a base, adapted to describe the combined change, with the remaining commits folded in as fixups.

Present a plan the user can decide on, including the analyzed range and commit count, each proposed merged commit with its source commits and resulting message, the commits that remain independent, and the fact that all affected SHAs change and that branches or collaborators referencing them must be handled. Show the plan directly; do not require a fixed panel or a fixed interactive menu. The user may approve, adjust grouping, ask for details, or cancel.

Do not run any rebase command until the user explicitly approves the plan.

### Phase 4: Back Up and Execute

Before rewriting, record the original tip and identify a usable recovery point under the repository's practice. The reflog and `ORIG_HEAD` can help recover a rebase, but later operations can change those references. If a temporary backup branch is useful, choose a non-conflicting task-owned name and preserve any existing branch; a fixed branch name is not a prerequisite.

Build the sequence plan from the approved groups:
- Use `pick` when the first commit's message is already the approved result, then `fixup` for the remaining commits in that group.
- Use `reword` instead of `pick` when the group's message must change, then the same `fixup` lines. Arrange an interactive editor or task-owned `GIT_EDITOR` to write the exact approved message for each `reword`; changing the description in the sequence plan does not change the commit message.

Then execute the rebase:

```bash
# Write the approved pick/reword/fixup lines to a temporary plan file
PLAN_FILE="$(mktemp)"
# ... populate "$PLAN_FILE" from the approved groups ...

if [ "$RANGE_LABEL" = "--root" ]; then
  GIT_SEQUENCE_EDITOR="sh -c 'cp \"$PLAN_FILE\" \"\$1\"' --" \
    git -C "$TARGET_REPO" rebase -i --root
else
  GIT_SEQUENCE_EDITOR="sh -c 'cp \"$PLAN_FILE\" \"\$1\"' --" \
    git -C "$TARGET_REPO" rebase -i "$BASE_COMMIT"
fi

# Handle conflicts
if [ $? -ne 0 ]; then
  echo "ERROR: rebase stopped. Resolve conflicts, then:"
  echo "  git -C \"$TARGET_REPO\" rebase --continue  # after resolving conflicts"
  echo "  git -C \"$TARGET_REPO\" rebase --abort     # abandon the whole operation"
  exit 1
fi
```

After completion, compare the resulting groups and full commit messages with the approved plan. Show the resulting history and the before/after commit counts:

```bash
FINAL_COUNT=$(git -C "$TARGET_REPO" log "$BASE_COMMIT"..HEAD --oneline | wc -l)
git -C "$TARGET_REPO" log --oneline --graph -n $((FINAL_COUNT + 5))

echo "Original commits: $ORIGINAL_COUNT"
echo "Reorganized commits: $FINAL_COUNT"
```

Report the recovery point and the outcome. Remove a task-created backup branch only after the result is accepted and cleanup is authorized; do not delete or expire reflog entries or unrelated references as routine cleanup.

## Constraints

- Never push — this skill only performs local rebase operations
- Never force — no `--force`, `--no-verify`, or other safety bypasses
- User confirmation required — always present the plan and get explicit approval before executing
- Recoverable rewrite — keep a recovery point (reflog, `ORIG_HEAD`, or a backup branch) and provide continue/abort recovery
- Clean working tree required — no uncommitted changes; preserve them, do not discard them
- Unpushed only — never rewrite commits that are already on a remote

## Edge Cases

- No upstream branch: Prompt user for commit range (recent N, from commit/tag, or all)
- No commits to squash: Inform user that all commits are independent
- Rebase conflicts: Stop and provide clear recovery instructions
- Other branches reference commits: Warn user about potential impact
