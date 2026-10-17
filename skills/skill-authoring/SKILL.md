---
name: skill-authoring
description: "Create, revise, split, merge, or retire an Agent Skill's discovery surface and admission boundaries: description, scope contract against neighboring Skills, reference layout, and activation metadata, with a discovery-layer self-review; also review a set of descriptions as text for overlap and selection blind spots. Not for changing only a Skill's domain method, which is ordinary implementation, or for measured selection or behavior experiments, which use testing-strategy."
---

# Skill Authoring

Shape where a Skill is found, what it admits, and what it hands to its neighbors, so that a model choosing among Skills sees each deciding fact when it decides. The Skill's domain method stays with that Skill.

## Use This Skill When

- creating, splitting, merging, renaming, or retiring a Skill
- revising a description, an activation mode or host invocation metadata, a neighbor boundary, or the reference layout
- reviewing a set of descriptions as text for overlap, contradiction, or selection blind spots

An edit that changes only a Skill's domain method, without touching its description, boundaries, or activation, is ordinary implementation. Measuring whether agents actually select or follow a Skill is an evaluation: use `references/agent-skill-evaluation.md` in `testing-strategy` with its authority and budget requirements.

Editing Skill files needs an explicit request. It does not authorize editing harness-global instruction files, installing or refreshing installed Skills, or running live-model trials; each needs its own approved scope. When a rename or retirement leaves a host entry instruction or an installed copy pointing at the old ID, report that follow-up instead of changing those files.

## Workflow

1. Write the scope contract first: the cluster of neighboring Skills, the question that separates them, what this Skill owns, and each handoff with its situation, one receiver, and the candidates it replaces. Read [Scope Contracts](references/scope-contracts.md).
2. Place each fact on the layer that is visible when the model uses it. Read [Discovery Layers](references/discovery-layers.md).
3. Write the body's admission section, then the description as its summary: the decision the Skill resolves, its trigger, the one or two most confusable exclusions with their receivers, and an explicit or overlay marker when the activation mode needs one.
4. Where the repository keeps an inventory, activation registry, or scope-contract registry, change that owner first and its summaries and projections after it. Follow the repository's own instructions for exact files, generators, and checks.
5. Write or revise the body and references with [Instruction Content](references/instruction-content.md).
6. Review layer by layer: each lower layer refines and never contradicts the one above, every exclusion names its receiver, no fact has two owners, and no trigger examples, keyword lists, or inventory constants enter installed text. Where the repository keeps selection probes, add or update a pair: one request the Skill should own and a nearby one it should hand off.
7. Run the repository's structural checks. Run a behavioral comparison only for a concrete behavioral question.

Report what changed on the discovery surface, the handoffs added or removed with their receivers, the checks run, and any entry, installation, or host follow-up that needs separate authority.
