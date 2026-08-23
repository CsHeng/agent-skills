# Execution Contexts And Permissions

RouterOS syntax is shared across contexts, but built-in variables, caller identity, permissions, timing, and error visibility are not. Confirm the exact context before adapting an example.

## Contexts

| Context | Decision-relevant behavior |
| --- | --- |
| Direct CLI or imported `.rsc` | Each CLI line has its own local scope unless grouped. Import executes file commands and can report multiple parse or runtime errors in verbose dry-run mode. |
| `/system script` repository | The stored script has an owner and policy set. Invocation form determines whether script or caller permissions govern execution. |
| Scheduler | A direct script-name event and an explicit `/system script run ...` form can use different permission semantics. Scheduler policy and the script policy must be reviewed together. |
| Netwatch and traffic events | The event provides its own variables and timing. Treat up/down/test bodies as event code, not as an ordinary interactive shell. |
| PPP, DHCP, and other service hooks | Built-in variables exist only in the documented hook context. Do not reuse them in a system script unless values are passed or captured deliberately. |
| `:execute` background job | The caller does not receive ordinary synchronous completion behavior. Bound concurrency, inspect job behavior when relevant, and make asynchronous failure observable. |

## Built-In Variables

- A context-provided variable does not need a `:local` or `:global` declaration in that context, but using the same name elsewhere may be an undeclared-variable error or a reserved-property conflict.
- Check the owning feature's current manual page for exact built-in names, types, and availability. Do not infer a PPP, DHCP, Netwatch, or scheduler variable from another event system.
- When a reusable system script needs event data, pass it through an explicit, documented boundary or capture only the minimum global state the design actually owns.

## Permission Semantics

The current manual's [Script permissions](https://manual.mikrotik.com/docs/developer-guides/scripting/#script-permissions) section distinguishes script permissions from inherited caller permissions:

- `/system script run <name> use-script-permissions` uses the script permission context.
- A scheduler event that calls a script by name behaves like `use-script-permissions`.
- An explicit `/system script run <name>` without that option can inherit scheduler or caller permissions.
- A script cannot use higher permissions than the invoking user or scheduler is allowed to supply; verify both policy sets and the invocation form when diagnosing `not enough permissions`.

Do not respond to a permission failure by reflexively setting `dont-require-permissions=yes` or broadening policy. First identify the caller, invocation form, script owner, script policy, scheduler or event policy, and exact failing command. Grant only the capability required by the approved owner boundary.

## Timing And Reentrancy

- Scheduler, Netwatch, and service events may overlap a previous run. Use a single-instance guard only when overlapping work would corrupt shared state or create duplicate mutations.
- Keep delays bounded and explain why the event cannot instead react to an observable state transition.
- Background work started with `:execute` needs explicit ownership of completion, errors, and duplicate jobs. Do not equate successful launch with successful completion.
- Event bodies should remain small when a named system script provides a clearer owner, permission set, and review surface; preserve context values explicitly when moving logic.
