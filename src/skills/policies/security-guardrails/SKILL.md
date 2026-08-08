---
name: security-guardrails
description: "Use for security implementation guardrails: secrets, TLS, CORS, input validation, SQL injection, XSS, uploads, and container hardening."
---
## Purpose

Provide comprehensive security implementation standards covering credential management, secret rotation, input validation, and other guardrails that can be reused across services.

## IO Semantics

Input: Service configurations, deployment environments, and code paths that handle credentials or security-sensitive operations.

Output: Concrete policies, code templates, and operational procedures for secure storage, rotation, and validation of secrets.

Side Effects: Applying these guardrails may require changes to deployment pipelines, secret management systems, and runtime configuration.

## Credential Management

Implement secure credential handling:
- Use environment variables for all configuration secrets
- Apply encrypted storage for sensitive environment variables
- Implement proper access controls for credential files
- Use secret management services for production environments

## Secret Rotation

Automate secret lifecycle management:
- Rotate credentials on schedule (default: 90 days)
- Generate cryptographically secure passwords
- Update database users atomically
- Store encrypted credentials with GPG

## Network Security

### TLS Configuration
- Use TLS 1.3 only in production
- Enable OCSP stapling
- Enforce HSTS with preload
- Configure forward secrecy cipher suites

### Security Headers
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Content-Security-Policy: configured per application

### CORS Configuration
- Whitelist specific origins
- Limit allowed methods and headers
- Set appropriate max-age for preflight caching

## Input Validation

### SQL Injection Prevention
- Detect SQL keywords in user input
- Use parameterized queries exclusively
- Sanitize all inputs at boundaries

### XSS Prevention
- Detect script tags and event handlers
- Sanitize HTML with bleach or equivalent
- Encode output appropriately

### File Upload Security
- Validate MIME types with magic bytes
- Enforce file size limits
- Generate secure filenames with hashes
- Set restrictive file permissions

## Container Security

### Hardening Practices
- Use multi-stage builds
- Create non-root users
- Remove build toolchain from runtime
- Set restrictive file permissions
- Configure health checks

### Image Security
- Use minimal base images (Alpine)
- Scan for vulnerabilities with Trivy
- Remove package caches
- Pin dependency versions

## Authentication And Abuse Controls

- Require multi-factor authentication, account lockout, rate limiting, or step-up verification when the threat model or policy justifies the control.
- Keep thresholds, recovery, bypass, and support ownership configurable and testable rather than embedding universal values.
- Store authentication factors and recovery material through the owned secret boundary; never generate or persist them as a logging side effect.

## Security Evidence Handoff

- Define which control outcome must be observable without recording secrets or unnecessary personal data.
- Route security and audit event selection, redaction, correlation, retention, access, alert evidence, and tamper evidence to `logging-standards`.
- Keep prevention, validation, authorization enforcement, and response behavior in this skill; logs are evidence, not the security control itself.

## Checklist

- [ ] Credentials stored in environment variables
- [ ] Secret rotation automated
- [ ] TLS 1.3 configured
- [ ] Security headers set
- [ ] Input validation at all boundaries
- [ ] SQL injection patterns detected
- [ ] XSS patterns detected
- [ ] File uploads validated
- [ ] Containers hardened
- [ ] Authentication and abuse controls match the threat model
- [ ] Security evidence requirements handed to `logging-standards`

## References

- [Python Security Examples](references/examples-python.md)
- [Infrastructure Security](references/infra-security.md)
