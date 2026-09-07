# Agent Skills 触发边界、执行收敛与上下文组合校准设计

日期：2026-09-07

目标仓库：`CsHeng/agent-skills`

状态：D1–D7 已批准并完成初始 candidate 实施；当前 checkout 策略及后续整合按[用户已批准补充](2026-09-07-checkout-selection-amendment.md)执行。

源码参考及现场核实基线：`809d8e44aac40fd507311bb267bc0400064e6077`；2026-09-07 核实时当前 HEAD 与参考提交相同，后续执行仍需检查漂移。

权限范围：原交接只授权设计与核实；后续用户已授权实施、当前 checkout 策略校准、生成、commit 和 push。未授权全局配置修改、行为实验、强制推送或部署。各阶段实际证据见关联 verification 与补充，不从设计文档自身推导执行授权。

## 本地适配与关联产物

本文由根目录原始设计交接迁入规范的阶段文档目录；保留 D1–D7 及验收语义；稳定架构事实按已验证源码单独维护，不将整份设计作为运行时指令。原始输入 SHA-256 为 `f92f05b445409dfdbad28e68f43fa989e593c2a3069ce7eed6003c4d6d38c4b7`，仅标识迁移前输入，不是本文件当前内容的 hash。

- [现场审计](2026-09-07-skill-boundaries-context-audit.md)：核心问题仍存在；Pi 用户级 AGENTS 已是薄封装，默认 Codex AGENTS 不存在，真实工程样本没有必须重写的已证实流程冲突。不预设用户级配置修改。
- [实施计划](2026-09-07-skill-boundaries-context-plan.md)：纳入 `code-simplification` 相邻调用方的强制 design 跳转校准；具体拆分、写集合与验证由该计划承接，不改变其审计 dispositions。
- 39 个已安装 skills 链接指向当前 checkout 的生成目录。首次计划据此设置隔离与独立整合门槛，现已由用户批准的补充取代：批准 repository source/generated payload 修改即覆盖既有链接的预期后续读取，不再仅因链接存在单独设 gate；真实额外外部作用仍保留权限边界。
- 结构检查基线已通过，98 tests passed；计划权限、依赖、恢复及证据边界的独立评审通过。这些证据不证明候选实现已完成、模型行为改善或成本下降。

## 1. 设计结论与已确认决策

本轮保留共享 skills 中的工程判断、项目约束和权限边界，纠正不必要的适用门槛、阶段跳转及停止条件。目标不是以文件数量、字数或 token 数为指标压缩整套 skills，也不是为单个模型重建一套方法论。

用户已确认以下方向。实现细节可以根据 workstation 当前仓库适配，但不能将这些方向重新解释为相反的默认行为。[^user-decisions]

| 决策 | 本设计采用的语义 |
| --- | --- |
| D1：分开实现 readiness 与委派 readiness。 | 普通实现不因缺少委派 profiles、并行策略或 review 次数预算而被阻断；实际委派才需要对应的责任、隔离和收敛信息。 |
| D2：按验收收敛，而不是按固定次数退出。 | 取消默认一次 repair 限制，也不替换为默认两次硬上限。允许必要的定向复审和多次局部修复，持续追求已授权目标的可验收；不能反向改写 plan 或削弱验收来制造通过。 |
| D3：根据实际决策需要触发 skill。 | 意图、边界和执行要求已经明确时直接实现；不要求先运行 design 才能得出“不需要 design”，也不把 design/plan/impl 当作必经流水线。 |
| D4：按任务分支展开内容。 | 收紧大型根文件的职责，优先处理 worktree 与 project analysis；修复 worktree 默认位置和仓库策略之间的条件冲突。 |
| D5：分类处理指令。 | 保留真实工程偏好、权限边界和模型无法可靠推断的事实；有选择地删减一般性手把手流程，并将运行时强保证留在 host/harness 的责任范围。 |
| D6：在 workstation 审计实际指令组合。 | 审计包括 `~/.codex/AGENTS.md`、`~/.pi/agent/AGENTS.md` 一类用户级配置及真实工程项目上下文，而不是只看 skills 仓库根 `AGENTS.md`。 |
| D7：长期效能评估暂留开放问题。 | 逐步积累可观测数据，但不把 benchmark、消融平台、全模型矩阵或统计收益证明设成本轮修改的前置门槛。 |

D2 在用户接受的“放宽到两次或不限制”范围内，选择**无默认固定次数上限**。次数可以成为某次调用显式预算的一部分，但不能继续作为共享 skill 对所有任务的默认完成判据。

本文是维护者设计文档，不应被整体复制进全局 `AGENTS.md` 或每个 `SKILL.md`。落地时只将必要语义放回各自的长期事实源。

