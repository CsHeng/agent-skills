# Design: 面向墙钟时间的规划、执行与显式架构重评

Status: approved_for_implementation。用户已批准本设计与配套计划；行为以实际实施和验证记录为准。

Date: 2026-09-20。

Repository: CsHeng/agent-skills。

Source baseline: `67d15db7e559b9b0abf5a33328cb7355064c6690`。

Companion: [implementation plan](2026-09-20-workflow-execution-economics-plan.md)。跨仓配套为 pi-extensions 的 `2026-09-20-async-subagents-git-worktrees-design.md` / `-plan.md`。两个仓库没有新增运行时依赖。

## SD-01. 目标与决策来源

目标是在既定 goals、验收、用户授权和可接受预算内，减少从开始实施到被接受的端到端人类墙钟时间，同时降低项目长期需要自己维护的责任。不得用最少 token、parent 持续编码、派发数量或当前 slice 的最少代码行代替这个目标。

用户已明确：main 忠实执行 impl plan，清晰的局部工作可以交给更快或更经济的模型；工作流语义不随模型与 reasoning 配置变化。设计与规划可以在一个会话完成，实施通常由新的 main 会话开始，因此 plan 必须足够自包含。

本轮还明确：实现不为是否委派额外调查；已定选型不默认重评，但用户可以显式发起替代评估；`initial write set` 不是永久文件白名单；验证与恢复成本必须对应真实变更风险。

这些是用户意图。下面的 Skill 分工和具体修改是本设计建议，等待确认。没有旧模型会话的因果对照，不能断言历史上过量 hash、演练或 prose gates 必然由 testing Skill 导致。

## SD-02. 当前事实与缺口

作者源在 `src/skills/`，`skills/` 与 `skills.index.json` 是生成物，公开 ID 共 39 个；必须从作者源修改并再生成。[S1]

现有 plan 已区分 goal 与 planning context，但仍在宣称 delegation-ready 时要求 exact write set。实现也要求积极考虑切片，尚未明确禁止为派发收益再做额外调查。这会让 initial inventory 再次变成派发资格障碍。[S2][S3]

`code-simplification` 当前是只读、行为保持的简化审计，默认不实施、不生成计划、不派发。它不是一般性的成熟框架替代入口。[S4]

`testing-strategy` 已限制 prose 字句测试、重复恢复演练，并区分常规测试与策略选择。架构 economics 已涉及维护周期和沉没成本。本次应补足触发边界与语义冲突，不再叠一层同义负向提示。[S5][S6]

## SD-03. 有效范围与不做事项

改变 design、plan、implement、code-simplification、testing、close 及其必要共享 references 的方法语义；同步相关 routing、生成投影和稳定架构说明。

不新增 Skill ID，不新增 executor、工作流编译器、固定评分表、派发估时工具、周期性架构审计或模型价格目录。不在 portable Skill 内规定 Pi 工具参数、Git checkpoint refs、worktree 路径或供应商 scheduler。

本次不重写其他业务项目，不迁移用户项目的框架，不修改 Pi 路由配置，不自动发布、安装、push、部署或调用付费模型。为库与工具保留必要的真实安全边界，不以“省时间”为由取消数据保护或已授权验收。

## SD-04. 规划承担独立性判断，实施不支付第二遍评估成本

### 规划交付的最低信息

`plan-change` 利用完成规划本来就需要的调查，为有实质工作量的任务记录：稳定 task ID、goal / acceptance、repository owner、已知输入和前置产物、预期独立组、必须由 parent 处理的 join、已知共享资源与初始写入区域。具体命名和格式由计划决定，不建立机器 schema 或新增必填表格。

`initial write set` 可以是已知文件或模块区域，遗漏普通实现文件不使计划失效。显式 forbidden paths、生产边界和用户固定接口仍是约束。写入不同 workspaces 不意味着语义独立；公共接口、生成器、依赖锁文件、端口和外部状态需要规划时说明已知影响。

规划可以建议 `delegable`、`conditional` 或 `local`，但这些只是语义提示，不是运行时枚举或批准证书。不要通过 explorer-first 或提前完成 worker 调查来把 conditional 填成 ready。

### 实施时的零新增评估原则

实施只使用 plan、已收集 context 和正常执行顺便获得的信息判断委派。不为判断“开不开户 worker”专门搜索、调用模型、运行探针、估算时长、购买数据或展开实现细节。

