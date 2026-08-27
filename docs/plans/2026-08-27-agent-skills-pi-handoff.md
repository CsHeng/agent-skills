---
title: Agent Skills 与 Pi Coding Agent 职责拆分 Handoff
status: Proposed for design and experiment
created: 2026-08-27
scope: CsHeng/agent-skills, Pi coding agent integration, future coding-agent orchestration
intended_readers:
  - repository maintainer
  - subsequent design and planning agents
  - Pi extension implementer
---

# Agent Skills 与 Pi Coding Agent 职责拆分 Handoff

## 0. 执行结论

本轮建议采用以下长期边界：

1. `agent-skills` 继续拥有可移植的工程语义，包括分析、设计、计划、实现约束、评审标准、truth sync、close 判断、风险分类、语言和安全策略。
2. Pi coding agent extension/package 接管单个 coding-agent harness 内的机械控制，包括工具开放范围、写入保护、审批、会话状态、模型和 thinking profile、同一会话内的 review/repair 循环、完成事件、通知和可观测性。
3. artifact schema、workflow mode、risk taxonomy、review verdict、deterministic validator 等跨 harness 合同保留为共享 contract/runtime library。它们既不应藏在 `SKILL.md`，也不应成为 Pi 私有状态。
4. 跨 Codex、Grok、Claude、Pi 的 executor 选择、预算、quota、execution DAG、跨 harness review 和 escalation，继续留给未来独立 router/orchestrator。第一版 Pi 试验不实现这一层。
5. Herdr 保留为可选的持久交互式 agent backend 和人类观测入口。任何 LLM 都不再承担 Herdr pane 状态轮询或 scheduler event loop。
6. 暂不 fork Pi，暂不删除现有 Codex/Claude 兼容运行面，暂不迁移 regulated workflow。先建立 Pi lane，以 30 至 50 个真实 change 验证职责拆分是否降低耗时、人类打断和维护复杂度。

这意味着 `agent-skills` 的目标从“portable coding-agent operating system”收缩为“portable engineering semantics and contracts”；Pi 是第一个承载这些语义的可编程 harness，但不会成为长期唯一宿主。

---

## 1. 为什么现在需要这份 handoff

当前工作流存在一个明确的经济性和控制面问题：

- Codex CLI 搭配 Sol 的实现质量较高，但 wall-clock latency 太长。
- Grok Build 搭配 Grok 4.6 的实现速度明显更快，但首轮质量和稳定性不足。
- 实际流程因此变成 `Grok implement -> Codex/Sol review -> 人类判断 -> repair/re-review`。
- 人类在这里承担了任务状态观察、review 调度、失败分类、下一执行者选择和收敛判断。模型执行时间缩短了，但 human interrupt cost 又进入关键路径。

长期需要自有的 model router 和 agent orchestration plane，这一判断仍然成立。当前没有足够时间持续投入完整 harness，因此更合理的阶段目标是：

- 先把已经写进 Skill 分发面的 harness mechanics 抽离出来；
- 让 Pi extension 承担单 harness 内的控制逻辑；
- 保留 vendor-native Codex/Grok/Claude 作为独立 executor；
- 等真实 telemetry 形成后，再实现跨 executor router。

这一迁移的价值不只在 Pi。它首先迫使仓库明确三种长期不同的资产：

| 资产 | 生命周期 | 期望可移植性 | 合理 owner |
|---|---|---:|---|
| 工程方法、artifact 语义、评审标准、风险原则 | 长 | 高 | Skills + contracts |
| 单 agent tool loop、permission、session、compaction、UI、事件 | 中 | 低到中 | Pi 或 vendor harness |
| 跨 agent 的 routing、预算、DAG、telemetry、escalation | 长 | 高 | 独立 orchestrator |

当前 `agent-skills` 同时覆盖了前两项，并开始部分覆盖第三项，因此出现了代码量、状态面和维护面的持续增长。

---

## 2. 对话与设计判断的演进历史

本节记录结论如何形成，避免后续实现只看到最终结构而丢失约束来源。

### 2.1 起点：重型 Skills 是阶段性 portability 策略

最初诉求并非抽象追求“完整 harness”，而是现实的 subscription 和模型差异：

- 不同阶段需要在 Codex、Claude Code、Grok Build 等 vendor-native coding agent 之间切换。
- 顶级模型通常与自家 harness 配合更好，尤其体现在 tool schema、system prompt、compaction、permission、auto-review 和 subscription economics。
- 单一 vendor 的订阅额度、速度或性价比很难持续满足长时任务。
- 自有 Skills 通过统一设计、计划、实现和评审方法，降低了 model/harness 切换后的行为漂移。

因此，重型 `agent-skills` 在当时解决了真实问题：它把 engineering intent 固化在用户拥有的 repo 中，而非散落在某个 vendor 私有配置里。

### 2.2 与 Superpowers、Matt Pocock Skills 对比后的边界发现

对比形成了一个重要区分：

- Superpowers 对开发流程有较强约束，但主要拥有 workflow semantics。session、tool loop、permission、sandbox 等 runtime 仍由宿主 coding agent 提供。
- Matt Pocock 的方法更偏小型、可组合、按需触发的 engineering disciplines，刻意避免 framework 接管完整 process。
- 当前 `agent-skills` 除了拥有 workflow semantics，还拥有 lifecycle state、ledger、admission、binding、artifact validation、failure policy、provider projection 和 standalone runtime bundle。

因此，“太重”并非单纯 Skill 文档太长，而是职责跨越了 Skill、harness runtime 和 orchestration policy 三层。

### 2.3 第一次长期判断：保留 engineering constitution，减少 runtime ownership

当时形成的方向是：

