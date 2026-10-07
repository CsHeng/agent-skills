# Install Surface

The portable install unit is one authored directory under `skills/<public-id>`. Each directory contains its own `SKILL.md`, authored provider metadata, and referenced resources. It does not resolve repository siblings or require executable workflow support. Product checks inspect this tree directly; there is no generated Skill mirror or installation-time compilation.

## Source And Installed Content

Global Skill discovery reads an independent installed copy. A host may read that copy directly or use links to it; discovery must not resolve into the active development checkout. Editing source, updating Git, generating diagrams, and running checks leave installed content unchanged. An explicitly authorized installation or update refreshes it. Source-change authority alone does not imply installation authority, and validation grants neither.

Prefer the existing `skills` CLI for installation and platform handling rather than repository-owned synchronization code or a dependency on rsync. Its default method copies to a canonical installation and links agent-specific discovery paths there; `--copy` selects separate host copies. Both can satisfy the boundary. See the [upstream installer](https://github.com/vercel-labs/skills/blob/main/src/installer.ts) and [CLI usage](https://github.com/vercel-labs/skills/blob/main/README.md).

## Explicit Refresh And Retirement

- Local checkout: repeat `skills add <local-skills-directory>` with the intended scope, agents, and public IDs. Local-path installs are not automatically refreshed by remote update.
- Remote source: use `skills update` for the intended installed IDs and scope. The manager owns source tracking and its update mechanics.
- Reinstallation of an existing Skill replaces that Skill's resources, including removed files. Retirement of a public ID is separate: explicitly remove the owned installed ID rather than assuming an update prunes the collection.
- The shared discovery directory may contain unrelated collections. Do not mirror-delete it or replace a same-named directory without establishing ownership. When migrating old checkout links, replace only the links belonging to this collection, preserving the installed content until an explicit refresh is requested.

The inspected CLI update path does not preserve a requested per-host `--copy` layout automatically. Links to its independent installed copy satisfy this product's boundary; consumers requiring physical copies for every host should explicitly reinstall in copy mode and verify their selected CLI version. See the [upstream update implementation](https://github.com/vercel-labs/skills/blob/main/src/update.ts).

## Optional Plugins And Discovery

Claude and Codex plugin manifests are optional packaging metadata. Use the plugin manager's installed copy and explicit update lifecycle; direct discovery of an active checkout would violate the same installation boundary. `install.sh` and `install-codex.sh` register plugin marketplaces/installations and do not implement the general Skill-copy lifecycle. Resolve their actual installed content before treating a local marketplace registration as an independent installation.

Keep one active discovery path per tool and public ID, including when mixing plugin and standalone installations. Installation success does not prove a running session has refreshed cached descriptions or already-loaded instructions; report actual installation, discovery, and any unperformed reload or behavioral check separately.
