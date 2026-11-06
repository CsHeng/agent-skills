---
name: runtime-diagnosis
description: "Diagnose live system behavior that diverges from expected state across component boundaries: network, containers, GitOps state, secrets, or automation. Not for new infrastructure design, which belongs to design-change, or routine config edits with a settled approach."
---

# Runtime Diagnosis

Diagnose operational systems by separating desired state, actual state, data path, control path, and ownership boundaries.

## Use This Skill When

- live system behavior diverges from expected state and the cause is unknown
- the failure crosses component boundaries (network, containers, GitOps/IaC, secrets, automation)
- existing domain skills do not own the narrow cause

New infrastructure design or access control design belongs to `design-change`. Routine configuration edits with a settled owner use `implement-change`. In-process error handling uses `error-patterns`.

## Workflow

1. Identify the target and the mismatch between desired and observed behavior using already available facts.
2. Follow the data path, control path, identity, or state boundary that could explain the mismatch. When a cross-boundary failure needs candidate observation points, read `references/analysis-axes.md`.
3. Resolve uncertainty that could change the repair or make the next operation unsafe. Once the cause and authorized fix are clear, implement or hand off that fix.
4. Verify affected behavior with existing observation points, preferring live runtime evidence when hardware, services, routers, or containers are available. Add instrumentation for an actual diagnosis gap, and include recovery when the operation exposes the corresponding risk.

## Recovery Selection

Calibrate recovery to state value, blast radius, recoverability, and control cost. Environment classification, direct cutover, and protection of retained slices follow `references/replacement-and-cutover.md` in `development-standards`; reuse of recovery evidence follows `references/oracle-selection.md` in `skills-routing`; recovery modes and authority follow `implement-change` (Recovery).

- Use backup, retained state, an HA peer, VRRP, or an old release as recovery surfaces; rollback needs the guarded-rollback criteria below.
- Use `stop-and-diagnose` when continued mutation could compound uncertainty but restoring old state is not proven safer.
- Use `guarded-rollback` for an explicit, observed hazard where rollback is safer than forward repair and its target and verification are already tested. Hazard classes: management-connectivity loss, a routing or control-plane cycle, writer or quorum exclusivity loss, irreversible data-safety risk.
- Move to planning or design when evidence shows an unresolved goal, boundary, or ordering decision.

## Output

When this skill owns a troubleshooting response, lead with the most likely boundary or state mismatch. Name the exact observation point for each claim and mark inferred causes as inferred. Include the selected recovery policy when a change affects access, routing, secrets, important retained state, shared hosts, or production, and name rollback when the guarded-rollback criteria apply.