- 保留 design/spec/plan/review/verification 的工程语义；
- 保留 risk model、truth contract、acceptance criteria；
- session、context compaction、PTY、tool cancellation、provider auth、sandbox、permission、interrupt/resume 等机制尽量交给成熟 harness；
- 不继续以 portability 为理由，在 Skills 中复刻完整 coding-agent runtime。

这一判断仍然有效，但随后用户补充了 router 的真实需求，长期边界因此进一步细化。

### 2.4 Codex/Sol 与 Grok 4.6 的现实工作流改变了问题定义

实际使用表明，单一强模型或单一快模型都不是最优解。真正需要选择的是 execution strategy，例如：

- Sol 直接实现；
- Grok 实现后由 Sol review；
- Sol 设计、Grok 实现、Sol review；
- Grok 实现、deterministic verification、Sol review、Grok repair；
- 高风险或架构任务直接交给强模型。

因此 router 的决策对象应是 execution DAG，而不只是模型名称。目标函数至少包括：

- wall-clock latency；
- defect 和返工概率；
- subscription/API quota；
- human interruption；
- repair/re-review 成本；
- regulated operation 风险。

其中 human interruption 的权重应很高。系统多花一轮廉价模型或 reviewer quota，通常比反复把人从其他工作中拉回更合理。

### 2.5 长期边界修正：own orchestration plane，rent execution plane

在上述事实下，长期“拥有自己的 harness”仍然成立，但应准确拆成：

- 自有 control/orchestration plane：task classification、routing、budget、DAG、review topology、retry、escalation、telemetry、acceptance；
- 外部 execution plane：Codex CLI、Grok Build、Claude Code、Pi、未来其他 harness；
- vendor harness 继续拥有 tool loop、provider integration、native prompt、sandbox、permission、context 和 terminal mechanics。

这使得当前最合适的阶段目标变成：长期 own harness，近期先 own a thin router；而本次 Pi 试验更早一步，先把单 harness 内机械逻辑从 Skills 中抽离。

### 2.6 Herdr 实验暴露了 LLM-as-orchestrator 的失败模式

曾经尝试由 Codex main agent 通过 Herdr Skill 管理其他 pane/tab 中的 coding agent。实际效果差，主要表现为 Codex 不断查询其他 agent 的状态，产生大量无效轮询。

这一失败的根因不在 tmux 或 Herdr 的 UI，而在控制环位置：

- worker 是否完成、是否 timeout、DAG dependency 是否 ready、retry 是否耗尽，均为确定性状态判断；
- 让高成本、慢速、非确定性的 LLM 反复执行这些判断，相当于让 reasoning process 承担 scheduler/event loop；
- 即使 Skill 提醒“不要频繁轮询”，也无法从架构上移除 polling，因为检查时机仍由 LLM 决定。

因此形成一条硬规则：

> LLM 可以参与语义决策，但不能充当 event loop、状态轮询器或长期 scheduler。

Herdr 的合理定位是：

- PTY/process persistence；
- attach/reattach；
- interactive agent session；
- lifecycle event 或 blocking wait；
- 人类可观察和介入。

Herdr 不拥有 task DAG、model routing、review topology、retry policy、budget 或 final acceptance。tmux 比 Herdr 更低一层，只能提供通用 PTY persistence。

### 2.7 当前提案：先用 Pi 验证职责拆分

Pi 的 extension、session、tool event、project trust、RPC 和 SDK 能力足以接走相当一部分当前位于 Skill runtime bundle 中的机械逻辑，同时仍可直接加载现有 Agent Skills。

本轮不把 Pi 直接升级为跨 vendor orchestrator。试验目标更窄：

1. 让现有 portable Skills 在 Pi 中工作；
2. 把单 agent harness mechanics 移入 Pi extension；
3. 观察 Skills 是否可以明显变薄；
4. 验证 Pi lane 是否减少 human interruption 和无效状态控制；
5. 保留当前 Codex/Grok native lane，避免一次迁移同时改变 model、harness 和 methodology。

---

## 3. 当前 `agent-skills` 的真实职责范围

截至 2026-08-27，仓库公开描述自己为围绕 sovereign harness kernel 组织的 portable Agent Skills collection。当前结构已经完成一部分逻辑分层，但运行时 authority 仍集中在 Skill 分发面。

### 3.1 当前 source 和 distribution 模型

- `src/skills/` 是嵌套的 authored skill tree。
- `skills/` 是生成后的 root-flat public payload，目前公开 39 个 Skill。
- `contracts/skills.toml` 拥有 public ID、source mapping、category、activation mode、role、runtime ownership、provider projection 和 mutation guard。
- `src/runtime/harness/` 是唯一 authored deterministic lifecycle runtime。
- `contracts/runtime-bundles.toml` 将 `artifacts.py`、`binding.py`、`cli.py`、`external_touch.py`、`ledger.py`、`lifecycle.py` 等复制进六个 generated lifecycle Skills。
- 当前设计要求这六个 Skill 在脱离仓库 sibling 和单独安装时仍保持 standalone closure。

### 3.2 当前 lifecycle kernel

当前顶层 lifecycle owner 包括：

- `analyze-project`
- `design-change`
- `plan-change`
- `implement-change`
- `review-change`
- `sync-truth`
- `close-change`

其中除 `analyze-project` 外，六个 workflow Skill 携带完整 harness runtime bundle。`src/runtime/harness/cli.py` 当前拥有：

- request classification 和 next-phase routing；
- design/plan validation；
- immutable plan compilation；
- ledger state 和 evidence operation；
- binding envelope；
- truth-sync evaluation；
- close evaluation。

这已经构成完整的 deterministic control surface，而不只是 prompt-side methodology。

