# Scope Contracts

A scope contract records how neighboring Skills divide requests that could plausibly select more than one of them. It belongs at the router or registry layer, where ambiguity is resolved, rather than in every Skill's description.

## Clusters And Questions

- Group Skills that a reasonable model could confuse for the same request. A Skill may belong to more than one cluster, and a method reference inside a Skill may be a member when requests select that method directly.
- Give each cluster one question whose answer separates its members. Phrase it as the decision the model actually faces, such as whether facts are only read, verified behavior is written back, or documentation structure changes.
- Clusters model the current inventory. Revise them when Skills change; they are not a priority order or a lifecycle.

## Handoffs

Write a handoff only for a situation a model is likely to misroute. Each handoff states:

- the situation, as a request or condition rather than a keyword;
- exactly one receiver: a Skill, a method reference inside a Skill, or no Skill when general instructions and repository rules suffice;
- the candidates it replaces, which never include the receiver.

Use no Skill as the receiver when the situation needs no reusable method from the collection that owns the registry, such as an ordinary commit or a routine known command. That exit stops a nearby Skill from absorbing work it should not own. A registry speaks only for its own collection, so a separately installed Skill whose description matches the work still applies.

If a refusal has no single receiver, rewrite the situation until it has one, or delete it. A negative that only restates what the description already excludes adds nothing.

## Keep One Owner

- The registry owns handoffs. A Skill body names the receiver for each case it refuses, consistent with the registry, without keeping its own neighbor list.
- A description keeps at most the one or two most confusable exclusions and names their receivers.
- Trigger examples and counterexamples live in maintenance probes, not in installed text.

## Anti-Patterns

- negatives without receivers, which say what not to do without saying who should act
- copying the whole negative list into the description
- keyword lists or lexical hints that act as a second router
- priority matrices or mandatory routing hops in place of a separating question
- a host-only mechanism that carries meaning the portable text lacks
