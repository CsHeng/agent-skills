# Herdr Runtime Adapter Contract

The adapter is a deliberately narrow lower-plane consumer of a controller-binding envelope. The
envelope is the sole source of task identity, provenance, touch set, oracle references, role,
physical binding, and capability. The adapter accepts no plan or ledger path and never writes
either one.

## Invocation and safety gates

Every mutating command requires:

1. `HERDR_ENV=1` and exact equality of `HERDR_WORKSPACE_ID`, `HERDR_TAB_ID`, and
   `HERDR_PANE_ID` with the envelope's caller context in `physical_binding`.
2. `--envelope` resolving to a regular file whose schema is `1` and artifact kind is
   `controller-binding-envelope`, with the required controller, provenance, task, physical,
   and authority fields. Forbidden scalar names include secret, token, password, API key, and
   prompt.
3. The canonical repository and selected checkout/worktree existing and sharing the same Git
   common directory. Writers must use an isolated worktree; explorers and reviewers are read-only
   and have an empty touch set.
4. `terminal_backend=herdr`, `agent_kind` in `codex|grok`, a bounded role-first agent name,
   and one of the delegated capability profiles. The pinned per-kind matrix validates model,
   effort, permission, sandbox, native-login endpoint/reference, and exact CLI argv before Herdr
   allocation. An always-approve permission is accepted only with `delegated-local-writer` and
   `workspace-write`.
5. An explicit non-symlink regular executable supplied by `--herdr-executable`. The adapter never
   resolves a default `herdr` from `PATH`, and a mise-style shim is rejected in favor of the real
   binary. Tests pass the fixture executable and assert that it is the only invoked executable; a
   live invocation passes the exact caller-selected Herdr binary.
6. A fresh run nonce. An existing run or active/cleanup-pending repository lease is a typed
   conflict; recovery must use `resume` or explicit owned `cleanup` and cannot steal a lease.

Binding and capability failures are zero-mutation. A successful preflight uses read-only
`workspace get`, `tab get`, and `pane get` calls to prove the caller hierarchy before creating the
owner-only lease and `state.json` for this run.

## State machine

`state.json` has schema version `1` and is replaced through a same-directory temporary file and
`os.replace`, under an owner-only mkdir lock. It records only bounded metadata, hashes, IDs,
observations, and evidence references; it never stores credentials, full prompts, or unbounded
terminal history.

```text
preflight -> allocated -> started -> prompted -> waiting -> collected
      ^          |            |          |           |          |
      +----------+------------+----------+-----------+----------+
                              -> cleanup-pending -> released
```

Herdr's observable states are `working`, `idle`, `done`, `blocked`, and `unknown`; the adapter
normalizes `working` to internal `busy` and adds bounded `stalled` and `timeout` outcomes. A busy
agent cannot receive another prompt. A prompt is submitted once per attempt and
the body is represented only by a SHA-256 hash. `idle`/`done` is an agent claim, not controller
verification. `collect` bounds terminal evidence and stores a redacted bounded excerpt plus its
hash. The adapter does not decide whether task oracles pass.

The repository lease is `active`, `cleanup-pending`, or `released`. Every lease read-modify-write
holds `.lease.lock` and validates the run ID, controller, nonce hash, repository identity, workspace,
and plan digest before mutation. Clean success closes every
owned live resource and then marks it released. Failure, blocked, unknown, stalled, timeout, or
unverified claims retain evidence and remain cleanup-pending while an owned live resource exists.
Explicit cleanup can release it after all owned processes and panes are gone. A mixed tab is never
closed: only individually proven owned child panes are closed and the lease records cleanup
residue. Allocation persists each returned tab or pane identity before any fallible process
inspection; incomplete enrichment therefore remains recoverable under a cleanup-pending lease.

## Herdr argv protocol

The executable receives vectors, never shell command strings assembled from task or prompt text:

```text
workspace get WORKSPACE
tab get CALLER_TAB
pane get CALLER_PANE
tab create --workspace WORKSPACE --cwd CHECKOUT --label LABEL --no-focus [--env NAME= ...]
pane split --pane PANE --direction right --cwd CHECKOUT --no-focus [--env NAME= ...]
agent start NAME --kind KIND --pane PANE --timeout 120000 -- [KIND-SPECIFIC ARGV]
agent prompt PANE PROMPT --wait --until ... --timeout 5000
agent wait PANE --until ... --timeout MILLISECONDS
agent get PANE
agent read PANE --source recent-unwrapped --lines 80 --format text
pane process-info --pane PANE
pane list --workspace WORKSPACE
tab get OWNED_TAB
pane close PANE
tab close OWNED_TAB
```

Herdr metadata commands return nested JSON entities such as `result.tab`, `result.root_pane`,
`result.pane`, and `result.agent`; `agent read --format text` returns bounded raw text. The fixture
mirrors those shapes. All output consumed by the adapter is capped, malformed output is a typed
protocol failure, and command failures cannot trigger a different backend.

Codex bindings use `--model`, `model_reasoning_effort`, disabled nested agents, a filtered shell
environment, the selected approval and sandbox modes, and a pinned checkout. Grok bindings use its
native reasoning, permission, sandbox, tool allowlist, disabled web search/subagents/memory, and
pinned checkout flags. Allocation blanks sensitive ambient environment names before either native
agent starts; only its declared native-login control plane remains available.

## Capability and runtime binding

`delegated-read-only` permits local reads and bounded inspection only. `delegated-local-writer`
permits writes and tests in the declared isolated worktree only. Both deny task-tool network,
undeclared credentials, SSH, provider actions, commit, push, deploy, and destructive actions
outside the worktree. Control-plane model inference and its declared endpoint/credential reference
are recorded as metadata and are not task-tool authority.

Role is read from the envelope's deterministic projection: `explorer` is only fast/light,
shared-read-only, and no touch refs; every other delegated plan task is `worker`. After the ledger
fully converges, the controller can issue a separately digested bounded-review envelope; reviewer
bindings require Codex SOL with high or xhigh reasoning and remain read-only. For
`semantic-routing`, a Codex explorer is Luna below xhigh and a Grok 4.5 explorer is below high;
unknown or non-lower orderings fail before allocation. `inherit-main` and `runtime-default` are
persisted as explicit policy exceptions rather than silently labeled as downgrades.

## Recovery and cleanup

`resume` and its `recover` alias revalidate repository revision, plan and ledger digests, nonce,
caller workspace/tab/pane/terminal identity, lease ownership, task projection, and every recorded
pane terminal, shell process, native argv, and available opaque agent-session identity before
acting. Any mismatch is `restart_mismatch` and leaves resources untouched. Cleanup first compares
the live caller hierarchy, terminal, and optional agent-session identity with the persisted caller
context, then re-enumerates the workspace, proves owned-pane identities plus foreground process
evidence, and targets agents by opaque pane ID rather than display name. Unknown or moved
resources are retained and reported as cleanup residue.
