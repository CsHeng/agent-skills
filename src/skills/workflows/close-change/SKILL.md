---
name: close-change
description: "Use after a verified change to decide merge, release, cleanup, an explicitly guarded recovery action, branch closure, or final close-gate status."
---

# Close Change

Judge whether the current change can finish.

## Use This Skill When

- the change is ready for merge, release, or workspace cleanup
- the harness must make the final close decision after review and verification
- the user wants an explicit closure judgment instead of an implied finish

## Do Not Use This Skill When

- the change still lacks required review, verification, or truth-sync evidence
- the task is still in design, planning, execution, or review
- the request only asks for local git status or cleanup advice

## Bundled Runtime

Resolve the installed helper relative to this `SKILL.md` before changing into the target repository. `SKILL_ROOT` is a local assignment to the activated skill directory, not an ambient host variable:

```bash
SKILL_ROOT="/absolute/path/to/close-change"
RUNNER="$(realpath "$SKILL_ROOT/scripts/harness/close-runner.sh")"
[[ -f "$RUNNER" ]] || exit 1
```

Validate the approved evidence package and emit the deterministic decision:

```bash
bash "$RUNNER" entry-phase
bash "$RUNNER" validate "<merge|release|cleanup>" "<approved-plan>" "<execution-result-json>" "<truth-sync-artifact-if-required>"
bash "$RUNNER" decision "<merge|release|cleanup>" "<approved-plan>" "<execution-result-json>" "<truth-sync-artifact-if-required>"
```

Close mode is `merge`, `release`, or `cleanup`, with `cleanup` as the default when omitted. The mode is judgment metadata only: this skill performs none of those external actions. Closure derives review, verification, truth requirement, stable truth refs, and artifact identities from the approved plan and immutable execution result. Caller-supplied status hints are non-authoritative and mismatches fail closed. If validation fails, follow the returned `plan-change`, `implement-change`, or `sync-truth` route.

## Workflow

1. Bind the approved plan, immutable execution result, and required truth-sync artifact by exact identity.
2. Confirm the target close mode: merge, release, or cleanup.
3. Block closure when required evidence or approvals are missing.
4. Produce one terminal close decision with `terminal_state: closed` and `next_entry: null`, or one owning blocked route.

## Operating Rules

- This is the top-level closure gate.
- Final completion judgment belongs to the harness.
- Human approval remains final for close.
- A successful close is terminal and never routes back to `close-change`.
- No change closes by default just because implementation stopped.
- Evidence before closure: review status, verification status, requested write/install/deploy/commit status, and truth-sync status must each be proven from current artifacts or command output.
- Do not infer close readiness from partial checks, previous-session output, or delegated-agent summaries.