## 2. 背景、证据与不变边界

### 2.1 证据强度

设计输入包括用户提供的《Rethinking skills and prompts for GPT-6 Astra》全文、OpenAI 当前模型指南、上述提交的关键源码，以及用户对真实执行任务的反馈。官方指南提示 Astra 对指令更敏感，可能在用户预期继续时停下，也可能在小任务上过度验证。这些是值得排查的机制线索，不是本仓库已经取得性能改善的实测证据。[^article][^model-guide]

用户报告实际任务中确实存在明确执行意图误触发 design；同时认为 review 总体可靠，尚未观察到无限 review/repair 或持续扩大范围的问题。该反馈支持本轮调整，但不等于已经证明任何模型、任务和上下文组合都不会出现不收敛。[^user-decisions]

原始设计交接编写时仅复核了参考提交的相关公开原始文件，未读取 workstation 的本地配置、未提交修改或真实会话。后续现场核实已读取必要配置、当前仓库与工程指令样本，确认相关问题仍存在；范围和限制见关联审计。两个阶段均未运行受控行为实验，不能将文件核实等同于行为因果证明。

### 2.2 保持现有 ownership

参考架构已经把 skills 定位为可组合的语义能力，而非仓库自带的工作流引擎。分析、设计、计划、实现与 review 独立可选；active coding agent 负责选择、判断和推进。此次修改沿用这一边界。[^composition]

| 责任 | 归属 |
| --- | --- |
| 目标、范围、验收基线及新增权限的确认。 | 用户及适用的仓库、环境策略。 |
| 请求解释、skill 选择、证据判断、review findings 裁决、是否继续修复及最终交付。 | 当前 active coding agent；委派不会转移这些最终责任。 |
| 可移植的工程方法、适用条件、约束与失败语义。 | 对应的共享 skills。 |
| 模型调用、工具执行、会话延续、取消、实际资源限制，以及已有运行时的调度机制。 | 兼容的 host/harness；本轮不新增或实现这类机制。 |

稳定不变量包括：保留公共 skill IDs 与分发结构；不静默改变任务范围、设计、事实依赖或验收要求；reviewer 保持只读；保留无关用户修改；不从实现授权推导 commit、push、发布、部署或外部写入授权。[^repo-agents][^review-change]

本轮不建设 orchestrator、attempt ledger、模型绑定层或强制全局 router；不为 Astra、Sol 等模型复制不同版本的公共 skill 正文；不以“新模型懂这些”为由整体移除工程约束。模型适配可以在实际调用层处理，但不能重新定义共享 skill 的含义。

## 3. D1：实现 readiness 与委派 readiness 分离

### 3.1 需要修正的语义

参考版本的 oracle selector 将 subagent、TDD loop 和 execution runner 放在同一个 work-package gate 下，要求 review budget、delegation policy、execution/reasoning profiles 等信息；`plan-change` 则允许不声明委派就绪的计划省略 profiles。这里应消除条件不一致，而不是再增加一套 readiness schema。[^oracle-selector][^plan-change]

### 3.2 普通实现只需要与当前任务有关的事实

开始已授权的局部实现，应能够确定目标与范围、允许修改的边界、必须保护的行为，以及用于判断结果的证据。相关事实可以来自用户明确请求、已有设计/计划、代码与项目契约，不要求为了满足流程重新生成一个完整工作包。

当现有测试或明确的 reproducer 已足以表达验收时，可以直接执行。只有“什么证据能够证明正确”仍需实质性选择时，才组合 oracle selector；使用 TDD 本身不构成委派，更不自动触发 profiles 和并行元数据要求。

缺失但确实必要的信息仍应补足。例如验收语义互相矛盾，或不清楚是否允许改变公共错误行为，不能假装任务已就绪。但应指出实际缺失的决定，而不是要求填满与任务无关的字段。

### 3.3 委派要求只约束实际委派

实际把可写任务交给另一个 agent 时，仍需明确它负责什么、在哪个仓库和写入范围内工作、如何隔离共享资源、返回什么证据，以及谁负责整合与最终验收。某个计划明确声明 delegation-ready 时，按当前约定提供必要的语义 profiles；这些要求不反向成为主 agent 本地执行的前置条件。

无法安全委派时，默认优先保留在主 agent 执行，前提是这不违反用户明确要求、任务依赖和实际权限。若用户把指定委派方式或并行能力作为硬要求，不能静默改为串行并宣称全部满足；应指出具体阻塞。

oracle selector 应主要拥有验证方法选择；计划和实现入口在实际需要时消费委派准备信息。优先复用已有引用，不新增一个“每个任务必读”的 readiness skill，也不让这些语义变成仓库控制器的运行状态。

