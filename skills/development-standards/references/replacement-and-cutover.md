# Replacement And Cutover

Read this when a change replaces a running implementation, version, configuration, or service, or when a plan or review must decide whether a proving environment, dual-running period, observation window, or rollback path belongs in the work. This is the single owner of that doctrine; lifecycle, review, security, and infrastructure Skills point here.

## Default Route

Classify the target with the environment rule in `development-standards`, then take the matching branch.

- Authorized rebuildable state (development hosts, disposable containers, regenerable artifacts): apply the change, verify on the real path, and repair forward. A separate proving environment, rehearsal, or rollback plan is not part of this branch.
- A slice holding retained state, credentials, or a shared host: take a targeted export or backup of that slice before the mutating step, then follow the rebuildable branch for everything else. The protection covers the slice, not the whole process.
- Production destructive change: before the operation, hold a named goal and impact, matching authorization, and a tested rollback (trigger, target, and verification exercised) alongside the recovery evidence this specific change requires. Executing that rollback is a separate decision, taken when an explicit observed hazard makes it safer than forward repair; `runtime-diagnosis` lists the hazard classes.

Design the target state rather than a coexistence period. Dual-running, compatibility layers, and observation windows are added only for a concrete consumer, retained-state, availability, or safety reason named in the design or request.

## Protected Before The Operation

Before the step that changes the live target, preserve the ability to repair it: credentials and secrets, irreplaceable data, unrelated services on the same host, explicit continuity commitments, and the access path used to repair. Explicit pre-cutover requirements from the user or an applicable runbook also stay ahead of the switch.

## After The Operation

Switching is not acceptance. Verify the required outcome on the real path, place observation, accounting, or failure tests where they inform the outcome (including after the switch), and finish fix-forward repair before claiming delivery. Reuse of earlier recovery evidence follows `references/oracle-selection.md` in `skills-routing`.
