# Skills 触发、收敛与 workstation 上下文核实

日期：2026-09-07

性质：本次维护的只读现场证据，不是新的全局指令或稳定架构事实。

设计输入：核实时为仓库根 `design.md`，原始 SHA-256 `f92f05b445409dfdbad28e68f43fa989e593c2a3069ce7eed6003c4d6d38c4b7`。现已迁移并适配为[阶段设计文档](2026-09-07-skill-boundaries-context-design.md)；此 hash 仅标识原始输入，不校验适配后文件。

核实基线：HEAD `809d8e44aac40fd507311bb267bc0400064e6077`，与设计参考提交相同。开始时仅 `design.md` 未跟踪，无已跟踪文件修改。

后续决定：[用户已批准的 checkout 补充](2026-09-07-checkout-selection-amendment.md)替代本记录中关于默认隔离及独立整合批准的建议；以下保留核实时事实和当时判断，不把阶段建议当成后续永久约束。

## A. 结论与证据范围

**judgment：D1–D7 合理，可以推进实施规划，无需泛化重开设计。** 主要问题是已定位的自然语言条件冲突和读取范围过宽，不是缺少工作流引擎。保留 39 个公共 IDs、源码/生成物边界、用户批准权、只读 reviewer 及项目专有约束。

本次采用 `mixed verification`：读取设计明确指定的 authored skills、相邻调用方、稳定架构和现有检查；检查用户级指令入口、安装链接、相关 Pi 加载代码及三个真实工程的根指令样本。`docs/plans/` 是阶段历史，默认搜索由 `docs/.ignore` 排除；本次没有将旧阶段计划当成当前事实。稳定架构总体可用，相关 skills 存在局部 `doc_doc_conflict`，因此受影响指令面的健康度为 `degraded`，不意味着整个仓库文档不可信。

没有运行受控模型行为实验，没有核验设计引用的外部模型文章/指南。设计中的模型敏感性和成本推论不是本地事实；以下源码冲突自身已足以支持修改。

## B. Skills 现状与设计适配

| 编号 | fact：当前证据 | judgment：处理 |
| --- | --- | --- |
| B1 · D1 | `src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md:95` 将 subagent、TDD loop、execution runner 放进同一 readiness gate，要求 maximum review budget、profiles、parallel policy 等。`src/skills/workflows/implement-change/SKILL.md:42` 已允许 profiles 缺省时本地执行；`src/skills/workflows/plan-change/SKILL.md:59` 已允许不声明委派就绪时省略 profiles。 | 冲突仍存在。修 selector 的无条件 gate，复用 plan/implement 的条件边界，不新建 readiness schema 或 skill。 |
| B2 · D2 | `src/skills/workflows/implement-change/SKILL.md:40` 限制一次修复且禁止复审；`:75` 将 `non-convergent` 绑定单次失败。`references/repair-loop.md:3` 的入口又只承认 review findings，正文第 6 步禁止另一轮 review。 | 同步改入口、修复引用和 outcome 解释；覆盖测试失败与 review findings 两条路径。 |
| B3 · D2 | `src/skills/workflows/design-change/SKILL.md:27`、`src/skills/workflows/plan-change/SKILL.md:29` 同样限制一次修复；`src/skills/workflows/review-change/SKILL.md:11` 称调用方请求其 single bounded review。 | 区分一次调用只评价一个目标与整个产物只准一次 review。设计/计划修复不产生批准或后续实施授权。 |
| B4 · D3 | `design-change` description 以“implementation planning 之前”定位；`testing-strategy` description 包括普通测试实现和选择 CI 命令，正文 `:13` 对 architecture/planning 要求先用 selector。router 的 design/plan/oracle negative cases 已排除部分直接执行，但发现阶段未加载 router。 | description 与正文同时收紧；保留 router direct-match bypass，不把加载 router 变成避开误触发的必要步骤。 |
| B5 · D3 补充调用方 | `src/skills/disciplines/code-simplification/SKILL.md:14` 将应用任何 candidate 都转给 design；`references/candidate-evidence.md:71` 重复同一跳转；routing TOML 的 `code-simplification-audit` negative case 也如此表述。 | 最小适配：明确授权且边界充分的 candidate 可转 implement；有实质取舍才转 design。只改交接语义，保留审计只读、证据门槛及现有 dispositions，不重做 simplification 方法。 |
| B6 · D4 worktrees | `src/skills/git/git-worktrees/SKILL.md:12` 要求遵循仓库策略；Failure Conditions 又要求仓库位置不同即停止。创建、ignore、列举、清理和例子仍硬编码 `.agents/worktrees`。根文件 273 行，包含全部操作分支。 | 确定实际位置后统一消费；本地嵌套路径的 Git/search ignore 与外部路径的适用条件分开；只读操作不因创建准备受阻。按操作拆引用，不按字数验收。 |
| B7 · D4 上下文 | worktrees 已有 exact bytes/hash 的 handoff context-transfer 例外，但前面一般规则仍写未提交 context 一律停下；create 示例也只说 plan 必须已提交。 | 保留并统一已有例外；不能推导所有未提交源文件都能转移，不能从本次维护授权推导真实 worktree 创建/删除授权。 |
| B8 · D4 analyze | `src/skills/workflows/analyze-project/SKILL.md:27` 起固定要求先读多个根文档、盘点术语、判断健康度/重建基础，再选输出深度；`references/output-contract.md` 将全部 axes 称 required analysis axes。 | 当前精简主要发生在输出，不在取证。根文件改为局部查询/证据扩展/完整 audit 入口，输出引用也需去掉隐性全量门槛。 |
| B9 · D5–D7 | `AGENTS.md`、`docs/architecture/skill-composition.md` 已支持独立可选能力、条件 review、active agent 裁决和 host mechanics 边界。`testing-strategy` 已禁止 prose snapshots；其 evaluation 引用已声明普通 skills 修改无需实验。 | 保留，不为本次设计重新创建 orchestrator、强制评估平台、模型正文分支或重复元规则。 |

