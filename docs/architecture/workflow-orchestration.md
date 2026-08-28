# Semantic Workflow Composition

The collection defines semantic responsibilities, not orchestration mechanics.

1. `analyze-project` maps current repository truth without mutation.
2. `design-change` defines a bounded change and performs one bounded design review.
3. `plan-change` turns approved scope into ordered tasks and performs one bounded plan review.
4. `implement-change` applies an approved plan, verifies it, and performs one bounded implementation review.
5. `sync-truth` updates stable truth when verified behavior changed.
6. `close-change` judges whether the requested change boundary is complete.

These Skills may be invoked independently when their preconditions are already satisfied. Informal work does not inherit review. `review-change` may also be invoked directly with one bounded target and does not route backward to manufacture missing phases.

Plans may describe task dependencies, safe independence, delegation eligibility, verification, and recovery because those facts help any implementing agent. They do not bind physical actors or models, schedule tasks, persist attempts, enforce a graph, or define replay behavior.
