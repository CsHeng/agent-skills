+++
artifact_kind = "plan-amendment"
contract_version = 1
approval_status = "approved"
parent_plan = "2026-08-28-semantic-skills-only-plan.md"
trigger = "implementation-review-needs-plan-change"
review_budget = 0
+++

# Semantic-Only Plan Scope Amendment

The user approved this amendment after the single formal implementation review found maintained semantic-only boundary leaks outside the original task scope.

## Added Scope

- `pyproject.toml` and `uv.lock`
- `docs/AGENTS.md`, `docs/README.md`, `docs/quickstart.md`, `docs/changelog/design-decisions.md`, and the obsolete architecture state-machine document
- all resources, scripts, generated files, routing metadata, and focused tests owned by `implement-change-via-herdr`, `review-design`, `review-plan`, `review-implementation`, and `implement-change` repair guidance
- static conformance and standalone-copy checks required to detect the accepted findings

## Required Outcome

Preserve all 40 public Skill IDs while removing executable workflow adapters and provider-coupled execution protocols. Retain exactly one formal review for design, planning, and implementation; a focused repair receives fresh verification without another review. Stable configuration and documentation must describe only the provider-neutral Skill repository.

This amendment authorizes one focused repair of the accepted implementation-review findings and fresh focused plus aggregate verification. It does not authorize another review, external settings changes, plugin installation, commit, push, publication, or deployment.
