# Model Prompt Guidelines And Cross-Model Steering

Read this reference when writing or revising Skill instructions that shape completion boundaries, stop conditions, assumption rules, approval lists, verification requirements, code-change stance, delegation rules, or output style, or when harmonizing behavior across model families.

## Contents

- [Official Vendor Guidelines](#official-vendor-guidelines)
- [Two Reading Habits](#two-reading-habits)
- [Cross-Model Authoring Rules](#cross-model-authoring-rules)
- [Dual-Reader Review Scan](#dual-reader-review-scan)

## Official Vendor Guidelines

- **OpenAI:** [Using the Latest Model (GPT-6.2 Astra and Sol)](https://developers.openai.com/api/docs/guides/latest-model) and [Prompt Engineering](https://developers.openai.com/api/docs/guides/prompt-engineering) cover writing style, self-contained final answers, autonomous task completion, reasonable reversible assumptions, reusing existing repository logic, focused regression testing, human-readable code, and prefix-cache stability.
- **Anthropic:** [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), [Prompting Claude Fable 5.2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2), [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5), [Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5), and [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) cover effort calibration, completing multi-step tasks through ordinary tool obstacles, keeping caution scoped to real risks, code-ownership framing effects, subagent cost expectations, natural prose aims, self-contained reports for low-context readers, and append-only history for preserved thinking.
- **Google Gemini:** [Prompt Design Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies), [Gemini Thinking](https://ai.google.dev/gemini-api/docs/thinking), [Latest Gemini Models](https://ai.google.dev/gemini-api/docs/models), and [What's New in Gemini 4 Hydrogen](https://ai.google.dev/gemini-api/docs/whats-new-gemini-4-hydrogen) cover direct instructions, consistent XML or Markdown delimiters, placing long context before the final task instruction, controlling reasoning cost through `thinking_level`, and steering agentic decomposition, adaptability, persistence, risk assessment, and ambiguity handling.

## Two Reading Habits

The same Skill text meets two reading habits across model families and effort levels:

- **Letter-following readers (such as GPT / Astra / Sol routes)** execute each sentence as a literal specification: an unmarked list becomes a mandatory checklist, a broad caution becomes an approval gate, a status taxonomy becomes an output template, and an unqualified instruction to add tests or split modules produces extra helper layers and oversized test suites.
- **Gist-following readers (such as Claude Fable / Opus / Sonnet and Gemini routes)** act on apparent intent: at lower effort or on long tasks they may end a turn at a natural pause (announcing the next step, offering to continue, listing non-blocking decisions, or reporting a milestone), omit secondary parts of a multi-part request, write choppy prose under hard word-count limits, or perform unrequested refactors when told they own the codebase.

Write each rule so that literal compliance and gist-level reading converge on the same engineering action.

## Cross-Model Authoring Rules

When authoring or revising a Skill, apply these steering principles while keeping each runtime rule at its single owning Skill:

- **Bind the outcome and finish line; leave means revisable.** Write rules that bind the observable result, user-fixed choices, and real safety and authority boundaries while leaving agent-inferred steps, task splits, and local proof methods revisable (`development-standards`, `plan-change`). Direct optional ideas outside the requested scope and repository policy to a brief closing note when useful.
- **Close discretionary mid-task stops.** In workflow Skills (`implement-change`), define when a turn may pause while ready authorized work remains: only for a decision that blocks the remaining work or an irreversible or external action awaiting confirmation, alongside normal task completion, explicit budgets, cancellation, or a host-supported yield while awaiting workers. Require progress notes, completed milestones, and non-blocking recommendations to travel in the same turn with the next ready action, and require a final completeness check against each part of the request.
- **Distinguish ordinary obstacles from `blocked`.** Have execution rules (`implement-change`) require diagnosing and working through ordinary obstacles (retrying a transient error or timeout, fixing a call, or using an available fallback) before reporting `blocked`.
- **Specify reversible assumptions vs blocking questions.** Have clarification rules (`design-change/references/goal-alignment.md`) instruct the agent to make a reasonable, reversible assumption for minor ambiguity, state it in one line when it affects the result, and continue, asking only when answers would materially change the goal, external behavior, retained state, or authority.
- **Name concrete approval targets and routine autonomous work.** Keep approval boundaries (`implement-change`, `development-standards`) specific about which external or destructive actions need permission and which local reads, builds, tests, scratch files, and task-owned development services proceed directly, preventing accumulated caution from stalling routine steps.
- **Frame code and dependency rules around autonomous library selection, readability, and request scope.** The user owns business intent while the agent owns technical selection and repository maintenance (`design-change`, `development-standards`, `references/dependency-selection.md`). Unless the user fixed a library or standard-library constraint, have the agent default to mature community libraries or frameworks for non-trivial general capabilities (recording the library and its capability boundary in the design so bespoke infrastructure and test suites do not bloat future session context), and use the standard library directly for small self-contained operations. Favor reusing existing repository functions and types, keeping edits within the requested scope, and writing human-readable code over dense one-liners or premature single-caller helpers; route separate cleanup ideas to a closing line.
- **Pair a real verification floor with targeted test additions.** In verification rules (`implement-change`, `testing-strategy`), require running an existing check or reproducer that exercises changed runtime behavior (reporting what actually ran and any remaining behavioral gap if only syntax was checked), while adding a persisted regression test only when requested, required by repository policy, or needed for a specific failure existing checks miss.
- **Express output style as reader-first aims.** In presentation rules (`output-styles`), ask for a self-contained final reply written for a reader who did not watch the intermediate steps, with typical sentence and paragraph lengths where a needed condition, reason, or consequence outranks the word count.
- **Price delegation and keep runtime knobs host-owned.** In delegation guidance (`implement-change/references/delegated-execution.md`), state the parent's coordination cost so workers are used only when parallel progress or isolation justifies it. Leave effort and thinking levels, sampling parameters, and prefix-cache or preserved-thinking mechanics to the host and user layers, and keep Skill text free of per-turn volatile values so host prompt caches and preserved thinking remain valid.

## Dual-Reader Review Scan

When editing behavioral rules in the areas above, check the changed sentences against both reading habits:

| Prompt pattern | Letter-following risk | Gist-following risk | Portable rewrite |
| --- | --- | --- | --- |
| Unmarked enumeration ("Confirm A, B, C, D, E") | Runs a preflight checklist or interrogates the user on all items | Skims the list and misses the binding constraint | Mark as "those the change touches" or "examples", and state that discoverable facts are read from the workspace |
| Unconditional step ("8. Obtain independent review") | Invokes a reviewer subagent on every trivial diff | Launches extra self-review rounds at high effort | Put the trigger condition before the verb ("When a condition in `review-change` holds, obtain review; otherwise continue to step 10") |
| Open milestone note ("Keep state recoverable at milestones") | Emits a formal status report artifact at each step | Treats the milestone summary as a place to end the turn | State that milestone notes travel in the same turn with the next ready action |
| Hard prose quota ("at most 20 words per sentence") | Chops conditions away from the actions they bound | Produces clipped, unnatural prose | State typical lengths and keep a needed condition, reason, or consequence with its action |
| Broad caution ("external changes need approval") | Pauses on local builds, tool calls, or development services | Accumulates caution across turns and asks permission for routine steps | Name the exact external targets and list the local actions that proceed directly |
| Broad test mandate ("write regression evidence for sibling paths") | Writes excessive test scaffolding around simple changes | Skips running existing checks at low effort | Require running an existing check or reproducer that exercises the change, and add a persisted test only for an uncovered failure |
