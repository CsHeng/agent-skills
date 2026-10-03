# Shell Code Review Checklist

Apply these checks to the caller's bounded shell target. Resolve the interpreter from a trusted shebang or caller context; if neither establishes it, obtain the missing context rather than guess. Read the target without executing it.

This is a language overlay, not a separate report. The primary reviewer owns severity order, required fields and the verdict. Contribute material findings, relevant diagnostics and verification gaps without imposing a second summary or category order.

## Review Checks

- Use the resolved interpreter's syntax-only check. A Bash parse does not validate zsh or POSIX sh behavior.
- For Bash/sh, run ShellCheck with GCC-format diagnostics. Pass `-s <bash|sh>` when the interpreter came from caller context rather than a trusted shebang.
- For zsh, use `zsh -n` and the manual language audit; do not present ShellCheck as zsh coverage.
- Check the applicable requirements owned by `shell-guidelines`: entrypoint strict mode, quoting, safe variable names, input validation, interpreter portability, failure propagation and trap behavior.
- Connect findings to location, evidence, impact, scope and the smallest viable correction. Preserve original logic and avoid unrelated formatting recommendations.
- Stay read-only. The calling implementing agent decides and applies repairs; a successful tool command is not authority to mutate.

Report syntax errors, unsafe expansions, prohibited variable names and missing required entrypoint safeguards when supported by evidence. If no material findings remain, let the primary owner state that result along with any unavailable, skipped or unverified checks. Do not attach raw tool output unless the caller needs it as evidence.