## 4. D2：围绕既定验收持续 review/repair

### 4.1 默认取消固定次数限制

参考实现将接受 findings 后的修复限制为一次，并把这一轮未通过直接解释为 `non-convergent`；repair reference 又禁止再次 review。应同时修正这些相关条款，不能只把数字从 1 改为 2，也不能保留一个事实上的“只能 review 一次”来重新制造相同停止点。[^implement-change][^repair-loop]

本设计中的 bounded repair，边界指目标、权限、修改范围和验收语义，不指固定次数。只要仍在该边界内，而且存在有证据支持的下一步，就应继续完成工作。

取消固定次数不意味着形式上保证收敛。固定 plan 仍可能包含矛盾、不可实现前提或不可获得的验收条件；agent 也可能没有有效诊断。因此停止应依据具体阻塞、缺少可行路径或真实预算，而不是“第几次失败”。

### 4.2 以授权的 acceptance baseline 为锚点

有已批准 plan 时，以其目标、约束、真实依赖、权限及验收条件为基线；明确的 bounded request 没有独立 plan 文件时，以已授权请求及适用项目契约为基线，不补造一份 plan 作为准入凭证。

实现可以调整范围内的技术细节、纠正代码、补充真实回归测试、记录执行状态和失败证据。这些属于执行，不等于改变批准的目标。不能为了通过 review 或测试而删除失败要求、改变 non-goals、放宽外部接口契约、改变批准的依赖约束，或自动把目标缩减成当前已经实现的部分。

同样不能把 oracle 当作绝对不可修改的代码。若测试本身写错，而独立的已批准契约清楚说明正确行为，可以在既有权限内修正测试实现，并保留修正依据。若修正实际上改变“什么才算正确”，则属于验收或设计决策，必须交回相应决策者。reviewer 的偏好不能替代该授权。

允许更新进度和附加证据，不允许把计划维护变成对已批准要求的静默重写。

### 4.3 Review 与 repair 的关系

review 仍按明确请求、适用规则或有证据的风险需要触发，不成为每次局部编辑之后的固定动作。每次 review 都有一个确定的目标、验收问题和证据范围；reviewer 返回候选 findings，active agent 裁决其因果关联与是否属于当前任务。[^review-change]

接受的范围内缺陷可以经过多次修复和验证。修复改变了此前 review 所依赖的内容、仍有需要独立判断的问题，或项目规则明确要求复审时，允许定向 rereview。复审应聚焦修复、受影响边界及尚未解决的 findings，不自动重新审计整个仓库。

先前 findings 的处理结论可以复用，但其证据必须仍适用于当前版本。已经裁决且没有新证据的问题，不因换了一个 reviewer 就自动重开；修复引入的新回归，也不能因为“上一轮已经 review 过”而被忽略。是否需要新的独立 review，由当前证据和适用规则决定，不由固定计数决定。

reviewer 不得递归启动新的工作流、修改被审查对象或替调用方决定继续执行。一次 review 调用只返回一次有边界的评价，不等于整个 change 只能调用一次 review。

### 4.4 完成、继续与停止

| 观察到的状态 | 所需行为 |
| --- | --- |
| 已满足授权目标，必要验证通过，必需 review 的有效 findings 均已处理。 | 完成任务；没有新修改、失败或未决风险时，不为了“再确认一次”重复测试或 review。 |
| 验证或 review 暴露可在既有范围内修复的缺陷。 | 继续诊断、修复和必要验证；首轮或第二轮失败本身都不是停止理由。 |
| 证据表明验收条件互相矛盾、批准前提失效，或达成目标必须越出范围。 | 保留当前证据，指出具体冲突和所需决定，返回适用的 replan/redesign 结果；不自行修改验收基线。 |
| 后续工作需要未获得的真实权限、必要输入或环境能力。 | 报告具体阻塞；可独立完成的已授权工作不必一并放弃，但不能把整体结果报成通过。 |
| 诊断重复却没有新证据，也没有可合理尝试的范围内路径。 | 报告为何当前无法继续收敛、已排除什么及还缺什么。不能只用失败次数说明 `non-convergent`。 |
| 用户取消，或达到本次明确的时间、调用、资源预算。 | 遵循实际限制，交付当前状态与剩余工作。预算耗尽不是“plan 已证明不可验收”，也不是成功。 |

“review 证明无法验收”在这里指有可核查证据支持的阻塞判断，不要求数学意义的不可实现证明；单纯一次测试红灯或 reviewer 说“有问题”不足以得出这个结论。

沿用现有 outcome 词汇时，应修改 `non-convergent` 的解释，避免把它绑定为单次修复失败。本轮不要求新状态枚举或 attempt 持久化协议；若已有表示无法区分真实阻塞与预算停止，由本地 plan 选择最小兼容改动。

