# Legacy CLAUDE.md Migration

Use this reference for an existing `CLAUDE.md` inside the authorized documentation scope. `AGENTS.md` is the only maintained AI-facing truth root. Migrate one way; never recreate `CLAUDE.md` as a file or compatibility link. The default scope is the repository root; nested paths require inclusion in the requested scope.

## Path Handling

Inspect both paths without following symlinks before mutation. Do not overwrite an existing `AGENTS.md`; if it is a symlink or another unsafe type, resolve that boundary before writing through it.

- `CLAUDE.md` absent: maintain `AGENTS.md` only.
- `CLAUDE.md` is a symlink, including a dangling link or a link to another target: unlink only; never edit, write through, or replace the link target. Reading or migrating the target is not a prerequisite for deleting the link.
- `CLAUDE.md` is a regular file and `AGENTS.md` is absent: rename `CLAUDE.md` to `AGENTS.md`, preserving its content. Then maintain valid AI guidance there and move human-facing material to `README.md` only within the authorized scope.
- Both are regular files: read both and merge only still-valid unique guidance into `AGENTS.md`, omitting duplicate or superseded rules. Never overwrite existing `AGENTS.md` content or discard still-valid `CLAUDE.md` guidance. Delete the legacy file only after every retained rule is verifiably owned by `AGENTS.md`. Resolve genuinely conflicting current rules instead of guessing.
- `CLAUDE.md` is a directory, device, socket, or another unsafe type: stop and request a decision instead of deleting or overwriting it.

## Final State

Removing a symlink does not create `AGENTS.md`. If it is still absent after cleanup, create it from current repository evidence and authorized guidance, not by blindly copying an arbitrary link target. If valid guidance cannot be established, report that remaining gap instead of inventing instructions.

Verify that a valid `AGENTS.md` exists and that `CLAUDE.md` does not exist as a file, symlink, or dangling symlink. Preserve unrelated guidance and files. Never remove a regular legacy file before its retained guidance is safely owned elsewhere; never recreate the compatibility link.
