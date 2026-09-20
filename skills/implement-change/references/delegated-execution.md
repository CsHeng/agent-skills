# Delegated Execution

Use this method for a bounded worker assignment, its follow-up, or an invocation failure. The parent owns the objective, decomposition, dispatch and continuation decisions, cross-task coordination, authority, finding adjudication, and final acceptance. A worker can perform investigation, implementation, tests, diagnosis, and authorized local repair; responsibility for verification is not a requirement that the parent run every command.

## Choose A Cohesive Slice

Prefer substantive work with its own acceptable result and local feedback loop, not one worker per file or separate code and test workers by default. Judge dispatch using the plan and context already collected. Do not search, probe, invoke another model, or estimate duration solely to decide whether to open a worker. When evidence is insufficient, the main performs the next useful implementation action; worker discovery stays with the worker. A separate explorer is useful for a substantive independent question, not a mandatory dispatch-assessment predecessor.

Prefer parallel ready slices with stable shared contracts, nonconflicting writes and resources, and clear convergence ownership. Shared generators, registries, lockfiles, fixtures, ports, and external state need owners; disjoint filenames alone do not establish independence. A useful singleton is valid where the host and call policy permit it. Retain trivial or tightly coupled work locally; call count and parent token share are not delivery goals.

## Async And Explicit Joins

A submission receipt is not child completion, source integration, or acceptance. Use the host's notification and state facilities; do not add sleep/status polling as a substitute for event delivery. Continue useful independent work when available, or wait normally when all ready work is already assigned. Await a result at its real dependency or integration join, not reflexively after submission. Foreground-only hosts cannot provide parent/child overlap; use them only when their actual benefits justify the overhead.

Parallel writing tasks retain separate results in managed workspaces. Same-task follow-up reuses context and work rather than allocating a new workspace per role invocation. Read-only review needs a stable candidate; a concurrent writer must not silently change that reviewed version.

## Dispatch Brief

Carry enough information for an executor without the original conversation to understand:

- the slice's result and relationship to the parent objective, including which outcomes are main goals or necessary conditions and which are authorized best-effort secondary work;
- protected behavior, acceptance, non-goals, important rationale, authorized tradeoff boundaries, relevant environment facts, and local choices left to the executor;
- accessible evidence and input version, repository ownership, initial write regions, explicit forbidden boundaries, and actual host capability constraints;
- actual tools, execution environment, shared-resource and isolation boundaries, required checks, and when to return a decision or blocker.

The brief carries authority and discretion; a child does not self-grant production permission, extra scope, or after-the-fact best-effort status. Glue around specified technology and in-brief secondary adaptation stay with the executor. Do not ask the child, or the user through the child, for execution products the slice can generate.

Keep simple briefs short. If documents are uncommitted, ignored, in another checkout, or absent from a snapshot, supply bounded excerpts or a genuinely readable source; naming a path does not transmit its contents. Do not assume either complete or absent inheritance of parent instructions. Use observable host context, not wholesale conversation or Skill copying.

Use known initial write regions inside the approved scope; do not pre-solve implementation or investigate missing filenames merely to qualify dispatch. Respect explicitly fixed file, interface, and ordering restrictions; distinguish them from an observed planning inventory or baseline SHA. Coordinate scope-contained ownership adjustments through the supported parent/host path without renewed user approval when the original authority covers them. Discovering another in-goal file does not itself expand user authority; a child must still respect explicit forbidden boundaries and real host capabilities. Exact host write capabilities remain binding for that dispatch even when the broader plan permits refinement. Actual host capability and permission govern execution: a Skill does not grant shell, private reviewer commands, isolation, or a persistent session.

## Local Feedback And Return

Within the brief, a worker can read, reproduce, edit, run permitted checks, interpret failures, and repair until its completion criteria hold. A red test or compiler error does not require returning every iteration or starting a full design/plan lifecycle. Apply [Focused Implementation Repair](repair-loop.md) to in-scope defects; independent review is not replaced by worker self-checking.

