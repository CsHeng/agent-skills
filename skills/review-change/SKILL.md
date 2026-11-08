---
name: review-change
description: "Review one bounded design, plan, or implementation target; return evidence-backed candidate findings and one verdict without mutating the target or synthesizing missing lifecycle work. An explicitly requested interactive grill or stress test of a design or plan belongs to design-change."
---

# Review Change

Review exactly one supplied target and leave repair judgment with the calling agent. `development-standards` applies from the start: a review judges whether proposed mechanisms and verification are necessary for the user's outcome as well as whether required behavior is missing.

## Use This Skill When

- `design-change`, `plan-change`, or `implement-change` requests a bounded review of a current artifact or a targeted rereview of a repair
- the user directly asks to review a specific design, plan, diff, or implementation slice

A standalone review needs only a bounded target and a review question. An explicit request to grill, stress-test, or challenge a design interactively uses `references/stress-test-mode.md` in `design-change`.

## When Review Runs

Callers invoke review when it is explicitly requested, an applicable repository rule requires it, or concrete boundary or behavioral uncertainty justifies it: security, retained state, concurrency, protocol compatibility, or cross-owner contract changes. A low-risk, contract-conforming edit verified by deterministic owner checks completes on the caller's self-check. Review directly when the target is small or delegation is unavailable; one independent reviewer suits a non-trivial target with material uncertainty.

Use the target-specific evaluator when it is discoverable (`review-design`, `review-plan`, `review-implementation`); otherwise perform the same bounded review directly. An evaluator receives only the bounded brief, stays read-only, returns candidate findings, and neither delegates, invokes another lifecycle phase, repairs files, nor widens scope. A worker's self-check is not independent review.

One invocation evaluates its supplied target once; the caller decides whether evidence or a rule needs another. A narrow deterministic repair whose direct check passes closes on the caller's verification; a justified rereview focuses on the repair, affected boundaries, and unresolved findings, prefers the original reviewer when the host can continue its context and target (supplying the previous result, the exact delta, parent dispositions, and the remaining question), and takes a fresh reviewer for a changed material boundary, deficient prior coverage, or an explicit independent-review request. Prior adjudications stand while their evidence applies; an old pass does not cover a new regression. The reviewer stays separate from the worker across rounds.

## Bounded Brief

- the user's required outcome in one sentence, then the target class and objective
- goals, non-goals, acceptance criteria, and any authorized best-effort discretion
- exact artifact, diff, or changed files and current candidate identity
- declared verification and evidence for that candidate, including gaps or invalidated results
- allowed supporting files, each with a reason and a genuinely accessible source or bounded excerpt

A path outside the evaluator's readable snapshot and a bare commit identifier are not supplied context: provide the exact diff and necessary blobs or confirm a bounded history-reading capability, supply review rules through accessible files, and deliver the changed delta explicitly on follow-up. When a capability is unavailable, the parent supplies the material or reviews directly, naming the actual reviewer and input. Return `needs-decision` when the target is missing or cannot be bounded.

## Candidate Findings

Ask first whether each proposed mechanism or acceptance condition is necessary for the outcome: a new test harness, simulation script, compatibility adapter, duplicate cross-layer assertion, hash, receipt, or gate that duplicates an existing owner check, freezes incidental literals, or rehearses a cutover already covered by authorized real-path verification gets a finding to remove or collapse it, not findings that polish its internals. Then check for omitted main goals, required oracles, and real boundaries: explicit user requirements, real consumer or protocol contracts, cryptographic behavior, artifact integrity across a trust boundary, security and retained-state protections, and authorized real-path verification bind. A secondary target raised into a gate, or an exhaustive secondary-feature catalog where discretion exists, is a defect; so is dropping a required result under best-effort language or deleting its oracle.

Each material candidate states its evidence and location, its causal connection to the target, the violated requirement or correctness risk, its consequence and confidence, and the smallest in-scope repair when one exists. For a diff target, a blocking finding is caused or newly activated by that diff; for a whole-artifact target, defects anywhere in the artifact are in scope. Unrelated, future-phase, speculative, and low-confidence observations stay out of blocking findings; a critical out-of-scope security or data-loss risk is reported for a decision without expanding repair authority. Execution success is not a review pass.

## Verdict

Return findings first, ordered by severity, then one verdict and the verification gaps:

- `pass`: no material causally bound finding remains, including when authorized secondary tradeoffs are disclosed and the main goals hold
- `needs-fixes`: one or more supported findings have an in-scope repair
- `needs-decision`: evidence or authority outside the review boundary is required, architecture intent must change, or scope or acceptance conditions are insufficient; say which
- `split-scope`: the supplied target cannot remain one bounded review surface

The caller adjudicates each candidate as accepted, rejected, deferred, or escalated with a reason, and the owning workflow judges deliverable readiness; a `pass` does not itself make a deliverable ready.