### 3.3 当前 mode 和 authority 设计

`contracts/lifecycle.toml` 与 `contracts/workflow-modes.toml` 定义：

- `read_only`
- `micro`
- `standard`
- `regulated`
- `emergency`

并规定 workflow mode selection 先于 phase implementation。当前默认 `unattended_execution = false`，design、plan、truth-sync 和 close 保留 human-sovereign gates。

这一风险模型应继续保留。需要迁移的是 gate 的机械执行位置，而非删除 gate 的语义。

### 3.4 当前 Herdr overlay 已经有正确的局部边界

`implement-change-via-herdr` 当前被定义为 explicit Tool-plane overlay，并要求 approved plan。它不拥有 lifecycle，合理职责是：

`preflight -> allocate -> shell-ready -> start -> prompt -> wait -> collect -> cleanup`

它不应选择任务、改变 ledger、负责收敛、执行 review、repair 或决定 lifecycle tail。这一设计边界可以保留，但在 Pi lane 中它不再作为 Skill-driven orchestration 入口。

### 3.5 当前仓库的内部矛盾

仓库一方面明确要求“Keep skills thin and operational”，另一方面又为了 standalone closure 将完整 lifecycle runtime 复制到六个 Skill 中。这并非简单实现错误，而是两种目标发生冲突：

- portable standalone Skill distribution；
- centralized and maintainable harness runtime。

Pi lane 提供了一个机会：保留 semantic portability，同时让特定 harness 的 runtime 通过 package/extension 正常安装，不再要求每个 lifecycle Skill 自带完整控制平面。

---

## 4. 新的职责与状态归属

### 4.1 目标分层

```text
┌───────────────────────────────────────────────────────────┐
│ Portable engineering semantics                            │
│ agent-skills: analyze/design/plan/review/policy/truth      │
└──────────────────────────┬────────────────────────────────┘
                           │ consumes
┌──────────────────────────▼────────────────────────────────┐
│ Portable contracts and deterministic validation           │
│ schemas, modes, risk, artifact validation, verdict schema │
└──────────────────────────┬────────────────────────────────┘
                           │ adapted by
┌──────────────────────────▼────────────────────────────────┐
│ Pi harness integration lane                               │
│ tools, gates, session state, same-harness convergence     │
└──────────────────────────┬────────────────────────────────┘
                           │ executes
┌──────────────────────────▼────────────────────────────────┐
│ Pi agent loop and provider/model                           │
│ read/write/edit/bash, session, compaction, RPC, SDK        │
└───────────────────────────────────────────────────────────┘

Future independent layer:

┌───────────────────────────────────────────────────────────┐
│ Cross-executor router/orchestrator                         │
│ Codex | Grok | Claude | Pi | Herdr backend                 │
│ DAG, budget, quota, telemetry, escalation, acceptance      │
└───────────────────────────────────────────────────────────┘
```

### 4.2 状态 owner 表

| 状态或决策 | 唯一 owner | 说明 |
|---|---|---|
| Repository code/docs/config | Git repository | 最终 durable truth |
| Approved design/plan artifact | Repo artifact + portable schema | 不进入 Pi 私有 session state 作为唯一副本 |
| Workflow mode 和 risk classification | Portable contract；初期显式选择 | Pi extension 执行，但不私自重新定义 |
| Artifact validation | Shared deterministic validator | Skill 描述语义，extension 调用 validator |
| 当前 Pi session 的 phase、attempt、active tool profile | Pi extension session state | 可由 `appendEntry`/tool result details 重建 |
| 跨 session 或跨 agent 的 durable task ledger | 现有 shared runtime，未来 orchestrator | 第一阶段不迁入 Pi JSONL 作为唯一 authority |
| Tool permission、protected path、external mutation gate | Pi extension | 在 `tool_call` 前执行 |
| Tool loop、retry、compaction、context、provider request | Pi core | 不在 Skill 中复刻 |
| Review criteria | Review Skills + portable verdict schema | 可移植语义 |
| 同一 Pi session 内 review/repair scheduling | Pi extension | 仅在 bounded profile 中使用 |
| 跨 Codex/Grok/Claude review topology | Future router | 不放进 Skills 或 Pi-specific package |
| Model/executor selection | Future router；Pi 内只允许 profile default | 避免 Pi lane 吞并跨 vendor routing |
| Terminal persistence/interactive attach | Herdr optional backend | 与 workflow policy 解耦 |

### 4.3 必须长期遵守的边界规则

1. 不需要理解代码语义的步骤，不唤醒 LLM。
2. worker completion、timeout、retry count、DAG readiness、test exit code、structured verdict 和 cleanup 均由确定性代码处理。
3. Skills 不能成为 session/PTY/process manager。
4. Pi extension state 不能替代 Git 中的 approved artifacts，也不能成为跨 harness 的唯一事实源。
5. Pi-specific behavior 必须通过 adapter 消费 shared contracts，不复制第二套 mode、risk 或 verdict table。
6. 首版 mode 通过显式 command/profile 选择。暂不引入隐藏式 LLM auto-routing，以免同时改变行为边界和实现位置。
7. regulated、external mutation、secrets、auth、deployment、network 和 IaC 继续走现有严格路径，直到 Pi lane 有独立证据。
8. 不因 Pi API 能实现某项功能，就立即把该功能放入 extension。只有机械控制逻辑适合迁移；工程判断仍留在 Skill。

---

## 5. 组件迁移矩阵

### 5.1 Workflow Skills

