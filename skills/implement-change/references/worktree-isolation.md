# Worktree Isolation

Read when this task needs its own Git worktree: an explicit worktree request, an applicable repository rule, a required branch state, or a concrete write or shared-resource conflict that the current checkout cannot absorb. Respect an explicit request for isolation. A standalone request to remove, prune, or repair an existing worktree reads only [Clean Up And Repair](#clean-up-and-repair). Read only the section for the current step.

A host-managed task workspace under an approved execution contract follows its own creation and cleanup procedure. For listing or comparing existing worktrees, use `git worktree list --porcelain` and read-only diffs. A branch diff compares committed trees and excludes another worktree's uncommitted state, so say which boundary a comparison covers; restoration, integration, commits, and removal require their own authority.

## Shared Boundaries

- Follow applicable repository instructions. A repository-defined worktree location takes precedence; when policy is absent, default new worktrees to `./.agents/worktrees/<branch-slug>/`. Honor a different declared location.
- Resolve the actual target once and use it throughout, binding commands with `git -C "$worktree_dir"`. A target this task resolved and verified stays the target for later steps, including a requested `smart-commit`. Keep the resolved target;  if the request and policy cannot be reconciled safely, ask about that conflict.
- Worktree creation, integration, deletion, and history changes require their applicable authority. Commits and cleanup of user worktrees require their own authority.
- Protect modified, staged, untracked, ignored, and uniquely committed work. Verify preservation before removal even for a clean worktree; transfer required uncommitted state to a new worktree.
- Never delete worktrees with `rm -rf` or use force as a default. Remove worktrees through Git after preservation and authority checks. Stop when preserving work requires a transfer method or authority that is unavailable.

## Create And Transfer Context

### Resolve The Actual Target

Use the repository's declared location. In its absence, use `./.agents/worktrees/<branch-slug>/`. Resolve the repository root, selected branch or explicit base, and actual absolute destination before executing commands. Use a filesystem-safe slug that excludes path traversal. Keep the branch identity separate from its path slug.

In the examples, `worktree_dir` is that resolved destination, `worktree_root` is its selected containing directory, and `branch` and `base` are the resolved Git refs. Resolve each as an explicit input. Quote all path/ref expansions; reject an ambiguous source or an unsafe path, including a symlink that changes the intended ownership boundary.

If the target exists, verify whether it is already the intended registered worktree. Preserve existing files, unrelated directories, and other worktrees. Resetting a reused worktree's branch or discarding its changes requires explicit authority.

### Preserve Required Context

Identify only the instructions, design/plan, source, and configuration actually needed for this task. Inspect their status, including ignored inputs when relevant:

```bash
git status --short -- "$context_file"
git status --ignored --short -- "$context_file"
```

- Confirm committed context exists at the selected starting ref.
- Modified, staged, untracked, and ignored context requires transfer to the recipient. Use an already explicitly authorized transfer that preserves the required bytes and semantics, or report the exact missing files and ask for a transfer decision. A commit is one transfer option and requires explicit authority.
- An explicitly requested isolated coding-agent handoff may use an exact bounded prompt or bridge plan payload with bytes/hash evidence and recipient no-edit constraints for design/plan context. Use this approved mechanism when it supplies the context faithfully.
- Required source and configuration must exist in the recipient filesystem. Transfer that state only with an authorized, verified method; otherwise stop. Keep credentials and irrelevant working-tree state in their existing location.
- Recheck the recipient's required context and report the files to reopen there. Distinguish an intentional untracked input from missing or altered data.

### Ignore Coverage Follows Location

For a new repo-local nested worktree, verify both Git and the search tools actually used exclude the actual selected directory. A path outside the repository must satisfy repository policy and explicit location authority; verify exclusion where applicable.

For a repo-local root, inspect Git's effective rule:

```bash
git check-ignore -v -- "$worktree_root/"
```

Verify effective exclusion through actual tool behavior. With authority to create disposable setup files, create a unique probe directory containing a harmless marker under the selected root, using a previously unused path. From the repository root, compare an unignored inventory with the normal hidden-file inventory:

```bash
rg --files --hidden --no-ignore --glob '!.git/**' .
rg --files --hidden .
```

Run the inventory from the repository root: a tool may traverse an explicitly supplied ignored path despite its ignore rules. Compare the marker's actual repository-relative path in these inventories; it must appear in the first and not the second, and `git check-ignore` must cover it. Use the corresponding real inventory if the task uses another search tool; verify each tool's actual behavior. For `rg`, exit 1 can mean an empty inventory; treat an error as inconclusive. Remove only the probe files and empty directories this setup created after recording the result.

When coverage is missing, conflicting, or cannot be verified, ask for the required ignore/setup decision before creating the worktree. Obtain authority for tracked ignore changes or a different location. Effective Git/search exclusion satisfies the coverage requirement.

#### Authorized Handoff Local Exclude

An explicitly requested isolated coding-agent handoff permits bounded local, untracked ignore setup for its temporary repo-local worktree when needed. General ignore changes and external locations require their own authority.

```bash
common_dir=$(git rev-parse --path-format=absolute --git-common-dir)
exclude_file=$(git rev-parse --path-format=absolute --git-path info/exclude)
```

Before writing:

- Reject a symlink or directory at the exclude-file path, and reject any resolved path outside the actual Git common directory, including escape through an ancestor symlink. Resolve the exclude path using Git in a linked worktree.
- Encode an exact repository-root-relative directory pattern for the selected temporary worktree root. Preserve literal spaces and escape Git-ignore metacharacters to ensure an exact match. If the exact safe pattern or its ownership is unclear, stop.
- Append that pattern at most once, preserving existing content and line boundaries. For the default root the pattern is `/.agents/worktrees/`; a custom root needs its own literal pattern. Tracked ignore-file edits require their own authority.
- Recheck Git exclusion and the actual search inventory using the disposable marker. A search rule that re-includes the marker defeats this setup; stop until effective coverage is established.

Record this as local setup metadata outside the implementation diff. If the exclude file cannot safely be changed or effective coverage still fails, report the blocker and seek a location decision.

### Create And Check

Use the command matching the requested source, after the applicable context, path, authority, and ignore checks:

```bash
# Existing local branch
git worktree add -- "$worktree_dir" "$branch"

# Existing remote-tracking ref already available locally; no fetch is implied
git worktree add --track -b "$branch" -- "$worktree_dir" "$base"

# New branch from an explicit base
git worktree add -b "$branch" -- "$worktree_dir" "$base"
```

Choose one of these alternatives. Create a new branch or fetch a remote only when that action belongs to the request. Check the result:

```bash
git -C "$worktree_dir" status --short
git worktree list --porcelain
```

Verify required context or complete its approved transfer, then report the actual `cd` destination and the context files to reopen. Report subsequent implementation and verification from their own evidence.

## Integrate

Read when the user authorizes bringing changes from a worktree or branch into a specific destination. Integration and commits each require explicit authority.

Resolve the actual destination and source, selected paths/commits, and intended change. Inspect destination staged and unstaged work before mutation:

```bash
git -C "$destination_dir" status --short
git -C "$destination_dir" diff
git -C "$destination_dir" diff --cached
```

Judge its overlap with the selected changes as for any checkout: continue when they touch different content or can safely be retained together, and resolve a specific overlap before writing. Git refuses to overwrite overlapping local changes during a merge or cherry-pick, but `restore` replaces the named paths without that check. Preserve unrelated work; use a reset, stash, or overwrite only with its owner's agreement. If the selected changes are unclear, compare first.

Choose the narrowest authorized operation. `source_ref`, `source_commit`, and `relative_file` below are resolved inputs; transfer source-worktree uncommitted changes using an authorized faithful method.

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

These are alternatives. The branch merge uses `--no-ff` to pause a fast-forward with `--no-commit`. Use the selected-file or hunk operation when that is the authorized scope. If needed changes are uncommitted at the source, require an explicit faithful transfer method.

On conflict, preserve the state and report conflicting paths. Resolve only within the authorized change; an abort, rollback, or broader merge needs an applicable recovery policy. Report integration success only after checking the complete result.

Review the resulting status and both staged/unstaged diffs, and run the destination's required verification. Commit only with explicit user authority for the selected result. A `merge --no-commit` leaves one pending merge: Git rejects a pathspec or grouped commit until it is concluded, so commit it as one unit after checking the complete result. Never abort it, convert it into a squash, or absorb unrelated staged work to make grouping possible. Remove the source worktree only after applicable authority and preservation checks.

## Clean Up And Repair

A worktree this task created is an execution resource. At closure, reclaim it through this section once its work is integrated or otherwise retained, or report it as retained with its reason. An explicit removal, metadata prune, or link repair request uses the same steps. Use actual paths from the worktree registry or an explicitly identified moved location. Follow this cleanup procedure for existing worktrees.

### Preserve Work Before Removal

Establish the exact target and applicable cleanup authority. Inspect its filesystem work and refs:

```bash
git worktree list --porcelain
git -C "$worktree_dir" status --short
git -C "$worktree_dir" status --ignored --short
git -C "$worktree_dir" diff
git -C "$worktree_dir" diff --cached
git -C "$worktree_dir" rev-parse HEAD
```

Inspect modified, staged, untracked, ignored, and required local override/context files. Keep secret contents out of the report. Verify any preservation/transfer before deletion; ignored files may be lost even when Git considers a worktree clean.

Check whether target commits remain reachable through the intended retained branch/ref, including a detached HEAD:

```bash
git -C "$worktree_dir" log --oneline "$retained_ref..HEAD"
```

Resolve `retained_ref` from the actual integration/preservation decision. A nonempty result needs evidence that the unique work is safely retained elsewhere or explicit disposition authority; check uncommitted and ignored files separately. Squash/cherry-pick integration may need content evidence because commit ancestry differs. Stop when retention or integration evidence is insufficient.

A user-approved isolated-handoff cleanup policy covers only that handoff's own resources after verified convergence establishes preservation of all unique work. Deleting unrelated worktrees or branches requires their own authority. Active work, locked worktrees, or unclear ownership require a specific decision before removal.

### Remove

After authority and preservation checks pass:

```bash
git worktree remove -- "$worktree_dir"
```

Diagnose a failure before considering a retry. A failure may reveal work or locks the preflight missed; diagnose it and obtain the needed explicit disposition. Never use `rm -rf` to delete a worktree; branch deletion requires explicit authority.

### Prune Or Repair Metadata

Prune only when stale metadata or a known accidental deletion is the actual target. Preview all affected entries:

```bash
git worktree prune --dry-run --verbose
```

Verify listed paths are truly stale, checking for inaccessible mounts, moved directories, and resources still in use. Resolve locks and obtain preservation evidence before deletion. With authority for the previewed set, execute and inspect the resulting registry:

```bash
git worktree prune --verbose
git worktree list --porcelain
```

For a moved or broken worktree link, resolve the correct repository and actual moved path, then use the targeted repair:

```bash
git worktree repair -- "$worktree_dir"
git -C "$worktree_dir" status --short
git worktree list --porcelain
```

Stop if the repository/target relationship cannot be established. Removing filesystem work requires separate authority. After any successful cleanup, report what was actually removed or repaired and which retained-work evidence was checked.
