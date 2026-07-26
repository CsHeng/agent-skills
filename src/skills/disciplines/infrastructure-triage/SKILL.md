---
name: infrastructure-triage
description: "Use for infrastructure, network, proxy, tunnel, container, GitOps, IaC, Secrets, Auth, and automation troubleshooting or design; analyze data path, control boundary, state owner, permissions, drift, explicit recovery policy, and observability."
---

# Infrastructure Triage

Diagnose and design operational systems by separating desired state, actual state, traffic path, control path, and ownership boundaries.

## Workflow

1. Identify the target surface: host, repo, runtime, cluster, container, router, service, cloud control plane, or automation runner.
2. Separate desired state from actual state.
3. Trace the data path and control path.
4. Identify state owner, permission principal, trust boundary, and recovery surface.
5. Collect evidence at boundaries before changing configuration.
6. Return the fix, verification point, observability point, and fallback.

## Analysis Axes

- Network: DNS, TLS, NAT, route, proxy, tunnel, firewall, listener, client-side proxy state.
- Containers: image digest, bind mounts, env injection, network namespace, published ports, health checks, in-container state.
- GitOps and IaC: declared state, live state, drift, state backend, apply identity, apply order, recovery policy.
- Secrets and Auth: credential source, storage boundary, token audience, principal, scope, rotation, audit trail.
- Automation: trigger identity, idempotence, concurrency, retry behavior, partial failure, recovery policy, audit evidence.

## Recovery Selection

- Default to backup or snapshot plus fix-forward for ordinary correctness, rendering, deploy-verification, and service-health failures.
- Treat backup, retained state, an HA peer, VRRP, or an old release as a recovery surface, not automatic rollback authorization.
- Use `stop_and_diagnose` when continued mutation could compound uncertainty but restoring old state is not proven safer.
- Use guarded automatic rollback only for an explicit, observed hazard such as management-connectivity loss, a routing or control-plane cycle, writer or quorum exclusivity loss, or irreversible data-safety risk, and only when the target and verification are tested.
- Failure count alone never justifies moving from implementation to planning or design.

## Output

- Lead with the most likely boundary or state mismatch.
- Distinguish verified facts from inferred causes.
- Name the exact observation point for each claim.
- Include the selected recovery policy when a change affects access, routing, secrets, production state, or remote execution. Name rollback only when the guarded criteria above apply.
- Prefer live runtime evidence when hardware, services, routers, or containers are available.