有足够依据且 host 支持时积极派发 cohesive slices；依据不足默认 main 直接做下一项有用的实施动作。正常实施过程中自然发现独立工作后可以派发，但不回头建立一个评估阶段。显式用户要求必须委派的任务不被这个默认策略悄悄覆盖，缺少必要输入时报告具体差异。

默认 main 实施不是要求它完成所有任务。两项独立复杂任务可以都交给 children；main 等待、整合和验收完全合理。Async singleton 也可以有收益。禁止按固定文件数、任务数量、秒数或 parent token 比例决定委派。

### 新 main 的交接

计划必须承载当前有效的目标、决策理由、独立性预期、前置输入、join、验收与已覆盖权限。引用本地 design / plan 路径时，说明执行者如何获得它们；未提交文档不能被假定自动出现在新的 checkout。无需把整个前序调查日志复制到 plan。

## SD-05. implement-change 保持单向执行责任

Implementation 消费已经确定的 goals、design 和 plan，不进行架构选型复赛，不自动调用 design-change / plan-change / code-simplification 来重新证明当前方案。局部调查、合理 glue、增加漏掉的调用方或测试文件、更新 initial write set、同任务 repair 都属于实施。

若遇到确实无法同时满足既定 goals / hard constraints 的证据，main 只报告该具体冲突、停止受影响动作，并保留独立授权工作。它不擅自替换目标或框架，也不自行反转整个阶段 DAG。现有 `replan` / `redesign` 结果若保留，只表示需要 owner 决策的真实边界冲突，不表示自动激活上游阶段。

删除本 slice 引入但不需要的 helper / fallback 仍是正常实施清理。用户没有请求时，不能将其扩大为全仓结构审计。完成仍以原验收为准，不能改写验收来制造成功。

## SD-06. 成熟能力复用与显式结构性重评

### 新增通用责任之前

当 design 的材料性选型尚开放，先核实项目已有能力、宿主原语、官方工具和可信社区实现。回答“谁已经可靠地拥有这项责任，以及我们还缺什么”，而不是展示大量候选或用当前功能少为自建找理由。

用户声明的维护周期、团队习惯、未来扩展方向与明确技术选择，是有效输入。现在用 Gin 而不实现未来全部功能，是允许的结构性投资；不能因为当前只有少量接口就擅自改成手写框架。第三方不可靠、许可/平台冲突、显著集成或性能收益仍可支持自建，但需要具体证据。

当证据足够形成选择即停止研究，不要求穷尽生态。已定选择不在每次 plan 或实现重新评分。

### 显式重评入口

保留 `code-simplification` 的普通只读局部审计行为。仅当用户明确要求“结构性简化、替代自建、采用成熟框架、重构/重写取舍、重新评估架构”时，启用 owner-local reference，建议名称 `references/structural-alternatives.md`。

该入口比较继续维护、局部简化、用成熟实现替换这三类现实选择；可以发现一次较大重构/重写更有收益，不能因为已投入很多就坚持原方案。只研究用户指定的仓库/模块，不自动评估所有项目。

输出为 read-only decision evidence：目标责任、候选替代、实际差距、迁移和未来维护成本、受影响契约、是否需要另行设计。它不自动创建 plan、不执行迁移、不将 `recommend-design` 当成用户授权。

用户可显式请求该评估；已经记录的触发信号可以在恰当报告里被提出一次，但不会触发周期运行或每轮 impl 的审计。普通 code-simplification 可以合法得出“没有值得改动的候选”，不制造发现配额。

## SD-07. 测试、保障与成本按同一标准判断

常规执行已有检查、增加普通回归，不自动加载完整 testing-strategy / oracle-selector 方法。只有测试策略本身需要选择或用户请求审计时才展开策略映射。

新增检查、hash、恢复协议、重放日志、部署演练或还原机制，都需对应具体受影响行为与失败模式。已有 Git OID、host identity 或项目机制足够时不另加自定义身份链。不是禁止 hash，而是不因换 revision、修 prose 或一次普通 repair 就自动生成新的恢复证明。

资料表明现有 Skill 已有很多此类限制，本次采用一次 owner-local 澄清并移除有冲突的普遍性措辞，不在所有 Skill 复制负向词表。审查只覆盖本变更命中的 instructions / checkers；不借机做全仓测试拆除。

