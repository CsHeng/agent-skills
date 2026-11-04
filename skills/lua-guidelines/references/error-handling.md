# Lua Protected Calls And Error Propagation

Read this when writing `pcall`/`xpcall` or `(value, err)` code. For generic error-handling patterns (resilience, resource management, monitoring), see `error-patterns`.

Use the protected-call mechanism for operations with a declared fallback, such as an optional module load.

- Scope `pcall`/`xpcall` to operations whose fallback behavior is declared.
- Call required reads, writes and parses directly so failure propagates as a surfaced error or a non-zero exit.
- Call a function returning `(value, err)` directly and keep both values; make any protective wrapper forward every result.
- Check the status and values `pcall` returns.

Example. The only protected call is the declared-optional module load; the required read propagates its failure.

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
