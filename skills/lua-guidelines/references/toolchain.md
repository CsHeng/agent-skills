# Lua Toolchain

Read this when installing the Lua checkers or choosing a checker version for a host runtime.

Manage the workstation Lua toolchain with mise:

```toml
# ~/.config/mise/config.toml
[tools]
lua = "latest"
lua-language-server = "latest"
stylua = "latest"
"cargo:selene" = "latest"
```

The `cargo:selene` backend needs a Rust toolchain; mise can provide it (`mise use cargo-binstall@latest`).

The mise-managed `lua`/`luac`, `selene` and `stylua` are workstation tools; the declared host owns the target runtime. Set each checker's Lua version to the declared host (for example `stylua`'s `syntax` setting and `selene`'s configured Lua version), and claim compatibility only for a host whose runtime you ran.
