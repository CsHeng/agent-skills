# Language Selection

## Purpose

Choose languages by execution scenario and the total cost of implementation, verification, environments, deployment, and maintenance.

## Respect Execution Constraints

An explicitly constrained native runtime is a hard boundary: when the target contract fixes BusyBox ash, POSIX `sh`, or another embedded runtime, use it and do not introduce Python or Go there. The mere presence of a minimal shell or base image is not such a restriction.

On resource-limited devices, account for available flash/NAND and RAM before adding an interpreter, package environment, installer, cache, or binary. Do not install Python or uv merely to enable glue on a target that does not already provide the required runtime. A controller's disk budget or a clean checkout does not establish that the target can afford the delivered footprint.

## Choose By Role

Prefer accumulating reusable Go implementations and tooling over introducing Python runtime environments. Choose between Shell and Go by the actual scenario and complexity; Python has only the standard-library glue and required-ecosystem roles below. This is a strategic preference, not language neutrality or a requirement to benchmark every Go tool.

Prefer Go for:

- developer, CI, controller, and operational tools with maintained logic beyond native command orchestration
- reusable parsing, state, and business logic that should serve both source-local development and built delivery
- daemons, APIs, exporters, collectors, concurrent agents, and image-contained services, where performance, memory, storage, and runtime dependency management are first-order concerns

Do not select Python for a general-purpose API, daemon, or other persistent service. A service inseparably tied to a required Python ecosystem is the exception, not an alternative merely because Python can implement the same API. Go's development-to-production path can use the same implementation through `go run` during development and a built binary or image in production.

Use Shell when the work fundamentally belongs to the native command or scripting ecosystem:

- GNU or other existing CLI composition, pipelines, bootstrap, environment discovery, and small hooks
- orchestration whose meaningful work remains in tools such as curl, ssh, kubectl, or native file utilities
- constrained native runtimes where only BusyBox ash or POSIX `sh` exists and no new runtime may be installed
- code that must affect the invoking shell, such as a sourced environment or profile, directory change, or exported variable

This Shell boundary applies on development and managed hosts, subject to their runtime contracts. Length, some branching, JSON, or a small amount of state does not make native orchestration a Go product.

Use Python only for:

- bounded standard-library glue using an interpreter already provided by the system or framework, typically alongside Shell in development, controller work, or one-shot framework-managed execution
- a required Python ecosystem, such as Ansible modules/plugins or pandas/scientific libraries, where the required capability or integration cannot reasonably be supplied through Shell/Go

For standard-library glue, confirm the required interpreter version is actually present and do not add third-party packages. The mere availability of Python on a production host does not make it a suitable general-purpose service runtime. For an ecosystem exception, identify the required capability or framework contract; ordinary HTTP, JSON, YAML, CLI packages, or the convenience of an available SDK do not qualify.

Outside those two roles, select Shell or Go rather than a Python package environment. When a helper needs third-party Python libraries, carefully evaluate implementing it in Go instead; Shell plus `go run` is appropriate if Shell retains genuine native orchestration. The development-to-production environment and distribution costs are sufficient reasons for this preference without a speed benchmark.

uv, venv, pyenv, and similar mechanisms manage a Python environment; they do not remove the installer, interpreter/version, dependency installation, storage, bootstrap, or target-runtime obligations. Moving caches outside a checkout avoids pollution, not those costs. Existing Python environment, cache, and verification guidance remains useful wherever Python is in use, but it is not an additional reason to select Python. Do not create Shell wrappers merely to install or activate such environments.

Account for target-specific builds, artifact updates, edit-to-run friction, and remaining native commands. Go usually moves module dependency resolution into development/build rather than a target interpreter environment; still verify CGO, dynamic libraries, external tools, and assets instead of claiming every Go binary is dependency-free. Neither minimizing language count nor eliminating Python is an independent goal unless explicitly required.

Use Lua when:

- extending an existing Lua codebase or Lua-based configuration ecosystem such as WezTerm, Hammerspoon, Rime, or Neovim
- PROHIBITED: introducing Lua as general-purpose automation when another established project language owns the boundary

