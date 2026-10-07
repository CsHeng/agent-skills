# Language Selection

## Purpose

Choose languages that reduce the total cost of implementation, verification, environments, deployment, and maintenance for the owned boundary. Removing a file extension or making every tool use one language is not an outcome by itself. This is a planning policy overlay, not the primary workflow owner or an ad hoc command-selection guide.

## Scope

Use this reference when design or planning introduces:

- a new project, persisted script, CLI, tool, service, or automation surface
- a temporary prototype that is being promoted into maintained repository code
- an approved migration or rewrite that may change implementation language

Do not use this reference for:

- agent ad hoc command composition; use [Tool Selection](tool-selection.md)
- ordinary changes to existing `.py`, `.sh`, `.go`, `.lua`, or other language-owned code
- choosing a search, parsing, formatting, or refactoring utility for the current session

## Preserve Fixed Boundaries

When modifying an existing implementation, preserve its established language and tooling unless the current request or approved design authorizes that migration. A nearby file extension alone does not authorize a rewrite.

An explicitly constrained native runtime is a hard boundary: when the target contract fixes BusyBox ash, POSIX `sh`, or another embedded runtime, retain it and do not introduce Python or Go there. The mere presence of a minimal shell or base image is not such a restriction.

Script length, accumulated state, age, or an embedded language alone does not justify a rewrite. Keep the user's migration objective distinct from the language chosen to achieve it.

Treat recurring runtime or dependency incidents, multi-host or multi-architecture distribution cost, and concurrency or performance constraints as migration signals. Compare the actual cost of retaining the current implementation, repairing its environment, and replacing it; a rewrite can remove a runtime while adding more build, compatibility, or maintenance work. These signals are evidence for design, not automatic rewrite permission.

## Choose By Role And Cost

Use Shell for:

- short, linear orchestration and glue
- environment discovery, bootstrap, or delegation to existing CLIs
- simple pipelines whose complete control flow remains easy to audit
- constrained native runtimes where only BusyBox ash or POSIX `sh` exists and no new runtime may be installed
- scripts that must affect the invoking shell, such as a sourced environment or profile, directory change, or exported variable
- simple scripts that grow longer; size or accumulated state alone is not a rewrite signal

Prefer Go when its delivery or runtime benefits reduce the total cost of:

- long-lived operational CLIs and tools whose distribution benefits from a single binary
- self-owned developer, CI, and controller tooling
- API or network services, exporters, collectors, controllers, and concurrent agents
- cross-host or cross-platform tools where runtime and dependency state should stay small
- cross-platform targets built once on a controller or CI runner and delivered as a binary or image
- maintained operational tools that benefit from compiled delivery; stable flags, exit codes, or tests alone do not make Go necessary

Use Python when:

- an existing Python project or provider SDK owns the integration boundary
- a Python ecosystem materially reduces implementation risk, such as data processing, scientific or media libraries, or a configuration-management controller collection
- a bounded batch, migration, audit, test, or configuration transformation is simpler with Python and its available runtime, standard library, or established test infrastructure
- short embedded or transported glue is clearer in Python than in Shell and the execution host already provides the needed interpreter and dependencies

Use Lua when:

- extending an existing Lua codebase or Lua-based configuration ecosystem such as WezTerm, Hammerspoon, Rime, or Neovim
- PROHIBITED: introducing Lua as general-purpose automation when another established project language owns the boundary

These are preferences, not global mandates. Repository-local architecture and runtime contracts take precedence. Production implementation and verification are separate language choices: Python tests or fixture generators can remain the simplest way to verify a Go or Shell product without putting Python on its production targets.

## Define Hybrid Ownership

When a persisted implementation uses multiple languages:

- Shell owns environment discovery and orchestration, together with validation of its own launcher inputs: argument presence and shape, environment variables it dereferences, and paths it resolves.
- The selected primary implementation owns domain parsing, state, and business rules; a launcher must not re-implement or duplicate those checks.
- Do not split one business rule across multiple languages.
- Keep language boundaries callable and testable without relying on generated command strings.
- The controller or CI host owns target-platform compilation and distribution; the target only runs the delivered artifact unless its own native runtime is the approved implementation.

Ad hoc command composition never requires this language-planning gate; use [Tool Selection](tool-selection.md) for those choices.

## Controller, CI, And Remote Placement

Decide where the code runs before choosing its language:

- A configuration-management controller's temporary module mechanism, such as the Python module Ansible generates and executes on a managed host, belongs to the controller. Use it as provided; do not vendor, reimplement, or treat it as this project's Python product.
- Local controller helpers follow the ordinary Go and Python cost comparison above. A long lifetime alone does not justify replacing a working helper.
- For one-shot remote glue, reuse the controller's built-in modules, local rendering, thin transported Shell, or a short Python fragment using the target's existing runtime. Choose the clearest adequate mechanism; do not create a new binary, package, or service merely to carry one action.
- For a persistent or high-frequency tool selected for Go, build for the target OS and architecture on the controller or CI and distribute the binary or image. The managed execution target must not need Go source, a compiler, module downloads, or `go run`. A retained Python tool follows its explicit interpreter/dependency contract, and a constrained target keeps its native runtime. A remote development or CI host explicitly owning the build is a controller, not that managed execution target.

Check actual incremental cost: an interpreter already required by Ansible, a new binary per tiny helper, repeated build-and-run wrappers, or external-command latency can change the benefit. Fix environment and scratch placement directly when that satisfies the goal; checkout contamination alone does not establish that a language rewrite is cheaper. Standard cache locations do not prevent a program's own writes.

## Migration And Verification

Explain a material language choice and its cost tradeoff in the task's existing design or plan when one is needed; do not require a new artifact or placeholder language metadata for an ordinary edit.

For an approved migration, update affected callers, documentation, and runtime dependencies while preserving the behavior consumers need. Existing Python tests, fixture generators, or independent reference implementations do not have to migrate with Go production code. Keep them when they remain useful at an acceptable verification cost; remove obsolete dependencies when their last real consumer is retired. An explicit requirement to remove a verification runtime still binds, but a production-runtime goal does not imply it.

Preserve supported inputs, outputs, persisted formats, and failure behavior that actual consumers or explicit contracts depend on. Do not automatically reproduce every old library behavior, such as argparse abbreviations, help wrapping, PyYAML's full scalar semantics, or incidental JSON ordering and number spelling. Byte compatibility needs a consumer that depends on those bytes, such as a retained signed record. A differential mismatch reveals a difference to assess; it does not make the old implementation's entire behavior a requirement or justify building a general compatibility layer for it.

When the choice depends on an interpreter or controller runtime, record its runtime and output contract: interpreter and dependency source, invocation, stdout result, and exit behavior.
