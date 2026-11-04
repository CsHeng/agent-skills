# Environment Scope And Temporary Storage

Read this when a change touches tool or project environment inputs, caches, disposable scratch, or where a task's temporary files live. Language, tool, and workflow guidance adds only concrete mappings and exceptions to these rules.

## Environment Scope

- Classify an environment input by ownership, shareability, and lifetime before choosing its location; a language, tool, or variable prefix does not decide its scope. Mutable state belongs to the project, subproject, or checkout that owns it, even when a shared cache also participates.
- Downloaded packages, compiled module caches, and bytecode caches may be shared or user-global; dependency environments, test state, generated artifacts, and coverage data stay with the owning project, subproject, or checkout.
- Enter the owning project context before running project commands: resolve the nearest owning project or subproject and run from its root or through an explicit project selector. An interpreter or tool found on `PATH` does not make the current directory or a global environment the owner.
- A user-global tool configuration may provide reusable caches and developer preferences; a project remains correct and reproducible without it, with project-owned configuration overriding or encapsulating those defaults.
- Apply run or task overrides after project defaults so they change only the current run's disposable state. An override that redirects retained project state is a deliberate, task-owned choice.
- Changing directory, invoking a launcher or version manager, or starting a subshell changes context and leaves inherited variables in place; reset or replace only the variables the new context owns.
- Keep reproducible project defaults in project-owned committed configuration, with local overrides under the project's declared ownership rules. Instruction files such as `AGENTS.md` navigate to the owning settings rather than copying them.
- Keep credentials, secrets, and per-user preferences with the user or host, outside project configuration and shared caches.

## Temporary Storage

- Treat `TMPDIR` as the standard temporary-directory root consumed by `mktemp` and supporting tools. A development environment may set it per repository group to an absolute disk-backed path such as `$HOME/tmp/<group>` through mise; without a declared root, agent-owned ad hoc scratch falls back to `$HOME/tmp`. Create the root before use and use unique task directories beneath it.
- Honor explicit repository output locations and language- or tool-specific directory settings. Python environments, Go build and module caches, and other reusable caches keep their own semantics; `TMPDIR` relocates neither them nor intermediate build files.
- Keep large clones, downloads, extraction, build intermediates, and test data on verified disk-backed storage; `/tmp` may be tmpfs and consume RAM. Portable project tools respect `TMPDIR` through their native temporary-file API and may keep the platform default when it is unset; runtime code keeps no developer home path, and legitimate target-system `/tmp` paths stay as written.
- Keep task scratch, reusable caches, and retained evidence distinguishable beneath their declared roots. Clean only owned inactive scratch. Environment changes reach newly launched consumers only, and controller settings do not propagate through SSH, sudo, containers, or services by themselves.
