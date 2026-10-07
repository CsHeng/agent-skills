---
name: smart-squash
description: "Use to reorganize, squash, or clean up unpushed commits by business logic after read-only preflight and explicit rewrite approval."
---

# Smart Squash

Reorganize a branch's commits that are not reachable from any known remote-tracking ref by business logic. This skill only rewrites local history: it never pushes, and it never rewrites a commit reachable from a known remote-tracking ref or local tag. A local tag protects history without proving publication. A commit absent from every fetched remote ref is only unpushed on the refs that were checked, not proof that it was never published, so the rewrite still requires explicit approval.

## Scope

This skill handles batch cleanup of commits that are not reachable from any known remote-tracking ref. A request to create new commits from working-tree changes belongs to `smart-commit`. Rewriting changes every affected commit SHA, so treat it as a destructive local operation: present the proposed result and get explicit user approval before running any rebase.

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
GIT_DIR="$(git -C "$TARGET_REPO" rev-parse --absolute-git-dir)"
git -C "$TARGET_REPO" status --short               # must be clean

# Refuse when a rebase or merge is already in progress
if [ -d "$GIT_DIR/rebase-merge" ] || [ -d "$GIT_DIR/rebase-apply" ] || [ -f "$GIT_DIR/MERGE_HEAD" ]; then
  echo "ERROR: repository is in rebase or merge state"
  exit 1
fi
```

A clean working tree is required; uncommitted changes are not part of the rewrite. Ask the user to commit, stash, or otherwise preserve them before proceeding, and never discard them to clear the tree.

Fetch from the configured remotes first so remote-tracking refs are current, and record whether the fetch actually succeeded. A failed or unavailable fetch is unknown evidence, not proof that nothing is published:

```bash
REMOTE_COUNT=$(git -C "$TARGET_REPO" remote | wc -l)
if [ "${REMOTE_COUNT}" -eq 0 ]; then
  FETCH_STATUS="no-remote"
elif git -C "$TARGET_REPO" fetch --all 2>/dev/null; then
  FETCH_STATUS="ok"
else
  FETCH_STATUS="failed"
fi
```

Select the candidate range. The branch's upstream is only a range-selection hint here; its difference from HEAD is not publication evidence:

```bash
RANGE_ARGS=()
RANGE_LABEL=""

if git -C "$TARGET_REPO" rev-parse @{u} >/dev/null 2>&1; then
  UPSTREAM_NAME="$(git -C "$TARGET_REPO" rev-parse --abbrev-ref --symbolic-full-name @{u})"
  RANGE_LABEL="@{u}..HEAD"
  RANGE_ARGS=("$RANGE_LABEL")
  BASE_COMMIT="$(git -C "$TARGET_REPO" merge-base @{u} HEAD)"
else
  UPSTREAM_NAME=""
  echo "No upstream branch detected. Select commit range:"
  echo "  1. Recent N commits (default: 10)"
  echo "  2. From specific commit/tag"
  echo "  3. All commits in current branch"
  read -r choice
  case $choice in
    1) read -r -p "Number of commits: " N; N="${N:-10}"; RANGE_LABEL="HEAD~$N..HEAD"; RANGE_ARGS=("$RANGE_LABEL"); BASE_COMMIT="HEAD~$N" ;;
    2) read -r -p "From commit/tag: " FROM; RANGE_LABEL="$FROM..HEAD"; RANGE_ARGS=("$RANGE_LABEL"); BASE_COMMIT="$FROM" ;;
    3) RANGE_LABEL="--root"; RANGE_ARGS=("--root" "HEAD"); BASE_COMMIT="$(git -C "$TARGET_REPO" rev-list --max-parents=0 HEAD)" ;;
  esac
fi
```

Classify every candidate commit by reachability, per commit, from known remote-tracking refs and local tags. This is a containment/intersection test, not the `HEAD ^<upstream>` set difference: a commit can be absent from the upstream branch yet still reachable from a second pushed branch or a protected local tag. Report full reference names to distinguish those cases; a local tag alone does not establish whether it was published:

```bash
REMOTE_REF_COUNT=$(git -C "$TARGET_REPO" for-each-ref --format='%(refname)' refs/remotes/ | wc -l)

CANDIDATES=$(git -C "$TARGET_REPO" rev-list "${RANGE_ARGS[@]}" --reverse) || {
  echo "ERROR: candidate range ${RANGE_LABEL} could not be enumerated"
  exit 1
}

for commit in $CANDIDATES; do
  protected_refs=$(git -C "$TARGET_REPO" for-each-ref --contains "$commit" --format='%(refname)' refs/remotes/ refs/tags/)
  if [ -n "$protected_refs" ]; then
    echo "PROTECTED-REF $commit refs=$protected_refs"
  elif [ "${FETCH_STATUS}" = "ok" ] && [ "${REMOTE_REF_COUNT}" -gt 0 ]; then
    echo "UNPUSHED-ON-KNOWN-REFS $commit"
  else
    echo "UNKNOWN $commit"
  fi
done
```

Also report local branches that contain candidate commits, since rewriting will strand or require rebasing them:

```bash
for commit in $CANDIDATES; do
  git -C "$TARGET_REPO" for-each-ref --contains "$commit" --format='%(refname:short)' refs/heads/
