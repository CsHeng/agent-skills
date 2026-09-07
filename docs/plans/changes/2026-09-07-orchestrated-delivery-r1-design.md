# Agent Skills：目标对齐、编排式执行与可验收委派设计

修订：R1 本地适配 / 2026-09-07。保留同任务多轮 parent-child 通信与 worker/reviewer 复用需求，并根据当前仓库区分已实现语义、待修改语义与 host 能力缺口。

第 15 节是 R1 新增需求；第 16 节限定本仓库本轮实施范围与证据等级，不撤销第 15 节需求。具体 transport、schema、存储与生命周期策略不是已实施能力，也不是本仓库的实现责任。

迁移输入为根目录 `agent-skills-design-r1.md`，迁移前 SHA-256：`ceaa13139e7a3d53e56b0ea622b9b56bf56c65165892a988035ae199ad7121a3`。输入所记更早原稿 SHA-256 为 `e099a8115058d7f6fa2b132f6bb30ecc33519c53458a35a5726c16b4936837d2`，两者不是同一版本。本文独立保留完整需求，不再依赖根目录副本。

日期：2026-09-07。

目标仓库：`CsHeng/agent-skills`。

状态：输入标明需求与总体方向已确认；本次用户授权核对现状、适配迁移及规划，未授权实施。适配后的实施范围与计划待批准；本文不是已实施记录，不继承上一轮安装、付费实验、提交、推送或部署权限。

本地核对基线：`55fc1a56454679b3f83ea3d2f812fb256bf4f62f`；开始时工作区仅有输入设计这一未跟踪文件。后续执行仍须重新核实 HEAD、工作区和实际可用能力。

配套设计由 `pi-extensions` 仓库维护。本文不依赖其未提交文件或固定路径，也不要求其先实施。后续唯一设计引用为本文件；实施计划见 [R1 实施计划](2026-09-07-orchestrated-delivery-r1-plan.md)。

## 1. 已确认结论与版本取代关系

**Main agent 是 orchestrator；worker 是目标与状态范围受限、但应具备完整局部开发能力的 coding agent。** Main 保留目标解释、任务分解、调度、跨任务综合、权限判断、review 裁决与最终验收责任；调查、实现、测试、诊断和局部修复劳动可以委派。最终负责验证，不等于每个验证命令都只能由 main 执行。

用户明确希望尝试更多有价值的 worker 并行，以便在整体可验收、真实费用可承受、wall time 更短的条件下，保留 Astra main，并把更多执行工作交给 Sol、Terra、Grok 等适合的 workers。模型名称表达本次使用目标，不成为共享 skills 的永久路由或能力判断。

本文整合前序 `design.md`、`design-v2.md`、`design-v3.md` 及用户最新接受的五项讨论，作为本仓库这轮增量修改的独立需求输入。它不是旧文件的机械拆分：

| 旧表述或潜在误读 | 本轮统一语义 |
| --- | --- |
| Worker 是无 shell 的精确文件编辑器，完整执行能力只是以后再评估的升级。 | Skills 按完整局部执行者定义合适任务，消费 host 实际能力；不能假定每个 host 已支持 shell，也不能永久把 worker 写成 oneshot 编辑器。 |
| Parent owns verification / repair，所以测试、诊断和修复都应留在 parent。 | Parent 拥有验收与修复裁决责任；执行反馈回路可由 worker 完成，整合检查也可委派。 |
| 增加 worker 调用不是目标，因此只需允许偶发 offload。 | 增加有效并行是明确选择的试验手段；不设置调用配额、不硬拆无价值任务，但应主动寻找适合委派的实质工作。 |
| 必须穷尽实现细节或先完成 explorer 调查才可派发。 | 先固定目标、契约和状态归属；worker 自行调查范围内的实现问题。只有真正影响分工的未知才需前置解决。 |
| 一次派发被拒即可回落 parent；压缩后忘记委派只能重读全部 skills。 | 区分可恢复调用错误、能力不足和语义失败；从真实能力与有效任务状态恢复，不无条件接管或全量重载。 |

上一轮已落地的 readiness 分层、取消固定 repair 次数、避免 design/plan 误触发、渐进披露和 current-checkout 默认继续保持。现场若发现后续已实现本文部分内容，直接复用，不重复立项。历史设计中与本文冲突的限制，不再作为本轮需求。[^prior][^user]

## 2. 目标、成功判断与非目标

### 2.1 优化整个交付单元，而不是单个工具调用

在稳定验收和权限边界内，关注总费用、真实交付经过时间、重复人工决策，以及 main 需要重新调查、重写或接管多少工作。更低的 parent token 占比、更多 worker 启动、更高并发或更长计划，单独都不能证明成功。

Main 不应提前替 worker 完成全部分析，再把剩下的代码输入工作交出去；也不应收到结果后无条件重做所有调查和测试。目标是转移内聚的工作与执行反馈，而不是增加一次传话。

同时，orchestrator 定位不禁止 main 亲自完成琐碎修改、紧密耦合的整合或当前没有适配执行者的工作。不要把“尽量委派”变成另一种流程仪式。是否继续本地执行，由实际协调成本、能力和任务边界决定，而不是统一比例。

### 2.2 本仓库不承担的工作

不新增默认激活的公共 pre-design / grill skill，不建立强制 design→plan→impl 流水线。不建设任务账本、计划编译器、调度器、模型绑定层、sandbox、遥测采集器或 compaction hook。不复制 Astra/Sol 专用版本，不在共享 skill 中写价格、并发数和机器权限。

不把全文注入全局 `AGENTS.md`，不以 benchmark、全模型消融或长期遥测平台作为本轮修改前置条件。`/plan` 用户没有使用，不纳入本轮原因分析或行为改造。

## 3. 当前证据与待验证假设

