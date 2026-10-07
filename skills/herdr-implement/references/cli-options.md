# Native CLI Options

Consult the selected client's current `--help` and installed documentation before launch; they own supported arguments and values. The mappings below were checked on 2026-10-07 with Herdr 0.9.3. They establish argument syntax, not authentication, model availability, effective effort or a successful live handoff.

Use native automatic approval by default. Add model and thinking arguments only when the user supplies those overrides; omission preserves the client's defaults. Translate the option name without substituting a model or changing the requested effort. Do not edit persistent client configuration to force an unsupported option, introduce a generic permission API or treat automatic approval as authority for unrelated work.

| Requested agent / checked version | Herdr `--kind` | Default native arguments | Optional model | Optional thinking |
| --- | --- | --- | --- | --- |
| `pi` / 1.0.4 | `pi` | `--approve` | `--model MODEL` | `--thinking LEVEL` |
| `codex` / 0.160.1 | `codex` | `--dangerously-bypass-approvals-and-sandbox` | `--model MODEL` | `-c 'model_reasoning_effort="LEVEL"'` |
| `claude` / 2.1.292 | `claude` | `--dangerously-skip-permissions` | `--model MODEL` | `--effort LEVEL` |
| `cursor-agent` / 2026.10.01-e373342 | `cursor` | `--force` | `--model MODEL` | For a supported explicit model, `--model 'MODEL[effort=LEVEL]'` replaces the plain model argument. |
| `grok` / 1.0.46 | `grok` | `--always-approve` | `--model MODEL` | `--reasoning-effort LEVEL` |

Pass native arguments after Herdr's `--`, using the actual pane ID returned by Herdr:

```text
herdr agent start <name> --kind <kind> --pane <returned-pane-id> -- <native-arguments>
```

For example, Codex with no overrides receives only `--dangerously-bypass-approvals-and-sandbox`. With an explicit model and `thinking=high`, append `--model MODEL -c 'model_reasoning_effort="high"'`. Quote each model/configuration value as one native argument: the outer single quotes are shell quoting, while the inner TOML double quotes remain part of the Codex configuration argument.

## Client Limits

- **Pi:** Tools already run without per-call approval. `--approve` trusts project-local configuration and resources for this process; it does not bypass extension-defined gates. `--thinking` accepts `off`, `minimal`, `low`, `medium`, `high`, `xhigh` and `max`, overrides a model's thinking suffix, and can clamp to the model's supported level.
- **Codex:** `-c` applies a configuration override for this invocation. Preserve the TOML string value for `model_reasoning_effort` and check the selected model's supported values; an accepted configuration key alone does not demonstrate effective reasoning effort.
- **Claude Code:** Use `--dangerously-skip-permissions`; `--allow-dangerously-skip-permissions` only makes bypass available and does not enable it. The checked help lists `low`, `medium`, `high`, `xhigh` and `max` for `--effort`; availability remains model-dependent.
- **Cursor Agent:** Herdr calls this kind `cursor`, while the user-facing CLI is `cursor-agent`. `--force` still honors explicit deny rules. Native `--trust` and `--approve-mcps` can resolve unattended workspace/MCP startup where needed; `--trust` can persist workspace trust. There is no confirmed standalone thinking option for the implicit default model. For a thinking-only request, resolve a supported model with the user rather than silently choosing one or dropping the requested effort. Preserve any other explicitly supplied model parameters when adding `effort`.
- **Grok:** `--reasoning-effort` applies to reasoning models. Check the selected model's accepted values instead of imposing another client's level list.

If an explicit option is unsupported or startup reports a concrete restriction, report that condition and preserve the requested settings for resolution. Do not silently retry without an override or claim that parsing proves the setting took effect. Keep native subagent selection and permission handling with each main session; this reference does not configure or manage their internal delegation.
