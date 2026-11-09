# Security And Audit Logging

Use this profile for security detection, investigation, access evidence, and compliance audit needs. Logging supplies evidence; authentication, authorization, validation, rate limiting, and incident response own their respective controls.

## Event Selection

Select events from the threat model, policy, and investigation questions. Common candidates include:

- authentication success, failure, factor enrollment, recovery, and lockout
- authorization denial and policy changes; successful reads only when the data sensitivity or audit obligation justifies the volume
- privileged role, permission, configuration, secret, or key changes
- sensitive-data access, export, deletion, or consent changes
- abuse controls such as rate-limit, upload, validation, or anomaly outcomes
- audit configuration, collector failure, integrity failure, and evidence access

For each event, name the actor, action, target, outcome, policy or reason code, time, source context, and owning system. Record previous and new values only when safe and required.

## Redaction And Data Minimization

- Never log passwords, authentication factors, session secrets, API keys, private keys, raw authorization headers, or secret-bearing URLs.
- Prefer stable internal identifiers over names, email addresses, full IP addresses, request bodies, or tokens.
- Omit sensitive values when the investigation can use an identifier or reason code. Treat hashes of guessable inputs as identifiable data.
- Sanitize attacker-controlled values for the sink and bound their length; structured encoding prevents log injection; apply retention classification to the encoded data.
- Test both representative emission and forbidden-field absence.

## Correlation

Carry the minimum stable correlation needed across the audited path: request, trace, session, job, transaction, or business operation ID. Keep actor and target identifiers distinct. Do not use a correlation identifier as authentication or authorization evidence by itself.

## Retention And Access

- Derive retention from investigation windows, legal or contractual policy, storage risk, and deletion obligations.
- Restrict log read, export, search, and deletion privileges separately from application administration when the evidence warrants it.
- Record access to sensitive audit evidence when required, and protect exports under the same or stronger classification.
- Assign archive, legal hold, deletion, and restoration to named owners and test the required retrieval path.

## Tamper Evidence

Use append-only storage, signed batches, hash chains, immutable retention, or an independent collector only when the threat model or policy requires tamper evidence. Define the protected boundary, key owner, verification procedure, clock assumptions, gap detection, and response to failed verification. Keep integrity evidence under an independent authority when independent evidence is required.

## Verification

- Exercise allowed and denied paths and compare expected event classes.
- Prove secrets and unnecessary personal data are absent.
- Follow correlation across the required services or jobs.
- Query events using the actual incident or audit consumer path.
- Test collector failure, retention, restricted access, and tamper evidence when those properties are contractual.
