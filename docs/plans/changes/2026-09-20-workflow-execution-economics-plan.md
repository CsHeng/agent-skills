# Plan: 实施规划经济性、显式结构重评与单向执行边界

Status: approved_for_implementation；用户已明确批准实施。本文可交给新 main 会话，不依赖之前聊天的隐含决策。

Date: 2026-09-20。

Repository / baseline: `CsHeng/agent-skills@67d15db7e559b9b0abf5a33328cb7355064c6690`。

Design: [目标设计](2026-09-20-workflow-execution-economics-design.md)。本计划的目标语义来自该设计；实现只解决局部技术问题，不再开启架构选型复赛。

## SP-01. 执行入口与范围

先读取当前 checkout 的 `AGENTS.md`、上述 design 与本 plan。核对是否仍基于该提交或其后继；后继有相关变化则合并有效事实，不 reset 用户修改、不因 SHA 不同要求重新授权。公开基线核查不是本机加载证明。

只修改本仓。作者源是 `src/skills/`；不得手改 `skills/` 或 `skills.index.json`。新 reference 路径是建议落点，不是强制实现白名单。必要的关联文件可以在同一目标内补改，最终报告实际 diff。

实施端点是更新后的完整源仓与已有生成物、适当检查结果、变更说明；本次不发布或安装，不做 live provider 实验。

## SP-02. 可直接消费的任务与独立性

| Task | 目标 | 事实依赖 | 独立性 / owner |
| --- | --- | --- | --- |
| S01 | 对齐 plan / implement 的 aggressive delegation、初始写集与单向阶段边界。 | 已确认 design。 | 可与 S02、S03 并行；workflow Skill 区域一个 writer。 |
| S02 | 增加成熟能力复用和显式结构性替代评估入口。 | 已确认 design。 | 可与 S01、S03 并行；design / architecture / code-simplification 区域一个 writer。 |
| S03 | 收紧 testing / oracle 触发，检查本次命中的过度保障诱因。 | 已确认 design。 | 可与 S01、S02 并行；testing 区域一个 writer。 |
| S04 | 对齐 close / git-worktrees 的执行资源和 host 隔离边界。 | S01 对 main / host 所有权的语义稳定。 | 独立局部任务；规模很小则 main 完成，不为派发额外调查。 |
| S05 | 整合 routing、稳定 docs、生成投影与相关结构测试。 | S01–S04。 | Main 独占共享 contracts / generated surfaces。 |
| S06 | 情景自审、仓库检查、针对性复核和交付。 | S05。 | Main 整合；reviewer 只读，不执行修复或重开设计。 |

S01、S02、S03 的区别是目标与作者目录，不是强制每个任务必须派一个 agent。模型只用表内和已有 context 判断，信息不足默认 main 做；不为估时再搜索。每个 worker 同时负责自己修改的相关检查与局部 repair。所有公共生成命令留到 S05，避免不同 worker 竞争生成物。

所有角色的具体 model / reasoning 由 host 路由或用户显式选择，本计划不绑定供应商。执行配置变更不重开语义计划。

## S01. 规划与实施的职责收敛

目标：plan 提供给新 main 的独立性信息足够使用；实施不再花额外预算判断是否派发，不因 initial writeset 漏项反转到 design/plan。

初始修改区域：

- `src/skills/workflows/plan-change/SKILL.md` 与 `references/delivery-and-delegation.md`。
- `src/skills/workflows/implement-change/SKILL.md` 与 `references/delegated-execution.md`。
- 仅当含有冲突语义时，更新同区域的 `references/repair-loop.md`；不新增通用 phase manager。

实施内容：将 delegation-ready 的 exact-file 前置条件替换为 goal、已知输入、初始写区、repository ownership、实际资源与 join 预期。对真的固定文件限制继续尊重，对 host-specific guards 描述为能力事实而非用户批准白名单。

明确“只用已收集 context；不知道则 main 实施”的默认规则。删除或重写会要求 dispatcher 为填 exact paths 再做整套调查的表达。保留必要的输入可用性与权限检查，它们不是收益估算。

实现不默认调用 upstream design/plan/architecture audit。对实际 hard constraint 冲突只报告具体 owner 决策，不擅自换技术方案；保持其余授权任务推进。允许 worker 局部调查、编写测试、诊断和修复，继续复用已有 worker/reviewer。

