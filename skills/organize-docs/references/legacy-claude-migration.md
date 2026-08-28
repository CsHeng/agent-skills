# Legacy CLAUDE.md Migration

Read this reference only when the repository root already had a `CLAUDE.md` path at the start of the requested documentation work. `AGENTS.md` is the maintained AI-facing truth root; `CLAUDE.md` remains only as compatibility for consumers that still look for that filename.

## Initial State

Record the initial path type before mutation:

- absent: return to the main workflow without creating `CLAUDE.md`
- regular file: migrate still-valid unique guidance before replacing the file
- symlink to `AGENTS.md`: preserve it without rewriting either path solely for compatibility
- broken symlink or symlink to another target: inspect the target and preserve any unique guidance before replacement
- directory, device, or another unsafe type: stop instead of overwriting it

## Migration

1. Read the existing `CLAUDE.md` content without editing through a symlink.
2. Classify its guidance as still valid and unique, already present in `AGENTS.md`, stale, or human-facing material that belongs in `README.md`.
3. If `AGENTS.md` is absent, create it from the still-valid AI-facing guidance. If both files exist, merge only unique durable guidance into `AGENTS.md`; do not preserve contradictory or duplicate instructions.
4. Verify that `AGENTS.md` owns every retained AI-facing rule before replacing the legacy path.
5. Replace the existing root path with the relative symlink `CLAUDE.md -> AGENTS.md`. Do not use an absolute target.
6. Verify that `CLAUDE.md` is a symlink, its textual target is `AGENTS.md`, and resolving it reaches the repository root's maintained `AGENTS.md`.

Never remove or replace a regular file until its retained guidance is verifiably owned elsewhere. If the content or target cannot be read safely, stop and request a decision instead of guessing.