参考版本已经把 skills 定位为可组合语义能力，而非第二个运行时；普通实现与实际委派 readiness 已分开，review/repair 按既定验收和证据继续。沿用这些架构，不重新迁移一个不存在的 skills 工作流引擎。[^composition]

本轮需要重点校准的现有措辞，是 `plan-change` 与 `implement-change` 中 parent-owned verification / repair / continuation 的边界，以及委派前需要的准确程度。现有计划支持条件性 delegation-ready，执行入口要求保留授权写集合；这些约束本身不应取消，但不能解释为必须由 parent 执行全部局部反馈。[^plan][^implement]

用户观察 worker 触发少、派发容易被拒后回落 main；提出 compaction 后能力或委派意图丢失的可能。原因还包括 worker 实际工具能力不足、计划过细或过粗、任务不适配，以及分工准备成本。这些是需区别验证的假设，不能把其中一个直接写成已证明根因。[^user]

输入设计的证据来自公开固定版本，而非真实 workstation；其中 DNS/clone 限制属于输入形成时的历史条件。本次本地适配已直接核对当前 authored skills、稳定架构、契约、检查入口与相关测试，并核对相邻 host 仓库的有限角色源码及当前工具接口；具体发现见第 16 节。用户报告 session 已重载，不等于所有 child 已加载候选语义。未进行真实 worker 开发、续接或成本对照实验，也未验证拒绝与 compaction 的因果根因。

## 4. Ownership 与跨仓库约定

| 责任 | Owner 与限制 |
| --- | --- |
| 用户目标、非目标、重要取舍、真实数据与外部操作权限。 | 用户及适用的项目/环境约定。Agent 不能把自写计划当作授权来源。 |
| 请求解释、任务细化、选择执行者、综合证据、裁决 findings、最终接受交付。 | Active main agent。可以委派辅助分析与验证执行，不转移最终责任。 |
| 有界事实调查。 | Explorer；worker 也可以调查自己负责的部分，explorer 不是其必经前置。 |
| 范围内实现、局部测试和基于反馈的修复。 | Worker，前提是实际 host 具备任务所需工具和环境。 |
| 独立评价与候选 findings。 | Reviewer。不得修改被审查源码或替 parent 决定通过、改范围、继续执行。只读源码不等于在所有 host 上永远禁止私有验证命令。 |
| 工具能力、状态隔离、调度、取消、结果完整性、源码导出及遥测。 | Host 与 `pi-extensions`；不根据自然语言 plan 自行授予能力或作业务验收。 |
| 可移植的方法与触发边界。 | `agent-skills`，不保存真实环境许可或执行状态。 |

两仓库使用同一条约定：**Child 返回有边界的候选成果和可核查证据；host 保证其所声明的机械执行与状态边界；parent 判断证据是否足以满足既定目标。** 进程成功、报告完整、源码导出成功、局部检查通过和最终验收通过，是不同事实。

该约定不是新的 JSON 协议或机器可解析 plan。Skills 表达语义；Pi 选择其支持的具体字段和执行机制。

## 5. 按需目标校准，不引入默认访谈

### 5.1 触发依据

只有出现具体的目标—手段错配、验收歧义、重要取舍或权限缺口时，才展开目标校准。用户已经明确执行目标和边界时直接推进，不先进入 design 再得出 `no-design`。

区分用户想获得的结果、已决定的硬约束和仍可替换的实现手段。不能因为用户指定了工具或方案就假定其没有想清楚；也不能用模型偏好的方案覆盖已批准决定。

### 5.2 决策负担归属

可从授权范围内的代码、文档、配置和工具查明的事实，由 agent 做针对性调查。已委派的局部实现选择，由执行者依据项目惯例和约束决定。真正改变目标、对外行为、重要状态、验收或权限的决定，才提交有权决定的人。

提问前应能说明不同合理答案将改变什么；还要判断该决定是否已经委派、是否必须现在作出、能否等待更便宜的运行证据。需要原型或实验才能回答的问题，不靠更多问答制造确定性。调查同样要与当前决定相称，不升级为全仓审计。

问题应携带必要证据、推荐判断和后果，而不是把设计工作重新包装为用户问卷。不固定“最多几个问题”，也不追求遍历所有设计分支。

### 5.3 结束与记录

下一步已经能够在现有授权内可靠推进，剩余未知可通过调查、实现、验证或合理暂缓处理时，结束澄清。只有新证据实质影响已确认边界时重开对应决定；换模型、换 reviewer 或换实现方式不构成重开理由。

把关键决定及必要理由写入既有 design、plan 或需求事实源，不让其只存在于聊天中。未知事实、实现假设、推荐与用户批准应明确区分。不新增每个问题的永久 ID 或独立需求数据库。

详细方法优先放在 `design-change/references/goal-alignment.md`，根文件仅条件引用；文件名可按当前目录适配。现有显式 stress-test 继续保留，不扩散为普通任务默认流程。实现中只需澄清一个问题时，解决后返回原任务，不因此调用完整 design workflow。[^design]

## 6. 项目交付边界：消费已有授权，持续到真正完成

### 6.1 分开任务、授权和能力

某个动作属于本次目标、已经取得相应授权、当前具备执行能力，是三个独立判断。常设部署权限不把“写 design”变成部署任务；计划包含部署也不授予部署权限；凭据存在更不等于获得操作许可。

当动作确属本次任务，可信项目约定或当前请求已经覆盖其目标和副作用时，核实必要前提后执行，不重复征求相同批准。只有新增目标、真实副作用或边界冲突时解决那个增量问题。

Plan 应区分 required authority 与 missing authority。必要但已经覆盖的权限不能一律列成 manual checkpoint。下游步骤缺少能力时，准确阻塞该步骤，不阻断仍可独立完成的授权工作，也不把局部完成报告成端到端完成。

### 6.2 项目事实源承载具体许可

