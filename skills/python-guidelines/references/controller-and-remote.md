# Controller And Remote Execution

Read this when Python crosses a host or controller boundary: a configuration-management module, a remote action, or a script transported to a managed target.

- The controller owns its temporary module execution, such as the Python module Ansible writes and runs on a managed host. Keep Python modules, plugins and collections where the framework owns that ecosystem.
- State the runtime and output contract: interpreter and dependency source, invocation, stdout result and exit behavior.
- A retained Python application uses its declared managed interpreter and environment, or a prebuilt image.
- The choice among built-in modules, shell and Python fragments for a one-shot remote action, and the rule that the controller or CI compiles while the target runs the binary, belong to `references/language-selection.md` in `skills-routing`.