| 当前组件 | 保留在 Skill 的内容 | 下沉到 Pi 或 shared runtime 的内容 | 初始结论 |
|---|---|---|---|
| `analyze-project` | evidence-first repo inspection、truth boundary、read-only 分析方法 | read-only tool profile、禁止 mutation、session status | 保留并变薄 |
| `design-change` | scope、boundary、truth impact、tradeoff、artifact 内容要求、review criteria | artifact schema validation、approval state、phase transition、active tools | 语义留 Skill，控制移出 |
| `plan-change` | task DAG 的语义、dependency、oracle、risk、recovery、delegation eligibility | plan compile、schema validation、ready-set admission、artifact digest、phase state | 语义留 Skill，确定性编译进 shared runtime |
| `implement-change` | 按 approved task 实现、遵守 touch set/oracle、失败诊断和修复原则 | task admission、binding、attempt counter、review loop scheduling、timeout、cleanup、state transition | 需要最大幅度拆分 |
| `review-change` | bounded review brief、finding validity、adjudication、verdict 语义 | reviewer invocation、result collection、retry/repair scheduling、structured output enforcement | 评审判断留 Skill，执行移出 |
| `sync-truth` | 哪些 stable truth 需要更新、evidence requirements、scope judgment | phase gating、artifact mutation authority、completion status | 保留为 semantic gate |
| `close-change` | merge/release/cleanup readiness judgment、remaining risk | final state transition、notification、session close、cleanup command | 保留为 semantic gate |

关键变化是：workflow Skill 仍可作为 phase-specific reasoning entry，但不再承担完整 lifecycle engine。`implement-change` 的目标应收缩为“如何可靠完成一个已 admitted task”，而非“如何调度整个 plan 并管理所有执行者”。

### 5.2 Session Skills

| 当前组件 | 处理 |
|---|---|
| `use-coding-skills` | 保留。它已经较小，继续负责 ambiguous selection、session/memory/truth boundary 和 compact handoff 语义。phase graph、repair budget 和运行状态不再塞回该 Skill。 |
| `output-styles` | 保留。纯 response composition，不属于 harness runtime。 |

### 5.3 Review components

以下保持为 read-only portable evaluator：

- `review-design`
- `review-plan`
- `review-implementation`

它们应输出符合 shared verdict schema 的结果，但不负责调用 reviewer、控制 repair 或改变 lifecycle state。

### 5.4 Discipline 和 Policy Skills

以下类型应继续留在 `agent-skills`：

- architecture、API contract、testing、error handling、code simplification；
- infrastructure triage、language/tool decision tree；
- language-specific guidelines；
- development、logging、security、SOPS/age policy；
- docs organization、skill mining、executable oracle selection。

这些内容是用户长期 engineering intent，跨模型、跨 provider 和跨 harness 都有价值。Pi extension 可以强制一部分 policy，例如 protected paths 和 dangerous command gate，但 policy 的语义来源仍在 contracts/Skills。

### 5.5 Tool 和 Manual Tool Skills

| 当前组件 | 建议 |
|---|---|
| `implement-change-via-herdr` | 保留为 legacy/compatibility adapter；Pi lane 不让主模型通过 Skill 驱动 pane polling。未来归入 executor backend。 |
| `codex-session-recovery` | 对 Codex lane继续保留；Pi lane 由 Pi session resume/tree/compaction 机制替代，不复制进入 Pi Skills。 |
| `git-worktrees` | worktree 使用原则可保留为 Skill；创建、绑定、dirty check 和 cleanup 更适合 extension command/tool 或 future orchestrator。 |
| `smart-commit` | commit message、scope、evidence 语义可保留；实际 gate、dirty-state check 和命令执行可成为 Pi command。 |
| `smart-squash` | 继续 explicit/manual；若迁移，做成 guarded Pi command，不做隐式行为。 |
| `web-fetch` | 若只是工程方法和证据策略可留 Skill；若主要是具体 fetch implementation，应改为 tool/extension。 |
| `docker-multiarch-build` | build strategy 和 verification 留 Skill；长任务执行、timeout、streaming、result collection 可由 custom tool/extension 承担。 |

### 5.6 必须从 Skill 分发面抽出的 runtime mechanics

以下内容不应继续以“每个 lifecycle Skill 自带 runtime”的形式扩张：

- ledger persistence 和 durability handling；
- artifact parser/validator/compiler；
- immutable task admission；
- actor/model/profile binding envelope；
- retry、repair attempt 和 convergence counter；
- execution timeout 和 completion event；
- external mutation gate；
- worktree/session binding；
- tool profile 切换；
- review invocation 和 structured verdict collection；
- cleanup 和 notification；
- session handoff/compaction mechanics。

其中 artifact/ledger 的跨 harness 部分进入 shared runtime；Pi-specific hook 和 session 部分进入 extension。

---

## 6. Pi integration 的建议设计

### 6.1 为什么 Pi 能承载这一层

当前 Pi 提供：

- 直接加载 `~/.agents/skills/`、`.agents/skills/` 或 settings 指定的 Skills；
- project trust，对 project-local settings、Skills 和 extensions 建立显式信任边界；
- TypeScript extensions；
- `before_agent_start` 注入 context 和按 turn 修改 system prompt；
- `tool_call` 阻止或修改 tool input；
- `tool_result` 规范化结果；
- `setActiveTools()` 切换 read-only、plan 或 implementation tool profile；
- `setModel()` 和 thinking level；
- `appendEntry()` 保存不进入 LLM context 的 session state；
- `agent_settled` 表示 retry、compaction 和 follow-up 均已结束，可避免外部 polling；
- RPC/SDK 用于后续程序化驱动；
- session start/resume/fork/compaction hooks；
- package 机制，可以同时分发 extensions 和 Skills。

这些 primitive 足够实现第一版 Pi lane，无需 fork Pi，也无需先重写通用 agent loop。

