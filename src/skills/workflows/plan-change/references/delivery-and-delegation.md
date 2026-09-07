# Delivery And Delegation

Read this reference when a plan must record delivery endpoints, two-stage planning versus dispatch, cohesive worker slices, required versus missing authority, or expected same-task interaction. Ordinary local plans that do not claim those arrangements may skip it.

## Two-Stage Concretization

Planning records stable, acceptable behavior, non-goals, important reasons, external behavior, acceptance, delivery endpoints, real dependencies, state ownership, covered and missing authority, and the space an executor may decide. Do not unconditionally freeze local variable names, helper structure, every command, or every failure branch.

At planning time, write known write surfaces, dependencies, and resources directly. Mark remaining local investigation as conditional delegation instead of inventing exact files. Ordinary implementation is not blocked by missing delegation metadata.

Before actual dispatch, the parent refines the host-needed read scope, exact source write set, execution environment, and necessary inputs from the current host contract and the already approved slice. Refinement inside that slice is execution and does not reopen the whole plan. Do not finish the executor's algorithm and implementation design merely to fill filenames, and do not reopen settled questions because the executor model changed.

A task already claimed delegation-ready must actually be ready. If the plan approved exact files, interfaces, or a fixed order, do not expand them. If it approved only a module-level range, the parent may refine files and coordinate ownership inside that range. Reassigning in-range resources is usually the parent's job; only a change to a user-reserved decision rises to a human. Dispatch refinement is not scope expansion.

## Authority, Capability, And Delivery

Whether an action belongs to this task, whether matching authority exists, and whether current capability can perform it are three independent judgments. Standing deploy permission does not turn a design-only task into deployment. A plan that mentions deploy does not grant deploy permission. Credentials are not permission.

When the action is in this task and a trusted project convention or the current request already covers its goals and side effects, check remaining premises and consume that approval. Ask again only for a new goal, real side effect, or boundary conflict.

Record required authority and missing authority separately. Already covered required authority is not a `manual_checkpoint`. A capability gap blocks that step without blocking independently completable authorized work and without reporting local completion as end-to-end delivery.

When the task includes implementation and delivery, the plan states the delivery endpoint and the evidence that endpoint needs. `close-change` still owns later completion judgment. This skill does not rewrite live project permissions.

## Cohesive Slices

A worker slice may include investigation, implementation, direct tests, command feedback, and in-scope local repair. Do not split by one file per worker or by sending code and tests to different workers by default. The parent should not exhaust implementation detail and then hand off leftover typing.

Explorer work is for separately valuable or parallel facts. It is not a startup gate for every worker. The worker may investigate callers and implementation inside its slice.

Actively look for independent slices whose interfaces and inputs are stable and whose writes and shared resources do not conflict. Do not pad extra calls. A singleton offload is useful when the host and applicable call policy allow it; if the host is narrower, keep the work local, do not invent a second slice, and do not claim wall time will shrink. Shared skills cannot override a host's tighter singleton or delegation limit.

Shared interfaces, generators, lockfiles, registries, fixtures, ports, and external state need an explicit owner. Non-overlapping files do not prove independence. Only real dependencies create serial order; document chapter order does not.

For actual delegation, record repository ownership, an exclusive write set, resource locks, safe isolation, and convergence ownership with the active parent. The host owns its execution mechanisms; planning does not implement a lock or prescribe working-directory flags, snapshot paths, schedulers, or handles. Use the current checkout by default where safe and permitted; isolation needs a real policy or state reason, not delegation terminology alone.

## Parent Decisions Versus Labor

Parent-owned verification, repair, and continuation mean adjudication, authority, cross-task synthesis, and final acceptance. They do not mean every test, diagnosis, or repair command must run on the parent. Verification or repair labor may have factual dependencies but does not by itself require an intervening parent decision.

Keep a decision boundary where the parent must synthesize, authorize, coordinate across tasks, adjudicate findings, accept the result, or decide continuation. Compatible hosts may consume true dependencies that have no intermediate decision. Do not compile a plan into a static worker-to-reviewer-to-repair chain that bypasses that adjudication. Concrete DAGs, queues, and workspaces belong to the host.

## Same-Task Interaction

A cohesive task may include several parent-child exchanges. The plan may say that follow-up repair or directed rereview should prefer the same worker or reviewer while the parent keeps adjudication. Do not prefill child handles, candidate IDs, or session identifiers that do not exist yet. Host results and progress records hold those mappings during execution.

Do not add a runtime field, public continuation skill, or durable actor binding. If the current host cannot continue a child, say so at dispatch; do not write a fake ready handle into the plan.

## Readiness And Profiles

Local readiness is the ordinary check that objective, authorized writes, protected behavior, factual dependencies, delivery endpoints, and acceptance evidence are coherent. It does not require delegation profiles, parallel policy, exact dispatch paths, or a fixed review budget.

Assess delegation readiness only for slices actually delegated or claimed delegation-ready, using the existing semantic profiles and facts. Keep that vocabulary provider-neutral. Plans that do not claim delegation readiness may omit profiles. Claiming delegation-ready without those facts is fabrication, not planning.

## Examples

These examples are not template gates.

A module-level approved slice may be dispatched with host-exact files inside that module. An already approved exact write set may not gain extra paths at dispatch. A design-only task stays design-only even when standing deploy permission exists. A delivery task with already covered commit, push, and deploy permission records those endpoints and consumes the permission instead of repeating the same approval. A cohesive parser-fix slice can locate implementation, edit approved files, run existing checks, and repair failures it caused, then return a candidate and evidence without changing a public schema. Two slices that still need an undecided shared schema are not independent.
