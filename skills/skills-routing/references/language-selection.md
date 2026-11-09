# Language Selection

## Decision Unit And Order

Choose an implementation for the complete user-facing capability: its behavior, entrypoint, dependencies, development loop, delivery, updates, verification, and resource use. Assess simplicity across the complete tool.

Use this decision order for new persisted code and authorized migrations. Use it as reasoning guidance.

```mermaid
flowchart TD
    A[Required behavior and existing user workflow] --> B[Target hardware, OS, architecture and available runtimes]
    B --> C[Exclude infeasible or unaffordable implementations]
    C --> D[Reuse existing platform, framework and command capabilities]
    D --> E{Execution role and delivery model}
    E -->|Production service, scheduled job or image product| P[Prefer Go through the binary or image delivery pipeline]
    E -->|Dotfiles or interactive script workflow| S[Prefer native Shell or provided standard-library Python]
    E -->|Other roles| O[Compare viable implementations and useful combinations]
    P --> F[Count incremental development, dependencies, delivery, updates and resource costs]
    S --> F
    O --> F
    F --> G{Does a change provide a concrete net benefit?}
    G -->|Yes| H[Use the selected ecosystem and verify business behavior and delivery]
    G -->|No| I[Keep the simpler implementation or repair an over-migration]
```

## Establish Target Capabilities First

Determine where the code actually runs, whether that target supports scripts or binaries, its OS/ABI and CPU architecture, available RAM and flash/storage, installed interpreters and native commands, and how code reaches it. Verify these capabilities on the execution target, including OS, runtime, and resource budget.

An explicitly constrained runtime is a hard boundary: retain required BusyBox ash, POSIX `sh`, device scripting, or other native technology. Distinguish ash, Bash and Zsh and their available commands. An incidental base image or available shell does not itself prohibit another implementation.

On constrained targets, count the delivered binary or interpreter, libraries, assets, installer and runtime storage against the actual budget. Use available target capabilities for glue. Selecting Go still requires a supported target and an affordable artifact; compiled delivery is not evidence of fit by itself.

Existing repository architecture and runtime contracts apply within the user's current authorized objective. A reassessment may correct model-derived language assignments and deployment mechanisms; preserve actual hardware, behavior and safety requirements established by the target and consumers.

## Choose By Business Role And Incremental Burden

First reuse an existing platform capability, framework module or native command that already owns the work. A helper invoked by a framework is not automatically part of that framework's required language ecosystem.

For dotfiles, interactive helpers, hooks and similar script-oriented tools, prefer Shell, an already-provided Python interpreter using only its standard library, or a simple combination of the two when they satisfy the behavior clearly and reliably. Choose between them by the actual logic and available commands. The normal edit, sync and invocation workflow is part of their value; Go must offer enough benefit to justify compilation and delivery. Apply this preference to its stated script-oriented context.

Use Shell for native command composition, pipelines, bootstrap, environment discovery, parent-shell effects and script-oriented work that remains clear with available tools. Length, branching, JSON, HTTP or a small amount of state does not independently justify a Go implementation. Use a suitable higher-level implementation when Shell parsing would be fragile.

Use standard-library Python for bounded script logic when the compatible interpreter is already provided on the actual execution target. It may be a named script or embedded in Shell; neither shape makes an absent interpreter available. Keep this role on the provided standard library.

Prefer Go for maintained production services, scheduled jobs and self-owned business logic shipped in an image or binary, subject to the target capabilities and required ecosystem integration. An existing build and artifact delivery pipeline usually makes compilation a normal product cost; apply the production delivery model to that runtime. Count incremental dependencies and delivery work. Short-lived jobs can share this production preference according to their delivery role.

For other maintained domain tools, Go's runtime, reuse and delivery advantages must fit the actual role. Reusable parsing and state logic can support that choice, but JSON, HTTP or state alone does not. Calling native tools from Go is appropriate when those tools own a required capability; ordinary orchestration or startup Shell can remain when useful. Production Go need not reimplement native system tools or every entrypoint in Go.

Select third-party Python only when a specific library or framework is the right match for the required business capability and that capability or integration is available only through Python. Identify the capability and why the viable Shell/Go choices cannot supply it. Library familiarity, an available SDK, or routine HTTP, JSON or YAML processing is not sufficient. Otherwise prefer Go over creating and maintaining a Python package environment, after considering whether existing native tools already suffice. This preference concerns the environment and delivery burden.

