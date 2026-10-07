# Candidate Evidence And Ablation

Evidence should answer the decision, not become another product to maintain. For a candidate, establish what changes, what required outcome remains, who actually depends on it, and why the result costs less to own. Add compatibility, retained-data, security, or recovery investigation only when that boundary is affected.

## Read The Requirement Before Preserving The Mechanism

Trace relevant entry points, callers, configuration, and persisted formats. Repository history can explain a mechanism; it does not make it necessary forever. A test that exercises only a helper introduced for the same guard proves reachability, not user value. A document describing the guard proves recorded intent, not an external obligation.

Separate a concept from its representations. Removing a duplicate document or generated form need not remove the underlying behavior; one live consumer does not justify every parallel representation. Where a real required integration is unwired, missing callers are not a reason to delete the requirement. Resolve that specific uncertainty rather than requiring proof of all conceivable consumers.

## Use A Bounded Ablation When Value Is Unclear

1. State the question: what user outcome or failure prevention is this mechanism supposed to contribute? Choose representative inputs and relevant adverse cases from actual use.
2. Observe the current behavior, then temporarily remove or bypass one coherent responsibility in a local, reversible candidate. Reuse existing tests or simple commands; do not build a general experiment harness merely for the cut. A read-only audit may use an authorized scratch copy, but does not mutate the source repository or live state.
3. Compare the required outcomes and relevant failures. When performance or resources motivate the change, compare the same workload under comparable conditions. Also inspect what implementation, tests, fixtures, dependencies, and documentation the cut removes or adds.
4. Interpret the difference. If a required result regresses, retain the responsibility or find a smaller implementation. If only an incidental representation or a test of the removed mechanism changes, reassess that assertion against actual requirements. Passing an unaffected suite alone cannot show the removed code was unnecessary.
5. Keep the smaller implementation when authorized and supported, or report the candidate with its remaining uncertainty. Remove temporary switches, duplicate implementations, and experiment scaffolding when they no longer serve the task.

Ablation supports a bounded causal conclusion under the exercised conditions. It does not prove that rare failure modes, external clients, or trust boundaries are absent. Inspect those boundaries when relevant; do not run destructive or production experiments under ordinary local-edit authority. No experiment is required for an obvious duplicated paragraph or straightforward redundant branch.

## Choose Evidence That Matches The Surface

- Code: required behavior, real consumer compatibility, state transitions, and meaningful failure handling.
- Tests: the defect or invariant detected; retain effective coverage while removing duplicate fixtures, implementation snapshots, or assertions without a requirement.
- Documentation and diagrams: whether the reader can understand current behavior, intent, and decisions with less duplication. Review meaning and update links as ordinary maintenance; do not create tests, digests, or goldens to freeze prose or diagrams.

Report a supported cut, a reason to keep the responsibility, or the specific missing fact. A short before/after explanation is normally enough; candidate classes, fixed scoring, exhaustive forms, and immutable evidence packages are not required.