`review-components/*` 现有“one bounded target”和“不递归委派”是每次评价的作用域，不是全 change 次数限制，未发现需要删掉这些约束的证据。session 的 `phase-boundary-decision-tree.md` 处理已完成工作的上下文选择，并且明确 mid-phase continue；不因标题含 phase 就删除其会话边界。

## C. Workstation 指令组合

调查范围限定为必要入口和配置，不读取 auth、密钥、SQLite、模型凭据文件或无关历史。下列文件路径是调查 owner 标识，不代表全部都在本次主会话被加载。

### C1. 当前 Pi 主会话

- **fact**：安装版本 `pi 0.85.1`；`PI_CODING_AGENT_DIR`、`PI_PACKAGE_DIR` 均未设置。`~/.pi/agent/AGENTS.md` 与本仓库 `AGENTS.md` 的内容在本会话可见的项目指令中出现，因此不只是文件存在证据。
- **fact**：用户级 AGENTS 仅保留语言/无可选 commentary 偏好、环境事实、直接匹配 bypass 和薄 router 提示；明确禁止重复 lifecycle、repair states、review budget。没有发现“所有修改先 design/plan”或“一次 repair”条款。不建议为这次维护重写它。
- **documented**：Pi 0.85.1 的本地 `README.md` / Context Files 说明从 global、祖先及 cwd 拼接上下文，同目录 `AGENTS.override.md` 优先于 `AGENTS.md`/`CLAUDE.md`；可通过 `--no-context-files` 禁用。`docs/settings.md` 说明 project settings 覆盖 global，`docs/skills.md` 说明发现目录及名称冲突 first-found 策略。这不是 Codex/Claude 的通用合并规则。
- **fact**：本仓库没有 `.pi/settings.json`、`.pi/SYSTEM.md`、`.pi/APPEND_SYSTEM.md` 或 `AGENTS.override.md`；检查的 home、workspace 祖先和 Pi home 未发现相关覆盖文件。本仓库 `CLAUDE.md` 是 `AGENTS.md` 的兼容链接，不能仅据两个文件名认定重复注入。
- **fact**：Pi settings 配置本地 `~/workspace/pi-extensions`、MCP adapter 和 todo package；MCP adapter 的 skills 被显式过滤为空。本地扩展 manifest 仅声明 extensions，不额外分发 coding skills。可见主会话工具/指导与相关扩展相符，但未导出完整底层请求 payload。

### C2. 安装目标与实时可见性

- **fact**：`~/.agents/skills` 有 40 个可见子项，其中本仓库的 39 个公共 skills 都是链接，解析到当前 checkout 的 `skills/<id>`；额外的 `herdr` 是独立目录，不是本仓库第 40 个 ID。
- **fact**：`~/.pi/agent/skills`、`~/.claude/skills` 不存在；`~/.codex/skills` 没有非隐藏用户副本，有 6 个 `.system` skills，名称不与本仓库 39 IDs 重复。检查到的 `~/.codex/plugins` 下没有文件。本次没有发现第二套 coding 安装副本。
- **重要影响**：对当前 checkout 运行生成器会改变这 39 个链接后续读取的内容，即使没有运行 install。新会话/重新加载通常才能刷新已缓存的 descriptions；当前已加载正文也不会自动被从上下文抹去。不能把“生成通过”表述成“正在运行的 agent 已采用全部新语义”。
- **处理**：候选实现默认在不被这些发现链接指向的隔离 checkout/copy 中生成、检查和评审；回到链接目标 checkout 的整合是显式批准点。不得重写用户安装链接或为隔离修改全局配置。

