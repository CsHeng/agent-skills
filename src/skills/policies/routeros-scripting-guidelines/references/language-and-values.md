# Language And Values

Use the current MikroTik [Scripting manual](https://manual.mikrotik.com/docs/developer-guides/scripting/) as the syntax authority.

## Lines And Scopes

- RouterOS executes command lines sequentially until the script ends or an uncaught runtime error stops it. A semicolon or newline terminates an ordinary command; braces, brackets, and parentheses establish blocks, command substitution, and expression grouping.
- Global scope is the script root. A block in braces creates local scope, and a local declaration is visible only after its declaration point inside that block and nested blocks.
- Except for context-provided built-in variables, declare every variable with `:local` or `:global` before use. Redeclare a global without a value when another script created it and the current scope needs access.
- Prefer `:local` unless state intentionally crosses executions or scripts. Treat global names and values as shared mutable state owned by the current RouterOS user.

## Variable Names

Follow the official definition rather than adding a project naming law:

- Ordinary unquoted variable names contain letters and digits. A name containing another character must be quoted according to RouterOS syntax.
- Names are case-sensitive.
- Built-in RouterOS property names are reserved and can conflict with user variables; choose a distinct name.
- The manual commonly uses names such as `myVar`. camelCase is a readable ordinary choice, not a universal requirement.

## Types And Values

- RouterOS values include `num`, `bool`, `str`, `ip`, `ip-prefix`, `ip6`, `ip6-prefix`, internal `id`, `time`, `array`, and `nil`.
- An uninitialized variable has type `nil`. Use `:typeof` when behavior depends on the actual runtime type and use explicit conversion commands when input shape is uncertain.
- Preserve IP and prefix types when using membership, bitwise, or routing expressions; do not assume every printed value is a plain string.
- Quote strings deliberately and account for RouterOS escape and interpolation rules. Use concatenation or expression substitution when interpolation would be ambiguous.

## Arrays And Functions

- Arrays can be positional or keyed. Read keyed members with `->`, and do not assume printed ordering is a stable identity.
- `print as-value` returns structured parameter arrays and is generally safer for programmatic reads than parsing aligned terminal text.
- RouterOS functions are values produced by `:parse` or local/global declarations whose body uses `:return`. Declare function parameters in the function's local scope and avoid hidden global dependencies.
- Use `:serialize` and supported conversion commands when structured output is required; verify availability on the target RouterOS version.

## Commands And Object Selection

- Use explicit menu paths when the surrounding context would otherwise make a relative command ambiguous. Nested menu commands may use their inherited path when that improves clarity without changing meaning.
- Select mutable objects by stable properties such as a unique name, comment, address, or other repository-owned identifier. Do not use print row numbers or assumed ordering as durable identity.
- Check the cardinality of `find` results before `get`, `set`, `remove`, or `move` when zero or multiple matches would change behavior.
- Keep expression grouping explicit around arithmetic, concatenation, and nested command substitution when RouterOS could parse the token as an address, path, or another command form.
