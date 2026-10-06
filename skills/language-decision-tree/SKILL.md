---
name: language-decision-tree
description: "Use during design or planning when a new persisted project, tool, automation surface, service, or approved migration needs an implementation-language decision, including controller, CI, and remote-target tooling. Do not use for agent ad hoc command choice or ordinary edits whose language is already fixed."
---

# Language Decision Tree

## Purpose

Choose the implementation language for a new persisted code boundary before implementation begins. This is a planning policy overlay, not the primary workflow owner or an ad hoc command-selection guide.

## Scope

Use this skill when design or planning introduces:

- a new project, persisted script, CLI, tool, service, or automation surface
- a temporary prototype that is being promoted into maintained repository code
- an approved migration or rewrite that may change implementation language

Do not use this skill for:

- agent ad hoc command composition; use `tool-decision-tree`
- ordinary changes to existing `.py`, `.sh`, `.go`, `.lua`, or other language-owned code
- choosing a search, parsing, formatting, or refactoring utility for the current session

## Step 1: Preserve Fixed Boundaries

When modifying an existing implementation, preserve its established language and tooling unless an approved design changes that boundary. A nearby file extension alone does not authorize a rewrite.

An explicitly constrained native runtime is a hard boundary: when the target contract fixes BusyBox ash, POSIX `sh`, or another embedded runtime, retain it and do not introduce Python or Go there. The mere presence of a minimal shell or base image is not such a restriction.

Script length, accumulated state, or age alone does not authorize a rewrite. Escalation needs both an approved boundary and one of the concrete migration signals below.

Treat recurring runtime or dependency incidents, multi-host or multi-architecture distribution cost, concurrency or performance constraints, and growth from thin orchestration into a maintained operational tool as migration signals. They are evidence for design, not automatic rewrite permission.

## Step 2: Classify The Persisted Implementation

Use Shell for:

- short, linear orchestration and glue
- environment discovery, bootstrap, or delegation to existing CLIs
- simple pipelines whose complete control flow remains easy to audit
- constrained native runtimes where only BusyBox ash or POSIX `sh` exists and no new runtime may be installed
- scripts that must affect the invoking shell, such as a sourced environment or profile, directory change, or exported variable
- simple scripts that grow longer; size or accumulated state alone is not a rewrite signal

Prefer Go for:

- long-lived operational CLIs and tools whose distribution benefits from a single binary
- self-owned developer, CI, and controller tooling, including ordinary host-side helper and test tools
- API or network services, exporters, collectors, controllers, and concurrent agents
- cross-host or cross-platform tools where runtime and dependency state should stay small
- cross-platform targets built once on a controller or CI runner and delivered as a binary or image
- state-changing tools that need stable flags, exit codes, completion, tests, and release artifacts

Use Python when:

- an existing Python project or provider SDK owns the integration boundary
- a Python ecosystem materially reduces implementation risk, such as data processing, scientific or media libraries, or a configuration-management controller collection
- a bounded batch, migration, audit, test, or configuration transformation materially benefits from that Python ecosystem or an existing Python-specific oracle, with an explicit runtime and output contract; being a script or test alone is not a Python-selection reason

Use Lua when:

- extending an existing Lua codebase or Lua-based configuration ecosystem such as WezTerm, Hammerspoon, Rime, or Neovim
- PROHIBITED: introducing Lua as general-purpose automation when another established project language owns the boundary

These are preferences, not global mandates. Repository-local architecture and runtime contracts take precedence.

## Step 3: Define Hybrid Ownership

When a persisted implementation uses multiple languages:

- Shell owns environment discovery and orchestration, together with validation of its own launcher inputs: argument presence and shape, environment variables it dereferences, and paths it resolves.
- The selected primary implementation owns domain parsing, state, and business rules; a launcher must not re-implement or duplicate those checks.
- Do not split one business rule across multiple languages.
- Keep language boundaries callable and testable without relying on generated command strings.
- The controller or CI host owns target-platform compilation and distribution; the target only runs the delivered artifact unless its own native runtime is the approved implementation.

Ad hoc command composition never requires this language-planning gate; use `tool-decision-tree` for those choices.

## Controller, CI, And Remote Placement

Decide where the code runs before choosing its language:

- A configuration-management controller's temporary module mechanism, such as the Python module Ansible generates and executes on a managed host, belongs to the controller. Use it as provided; do not vendor, reimplement, or treat it as this project's Python product.
- Local controller helpers that run on the controller host follow the ordinary Go and Python rules above; prefer Go for a long-lived, self-owned helper.
- Simple one-shot remote glue should prefer the controller's built-in modules, local rendering, or a thin transported Shell command. Do not create a new Go or Python product for one remote action.
- For a persistent or high-frequency tool selected for Go, build for the target OS and architecture on the controller or CI and distribute the binary or image. The managed execution target must not need Go source, a compiler, module downloads, or `go run`. A retained Python tool follows its explicit interpreter/dependency contract, and a constrained target keeps its native runtime. A remote development or CI host explicitly owning the build is a controller, not that managed execution target.

Prefer the language that reduces checkout contamination or materially improves runtime memory, disk, startup, or delivery for the owned boundary. Standard cache locations do not prevent a program's own writes. Check actual incremental cost: an interpreter already required by Ansible, a new binary per tiny helper, or external-command latency can change the benefit. Do not choose a language for purity or uniformity alone.

## Recording

For each new or migrated persisted implementation boundary, record:

- `implementation_archetype`
- `implementation_language`
- `language_rationale`

If a repository-preferred language is not selected, record the hard constraint or ecosystem advantage that controls the decision. Ordinary existing-language tasks do not need placeholder language metadata.

For an approved migration slice, move the implementation together with its related tests, executable fixture generators, callers, documentation, and runtime dependencies in the same batch without weakening the oracle. A temporary differential oracle in the prior language may support the work in progress, but remove that executable dependency before accepting the slice rather than treating it as a permanent generic exception. Preserve inert compatibility fixtures and genuinely ecosystem-specific oracles, keep other unmigrated suites usable, and retire shared helpers only after their last dependent moves.

When the choice depends on an interpreter or controller runtime, record its runtime and output contract: interpreter and dependency source, invocation, stdout result, and exit behavior.