### 4.5 相关文件的一致性

需要检查实现入口、repair reference、review 入口、路由及任何仍然表述“整个 change 最多一次”的调用方说明。参考版本的 design/plan 入口也有一次修复措辞；若统一调整这些相邻语义，其目标仍分别受已确认的设计输入和规划边界约束，不能让设计或计划通过自我 review 获得用户批准。[^design-change][^plan-change]

尤其要区分“允许继续修复一个已授权产物”与“允许自行批准新设计、改写计划并实施”。前者是本轮目标，后者不在本轮授权内。

## 5. D3：以实际需要校准发现与触发

### 5.1 不再用阶段位置代替适用条件

description 应说明该 skill 解决什么尚待处理的问题，而不是说明它通常出现在某个阶段之前。参考版本的 `design-change` 以 implementation planning 之前作为定位；正文虽支持 `no-design`，仍可能使 agent 必须先进入设计才能退出设计。[^design-change]

判断应直接消费当前请求和有效上下文。用户已经给出明确目标、必要决定和执行授权时，可以直接选择实现。需要调查代码和做局部技术选择，不自动等于需要产出新的设计文档或重新审批。

反过来，用户说“直接实现”也不会消除真实的架构冲突或权限缺口。只有会实质改变范围、兼容性、状态归属、验收或授权的未决问题，才应形成对应的设计/计划决定；应明确指出该问题，而不是惯性启动全流程。

用户明确要求输出 design 或 plan 文档时，该产物本身就是任务，即使其中一些决定已经做过。此时整理既定决定，不重新发明争议，也不擅自进入后续实施。

### 5.2 关键触发边界

| Skill | 应触发的情况 | 不应因此触发的情况 |
| --- | --- | --- |
| `design-change` | 存在实质性设计决定，或用户明确要求形成设计产物。 | 只是要执行已明确的局部修改、已有批准方案，或任务文字包含“数据库”“架构”等领域词。 |
| `plan-change` | 用户要求可交接计划，或确实需要决定任务依赖、执行顺序、协调与验证安排。 | 局部修改不需要独立计划产物；或已有计划仅待执行。 |
| `executable-oracle-architecture-selector` | 尚不清楚什么证据足以验证行为，需要在 oracle 方法之间选择或修订。 | 运行已知测试、按明确契约补一个回归案例，或任务采用 TDD。 |
| `testing-strategy` | 需要设计或调整验证边界、fixtures、测试分层、隔离和执行 lanes。 | 只是执行已有验证命令，或使用已有明确策略实现常规测试。 |
| `use-coding-skills` | 原生直接匹配存在实质歧义，或需要其既有会话边界指导。 | 已直接匹配一个适当 skill；不为了获得其 negative cases 而强制先读取整个 router。 |

参考路由已经支持 direct-match bypass，因此关键排除条件必须在发现阶段可见，不能仅存在于模型尚未加载的正文或 `routing.toml` 内。[^routing]

### 5.3 可用于本地适配的 description 草案

以下是设计草案，不是最终逐字契约；本地可根据发现投影方式和语言风格调整。必须保留“何时需要”及最关键的误触发排除条件，不需要为每个 description 罗列所有反例。

`design-change`：

```text
Resolve material design decisions or produce a requested change design. Use when goals, boundaries, ownership, compatibility, or acceptance need a decision; not to execute an already bounded change or approved plan.
```

`plan-change`：

```text
Create a requested implementation plan or resolve execution ordering, dependencies, coordination, and verification for an authorized change. Not for executing an existing plan or a bounded change that needs no separate planning artifact.
```

`executable-oracle-architecture-selector`：

```text
Choose or revise executable evidence when how to verify a change is unresolved. Use to select oracle methods and protected boundaries; not to run known checks or implement tests under an established strategy.
```

`testing-strategy`：

```text
Design or revise verification coverage, suite placement, fixtures, isolation, and execution lanes for an established oracle. Use for test-strategy decisions or suite audits; not merely to run existing checks.
```

应同步检查正文入口、负向案例与实际分发投影是否表达一致含义。不将 discovery 修正实现为另一个全局前置 router，也不通过减少公共 IDs 规避触发问题。

## 6. D4：渐进披露与局部规则修复

### 6.1 根文件保留什么

根 `SKILL.md` 应足以判断适用性、选择当前操作分支，并遵守进入该分支前需要知道的共同约束。只与某个分支相关的命令、范例和排错细节按需读取。

