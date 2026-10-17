# Worktree Isolation

Read when this task needs its own Git worktree: an explicit worktree request, an applicable repository rule, a required branch state, or a concrete write or shared-resource conflict that the current checkout cannot absorb. Respect an explicit request without requiring evidence that the user could not work in place. A standalone request to remove, prune, or repair an existing worktree reads only [Clean Up And Repair](#clean-up-and-repair). Read only the section for the current step.

A host-managed task workspace under an approved execution contract is not this path; it brings its own creation and cleanup, so do not duplicate them. Listing or comparing existing worktrees needs no special method: use `git worktree list --porcelain` and read-only diffs. A branch diff compares committed trees and excludes another worktree's uncommitted state, so say which boundary a comparison covers; a comparison never restores, merges, commits, or removes anything.

## Shared Boundaries

- Follow applicable repository instructions. A repository-defined worktree location takes precedence; only when no policy exists, default new worktrees to `./.agents/worktrees/<branch-slug>/`. A different declared location is not itself a reason to stop.
- Resolve the actual target once and use it throughout, binding commands with `git -C "$worktree_dir"`. A target this task resolved and verified stays the target for later steps, including a requested `smart-commit`. Never silently substitute a parent-directory, home-directory, or default path; if the request and policy cannot be reconciled safely, ask about that conflict.
- Worktree creation, integration, deletion, and history changes require their applicable authority. Implementation authority does not imply commits or cleanup of user worktrees.
- Protect modified, staged, untracked, ignored, and uniquely committed work. A clean status alone does not prove that removal is safe, and a new worktree does not inherit uncommitted state.
- Never delete worktrees with `rm -rf` or use force as a default. Stop rather than lose work, invent a transfer mechanism, or widen authority.

## Create And Transfer Context

### Resolve The Actual Target

Use the repository's declared location. Without one, use `./.agents/worktrees/<branch-slug>/`. Resolve the repository root, selected branch or explicit base, and actual absolute destination before executing commands. Use a filesystem-safe slug without path traversal. Keep the branch identity separate from its path slug.

In the examples, `worktree_dir` is that resolved destination, `worktree_root` is its selected containing directory, and `branch` and `base` are the resolved Git refs. They are inputs, not guessed fallbacks. Quote all path/ref expansions; reject an ambiguous source or an unsafe path, including a symlink that changes the intended ownership boundary.

If the target exists, verify whether it is already the intended registered worktree. Do not overwrite a file, unrelated directory, or different worktree. Reusing an existing worktree does not authorize resetting its branch or discarding its changes.

### Preserve Required Context

Identify only the instructions, design/plan, source, and configuration actually needed for this task. Inspect their status, including ignored inputs when relevant:

```bash
git status --short -- "$context_file"
git status --ignored --short -- "$context_file"
```

- Confirm committed context exists at the selected starting ref, not merely somewhere in the source branch history.
- Modified, staged, untracked, and ignored context will not automatically appear in the recipient. Use an already explicitly authorized transfer that preserves the required bytes and semantics, or report the exact missing files and ask for a transfer decision. A commit is one option, not the only option and not implied authority.
- An explicitly requested isolated coding-agent handoff may use an exact bounded prompt or bridge plan payload with bytes/hash evidence and recipient no-edit constraints for design/plan context. Do not demand a commit when this approved mechanism already supplies the context faithfully.
- A prompt alone cannot satisfy source/configuration that must exist in the recipient filesystem. Transfer that state only with an authorized, verified method; otherwise stop. Do not copy credentials or irrelevant working-tree state as a convenience.
- Recheck the recipient's required context and report the files to reopen there. Distinguish an intentional untracked input from missing or altered data.

### Ignore Coverage Follows Location

For a new repo-local nested worktree, verify both Git and the search tools actually used exclude the actual selected directory. A path outside the repository does not require a fictional repository-local ignore entry, but must still satisfy repository policy and explicit location authority.

For a repo-local root, inspect Git's effective rule:

```bash
git check-ignore -v -- "$worktree_root/"
```

Do not treat matching text in `.ignore`, `.rgignore`, or `.fdignore` as proof of effective exclusion. With authority to create disposable setup files, create a unique probe directory containing a harmless marker under the selected root, never overwriting an existing path. From the repository root, compare an unignored inventory with the normal hidden-file inventory:

```bash
rg --files --hidden --no-ignore --glob '!.git/**' .
rg --files --hidden .
```

Do not pass the ignored worktree root as an explicit search operand: a tool may traverse an explicitly supplied ignored path despite its ignore rules. Compare the marker's actual repository-relative path in these inventories; it must appear in the first and not the second, and `git check-ignore` must cover it. Use the corresponding real inventory if the task uses another search tool; one tool's ignore file does not establish another's behavior. For `rg`, exit 1 can mean no files; an error is not successful exclusion. Remove only the probe files and empty directories this setup created after recording the result.

When coverage is missing, conflicting, or cannot be verified, ask for the required ignore/setup decision before creating the worktree. Do not silently modify tracked ignore files or substitute a different location. No search-ignore file is required when effective Git/search exclusion is already proven; absence of one is not by itself a blocker.

#### Authorized Handoff Local Exclude

An explicitly requested isolated coding-agent handoff permits bounded local, untracked ignore setup for its temporary repo-local worktree when needed. This exception does not authorize general ignore changes or apply to external locations.

```bash
common_dir=$(git rev-parse --path-format=absolute --git-common-dir)
exclude_file=$(git rev-parse --path-format=absolute --git-path info/exclude)
```

Before writing:

- Reject a symlink or directory at the exclude-file path, and reject any resolved path outside the actual Git common directory, including escape through an ancestor symlink. Do not use a guessed `.git/info/exclude` path in a linked worktree.
- Encode an exact repository-root-relative directory pattern for the selected temporary worktree root. Preserve literal spaces and escape Git-ignore metacharacters rather than interpreting them as broader matches. If the exact safe pattern or its ownership is unclear, stop.
- Append that pattern at most once, preserving existing content and line boundaries. For the default root the pattern is `/.agents/worktrees/`; a custom root needs its own literal pattern, not that default. Do not edit tracked `.gitignore`, `.ignore`, `.rgignore`, or `.fdignore` merely to launch a handoff.
- Recheck Git exclusion and the actual search inventory using the disposable marker. A search rule that re-includes the marker defeats this setup; stop rather than declaring coverage from the local-exclude write alone.

Record this as local setup metadata outside the implementation diff. If the exclude file cannot safely be changed or effective coverage still fails, report the blocker; do not invent another location.

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

These are alternatives, not a sequence. Do not create a new branch or fetch a remote unless that action belongs to the request. Check the result:

```bash
git -C "$worktree_dir" status --short
git worktree list --porcelain
```

Verify required context or complete its approved transfer, then report the actual `cd` destination and the context files to reopen. An authorized setup is not proof the subsequent implementation has run or passed.

## Integrate

Read when the user authorizes bringing changes from a worktree or branch into a specific destination. Creation or comparison does not authorize integration or a commit.

Resolve the actual destination and source, selected paths/commits, and intended change. Inspect destination staged and unstaged work before mutation:

```bash
git -C "$destination_dir" status --short
git -C "$destination_dir" diff
git -C "$destination_dir" diff --cached
```

Existing destination work does not block integration by itself. Judge its overlap with the selected changes as for any checkout: continue when they touch different content or can safely be retained together, and resolve a specific overlap before writing. Git refuses to overwrite overlapping local changes during a merge or cherry-pick, but `restore` replaces the named paths without that check. Preserve unrelated work; do not use a reset, stash, or overwrite as an implicit cleanup step. If the selected changes are unclear, compare first.

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

Review the resulting status and both staged/unstaged diffs, and run the destination's required verification. Commit only with explicit user authority for the selected result. A `merge --no-commit` leaves one pending merge: Git rejects a pathspec or grouped commit until it is concluded, so commit it as one unit after checking the complete result, and never abort it, convert it into a squash, or absorb unrelated staged work to make grouping possible. Do not remove the source worktree merely because integration was requested or a command exited successfully.

## Clean Up And Repair

A worktree this task created is an execution resource. At closure, reclaim it through this section once its work is integrated or otherwise retained, or report it as retained with its reason. An explicit removal, metadata prune, or link repair request uses the same steps. Use actual paths from the worktree registry or an explicitly identified moved location, not a guessed default directory. Cleanup does not require creation ignore setup.

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

Inspect modified, staged, untracked, ignored, and required local override/context files. Do not expose secret contents in the report. Verify any preservation/transfer before deletion; ignored files may be lost even when Git considers a worktree clean.

Check whether target commits remain reachable through the intended retained branch/ref, including a detached HEAD:

```bash
git -C "$worktree_dir" log --oneline "$retained_ref..HEAD"
```

Resolve `retained_ref` from the actual integration/preservation decision, not a guessed branch name. A nonempty result needs evidence that the unique work is safely retained elsewhere or explicit disposition authority; an empty result does not cover uncommitted or ignored files. Squash/cherry-pick integration may need content evidence because commit ancestry differs. Stop when retention or integration evidence is insufficient.

A user-approved isolated-handoff cleanup policy covers only that handoff's own resources after verified convergence establishes that no unique work remains. It does not authorize deleting unrelated worktrees or branches. Active work, locked worktrees, or unclear ownership require a specific decision before removal.

### Remove

After authority and preservation checks pass:

```bash
git worktree remove -- "$worktree_dir"
```

Do not automatically retry with `--force`. A failure may reveal work or locks the preflight missed; diagnose it and obtain the needed explicit disposition. Never use `rm -rf` to delete a worktree, and do not delete its branch as an implied follow-up.

### Prune Or Repair Metadata

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