Return the actual changes and candidate identity, executed checks with real outcomes, unrun or invalidated checks, necessary evidence locations, remaining questions or blockers, and any authorized secondary tradeoff with its reason and impact. A host snapshot or diff identity is sufficient; do not commit merely to name a candidate. Keep process success, report completeness, source export, local test success, and parent acceptance distinct.

Evidence must cover the final exported candidate. A passing check that depended on temporary source edits omitted from export does not validate the exported result. Later changes can invalidate only part of the evidence; reuse the applicable part and verify affected combinations and missing acceptance. The parent decides sufficiency, not the host status or the worker's confidence.

## Same-Task Continuation

A returned report or exited process does not by itself end a logical assignment. Prefer the original worker for an accepted in-scope defect or answered clarification when its context, workspace, permissions, and route remain valid and the host supports continuation. After a blocking question is answered, resume the original authorized assignment rather than closing on confirmation. A question needing parent coordination is not necessarily human approval or permanent failure. Worker self-repair inside a call and parent-child exchanges across calls are different capabilities.

Before continuing, use current host evidence to reconcile the previous candidate/export, actual baseline and drift, pending reports, permissions, and available executor. Coordinate other integrated changes before allowing writes. A changed baseline or overlapping file is not by itself a changed goal or missing permission: read the changes, retain compatible work, merge or rebase through an authorized supported path, and verify the affected integration. If candidate apply refuses drift, prepare a reconciled candidate rather than forcing the stale apply or treating the refusal as a demand for user approval. Ask only when the actual conflict cannot be resolved safely inside existing authority. Never let remembered file contents overwrite the current baseline. After compaction, recover existing results and executors before creating replacements; a missing handle in a summary does not prove the executor is absent.

An incremental brief normally supplies the existing task/result reference, current candidate or baseline, adjudicated findings or answered question, concrete error evidence, allowed repair, and expected return. Keep original non-goals, acceptance, main goals, and authorized discretion intact. Do not rewrite the initial prompt to change scope silently, let the child self-authorize, or reopen settled findings without new evidence.

Use a new executor when the task is unrelated, state cannot safely continue, capability or route is unavailable, or persistent misunderstanding leaves no useful progress. Identify continuation, migration, branching, and reconstruction honestly; a bounded summary rebuild is not complete native-session continuity. Do not silently change a user-selected route or reuse an executor across repositories or roles. Reviewer continuity is evaluated through `review-change`, never by relabeling the worker as an independent reviewer.

Use only the host's supported continuation and state checks, not arbitrary transcripts or raw session commands to bypass them. Foreground round-to-round exchange does not imply steering while a child is running. If continuation is unavailable, state the limitation and choose an authorized local or reconstructed path; do not claim the runtime requirement is delivered.

## Invocation Recovery

Classify the observed failure before changing execution ownership:

| Evidence | Response inside existing authority |
| --- | --- |
| Invalid parameters or admission rejection before child startup | Correct the supported call and resubmit when useful; do not automatically take over the whole implementation. |
| Child safety refusal or tool misuse | Inspect the actual permission boundary; correct safe misuse only, never evade the guard or expand authority through retries. |
| Environment, capability, or route failure | Resolve the concrete prerequisite when authorized; otherwise report the affected step and preserve explicit route requirements. |
| Incomplete final report | Reconcile real output and state; obtain missing evidence through an available supported path, not a guessed pass or duplicate execution. |
| Source export conflict | Pause affected writes, reconcile current ownership and changes, and invalidate evidence that no longer covers the candidate. |
| Candidate violates acceptance | Parent adjudicates the defect; continue a bounded worker repair or choose justified local takeover without weakening the oracle. |

Local takeover or re-slicing is legitimate when the task does not fit, capability is unavailable, coordination costs outweigh value, diagnosis has no useful next step, or an explicit budget is reached. Record the actual reason and remaining work. Do not retry to manufacture a green tool status, hide fallback, delete acceptance, or infer parent acceptance or takeover merely from neighboring messages.