拆文件的验收不是根文件变短，而是未选择的分支不会被要求一起阅读。若根文件要求“先读全部 references”，只是移动文本，并未改善适用范围。现有 authoring guidance 已包含描述精度、渐进披露及单一长期 owner 的原则；本轮优先应用它们，不再叠加一份重复元规则。[^skill-authoring]

### 6.2 `git-worktrees`

按创建与上下文转移、比较、合并、清理/修复等操作组织按需引用，根文件保留操作选择、权限和防丢失约束。具体新文件名由本地 plan 决定，不新增公共 skill。

需要同时修正位置语义。参考版本一方面要求采用仓库已有 worktree 策略，另一方面把“仓库声明不同位置”列为停止条件。应以适用仓库策略为实际依据；只有请求和策略存在无法自行解决的冲突、目标不明确或操作无法安全执行时才暂停。[^worktrees]

一旦确定实际位置，相关创建、检查、比较和清理逻辑都应消费该位置，不能正文说遵循自定义路径，后续检查却仍硬编码默认目录。操作范围也必须匹配：只读列举或比较不应被创建 worktree 所需的路径设置和上下文转移要求阻断。

保留未提交上下文的显式处理。新 worktree 所需的设计、计划或源文件不能被假定已经存在；已有明确授权且能保真转移上下文的机制可以继续使用，不把“必须先 commit”设为唯一方法。若接收方缺少必要状态，又没有可用的授权转移路径，仍需报告阻塞。[^worktrees]

本次结构调整不自动授予创建、合并或删除 worktree 的权限，也不放宽对未提交工作、独有提交及 cleanup 的保护；原有有效的 Git/search ignore 约束应按照实际操作和路径适用。

### 6.3 `analyze-project`

局部事实查询先读取足以回答该问题的稳定事实源，并做必要的针对性核实。只有用户要求全貌、事实源不明确、文档与实现冲突，或证据不足以支持回答时，才展开术语盘点、完整文档健康判断或代码重建。

参考版本已经区分精简输出与完整 audit；本轮需要让内部读取和分析范围也随问题缩放，而不是最后才把一个完整分析过程压成短回答。[^analyze-project]

保留适用指令、稳定事实与阶段历史的区别，以及只读边界。“少读不相关内容”不等于忽略项目约束；也不能因为默认搜索没有返回内容，就宣称被忽略或隐藏的内容不存在。

## 7. D5：指令分类与保留原则

| 指令性质 | 处理原则 |
| --- | --- |
| 明确的工程取舍、真实需求和必须保护的边界。 | 保留适用条件与理由。例如 ownership、兼容性、状态归属、不能弱化 oracle、不能擅自扩大范围；模型知道概念不代表会选择相同取舍。 |
| 模型无法可靠推断的仓库、工具或环境事实。 | 保留在可信且可维护的事实源，按需引用；避免复制后过期。 |
| 一般开发常识、重复检查、对所有任务规定同一阅读/执行顺序。 | 作为重点删减候选。先判断是否有本项目特殊意义，不能仅凭“模型已经会了”直接删去必要验证。 |
| 用提示词模拟权限强制、资源限制、调度或会话状态机。 | 保留必要语义边界，实际强保证归 host/harness 或环境；本轮不因为发现此类内容就顺带建设运行时。 |

测试调整也按此区分。“一定要多测几轮”可以是多余流程；保护共享函数不同调用方的行为、运行项目声明的生成检查则可能是验收所必需。没有新修改、失败或未决问题时不反复验证，但不能以节省成本为由省掉适用的必要检查。[^testing-strategy]

授权描述应对已知环境事实给出明确边界。例如只有确认某组测试确实使用可丢弃 fixtures、没有生产访问且允许自动修复时，才能据此允许连续执行。不能把官方示例直接当作所有真实项目的事实，也不能从“可逆操作”普遍推导授权。

## 8. D6：真实 workstation 的指令组合审计

### 8.1 审计对象

本轮不能仅审计 skills 仓库自己的根 `AGENTS.md` 就得出“全局上下文没有问题”。实际关注的是所用 model/host 在真实工程任务中看到的指令组合。用户明确要求把用户级配置与工程项目叠加影响纳入现场评估。[^user-decisions]

现场应从当前使用的 agent 入口确认实际配置来源，包括用户指出的 `~/.codex/AGENTS.md`、`~/.pi/agent/AGENTS.md` 一类入口，真实项目及作用域内的指令文件，已安装 skills 的实际副本或链接，以及与本次问题相关的插件、hooks、session continuation 和子 agent 上下文。

这些路径是调查入口，不是对某个 host 当前加载行为的保证。环境变量、自定义 home、安装方式或版本可能改变实际来源。实际优先级、覆盖方式、作用域和重复注入情况应以对应版本可见证据确认，不能假定两个 agent 使用同一种合并逻辑，也不能把上述列举顺序当作统一优先级。

