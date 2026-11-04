---
name: logging-standards
description: "Use for goal-driven application, observability, security, and audit logging: event selection, structured fields, levels, correlation, redaction, retention, access, and tamper evidence."
---

# Logging Standards

Design logs from the operational, diagnostic, security, or audit question they must answer. Choose timestamp, format, fields, backend, and retention from the consumer's decision and the repository's owned schema.

Logging records evidence; `security-guardrails` owns prevention controls and `error-patterns` owns failure classification and recovery policy.

## Design Workflow

1. State the consumer and decision: debugging, operations, alerting, incident response, access evidence, compliance, or business audit.
2. Select the smallest event set that answers that decision without duplicating metrics, traces, or domain state.
3. Define stable event names, severity semantics, required fields, correlation, cardinality limits, and ownership.
4. Classify secrets, personal data, regulated data, and attacker-controlled values before choosing redaction or omission.
5. Define routing, access, retention, deletion, integrity, and failure behavior according to repository and operational policy.
6. Verify representative events, absent sensitive fields, correlation across the required path, and the consumer's query or alert.

## Event And Level Rules

- Log state transitions, boundary outcomes, and actionable failures rather than narrating every function call.
- Use levels according to the service's operational response: reserve `ERROR` for failures an owner must investigate or a declared operation failed, and give expected client rejection the level its operational response needs.
- Keep access logs, application events, and immutable audit records distinct when their consumers, schemas, access, or retention differ.
- Record an error where useful context and response ownership meet.

## Structured Context

- Use stable machine-queryable event names and fields with consistent types; put queryable meaning in fields, with message text as supporting context.
- Include request, operation, trace, span, job, or business correlation when it is available and needed by the consumer.
- Keep high-cardinality or unbounded values out of indexed fields unless the backend and query need justify them.
- Follow repository or platform schemas such as OpenTelemetry or ECS where the repository already owns them.

## Security And Audit Profile

Read `references/security-and-audit-logging.md` when the request concerns authentication, authorization, privileged operations, sensitive-data access, redaction, retention, restricted access, suspicious activity, or tamper evidence.

## Operations

When log volume, transport, or storage bounds are in scope, read `references/operations.md`.

## Result

When this skill owns the response, lead with the logging goal and selected event contract, then report the decision-relevant event classes, fields, sensitive data handling, delivery and retention ownership, and executable evidence.
