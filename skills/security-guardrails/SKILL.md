---
name: security-guardrails
description: "Use for security implementation guardrails: secrets, TLS, CORS, input validation, SQL injection, XSS, uploads, and container hardening calibrated to actual exposure and loss."
---

# Security Guardrails

## Purpose

Select controls that protect the current goal from actual exposure, exploitability, expected loss, and blast radius at a control cost the threat justifies. Add a control only when it closes a named exposure at the current boundary.

## Risk Calibration

Apply the environment classification in `development-standards` and the recovery calibration in `runtime-diagnosis`. Clearly exploitable harm is not waived by a "dev" label; protect real secrets, shared-host boundaries, and production in every environment.

## Credential Management

When the change handles secrets:

- Keep credentials out of source, logs, prompts, and client-visible payloads.
- Load secrets from the environment or the repository-owned secret boundary already in use.
- Restrict access to credential files when files are the owned store.
- Rotate or revoke credentials on compromise, ownership change, or existing policy.

## Network, Headers, And Containers

When the service exposes TLS, CORS, or response headers, or the change builds or hardens images, read `references/infra-security.md`. Derive TLS versions, header set, and CORS allowlist from the clients and browser origin policy the service actually has.

## Input Validation

Validate untrusted input at the owned boundary for the types, lengths, and semantic rules the operation needs. Reject invalid required input rather than guessing.

### Injection

- Use parameterized queries or the driver's bound-parameter API so values cannot become SQL syntax.
- Apply the same bound-parameter or typed-binding rule to other query languages the code constructs.

### XSS

- Encode or pass values in the encoding required by the output context (HTML text, attribute, URL, JS).
- Use the platform's HTML sanitizer when the product must accept HTML.

### File Uploads

When the product accepts files, read `references/file-uploads.md`.

## Authentication And Abuse Controls

- Require multi-factor authentication, account lockout, rate limiting, or step-up verification when the threat model or policy justifies the control.
- Keep thresholds, recovery, bypass, and support ownership configurable and testable rather than embedding universal values.
- Store authentication factors and recovery material through the owned secret boundary; keep them out of logging side effects.

## Security Evidence Handoff

Define which control outcome must be observable without recording secrets or unnecessary personal data, and route security and audit event selection, redaction, correlation, retention, access, alert evidence, and tamper evidence to `logging-standards`. Prevention, validation, authorization enforcement, and response behavior stay here; logs are evidence of the control.

## References

- [Python Security Examples](references/examples-python.md)
- [Infrastructure Security](references/infra-security.md)
- [File Uploads](references/file-uploads.md)
