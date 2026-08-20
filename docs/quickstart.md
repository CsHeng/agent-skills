# Quickstart

A five-minute path from a live skill checkout to a first completed change.

## 1. Install And Verify

Keep this repository as a local Git checkout and create one child symlink per selected public ID from its generated `skills/` tree into `~/.agents/skills/`. Pull the checkout to update it and start a new agent session so compatible tools refresh discovery.

Before exposing the same links through a provider-specific directory, prove that every tool scanning both roots deduplicates or has the provider compatibility path disabled. On the primary development machine, verify Grok has no duplicate names and ignores Claude skills before adding Claude child links, then repeat the probe afterward.

Claude Code and Codex plugin installers and `npx skills@latest add CsHeng/agent-skills` remain compatible alternatives. They are not the recommended local path because they introduce provider caches or copied destinations with separate update and removal state. Exact optional commands are in the README Install section.

## 2. What You Got

Seven top-level skills form the sovereign kernel:

The table uses portable unqualified IDs. A host may display or invoke the same skill with a collection prefix such as `coding:design-change`; that prefix is host notation, not a second public identity.

| Skill | Role |
|---|---|
| `analyze-project` | Read-only project explanation and drift detection |
| `design-change` | Design a change: scope, boundaries, truth impact |
| `plan-change` | Versioned task DAG, verification, failure policy |
| `implement-change` | Execute an approved plan with review and repair |
| `review-change` | Agent-native review gate over a bounded slice |
| `sync-truth` | Update stable docs after a verified change |
| `close-change` | Merge, release, or cleanup judgment |

Everything else (language guidelines, testing, security, tooling, git helpers) is a lower-plane skill these seven compose automatically. The full map: [skill planes overview](architecture/generated/skill-planes.svg); the authoritative inventory is `contracts/skills.toml`.

The human shorthand **design → plan → execute** maps to `design-change` → `plan-change` → `implement-change`.

## 3. Pick Your Entry Point

The harness selects a workflow mode from your request; you only pick the entry:

| Your situation | Start with | Gates you will hit |
|---|---|---|
| "Explain this repo / find drift" | `analyze-project` | none (read-only) |
| Small, bounded, low-risk edit | `plan-change` | plan approval → execute → close |
| Ordinary feature, fix, or refactor | `design-change` | design approval → plan approval → review → truth sync → close |
| Infra, secrets, auth, public API, migration | `design-change` | full gate chain with explicit recovery surface |
| Production is on fire | describe the emergency | minimal up-front ceremony, post-hoc review + truth sync |

You stay sovereign: the harness stops for explicit human approval at design, plan, truth-sync, and close. It never runs unattended by default, and execution is serial unless you approve a named parallel batch in the plan.

## 4. First Change Walkthrough

A standard feature, end to end, using one host's optional `coding:` rendering:

```text
$coding:design-change add a --json output mode to the status command
  → harness writes a design artifact, runs bounded design review
  → you approve (approval_status recorded on the artifact)

$coding:plan-change
  → harness reads the approved design, writes a versioned task DAG with
    tests/oracles per task, runs bounded plan review
  → you approve

$coding:implement-change
  → harness executes the plan as one unit, verifies each task,
    runs one bounded implementation review, repairs what it accepts

$coding:sync-truth
  → stable docs updated only if the change has real truth impact

$coding:close-change
  → merge/release judgment and remaining human actions
```

Stage artifacts (designs, plans) live under `docs/plans/`. They are kept for history and excluded from default docs searches.

## 5. Go Deeper

- How routing, modes, gates, and the repair loop actually work: `docs/architecture/workflow-orchestration.md` (with rendered diagrams under `docs/architecture/generated/`).
- How an individual skill works: its `SKILL.md` under `skills/`.
- What each skill is allowed to do (mutation, agents, invocation): `contracts/skills.toml`.
- AI-facing repository rules: `AGENTS.md`.
