# Agent Skills Pi Handoff

## 当前结论

`PI-HARNESS-003` 已取代 `PI-HARNESS-002` 的命令驱动部分。Pi 现在通过一个全局安装的模块化 host adapter 承担单代理机械运行时职责；普通自然语言请求和原生 `/skill:<name>` 是正常入口，不再需要 `/csheng-run`、mode 参数、auto 标记或启动 flag。

portable Skills 与 canonical contracts 仍是 sovereign semantic kernel。它们拥有请求含义、设计与计划边界、实现与验证含义、review judgment、recovery choice、truth sync 和 close judgment。Pi adapter 只拥有 invocation state、authority source、tool profile、task progress、attempt accounting、branch replay、typed handoff validation、follow-up scheduling、settlement、UI status 与 sanitized telemetry。

## 当前结构

```text
integrations/pi/
├── extensions/coding-harness/
│   ├── artifact-bridge.ts
│   ├── authority-profile.ts
│   ├── continuation.ts
│   ├── contracts.ts
│   ├── index.ts
│   ├── session-state.ts
│   ├── skill-bridge.ts
│   ├── task-ledger.ts
│   ├── telemetry.ts
│   ├── tool-policy.ts
│   ├── transition-runtime.ts
│   └── ui-status.ts
├── generated/lifecycle-contracts.json
├── scripts/
│   ├── run-native-discovery-probe.sh
│   └── run-native-workflow-probe.sh
├── tests/
├── package.json
└── README.md
```

`index.ts` 只注册 Pi public events、tools 和 diagnostic command，并连接 behavior-bearing modules。它不包含固定 phase sequence、phase goal、provider/model route、runner command 或 Skill-local controller fallback。

## 两个独立安装面

1. 40 个 Skills 通过 `~/.agents/skills/<public-id>` child symlink 指向本 checkout 的 `skills/<public-id>`，每个 ID 只有一个 active discovery path。
2. Pi adapter 通过 `~/.pi/agent/settings.json` 的一个 user-level local package entry 指向 `integrations/pi/`。package 只暴露 extension，不再次暴露 Skills。

项目内 `.pi/settings.json` 不加载 extension，因此任意 repository 都能获得同一 host mechanics，也不会在本 repository 中出现第二个 adapter instance。

## Authority Profile

portable default 是 phase-gated。当前 validation machine 在 user-level settings 中使用：

```json
{
  "codingHarness": {
    "version": 1,
    "authorityProfile": "local-validation"
  }
}
```

这个 profile 只预授权 bounded repository-local `micro` 和 `standard` continuation。adapter 将 exact authority source 与 terminal intent 记录在 session state 中。缺失 profile 会回到 phase-gated；unknown、malformed 或 stale version 会 fail closed。parser 不读取 provider、model 或 credential fields。

## Native Entry 与 Handoff

- explicit `/skill:<name>` 在 Pi `input` event 中绑定 owner，不替换原命令。
- natural request 继续使用 Pi native Skill discovery；agent 通过 generic `coding_harness_bind` 报告已选 owner、mode 和 terminal intent。phase 与 evaluator role 由 host 从 generated contracts 推导。
- active Skill 通过 `coding_harness_signal` 报告 evidence、outcome、next owner 与 optional evaluator role。host 校验 legal handoff 后推导 Pi phase。
- `agent_end` 只调度已经持久化的 staged handoff；extension-originated `/skill:<owner>` input 激活 scheduled handoff；replay 不会重复调度。
- `agent_settled` 才记录 terminal settlement。assistant prose 不推进 state。

## State 与安全边界

`coding.harness.session.v1` 是 closed schema，记录 request identity/digest、terminal intent、mode、owner/role/phase、authority source、artifact refs、task progress、attempts、accepted findings、pending handoff、tool profile、terminal outcome 与 settlement。

未绑定 owner 前，read discovery 可用，mutation fail closed。绑定后，tool set 和 preflight 根据 active phase、approved scope 与 protected-path policy 推导。adapter 始终阻止 repository 外写入、`.git`、`.env*`、project Pi settings、recursive delete、privileged/remote mutation、commit、push、publish 与 deploy。

`src/runtime/harness/` 只保留 durable artifact/ledger compatibility boundary。Pi 可以在 artifact boundary 直接调用 validator；Python 不 poll、schedule 或 advance Pi session，Skills 不查找或执行 lifecycle CLI。

## 已验证证据

- generated contract parity 与 negative parsing tests
- pure session replay、task readiness、transition、repair budget 与 artifact bridge tests
- fake/module-level authority、Skill bridge、tool gate、continuation 与 settlement tests
- temporary Pi extension loading before global settings mutation
- disposable repository 中 40 个 unique Skill commands 与 1 个 adapter instance
- user-level settings 的 non-package/non-harness structural digest 在安装前后保持一致
- 40 个 global child symlinks 全部解析到本 checkout 的 matching generated Skill
- natural standard implementation 在 disposable repository 中完成 mutation、verification、review、truth/close routing，并产生唯一 settled pass

## 维护命令

```bash
python3 scripts/generate-pi-contracts.py
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
npm --prefix integrations/pi test
bash integrations/pi/scripts/run-native-discovery-probe.sh
bash integrations/pi/scripts/run-native-workflow-probe.sh
bash scripts/check.sh
```

live probes 会在 checkout 外创建 disposable Git repository，只输出 redacted state evidence，不 commit 或 push。使用 `pi --no-extensions` 可以关闭 adapter，同时保留 portable Skills 的 extension-off 语义路径。