在真实项目既有 `AGENTS.md` 或直接引用的交付文档中，维护用户确认的简短约定：任务何时需要交付、目标 remote/ref/environment、要保护的状态、已授权操作、完成证据及需要暂停的例外。

候选语义如下，**不是对任何真实项目的授权**：

> 当任务要求实现并交付时，完成包括适用检查、仅提交本任务变更、正常推送到项目指定目标、通过既有机制更新指定环境，以及取得对应版本的运行验收证据。已确认范围内不逐步重复询问；目标、副作用、数据保护或权限发生实质变化时，暂停受影响动作并说明具体缺口。

Workstation 从已有事实填入目标和批准来源；确实缺少的权限才提交用户。不要批量重写所有项目，也不要在共享 skill 中增加“未商业化模式自动允许 push/deploy”。Push 所携带的全部待推送历史及其触发的 CI/CD，均属于实际操作边界。

### 6.3 验证与恢复按实际变化缩放

未商业化不证明没有独有数据或真实用户。判断应依赖本次变化、状态价值、影响范围与旧证据是否仍有效，而不是项目标签。

普通逻辑修改未影响持久化和恢复路径，不默认追加完整 backup/restore 演练。修改 migration 时验证实际使用的状态转换，不能以空库初始化替代现存状态升级。修改 backup/restore 本身时，恢复就是本次产品行为，应获得相应验证。项目已有明确且适用的要求仍应遵守，不能为省时间静默跳过。

这些语义由既有 oracle/testing owners 按需维护，不新增一套风险评分、固定审计清单或每次开工前的环境预演。

## 7. 计划精度：固定决定边界，不替执行者穷尽开发过程

### 7.1 计划必须传递的内容

对实际需要计划的任务，保留目标、非目标、重要理由、对外行为、验收和交付终点、真实依赖、状态归属、已覆盖与仍缺的权限，以及执行者可自行决定的空间。局部变量、helper 结构、每次命令、全部可能失败分支，不应无条件提前固定。

共享 skill 保持模型中立。Astra 规划、Sol 执行或反向组合都消费同一基线；不得因换模型重问已经解决的问题，或把“允许细化”解释为扩范围。

### 7.2 两次具体化

**规划时**确定稳定、可验收的行为切片，能明确的写入面、依赖和资源直接记录；仍需局部调查的地方标为条件性委派，不虚构准确文件。普通实现不因缺少委派元数据而被阻断。

**实际 dispatch 前**，parent 根据当前 host 契约确定读范围、具体源码写集合、执行环境与必要输入。已有任务边界允许的局部调查和细化属于执行，不要求重新批准整个 plan。不能为填准文件名先替 worker 完成全部算法和实现设计。

已经声明 delegation-ready 的任务仍应真实就绪。若 plan 明确批准了精确文件、接口或固定执行顺序，不能自行扩大；若只是模块级已批准范围，parent 可在该范围内细化和协调归属。范围内资源重新分配通常是 parent 的职责；只有改变用户保留的决定才上升为人类问题。

### 7.3 按内聚成果切分

Worker slice 默认可以同时包含调查、实现、直接测试、命令反馈和局部 repair。不按“一文件一 worker”或“代码与测试必须分给不同 worker”切分。Explorer 用于值得单独或并行调查的事实问题，不是每个 worker 的启动 gate。

多个接口和输入已稳定、源码写入与共享资源不冲突的切片适合并行；singleton offload 在 host 与适用调用策略允许时也有价值，不需要先凑第二项工作。不能用共享 skill 覆盖当前 host 更窄的 singleton 或委派限制。共享接口、生成器、lockfile、注册表、fixture、端口和外部状态需要明确 owner；文件不重叠不证明任务独立。

真实依赖才构成串行顺序，文档章节顺序不构成依赖。需要 parent 综合、授权、跨任务协调或裁决的位置保留决策边界；“某项验证命令需要运行”本身不再自动构成 parent 必须介入的边界。

不得将整份 plan 编译成静态 worker→reviewer→repair 链绕过 parent 的语义裁决。兼容 host 可消费没有中间决策的真实依赖；具体 DAG、队列和工作空间由 host 负责。

### 7.4 切片示例，不是新的模板门槛

一个可交出的任务可以是：“按已冻结的输入契约修复解析行为，保护已有错误分类；自行定位实现和直接回归测试，在获准文件内完成修改，运行已有检查并修复本次造成的失败；不改公共 schema，返回候选版本和检查证据。”

Parent 只需在 dispatch 时补该 host 必要的准确文件和可访问输入。另一个独立切片可以消费相同冻结契约实现报告展示；公共 schema 若尚未决定，应先解决那个真实依赖，而不是让两个 worker 各自发明它。

## 8. 实施语义：主动委派，并允许 child 自主闭环

### 8.1 正向行为

对于有独立交付价值、具备足够边界且 host 能执行的实质任务，main 应优先考虑委派；多个就绪独立切片优先并行。不先自行实现，再形式化地找 worker 做边角工作。

Worker 可以自行读取授权上下文、复现、编辑、运行适用测试、解释错误并继续修复。无需每轮 red-green 返回 parent，也不重新运行完整 design/plan 生命周期。范围内批量编辑可以合理；不因“批量”一词就禁止，不因只改一个文件就认为安全。真实工具与状态 guard 由 host 保证。

Review role 不能修复被审查源码；worker 的自检不等于独立 review。Parent 可委派整合检查或定向修复，但仍裁决结果是否满足本次目标。

### 8.2 继续与停止

在同一验收基线内、有新的有效诊断或合理下一步时继续局部修复，无默认一轮或两轮硬上限。编译失败、测试失败、一次安全拒绝后的可修正误用，不是自动退回 main 的理由。

需要更改目标、验收、重要接口、超出真实权限，或出现跨任务归属冲突时，交回对应决策者。无法取得必要环境、没有有效诊断路径、用户取消或实际预算到达时，保留证据报告具体阻塞。预算停止不等于目标不可实现。

