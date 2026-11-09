# Convergence And External I/O

## Convergent Configuration

- Read current state before writing. Add missing objects, update mismatched owned properties, preserve explicitly unowned properties, and remove objects only when the active repository or workflow owns their retirement.
- Match objects by stable identity and validate `find` cardinality, following Commands And Object Selection in [language-and-values.md](language-and-values.md).
- Write state from a scheduler or recurring event only when it has changed. A no-op run should stay quiet unless the owning observability contract requires an explicit heartbeat.
- Distinguish an expected absence, a safe no-op, stale owned state, invalid input, and an unavailable dependency. The primary workflow decides whether each case fails open, fails closed, or stops for repair.
- Make partial progress visible. When several dependent mutations cannot be made atomic, order them so an interruption leaves a diagnosable state and a rerun converges safely.

## Runtime Errors And Retry

- An uncaught runtime error stops the script. Use `:onerror <name> in={...} do={...}` when the script can add context, preserve a deliberate failure policy, or continue safely. The error variable must be declared in the documented parameter order so the handler can read it.
- Use `:error` for an invalid state that must stop the current execution; an expected no-op or an optional dependency with a preserve-state policy continues normally.
- Retry only transient operations with `:retry`, a bounded attempt count and a delay.
- Log the final retry failure with enough operation context to diagnose it, then follow the caller-owned failure policy.

## Imports And Validation

- Use `import <file> verbose=yes dry-run` where supported to find import errors without applying configuration. Dry-run checks parser and import shape; later live execution needs separate evidence for permissions, context variables, dependencies, and desired effect.
- Catch import errors only when the handler adds useful evidence or implements an approved safe continuation. A failed import produces a failure log.
- Validate on the target RouterOS version when a command, parameter, type, or global function may be version-specific.

## External I/O

- Treat `/tool fetch`, DNS resolution, file reads, remote command output, and API responses as untrusted inputs. Validate transport success, expected content type or shape, non-empty results when required, and bounded size before mutation.
- Prefer structured output such as `as-value` or serialized data when the producer supports it. If text parsing is unavoidable, reject malformed or ambiguous lines in full.
- Separate acquisition from mutation: obtain and validate the complete candidate first, then converge owned RouterOS state. Preserve previous known-good state when the approved policy says an unavailable or invalid source must fail open.
- Bound network time, retries, and produced files. Clean up only artifacts the current script owns, and use an in-memory value when it is sufficient.

## Logging And Evidence

- Use `debug`, `info`, `warning`, and `error` according to operational consequence. Keep recurring unchanged runs quiet in the system log.
- Give related messages a stable, concise prefix and include the object or operation identity, outcome, and safe reason.
- A log proves that code reached the log statement. Pair it with state readback when acceptance depends on an actual RouterOS mutation.
