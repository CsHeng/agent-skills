# Memory Boundary

Agent memory is a recall layer, not the primary source of truth. Keep session scope bound to the named repository, product surface, or workflow, and treat explicit read-only wording literally. Prefer current local evidence and live runtime checks over stale memory when verification is cheap, and verify current external facts before relying on versions, project support, APIs, protocols, pricing, laws, or ecosystem state.

## Evidence And Intent

Use current code, scripts, and configuration to establish implementation, and relevant runtime observations to establish what actually runs. Tests provide bounded behavioral evidence. Documents, diagrams, and skills express intended behavior and guidance; they do not override contradictory implementation or runtime facts. Generated memories, summaries, and logs supply recall to verify, not another source of requirements.

## Use Memory When

- The task depends on prior user preferences, recurring failures, or known local topology.
- The target repo, runtime, module, or workflow appears in memory.
- A current question asks about previous decisions or consistency with prior work.

## Verify Memory When

- The fact can drift and is cheap to verify.
- The answer depends on current install state, live runtime, tool versions, service behavior, or external project support.
- A memory note conflicts with repository truth or current command output.
- A compact or session summary claims executor, permission, running, or failed state.

## Recovery Evidence

Capability, guidance, and task-delegation state are different facts. Runtime restores tools and installed guidance; recover task decisions from repository truth, current host results, still-valid approvals, actual changes, unadjudicated reports, and continuable executors.

After compaction or resume, reconcile those actual changes, the current goal and approval baseline, unadjudicated reports, and any still-valid executor before choosing continue or create.

For authority, reconcile the current project plan or approval summary with trusted task-specific user approvals, including later additions that supersede earlier restrictions. Keep the effective target, side effects, exclusions, and remaining decisions distinct from uncompleted checks. An outdated project paragraph cannot override a later explicit approval. A summary cannot grant new permission or restore a superseded gate; if the approval basis cannot be established, ask only about that missing boundary.

Do not treat a compact or memory summary of running, failed, or missing handles as current executor state. Do not overwrite source from a summary, do not accept an unverified candidate, and do not redispatch or recreate work only because a handle is absent. Recovery does not restart skill selection; same-task follow-up is not a completed phase boundary and does not require a full skills reload.

Do not read arbitrary historical JSONL, transcripts, or raw sessions to bypass host workspace, permission, or capability checks. If the host cannot resume a session, report that gap and choose a bounded rebuild or local continue; do not claim continuation is already supported, and do not disguise a new session as the original executor.

## Compact Payload Priority

Persistent compaction and recovery preferences belong in harness-global instructions, not solely in a task-loaded skill; this reference supplies the portable method, while project-owned design, plan, or approval summaries record task-specific decisions. Neither those records nor a compact summary grants approval.

When compacting or handing off long conversations, preserve in priority order:

1. Current objective and why it matters, delivery endpoint, and effective task-scoped approval baseline: approved actions and targets, remaining exclusions and owner decisions, and the source of each approval with the owning project-record references. Preserve the maintenance and simplicity intent; do not promote accumulated methods, task lists, or evidence bookkeeping into new requirements.
2. Architecture decisions and durable contracts.
3. Modified files and key changes.
4. Current verification status, separate from permission status.
5. Open TODOs, recovery notes, unadjudicated reports, still-valid executors, and next gates.
6. Tool outputs only as pass/fail or the smallest required evidence.

Reconcile history and split-turn context into one current account. Mark restrictions superseded by matching later explicit approval as historical, not active blockers; do not concatenate old pending gates with their approved replacements. Unfinished implementation or verification is not missing authority, and an approval does not establish that a check passed.

## Promotion Rule

Promote repeated or durable behavior into repo docs, repo-local skills, or generic skills. After promotion, treat the memory entry as a cleanup candidate rather than a parallel rule source.
