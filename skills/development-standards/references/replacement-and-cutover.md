# Replacement And Cutover

Read this when a change replaces a running implementation, version, configuration, or service, or when a plan or review must decide whether a proving environment, dual-running period, observation window, or rollback path belongs in the work. This is the single owner of that doctrine; lifecycle, review, security, and infrastructure Skills point here.

## Default Route

Classify the operation with the protection rule in `development-standards`, then take the matching branch.

- Apply, check on the real path, repair forward: the default for every replacement, including on hosts that serve real users. A new image, route, selector, kernel or service configuration is switched, its required outcome is checked on the real path, and defects are repaired in place. Rolling the change back is the same kind of change in the other direction, taken when observation after the switch shows a hazard that rollback clears sooner than forward repair; `runtime-diagnosis` lists those hazard classes.
- Protect the slice first: when the step can lose retained data or credentials, take a targeted export or backup of that slice before the mutating step, exercise the transition on realistic non-empty old state when a format or schema changes, and check the restore path when the change touches it. Then continue with the default branch for everything else; the protection covers the affected slice.

Design the target state. Dual-running, compatibility layers, and observation windows are added only for a concrete consumer, retained-state, availability, or safety reason named in the design or request.

## Protected Before The Operation

Before the step that changes the live target, preserve the ability to repair it: credentials and secrets, irreplaceable data, unrelated services on the same host, explicit continuity commitments, and the access path used to repair. Explicit pre-cutover requirements from the user or an applicable runbook also stay ahead of the switch.

## After The Operation

After switching, verify the required outcome on the real path, place observation, accounting, or failure tests where they inform the outcome (including after the switch), and finish fix-forward repair before claiming delivery. Reuse of earlier recovery evidence follows `references/oracle-selection.md` in `skills-routing`.