完成要求已满足时结束；不因仍有额度而继续优化、重复 review 或全仓扫描。

### 8.3 派发拒绝后的恢复

区分调用参数或 admission 失败、child 内安全拒绝、环境/路由失败、最终报告不完整、源码导出冲突，以及业务结果不满足。一次无 child 启动的字段错误，应优先在原授权内修正并重发，不自动把整项实现收回 main。

子任务确实不适配、能力不可用、协调开销过高、重复失败没有进展或预算不支持时，parent takeover 是有效选择，不应成为禁止事项。不能用重复派发逐步扩大权限，也不通过修改 plan、删验收或隐藏模型 fallback 让调用变绿。

稳定错误码和机械状态由 host 提供，skills 只说明如何使用。Parent 的语义 repair、接受与 takeover 若没有明确记录，后续不能仅凭工具成功状态或相邻消息推断。

## 9. Brief 与验证证据：减小上下文，不丢目标

### 9.1 Brief 的责任

Brief 应使没有原对话的执行者理解本切片结果、与父目标的关系、不可改变的行为、重要理由、允许自行决定的实现空间、可访问材料、源码归属和完成证据。

不要求填满统一大表。简单切片几句话足够，复杂任务才增加必要摘录。关键文档未提交、被忽略、跨 checkout 或未进入 snapshot 时，传入有界摘录或实际可读来源；路径字符串不是内容传递。

不假定 child 继承 main 的全部 skills、对话和上下文，也不假定其完全没有项目指令。实际继承由 host 证明。不能为补 brief 自动加载整套 skills 或将主会话全文复制给所有 children。

### 9.2 返回证据与接受权分离

Worker 返回实际变更、候选内容身份、执行过的检查及其真实状态、未执行或失效的验证、必要日志位置和仍存在的阻塞。候选身份可来自 host 快照/diff 标识，不要求为获得版本号先 commit。

测试证据必须对应最终候选。后续修改影响了某项检查，原证据不能继续冒充新版通过。依赖未导出的临时源码修改而获得的绿灯，也不能在丢掉那些修改后复用。

Parent 复用仍适用的局部证据，安排组合后受影响的验证及未覆盖验收。多个局部绿灯不保证组合正确；但 parent 也无需重复每条可靠且仍适用的检查。需要的验证执行可再次委派，接受结果的决定留在 parent。

### 9.3 验收不可被反向改写

已批准目标、非目标、重要依赖、权限和验收在 repair 中保持稳定。可以维护进度、添加证据、在明确独立契约下修正错误的测试实现；不能删掉失败要求、放宽断言或把 plan 改写成当前实现的说明。

Reviewer 返回候选 findings，不授予新的需求或修复范围。已有裁决在证据仍有效时复用；必要定向复审由新变化或未决问题触发，不进行无限全面重审。[^review]

## 10. 长会话与 compaction 后的连续性

用户提出的 compaction 影响是待验证假设。Skills 不应宣称每次压缩都会丢工具，或通过强制全量重读来“修复”。

语义上需要保留：当前目标与验收基线、已确认授权和决定、各工作切片的实际状态、已返回但未裁决的结果、真实阻塞、仍适合委派的下一步。使用已有 plan、进度和可信 host 结果，不创建一套重复 mission ledger。

区分 capability、guidance 与任务委派状态。前两者的持久来源和恢复由 runtime 负责；parent 从有效资料恢复后续决定。工具不可用与“不值得委派”不能混同，旧摘要中的 running/failed 也不一定是当前状态。

恢复时先核对已有结果和实际变更，不重复派发已完成或仍在执行的工作，不凭压缩摘要覆盖源码，不把待验证候选误当已接受结果。无需每次 compaction 人工重新批准范围内继续执行。

将必要薄语义放在既有 session/implementation owner；不要为这一问题新增强制 router 或要求每天审计 workstation 的全部配置。

## 11. 拟修改面与单一长期 owner

以下是固定版本下的定位入口；现场可复用已有 reference，而非必须创建表中候选文件。

| 落点 | 修改目的 |
| --- | --- |
| `docs/architecture/skill-composition.md` 及根 `AGENTS.md` 的必要语义 | 区分验收责任与执行劳动；保留 host/skills 边界、已有授权消费、独立 capability 组合。 |
| `src/skills/workflows/design-change/SKILL.md` 与按需 `references/goal-alignment.md` | 最小目标校准、提问归属与足以推进的停止条件；保留显式 stress-test。 |
| `src/skills/workflows/plan-change/SKILL.md` | 计划/dispatch 两层具体化、主动内聚委派、完整局部回路、交付终点、required/missing authority。 |
| 计划已有 references；必要时新增 `references/delivery-and-delegation.md` | 详细交付与 brief 方法按需披露，不成为每个小任务必读的巨大 reference。 |
| `src/skills/workflows/implement-change/SKILL.md`、`references/repair-loop.md` | 主动委派、child 局部闭环、可恢复派发错误、证据复用与 parent 裁决。纠正 verification/repair 全留 parent 的歧义。 |
| `src/skills/workflows/review-change/SKILL.md` 与相关 evaluator | Review 与验证执行的区别；按任务问题检查目标丢失、证据失配，不固定增加一轮 review。 |
| Oracle/testing owners | 验证与本次变化、状态价值和证据有效性对应；不附加无关恢复仪式。 |
| 既有 session preference/routing 引用 | 必要的薄触发与恢复语义；不改变 direct-match bypass，不引入 mandatory router。 |
| `contracts/skills.toml`、生成产物与必要触发案例 | 仅同步真实变化的描述、依赖和分发投影；保留现有 public IDs，不新增公共 skill。 |

同一方法只保留一个主要 owner，入口条件引用，不把全文复制到多个 SKILL。遵守单个安装单元的 reference closure，不依赖另一个仓库或未安装 sibling reference 的偶然存在。

