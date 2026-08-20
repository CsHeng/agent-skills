+++
artifact_kind = "design"
contract_version = 4
approval_status = "approved"
truth_impact = "high"
truth_sync_required = true

[scope]
impl_file_refs = ["AGENTS.md", "README.md", "contracts/install-targets.toml", "docs/architecture/harness-state-machine.md", "docs/architecture/install-surface.md", "docs/architecture/workflow-orchestration.md", "docs/changelog/design-decisions.md", "docs/quickstart.md"]
test_file_refs = ["tests/test_install_target_contracts.py"]
external_impl_file_refs = []
+++
# Design

## Live-Symlink Skill Management

## Problem

The repository currently presents native Claude Code and Codex plugins as its maintained primary distribution paths and presents `npx skills` as the portable path for other agents. That operating model does not fit the primary user of this repository. The upstream CLI copies selected skills into provider-owned directories, so every installation creates another update and removal lifecycle. Native plugin installation adds versioned caches and a second discovery route beside the live `~/.agents/skills` links. Tools such as Grok can then discover the same public ID through both a generic skill root and a provider plugin.

The user instead maintains local Git clones, updates them explicitly with Git, and wants skill content to remain live through symlinks. Claude Code is now an occasional consumer and does not justify a separately maintained active plugin or skill adapter on the current development machine.

## Goals

- Make the generated root-flat `skills/` payload plus user-managed symlinks the recommended local management topology.
- Recommend one symlink per public ID under `~/.agents/skills/`, targeting this repository's generated `skills/<id>/` directories.
- Recommend local Git clones plus `git pull` and symlinks for third-party skill collections instead of copied installations.
- Keep `npx skills` compatible and documented, but clearly mark its copy/update/removal lifecycle as upstream-managed and non-recommended for this repository's primary operating model.
- Retain Claude Code and Codex plugin manifests and installers as optional compatibility surfaces rather than the recommended local path.
- Remove the currently installed `coding@csheng` plugin from Claude Code and Codex on this development machine.
- Prove that Grok sees every skill name once and does not consume Claude skills before exposing the same 39 coding skills to Claude through symlinks.
- After that Grok precondition passes, add one Claude child symlink per coding public ID and prove that Grok still reports no duplicate names.

## Boundaries

`src/skills/` remains authored truth and `skills/` remains the sole generated root-flat payload. The repository does not turn `~/.agents/skills` into authored truth and does not copy generated skills into user directories. A local manager creates or refreshes child symlinks whose targets are `skills/<public-id>/`; editing remains source-first followed by repository generation.

The repository recommends the topology but does not own arbitrary third-party clone locations, run `git pull`, mutate another repository, or automatically delete stale links. Consumers inspect and manage those checkouts and links. The portable payload remains resource-closed so copy-based tools, `npx skills`, and optional provider plugins continue to work.

Plugin manifests, marketplace metadata, validation, and installer scripts remain present for compatibility. They are no longer described as the primary development path. This change removes only the user-installed `coding@csheng` plugins from Claude Code and Codex; it does not remove either marketplace registration, delete plugin source from this repository, uninstall unrelated plugins, or change plugin versions.

The current machine adds Claude coding-skill links only after two preconditions pass: Grok reports no duplicate skill names through the existing `~/.agents/skills` topology, and Grok's resolved configuration keeps Claude skill compatibility disabled plus the `coding` plugin disabled. The change then creates one child symlink under `~/.claude/skills` for each of this repository's 39 public IDs, targeting the same generated directories as the corresponding `~/.agents/skills` links. It preserves the existing unrelated `~/.claude/skills/herdr` entry and refuses to replace any conflicting path.

Grok's compatibility settings remain unchanged. After the Claude links are created, Grok must still report no duplicate public IDs and no Claude-sourced coding skills. If that postcondition fails, remove only the Claude coding symlinks created by this change and verify that Grok returns to the captured baseline; do not broaden Grok discovery or rewrite its configuration. Codex, Grok, and other compatible agents continue to consume the existing `~/.agents/skills` child links. Ante or another tool without a compatible global root may use one provider-specific directory symlink to `~/.agents/skills`, but this milestone does not create that adapter.

The cross-tool public identity is the unqualified skill ID such as `implement-change`. A host may render a provider or collection prefix such as `coding:implement-change`, but that host notation is not the portable identity contract.

## Acceptance

- The install contract names live per-skill symlinks under `~/.agents/skills` as recommended, plugins as optional compatibility, and `npx skills` as compatible but non-recommended.
- Stable repository guidance agrees on source, generated payload, local Git clone, symlink, update, duplicate-discovery, plugin, and Claude-machine boundaries.
- Both provider manifests still target the same generated payload and existing plugin validators remain usable.
- Claude Code and Codex no longer report `coding@csheng` as installed on this machine; their marketplace registrations may remain.
- Exactly the 39 coding public IDs are added as non-conflicting child links under `~/.claude/skills`, the unrelated `herdr` link is preserved, and every new link resolves to the same generated directory as its `~/.agents/skills` counterpart.
- Grok reports no duplicate skill names both before and after the Claude links are added, and its resolved coding skills remain sourced through `~/.agents/skills` rather than Claude compatibility.

## Recovery

Use fix-forward for repository drift. Plugin removal is intentionally reversible through the retained optional installers, but verification failure does not authorize automatic reinstallation. The Claude-link action has one guarded recovery: if and only if the post-link Grok probe reports a new duplicate name or a Claude-sourced coding skill, remove exactly the 39 links created by this action, preserve the pre-existing `herdr` link and plugin-removal state, and rerun the same probe. Any subsequent Grok configuration change requires separate evidence and authority.