done | sort -u
```

Report the actual preflight findings and their consequences: clean or dirty tree, rebase or merge in progress, the fetch status, the configured upstream (or that it is absent), the selected range and its commit count, each candidate's reachability class, and any other branch that contains a candidate. Interpretation rules:

- `PROTECTED-REF` means the candidate is reachable from a known remote-tracking ref or local tag. Refuse to rewrite the range while those refs contain a candidate. A remote-tracking ref records known remote reachability; a local tag protects the candidate but does not prove publication. Report fetch failures alongside this protection because remote evidence may be stale.
- `UNPUSHED-ON-KNOWN-REFS` means the fetch succeeded, remote-tracking refs were available to check, and no checked remote-tracking ref or local tag contains the commit. Report it with that qualification; it is not proof that the commit was never published, because a remote ref may not have been fetched, may have been deleted, or may live on a fork.
- `UNKNOWN` means no protected ref was found and publication evidence is incomplete: the fetch failed, no remote is configured, or there are no remote-tracking refs to test against. Report an explicit unknown and never describe the candidates as unpushed.
- No upstream configured is itself an explicit unknown for the branch baseline. Report `upstream: none configured`; do not treat the absence of an upstream as evidence that candidates are unpushed.

State facts and risks directly; do not wrap them in a fixed severity panel or checkmark template. A clean reachability result is not rewrite authorization; the plan in Phase 3 still requires the user's separate, explicit approval.

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

If the selected range is empty, report zero candidate commits and stop without proposing a rewrite. For a nonempty range, analyze the commits before deciding whether any groups can merge.

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

If no mergeable groups are found and no other reorganization is needed, report that result for the analyzed range and stop without a rebase.

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

REBASE_EXIT_CODE=0
if [ "$RANGE_LABEL" = "--root" ]; then
  GIT_SEQUENCE_EDITOR="sh -c 'cp \"$PLAN_FILE\" \"\$1\"' --" \
    git -C "$TARGET_REPO" rebase -i --root || REBASE_EXIT_CODE=$?
else
  GIT_SEQUENCE_EDITOR="sh -c 'cp \"$PLAN_FILE\" \"\$1\"' --" \
    git -C "$TARGET_REPO" rebase -i "$BASE_COMMIT" || REBASE_EXIT_CODE=$?
fi

# Handle conflicts
if [ "$REBASE_EXIT_CODE" -ne 0 ]; then
  echo "ERROR: rebase stopped. Resolve conflicts, then:"
  echo "  git -C \"$TARGET_REPO\" rebase --continue  # after resolving conflicts"
  echo "  git -C \"$TARGET_REPO\" rebase --abort     # abandon the whole operation"
  exit "$REBASE_EXIT_CODE"
fi
```

After completion, compare the resulting groups and full commit messages with the approved plan. Show the resulting history and the before/after commit counts:

```bash
if [ "$RANGE_LABEL" = "--root" ]; then
  FINAL_COUNT=$(git -C "$TARGET_REPO" rev-list --count HEAD)
else
  FINAL_COUNT=$(git -C "$TARGET_REPO" rev-list --count "$BASE_COMMIT"..HEAD)
fi
git -C "$TARGET_REPO" log --oneline --graph -n $((FINAL_COUNT + 5))

echo "Original commits: $ORIGINAL_COUNT"
echo "Reorganized commits: $FINAL_COUNT"
```

Report the recovery point and the outcome. Remove a task-created backup branch only after the result is accepted and cleanup is authorized; do not delete or expire reflog entries or unrelated references as routine cleanup.

## Constraints

- Never push — this skill only performs local rebase operations
- Never force — no `--force`, `--no-verify`, or other safety bypasses
- Explicit rewrite approval required — always present the plan and get the user's separate approval before executing; a clean preflight result never authorizes the rewrite
- Recoverable rewrite — keep a recovery point (reflog, `ORIG_HEAD`, or a backup branch) and provide continue/abort recovery
- Clean working tree required — no uncommitted changes; preserve them, do not discard them
- Reachability, not difference — classify each candidate with `for-each-ref --contains` against known remote-tracking refs and local tags; never infer that a commit is unpushed from `HEAD ^<upstream>` or `@{u}..HEAD`, which are set differences
- Never rewrite a protected candidate — refuse when any candidate is reachable from a known remote-tracking ref or local tag; a local tag alone is not publication evidence
- Unknown stays unknown — a failed fetch or absent remote refs leaves publication unknown for candidates without protected refs; a missing upstream leaves the branch baseline unknown. Report the gap and ask instead of asserting the commits are unpushed
- No universal publication claim — absence from every fetched remote ref does not prove a commit was never published; state which refs were checked

## Edge Cases

- No upstream branch: Treat the branch publication baseline as unknown, prompt the user for a commit range (recent N, from commit/tag, or all), and never assume the candidates are unpushed
- Fetch fails or no remote: Preserve any known ref protection, report publication as unknown for candidates without protected refs, and ask how to establish what is published
- Candidate reachable from another remote-tracking ref or local tag: Report the protected reference and refuse, even when the upstream difference looks clean; do not call a local tag proof of publication
- Empty candidate range: Report zero candidates; no grouping or rewrite is needed
- Nonempty range with no mergeable groups: Report the grouping result for that range; skip the rebase when no other reorganization is needed
- Rebase conflicts: Stop and provide clear recovery instructions
- Other branches reference commits: Warn user about potential impact
