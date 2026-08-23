# Convergence And External I/O

## Convergent Configuration

- Read current state before writing. Add missing objects, update mismatched owned properties, preserve explicitly unowned properties, and remove objects only when the active repository or workflow owns their retirement.
- Match objects by stable identity and validate `find` cardinality. Positional row numbers and print order are observation conveniences, not durable selectors.
- Avoid rewriting unchanged state from a scheduler or recurring event. A no-op run should stay quiet unless the owning observability contract requires an explicit heartbeat.
- Distinguish an expected absence, a safe no-op, stale owned state, invalid input, and an unavailable dependency. The primary workflow decides whether each case fails open, fails closed, or stops for repair.
- Make partial progress visible. When several dependent mutations cannot be made atomic, order them so an interruption leaves a diagnosable state and a rerun converges safely.

## Runtime Errors And Retry

- An uncaught runtime error stops the script. Use `:onerror <name> in={...} do={...}` when the script can add context, preserve a deliberate failure policy, or continue safely. The error variable must be declared in the documented parameter order so the handler can read it.
- Use `:error` for an invalid state that must stop the current execution. Do not use it for an expected no-op or an optional dependency whose accepted policy is to preserve current state.
- Use `:retry` only for a transient operation with a bounded attempt count and delay. Do not retry syntax errors, permission errors, invalid configuration, or deterministic rejection.
- Log the final retry failure with enough operation context to diagnose it, then follow the caller-owned failure policy. Never log credentials, tokens, private keys, or secret-bearing URLs.

## Imports And Validation

- Use `import <file> verbose=yes dry-run` where supported to find import errors without applying configuration. Dry-run is a parser and import-shape oracle, not proof that later live execution has the required permissions, context variables, dependencies, or desired effect.
- Catch import errors only when the handler adds useful evidence or implements an approved safe continuation. Do not hide a failed import behind a success log.
- Validate on the target RouterOS version when a command, parameter, type, or global function may be version-specific.

## External I/O

- Treat `/tool fetch`, DNS resolution, file reads, remote command output, and API responses as untrusted inputs. Validate transport success, expected content type or shape, non-empty results when required, and bounded size before mutation.
- Prefer structured output such as `as-value` or serialized data when the producer supports it. If text parsing is unavoidable, reject malformed or ambiguous lines rather than partially accepting them.
- Separate acquisition from mutation: obtain and validate the complete candidate first, then converge owned RouterOS state. Preserve previous known-good state when the approved policy says an unavailable or invalid source must fail open.
- Bound network time, retries, and produced files. Clean up only artifacts the current script owns, and avoid persistent files when an in-memory value is sufficient.
- Keep credentials in the repository or runtime secret mechanism owned by the primary workflow. Do not embed them in a reusable generic script or diagnostic transcript.

## Logging And Evidence

- Use `debug`, `info`, `warning`, and `error` according to operational consequence rather than logging every command. Recurring unchanged runs should not flood the system log.
- Give related messages a stable, concise prefix and include the object or operation identity, outcome, and safe reason.
- A log proves that code reached the log statement. Pair it with state readback when acceptance depends on an actual RouterOS mutation.
- Preserve the distinction between source validation, import dry-run, live execution, and post-change state evidence in the final report.
