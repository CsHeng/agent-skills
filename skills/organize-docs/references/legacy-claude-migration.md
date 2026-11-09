# Legacy CLAUDE.md Migration

Use this reference for an existing `CLAUDE.md` inside the authorized documentation scope. `AGENTS.md` is the only maintained AI-facing truth root. Migrate one way and keep `CLAUDE.md` absent as both a file and compatibility link. The default scope is the repository root; nested paths require inclusion in the requested scope.

## Path Handling

Inspect both paths themselves before mutation, leaving symlinks unresolved. Preserve existing `AGENTS.md` content; if it is a symlink or another unsafe type, resolve that boundary before writing through it.

- `CLAUDE.md` absent: maintain `AGENTS.md` only.
- `CLAUDE.md` is a symlink, including a dangling link or a link to another target: unlink only and leave the link target untouched. The link itself supplies sufficient evidence for unlinking.
- `CLAUDE.md` is a regular file and `AGENTS.md` is absent: rename `CLAUDE.md` to `AGENTS.md`, preserving its content. Then maintain valid AI guidance there and move human-facing material to `README.md` only within the authorized scope.
- Both are regular files: read both and merge only still-valid unique guidance into `AGENTS.md`, omitting duplicate or superseded rules. Preserve existing `AGENTS.md` content and still-valid `CLAUDE.md` guidance. Delete the legacy file only after every retained rule is verifiably owned by `AGENTS.md`. Resolve genuinely conflicting current rules with the appropriate authority.
- `CLAUDE.md` is a directory, device, socket, or another unsafe type: stop and request a decision before any deletion or overwrite.

## Final State

After removing a symlink, check for `AGENTS.md`. If it is still absent after cleanup, create it from current repository evidence and authorized guidance. If valid guidance cannot be established, report that remaining gap.

Verify that a valid `AGENTS.md` exists and that `CLAUDE.md` does not exist as a file, symlink, or dangling symlink. Preserve unrelated guidance and files.
