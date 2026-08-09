# Stress-Test Mode

Use this reference only when the user explicitly asks to grill, stress-test, harden, challenge, or interrogate a design or plan. Do not make this the default for ordinary implementation tasks.

## Rules

- Prefer questions that resolve scope, non-goals, state ownership, permission boundaries, data paths, recovery policy, or verification.
- Exclude questions whose answers would not change the design, plan, execution gate, verification, or recovery boundary.

## Frontier Contract

- `frontier`: Keep every unresolved decision-changing question whose prerequisites are already settled in the current frontier. A question that depends on another unresolved answer waits for a later round.
- `round`: Ask the whole current frontier in one numbered round instead of serializing independent decisions across separate turns.
- `question_id`: Give questions stable `Q*` identifiers that remain unchanged when later rounds add newly unblocked questions.
- `recommendation`: Include the recommended answer for every question.
- `tradeoff`: State the material cost, risk, or discarded alternative attached to the recommendation.
- `fact_owner`: Inspect code, docs, runtime, and required external evidence with the main agent instead of asking the user for facts that can be discovered. This contract does not add automatic delegation authority.
- `sequential_override`: Respect an explicit user preference to work one question at a time without changing the decision tree or completion condition.

Recompute the frontier after each user reply: record settled decisions, unlock questions whose prerequisites are now satisfied, and ask the next complete round.

- `completion`: Stop when no unresolved decision-changing question remains. Do not act on the result until the user confirms shared understanding and the owning workflow's approval gate permits continuation.

## Question Shape

Render each question with its stable identifier, short title, decision body, recommendation, and tradeoff. Keep one round scannable so the user can answer by identifier without quoting the questions.

## Output Shape

After the stress-test, convert answers into:

- confirmed assumptions
- rejected alternatives
- remaining open constraints
- design or plan changes
- verification and recovery implications
