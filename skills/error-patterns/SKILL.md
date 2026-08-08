---
name: error-patterns
description: "Use for resilience and recovery decisions: failure classification, bounded retries, circuit breaking, cleanup, degraded behavior, health evidence, and resource recovery. Do not use as the lifecycle owner or for general incident triage."
---

# Resilience And Recovery

Choose failure behavior that preserves correctness, bounds amplification, and makes recovery observable. Apply this skill to a known application or dependency boundary; let the primary workflow own planning, mutation, review, and close.

## Scope

Use this skill for:

- classifying failures by cause, permanence, caller action, and recovery path
- deciding whether retries, circuit breaking, fallback, degradation, or fail-fast behavior fit a boundary
- defining cleanup, cancellation, timeout, idempotency, and resource recovery
- defining health, readiness, and recovery evidence

Do not use it to own:

- infrastructure incident triage before the failing state owner and data path are known; use `infrastructure-triage`
- application, security, or audit log design; use `logging-standards`
- input validation and exploit prevention; use `security-guardrails`
- test-layer and CI design; use `testing-strategy`
- lifecycle recovery routing, rollback authorization, or completion judgment

## Decision Workflow

1. Name the protected operation, caller contract, owned state, failure boundary, deadline, and irreversible effects.
2. Classify the failure using evidence rather than message text alone.
3. Decide which actor can safely recover and which state must be preserved or cleaned up.
4. Select the smallest behavior that prevents invalid state and avoids failure amplification.
5. Define observable success, exhaustion, degraded state, and recovery evidence.
6. Verify the failure and recovery paths with the smallest realistic executable oracle.

When a reproducible code or performance failure needs a tighter evidence loop, read `references/debugging-tight-loop.md`. That reference helps establish the oracle; it does not make this skill the incident or lifecycle owner.

## Failure Classification

Classify enough to drive caller behavior. Useful distinctions include:

- invalid input or violated precondition: reject without retry
- authentication or authorization failure: fail closed and expose only safe reason information
- conflict or stale state: return the concurrency or reconciliation action the caller can take
- transient dependency or transport failure: retry only inside the remaining deadline and idempotency boundary
- permanent dependency or configuration failure: stop amplification and route actionable evidence to the owner
- cancellation or timeout: preserve caller intent and do not disguise it as a generic internal error
- resource exhaustion or corruption risk: contain work, protect state, and make recovery ownership explicit

Use typed or structured errors when callers need stable branching. Preserve the original cause while adding boundary context; do not leak secrets or internal details into user-facing errors.

## Pattern Selection

### Bounded Retry

Retry only a classified transient operation that is idempotent or protected by an idempotency mechanism. Bound attempts by deadline and budget, apply backoff and jitter where concurrency could synchronize, and surface final exhaustion. Do not layer independent retries at every hop.

### Circuit Breaking And Load Shedding

Use a circuit breaker when repeated dependency calls demonstrably amplify latency or resource exhaustion and the caller has meaningful open, half-open, and recovery behavior. Prefer concurrency limits, queues, or load shedding when the actual constraint is local capacity rather than dependency health.

### Fallback And Degraded Behavior

Use fallback only when stale, partial, cached, or read-only behavior is valid for the caller contract. Mark degraded results and define freshness, consistency, and exit conditions. Never turn a required failure into silent success.

### Cleanup And Resource Recovery

Acquire and release files, locks, connections, transactions, processes, and temporary state under one visible ownership boundary. Cleanup must run on error, cancellation, and timeout without deleting evidence or state required for safe recovery. Make cleanup idempotent when it can be retried.

### Health And Readiness Evidence

Health checks should answer an actor's decision. Liveness proves the process can make progress; readiness proves it can safely receive the declared work; dependency health and degraded-state evidence should be separate when their recovery actions differ. Avoid checks that merely test a port while hiding an unusable dependency or exhausted resource.

## Verification And Handoff

- Exercise representative transient, permanent, timeout, cancellation, partial, and cleanup paths that the boundary declares.
- Prove retry budgets, idempotency, resource release, degraded markers, and health-state transitions where they apply.
- Route concrete logging fields to `logging-standards` and test placement to `testing-strategy`.
- Return recovery evidence and unresolved risk to the owning workflow. Do not independently choose rollback, widen the plan, or declare the change complete.
