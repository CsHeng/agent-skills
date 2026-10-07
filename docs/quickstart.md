# Quickstart

## Install From A Local Checkout

The directories under `skills/` are ready to install. From this repository, list them and explicitly install the selected collection for your agents; this example selects Codex and Pi:

```bash
npx skills@latest add ./skills --list
npx skills@latest add ./skills --global --agent codex pi --skill '*'
```

The CLI copies content into an independent installed location and may link agent discovery paths to that copy. Editing or pulling this checkout does not refresh global Skills. Repeat the local `add` command when you want to install the current checkout contents; local-path installs do not receive remote updates. Keep one active discovery path per tool and public ID. For agents and flags, see the [skills CLI documentation](https://github.com/vercel-labs/skills/blob/main/README.md).

## Remote Installation And Removal

For a remotely tracked installation, use the repository source instead of a local path:

```bash
npx skills@latest add CsHeng/agent-skills --global --agent codex pi --skill '*'
```

Refresh the intended installed IDs with `npx skills@latest update --global <skill-id>`. Reinstallation refreshes an existing Skill's resources; retiring a Skill requires explicit removal with `npx skills@latest remove --global --skill <skill-id>` and the intended agent selection. Check ownership before replacing or removing same-named content, and preserve Skills from other sources. The [install contract](architecture/install-surface.md) explains migration from checkout links and plugin installations.

Optional Claude and Codex plugins have their own explicit installation and update lifecycle. Their discovered content must come from a managed installed copy. `install.sh` and `install-codex.sh` only help register/install those plugins; they are not the general copy/update commands above.

## Choose A Skill

Use an explicitly named or confidently matched Skill directly. Use `skills-routing` when Skill selection or a tool, language, verification, or simplification choice needs guidance. Read only its relevant method reference; it is not a mandatory first stage.

Select `design-change` when an unresolved persisted boundary needs a decision, `plan-change` when an accepted scope needs execution ordering and oracles, and `implement-change` when an explicit bounded mutation request or approved plan is ready. These capabilities may be used independently when their own preconditions are satisfied.

Invoke `review-change` for an explicit bounded review request, an applicable repository or approved-scope rule, or an evidence-backed risk or uncertainty judgment. Review does not manufacture earlier work, and a review evaluator never owns repair.
