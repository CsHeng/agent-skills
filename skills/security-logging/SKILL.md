---
name: security-logging
description: "Compatibility entry for explicitly named security-logging requests; hand off security and audit evidence to logging-standards."
---

# Security Logging Compatibility

Use this skill only when the user explicitly names `security-logging` or an existing thin host entry selects this public ID. It is retained for compatibility and owns no independent logging or security-control workflow.

Route the request as follows:

- `logging-standards` owns security and audit event selection, structured fields, redaction, correlation, retention, access, alert evidence, and tamper evidence; read its `references/security-and-audit-logging.md` profile
- `security-guardrails` owns validation, injection prevention, uploads, CORS, TLS, authentication controls, and other exploit-prevention behavior

Do not emit an independent checklist or report schema. Preserve this public ID until a separately approved compatibility migration removes it.