Preserve required Python framework execution under its established contract. Ansible's generated modules and Python-only framework integration are framework capabilities to preserve. Justify another Python application by its required capability. uv, venv and pyenv manage environment costs; account for interpreter compatibility, installation, updates, isolation, image size and storage obligations.

Use Lua for an existing Lua implementation or configuration ecosystem. Use the established project language for general-purpose automation when it owns that boundary. Other constrained targets follow their actual native technology.

## Keep Combined Implementations One Usable Tool

Shell plus standard-library Python and Shell plus a delivered binary are useful combinations when each part reduces the complete implementation's burden. Shell may own the stable user entrypoint, locate its co-delivered implementation, pass inputs, or retain native orchestration and parent-shell effects. Preserving that entrypoint can be useful even when Shell owns no business logic. Keep domain rules in one implementation.

For a tool expected to work after its normal copy, sync or install operation, deliver and update the entrypoint and its implementation together. Deliver the helper, path configuration, and compatible versions as a usable unit when the implementation language changes. Self-contained delivery means usable under its declared system prerequisites. A binary can satisfy it when the existing delivery mechanism actually carries the correct artifact and required assets.

Count development-to-deployment differences, compilation, platform builds, native commands, CGO/dynamic libraries, artifact size and updates. A binary may move dependencies to the build host but does not automatically remove all runtime dependencies. Keep launchers, private build/cache lifecycles, and distribution mechanisms tied to a necessary delivery boundary. Reuse the existing entrypoint and delivery mechanism when they suffice.

The controller or CI owns compilation for managed execution targets; deliver the target-compatible binary or image with its required runtime assets. A host explicitly owning development/build work is a different execution role. One-shot remote work should reuse framework modules, native Shell or standard-library Python under an established interpreter contract before introducing another maintained product.

## Reassess Migrations Against The Original Outcome

For an authorized reassessment, start from the business capabilities actually changed, including original Shell and embedded scripts. Compare the earlier implementation, the current complete tool and the simplest viable correction. A remaining-Python inventory misses unnecessary Go implementations and costs introduced by the migration itself.

Separate a language decision from the quality of its implementation. When production or image delivery justifies Go, compare completing the current Go design, reusing suitable Go packages and replacing the flawed implementation before concluding that the language should change. Re-select parsing, serialization and other libraries for the business contract in the target ecosystem; preserve the business contract across the translation. Assess a suitable compiled dependency's own build, update and runtime costs separately from a Python package's interpreter and environment burden.

Audit supporting machinery as well as top-level commands: migration-created file utilities, path handling, syntax analysis, coercion, transport and compatibility helpers can carry most of the unnecessary cost. Trace each suspect responsibility to its consumers and domain tests, then compare existing project capabilities, the target standard library and suitable mature packages before retaining custom code. Use language-prefixed names and generic utility files as discovery clues; genuine source-language analysis or required protocol encoding may need a narrow adapter. Reduce the responsibility or replace its implementation. A mature library owns general mechanics; the product still owns its business decisions and data protections.

Choose retention, a small repair, a replacement within the selected language, restoration of the simpler approach, or a useful combination by the user's outcome. Preserve later valid fixes and required data behavior when restoring an approach; review each restored change against current requirements. A migration-created wrapper, interface, compatibility layer or test is not automatically a permanent requirement. Explain the burden removed and introduced; preserving an already-written implementation is not itself a benefit.

Production and verification have separate execution environments. Retain useful tests and fixture generators when changing production language, and classify controller-side test dependencies separately from target runtime dependencies. Reassess what those tests assert: derive scenarios and expected results from business rules, actual consumers and retained data. Keep exact serialization, errors or bytes only where an actual protocol or consumer requires them. Fix environment or scratch placement directly when that solves the actual problem.

## Evidence And Acceptance

Explain material choices using target capabilities, business needs, the existing user workflow and total maintenance cost. Use proportionate evidence. When speed, memory, image size or storage decides the choice, compare representative complete executions and incremental dependencies, including relevant cold/warm behavior, build/runtime caches and artifacts. Code length alone is neither a benefit nor a defect.

Verify the actual entrypoint with the declared delivered files and prerequisites, from a representative working directory and environment. Check useful behavior, outputs and failure handling as well as how users obtain and update the tool. A backend unit test does not establish that the distributed entrypoint is usable. Local delivery simulation can establish this boundary without installing into the user's live environment.