### 8.2 优先回答的问题

现场检查应能定位：是否存在要求所有修改先 design/plan 的全局条款；是否存在重复的“每次修改前先读整套文档”；是否仍有一次 review/repair 或实现首版即交还用户的规则；是否有多份安装副本导致修改未生效；项目和全局权限声明是否冲突；worker 是否拿到了与主 agent 不同的边界。

对具体冲突，指出已读取的来源、适用条件、影响及应修改的 owner。不要默认把所有环境差异修进共享 skills，也不要通过共享 skills 覆盖真实项目更具体的要求。

文件存在、文件被加载、文件导致了某种行为，是三个不同的判断。优先利用可见配置、加载记录和实际执行痕迹；agent 对自己为何停下的解释可作为线索，但不能单独证明因果。host 不暴露的 system prompt、上下文处理或插件行为应标记为未知，不推断它们无影响。现有评估方法也要求区分激活证据与模型自述。[^skill-evaluation]

### 8.3 修改边界与验证对象

skills 仓库内的源文件改动与 workstation 用户级配置改动应能够分别审查和回退。审计并不授权批量重写 `~/.codex/`、`~/.pi/` 或所有项目；修改具体全局/项目文件前，核对本次工作授权，并保留适用约束。

skills 仓库根 `AGENTS.md` 仍负责自身维护契约，包括源码与生成物关系、分发和校验要求。它可以被纳入组合检查，但既不应作为通用 agent 行为的唯一实验环境，也不应为了模拟普通项目而删除自身必要规则。[^repo-agents]

若全局条款中确实重复定义了公共 skill 的流程，优先将长期语义保留在 skill owner，用户级配置仅保留用户偏好、环境约束和必要的薄路由提示。这与既有路由对 environment instructions 的边界一致。[^routing]

现场审计是本次维护任务的一部分，不应被写成“以后每次编码前审计整套 workstation”。证据收集也应只覆盖必要配置与轨迹，不采集或导出凭据和无关会话。

## 9. 预期变更面与分发约束

以下是基于参考提交的定位入口，不是保证当前 HEAD 相同的完整文件清单。局部新 reference 的名称、现有测试的具体落点和源码迁移，由 workstation 的 plan 根据当前树确定。

| 变更面 | 预期调整 |
| --- | --- |
| `src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md` | 收紧触发；解除普通实现与委派元数据的错误绑定；让 readiness 回到实际适用条件。 |
| `src/skills/workflows/implement-change/SKILL.md` 与 `references/repair-loop.md` | 改为基于验收和证据的继续/停止语义；取消默认固定 repair 次数；允许必要定向复审。 |
| `src/skills/workflows/review-change/SKILL.md` 及相关 review 调用方 | 区分每次有边界的 review 与整个任务的总调用次数；保留 reviewer 只读和调用方裁决。 |
| `src/skills/workflows/design-change/SKILL.md`、`src/skills/workflows/plan-change/SKILL.md` | 改善入口与 description；排除已明确执行任务；检查相邻 repair 条款但不改变批准权。 |
| `src/skills/disciplines/testing-strategy/SKILL.md` | 区分策略设计与常规测试执行；避免因为使用现有测试方法而重新进入 oracle/plan 流程。 |
| `src/skills/session/use-coding-skills/references/routing.toml` | 补齐相关触发反例并校准直接匹配语义，不改成强制 router。 |
| `src/skills/git/git-worktrees/` | 按操作渐进披露；统一仓库位置策略；让 preflight 与实际操作相称；保留上下文与数据保护。 |
| `src/skills/workflows/analyze-project/` | 让局部查询、证据不足后的扩展和完整 audit 对应不同读取深度。 |
| `contracts/skills.toml`、生成投影和必要架构说明 | 仅在真实契约、依赖或投影需要同步时修改；不顺带扩大权限或重建分发架构。 |
| workstation 用户级与真实项目指令 | 独立记录组合冲突和修改建议；只有相应修改获得授权后落地。 |

参考仓库将 `src/skills/` 作为 authored truth，`contracts/skills.toml` 管理公共身份和发现等契约；`skills/` 与 `skills.index.json` 属于生成物。应从真实 owner 修改并重新生成，不手工修补安装投影。[^repo-agents][^contracts]

参考版本的根 `AGENTS.md` 要求在相关源码和架构改动后运行：

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

以上命令仍是当前仓库维护要求；现场核实已运行 `bash scripts/check.sh` 并通过，未执行修改生成物的前三项命令。未来 candidate 必须按关联计划重新生成和验证，不能复用修改前基线冒充新版本通过。通过这些检查可证明对应的结构、生成和一致性属性，不能据此宣称真实模型已经减少误触发或降低成本。[^repo-agents][^skill-evaluation]

