---
name: security-guardrails
description: "Use for security implementation guardrails: secrets, TLS, CORS, input validation, SQL injection, XSS, uploads, and container hardening calibrated to actual exposure and loss."
---

# Security Guardrails

## Purpose

Select controls that protect the current goal from actual exposure, exploitability, expected loss, and blast radius without adding control cost the threat does not justify. Security relevance triggers judgment; it does not make every listed control mandatory.

Do not introduce a secret service, rotation framework, scanner, container baseline, or CI pipeline merely to satisfy this skill.

## Risk Calibration

No scoring system, zero-risk proof, or fixed control catalog is required. Clearly exploitable harm is not waived by a "dev" label.

| Current execution target | Default posture | Still protect |
| --- | --- | --- |
| Authorized rebuildable development | Destructive update, rebuild, or replace; prefer fix-forward; verify the main path and related smoke | Stay within the approved goal and state; protect production, shared-host boundaries, and real secrets |
| Development with retained state | Protect the retained slice; use targeted backup or export only when that state needs it | Unique data, credentials, and explicitly retained objects; do not escalate to a full production process |
| Actual production, especially destructive change | Confirm goal, impact, authorization, and the recovery evidence this change needs | Real services, important data, access, and external behavior commitments |

Remote hosts, multi-repository work, Ansible, and deploy wording do not by themselves mean production. Prefer trusted project facts; verify only what is needed when the environment is unclear. A change that would exceed approved production goals, commitments, risk, or authority needs narrow authorization before the affected action. In-scope adaptations and already-authorized deployments do not require renewed approval.

## Credential Management

When the change handles secrets:

- Keep credentials out of source, logs, prompts, and client-visible payloads.
- Load secrets from the environment or the repository-owned secret boundary already in use.
- Restrict access to credential files when files are the owned store.
- Do not add a secret-management service, encryption framework, or rotation schedule by default.

Rotate or revoke credentials when compromise, ownership change, or an existing policy requires it. Do not impose a universal interval such as 90 days.

## Network Security

Apply network controls only to services that actually expose that boundary.

### TLS

- Use TLS when the network path needs confidentiality or integrity.
- Choose protocol versions and ciphers the clients and threat model support. Do not require TLS 1.3-only, OCSP stapling, HSTS, or preload by default.

### Security Headers

- Set headers that the application and browser threat model need, such as frame isolation, content-type sniffing protection, referrer policy, or CSP.
- Do not treat a fixed header list or `X-XSS-Protection` as a required control.

### CORS

- If the browser origin policy matters, allow specific origins, methods, and headers required by the product.
- Do not copy a generic allowlist or max-age from an example.

## Input Validation

Validate untrusted input at the owned boundary for the types, lengths, and semantic rules the operation needs. Reject invalid required input rather than guessing.

### Injection

- Use parameterized queries or the driver's bound-parameter API so values cannot become SQL syntax.
- Do not treat SQL keyword filtering, regex denylists, or string sanitization as an injection defense.
- Apply the same bound-parameter or typed-binding rule to other query languages the code constructs.

### XSS

- Encode or pass values in the encoding required by the output context (HTML text, attribute, URL, JS).
- Use the platform's HTML sanitizer only when the product must accept HTML.
- Do not treat script-tag or event-handler string detection as a substitute for contextual encoding.

### File Uploads

When the product accepts files:

- Cap size.
- Inspect content rather than trusting the client MIME type or extension alone when that distinction matters.
- Do not persist caller-supplied paths as filenames.
- Store outside the web root or serve with non-executable permissions when applicable.

## Container Security

When the change builds or hardens images:

- Drop build toolchains from runtime.
- Run as non-root when the runtime allows it.
- Limit filesystem permissions to what the process needs.

Do not require a specific base image, scanner, health-check stack, or CI security workflow.

## Authentication And Abuse Controls

- Require multi-factor authentication, account lockout, rate limiting, or step-up verification when the threat model or policy justifies the control.
- Keep thresholds, recovery, bypass, and support ownership configurable and testable rather than embedding universal values.
- Store authentication factors and recovery material through the owned secret boundary; never generate or persist them as a logging side effect.

## Security Evidence Handoff

- Define which control outcome must be observable without recording secrets or unnecessary personal data.
- Route security and audit event selection, redaction, correlation, retention, access, alert evidence, and tamper evidence to `logging-standards`.
- Keep prevention, validation, authorization enforcement, and response behavior in this skill; logs are evidence, not the security control itself.

## Checklist

Apply only the rows whose boundary is in scope for this change:

- [ ] Secrets stay out of source, logs, and unauthorized files
- [ ] Credential storage matches the owned secret boundary; no new secret service by default
- [ ] Rotation or revocation happens only when compromise, ownership, or policy requires it
- [ ] TLS and headers match actual exposure, not a universal template
- [ ] CORS is origin-specific when the browser origin policy matters
- [ ] Untrusted input is validated at the owned boundary
- [ ] Queries use bound parameters; output uses contextual encoding
- [ ] Uploads are size-limited, content-checked as needed, and stored on a safe path
- [ ] Images drop build tools and avoid unnecessary root
- [ ] Authentication and abuse controls match the threat model
- [ ] Security evidence requirements handed to `logging-standards`

## References

- [Python Security Examples](references/examples-python.md)
- [Infrastructure Security](references/infra-security.md)