根 `AGENTS.md` 应保留本仓库维护契约；不能为了减少 runtime 指令而删除必要生成检查。Workstation 的全局与真实项目配置只在必要范围内核对，并分别取得修改授权，不批量重写。

## 12. 验收场景

以下场景定义应满足的行为，不要求先建设自动全模型 benchmark。可通过当前结构检查、维护者场景审查及获授权的真实任务分别取得对应证据。

| 场景 | 期望 |
| --- | --- |
| 已明确的局部执行请求。 | 直接推进，不进入完整访谈/design/plan，不制造委派元数据作为普通实现 gate。 |
| 一个真实且会改变验收的歧义。 | 有证据地解决最小决定后继续，不穷尽所有可能问题。 |
| 普通局部技术选择。 | 执行者自行判断，不因换模型反复请求用户决定。 |
| 请求实现并交付，项目已有有效 commit/push/deploy 许可。 | 消费许可，持续到对应交付证据；不把每个动作变成重复审批。 |
| 只要求 design，即使存在常设部署权限。 | 只交付 design，不自动实施。 |
| 未商业化但存在不可重建数据。 | 保持数据保护，不把阶段标签当重置许可。 |
| 普通逻辑修改不影响恢复机制。 | 不添加无关完整恢复演练；必要行为检查仍执行。 |
| 两个独立内聚实现切片需要多轮测试反馈。 | 优先适配 worker 并行；每个 worker 自行完成局部闭环，不每次红灯回 main。 |
| 只有一个有价值的 worker slice。 | 在实际 host 与调用策略允许时使用 singleton；否则如实保留本地工作，不凑数或绕过限制，不宣称一定缩短 wall time。 |
| 实现前仍需调查局部调用方。 | Worker 可自行调查；不要求 explorer 必须先完成全部事实。 |
| 实際 host 没有任务所需执行能力。 | 明确适配、调整分工或本地执行；不假装能力存在，不无声扩权。 |
| 明确 write set 需要协调调整，但仍在用户已批准模块范围内。 | Parent 处理实际归属与权限重派；不重做整份设计，也不让 child 自行扩范围。 |
| 一次无启动参数错误或可恢复工具拒绝。 | 在原权限内修正后继续，不自动接管整段实现。 |
| Worker 最终候选有可靠局部测试证据。 | Parent 复用有效部分并安排必要组合验证，不无条件重做全部测试。 |
| Reviewer 建议放宽验收才能通过。 | 按批准基线裁决，不自动修改 plan/oracle。 |
| Parent 在长任务中发生 compaction。 | 从可信状态恢复委派与未决结果，不重复派发、丢失授权或强制重载全部 skills。 |
| 范围内修复多次仍有新的有效诊断。 | 继续，不因固定次数终止；真实预算和无可行路径仍有明确停止语义。 |
| 目标与必需证据全部满足。 | 结束，不为调用数、并发率或更多 review 继续工作。 |

自然语言改动不采用关键词集合、prose snapshot 或固定问答措辞来假装证明模型理解。真实结构、链接、嵌入命令、契约和分发一致性按既有工具验证；行为效果与机械检查分别报告。

## 13. 本地适配与实施计划输入

接手 agent 先读取当前 repo 指令、相关源码与已生效投影，标出本文语义中已实现、需修改和需要局部选择的部分。不要重新询问已经批准的 main/worker 分工、shell 方向和主动并行目标；只有当前事实使其无法按既定边界实现时，提出具体证据与最小决定。

详细计划应将共享 skills 源码、生成与检查、获准 workstation 配置适配分开。当前维护入口如下，现场以现行 `AGENTS.md` 为准；这些命令不是本次已经运行的记录。[^repo]

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

Skills 可以先完成语义修正，实际 dispatch 仍消费当时可用能力。Pi shell 尚未就绪不应阻塞目标校准、授权消费或 plan 改动；同样，skills 已更新也不证明 child 已加载新语义。

本仓库只定义评估应关注总费用、时间、验收及人工/parent 重复劳动，不实现 producer 或 evaluator。少量有授权的真实案例可辅助发现误触发、范围丢失和回落；正式消融、采样量与长期因果评价继续为开放问题，不成为日常开发门槛。

交付时分别报告：源码与分发检查结果、真实加载版本、场景观察及未验证部分。不要把没有观察到的委派机会、compaction 影响或经济收益补成零或通过。

## 14. 配套仓库接口与长期边界

Pi 负责提供真实可用的角色能力、局部 bash 执行、state guard、派发恢复、最终报告与导出状态、compaction 后能力连续性以及脱敏遥测。它不解析本设计来生成任务，不自动授予项目许可，也不替 parent 接受业务结果。

Skills 不要求固定 Pi 字段名、命令名、sandbox 后端、worker 数量或模型。新 role 未来可以扩展，但不在本轮新增角色清单或递归委派。某角色只读的是哪些状态，应与其实际能力一致，而非用“只读”一词禁止所有验证劳动。

最终应形成的使用方式是：用户只处理真正属于自己的目标和权限决定；main 调度和裁决；适合的 subagents 独立完成有边界的工作；已有验收和运行证据决定是否完成。更多并行是实现这一目标的手段，不能通过放松质量或隐藏成本来制造收益。

## 15. R1 增量：同一任务内的多轮通信与执行者复用

### 15.1 新增需求及优先级

用户补充：main 将实现打回时，原 worker 应能继续修改；reviewer 应能针对后续版本继续复审，而不是每一轮都新建会话、重新调查。首要考量是费用、任务连续性和避免重复劳动的经过时间。Explorer 的复用优先级较低，但不从共享方法上禁止复用。

此需求属于完整委派闭环的核心能力，与“单次 child 调用内可以反复测试和修复”不同。本文原第 9–10 节关于证据和长会话连续性的说明仍成立，但仅有这些说明不能证明跨调用复用已经满足。

