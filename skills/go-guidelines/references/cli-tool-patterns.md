# Go CLI Tool Patterns

## Purpose

Build maintained command-line tools with an explicit operator contract, reviewable state changes, testable core behavior, and predictable binary delivery.

## Parser Selection

Use the standard library `flag` package for a single command with a small stable option set and no meaningful command tree.

Prefer Cobra when the owned interface needs:

- multiple or nested commands
- shell completion as a first-class operator feature
- command and flag deprecation, aliases, groups, or generated documentation
- dynamic argument or flag completion

Select Kong or another parser when an approved project explicitly values its typed declaration model and does not need Cobra's broader command ecosystem. A small command uses `flag`.

For a migration from another language, follow CLI Parity in `migration.md`.

## Project Shape

A growing CLI should keep framework code at the adapter boundary:

```text
cmd/tool/main.go        process setup and exit status
internal/cli            flag or Cobra adapters and rendering
internal/app            use cases and typed requests
internal/config         explicit configuration loading
internal/client         external API adapters
internal/output         JSON, YAML, and table renderers
```

Use command constructors for command creation and registration. Inject dependencies through constructors. A Cobra `RunE` adapter should validate CLI inputs, construct a typed request, call an application use case, and return its error; the application use case owns the business workflow.

A small command keeps the same separation through functions and injected IO.

## IO And Exit Contract

- Write machine-consumable results to stdout.
- Write logs, progress, warnings, and diagnostics to stderr.
- Keep core logic independent from `os.Args`, process-global standard streams, and direct `os.Exit` calls.
- Centralize final error formatting and exit-code mapping at the process boundary.
- Offer explicit output modes such as `--output=json`, `--output=yaml`, or `--output=table` when automation consumes results.
- Keep state-changing semantics identical whether or not a TTY is present.

Use `log/slog` for structured diagnostic logging unless the existing project owns another logger. Log an error once at the boundary that owns presentation or recovery.

## Configuration And Credentials

Prefer an explicit precedence contract such as defaults, optional config file, environment, then CLI flags. Validate the final typed configuration once. Add a configuration framework only when the number of providers and merge rules justify it.

Keep secrets out of command arguments when shell history would expose them. Prefer environment variables, standard input, credential helpers, keychains, or project-owned secret providers. Redact a configuration object before rendering it.

## Completion

When the CLI requires completion, use its parser's support for the shells the project owns. Reuse the same typed data source for execution and dynamic completion to keep command behavior and suggestions aligned. Completion must be bounded, side-effect free, and fast enough for interactive use.

## State-Changing Safety

- Give destructive or high-impact commands an explicit dry-run or plan mode when the operation can be previewed.
- Make confirmation behavior explicit with flags such as `--yes`.
- Validate the complete target set before the first mutation.
- Preserve idempotency where the domain allows it.
- Define partial-failure, recovery policy, retry, and exit-code behavior before adding concurrency.
- Use `context.Context` for cancellation of network, filesystem, and subprocess work.
- When calling external programs, use `os/exec` with argument slices.

## Testing

Test core use cases directly with typed requests and injected dependencies. Test CLI adapters through explicit argument slices and injected stdin, stdout, and stderr.

Use golden tests when the text or exact bytes are part of the required output contract. For structured output consumed by value, compare parsed meaning. Test help or completion behavior at the granularity its users need. Use a subprocess or testscript-style integration test when process behavior, environment, exit status, or multi-command filesystem effects are the contract under test. Existing verification in another language may continue to exercise those boundaries.

## Build And Delivery

Follow `build-and-delivery.md` for build output, scratch, `go run` versus explicit builds, and target delivery. For a CLI, build main packages with an explicit `-o` path, inject version and build date when operators need provenance, and add GoReleaser when release archives, checksums, multiple targets, package-manager publishing, SBOMs or signing justify it.

## Checklist

- parser choice matches command complexity
- framework types stop at the CLI adapter boundary
- stdout, stderr, exit codes, and output formats are explicit
- completion is side-effect free and uses shared data sources
- state-changing commands define preview, confirmation, partial failure, and recovery behavior
- tests cover core behavior and the material process contract
- build, scratch and delivery follow `build-and-delivery.md`
