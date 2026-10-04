---
name: smart-commit
description: "Use when the user explicitly asks to group current working-tree diffs by business domain or purpose and create focused local commits, including staged and unstaged splits. Do not use for a generic commit request, diff inspection, status reporting, or history cleanup."
---

# Smart Commit

Group the current working-tree changes by business purpose and create focused local commits when the request combines semantic grouping with local commit creation.

## Scope

This skill covers change analysis through commit execution. It creates new local commits; an explicit request to reorganize or squash existing commits belongs to `smart-squash`.

Select this skill only when the user explicitly asks to group working-tree changes by business domain or purpose and create the resulting focused local commits. A generic request to commit, inspect diffs, summarize status, or clean up history does not match this skill. Once the request matches, default to committing eligible changes without a confirmation gate. Stop for confirmation only when Git is already tracking or staging content that appears unsafe to version.

Committing does not grant push authority. Decide whether push is in scope only from the user's own instruction; never infer it from this skill, a commit request, or a successful commit. Never use `--force`, `--no-verify`, or another safety bypass.

## Target Repository Binding

Bind the target repository before any Git inspection or write. The target repository is the Git root for the user's invocation working directory or an explicit user-supplied repository path, not the repository that stores this skill.

```bash
INVOCATION_CWD="$(pwd -P)"
TARGET_REPO="$(git -C "$INVOCATION_CWD" rev-parse --show-toplevel)"
printf 'Target repository: %s\n' "$TARGET_REPO"
```

Rules:
- Run every Git command as `git -C "$TARGET_REPO" ...`.
- Never use the plugin repository as the implicit target repository just because this skill file is loaded from there.
- The plugin repository is a valid target only when the invocation working directory resolves to it or the user explicitly selects it.
- If the resolved `TARGET_REPO` conflicts with the user's stated path, stop before running `git log`, `git diff`, `git add`, or `git commit`.

## Workflow

### Phase 0: Recent Unpushed Context (Optional)

When the branch has unpushed commits, you may check whether the most recent ones touch the same files as the current changes:

```bash
if git -C "$TARGET_REPO" rev-parse @{u} >/dev/null 2>&1; then
  git -C "$TARGET_REPO" log @{u}..HEAD --oneline -5
  git -C "$TARGET_REPO" log @{u}..HEAD --name-only --format="" -3 | sort -u
else
  git -C "$TARGET_REPO" log --oneline -5
fi
```

Overlap between recent unpushed commits and the current changes is useful context, not a gate. Report it and continue with a new focused commit unless the user explicitly asked to amend or squash.

Amend only on an explicit user request, after staging the intended files, and scope the amend to those paths too, so pre-existing staging for other work is not swept in:

```bash
git -C "$TARGET_REPO" add -- <files>
git -C "$TARGET_REPO" commit --amend --no-edit -- <files>
```

If the user asked to squash or reorganize history, invoke `smart-squash` instead of continuing here. When many unpushed commits exist, note that `smart-squash` can reorganize them later; do not block the current commit.

### Phase 1: Collect and Exclude

Gather the full picture of repository changes:

```bash
git -C "$TARGET_REPO" rev-parse --git-dir          # validate repository
git -C "$TARGET_REPO" status --short               # all changes overview
git -C "$TARGET_REPO" diff --cached --name-status  # staged changes
git -C "$TARGET_REPO" diff --name-status           # unstaged changes
git -C "$TARGET_REPO" ls-files --others --exclude-standard  # untracked files
```

If `git status --short`, staged diff, unstaged diff, and untracked-file checks are all empty, stop with a no-op result. Do not run grouping heuristics or invent a commit plan for a clean worktree.

Read file contents when needed to assess whether a file should be excluded.

#### Exclusion Criteria

Evaluate each changed/untracked file against these categories:

| Category | Examples | Action |
|----------|----------|--------|
| Secrets & credentials | API keys, tokens, passwords, .env files, private keys | Exclude, warn user; stop if tracked or staged |
| Foreign or unowned generated output | build/, dist/, *.pyc, __pycache__/, node_modules/, local caches and intermediate artifacts not intended as deliverables | Exclude; usually already matched by .gitignore |
| Intentional tracked generated deliverables | Committed generated mirrors, generated clients or docs, checked-in build outputs, and lock files that a source change in the same group requires | Include with the group whose source change produces or requires them |
| Large binaries | Images >1MB, compiled binaries, archives | Exclude, note reason |
| Temporary files | *.tmp, *.swp, *.log, .DS_Store | Exclude |
| IDE/editor config | .idea/, .vscode/settings.json (user-specific) | Exclude |
| Lock files with no source change | package-lock.json alone without package.json change | Exclude unless dependency intent is clear |

Apply judgment beyond these rules — analyze file content semantically when the filename alone is ambiguous. For example, a `.json` file could be configuration (commit) or generated output (exclude).

Treat "generated" as a question of ownership and intent, not as a blanket category. A file the repository already tracks as a deliverable — for example a generated distribution mirror, a generated client or API document, a checked-in lock file, or a build output the project commits on purpose — is committable and belongs to the group whose source change produced or updated it. Foreign or unowned build output, caches, and ignored intermediates stay excluded. When it is unclear whether a tracked generated file is an intentional deliverable, check the repository's own conventions and `.gitignore` before excluding it; do not exclude a file merely because its name or directory looks generated.

When uncertain, include the file only if it is a normal source, config, test, docs, or lockfile change. If uncertainty is about whether a tracked or staged file should be versioned at all, stop and ask for human confirmation before committing.

#### Human Confirmation Gate

Do not ask for confirmation for ordinary eligible changes. Stop and ask the user before any commit only when Git is already tracking or staging content that appears unsafe or inappropriate to version:

- A tracked or staged file appears to contain secrets, credentials, local machine state, foreign or unowned generated output, temporary logs, personal IDE settings, or other content that should not be in Git.
- The safe path would require removing a tracked file from Git or changing `.gitignore` before committing.

Untracked excluded files do not require confirmation; leave them untracked and continue with eligible tracked/staged/untracked source files.

#### Exclusion Reporting

List excluded files with the path and the reason, so the user can see what was left out and why.

### Phase 2: Semantic Grouping

Analyze remaining files and group them by business purpose:

1. Read file diffs to understand what each change does
2. Identify logical units — changes that serve the same business goal belong together
3. Respect dependencies — if schema changes enable code changes, schema comes first
4. Keep commits atomic — each commit should be independently meaningful

Grouping signals to consider:
- Files modified together for the same feature or fix
- Shared module/package boundaries
- Configuration changes that accompany code changes
- Documentation updates paired with the code they describe
- Pure refactoring separated from behavioral changes
- Test additions grouped with the code they test

Generate a commit message for each group following conventional commits:
- Imperative mood subject line, max 50 characters
- Blank line after subject
- Optional body describing what and why
- Body lines wrapped at ~72 characters

### Phase 3: Present Plan and Execute Automatically

Show the plan before executing: each commit group with its message and the files it includes, plus the excluded files and why they were excluded. A single group needs only its message and files; do not force a fixed template or decorative panel around the report.

Execute each eligible commit group sequentially without waiting for a confirmation prompt:

```bash
# For each group: register new untracked files so the pathspec can match them,
# then commit only that group's paths with a trailing pathspec.
git -C "$TARGET_REPO" add -- <file1> <file2> ...
git -C "$TARGET_REPO" commit -m "<message>" -- <file1> <file2> ...
```

The trailing `-- <paths>` is what scopes the commit: Git records the current working-tree content of exactly those paths and leaves staged changes to every other path staged and out of this commit. A bare `git commit` after a path-level `git add` records the entire index, so it would silently absorb another group's already-staged changes; never use it here. The preceding `add` exists only to make new untracked files known to Git, because a pathspec commit cannot match a file Git has never seen.

Because a pathspec commit takes the working-tree content of each named path, every unstaged change in a named path is committed too, and the recipe cannot split one path at hunk level. If two groups touch the same file, they cannot be separated here: whichever group commits first takes that file's entire current working-tree content, including the other group's changes to it, and the second group then has nothing left for that file. Do not claim per-hunk separation for this recipe. Treat a shared file as belonging to one group, or use the index-commit exception below only when the user explicitly needs a hunk-level split.

A genuine hunk-level split needs an index commit, not a pathspec commit: stage exactly that group's hunks with `git add -p`, confirm with `git status` that nothing else is staged, then run a bare `git commit` and verify the resulting tree. This is the one place a bare `git commit` is correct, and it is valid only while the index holds exactly that group; if another group already has staged changes, sequence the commits (commit the staged group first, or set it aside with `git stash --staged`) before hunk-staging. Never combine `git add -p` with a pathspec commit: a pathspec commit records the whole working-tree content of the named paths and ignores the staged hunks, silently committing the other group's unstaged changes in that file.

Between commits, verify the previous commit succeeded before proceeding. If a commit fails, stop and report the error — do not continue with remaining commits. After each commit, confirm that its recorded tree contains only that group's paths:

```bash
git -C "$TARGET_REPO" show --stat --oneline HEAD
git -C "$TARGET_REPO" show --name-only --format="" HEAD
```

If the user explicitly requested only some groups, stage and commit only the requested groups. Leave rejected or deferred groups uncommitted and visible in the working tree; do not silently absorb them into approved commits.

After all commits complete, run `git -C "$TARGET_REPO" log --oneline -<N>` to show the results.

## Constraints

- Determine whether push is in scope from the user's information instead of imposing a skill-level prohibition or default; a commit request alone does not grant push authority
- Never force — no `--force`, `--no-verify`, or other safety bypasses
- Automatic execution after matching the domain-grouping commit request — present the plan, then commit eligible groups without a separate confirmation prompt
- Human confirmation required only for tracked or staged content that appears unsafe or inappropriate to commit
- Preserve working state — only commit files included in the plan; leave other changes untouched
- Group-scoped commits — always pass the group's paths as a trailing pathspec (`git commit -m "<message>" -- <paths>`); never run a bare `git commit` that records the whole index and absorbs another group's staged changes
- Generated output is judged by ownership and intent — intentionally tracked generated deliverables are committed with the owning group, while foreign or unowned generated output is excluded
- Shared-file limitation is disclosed — a path-scoped commit commits the whole current content of each named path, so two groups touching one file cannot be separated by this recipe
- Partial user scope stays partial — rejected groups remain unstaged or restored to their previous staged state
- Respect .gitignore — never attempt to add files matched by .gitignore
- Recent-commit context is optional and never blocks a new focused commit
- Large unpushed history suggests `smart-squash` for later cleanup, but does not block default execution

## Edge Cases

- No changes detected: Inform the user and suggest checking the target path
- All files excluded: Present exclusion list, explain why nothing remains to commit
- Single logical group: Create one commit — no need to force multiple groups
- Merge conflicts present: Stop and inform the user to resolve conflicts first
- Partial staging: If some files are already staged, incorporate them into the plan, note the pre-existing staging, and let each path-scoped commit carry only its own group; staged changes in other paths stay staged. Never replace the scoped commit with a whole-index `git commit` to include them.
- Two groups touch one file: The recipe cannot split a single file across commits at hunk level. Pick one owning group, or use deliberate `git add -p` staging with an explicit tree check; state the limitation to the user instead of claiming a clean split.