### 6.2 推荐 extension modules

```text
integrations/pi/
├── package.json
├── extensions/
│   └── csheng-workflow/
│       ├── index.ts
│       ├── contracts.ts
│       ├── mode.ts
│       ├── tool-policy.ts
│       ├── protected-paths.ts
│       ├── artifact-bridge.ts
│       ├── workflow-state.ts
│       ├── review-loop.ts
│       ├── handoff.ts
│       ├── telemetry.ts
│       └── ui.ts
└── tests/
    ├── mode.test.ts
    ├── tool-policy.test.ts
    ├── state-replay.test.ts
    └── artifact-bridge.test.ts
```

各模块职责：

- `contracts.ts`：只读取 shared contract/validator 输出，不维护第二套 mode/risk table。
- `mode.ts`：实现显式 `/mode read-only|micro|standard|regulated|emergency`，设置 tool profile 和 phase context。
- `tool-policy.ts`：在 `tool_call` 前评估 bash、write、edit 和 custom tool；默认 block 不合规操作。
- `protected-paths.ts`：处理 secrets、generated payload、external file、artifact authority 和 project boundary。
- `artifact-bridge.ts`：调用现有 Python CLI 或后续 shared validator，不在 TypeScript 中复制 artifact semantics。
- `workflow-state.ts`：保存 session-local phase、attempt、active artifact、last verdict；可从 session branch 重建。
- `review-loop.ts`：仅处理同一 Pi harness 内的 bounded review/repair；先不调用 Codex/Grok 外部 agent。
- `handoff.ts`：在 compaction、session switch、fork、close 时生成 compact state summary，同时保留 durable artifact references。
- `telemetry.ts`：记录 latency、tool calls、blocked operations、review rounds、human prompts、cost 和 completion outcome。
- `ui.ts`：状态栏展示 mode、phase、artifact、attempt、mutation profile；在 `agent_settled` 发通知。

### 6.3 Pi event 到当前 harness 职责的映射

| Pi hook/API | 适合接管的现有职责 |
|---|---|
| `project_trust` | project-local extension 和 Skill 的信任边界 |
| `resources_discover` | 加载 portable Skills 和 project overlays |
| `session_start` | 恢复 session-local workflow state，验证 repo/artifact digest |
| `before_agent_start` | 注入当前 mode、phase、approved artifact、task scope、active policy |
| `setActiveTools()` | read-only、design、plan、implementation、review 工具面 |
| `tool_call` | mutation gate、protected path、approved touch set、dangerous command、external mutation |
| `tool_result` | verification result 和 structured evidence normalization |
| `turn_end` | 最小 telemetry 和 progress evidence，不做 scheduler polling |
| `agent_end` | 收集单次 agent run 结果，但不假定 workflow 已结束 |
| `agent_settled` | 可靠地触发完成通知、下一确定性 gate 或 external orchestrator event |
| `appendEntry()` | session-local state/evidence；不作为跨 harness approved artifact 的唯一副本 |
| `session_before_switch/fork/compact` | 阻止未保存 handoff，生成 compact workflow state |
| RPC/SDK | 后续 thin orchestrator 驱动 Pi，避免通过 terminal pane 注入 prompt |

### 6.4 Pi-specific 实现风险

1. Extension 具有完整系统权限。project trust 是必要条件，但不能替代 extension source review 和 pinned dependency。
2. `tool_call` 修改 input 后不会再次进行 schema validation。对关键 mutation 更稳妥的方式是 block 原调用并要求使用受控 custom tool，而非静默改写危险参数。
3. Pi 默认支持 parallel tool execution。任何自定义文件 mutation tool 都必须使用 Pi 的 per-file mutation queue，否则与 built-in `edit/write` 并发时可能产生 lost update。
4. `appendEntry()` 适合 session-local extension state，但 session fork/tree 会引入分支语义。状态必须按当前 branch 重建，不能简单读取所有历史 custom entries。
5. `agent_end` 后 Pi 仍可能 retry、compact 或处理 follow-up。外部完成信号必须使用 `agent_settled`。
6. Pi model switching API 只适合 Pi 内部 model/profile；跨 vendor native harness 的执行器选择仍应由未来 router 完成。
7. Pi package 和 API 当前迭代较快。集成层应小、测试充分，避免引用内部未公开实现。

---

## 7. Shared contracts/runtime 的过渡策略

### 7.1 第一阶段不要重写现有 Python harness

最安全的第一版应避免把 `src/runtime/harness` 全部改写成 TypeScript，采用以下过渡方式：

- Pi extension 通过稳定 CLI/JSON 协议调用现有 validator、compiler 和 ledger；
- 先把 invocation、session、tool gate 和 UI 从 Skill 中移到 extension；
- 测量哪些 runtime capability 仍有真实价值；
- 再把 `src/runtime/harness` 分解为 portable contract library 与 legacy lifecycle controller。

这避免一次迁移同时改变语言、schema、state machine 和 harness。

### 7.2 推荐的中期拆分

```text
src/runtime/
├── contracts/
│   ├── artifacts.py
│   ├── plan.py
│   ├── review.py
│   ├── risk.py
│   └── schema.py
├── state/
│   ├── ledger.py
│   └── evidence.py
└── legacy-controller/
    ├── binding.py
    ├── lifecycle.py
    └── cli.py
```

或者保留现有路径，先按 module boundary 改 import。重点在 ownership，而非目录命名。

中期目标：

- `contracts` 和 validator 是跨 harness authority；
- `state/ledger` 是否保留取决于跨 session/cross-agent 需求；
- `legacy-controller` 仅服务当前 standalone Codex/Claude lane；
- Pi lane 不再从六个 Skill 中运行复制后的 Python controller。

