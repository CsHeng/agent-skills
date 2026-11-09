# Ad Hoc Command Composition

Read this for temporary task execution that nests interpreters, needs procedural logic, or mutates state; the language of persisted repository tools belongs to `shell-guidelines` and language selection.

## Preference Order

1. Run one purpose-built command directly.
2. Use a structured tool such as `rg`, `fd`, `jq`, `yq`, or `ast-grep`.
3. Use a small single-layer Shell pipeline whose data flow stays visible.
4. Put procedural logic in a repo-external scratch script, review and syntax-check it, then invoke it directly.
5. Use a nested interpreter only when the preceding forms are materially worse for the bounded task and the exact command, inputs, and effects stay reviewable.

A scratch script is the right form when logic needs loops, exception handling, several data structures, non-trivial regular expressions, or more than one quoting layer. Place it in a unique task directory under the declared scratch root or `$TMPDIR` (falling back to `$HOME/tmp` for agent-owned work), write it with the environment's file-editing capability, run the language syntax check, and remove owned scratch after the task.

## Safety

- Ad hoc Shell complies with the `shell-guidelines` language constraints.
- Pass variable data through arguments, standard input, environment variables, or structured files; keep code static and data separate to preserve the executable source boundary for untrusted input.
- Destructive operations (mass edits, deletes, resets) run under matching authority with an understood, scoped impact; a sufficient current request or approved plan supplies that scope.
- When one mutation must span nested language layers, make inner-layer failure propagate to the outer layer and verify the post-mutation state explicitly.

## Mutation Workflow

For a multi-file, remote, destructive, or otherwise irreversible operation, establish the target set and recovery boundary before executing; a read or a clearly bounded single-file edit needs none of this.

1. Count the candidate set without mutation.
2. Preview representative and boundary cases.
3. Validate the active repository, host, and path.
4. Identify backup, idempotency, and recovery behavior; guarded rollback applies only when explicitly authorized.
5. Execute with the simplest reviewable command shape.
6. Verify the resulting state independently.

When the target set or recovery path cannot be made explicit, stop and surface the uncertainty.
