# Debugging Tight Loop

Use this reference for hard bugs, performance regressions, flaky behavior, or repeated runtime failures.

## Gate

Prefer a red-capable feedback loop before hypothesizing. A useful loop is:

- specific to the reported symptom
- deterministic, or high-reproduction for flaky bugs
- fast enough to run repeatedly
- runnable in the current authorized environment

Acceptable loops include a focused test, CLI command with fixture input, curl script, Playwright probe, trace replay, throwaway harness, property/fuzz loop, or bisect command.

If a perfect agent-runnable loop cannot be built, do not freeze unrelated authorized work. Continue with the best available logs, traces, equivalent before-state evidence, or partial reproduction; ask for runtime access, captured artifacts, or permission to add temporary instrumentation for the blocked diagnosis only.

## Workflow

1. Reproduce the symptom with the loop or the best available equivalent evidence.
2. Minimize inputs, config, state, and steps one at a time.
3. Rank falsifiable hypotheses that the current evidence can test. Do not define effort by a fixed hypothesis or test count.
4. Test one hypothesis per probe.
5. Tag temporary instrumentation with a unique prefix and remove it before closeout.
6. Add or preserve a regression check at the correct seam when one exists.
7. Rerun the original loop and the regression check before declaring the bug fixed.

For performance regressions, establish a measurement baseline before changing code or config.