### 7.3 standalone closure 决策如何处理

2026-08-19 的设计决定要求六个 lifecycle Skill 各自携带完整 runtime，以保证选定 Skill 可以独立运行。本轮不立即废除该决定，而是把它标记为“legacy portable distribution constraint”。

过渡期允许两个 lane 并存：

| Lane | Distribution | Runtime owner |
|---|---|---|
| Existing portable/legacy lane | 当前 generated root-flat Skills，六个 owner 带 bundle | skill-local copied harness |
| Pi experiment lane | portable semantic Skills + Pi extension + shared runtime | Pi extension/shared CLI |

只有在 Pi 试验和其他 harness adapter 证明外置 runtime 更可维护后，才决定：

- 完全取消 standalone runtime closure；
- 提供 `semantic-only` 与 `standalone-harness` 两个 profile；
- 或保留 legacy bundle 但停止新增功能。

该决策必须基于实际安装、升级和故障成本，而非代码审美。

---

## 8. Herdr 与 Pi 的关系

### 8.1 保留的用途

Herdr 仍适合：

- 需要 interactive vendor-native agent 的任务；
- 长 session persistence；
- detach/reattach；
- 人类中途 attach；
- 缺少可靠 headless/RPC API 的 executor；
- 统一的 terminal observability。

### 8.2 禁止恢复的模式

以下模式不应在 Pi lane 或未来 router 中重现：

```text
main LLM
  -> start worker pane
  -> inspect status
  -> reason about waiting
  -> inspect status again
  -> read pane output
  -> decide whether completed
```

正确模式是：

```text
deterministic process/extension
  -> start worker backend
  -> await lifecycle event or blocking wait
  -> collect structured outcome
  -> invoke LLM only when semantic decision is needed
```

### 8.3 迁移结论

- `implement-change-via-herdr` 当前继续存在，避免破坏现有使用。
- Pi 第一阶段不依赖 Herdr。
- 若后续将 Herdr接入 router，应实现 executor adapter，不再实现 Skill-level orchestration。
- tmux 仅作为 generic PTY fallback，不进入 task lifecycle contract。

---

## 9. 实验计划

### 9.1 实验原则

实验需要分离三个变量：

1. model 能力；
2. harness 能力；
3. Skill/extension 职责拆分。

不要在同一批任务中同时从 Sol 换到其他模型、从 Codex 换到 Pi、重写 Skills、引入 multi-agent router。否则无法判断收益来自哪里。

### 9.2 Phase 0：建立 baseline

选取最近或接下来至少 10 个真实 change，记录当前 Codex/Sol + existing Skills 路径：

- task type 和 risk mode；
- wall-clock；
- active model time；
-等待/轮询时间；
- human intervention 次数和分钟数；
- tests/oracles；
- review findings；
- repair rounds；
- token/quota 或可获得的 cost；
- final accepted/reverted/follow-up defect。

这一阶段不改行为，只建立比较基线。

### 9.3 Phase 1：Pi compatibility lane

目标：验证现有 portable Skills 能被 Pi 正确发现和使用，同时不迁 lifecycle authority。

实现：

- 使用 `.pi/settings.json` 或 global settings 加载现有 `skills/`/`~/.agents/skills/`；
- 新建最小 extension，只实现 project trust 辅助、status、notification、telemetry；
- 不实现 plan mode、不拦截写入、不改变 model；
- 选择 5 至 10 个 read-only 或低风险任务。

成功标准：

- Skill discovery 与 direct invocation 稳定；
- session resume/compaction 不丢关键 context；
- 无新增 repo mutation 风险；
- 能记录可用 telemetry。

### 9.4 Phase 2：迁移 mechanical gates

目标：让 Pi extension 接管确定性工具控制，但不接管完整 lifecycle。

实现：

- `/mode` 显式设置；
- read-only 和 implementation active tool profile；
- protected paths；
- dangerous bash approval；
- approved artifact/touch-set 只读桥接；
- `agent_settled` notification；
- handoff/compaction state card。

优先选择 `read_only` 和 `micro`，regulated 仍禁用。

成功标准：

- 未授权 mutation 被稳定阻止；
- false-positive block 可接受；
- 不需要在 Skill prompt 中重复 tool permission 机械步骤；
- extension state 可从 session branch 正确重建。

### 9.5 Phase 3：迁移 micro/standard 的单 harness lifecycle

目标：验证 Skill 语义与 Pi runtime mechanics 分离后，单 agent change 能完成闭环。

实现：

- design/plan artifact bridge；
- phase state；
- verification command/result；
- bounded same-Pi review；
-一轮 repair 和 re-review；
- fail/stop/escalate typed outcome。

限制：

- serial only；
- no subagent scheduler；
- no Herdr；
- no Codex/Grok external reviewer；
- no regulated/external mutation；
- no automatic model routing。

成功标准：

- 人类仅在 approval、ambiguity 或 non-convergence 时介入；
- 无 LLM polling；
- Skill 文档中可删除对应 runtime mechanics；
- quality 不低于 baseline。

### 9.6 Phase 4：逐步抽离现有 runtime bundle

只有 Phase 3 成功后执行：

- 标记哪些 `src/runtime/harness` module 已被 Pi extension 或 shared runtime替代；
- 对 Pi package 不再生成 skill-local runtime bundle；
- 保留 legacy lane；
- 更新 design decision，明确 supersede scope；
- 再评估 standalone closure 是否值得长期维护。

### 9.7 Phase 5：决定是否进入 router 研究

只有累计至少 30 个 change，最好 50 个，且 telemetry 可用后，再评估：

