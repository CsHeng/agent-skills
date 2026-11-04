---
name: error-patterns
description: "Use for resilience and recovery decisions: failure classification, bounded retries, circuit breaking, cleanup, degraded behavior, health evidence, and resource recovery. Do not use as the lifecycle owner or for general incident triage."
---

# Resilience And Recovery

Choose failure behavior that preserves correctness, bounds amplification, and makes recovery observable for a known application or dependency boundary.

## Scope

Use this skill for:

- classifying failures by cause, permanence, caller action, and recovery path
- deciding whether retries, circuit breaking, fallback, degradation, or immediate rejection fit a boundary
- defining cleanup, cancellation, timeout, idempotency, and resource recovery
- defining health, readiness, and recovery evidence

Hand off to the matching owner:

- infrastructure incident triage before the failing state owner and data path are known: `infrastructure-triage`
- application, security, or audit log design: `logging-standards`
- input validation and exploit prevention: `security-guardrails`
- test-layer and CI design: `testing-strategy`
- rollback authorization and completion judgment: the primary workflow (`implement-change`, Recovery)

## Decision Workflow

1. Name the protected operation, caller contract, owned state, failure boundary, deadline, and irreversible effects.
2. Classify the failure using evidence rather than message text alone.
3. Decide which actor can safely recover and which state must be preserved or cleaned up.
4. Select the smallest behavior that prevents invalid state and avoids failure amplification.
5. Define observable success, exhaustion, degraded state, and recovery evidence.
6. Verify the failure and recovery paths with the smallest realistic executable oracle: exercise the transient, permanent, timeout, cancellation, partial, and cleanup paths the boundary declares, and prove retry budgets, idempotency, resource release, degraded markers, and health-state transitions where they apply.

When a reproducible code or performance failure needs a tighter evidence loop, read `references/debugging-tight-loop.md`.

## Failure Classification

Classify enough to drive caller behavior. Useful distinctions include:

- invalid input or violated precondition: reject without retry
- authentication or authorization failure: fail closed and expose only safe reason information
- conflict or stale state: return the concurrency or reconciliation action the caller can take
- transient dependency or transport failure: retry per Bounded Retry
- permanent dependency or configuration failure: stop amplification and route actionable evidence to the owner
- cancellation or timeout: preserve caller intent and report it as cancellation or timeout
- resource exhaustion or corruption risk: contain work, protect state, and make recovery ownership explicit

Use typed or structured errors when callers need stable branching. Preserve the original cause while adding boundary context, and keep secrets and internal details out of user-facing errors.

## Pattern Selection

### Bounded Retry

Retry a classified transient operation that is idempotent or protected by an idempotency mechanism, inside the remaining deadline. Bound attempts by deadline and budget, apply backoff and jitter where concurrency could synchronize, and surface final exhaustion. Retry at one owning layer per call chain.

### Fallback And Degraded Behavior

Use fallback when stale, partial, cached, or read-only behavior is valid for the caller contract. Mark degraded results and define freshness, consistency, and exit conditions. Return a required failure to the caller as a failure.

### Cleanup And Resource Recovery

Acquire and release files, locks, connections, transactions, processes, and temporary state under one visible ownership boundary. Cleanup runs on error, cancellation, and timeout while keeping the evidence and state required for safe recovery, and it is idempotent when it can be retried.

### Circuit Breaking, Load Shedding, And Health

When the boundary calls a remote dependency or declares health or readiness endpoints, read `references/patterns.md`.

## Handoff

Reuse of recovery evidence follows `references/oracle-selection.md` in `skills-routing`. Return recovery evidence and unresolved risk to the owning workflow, which decides rollback, scope, and completion.
