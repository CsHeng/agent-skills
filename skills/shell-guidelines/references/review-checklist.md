# Shell Code Review Checklist

Apply these checks to the caller's bounded shell target. Resolve the interpreter from a trusted shebang or caller context; if neither establishes it, obtain the missing context. Read the target statically.

Contribute material findings, relevant diagnostics and verification gaps to the `review-change` caller.

## Review Checks

- Use the resolved interpreter's syntax-only check. A Bash parse does not validate zsh or POSIX sh behavior.
- For Bash/sh, run ShellCheck with GCC-format diagnostics. Pass `-s <bash|sh>` when the interpreter came from caller context rather than a trusted shebang.
- For zsh, use `zsh -n` and the manual language audit, and report ShellCheck as bash/sh coverage only.
- Check the applicable requirements owned by `shell-guidelines`: entrypoint strict mode, quoting, safe variable names, input validation, interpreter portability, failure propagation and trap behavior.
- Connect findings to location, evidence, impact, scope and the smallest viable correction. Preserve original logic and keep recommendations to the finding.
- Stay read-only; the caller applies repairs.

Report syntax errors, unsafe expansions, reserved variable names and missing entrypoint safeguards when supported by evidence. When no material findings remain, state that result with any unavailable, skipped or unverified checks. Attach raw tool output when the caller needs it as evidence.
