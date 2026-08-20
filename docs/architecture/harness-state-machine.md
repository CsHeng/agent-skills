# Harness State Machine

Workflow mode selection happens before phase implementation. `design-change` is a phase implementation, not the global router.

See `workflow-orchestration.md` for the canonical maintenance view of lifecycle composition, the generated full [harness routing sequence](diagrams/harness-routing-sequence.puml), the installed implementation invocation DAG, and the controller-owned repair loop.

## Modes

The canonical mode data lives in `contracts/workflow-modes.toml`.

| Mode | Use | Mutation | Design | Plan | Review |
|---|---|---:|---:|---:|---:|
| `read_only` | Explanation, triage, audit, inventory, fact gathering | no | no | no | no |
| `micro` | Small bounded low-risk edit | yes | no | yes | optional |
| `standard` | Ordinary feature, fix, or refactor | yes | yes | yes | yes |
| `regulated` | Infra, network, secrets, auth, security, deployment, public API, data migration | yes | yes | yes | yes |
| `emergency` | Break/fix or urgent recovery | yes | posthoc | minimal | posthoc |

## Routing Defaults

- Read-only questions route to `read_only`.
- Typo, local docs, or narrow low-risk changes route to `micro`.
- Ordinary implementation work routes to `standard`.
- Infra, network, GitOps, IaC, secrets, auth, security, deploy, public API, and data migration work routes to `regulated`.
- Outage, urgent revert, or broken local workflow recovery routes to `emergency`.

The runtime exposes whole-request `lifecycle classify` and whole-transition `lifecycle next` operations. They consume a normalized projection of `contracts/lifecycle.toml`, `contracts/workflow-modes.toml`, and `src/skills/session/use-coding-skills/references/routing.toml`; unknown or contradictory typed requests fail closed. The Python package does not own a duplicate classification or phase table.

## Composition Rule

Workflow skills own lifecycle state. Lower-plane skills may be composed into a workflow, but they do not advance approval, execution, review, truth sync, or close state by themselves.

Allowed composition example:

```text
regulated workflow -> infrastructure-triage -> security-guardrails -> design-change -> review-design -> plan-change -> review-plan -> implement-change -> review-change -> review-implementation -> sync-truth -> close-change
```

Not allowed:

```text
infrastructure-triage -> execute repo mutation -> close change
```

The cross-skill invocation graph stays acyclic. `implement-change` owns an internal `repair -> verify -> review` state transition; lower-plane reviewers return evidence and never call back into the controller. The installed `use-coding-skills/references/routing.toml` contract maps discovery and lifecycle phases to their owners, while the generated diagrams and their source precedence are documented in `workflow-orchestration.md`.

The active entry surface consists of public skills. The recommended local path exposes the generated payload through live child links under `~/.agents/skills`; provider plugins and `npx skills` copies are optional compatibility paths. Distribution choice does not change lifecycle ownership, state transitions, or approval gates, and each tool should resolve one active path per public ID.

## Evidence-Bound Lifecycle Tail

The execution tail uses explicit evidence states rather than conversation-memory claims:

```text
implementation-pending -> task-complete -> truth-sync-pending -> ready-for-close -> closed
```

`implement-change` emits immutable execution evidence only after the approved task ledger has controller convergence, oracle, and integration proof and the bounded review and verification gates pass. If the approved version-4 design has medium or high truth impact, it must require truth sync and the matching plan must declare non-empty stable truth refs inside its immutable touch set; missing or invalid scope returns `truth-sync-scope-required`.

Truth-affecting work advances to controller-authorized `sync-truth` preparation. `sync-truth` may update only the declared stable refs, may compose `organize-docs` only for supported structured docs-governance predicates, and then stops at the explicit human truth approval gate. Non-truth-affecting work can enter `ready-for-close` directly.

`close-change` validates the approved plan, immutable execution result, and exact approved truth artifact when one is required. Successful close judgment transitions from `close` to terminal `closed`, reports `next_entry: null`, and performs no repository or external lifecycle action. `closed` is idempotently terminal; a successful close never routes back to `close-change`.

## Versioned Authority And Durability

HCR-001 makes artifact contract version 4 and ledger version 4 the only authoring and mutable execution authority after refresh. Version 4 compiles truth coupling, complete task safety fields, named batch topology, and runtime policy into one immutable projection. The ledger derives the ready set, admits only an approved serial task or exact named batch, records capacity and serialization provenance, and is the sole source for runtime binding.

Version-3 artifacts and ledgers are compatibility readers only: immutable evidence and digest verification remain available, and truth-sync or close may finish work that had already converged before refresh. Version-3 initialization, task transition, verification, review, repair, external evidence, admission, and binding return typed rejection; new work cannot downgrade to the prior authority shape.

Ledger replacement stages and fsyncs the candidate, atomically promotes it, and fsyncs the parent directory. A post-promotion failure attempts durable restoration of the preceding ledger. Proven restoration returns `ledger-write-failed`; if neither promoted nor restored authority can be proven, the runtime returns `ledger-durability-unknown`, retains recovery evidence, and forbids blind retry or automatic digest refresh.