## 10. 本轮验收语义与回归边界

本轮需要证明改动一致表达已选语义，分发产物正确，且没有削弱权限和验收边界。不要求先证明整套 skills 相比无 skills 存在统计收益。

以下案例用于指导文本审查和已有验证机制的适配；不是一份已经运行过的 benchmark，也不要求为每一行建设自动 agent runner。

| 情境 | 期望行为及受保护边界 |
| --- | --- |
| 用户要求执行一个目标、范围和验收都明确的局部修改。 | 直接实现，不先产出完整 design/plan，也不调用 design 只为得到 `no-design`。 |
| 用户明确要求形成设计或计划文档。 | 交付对应产物；既定决定不重审，未获授权的后续实现不自动启动。 |
| 表面上是直接执行，但实际发现互相矛盾的接口或权限要求。 | 定位最小真实决定，报告证据；不以直接执行为由越过边界。 |
| 本地主 agent 执行已知验证或补明确回归案例。 | 不要求 execution/reasoning profiles、parallel policy 或固定 review budget。 |
| 准备委派但写入范围、隔离或收敛责任不清。 | 不把切片声明为可安全委派；在用户要求允许时由主 agent 执行，否则报告相应阻塞。 |
| 第二次甚至后续修复仍有范围内缺陷，但有新的有效诊断。 | 继续围绕相同验收基线收敛，不因次数终止；必要时允许定向复审。 |
| 修复本身引入新的回归。 | 使用当前证据修复；不能以旧版 review 已通过替代对新版受影响边界的判断。 |
| review 发现 plan 的验收前提无效，或只能扩大范围才能完成。 | 返回有证据的设计/计划决定需求；不自动编辑 plan 或弱化 oracle。 |
| 出现不相关、已存在或无新证据的重复 review 意见。 | 保持有依据的裁决，不将其自动纳入当前修复，也不被迫无限重新审计。 |
| 仓库已定义不同于 skill 默认值的 worktree 位置。 | 在权限内遵守该位置；检查与命令消费实际位置，不仅因“不同”而暂停。 |
| 创建 worktree 时必要任务上下文未提交。 | 使用已有明确授权的保真转移方式，或报告真实缺口；不假设新 worktree 自动继承。 |
| 用户只问一个局部项目事实。 | 定向取证并回答；证据不足时才扩大读取，不固定进行全项目健康审计。 |
| 修改了生成式 skills 源文件，或项目声明了必要检查。 | 执行适用的维护与验收检查，不把“避免过度测试”用作省略必要检查的理由。 |
| 当前任务已满足要求，没有新变化或风险。 | 完成，不为消耗预算而继续 review、测试或优化。 |

对自然语言改动，不新增逐字断言、关键词集合断言或 prose snapshot 来假装证明模型行为。保留 frontmatter、链接、结构化契约、嵌入命令、生成一致性及真实消费者接口检查；有授权且值得成本时再补行为场景。参考测试策略已明确这一边界。[^testing-strategy]

交付说明应区分“源码与分发已验证”“在某个实际会话观察到预期行为”“行为尚未实测”。若部分 workstation 上下文不可见，保留该限制，不阻止可以独立完成的仓库一致性修正，也不把未知项计作通过。

## 11. D7：长期可观测性与评估的开放问题

正式评估方案本轮不定型。既有 `agent-skill-evaluation.md` 可以保留为按需方法参考，不扩展成默认 CI gate 或每次任务的实验义务。[^skill-evaluation]

后续值得积累的是能辅助定位判断的低干扰证据：任务及实际验收结果、使用的 model/host 与 skills 版本、可见的指令来源、实际触发和停顿、修复与复审过程，以及能够可靠取得的时间或成本。优先利用已有会话与执行记录；这些信息方向不是本轮必须实现的统一事件 schema、日志平台或持久化服务。

尚待决定的问题包括：

- 如何区分 description 误触发、全局/项目规则冲突、证据不足和模型自身判断，而不把模型自述当作因果证明。
- 如何从真实任务抽取有代表性的案例，同时避免为了可重复性抹掉真实工程环境的重要约束。
- 如何保留可比较的版本与有效上下文证据，并识别重试、恢复、缓存、子 agent 和安装副本造成的污染。
- 何时值得比较当前 bundle 与候选 bundle，何时另做无自定义 skills 对照；两类对照回答不同问题，不相互替代。
- 如何定义有价值的收敛、无效反复与必要人工决策，以及在何种证据下才需要重新引入某类调用预算。

