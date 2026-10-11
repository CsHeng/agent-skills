---
name: infrastructure-triage
description: "Diagnose operational state mismatches or cross-boundary failures, or resolve infrastructure design affecting access, shared resources, or retained state. Not for routine config or deployment edits with a settled approach."
---

# Infrastructure Triage

Diagnose and design operational systems by separating desired state, actual state, traffic path, control path, and ownership boundaries.

## Workflow

Use only the investigation needed to explain the observed failure or decide the actual operational boundary. Routine Ansible, container, or deployment edits do not require this workflow merely because of their file type or vocabulary.

1. Identify the relevant target and the mismatch between desired and observed behavior, using already available facts.
2. Follow the data path, control path, identity, or state boundary that could explain that mismatch. Do not inspect every analysis axis by default.
3. Resolve uncertainty that could change the repair or make the next operation unsafe. Once the cause and authorized fix are sufficiently clear, implement or hand off that fix rather than expanding preflight.
4. Verify the affected behavior with existing observation points where sufficient. Add instrumentation only for an actual diagnosis gap; include recovery only when the operation exposes the corresponding risk.

## Analysis Axes

The following are investigation options, not a checklist or a requirement to construct new observability and recovery surfaces.

- Network: DNS, TLS, NAT, route, proxy, tunnel, firewall, listener, client-side proxy state.
- Containers: image digest, bind mounts, env injection, network namespace, published ports, health checks, in-container state.
- GitOps and IaC: declared state, live state, drift, state backend, apply identity, apply order, recovery policy.
- Secrets and Auth: credential source, storage boundary, token audience, principal, scope, rotation, audit trail.
- Automation: trigger identity, idempotence, concurrency, retry behavior, partial failure, recovery policy, audit evidence.

## Recovery Selection

Calibrate recovery to state value, blast radius, recoverability, and control cost. Remote hosts, Ansible, and deploy wording do not by themselves select production recovery.

- Authorized rebuildable development may rebuild, replace, or fix-forward. Do not default to backup or snapshot for ordinary correctness, rendering, deploy-verification, or service-health failures.
- Protect unique data, credentials, shared hosts, and explicitly retained state with a targeted backup or export when that slice needs it. Do not escalate a retained-state exception into a full production process.
- Actual production, especially destructive change, needs a named goal, impact, authorization, and the recovery evidence this change requires. Reuse still-valid recovery evidence; a new revision, digest, or template-only edit does not by itself trigger a full restore drill. Re-verify when retained-state migration, recovery implementation, or runtime recovery conditions changed.
- Treat backup, retained state, an HA peer, VRRP, or an old release as a recovery surface, not automatic rollback authorization.
- Use `stop_and_diagnose` when continued mutation could compound uncertainty but restoring old state is not proven safer.
- Use guarded automatic rollback only for an explicit, observed hazard such as management-connectivity loss, a routing or control-plane cycle, writer or quorum exclusivity loss, or irreversible data-safety risk, and only when the target and verification are tested.
- Failure count alone never justifies moving from implementation to planning or design.

## Output

- When this skill owns a troubleshooting response, lead with the most likely boundary or state mismatch. When supporting another workflow, contribute the relevant findings to its deliverable under `output-styles` without prescribing another opening or report.
- Distinguish verified facts from inferred causes.
- Name the exact observation point for each claim.
- Include the selected recovery policy when a change affects access, routing, secrets, important retained state, shared hosts, or production. Name rollback only when the guarded criteria above apply.
- Prefer live runtime evidence when hardware, services, routers, or containers are available.
