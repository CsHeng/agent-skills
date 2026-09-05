# Agent Skill Evaluation

Use this method when efficacy measurement is requested or a bounded risk judgment justifies evaluating agent guidance and the necessary execution authority and budget exist. Ordinary Skill editing does not require an experiment. Source review and maintenance checks can establish a guidance or distribution change, not that an agent follows it or works more safely, cheaply, or quickly.

This reference supplies evaluation guidance, not a benchmark runner, host adapter, persistent result store, mandatory CI gate, or permission grant.

## Question and Comparator

State the claimed behavior change, task boundary, and acceptance criteria before comparing outputs. For an incremental Skill change, compare the current relevant Skill bundle at a pinned revision with the candidate bundle, keeping unrelated instructions constant. Identify each variant's exact content, including uncommitted changes when a revision alone is insufficient.

A no-Skill or terse-prose control is optional when it answers a distinct question. It does not replace the existing-bundle baseline for deciding whether an incremental change helps. Select tasks that exercise the claimed improvement and its protected counterexamples; do not generalize beyond the evaluated tasks and conditions.

## Authority and Controlled Execution

Before running, establish authority for the selected host, external model calls and cost, credentials, data exposure, repository writes, and cleanup. Use only approved task data and disposable state. Missing authority or budget means report the limitation or propose a separately scoped evaluation; editing a Skill does not authorize a trial, installation, settings mutation, or data upload.

Keep fixture revisions, tasks, host and model configurations, tool and permission surfaces, resource budgets, and observable environments comparable between variants. Record intentional differences rather than attributing every outcome to the Skill. Use fresh task contexts and isolated writable state for separate runs; do not let one variant's outputs or repairs become the other's starting point.

Account for inherited repository and global instructions, discovery paths, plugins, hooks, memory, caches, sessions, and delegated-agent context where relevant. Build subprocess environments from an explicit allowlist and isolate homes or caches as needed. Do not globally disable or rewrite the user's settings to obtain isolation; if the selected host cannot isolate the required state within approved authority, stop that comparison or limit its claim.

## Activation and Contamination Evidence

Establish which intended instructions are active in each variant, including relevant child-agent contexts. A candidate absent from the explicit prompt can still enter a control through another discovery path, plugin, or hook.

Use the host's observable configuration and context evidence and, where needed, a discriminating activation control whose expected contrast is defined before the trial. A model's self-report or a single stylistic difference is not sufficient proof that the intended instructions are the only active difference.

Record what the host cannot expose. A contaminated run is invalid for an isolated comparison; materially unverified isolation remains uncertain and cannot support a causal savings claim. Preserve the observation and explain its classification rather than silently counting it as clean or discarding it. Repair isolation only within approved authority, and distinguish any replacement run from the original attempt.

## Independent Acceptance Evidence

Judge the actual edited files or other owned deliverable through the task's real correctness, completeness, security, accessibility, compatibility, and regression oracles as applicable. Use the smallest realistic boundary that proves the requirement. Keep those oracles independent of the candidate instructions and generated outputs; an agent-written test alone must not redefine acceptance.

A shorter result that omits a requested behavior, validation guard, accessibility condition, or useful regression check fails the corresponding requirement. Size or cost reductions do not compensate for that failure, and necessary tests are not bloat. State which required boundaries were executed, reviewed, or left unverified.

Where useful, check the oracle against known-good and plausible-but-wrong reference cases before trusting its scores. An optional model judge needs a stated rubric, calibration evidence, and limits; treat it as supporting evidence, not a sole security oracle or a substitute for a decisive executable check that is available.

## Bounded Attempts and Comparison

Choose a repeat, resource, and stopping budget justified by the question before execution. Keep per-task observations and account for every attempt: successes, failed acceptance, execution failures, timeouts, exclusions, and replacement runs. Do not retry until a preferred answer appears or silently remove failures from denominators.

Report relevant variation across runs. If different measures use different eligible subsets, state each subset and why data are missing. Unavailable or incomparable cost, token, or timing observations do not become zero. No universal sample count, pass percentage, or automatic CI threshold follows from this method.

Compare required behavior first. Treat code size, dependency count, and maintenance surface as contextual proxies for a named goal, not as the goal itself. Report tokens, cost, and latency only when the observed accounting and execution conditions are comparable, including relevant setup or instruction overhead. A more compact answer is not necessarily a smaller implementation or a cheaper agent run.

## Reporting and Claim Limits

Keep the report proportional to the decision. Include the question, comparator and content revisions, task/fixture and model/host conditions, isolation and activation evidence, acceptance results, attempt accounting, comparable measures, and remaining uncertainty. Preserve enough evidence for a reviewer to trace each material conclusion, subject to approved data handling; no new ledger or result schema is required.

Separate measured facts from inference and judgment. Report observed numerators, denominators, tasks, models, revisions, and limitations rather than universal safety or benefit claims. A small set of passing adversarial cases is evidence about those cases, not proof that generated code is secure.

Without an actual controlled comparator, do not invent a per-repository counterfactual saving from code that was never written. Published benchmarks from other tasks or environments are external evidence, not measurements of this change. Convergence, no measurable benefit, and insufficient evidence are valid results; do not manufacture an improvement to justify retaining a Skill rule.
