---
name: routeros-scripting-guidelines
description: "Apply RouterOS v7 scripting language guidance when writing, reviewing, or diagnosing persisted .rsc files, script repository sources, scheduler, Netwatch, PPP or DHCP event bodies, imports, error handling, permissions, or external I/O. Use as a conditional language overlay; the primary workflow retains repository ownership and live-device authority."
---

# RouterOS Scripting Guidelines

Apply RouterOS language and execution semantics inside the active primary workflow. Use the current [MikroTik Scripting manual](https://manual.mikrotik.com/docs/developer-guides/scripting/) as the authority for syntax and version-specific behavior; repository examples may show useful patterns but do not override the manual or become universal rules.

## References

Read only the references needed for the current task:

- For declarations, scopes, variable names, values, arrays, substitutions, functions, and object selection, read [language-and-values.md](references/language-and-values.md).
- For script repository, CLI/import, scheduler, Netwatch, PPP, DHCP, caller permissions, and background execution, read [execution-contexts-and-permissions.md](references/execution-contexts-and-permissions.md).
- For convergence, runtime errors, retries, imports, external I/O, logging, and validation, read [convergence-and-external-io.md](references/convergence-and-external-io.md).

## Working Method

1. Identify the RouterOS version and exact execution context before choosing syntax, built-in variables, or permission assumptions.
2. Declare data in the narrowest useful scope and select RouterOS objects by stable properties rather than display order.
3. Separate expected absence or no-op state from a runtime failure, then make the caller-owned failure policy explicit.
4. Prefer read-before-write convergence for reusable configuration scripts and bounded error handling for genuinely fallible operations.
5. Validate with the narrowest safe oracle available, escalating from source inspection to import dry-run or live execution only when the primary workflow authorizes it.

## Operating Rules

- Do not copy secrets into scripts, logs, examples, or evidence.
- Do not treat `dont-require-permissions` as a default fix for permission errors.
- Do not invent a generic live-device apply path, backup policy, rollback rule, or network design. The primary workflow and repository owner retain those decisions.
- When current RouterOS behavior differs from remembered syntax or an example, verify the target version against the official manual and the actual execution context.
