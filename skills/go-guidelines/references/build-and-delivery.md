# Go Build And Delivery

Read this when producing, running, testing or delivering a Go artifact: choosing between `go run` and an explicit build, placing build output and scratch, running coverage or fuzz, or shipping a binary to a target host.

## Output And Scratch

- Apply the environment-scope and temporary-storage rules in `development-standards`; this reference adds the Go mappings.
- `GOCACHE` and `GOMODCACHE` are shareable build and module caches that may be user-global. Keep them shared unless an actual isolation requirement calls for a task-local cache. A module's declared dependencies and per-run build or test scratch stay with the owning module or run.
- Pass an explicit `-o` when building, and write to the repository's declared scratch or output directory (an ignored in-repo `tmp/`, `dist/` or `bin/`, or a directory outside the tree), otherwise to a unique task directory under `TMPDIR`, or `$HOME/tmp` for agent-owned ad hoc work when `TMPDIR` is unset. This keeps the implicit `./<name>` binary out of the checkout.
- Go places intermediate build files independently of final output placement. Honor an explicit `GOTMPDIR`; otherwise Go uses the platform temporary directory, which on Unix follows `TMPDIR`. Make sure the effective scratch root exists and is disk-backed for large builds. Keep `GOCACHE` and `GOMODCACHE` at their own locations.
- Test binaries, `-coverprofile` output, fuzz corpora and explicit build outputs can appear as untracked or ignored files even though the caches live outside the tree. After verification, inspect ignored and untracked files as well as tracked diffs, remove per-run scratch after its use ends, and retain declared delivery artifacts and bounded caches under their ownership contract. Another owner's data and cache stay in place.
- Reuse the repository's build/run entrypoint or a small shared launcher for genuinely shared setup and cleanup; retain command-specific cancellation or recovery behavior where needed.

## `go run` And Explicit Builds

- `go run` is a development convenience for a host that owns the source and toolchain, including a remote development host. Consumer delivery uses an explicit artifact contract.
- Use an explicit build when the consumer needs an artifact, a reusable executable, or startup or process behavior that `go run` does not provide. The Go driver adds overhead and may not preserve the child program's exact exit status or signal behavior, so verify those requirements before changing the invocation mechanism.
- Use `-trimpath` when reproducible path-independent build metadata matters. Inject version, commit and build date through project-owned build flags when operators need provenance.
- Add GoReleaser when release archives, checksums, multiple `GOOS`/`GOARCH` targets, package-manager publishing, SBOMs or signing justify its configuration surface.

## Delivery To A Target

- Build on the controller or CI host for the target `GOOS`/`GOARCH` and ship the binary or image; managed and production targets run that artifact. The owning boundary for this rule is `references/language-selection.md` in `skills-routing`.
- When an existing Shell entrypoint uses the binary, integrate both into the same declared delivery and update operation, including required assets, and verify the entrypoint in the delivered layout.