自然语言 instructions 的语义不能靠断言固定句子、关键词集合或 hardcode `gate` 字样来证明。维持语法、ID、链接、生成一致性与真实 consumer tests。离线情景审阅可以检查方向，但不宣称证明模型行为改善；昂贵 live ablation 不属于本次必过项。

## SD-08. 隔离、同步和 close 的 portable 表达

并行写任务需要独立、可保留结果的工作区，具体由受管 host 提供。同任务多轮复用上下文和工作成果；host 内部隔离不等于要求模型显式运行独立的 `git-worktrees` Skill。后者的用户调用与变更权限保持现有独立边界。

Parent dirty 不阻止开始实现或后续派发；不自动 commit/stash。输入基线、候选整合与测试环境要准确描述，但 Skill 不实现文件复制、Git 合并或后台进程管理。

Close 判断覆盖仍活跃的任务、未集成结果、后续 review/repair 需求与资源保留/回收 disposition。`close-change` 保持语义 owner，不增加 may_mutate_repo 权限；真正的回收交由已有授权的实施 owner 或 executor。不能从业务 fulfilled 自动推导删除用户分支，也不能让正常受管资源关闭每次都重复找用户审批。

## SD-09. 验收

| ID | 验收结果 |
| --- | --- |
| S-AC1 | 39 个公开 Skill ID、provider-neutral 边界与作者/生成关系保持一致。 |
| S-AC2 | Plan 能让新的 main 理解独立切片和 join；不要求 upfront exact file 白名单。 |
| S-AC3 | 派发收益只使用已有信息；信息不足默认本地实施，不创建额外评估预算。 |
| S-AC4 | implement-change 不自动重开设计/规划；新增范围内文件不触发用户审批。 |
| S-AC5 | 结构性替代有显式只读入口，普通简化/实现不自动升级为架构审计。 |
| S-AC6 | 成熟能力优先的判断包含用户声明的维护周期，允许证据支持的重构/重写。 |
| S-AC7 | 验证强度对应真实变更；不靠 prose snapshots 或新增仪式证明收益。 |
| S-AC8 | Close 语义包含执行资源 disposition，且不扩张清理与部署权限。 |
| S-AC9 | 生成与仓库检查通过；无法运行的检查明确列出，不用文档 review 冒充运行效果。 |

## SD-10. 交付、评审与批准边界

交付端点为本仓作者源、必要 references / contracts / generated surfaces / 稳定文档的协调修改与测试报告。计划允许在用户之后确认时为交付建立本地工作分支和本地提交，但不包含 remote push、tag、安装、发布或模型调用。

本轮只有静态源码核查与设计自审，没有独立 reviewer，也没有修改仓库实现。实施时对阶段边界、触发精度和授权语义做一次针对性审阅；后续修复只复查失效证据，不规定评审次数。

## 实施授权记录

2026-09-20：用户批准四份 design/plan，授权在两个仓库副本中实施、运行离线检查、创建本地 Git 提交并返回完整 ZIP。用户随后明确允许 best-effort 交付，受阻项如实记录；不包含远程 push、发布、安装或付费模型调用。

## 来源

所有来源于 2026-09-20 读取。材料事实以对应固定提交为准；设计决策来自本轮用户意图及本文推导。

- [S1 AGENTS / authored truth](https://github.com/CsHeng/agent-skills/blob/67d15db7e559b9b0abf5a33328cb7355064c6690/AGENTS.md)
- [S2 plan-change](https://github.com/CsHeng/agent-skills/blob/67d15db7e559b9b0abf5a33328cb7355064c6690/src/skills/workflows/plan-change/SKILL.md)
- [S3 implement-change](https://github.com/CsHeng/agent-skills/blob/67d15db7e559b9b0abf5a33328cb7355064c6690/src/skills/workflows/implement-change/SKILL.md)
- [S4 code-simplification](https://github.com/CsHeng/agent-skills/blob/67d15db7e559b9b0abf5a33328cb7355064c6690/src/skills/disciplines/code-simplification/SKILL.md)
- [S5 testing-strategy](https://github.com/CsHeng/agent-skills/blob/67d15db7e559b9b0abf5a33328cb7355064c6690/src/skills/disciplines/testing-strategy/SKILL.md)
- [S6 architecture economics](https://github.com/CsHeng/agent-skills/blob/67d15db7e559b9b0abf5a33328cb7355064c6690/src/skills/disciplines/architecture-patterns/references/architecture-decision-economics.md)