验收：对应 S-AC2、S-AC3、S-AC4。拿一个 plan 中两个独立复杂任务、一个 trivial task、一个 write set 漏掉调用方的任务做离线语义走读，不为这些情景增加固定句子的 CI 断言。

## S02. 成熟能力复用与结构性替代入口

初始修改区域：

- `src/skills/workflows/design-change/SKILL.md`。
- `src/skills/disciplines/architecture-patterns/SKILL.md` 与 `references/architecture-decision-economics.md`。
- `src/skills/disciplines/code-simplification/SKILL.md`；按需新增 `references/structural-alternatives.md`。

实施内容：只在材料性选型尚开放或用户显式重评时要求有目标的官方/社区核实；不建立每个 plan task 的 research requirement。补充用户声明的维护周期与团队路线是有效证据，既不能因当前 slice 简单推翻 Gin 一类明确选型，也不能因沉没成本阻止被明确请求的替代研究。

`code-simplification` 保持普通只读简化入口；为显式结构性评估增加渐进披露 reference，而不是把所有简化审计升级。它可以推荐大重构或重写，但只能交付证据，不自动生成设计、计划或实现。Frontmatter 应同时能被明确的结构替代请求命中，且排除普通实现、一般 review 和未请求的全仓审计。

验收：对应 S-AC5、S-AC6。对“修一个函数”“普通 code-simplification”“明确请评估从自建迁移成熟框架”“已选 Gin 的实现”四种输入检查触发与停止位置。允许无收益结论，不制造候选数量。

## S03. 验证的适用范围与比例原则

初始修改区域：`src/skills/disciplines/testing-strategy/SKILL.md`、该目录内实际关联的 reference；检查 `executable-oracle-architecture-selector` 的触发段落时只改与本目标直接矛盾的内容。可以扩展现有 `references/goal-and-risk-cases.md` 的少量离线案例。

实施内容：清楚区分“选择/审计策略”与“运行已有检查/普通回归”。例如 `Record this chain before adding tests` 这类全称式表达，应限定在该 Skill 正在解决策略决策的范围，不能变成每次新增测试都要填表。

对新 hash、还原证明、恢复演练、部署循环，要求说明受影响行为，复用仍然有效的证据与现有身份原语。不要禁止真正需要的完整性校验或弱化真实迁移检查。不要将历史模型的表现归因成已证明的 Skill 缺陷。

在受本次修改影响的维护测试中，保留结构、标识、链接、生成与 consumer 测试。命中只锁定自然语言措辞的断言时，按现有 testing 规则删除该 prose snapshot，而不是换更小关键词继续锁 prose；不得借机全仓移除测试。

验收：S-AC7。文档修改不引入 executable business test；异步/工作区状态变更仍要求真实行为测试。把这两者明确区分，不形成“一概少测”的新口号。

## S04. Close 与工作区职责

初始区域：`src/skills/workflows/close-change/SKILL.md`、`src/skills/git/git-worktrees/SKILL.md` 的相关边界，以及确有必要的 owner-local reference。

实施内容：增加 close 所需的 execution resource disposition 语义，区分清理完成、因后续修复保留、未集成而不能删除。继续由现有执行 owner 发出 host cleanup 操作；`close-change` 自身保持只读语义权限，不修改其 `may_mutate_repo` 为 true。

明确 host 自动提供任务 worktree 不等于模型主动调用 `git-worktrees` Skill；后者显式调用和仓库 mutation 权限不改变。Parent dirty 可正常实施；保留已有修改，不自动要求 commit/stash。

验收：S-AC8。既不会每个临时目录都重新审批，也不会把业务完成等同于授权删除任意分支。

## S05. 整合、生成与稳定事实

Main 接收 S01–S04 的 diff，解决共享术语冲突。初始整合区域：`contracts/skills.toml`、`src/skills/session/use-coding-skills/references/routing.toml`、`docs/architecture/skill-composition.md`、与变更直接相关的其他稳定文档和维护测试。不要因为提到路由就改所有 public activation modes。

39 个 public IDs 不变。只有实际描述/依赖发生变化才修改合同；不要新增 executable schema 来检查用户 plan 的自然语言独立性。保持 semantic dependency 是真正需要的内容，不把可选结构审计变成 implement 的必加载依赖。

所有作者修改合并后，在仓库现有工具链运行：

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

