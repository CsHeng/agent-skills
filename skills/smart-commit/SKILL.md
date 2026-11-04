---
name: smart-commit
description: "Use when the user explicitly asks to group current working-tree diffs by business domain or purpose and create focused local commits, including staged and unstaged splits. Do not use for a generic commit request, diff inspection, status reporting, or history cleanup."
---

# Smart Commit

Group the current working-tree changes by business purpose and create focused local commits when the request combines semantic grouping with local commit creation.

## Scope

This skill covers change analysis through commit execution. It creates new local commits and commits eligible changes without a confirmation gate; reorganizing or squashing existing commits is a history rewrite that needs the user's explicit rewrite authority.

Push authority comes only from the user's own instruction, and a commit request does not grant it. Run Git with its default safety checks, hooks included.

## Target Repository Binding

Bind the target repository before any Git inspection or write. The target repository is the Git root for the user's invocation working directory, an explicit user-supplied repository path, or a checkout the current task already resolved and verified as its target, such as its own worktree. For an explicit or task-resolved path, resolve `TARGET_REPO` from that path instead of the invocation directory.

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

### Phase 1: Collect And Exclude

```bash
git -C "$TARGET_REPO" rev-parse --git-dir          # validate repository
git -C "$TARGET_REPO" status --short               # all changes overview
git -C "$TARGET_REPO" diff --cached --name-status  # staged changes
git -C "$TARGET_REPO" diff --name-status           # unstaged changes
git -C "$TARGET_REPO" ls-files --others --exclude-standard  # untracked files
```

When all four checks are empty, report a no-op and stop. Read file contents when needed to decide whether a file belongs in a commit.

Exclude files that should not be versioned: secrets and credentials, foreign or unowned generated output and caches, large binaries, temporary files, user-specific IDE config, and lock files with no source change. Include intentionally tracked generated deliverables with the group whose source change produces or requires them. Add only files that `.gitignore` does not match. Read `references/exclusion-criteria.md` when an untracked, tracked-generated or ambiguous file is present.

Commit ordinary eligible changes directly. Stop and ask the user before any commit only when Git is already tracking or staging content that appears unsafe to version: a tracked or staged file that appears to contain secrets, credentials, local machine state, foreign generated output, temporary logs or personal IDE settings, or a safe path that requires removing a tracked file from Git or changing `.gitignore`. Untracked excluded files stay untracked while the run continues.

List each excluded file with its path and reason.

### Phase 2: Semantic Grouping

Read the diffs, then group files by business purpose:

1. Changes that serve the same business goal belong together: files modified together for a feature or fix, shared module boundaries, configuration that accompanies code, documentation paired with the code it describes, tests with the code they test.
2. Order groups by dependency; for example, schema changes come before the code that uses them.
3. Keep each commit atomic and independently meaningful, with pure refactoring separate from behavioral changes.
4. A single logical group yields one commit.

Write each message in the repository's own commit-message convention, as seen in recent `git log`. Without one, use an imperative subject of about 50 characters, a blank line, and an optional body wrapped near 72 characters.

### Phase 3: Present Plan And Execute

Show each commit group with its message and files, plus the excluded files and reasons; a single group needs only its message and files. Then execute each eligible group in sequence without waiting for confirmation:

```bash
# For each group: register new untracked files so the pathspec can match them,
# then commit only that group's paths with a trailing pathspec.
git -C "$TARGET_REPO" add -- <file1> <file2> ...
git -C "$TARGET_REPO" commit -m "<message>" -- <file1> <file2> ...
```

The trailing `-- <paths>` scopes the commit: Git records the current working-tree content of exactly those paths and leaves staged changes to every other path staged. The preceding `add` only makes new untracked files known to Git. Commit each group this way; `references/split-and-merge-cases.md` covers the exceptions.

After each commit, confirm its recorded tree holds only that group's paths, and stop and report if a commit fails:

```bash
git -C "$TARGET_REPO" show --stat --oneline HEAD
git -C "$TARGET_REPO" show --name-only --format="" HEAD
```

When the user asked for only some groups, commit only those and leave the rest uncommitted and visible in the working tree. When some files are already staged, include them in the plan, note the pre-existing staging, and let each path-scoped commit carry only its own group. When merge conflicts are present, stop and ask the user to resolve them first. When all files are excluded, present the exclusion list and explain why nothing remains.

Finish with `git -C "$TARGET_REPO" log --oneline -<N>` to show the results.

## References

- `references/exclusion-criteria.md`: classifying an untracked, tracked-generated or ambiguous file.
- `references/split-and-merge-cases.md`: two groups sharing one file, a hunk-level split, partial staging, or `MERGE_HEAD` present.
- `references/amend-and-unpushed-context.md`: the user mentions amend or squash, or the branch is ahead of its upstream.
