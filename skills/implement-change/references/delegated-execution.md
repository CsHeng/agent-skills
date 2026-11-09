# Delegated Execution

Use this method for a bounded worker assignment, its follow-up, or an invocation failure. The parent owns the objective, decomposition, dispatch and continuation decisions, cross-task coordination, authority, finding adjudication, and final acceptance. A worker can perform investigation, implementation, tests, diagnosis, and authorized local repair; the parent judges verification evidence from the commands performed.

## Choose A Cohesive Slice

Delegate a slice that has its own write surface or a broad read-only question and is large enough to carry its own coordination: each handle costs the parent several turns to dispatch, read and integrate, and its report stays in the parent context afterwards, while worktree preparation is cheap. A slice the main agent could finish in a handful of turns belongs in the main agent or inside a larger slice. Use the available host delegation capability. Choose cohesive slices with independently useful results and local feedback, keeping real coupling together and preserving necessary parent joins. Keep tightly coupled changes—especially edits sharing a single generator, derived catalog, or compact total diff across one or more authorized repositories—in the active main agent, or inside a single multi-repository worker grant when context isolation is specifically useful, with code and its tests kept together by default. Choose the worker unit from the actual cohesive slice.

Judge that choice from the plan and context already collected. Use the available plan and context to decide whether and how to delegate. When known facts are insufficient, the main performs the next useful implementation action and delegates independent work as it becomes ready. Use a separate explorer for a substantive independent question.

Prefer parallel ready slices with stable shared contracts, nonconflicting writes and resources, and clear convergence ownership. Shared generators, registries, lockfiles, fixtures, ports, and external state need owners; judge independence across these shared resources as well as filenames and repository roots. A useful singleton is valid where the host and call policy permit it. Retain trivial or tightly coupled work locally. Delivery goals determine the appropriate worker count and coordination.

## Async And Explicit Joins

A submission receipt records submission; completion, integration, and acceptance each require their own evidence. An inspect result is an immediate snapshot; rely on a supported execution-completion notification for completion. Read and judge a completed subset, then dispatch new nonconflicting work, before other tasks in the same submission finish. When no independent runnable work remains, end the current model turn with the task unfinished and rely on the supported execution-completion notification. Keep the task unfinished and active while awaiting completion. Use an explicit wait or join only at a useful dependency, with a caller-selected duration; choose each wait based on a useful dependency. Foreground-only hosts cannot provide parent/child overlap; use them only when their actual benefits justify the overhead.

Parallel writing tasks retain separate results in managed workspaces. Same-task follow-up reuses context and work. Read-only review needs a stable candidate; coordinate concurrent writers to preserve that reviewed version.

Hold a finished candidate until the batch's review point unless a ready task, a shared generator or registry, or your next decision depends on the integrated tree; those dependencies are the ones declared at create time. Review the held set once when review is warranted, repair, then apply. Applying each candidate as it finishes forces its siblings to refresh before they can continue.

## Dispatch Brief

Carry enough information for an executor without the original conversation to understand:

- the slice's result and relationship to the parent objective, including which outcomes are main goals or necessary conditions and which are authorized best-effort secondary work;
- protected behavior, acceptance, non-goals, important rationale, authorized tradeoff boundaries, relevant environment facts, and local choices left to the executor;
- accessible evidence and input version, repository ownership, initial write regions, explicit forbidden boundaries, and actual host capability constraints;
- actual tools, execution environment, shared-resource and isolation boundaries, useful local checks, any explicitly assigned broader check, and when to return a decision or blocker.

The brief carries authority and discretion; production permission, scope, and best-effort status come from the approved brief and trusted authority. Glue around specified technology and in-brief secondary adaptation stay with the executor. The child generates execution products within its slice.

Keep simple briefs short. If documents are uncommitted, ignored, in another checkout, or absent from a snapshot, supply bounded excerpts or a genuinely readable source; provide accessible content and confirm which parent instructions the host supplies. Skill directories and their reference bodies are discoverable resources; supply needed parent decisions in the brief. When a needed method or decision will not reach the child that way, including a temporary skill or a choice that exists only in the parent conversation, put that skill, reference, or decision in the brief. Use observable host context and provide bounded relevant material.

Use known initial write regions inside the approved scope and leave implementation discovery to the executor. Respect explicitly fixed file, interface, and ordering restrictions; distinguish them from an observed planning inventory. Coordinate scope-contained ownership adjustments through the supported parent/host path without renewed user approval when the original authority covers them. User authority sets the scope for any newly discovered in-goal file; a child must respect explicit forbidden boundaries and real host capabilities. Exact host write capabilities remain binding for that dispatch even when the broader plan permits refinement. Actual host capability and permission govern execution; Skills supply methods within those boundaries.

