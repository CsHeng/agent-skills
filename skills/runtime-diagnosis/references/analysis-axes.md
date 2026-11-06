# Analysis Axes

Read this when a cross-boundary failure needs candidate observation points. The axes are investigation options; pick the ones the mismatch points to.

- Network: DNS, TLS, NAT, route, proxy, tunnel, firewall, listener, client-side proxy state.
- Containers: image digest, bind mounts, env injection, network namespace, published ports, health checks, in-container state.
- GitOps and IaC: declared state, live state, drift, state backend, apply identity, apply order, recovery policy.
- Secrets and Auth: credential source, storage boundary, token audience, principal, scope, rotation, audit trail.
- Automation: trigger identity, idempotence, concurrency, retry behavior, partial failure, recovery policy, audit evidence.
