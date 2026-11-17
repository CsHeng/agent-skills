# Automation Sourcing And Driver Evaluation

Read this when a protected boundary needs UI, device, browser, or system-level automation machinery: choosing it for a new project, re-evaluating it, or noticing that project test code has started to implement generic driving mechanisms. It covers what to source from existing tools, how to compose them by layer, and a repeatable way to compare candidates. The economic comparison itself follows `references/dependency-selection.md` in `development-standards` and `references/architecture-decision-economics.md` in `architecture-patterns`; tool names, versions, and results belong to the project's records.

## Contents

- [Compose By Layer](#compose-by-layer)
- [Locator Order](#locator-order)
- [What To Source And What To Own](#what-to-source-and-what-to-own)
- [Candidate Evaluation](#candidate-evaluation)
- [Agent-Judged Checks](#agent-judged-checks)
- [Emulators, Hardware, And Personal Devices](#emulators-hardware-and-personal-devices)

## Compose By Layer

Expect a combination. No single tool observes every boundary, so choose per layer, and give each layer a fallback and the condition that triggers it.

| Layer | Typical evidence | Cannot see |
| --- | --- | --- |
| In-process or headless model of the UI | State, navigation, logical focus, component wiring | Real input delivery, system UI, rendering, media |
| The UI framework's own runner on a real platform | The app's views under platform input and rendering | Other apps, system dialogs, the installed artifact's packaging |
| Black-box driver on the installed artifact | Install, launch, system pickers, input methods, remote or keyboard keys, lifecycle | Domain outcomes such as decoded media or released resources |
| Project-owned domain probes | Media frames, request counts, resource release, protocol state | Whether a user could reach the state through the UI |
| Human or hardware acceptance | Vendor input devices, decoders, perceived quality | Repeatability |

Start from the first-party testing guidance of the selected UI framework or stack, adopt what it covers, and add the next layer only for a boundary the layer below cannot observe. Read that guidance at the project's pinned version and reread it on every upgrade. Record a framework gap as a dated observation tied to a version; young frameworks change quickly, and an old gap is not a durable limit.

## Locator Order

Prefer, in order: the framework's semantic model and test identifiers, the platform accessibility tree, then vision.

- A missing identifier, label, or role is a testability defect in the product. Fix it at the source; the same metadata serves assistive technology. Test-side workarounds keep the cost and hide the gap.
- Use vision for surfaces that expose no semantics, such as custom-drawn views, and for properties the tree does not carry, such as a visual focus highlight. Give each visual assertion a reviewed baseline or an explicit rubric.
- Check what the tree actually reports before relying on it. Logical focus held by the framework may not appear as platform focus, and nodes under an overlay can remain present; scope selectors to the active layer.
- Coordinates are a last resort and are never recorded as the durable form of a step.

Exploration and regression are different jobs. Let an agent explore with snapshots or vision to find the path, then codify the confirmed path as a deterministic script with semantic selectors and explicit waits. The codified script runs without model judgment.

A dispatched action is not an outcome. Follow each action with a wait or assertion on observable state; a driver can report a tap that the target ignored. When that happens, send the same action through a raw platform input event and through the accessibility action: if those work, the fault lies in the driver backend's injection path, so try another backend before changing the product.

## What To Source And What To Own

Source generic mechanisms from an existing tool: device selection and claims, element location, input injection (pointer tool type, input methods, remote and keyboard keys), settling and waiting, capture, and session cleanup. Own what carries the product's meaning: scenarios, fixtures, domain probes and their oracles, thin adapters, and the evidence policy.

Treat these as a signal to stop and evaluate sourcing: project test code parses a view hierarchy, injects raw input events, manages an input method, or patches a platform input quirk. Each is a mechanism a driver already maintains across OS versions.

Bespoke code remains right where available tools fail a concrete requirement; keep it narrow and state the gap.

## Candidate Evaluation

Run this when selecting machinery, and rerun it on a trigger: a framework or driver major upgrade, a new target platform, recurring flakiness, or growing bespoke driver code.

1. **Candidates.** Compare the status quo, the first-party option, one or two established tools, and one agent-first tool. Pin every version. Install project-locally first and promote a tool to shared tooling only after sustained use.
2. **Probe paths.** Choose two or three real paths that expose differences, not the happy path: a cross-app system surface, non-ASCII or input-method text, non-pointer input, a lifecycle transition. Assert with semantic identifiers and visible text.
3. **Criteria, in priority order.**
   1. It proves the needed boundary on each target carrier.
   2. Its result is trustworthy: the path fails on a build with the known defect and passes on the repaired build; count actions reported as successful that had no effect.
   3. The codified path replays without a model and exits non-zero on failure.
   4. Agent cost: latency and size of observing the screen, whether errors name the next step, a stable command-line surface, authoring and repair speed.
   5. Failure artifacts are retained automatically: screenshot, hierarchy, logs.
   6. Residue on the device and host: helper apps, changed input method, background processes.
   7. Maintenance: version pinning, release cadence and response to OS releases, platform coverage, license and hosted-service lock-in, and exit cost such as export to a common format.

   Agent-friendliness matters increasingly as agents author and maintain checks; it ranks after the first three criteria because a fast tool that cannot prove the boundary or reports false success protects nothing.
4. **Record.** Keep the probe flows and the commands in the project so the comparison can be rerun. Record each run as a dated entry with versions, carriers, per-criterion results, and what was not covered; append new entries.
5. **Decide a combination.** Name the choice per layer, the fallback, the conditions that would change it, and the evidence still missing. A single run supports a direction; migration of an existing suite waits for repeated-run stability on the paths that matter.

## Agent-Judged Checks

A check whose pass or fail is decided by a model at run time is its own class. It tolerates UI change and is quick to write; an ambiguous instruction can also pass when the behavior is wrong.

- Prove each such check can fail before trusting its pass: break the behavior deliberately and confirm the failure.
- Phrase verification so it cannot be satisfied by performing the action.
- Use it for exploration, smoke coverage, and properties without a semantic handle. Keep a deterministic oracle as the regression gate for required behavior.
- Record the model, instructions, and device conditions with the result.

## Emulators, Hardware, And Personal Devices

Emulators and simulators prove the interaction layer: layout, focus movement, key handling, lifecycle. Hardware proves the input delivery chain, vendor key interception, decoders, and vendor system surfaces. Record them as separate results; an emulator pass does not close a hardware requirement.

On a device that holds a person's data, run only flows that preserve it, restore every setting the run changed, and remove helper apps the tools installed. Flows that clear app state run on emulators or dedicated devices. On a desktop host that also runs the person's own install, give the test build a distinct application identity so its state lives apart; an environment override the app may ignore is not isolation, so verify where the test build writes.

Host permissions and security settings a driver needs, such as accessibility access, screen capture, or UI-automation authorization, are preconditions the machine owner grants. Record each one in the project's setup documentation with what fails without it, and do not change it from a script.

Treat device preconditions, such as keeping the screen awake while a flow runs, as state changes with an owner:

- State the precondition as the outcome the run needs, such as "the screen stays on while the run lasts", not as a target value. When it already holds, leave the setting untouched; otherwise add only what is missing, and never weaken or reset the owner's choice.
- Read the original value before changing it and persist it outside the run's process, so a run killed before its exit handler can be restored by the next start or an explicit recovery command. An exit handler alone does not run on a forced kill or a host crash.
- Restore on exit, read the value back, and remove the record only after the read matches.
- A current value that is neither the original nor the run's temporary value was changed by someone else; keep it and report it.
- Never infer the original from a platform default or from a later reading. When no record establishes it, ask the device owner.
- Hold one claim per device and setting; a second run on the same device refuses rather than recording the first run's temporary value as its original.
- Before blaming a driver for a changed setting, check whether the driver itself writes it; record the result with the driver evaluation.
