---
name: infrastructure-triage
description: "Diagnose operational state mismatches or cross-boundary failures, or resolve infrastructure design affecting access, shared resources, or retained state. Not for routine config or deployment edits with a settled approach."
---

# Infrastructure Triage

Diagnose and design operational systems by separating desired state, actual state, traffic path, control path, and ownership boundaries.

## Workflow

Use the investigation needed to explain the observed failure or decide the actual operational boundary.

1. Identify the relevant target and the mismatch between desired and observed behavior, using already available facts.
2. Follow the data path, control path, identity, or state boundary that could explain that mismatch. When a cross-boundary failure needs candidate observation points, read `references/analysis-axes.md`.
3. Resolve uncertainty that could change the repair or make the next operation unsafe. Once the cause and authorized fix are sufficiently clear, implement or hand off that fix.
4. Verify the affected behavior with existing observation points, preferring live runtime evidence when hardware, services, routers, or containers are available. Add instrumentation for an actual diagnosis gap, and include recovery when the operation exposes the corresponding risk.

## Recovery Selection

Calibrate recovery to state value, blast radius, recoverability, and control cost. Environment classification, direct cutover, and protection of retained slices follow `references/replacement-and-cutover.md` in `development-standards`; reuse of recovery evidence follows `references/oracle-selection.md` in `skills-routing`; recovery modes and authority follow `implement-change` (Recovery).

- Use backup, retained state, an HA peer, VRRP, or an old release as recovery surfaces; rollback needs the guarded-rollback criteria below.
- Use `stop-and-diagnose` when continued mutation could compound uncertainty but restoring old state is not proven safer.
- Use `guarded-rollback` for an explicit, observed hazard where rollback is safer than forward repair and its target and verification are already tested. Hazard classes: management-connectivity loss, a routing or control-plane cycle, writer or quorum exclusivity loss, irreversible data-safety risk.
- Move to planning or design when evidence shows an unresolved goal, boundary, or ordering decision.

## Output

When this skill owns a troubleshooting response, lead with the most likely boundary or state mismatch. Name the exact observation point for each claim and mark inferred causes as inferred. Include the selected recovery policy when a change affects access, routing, secrets, important retained state, shared hosts, or production, and name rollback when the guarded-rollback criteria apply.