## Local Feedback And Return

The worker implements its slice with necessary local feedback: relevant unit tests, compilation, or a narrow reproduction, followed by in-scope repair. Batch related edits before checks that cannot usefully guide intermediate work. Keep ordinary red-green iterations local; use [Focused Implementation Repair](repair-loop.md) for the bounded repair.

The parent coordinates integration, cutover, and broader verification for the combined change; workers execute those only when assigned. A source-only worker returns usable capability and explicit gaps; the parent owns deployment qualification. Retain product guards only for actual input, authority, or safety boundaries; report live authority and evidence gaps to the parent. The parent judges whether each gap blocks cutover or can be checked afterward, reusing applicable local evidence.

Return the candidate, checks actually performed and their outcomes, known problems, unverified parts, and authorized secondary tradeoffs. A host snapshot or diff identity identifies a candidate; commits require their own authority. The parent decides final acceptance from the integrated result and evidence.

Evidence must cover the final exported candidate. Verify the exported result using checks whose inputs match that candidate. Later changes can invalidate only part of the evidence; reuse the applicable part and verify affected combinations and missing acceptance. The parent decides evidence sufficiency.

## Same-Task Continuation

The parent determines when the logical assignment ends. Prefer the original worker for an accepted in-scope defect or answered clarification when its context, workspace, permissions, and route remain valid and the host supports continuation. Reuse that task's handle and native JSONL. After reload, locate them through the host before creating another task; identify the assignment by its host handle and context. After a blocking question is answered, resume the original authorized assignment. Classify a coordination question by its actual authority and recovery needs. Worker self-repair inside a call and parent-child exchanges across calls are different capabilities.

Before continuing, use current host evidence to reconcile the previous candidate/export, actual baseline and drift, pending reports, permissions, and available executor. Coordinate other integrated changes before allowing writes. When a baseline changes or files overlap, read the changes, retain compatible work, merge or rebase through an authorized supported path, and verify the affected integration. If candidate apply refuses drift, prepare a reconciled candidate within existing authority. Ask only when the actual conflict cannot be resolved safely inside existing authority. Read the current baseline before writing and preserve its applicable changes. After compaction, recover existing results and executors before creating replacements; locate handles through the host.

An incremental brief normally supplies the existing task/result reference, current candidate or baseline, adjudicated findings or answered question, concrete error evidence, allowed repair, and expected return. Keep original non-goals, acceptance, main goals, and authorized discretion intact. Keep scope changes explicit and authorized; the parent controls authority and reopens settled findings on new evidence.

Use a new executor when the task is unrelated, state cannot safely continue, capability or route is unavailable, or persistent misunderstanding leaves no useful progress. Identify continuation, migration, branching, and reconstruction honestly; identify a bounded summary rebuild as reconstruction. Preserve a user-selected route and use a suitable executor for each repository and role. A task may span repositories when its access grants cover them. Reviewer continuity is evaluated through `review-change`; independent review requires an independent reviewer.

Use only the host's supported continuation and state checks. Use the host's actual running-child steering capability. If continuation is unavailable, state the limitation and choose an authorized local or reconstructed path; report the runtime requirement as undelivered.

## Invocation Recovery

Classify the observed failure before changing execution ownership:

| Evidence | Response inside existing authority |
| --- | --- |
| Invalid parameters or admission rejection before child startup | Correct the supported call and resubmit when useful; choose implementation ownership based on the actual failure. |
| Child safety refusal or tool misuse | Inspect the actual permission boundary; correct safe misuse within the guard and existing authority. |
| Environment, capability, or route failure | Resolve the concrete prerequisite when authorized; otherwise report the affected step and preserve explicit route requirements. |
| Incomplete final report | Reconcile real output and state; obtain missing evidence through an available supported path. |
| Source export conflict | Pause affected writes, reconcile current ownership and changes, and invalidate evidence whose coverage changed with the candidate. |
| Candidate violates acceptance | Parent adjudicates the defect; continue a bounded worker repair or choose justified local takeover without weakening the oracle. |

Local takeover or re-slicing is legitimate when the task does not fit, capability is unavailable, coordination costs outweigh value, diagnosis has no useful next step, or an explicit budget is reached. Record the actual reason and remaining work. Report fallback and actual results, preserve acceptance, and base parent acceptance or takeover on explicit decisions and evidence.
