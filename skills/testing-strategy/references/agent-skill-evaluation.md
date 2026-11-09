# Agent Skill Evaluation

Use this method when efficacy measurement is requested or a bounded risk judgment justifies evaluating agent guidance and the necessary execution authority and budget exist. Ordinary Skill editing uses source review and maintenance checks to establish a guidance or distribution change. Evaluation establishes evidence of agent adherence and safety, cost, or speed outcomes.

This reference supplies evaluation guidance; the user or approved plan owns execution authority.

For offline review of goal, risk, and discretion behavior, use [Goal And Risk Cases](goal-and-risk-cases.md). Those cases are optional comparison material.

## Question and Comparator

State the claimed behavior change, task boundary, and acceptance criteria before comparing outputs. For an incremental Skill change, compare the current relevant Skill bundle at a pinned revision with the candidate bundle, keeping unrelated instructions constant. Identify each variant's exact content, including uncommitted changes when a revision alone is insufficient.

A no-Skill or terse-prose control is optional when it answers a distinct question. Use the existing-bundle baseline to decide whether an incremental change helps. Select tasks that exercise the claimed improvement and its protected counterexamples, including [Goal And Risk Cases](goal-and-risk-cases.md) when they match the claim; limit conclusions to the evaluated tasks and conditions.

## Authority and Controlled Execution

Before running, establish authority for the selected host, external model calls and cost, credentials, data exposure, repository writes, and cleanup. Use only approved task data and disposable state. Missing authority or budget means report the limitation or propose a separately scoped evaluation; trials, installation, settings mutation, and data upload each require appropriate authority.

Keep fixture revisions, tasks, host and model configurations, tool and permission surfaces, resource budgets, and observable environments comparable between variants. Record intentional differences and their possible effects. Use fresh task contexts and isolated writable state for separate runs; each variant starts independently of the other's outputs and repairs.

Account for inherited repository and global instructions, discovery paths, plugins, hooks, memory, caches, sessions, and delegated-agent context where relevant. Build subprocess environments from an explicit allowlist and isolate homes or caches as needed. Keep the user's global settings intact when obtaining isolation; if the selected host cannot isolate the required state within approved authority, stop that comparison or limit its claim.

## Activation and Contamination Evidence

Establish which intended instructions are active in each variant, including relevant child-agent contexts. A candidate absent from the explicit prompt can still enter a control through another discovery path, plugin, or hook.

Use the host's observable configuration and context evidence and, where needed, a discriminating activation control whose expected contrast is defined before the trial. Establish the active instruction differences with host evidence and discriminating controls.

Record what the host cannot expose. A contaminated run is invalid for an isolated comparison; materially unverified isolation remains uncertain and cannot support a causal savings claim. Preserve the observation and explain its classification. Repair isolation only within approved authority, and distinguish any replacement run from the original attempt.

## Independent Acceptance Evidence

Judge the actual edited files or other owned deliverable through the task's real correctness, completeness, security, accessibility, compatibility, and regression oracles as applicable. Use the smallest realistic boundary that proves the requirement. Keep those oracles independent of the candidate instructions and generated outputs; the task's requirements own acceptance.

A shorter result that omits a requested behavior, validation guard, accessibility condition, or useful regression check fails the corresponding requirement. Assess size and cost only after required behavior and necessary tests pass. State which required boundaries were executed, reviewed, or left unverified.

Where useful, check the oracle against known-good and plausible-but-wrong reference cases before trusting its scores. An optional model judge needs a stated rubric, calibration evidence, and limits; treat it as supporting evidence alongside available decisive executable checks and independent security oracles.

## Bounded Attempts and Comparison

Choose a repeat, resource, and stopping budget justified by the question before execution. Keep per-task observations and account for every attempt: successes, failed acceptance, execution failures, timeouts, exclusions, and replacement runs. Follow the predefined stopping budget and include failures in the applicable denominators.

Report relevant variation across runs. If different measures use different eligible subsets, state each subset and why data are missing. Report unavailable or incomparable cost, token, or timing observations as unavailable or incomparable. Choose sample counts, pass percentages, and CI thresholds for the question and risk.

Compare required behavior first. Treat code size, dependency count, and maintenance surface as contextual proxies for a named goal. Report tokens, cost, and latency only when the observed accounting and execution conditions are comparable, including relevant setup or instruction overhead. Measure implementation size and run cost independently of answer length.

When cost, elapsed time, or repeated labor is in scope, compare the accepted result of the complete task across every round that produced it. Record host facts that distinguish create, continue, and reconstruct; classify each according to the host operation. Count incremental usage once, including recovered historical usage only for distinct rounds. Establish prefix-cache behavior and savings from direct evidence, and assess reuse against the task objective.

## Reporting and Claim Limits

Keep the report proportional to the decision. Include the question, comparator and content revisions, task/fixture and model/host conditions, isolation and activation evidence, acceptance results, attempt accounting, comparable measures, and remaining uncertainty. Preserve enough evidence for a reviewer to trace each material conclusion, subject to approved data handling; no new ledger or result schema is required.

Separate measured facts from inference and judgment. Report observed numerators, denominators, tasks, models, revisions, and limitations. Bound adversarial-case conclusions to the cases exercised.

Estimate per-repository savings from an actual controlled comparator. Identify published benchmarks from other tasks or environments as external evidence. Report convergence, no measurable benefit, and insufficient evidence when observed, and decide whether to retain a Skill rule on the available evidence.
