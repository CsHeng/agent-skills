# Design Decisions

## 2026-10-07 — One Authored Tree And Explicit Installation

`skills/<public-id>/` is the only authored and installable Skill tree. Instructions, references, scripts, assets, and provider metadata are edited directly there; the public inventory retains useful activation and semantic checks. The former nested source tree, flattening, generated index, source map, and mirror-parity checks are removed. Architecture diagrams remain generated views of the product contract.

Installed Skills are independent copies. Source edits, Git updates, generation, and checks do not refresh global content; explicit installation or update does. Prefer the existing `npx skills` manager for platform handling. Links between host discovery and a managed installed copy remain valid; links back to the active development checkout do not. Local-path installs refresh through another explicit add, remotely tracked installs use the manager's update operation, and retired owned IDs need explicit removal. Preserve unrelated installed Skills.

Optional plugins retain their own managed installation lifecycle and must satisfy the same separation. The repository's plugin-registration helpers do not provide a general copy/update command. This decision supersedes the 2026-08-20 live-checkout-link recommendation and the 2026-08-07 generated-tree design; it also replaces the generated-distribution and parity portions of the 2026-08-28 decision without changing its semantic-only product boundary.

## 2026-08-28 — Portable Semantic Skills Only

### Decision

This repository owns provider-neutral semantic Agent Skills, declarative authoring contracts, generated portable distribution, static conformance, stable documentation, and optional plugin manifests. It owns no workflow engine, artifact validator, task graph compiler, mutable execution ledger, provider adapter, actor or model binding, attempt scheduler, or replay protocol.

The active coding agent owns request interpretation, Skill selection, sequencing, evidence judgment, conditional review, finding adjudication, and the final response. Review runs only for explicit intent, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. Standalone review starts from the supplied bounded target without synthesizing upstream work; evaluators remain read-only and the calling agent owns any accepted repair.

### Consequences

- Public Skill IDs remain stable and portable across compatible agent products.
- Mechanically enforced workflow behavior belongs outside this repository and is neither imported nor named as a dependency.
- Repository scripts validate only authored inventory, metadata, reference closure, generated parity, documentation, and ordinary code quality.
- Earlier runtime, provider-binding, generated lifecycle, fixed phase, workflow-mode, and mandatory-review decisions are superseded. Their historical detail is retired to `$AGENT_ARCHITECTURE_DIR/archived/agent-skills/plans/`, outside current product truth; only active change bundles remain under `$AGENT_ARCHITECTURE_DIR/docs/plans/skills/`, registered in that domain's index.

## 2026-08-20 — Live Child Links Are The Recommended Local Path

Superseded by the 2026-10-07 explicit installation decision above.

Use a local Git checkout plus one child symlink per public ID. Update the checkout with Git, regenerate its owned payload, and start a new agent session. Optional plugin or copied installations have separate update and removal lifecycles, and each tool should expose only one active path per public ID.

## 2026-08-07 — Generated Root-Flat Distribution

Superseded by the 2026-10-07 single-tree decision above.

`src/skills/` is authored truth. `skills/` is the generated root-flat payload for distributed public IDs, and each distributed Skill must be self-contained under its own standard Agent Skills directory. Undistributed public IDs stay contracted and authored but are omitted from that payload. Provider plugin manifests package that same payload without changing semantics.
