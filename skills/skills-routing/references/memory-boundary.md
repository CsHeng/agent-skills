# Memory Boundary

Agent memory is a recall layer, not the primary source of truth. Keep session scope bound to the named repository, product surface, or workflow, and treat explicit read-only wording literally. Prefer current local evidence and live runtime checks over memory when verification is cheap, and verify current external facts before relying on versions, project support, APIs, protocols, pricing, laws, or ecosystem state. Generated memories, summaries, and logs supply recall to verify, not another source of requirements.

## Use Memory When

- the task depends on prior user preferences, recurring failures, or known local topology
- the target repository, runtime, module, or workflow appears in memory
- a current question asks about previous decisions or consistency with prior work

## Verify Memory When

- the fact can drift and is cheap to verify
- the answer depends on current install state, live runtime, tool versions, service behavior, or external project support
- a memory note conflicts with repository truth or current command output
- a compact or session summary claims executor, permission, running, or failed state

## Recovery Evidence

Capability, guidance, and task-delegation state are different facts: runtime restores tools and installed guidance; task decisions come from repository truth, current host results, still-valid approvals, actual changes, unadjudicated reports, and continuable executors. The persistent recovery preference (reconcile history into one current account, treat a superseded restriction as historical, ask only about a genuinely unrecoverable approval boundary) lives in the user's harness-global instructions; this reference supplies the portable method.

After compaction or resume, reconcile those facts before choosing continue or create. For a delegated executor, locate the existing handle and its native session through the host; a changed process ID does not end the task, and an absent handle in a summary does not mean the task is gone. A summary never grants permission, confirms a check passed, or replaces an unverified candidate's evidence. Raw historical sessions are not a way around host workspace, permission, or capability checks; when the host cannot resume a session, report the gap and choose a bounded rebuild or local continue.

## Compact Payload Priority

When compacting or handing off, preserve in priority order:

1. Current objective and why it matters, delivery endpoint, and the effective task-scoped approval baseline with its sources and owning project records, keeping maintenance and simplicity intent intact.
2. Architecture decisions and durable contracts.
3. Modified files and key changes.
4. Current verification status, separate from permission status.
5. Open TODOs, recovery notes, unadjudicated reports, still-valid executors, and next gates.
6. Tool outputs only as pass/fail or the smallest required evidence.

## Promotion Rule

Promote repeated or durable behavior into repository docs, repository-local skills, or generic skills; after promotion, treat the memory entry as a cleanup candidate.
