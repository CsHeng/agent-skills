---
name: review-implementation
description: "Read-only evaluator for one bounded implementation target, by default an exact diff, supplied with its brief. Return causally qualified candidate findings; direct review requests belong to review-change, and repair decisions stay with the calling implementing agent."
---

# Review Implementation

Review only the supplied objective, non-goals, acceptance criteria, exact changed files or diff, declared verification, and a small justified supporting-file set, under the finding rules, causal scope, and verdict in `review-change`.

## Implementation-Specific Checks

- Evidence applies to the actual candidate and protected behavior. On follow-up, inspect the supplied new content, prior dispositions, unresolved findings, and affected regression boundaries; a repair claim needs evidence, and the affected boundaries determine the follow-up audit.
- A blocking candidate is caused or newly activated by the current diff, violates a named requirement or oracle, has a concrete consequence, carries sufficient evidence, and admits a smallest fix inside the approved scope. When the brief supplies a whole artifact, defects anywhere in it are in scope.
- A new issue enters scope when evidence shows it blocks the current outcome or its necessary correctness or safety within the chosen design and authority; a directly blocking caller or schema mismatch and a change-induced regression qualify when supported by that evidence. A demonstrated critical risk outside authority is returned as `needs-decision`.
- When the selected mechanism produces a growing repair stream, the finding compares simplifying or removing it with further hardening.
- Newly introduced or changed identifiers are checked for leaked plan task IDs, stage codes, or review rounds under the naming rule in `development-standards`, with evidence tying the name to the plan and establishing the appropriate domain responsibility; genuine domain terminology and compatibility-bound names stand.
- Accept an authorized best-effort secondary adaptation with evidence; flag relabeling a required result as secondary, deleting its oracle, or replacing a specified library when substitution authority is absent.