以下是用户已表达的要求：同一任务内支持 parent-child 多轮交换；worker/reviewer 优先保留有效的既有上下文和工作状态；是否更经济、更快仍以真实证据评估。下面的具体接口、存储、默认存活策略与异常处理是供项目适配的候选设计，不是已实施记录或用户已逐项批准的 API。

### 15.2 默认按有生命周期的任务执行者分工

一个内聚任务可以包含多次 parent-child 交互。单次报告完成、工具调用返回、进程退出，都不自动意味着这个逻辑执行者必须关闭。

| 情境 | Skills 应指导的行为 |
| --- | --- |
| 原 worker 已交付候选，main 接受了范围内的缺陷或验证失败。 | 在原会话与工作状态仍有效时，续接原 worker，传入具体差异与证据，不重新下发一份从零实现任务。 |
| Worker 遇到只有 parent 能解决的局部信息或协调缺口。 | 返回具体问题并让出执行；parent 解决后续接原任务。不要将正常交回问题等同永久失败或人类审批。 |
| Reviewer 需要确认其既有 findings 是否被修复。 | 续接原 reviewer，提供明确的新候选与变化，要求定向复审及受影响边界检查。 |
| 新任务与原任务无关，原会话无法安全恢复，或确需独立新视角。 | 明确新建的原因，创建新会话；有用且可信的材料可以有界移交，但不能把摘要重建冒充完整续接。 |
| Explorer 只需回答一次廉价、有界事实问题。 | 保持一次性调用即可；调查本身昂贵或需要连续追问时允许复用。 |

“优先复用”不是“不允许换执行者”。已有上下文失效、任务或权限明显变化、模型/环境不可用、持续误解且无有效进展，都可能使新会话或重新切分更合理。不要为了提高复用率把不相关任务堆入一个永久大上下文。

### 15.3 Continuation brief 传增量，而非重写过去

初次委派仍应传递足够的目标、约束、来源和验收。续接时通常只补：对应的既有任务/结果引用、当前候选或基线、main 已裁决的具体 findings、错误与日志证据、允许的范围内修复，以及这次需要返回什么。

原有 plan、non-goals 与批准边界继续有效。明确说出发生变化的事实，不能通过把整个初始 prompt 改写一遍悄悄改变任务。当前 host 没有保留完整历史时，应如实标示上下文重建，并补足必要信息。

示例语义：

> 继续同一个任务。对你上一轮候选 C1，范围内测试 E1 暴露了问题 F1；此前已裁决的 F2 不重开。修复 F1 并检查受影响边界，保留原接口和验收。当前工作基线及其他已整合变更由 host 给出的有效快照为准；不要依据历史文件内容覆盖更新。返回新候选和本轮证据。

示例不是强制模板，不要求每个简单 follow-up 填满字段。具体 handle、candidate 和证据表示属于 host。

### 15.4 Reviewer 连续性不等于放弃独立判断

Reviewer 与 worker 的角色和会话分离。同一个 reviewer 对同一 change 持续复审，不等于让 worker 审自己；也不必为了“独立”每轮清空 reviewer 的历史。

复审必须确认当前内容与上一轮不同之处，判断已有 findings 的处理以及修复是否引入相关回归。历史结论只能在证据仍有效时复用。不能只接受 worker 的“已修好”声明，也不能因为 main 希望完成就承诺通过。

有实质理由需要不同视角时，main 可以发起 fresh review，例如重要边界改变、前一 reviewer 覆盖或判断有问题，或用户明确要求独立复核。它不是每轮固定追加的流程。不得在同一会话中把 worker 改名为 reviewer 来制造独立性。

### 15.5 会话复用不覆盖状态与权限边界

“同一个执行者”至少需要可靠的上下文延续，以及适用的 workspace/目标版本和权限状态。旧 transcript 中存在某个文件路径或批准描述，不证明当前仍可访问、仍获授权或仍是最新版本。

Parent 通过 host 的真实结果确认：会话是否可续接、上轮候选是否已经导出、当前基线是否漂移、还有什么未裁决结果。需要先协调源码归属或同步其他已整合变更时，完成该协调再续接；不要求用户重做已批准设计。

会话不能被无条件复用于不同项目或不同角色。模型/提供商调整也不能静默发生；遵守实际路由授权，并如实区分继续、迁移、分支或重建，不保证跨模型仍享有相同缓存。

### 15.6 交流方式与 parent 编排责任

必要能力是 parent 与指定 child 的多轮交换：parent 可以提供补充信息、修复要求或定向复审；child 可以返回候选、证据、问题和阻塞。第一条可用路径可以仍然是 foreground 的轮次间通信，不要求先建设全网状 agent 消息总线或后台 mission 引擎。

“每一轮必须回到 parent 裁决”与“每一轮必须新开 child”完全不同。前者保留判断权，后者会丢失有效工作连续性。Skills 不规定必须保留相同 PID 或终端窗口；同一有效 native session 与受管工作空间在新进程中恢复，也可以满足连续性。

若 host 只有报告返回后才能让 main 发新消息，就不能声称 main 能在 child 仍运行、父工具仍阻塞时自由插话。运行中 steering 的机制由 host 明确提供，不能用轮询或隐藏重启模拟。

### 15.7 计划和 compaction 恢复需要保留什么

计划只表达长期稳定的任务边界与预期交互；首次创建前无需填写尚不存在的 child handle。实际执行中由 host 的结果和必要进度记录保留任务与可续接 handle、最新候选、待回应问题/待裁决报告之间的对应。

Parent 在 compaction 或恢复后应先确认已有执行者和结果，再决定续接或创建。不要仅因为摘要没有出现某个 handle 就新建替代者；也不要根据陈旧 running 状态自动恢复执行。