### C3. Codex 入口

- **fact**：`codex-cli 0.153.4`；本进程 `CODEX_HOME` 未设置，默认路径 `~/.codex/AGENTS.md` 不存在，不应虚构该文件中的规则或创建空白替代。
- **fact**：仅提取相关配置项，未发现 `instructions`、`developer_instructions`、`model_instructions_file`、`experimental_instructions_file` 或 project-doc fallback/size override；hooks feature 已配置。`hooks.json` 绑定 session-state 与通知 hook。
- **uncertain**：这不是一条正在运行的 Codex 会话的最终加载证明；未审计 Codex 内部提示、完整 hook 下游和所有历史调用的 CLI overrides。不据此宣称 Codex 完全无上下文影响，也不将 Pi 的拼接规则套用给它。

### C4. 真实工程样本

| 已读取来源 | 事实与判断 | owner / 本轮处理 |
| --- | --- | --- |
| `~/workspace/drone/backend/AGENTS.md` | Implementation Gate 是具体领域不变量、禁止的生产/外部动作和生成物规则，不是必须先 design 的流程门槛。未发现默认 review 次数。 | backend owner；保留，不抽成通用 skills 规则。 |
| `~/workspace/homelab/homelab-infra/AGENTS.md` | scoped AGENTS/README 优先；额外多仓文档仅在 cross-repository 工作时读取；worktree cleanup 要检查 ignored files 并保留本地 overrides。 | infra owner；保留适用条件和防丢失约束，不为减少阅读整体删去。 |
| `~/workspace/pi-extensions/AGENTS.md` | host owns context、tool profile、固定 child 角色和物理资源限制；不拥有语义验收/repair/continuation；子 agent 不加载 skills。 | pi-extensions owner；不是共享 skills 的新 runtime 需求，本轮不修改。 |

以上是刻意选取的实现、基础设施、host 三类根指令样本，不是所有工程所有子目录的完整审计；不存在这些项目正在本次主会话中全部注入的证据。后续实际操作仍需遵循目标项目的最近 scoped 指令。

### C5. Children、hooks 与 continuation 的证据限制

- `pi-extensions/extensions/subagents/runner.ts:119` 的 child 参数禁用 auto extensions、skills、prompt templates，显式加载 path guard 和 role prompt；没有禁用 context files。因此主 agent 的已加载 skills 不能假定由 worker 自动继承；任务 brief 要传递必要验收与限制。读取外部项目也不等于加载其完整资源。
- `extensions/subagents/roles.ts:8` 保留只读 evaluator、不递归、最终裁决归 parent；worker 禁止命令执行，不是可替主 agent 完成验证的 actor。此边界无需修入 skills。
- `extensions/plan-mode/index.ts:17` 的只读提示仅在该 profile 激活时追加。主会话可见 tools 未处于该只读集合，没有将它当成本次无法实现的原因。通知扩展与 session-state 扩展的存在也不等于强制 design/repair 行为。
- 本次两批探索调用的工具摘要报告 `succeeded`，但它们的当前任务诊断记录均终止于 tool results，没有最终事实报告；首批还有 root 列举超出声明 scope 的拒绝。更正为根 scope 后仍未返回报告。没有采用这些成功标签作为审计证据，相关结论由主 agent 直接核实。
- 该观察只能证明这几次工具级“成功”不足以证明任务完成，不能证明由共享 skills 引起、模型普遍失效，或本轮设计已改善行为。不在本仓库顺带修 host；未来委派必须检查实质完成证据。

## D. 已执行的验证

`bash scripts/check.sh`：**通过**。

- contract-package、root-flat parity、install-surface、index、diagrams：通过。
- Ruff、ty：通过。
- pytest：**98 passed**。
- Markdown：300 files，0 files with hard wrap。

这是修改前的结构、生成一致性及现有自动检查基线，不是模型触发/收敛收益证明。本次核实没有修改 skills、生成投影、用户配置或其他项目，没有 install、commit、push、部署或行为实验。

## E. 交给规划的决定

- E1：共享 skills 语义校准、worktrees 渐进披露、analyze-project 取证深度是本轮实施包；相邻 simplification 交接仅作 D3 一致性修复。
- E2：用户级与真实工程 AGENTS 目前无必须修正的已证实流程冲突，保持只读。不创建缺失的 Codex AGENTS。
- E3：分离 repository candidate 验证与 live-linked checkout 整合；没有 consumer 激活证据时报告未实测。
- E4：worktree 命令用临时 Git fixtures 验证；自然语言语义使用设计第 10 节场景审查，不新增 prose 断言或模型 runner。
- E5：host 返回不完整报告作为委派可用性限制记录，不作为仓库实现阻塞；委派非用户硬要求时可由主 agent 执行。
