---
name: logging-standards
description: "Use for goal-driven application, observability, security, and audit logging: event selection, structured fields, levels, correlation, redaction, retention, access, and tamper evidence."
---

# Logging Standards

Design logs from the operational, diagnostic, security, or audit question they must answer. Do not impose one timestamp, line format, field set, backend, or retention period on every service.

## Ownership Boundary

- This skill owns application, access, observability, security, and audit log event design.
- `security-guardrails` owns prevention and enforcement controls such as input validation, injection prevention, CORS, TLS, uploads, authorization, and container hardening.
- `error-patterns` owns failure classification and recovery behavior. Logging records the evidence but does not replace the recovery policy.
- A lifecycle workflow remains the primary owner when logging is one part of a larger implementation or review.

## Design Workflow

1. State the consumer and decision: debugging, operations, alerting, incident response, access evidence, compliance, or business audit.
2. Select the smallest event set that answers that decision without duplicating metrics, traces, or domain state.
3. Define stable event names, severity semantics, required fields, correlation, cardinality limits, and ownership.
4. Classify secrets, personal data, regulated data, and attacker-controlled values before choosing redaction or omission.
5. Define routing, access, retention, deletion, integrity, and failure behavior according to repository and operational policy.
6. Verify representative events, absent sensitive fields, correlation across the required path, and the consumer's query or alert.

## Event And Level Rules

- Log state transitions, boundary outcomes, and actionable failures rather than narrating every function call.
- Use levels according to the service's operational response. `ERROR` should normally mean an owner must investigate or a declared operation failed; expected client rejection is not automatically an error.
- Keep access logs, application events, and immutable audit records distinct when their consumers, schemas, access, or retention differ.
- Avoid duplicate emission at every layer. Record an error where useful context and response ownership meet.

## Structured Context

- Prefer stable machine-queryable event names and fields with consistent types.
- Include request, operation, trace, span, job, or business correlation only when it is available and needed by the consumer.
- Keep high-cardinality or unbounded values out of indexed fields unless the backend and query need justify them.
- Treat message text as supporting context, not the only schema.
- Follow repository or platform schemas such as OpenTelemetry or ECS when they are already owned; do not add a standard merely for uniformity.

## Security And Audit Profile

Read `references/security-and-audit-logging.md` when the request concerns authentication, authorization, privileged operations, sensitive-data access, redaction, retention, restricted access, suspicious activity, or tamper evidence.

## Operations

- Bound local storage and define rotation or backpressure before logs can exhaust a runtime.
- Make transport failure behavior explicit: drop, buffer, retry, block, or fail closed only according to the event's requirement.
- Assign aggregation, archive, retention, and deletion to named infrastructure or compliance owners.
- Test queries and alerts with representative events. A log that cannot be retrieved or correlated does not satisfy its goal.

## Result

When this skill owns the response, lead with the logging goal and selected event contract. Report only the decision-relevant event classes, fields, sensitive data handling, delivery and retention ownership, and executable evidence. Do not emit a second report when another lifecycle or domain skill owns the task.