这些命令来自本仓 AGENTS；`scripts/check.sh` 还使用 `uv` 提供 ruff、ty、pytest 环境。缺工具或无法取得依赖属于具体环境限制，不能把未运行写成通过。[P1][P2]

核对生成 diff 只来自相应作者改变。稳定 docs 描述实际交付的语义；本 design/plan 作为 stage artifact 留在 `docs/plans/changes/`，不是新 runtime input。

## S06. 最终验证与交付

完成以下审查一次；仅当后续修改使证据失效才重做对应部分：

| 情景 | 应有行为 |
| --- | --- |
| 新 main 只拿到已定 design/plan。 | 直接执行，不为重新认识项目做全量架构研究。 |
| 两个已知独立重任务。 | 允许同时派给 children，parent 可等；不强制 parent 编码。 |
| 是否值得派发的 context 不足。 | Main 做正常实施，不发起专门估时搜索。 |
| Worker 发现同 goal 下还需要一个文件。 | 扩展初始区域并验证，不要求新的用户许可。 |
| 用户显式要求替代自建框架。 | 有边界的只读结构评估，可建议重写，但不实施。 |
| 普通小改动与真实持久状态变更。 | 前者复用已有验证；后者验证实际受影响状态，不混淆。 |
| 任务完成仍有 worktree。 | 按已覆盖权限回收或明确保留，不能忽略或乱删。 |

这些是人工/agent 语义检查案例，不是 mandatory live evaluations，不建立关键词测试集。

需要针对性 reviewer 时只提供当前改动、design 目标与上述边界；main adjudicate findings。普通 repair 回原 worker，不固定评审轮数，不把无关旧缺陷加入此次交付。

交付说明须区分：作者变更、生成变更、实际运行的命令及结果、跳过的项目、行为/经济效果未测、当前 Git base 和新提交（仅在之后批准本地提交时）。

## SP-03. 跨仓依赖与版本交接

本仓不导入 pi-extensions。S01–S06 可与 runtime 实现独立推进，不能因为 runtime 尚未上线就删除 portable host-capability 条件。Runtime 会消费模型行为而非本 Skill repo 的内部文件。

组合验收在两个 repo 都交付后进行：plan 的 initial writeset 语义、async capability 提示、resource close 与 main acceptance 不冲突。不要把 runtime tool field 复制到 Skill guidance。

## SP-04. 实施批准摘要

当前已覆盖：读取公开源码、研究、编写四份 design/plan 与交付文档包。没有批准修改实现。

后续一次确认可以覆盖：在本仓副本中编辑上述目标内作者源、必要测试/生成物/稳定文档；运行离线检查；局部修复；建立本地交付分支与本地提交；打包完整仓库。具体文件与任务数量不是批准白名单。

不包括：remote push/tag、改 GitHub 设置、发布插件、安装到用户 Pi、修改 provider/model 配置、调用付费模型、访问生产数据或部署。实施可以在目标内持续推进，无需每个 slice 重新确认。

能力前提：完整源码和原始 Git 历史能进入执行环境，且所需工具/依赖可用。本轮 web 能读源码，但容器 GitHub clone 的 DNS 解析失败，未取得完整仓库，未运行本仓检查。这是交付能力限制，不是设计悬而未决。

若用户选择本地 agent 执行，本计划已经足够交接。若选择本会话后续实施，需要先满足完整仓库输入/可克隆前提；不能将从网页拼接的片段或 `git init` 新建历史称为完整原仓的新版本。

## 实施授权记录

2026-09-20：用户批准四份 design/plan，授权在两个仓库副本中实施、运行离线检查、创建本地 Git 提交并返回完整 ZIP。用户随后明确允许 best-effort 交付，受阻项如实记录；不包含远程 push、发布、安装或付费模型调用。

## 来源

- [P1 作者源与仓库检查](https://github.com/CsHeng/agent-skills/blob/67d15db7e559b9b0abf5a33328cb7355064c6690/AGENTS.md)
- [P2 check.sh](https://github.com/CsHeng/agent-skills/blob/67d15db7e559b9b0abf5a33328cb7355064c6690/scripts/check.sh)
- [P3 public contracts](https://github.com/CsHeng/agent-skills/blob/67d15db7e559b9b0abf5a33328cb7355064c6690/contracts/skills.toml)
- 其他事实来源见配套 design；读取日期为 2026-09-20。
