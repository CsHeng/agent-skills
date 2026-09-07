# Creation And Context

Read only for creating a worktree or preparing an explicitly authorized isolated handoff. Do not apply these prerequisites to List or Compare.

## Resolve The Actual Target

Use the repository's declared location. Without one, use `./.agents/worktrees/<branch-slug>/`. Resolve the repository root, selected branch or explicit base, and actual absolute destination before executing commands. Use a filesystem-safe slug without path traversal. Keep the branch identity separate from its path slug.

In the examples, `worktree_dir` is that resolved destination, `worktree_root` is its selected containing directory, and `branch` and `base` are the resolved Git refs. They are inputs, not guessed fallbacks. Quote all path/ref expansions; reject an ambiguous source or an unsafe path, including a symlink that changes the intended ownership boundary.

If the target exists, verify whether it is already the intended registered worktree. Do not overwrite a file, unrelated directory, or different worktree. Reusing an existing worktree does not authorize resetting its branch or discarding its changes.

## Preserve Required Context

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

## Ignore Coverage Follows Location

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

### Authorized Handoff Local Exclude

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

## Create And Check

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
