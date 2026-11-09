---
name: lua-guidelines
description: "Apply Lua policy as a conditional overlay when writing or reviewing Lua code, including WezTerm, Hammerspoon, Rime, and Neovim Lua files: style, module boundaries, luac validation, and selene linting. Configuration that contains no Lua code, such as Rime schema or dictionary YAML, does not need it."
---

# Lua Guidelines

Apply these standards to `.lua` files, including those in configuration ecosystems such as WezTerm, Hammerspoon, Rime and Neovim tooling. Language selection reads `references/language-selection.md` in `skills-routing`; ad hoc tool selection and search/refactor workflow read `references/tool-selection.md` there.

## Progressive Disclosure

- Installing the checkers, or choosing a checker for a host runtime: `references/toolchain.md`
- Writing `pcall`/`xpcall` or `(value, err)` code: `references/error-handling.md`

## Rules

- Use `local` for variables and functions, and keep state in `local` variables. Return a module table and keep module state local.
- Structure modules as `local M = {}` ... `return M`.
- Scope `pcall` to a declared-optional import with an explicit fallback, such as `pcall(require, "mod")`.
- Format with `stylua` when available, with its `syntax` set to the target Lua version; validate runtime compatibility separately.
- Validate with a checker that matches the declared target runtime, and state which version ran: `lua-language-server --check` when available, `luac -p path/to/file.lua` or `lua -e 'assert(loadfile("path/to/file.lua"))'` when that Lua matches the target.
- Claim compatibility only for hosts whose Lua version you ran. Validate against the actual LuaJIT or older host before claiming its compatibility.
- Lint with `selene` when available, configured per repository with the target Lua version.
- For generic error-handling patterns, see `error-patterns`.