Explicit repository architecture and runtime contracts take precedence. Production and verification have separate execution environments: a controller-side interpreter or test dependency is not automatically a production-target dependency.

## Define Hybrid Ownership

A language boundary needs useful work to own; it is not a reason to add a launcher. Prefer direct invocation when the primary implementation or an existing task entrypoint already handles the requirement. Shell plus `go run` is appropriate when Shell retains actual native orchestration and Go owns the structured logic; a wrapper whose only purpose is to build and launch that logic is not the same benefit. Count invocation, build, and distribution work rather than treating language count alone as the measure of simplicity.

When multiple languages are justified:

- Shell retains necessary parent-shell effects, native orchestration, or bootstrap, and validates only its own inputs and resolved paths.
- The selected primary implementation owns domain parsing, state, and business rules; a launcher must not re-implement or duplicate those checks.
- Do not split one business rule across multiple languages or move native Shell behavior into Go only to call Shell again to reproduce it.
- Keep language boundaries callable and testable without relying on generated command strings.
- When binary delivery is selected, the controller or CI host owns target-platform compilation and distribution; the managed target runs the delivered artifact.

## Controller, CI, And Remote Placement

Decide where the code runs before choosing its language:

- A configuration-management controller's temporary module mechanism, such as the Python module Ansible generates and executes on a managed host, belongs to the controller. Use it as provided; do not vendor, reimplement, or treat it as this project's Python product.
- Controller helpers follow the Go default, native-Shell boundary, and standard-library Python glue exception above.
- For one-shot remote glue, reuse framework-native modules, Shell, or Python under the established interpreter contract. If the owned helper requires third-party Python dependencies, carefully evaluate implementing it in Go rather than expanding the target's Python environment. Distinguish that helper from the framework's own native module/runtime implementation.
- For a persistent or high-frequency tool selected for Go, build for the target OS and architecture on the controller or CI and distribute the binary or image. The managed execution target must not need Go source, a compiler, module downloads, or `go run`. A retained Python tool follows its explicit interpreter/dependency contract, and a constrained target keeps its native runtime. A remote development or CI host explicitly owning the build is a controller, not that managed execution target.

## Choose Invocation And Delivery Separately

Selecting Go does not require a new Shell launcher or a distributed binary for a source-local tool. On a developer, CI, or controller host that already owns the Go toolchain and source, prefer direct `go run ./cmd/tool` or the existing task entrypoint when compile-and-execute meets the consumer contract. Go manages module/build caches; do not create a private build-and-delete lifecycle for each command merely to avoid an implicit output binary in the checkout.

Use an explicit build when a consumer needs a reusable executable path, a release artifact, lower repeated startup cost, or process/exit/signal behavior that the `go run` driver cannot satisfy. `go run` is not identical to executing the resulting binary: cache reuse does not eliminate driver/startup overhead or guarantee the program's exact exit status and process behavior. Verify the boundary that matters rather than mechanically replacing every `go build` with `go run`. Prebuilt delivery remains required for managed or production execution targets that do not own the build role.

If setup or lifecycle ownership really needs a wrapper, reuse the existing entrypoint and keep only that necessary work there; do not introduce a shared launcher framework merely to make an unnecessary boundary cheaper. Fix environment and scratch placement directly when that satisfies the goal. Standard cache locations do not prevent a program's own writes.

## Cost And Verification

Explain the language choice through the execution environment, required capabilities, invocation and delivery, and total maintenance cost.

When speed, memory, or disk savings decide the choice, use representative end-to-end evidence rather than language reputation or a binary-only comparison. Include cold and warm invocation where relevant, the compiler/driver and child processes actually launched, incremental toolchain/runtime and cache/artifact storage, and the commands that dominate elapsed time. Reuse credible existing evidence and keep probes proportional; no universal benchmark suite is required. Without evidence of the claimed benefit, do not justify extra mechanisms as an optimization.

When the choice depends on an interpreter or controller runtime, record its runtime and output contract: interpreter and dependency source, invocation, stdout result, and exit behavior.