- Pi 是否适合成为自有 router 的 substrate；
- 还是独立 Go/TS orchestrator 通过 Pi RPC、Codex headless、Grok ACP 驱动 executors；
- 哪类任务 Grok-first 更划算；
- 哪类任务应直接 Sol；
- cross-provider review 是否真正降低 defect，而非增加 mismatch。

---

## 10. 评估指标与退出条件

### 10.1 核心指标

| 维度 | 指标 |
|---|---|
| 时间 | task accepted wall-clock、model active time、idle/wait time |
| 人类成本 | interrupts/task、human minutes/task、被动等待次数 |
| 质量 | first-pass oracle pass、review findings、repair rounds、follow-up defect/revert |
| 控制正确性 | unauthorized mutation、false block、stale artifact、state replay failure |
| 路由准备度 | task type、risk、diff size 与 outcome 的关联数据是否完整 |
| 经济性 | subscription quota、API cost、review cost、wasted runs |
| 维护性 | extension LOC、shared runtime LOC、skill payload reduction、每次 Pi 升级修复量 |
| 可移植性 | 同一 Skill 在 Pi/Codex 的语义漂移、artifact compatibility |

### 10.2 继续投入条件

满足大部分以下条件时继续扩大 Pi lane：

- human interruption 明显下降；
- accepted wall-clock 不劣于当前路径；
- first-pass 或最终质量无显著回退；
- mutation guard false-positive 低；
- session resume/fork/compaction 不破坏 state；
- Skills 可实际删除 runtime mechanics，而非只增加一层 adapter；
- Pi upgrade maintenance 可控；
- portable contracts 没有被 Pi-specific schema 侵蚀。

### 10.3 停止或回滚条件

出现以下任一 load-bearing failure，应停止迁移并保留 legacy lane：

- Pi session JSONL 成为唯一 workflow truth，导致 branch/resume 后 authority 不明确；
- extension 与 Skill 各维护一套 mode/risk/repair 规则；
- tool gate 误拦截严重，用户频繁 bypass；
- model 在 Pi 中的实际质量显著低于 vendor-native harness；
- Pi API churn 使 integration maintenance 高于现有 runtime；
- review/repair loop仍依赖 LLM 轮询；
- regulated workflow 在证据不足时被意外放开；
- 为了适配 Pi 又把 portable Skill 写成 Pi-specific prompt。

---

## 11. 建议的实现顺序

### Change 1：只建立架构和 package skeleton

新增：

- 本 handoff；
- `docs/architecture/skill-harness-boundary.md`；
- `integrations/pi/README.md`；
- `integrations/pi/package.json` 或本地 package skeleton；
- `.pi/settings.json.example`；
- empty extension entry 和 smoke test。

不改任何 lifecycle behavior。

### Change 2：Skill discovery、status 和 telemetry

实现：

- `resources_discover` 或 settings；
- session status；
- `agent_start/end/settled` telemetry；
- completion notification；
- no mutation interception。

### Change 3：显式 mode 和 tool policy

实现：

- `/mode`；
- active tool profiles；
- protected paths；
- bash/write/edit gate；
- tests for parallel preflight and session replay。

### Change 4：artifact validator bridge

实现：

- 从 extension 调现有 shared Python CLI；
- JSON input/output；
- artifact digest 和 current phase 注入；
- 不改 artifact schema。

### Change 5：micro workflow

实现单一 serial slice：

`plan-lite -> execute -> verify -> close`

先不实现 design、review 和 truth-sync 的完整闭环。

### Change 6：standard workflow 的 bounded review/repair

在 micro 稳定后增加：

`analyze -> design-lite -> plan -> execute -> review -> sync-truth -> close`

repair 最多一轮或两轮，超过预算直接 typed escalation。

### Change 7：更新 portable distribution 决策

基于数据决定：

- Pi profile 不再 bundled runtime；
- legacy profile 是否冻结；
- `src/runtime/harness` 如何拆分；
- 是否发布 Pi package。

---

## 12. 第一版明确不做的事情

- 不实现跨 Codex、Grok、Claude 的 model router。
- 不替换 Codex CLI 或 Grok Build。
- 不让 Pi main model 管理 Herdr panes。
- 不实现 multi-agent parallel scheduler。
- 不 fork Pi。
- 不迁移 regulated、network、GitOps、IaC、secrets、auth、deployment 和 external mutation workflow。
- 不重写全部 Python runtime 为 TypeScript。
- 不把 approved artifacts 只存入 Pi session。
- 不使用 LLM 自动判断所有 workflow mode。
- 不为了“统一”而牺牲 vendor-native model/harness affinity。

---

## 13. 已确认决策、待验证假设和开放问题

### 13.1 已确认决策

1. `agent-skills` 需要收缩 runtime ownership，但保留 engineering semantics。
2. 长期仍需要自有 orchestration plane，以解决质量、时间、经济和 human interruption 的组合优化。
3. Herdr/tmux 不承担 orchestration policy。
4. LLM 不承担 scheduler event loop。
5. Pi 作为试验 harness，不作为立即替代所有 vendor-native agent 的统一 runtime。
6. 第一阶段不 fork Pi。
7. 跨 provider review 继续留在 skills layer 之外。
8. risk mode 和 human-sovereign gates 不因迁移而删除。

### 13.2 待验证假设

1. Pi extension 能接走足够多的 mechanical control，使 lifecycle Skills 明显变薄。
2. Pi 中使用相同或同等级模型时，质量不会因离开 vendor-native harness 大幅下降。
3. `agent_settled`、RPC 和 session hooks 可以消除当前 polling/HITL 调度问题。
4. micro/standard workflow 的 session-local state 足以由 Pi 管理；跨 session durable ledger 仍可通过 shared runtime 保持。
5. Pi package/API 的升级维护成本低于当前六份 runtime bundle 和 provider projection 的长期成本。