恢复后的权限与能力由当前 host 核实。Skills 不能要求读取任意历史诊断 JSONL 并自行执行 `pi --session`，以绕过 host 的 workspace 与 capability 校验。

### 15.8 成本与时间判断

主要收益假设是减少重复调查、环境准备、实现重建和 review 重建；prefix cache 可能带来额外收益，但不是复用的定义，也不保证每次续接更便宜。OpenAI 的缓存文档明确要求有效的匹配前缀，缓存还有存续条件；同一会话与缓存命中不是一个事实。此说明不推导其他 provider 的定价或订阅扣额。[^r1-cache]

本仓库只要求评估语义：比较完整任务的接受结果、所有轮次总费用、经过时间和重复劳动。Host 记录 create/continue/reconstruct 等实际事实、增量 usage 与候选关联；不要将两轮复用统计成两个新 worker，也不要将恢复后的全部历史 usage 重复累加。复用率本身不是目标。

### 15.9 增量修改面与验收

`plan-change` 的委派说明、`implement-change` 及 repair reference、`review-change` 与已有 session 恢复方法，应统一“同任务优先续接，主 agent 保留裁决”的语义。无需新增公共 continuation skill，也不要求每次 follow-up 重新生成完整 plan 或再 review brief。

| 场景 | 验收语义 |
| --- | --- |
| Worker 返回后 main 打回一个范围内问题。 | 优先续接原执行者；它能消费旧上下文和新增证据，独立完成下一轮局部反馈。 |
| Reviewer 复审修复版本。 | 保留既有 findings 背景，检查真实新候选及受影响边界，不从零重复全面审计。 |
| 一次正常的澄清往返。 | Child 返回问题、main 提供答案后原任务继续；不默认上升到人类或新建会话。 |
| Parent 压缩后继续任务。 | 恢复正确 handle 和待裁决状态，不重复创建、执行或导出。 |
| 状态漂移或会话不可恢复。 | 定位实际缺口，安全同步/重建/重新分工；不把新会话伪装成原会话。 |
| 新的独立审查确有必要。 | 可以 fresh review，但说明实际目的；不为复用率牺牲覆盖。 |
| Host 暂未支持续接。 | 如实说明当前能力与影响；本地已有能力可以继续使用，但不能将新增需求判定为已完成。 |

本轮新增需求来源是用户关于“worker 被 main 打回后继续、reviewer 复用、避免重复费用和时间”的明确表达。它补足而不推翻前文完整 worker、状态 guard、可恢复派发和整体评估方向。

## 16. 本地适配结论与本轮范围

### 16.1 当前源码证据与增量

| 当前事实 / 定位 | 本轮处理 |
| --- | --- |
| `design-change/SKILL.md` 已支持 bounded clarification 与 direct implementation bypass；`references/stress-test-mode.md` 仅显式触发，并有稳定 Q IDs。 | 新增按需 goal-alignment reference，补足目标/手段、提问归属及足以推进的停止条件；不把普通澄清扩成 stress-test，也不把其 Q IDs 扩成永久需求账本。 |
| `plan-change/SKILL.md` 已分离本地 readiness 与 delegation-ready，profiles 为 provider-neutral。 | 补两次具体化、内聚工作包与交付终点；保留已声明 delegation-ready 的准确性，不把 host handle 写入永久计划。 |
| `plan-change` 与 `implement-change` 的 hard-predecessor 条款混列 parent-owned verification / repair；后者还有 “Delegation does not transfer … verification … repair … continuation”。 | 区分局部执行劳动与 parent 决策权；测试、诊断、获准修复可以委派，跨任务综合、权限、finding 裁决、最终接受与续接决定仍在 parent。不能投影成静态 reviewer→repair 链。 |
| `implement-change/references/repair-loop.md` 已按证据继续，无默认次数上限。 | 在既有规则中加入 worker 局部循环与同任务续接，不另造循环或预算模型。 |
| `review-change` 已限定 read-only evaluator、定向复审及证据仍有效才复用裁决；三个 evaluator 均禁止自行修复和递归委派。 | 补 reviewer 连续性与当前候选核对；只按各 evaluator 的目标补缺口，不复制一套执行协议或放宽角色权限。 |
| `close-change` 已区分未获授权与未完成操作，但未细化已有许可消费、完整待推送历史和版本绑定交付证据。 | 明确任务/权限/能力三者独立、实际交付终点与副作用范围；不修改真实项目许可。 |
| oracle/testing 已有状态模型、oracle integrity 与 docs 验证规则。 | 只补状态升级及 backup/restore 的变化敏感边界，复用既有验证策略；不要求每次逻辑修改都做恢复演练。 |
| session 已有渐进披露、memory truth order 与 PB1–PB5 phase-boundary 方法。 | 保留既有分支顺序，增加同任务结果/执行者恢复的薄语义；不把 phase handoff 变成所有 follow-up 的门槛。 |
| `tests/test_session_interaction_contracts.py` 尚以句子、标题、关键词及文本顺序保护 stress-test 和 phase-boundary 含义。 | 这些断言与现行 testing-strategy 冲突，且覆盖本轮拟改面。仅清理这一相关文件的 prose snapshots；稳定 routing ID/owner 与路径存在、reference closure 由结构检查保护，不另写同义关键词测试。 |

### 16.2 Host 与本仓库验收分离

当前相邻 `pi-extensions` HEAD 为 `ba3207b5e7938a2f052961a2031310efd72588cf`。其 `extensions/subagents/roles.ts` 中 worker 工具为 read/grep/find/ls/edit/write，explorer/reviewer 为 read/grep/find/ls，没有 bash；这只是该源码基线证据，不证明所有 host 都如此。当前 `csheng_subagents` 接口只提供 bounded foreground batch，没有针对既有 child handle 的 continue 参数。本次没有验证后台 steering、跨调用 worker 工作区延续或 reviewer 私有命令能力。