自然执行记录可以发现趋势和失败模式，但未经控制的环境变化不能直接支持“某条 skill 节省了多少成本”的因果结论。未知或不可比的数据保留为未知，不补零，也不只保留成功运行。

长期希望得到的是可追溯的判断辅助，而不是迫使所有任务先满足一个评估体系。本轮不确定统一采样量、统计阈值、强制模型矩阵、固定提示词全集或自动调参机制。

## 12. 交接与本地适配要求

2026-09-07 的现场核实已完成，事实及可见性限制见关联审计。接手实施时复核当前 HEAD、工作区修改、设计内容及安装链接相对记录是否漂移；没有新证据时不重复整套 workstation 审计，也不因交接重新做泛化设计。只有新证据真正影响既定边界时才提出具体变更理由。

关联实施计划已将共享 skills 改动、生成与检查、隔离 candidate 和条件整合分开；本轮不含 workstation 用户级配置写入。具体文件拆分和执行顺序由源码依赖决定，不照抄本文件章节顺序制造任务依赖；不因为包含“评估”就先建设实验平台。该 candidate 计划后来已获用户明确实施批准；新的 checkout/整合决定见关联补充。授权来自用户，不来自设计整理或评审成功。

最终实现仍应维护同一事实链：已确认目标和验收决定什么需要完成；实际证据决定是否完成或被什么阻塞；review 提供受边界约束的判断；plan 不能被反向改写成当前实现的说明书。

---

## 参考资料与来源

以下仓库链接固定到源码参考提交，访问日期均为 2026-09-07。它们用于解释本设计对应的旧语义与文件位置；现场实施应读取当前版本。来源说明不应复制进日常激活的 skill 上下文。

[^user-decisions]: 本对话中用户在 2026-09-07 对审计建议的逐项反馈：接受 readiness 分层、触发调整、渐进披露和指令分类；认为一次 repair 过紧，接受两次或不设限制，要求持续追求既定 plan 的可验收且不得反向自动改计划；将 AGENTS 审计范围明确扩展到真实 workstation 用户级与工程项目上下文；将长期评估留为开放问题。这是需求和经验反馈，不是外部实验报告。

[^article]: 用户在本对话提供的《Rethinking skills and prompts for GPT-6 Astra》全文与 description 示例图片。本设计不假定一个未提供的独立发布地址，也不把其中的模型行为描述视为本地运行证据。

[^model-guide]: OpenAI，Model guidance，Prompting best practices / GPT-6 Astra behavior、Initiative and follow-through、Instruction following、Testing and verification。`https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra`

[^composition]: 仓库架构，Skill Composition。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/docs/architecture/skill-composition.md`

[^repo-agents]: 仓库根维护指令，Truth And Generated Surfaces、Skill Composition、Working Rules、Validation。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/AGENTS.md`

[^oracle-selector]: Oracle selector，description 与 Work-Package Readiness。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md`

[^plan-change]: Plan Change，入口、委派条件、review/repair 及批准边界。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/workflows/plan-change/SKILL.md`

[^implement-change]: Implement Change，Implement And Verify、Review Adjudication、Outcomes。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/workflows/implement-change/SKILL.md`

[^repair-loop]: Focused Implementation Repair。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/workflows/implement-change/references/repair-loop.md`

[^review-change]: Review Change，调用范围、read-only evaluator、候选 findings 与调用方裁决。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/workflows/review-change/SKILL.md`

[^design-change]: Design Change，description、适用条件、Design 与 Decision States。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/workflows/design-change/SKILL.md`

[^routing]: 安装路由引用，direct-match bypass、environment instructions 与 trigger cases。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/session/use-coding-skills/references/routing.toml`

[^skill-authoring]: Skill Authoring，Description Quality、Progressive Disclosure 与 Activated Instruction Content。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/policies/development-standards/references/skill-authoring.md`

[^worktrees]: Git Worktrees，Core Policy、Context Preservation、Path Policy 与 Failure Conditions。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/git/git-worktrees/SKILL.md`

[^analyze-project]: Analyze Project，Workflow 与 Operating Rules。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/workflows/analyze-project/SKILL.md`

[^testing-strategy]: Testing Strategy，description、Documentation And Markdown Verification 与 Oracle Integrity。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/disciplines/testing-strategy/SKILL.md`

[^skill-evaluation]: Agent Skill Evaluation，普通修改不强制实验，激活与污染证据、独立验收和结论边界。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/src/skills/disciplines/testing-strategy/references/agent-skill-evaluation.md`

[^contracts]: Skills 分发契约，公共身份、authored sources、activation modes 与语义属性。`https://raw.githubusercontent.com/CsHeng/agent-skills/809d8e44aac40fd507311bb267bc0400064e6077/contracts/skills.toml`
