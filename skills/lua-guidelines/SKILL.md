---
name: lua-guidelines
description: "Use for Lua code or configuration, including WezTerm, Hammerspoon, Rime, luac validation, selene linting, and Lua review."
---

# Lua Guidelines

## Purpose

Define Lua coding standards for scripts and configuration files: style, module boundaries, and lightweight validation.

## Scope

In-scope:
- Editing or creating Lua files (`.lua`)
- Lua-based configuration ecosystems (for example: WezTerm, Hammerspoon, Rime, Neovim tooling)

Out-of-scope:
- Language selection (see `language-decision-tree` skill)
- Tool selection and search/refactor workflow (see `tool-decision-tree` skill)

## Tool Management

PREFERRED: Use mise to manage the workstation Lua toolchain:
```toml
# ~/.config/mise/config.toml
[tools]
lua = "latest"
lua-language-server = "latest"
stylua = "latest"
"cargo:selene" = "latest"
```

REQUIRED: Ensure Rust toolchain is available for cargo backend (mise can manage: `mise use cargo-binstall@latest`).

NOTE: The mise-managed `lua`/`luac`, `selene`, and `stylua` are workstation tools, not the target runtime. Set each checker's Lua version to the declared host (for example `stylua`'s `syntax` setting and `selene`'s configured Lua version), and do not claim compatibility for a host you cannot run.

## Rules (Hard Constraints)

### Namespace
REQUIRED: Use `local` for variables and functions.
PROHIBITED: Mutate `_G` directly; return a module table instead.

### Module Patterns
REQUIRED: Use `local M = {}` + `return M` for modules.
PREFERRED: Scope `pcall` to declared-optional imports, for example `pcall(require, "mod")` with an explicit fallback.

### Formatting
PREFERRED: Use `stylua` if available and set its `syntax` to the target version; formatting is not runtime validation.

### Validation
REQUIRED: Validate with a checker that matches the declared target runtime, and record which version ran.
PREFERRED: Use `lua-language-server --check` when available for comprehensive diagnostics.
PREFERRED: Use `luac -p path/to/file.lua` when that `luac` matches the target runtime.
PREFERRED: Fallback to `lua -e 'assert(loadfile("path/to/file.lua"))'` when that `lua` matches the target runtime.
NOTE: A pass from a different Lua version (for example workstation Lua against a LuaJIT or older host) is not evidence that the host accepts the file; do not claim compatibility for a host you cannot run.

### Linting
PREFERRED: Use `selene` when available and configure its Lua version to match the target; configure per-repo if needed.

## Checklist

- No unintended globals
- Consistent module return style
- Syntax validated (`lua-language-server --check`, `luac -p`, or `loadfile`) with a checker matching the target runtime
- Lint clean when `selene` is available and configured for the target Lua version

## Error Handling

For generic error handling patterns (resilience, resource management, monitoring), see `error-patterns` skill.

### Protected Calls And Error Propagation

The protected-call mechanism is for genuinely optional operations with a declared fallback, such as an optional module load. It is not a default wrapper around required work.

REQUIRED: Scope `pcall`/`xpcall` to operations whose fallback behavior is declared; do not wrap a required read, write, or parse merely to return `nil`.
REQUIRED: Let required failures propagate visibly (a non-zero exit or a surfaced error); never convert them into a silent `nil`.
REQUIRED: Preserve multiple returns; call a function returning `(value, err)` directly and keep both values, and make any protective wrapper forward every result rather than only the first.
REQUIRED: Handle errors explicitly; do not ignore the status or values returned by `pcall`.

Example. The only protected call here is the declared-optional module load; the required read propagates its failure.
```lua
-- Optional dependency: pcall is scoped to a declared fallback.
local function optional_require(module_name, fallback)
    local ok, result = pcall(require, module_name)
    if not ok then
        return fallback
    end
    return result
end

local json = optional_require("cjson", nil)  -- declared fallback: cjson is not required

-- Required input: failure propagates and (value, err) keeps both returns.
local function read_config(path)
    local handle, err = io.open(path, "r")
    if not handle then
        error(("cannot open config %q: %s"):format(path, err), 2)
    end
    local contents, read_err = handle:read("*a")
    local closed, close_err = handle:close()
    if not contents then
        error(("cannot read config %q: %s"):format(path, read_err or "read returned no data"), 2)
    end
    if not closed then
        error(("cannot close config %q: %s"):format(path, close_err), 2)
    end
    return contents
end
```