因此，本仓库可以完成完整 worker 和同任务优先复用的**可移植语义**，不能声称当前 Pi 已提供 shell、续接或节省费用。当前 host 的 parent-owned verification/repair 等调用限制仍生效；源码意图不覆盖实际工具策略。若后续 host 提供可核查能力，再安排获授权的真实行为验证；外部能力缺口不阻塞本仓库文档语义修改，也不被计作 R1 跨仓库能力已完成。

### 16.3 单一方法 owner 与渐进披露

- 目标校准细节归 `design-change/references/goal-alignment.md`；根入口条件引用，stress-test 仅调整事实调查责任的歧义。
- 交付规划与两次具体化归 `plan-change` 及按需 `references/delivery-and-delegation.md`。
- 调用恢复、brief、局部证据与 worker 续接细节归 `implement-change/references/delegated-execution.md`；既有 repair reference 只保留收敛/修复规则并引用，不复制协议。
- Reviewer 连续性归 `review-change`；session 只保留恢复判断所需薄摘要，不成为委派工具或强制 router。每个安装单元内部 reference 必须闭合；跨 Skill 仅按独立能力组合，不链接未安装 sibling 文件。
- `close-change` 负责交付完成判断，oracle/testing 负责状态相关证据；stable architecture 在实现验证后同步。

根 `AGENTS.md` 仅在实施中消除“拥有修复”可能禁止 worker 执行修复的歧义，保留维护入口与权限约束。39 public IDs、`contracts/skills.toml` 的角色/权限及 `delegation-profiles.toml` 的语义词汇不需变化；不新增 runtime 字段或 semantic dependency。只有发现不可通过当前约定实现的事实时，才提出最小设计/范围决定。

### 16.4 本轮非目标、取舍及可重开条件

不修改 sibling host、全局 instructions、真实项目 AGENTS、安装链接、插件 manifest、模型路由或配置；不实现任务/会话存储、自动调度、benchmark 平台，也不新增公共 Skill。明确当前 checkout 是默认工作场所，任务文档和不冲突的修改不触发隔离或预先提交。

选择共享语义先行而不等待 host，是因为 goals/authority/plan/acceptance 的改进不依赖 child shell；代价是只能给出语义与分发证据，不能把完整运行需求宣布完成。放弃统一巨型 reference 和主 agent 全部预研，因为前者增加无关上下文，后者抵消内聚委派；放弃永久精确 actor/handle 计划和全局配置覆盖，因为它们跨越 host/state owner。

本轮 oracle 为结构/分发检查与有界场景审查，不是措辞单测。未来实施须逐项核对第 12 节和第 15.9 节，区分源码支持、实际观察与未验证。修复保留既定目标、权限和验收，默认 fix-forward；host 新增真实续接能力、当前角色契约发生冲突或有授权的任务证据暴露实质误导时，重开对应局部决定，不重跑全部设计。

---

## 来源与证据边界

公开来源访问日期：2026-09-07。固定提交用于复核输入，不声明 workstation 当前状态。正文的“应”“建议”“本轮”表达设计语义，不声称已经实施。

[^user]: 本对话用户逐项确认：目标校准、已有授权消费、main orchestrator、worker 完整局部开发与 bash、状态而非工具语法 guard、可恢复拒绝、compaction 三类连续性、整体费用与 wall time 评估；最终明确“1–5 都接受”并要求按仓库拆分设计。“GPT模型价格对比表”相关检索支持成本与遥测关注方向，不包含一份可视为已实施的完整指标规范。
[^prior]: 当前对话的前序文件：`design.md`（SHA-256 `f92f05b445409dfdbad28e68f43fa989e593c2a3069ce7eed6003c4d6d38c4b7`）、`design-v2.md`（`51114f89a3353d67a1731b809cbc75e0f52438d9aec055b5b4fa4ac8683e85bf`）、`design-v3.md`（`d2352a7c9b0386250f9d1fa48d6d10a788fea2871c2999af2e7dea42e4a0a9f4`）。本文已吸收本仓库所需内容，无需把历史文档全部加入日常上下文。
[^composition]: Skill composition 与 ownership。<https://raw.githubusercontent.com/CsHeng/agent-skills/55fc1a56454679b3f83ea3d2f812fb256bf4f62f/docs/architecture/skill-composition.md>
[^plan]: 计划入口、条件委派、profiles 与批准边界。<https://raw.githubusercontent.com/CsHeng/agent-skills/55fc1a56454679b3f83ea3d2f812fb256bf4f62f/src/skills/workflows/plan-change/SKILL.md>
[^implement]: 实现、验证、checkout、repair、验收完整性。<https://raw.githubusercontent.com/CsHeng/agent-skills/55fc1a56454679b3f83ea3d2f812fb256bf4f62f/src/skills/workflows/implement-change/SKILL.md>
[^design]: 设计入口、clarification 与显式 stress-test 引用。<https://raw.githubusercontent.com/CsHeng/agent-skills/55fc1a56454679b3f83ea3d2f812fb256bf4f62f/src/skills/workflows/design-change/SKILL.md>
[^review]: Bounded brief、只读 evaluator 与候选 findings。<https://raw.githubusercontent.com/CsHeng/agent-skills/55fc1a56454679b3f83ea3d2f812fb256bf4f62f/src/skills/workflows/review-change/SKILL.md>
[^repo]: 源码/生成物、public IDs 与维护检查。<https://raw.githubusercontent.com/CsHeng/agent-skills/55fc1a56454679b3f83ea3d2f812fb256bf4f62f/AGENTS.md>
[^r1-cache]: OpenAI Prompt caching：<https://developers.openai.com/api/docs/guides/prompt-caching>，访问日期 2026-09-07。仅用来区分会话连续性与前缀缓存，未据此推导具体模型价格或订阅扣额。