### 13.3 开放问题及默认答案

| 问题 | 当前默认 |
|---|---|
| Pi extension 和 Skills 是否放同一 repo？ | 是。先放 `integrations/pi/`，边界稳定后再拆 package/repo。 |
| 是否立即删除六个 Skill 的 runtime bundle？ | 否。保留 legacy lane，先验证 Pi。 |
| ledger 是否迁入 Pi session？ | 否。session state 可镜像，durable authority 暂留 shared runtime。 |
| Pi 是否负责跨模型 routing？ | 否。只允许 profile default 和人工切换。 |
| review 是否调用 Codex/Sol 外部 reviewer？ | 第一版否。先验证 same-Pi bounded review。 |
| Herdr 是否接入 Pi？ | 第一版否。后续只能作为 backend adapter。 |
| regulated 是否纳入试验？ | 否，直到 standard lane 有足够证据。 |
| 是否改用 Go 重写 runtime？ | 否。本轮只重划 ownership，不混入语言迁移。 |

---

## 14. 对现有 design decisions 的影响

以下历史决定继续有效：

- workflow mode selection 先于 phase implementation；
- provider-switching review 不属于 Skill layer；
- controller-owned repair，review evaluator 保持 read-only；
- machine-readable governance 进入 contracts，`SKILL.md` 保持 model-facing instruction；
- host wrapper 保持薄，不复制 repo-owned graph 和 budgets。

以下决定需要新增 scoped supersession：

- “六个 generated lifecycle Skill 必须携带完整 runtime”继续适用于 legacy standalone distribution，但不再约束 Pi package lane。
- “implement-change 是 runtime binding 和 convergence 的唯一 owner”需要拆成两部分：Skill 拥有 implementation/repair semantics；Pi extension 或 future orchestrator 拥有 binding、attempt、scheduling 和 convergence mechanics。
- “sovereign harness kernel”可以继续描述用户拥有的 contracts 和 orchestration policy，但不再意味着所有 runtime primitive 都必须位于 Skill payload。

建议新增一条 ADR：

> Pi integration introduces a harness-owned mechanical control lane while preserving agent-skills as portable semantic authority. Legacy standalone skill runtime remains compatibility-only until empirical evaluation completes.

---

## 15. 交给下一 coding agent 的起始任务

下一 session 不应直接开始删除 runtime。建议使用以下任务边界：

```text
Read:
- AGENTS.md
- README.md
- docs/changelog/design-decisions.md
- this handoff
- contracts/skills.toml
- contracts/lifecycle.toml
- contracts/workflow-modes.toml
- contracts/runtime-bundles.toml
- src/runtime/harness/**
- src/skills/session/use-coding-skills/**
- src/skills/workflows/implement-change/**
- src/skills/tools/implement-change-via-herdr/**

Goal:
Design Phase 1 of a Pi integration lane that loads the existing portable
skills and adds only status, completion notification, and telemetry.

Constraints:
- Do not remove or rewrite the legacy runtime bundle.
- Do not add model routing, subagents, Herdr orchestration, or regulated mode.
- Do not duplicate lifecycle/risk tables in TypeScript.
- Keep approved artifacts and durable state outside Pi-private session state.
- Use Pi public extension APIs only.
- Produce a design and executable plan before implementation.

Required design outputs:
- precise source-of-truth and state-ownership table;
- proposed `integrations/pi/` package layout;
- Pi API compatibility assumptions;
- test strategy for skill discovery, session resume, `agent_settled`, and telemetry;
- rollback/removal path;
- explicit list of existing files left unchanged.
```

---

## 16. Evidence anchors

本 handoff 基于 2026-08-27 访问到的以下当前材料：

### `CsHeng/agent-skills`

- `README.md`
- `AGENTS.md`
- `contracts/skills.toml`
- `contracts/lifecycle.toml`
- `contracts/workflow-modes.toml`
- `contracts/runtime-bundles.toml`
- `docs/changelog/design-decisions.md`
- `docs/architecture/workflow-orchestration.md`
- `src/runtime/harness/`
- `src/skills/session/use-coding-skills/`
- `src/skills/workflows/implement-change/`
- `src/skills/tools/implement-change-via-herdr/`

### Pi coding agent

- `packages/coding-agent/README.md`
- `packages/coding-agent/docs/extensions.md`
- `packages/coding-agent/docs/skills.md`
- `packages/coding-agent/docs/settings.md`
- `packages/coding-agent/docs/packages.md`
- `packages/coding-agent/docs/rpc.md`
- `packages/coding-agent/docs/sdk.md`

Pi 和仓库主分支都可能继续变化。进入实现前应重新验证 public extension API、package manifest、session state 和 project trust 行为。

---

## 17. 最终交接判断

本次改造不应被理解为“从自研 harness 退回到依赖 Pi”。更准确的方向是重新划分 ownership：

- 用户继续拥有长期稳定、跨 vendor 的工程语义和 contracts；
- Pi 接管它已经擅长的单-agent runtime mechanics；
- vendor-native Codex/Grok/Claude 继续保留各自优势；
- 未来 router 只拥有跨 executor 的 control plane；
- Herdr 只提供交互式 session substrate；
- 人类只在审批、歧义、风险和无法自动收敛时进入关键路径。

若 Pi 试验成功，`agent-skills` 会更轻、边界更清楚，同时为未来 router 留出稳定 contract。若试验失败，现有 legacy lane 仍然可用，损失局限在独立 integration package，不会破坏当前生产工作流。
