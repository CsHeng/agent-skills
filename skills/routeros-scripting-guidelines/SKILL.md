---
name: routeros-scripting-guidelines
description: "Apply RouterOS v7 scripting language guidance when writing, reviewing, or diagnosing persisted .rsc files, script repository sources, scheduler, Netwatch, PPP or DHCP event bodies, imports, error handling, permissions, or external I/O. Use as a conditional language overlay; the primary workflow retains repository ownership and live-device authority."
---

# RouterOS Scripting Guidelines

Apply RouterOS language and execution semantics inside the active primary workflow. Verify syntax and version-specific behavior against the current [MikroTik Scripting manual](https://manual.mikrotik.com/docs/developer-guides/scripting/) and the target version's actual execution context; repository examples show patterns and defer to the manual.

## References

Read only the references needed for the current task:

- For declarations, scopes, variable names, values, arrays, substitutions, functions, and object selection, read [language-and-values.md](references/language-and-values.md).
- For script repository, CLI/import, scheduler, Netwatch, PPP, DHCP, caller permissions, and background execution, read [execution-contexts-and-permissions.md](references/execution-contexts-and-permissions.md).
- For convergence, runtime errors, retries, imports, external I/O, logging, and validation, read [convergence-and-external-io.md](references/convergence-and-external-io.md).

## Working Method

1. Identify the RouterOS version and exact execution context before choosing syntax, built-in variables, or permission assumptions.
2. Separate expected absence or no-op state from a runtime failure, then make the caller-owned failure policy explicit.
3. Validate with the narrowest safe oracle available, escalating from source inspection to import dry-run or live execution when the primary workflow authorizes it. Take the live-device apply path, backup and rollback policy from the primary workflow and repository owner.
4. Keep secrets in the repository or runtime secret mechanism, and diagnose permission errors by caller, invocation form and policy sets first.
