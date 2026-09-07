# R1：目标对齐、编排式交付与同任务续接实施计划

日期：2026-09-07。基线：`55fc1a56454679b3f83ea3d2f812fb256bf4f62f`。

设计唯一入口：[本地适配后的 R1 设计](2026-09-07-orchestrated-delivery-r1-design.md)，尤其是第 12、15、16 节。根目录输入已迁移，不再作为后续执行入口。

状态：已获用户明确批准（`approve and $implement-change`），T0–T8 已完成，本仓库语义与分发里程碑 `pass`。批准覆盖本设计适配范围及 T0–T8；不包含 commit/push、配置/安装或外部 host 开发。以下任务和验收保持原批准基线，执行进度另记。

## A. 里程碑与保护边界

本里程碑交付共享 skills 的语义增量、相应稳定真相与 generated parity：main 保留目标、调度、权限、裁决和最终验收，适配的 worker 完成有界调查/实现/验证/修复；同任务优先续接，但不捏造 host 能力。

必须保持：39 public IDs；现行角色、权限与语义依赖；provider-neutral profiles；reviewer 只读及不得递归委派；直接 bounded implementation 无强制 design/plan/oracle reselection；无默认 repair/review 次数上限；current-checkout 默认；不弱化验收或把工具成功等同业务接受。

本里程碑不实现 Pi shell、session transport、存储、scheduler、state guard 或模型配置；不修改全局/真实项目指令、安装链接、插件 metadata，不建设 benchmark、运行付费行为实验或执行外部部署。不顺带清理其他测试与历史文档，不修改 `contracts/skills.toml`、`delegation-profiles.toml` 或 routing 词汇。

源码保持现有英文约定；本阶段设计/计划/验证记录使用中文。没有新持久化工具或语言选择；T6 只修改现有 Python 测试，届时遵守仓库测试约定与 `python-guidelines`。

## B. 现状判断与适配理由

- 已实现且复用：触发/readiness 分层、证据驱动收敛、渐进披露、现有 review dispositions、独立 capability 与 current-checkout。不会重做上一轮。
- 真实歧义：plan/implement 把 parent-owned verification/repair 与最终判断混列；现有条款可能让调用方把全部执行反馈留在 parent。
- 真实缺口：最小目标校准方法、计划与 dispatch 两次具体化、完整内聚工作包、已有交付许可消费、最终候选关联证据，以及跨调用 worker/reviewer 连续性。
- 相关测试债务：`tests/test_session_interaction_contracts.py` 仍冻结自然语言与标题顺序，覆盖本轮 session/stress-test 改动且违反当前 docs-testing 规则。仅在 T6 清理这一有直接关联的边界，不扩成全仓测试改造。
- 外部能力限制：设计 §16.2 记录的 host 源码无 worker bash，当前 foreground batch 接口无 child continuation 参数。这不是新增 skills 公共 API 的理由，也不阻塞共享语义修改；完整运行效果仍未验证。

## C. 授权与前置条件

| 项目 | required authority / 前提 | 当前状态与处理 |
| --- | --- | --- |
| 适配设计、迁移、制定计划、只读评审和文档检查 | 本次用户请求 | 已覆盖，本次可完成。 |
| T0–T8 源码、相关测试、稳定文档、生成物修改 | 用户批准本计划及实施范围 | 已由本轮明确批准覆盖，按原范围实施。 |
| 当前 checkout 中保留本任务阶段文件及其他不冲突修改 | 仓库维护政策；实施前重核 diff | 默认允许，不要求预先 commit、worktree 或 clone。 |
| 未来有界 child 调用 | 当前 host 能力、调用政策和任务权限 | 执行前核对。计划不授予 spawn、shell、验证或持久 session 权限。 |
| 真实项目 commit/push/deploy、全局配置、安装、模型付费实验 | 单独任务范围与相应已有或新增许可 | 本里程碑排除；凭据存在不算授权。 |
| Skills 跨调用续接语义落地 | 文档与场景审查 | 不依赖 sibling 仓库先实施；不得宣称 host 能力已交付。 |
| 真实续接/成本效果证明 | 可验证的 host 能力、隔离条件、明确预算与运行授权 | 未具备本次证据与权限，作为后续独立工作，不伪装成计划内已通过。 |

本计划不存在已知账号、硬件或凭据前置阻塞。C 表中实施批准已取得，不要求逐个动作重复审批；已有批准覆盖相同任务与副作用时，消费批准即可。只有实际缺口才使用 `manual_checkpoint`，不把所有 required authority 当作 missing authority。

## D. 稳定任务与准确写范围

所有写路径均相对本仓库。T1–T6 是可独立实现的内聚成果，不是强制子代理调用列表；禁止修改表外路径来凑通过。T7/T8 的汇合决策归 parent。各任务可以在本范围内调查、组织段落、调整必要 frontmatter 描述及自检，不必预先固定每条文字或每次命令。

### T0 — 核实获准范围与执行状态

- 前置：用户实施批准；重新读取本设计/计划、当前 AGENTS、HEAD 与 `git status --short`，核对批准之后的漂移。
- 写入：无。
- 行动：确认下面准确 write sets 仍覆盖实际改动；核对当前 host 的读写/执行/返回/续接能力，而非按历史工具名推断。默认当前 checkout，冲突调查限定实际文件与共享资源。
- 完成：保护原有修改，确定能本地/委派执行的任务及真实限制；没有未知冲突就继续，不做 workstation 全局并发扫描。设计前提失效才回到局部设计决定。

### T1 — 补最小目标校准方法

- 依赖：T0 的当前状态与授权确认；不依赖其他源码任务。
- 准确写入：
  - `src/skills/workflows/design-change/SKILL.md`
  - `src/skills/workflows/design-change/references/goal-alignment.md`（新增）
  - `src/skills/workflows/design-change/references/stress-test-mode.md`
- 内容：目标/手段/硬约束区分；先查可发现事实，仅把真正改变决定的问题交给对应 owner；推荐与后果；足以推进即停止。根文件按需引用；stress-test 保留显式触发、frontier 和 Q IDs，仅澄清事实调查责任不等于 main 必须亲做全部劳动，也不新增委派授权。
- 完成与证据：用 V1–V3 检查已明确任务可直接推进、局部选择不反复问用户、一个歧义只解决该决定；普通澄清不启用 stress-test，也不生成永久问题账本。

### T2 — 形成两阶段具体化与交付规划

- 依赖：T0；设计已冻结的 scope/owner/acceptance，无 T1/T3 文本产物依赖。
- 准确写入：
  - `src/skills/workflows/plan-change/SKILL.md`
  - `src/skills/workflows/plan-change/references/delivery-and-delegation.md`（新增）
- 内容：规划先固定行为与归属，dispatch 再细化 host 所需准确文件/输入；不虚构已就绪状态，不擅自扩大用户已批准的精确范围。按内聚结果含调查、实现、直接测试和局部修复切分；主动识别有价值并行，不把 explorer 当固定前置或把所有验证当 parent 中介。计划表达预期同任务交互，不预填尚不存在的 handle。
- 完成与证据：保留 delegation-ready 条件与语义 profiles；解释普通本地 readiness 不依赖其完整性。区分交付终点、required/missing authority 和能力；真实 parent 决策仍切断静态依赖链。V1–V3 覆盖模块范围可细化、精确 write set 不可自行扩张、只写设计不部署等正反例。

### T3 — 补内聚执行、续接与审查边界

- 依赖：T0；消费设计既定 owner，不等待 T2 的措辞定稿。
- 准确写入：
  - `src/skills/workflows/implement-change/SKILL.md`
  - `src/skills/workflows/implement-change/references/repair-loop.md`
  - `src/skills/workflows/implement-change/references/delegated-execution.md`（新增）
  - `src/skills/workflows/review-change/SKILL.md`
  - `src/skills/review-components/review-design/SKILL.md`
  - `src/skills/review-components/review-plan/SKILL.md`
  - `src/skills/review-components/review-implementation/SKILL.md`
- 内容：详细 delegated-execution reference 统一初次/增量 brief、host 能力消费、局部回路、错误类别、候选/检查证据、续接/重建区别及安全 takeover。根入口仅保留必要规则；repair reference 不复制整套委派方法。父目标、范围、接口、验收、重要理由和可访问内容必须传到 child；路径字符串不等于已传递文件。
- 内容：把 parent 最终判断与可委派劳动分开；worker 对授权缺陷自行诊断/修复，reviewer 只返回候选。复审优先有效原 reviewer、角色/会话不得伪装独立；新候选、新回归和仍有效裁决都要核对。Evaluator 仅按其 bounded target 补适用的目标、计划精度或候选证据检查；不让 reviewer 运行权限超出 host 的命令，不要求新 review 仪式。
- 完成与证据：V1–V3 覆盖参数/admission 失败与已启动 child 的安全/环境/语义失败区别、无权限膨胀的恢复、当前 host 不支持时如实报告、无静态 reviewer→repair 链；证据对应最终候选，组合验证与 final acceptance 留 parent。无默认次数上限，不把结果完整或 export 成功写成验收。

### T4 — 保留长会话与任务连续性的薄语义

- 依赖：T0；设计已明确恢复契约，不需等待 T3 实现。
- 准确写入：
  - `src/skills/session/use-coding-skills/SKILL.md`
  - `src/skills/session/use-coding-skills/references/phase-boundary-decision-tree.md`
  - `src/skills/session/use-coding-skills/references/memory-boundary.md`
- 内容：区分 capability、guidance、任务状态；恢复目标/批准/实际变更/未裁决报告/可续接执行者后再决定下一步。保持 phase-boundary 的既有分支顺序和 direct-match bypass，同任务 follow-up 不被迫进入阶段转换。旧摘要不是当前 running 状态；不因 handle 缺失重复创建，也不读取任意历史 JSONL 自行绕过 host 恢复校验。
- 完成与证据：V1–V3 覆盖 compaction、已有结果、漂移、不可续接和新建的真实理由；不复制 T3 的详细 continuation brief，不新增 mission ledger、强制 router 或全量 skills reload。

### T5 — 校准交付终点与状态敏感证据

- 依赖：T0；与 T2 共享设计约定而非源码依赖。
- 准确写入：
  - `src/skills/workflows/close-change/SKILL.md`
  - `src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md`
  - `src/skills/disciplines/testing-strategy/SKILL.md`
  - `src/skills/disciplines/testing-strategy/references/agent-skill-evaluation.md`
- 内容：任务/授权/能力独立；消费已覆盖许可而不把常设权限扩成任务。交付以指定版本和终点的真实证据判断；完整待推送历史与 CI/CD 副作用计入操作范围。已有可靠 evidence 可复用，未覆盖组合和状态转换仍须验证。
- 内容：普通逻辑变化不自动触发全量 backup/restore，migration 验证真实现存状态升级而非仅空库初始化，backup/restore 改动验证恢复行为；不可重建数据不因项目阶段而降级保护。评估 reference 仅增量说明完整任务/全部轮次、真实继续/重建与 usage 去重，不绑定 provider 或实现指标系统。
- 完成与证据：V1–V3 覆盖有/无既有许可、只规划、push 携带其他历史、自动部署副作用、状态保护与局部绿灯失效；不用新增风险评分、固定演练清单或实验前置门槛。

### T6 — 清理本轮相关的 prose snapshot 测试

- 依赖：T0；依据已确认的测试分类决策独立修改，不等待 prose 定稿。
- 准确写入：`tests/test_session_interaction_contracts.py`。
- 内容：逐断言分类，删除只冻结句子、关键词、标题文字/顺序和含义的断言；不能把大 snapshot 缩成小关键词集合。保留稳定 routing case ID/owner 与实际路径/reference 存在检查；reference closure 与分发一致性复用现有 checker，不重复造自然语言 oracle。
- 完成与证据：列出删除/保留类别与现有结构覆盖 owner；运行该文件及 V1/V4。测试数量减少不是弱化业务验收，语义检查由 V3/V5 明确承接。若发现需改新结构契约或其他测试才能通过，先由 parent 判定是否超出本计划，不扩成全仓清理。

### T7 — 汇合裁决并同步稳定真相

- 依赖：T1–T6 的候选与局部证据；各独立结果必须由 parent 核对后才能写当前稳定真相，不能直接用 host 硬前驱绕过该决策。
- 准确写入：
  - `AGENTS.md`
  - `docs/architecture/skill-composition.md`
  - `docs/architecture/invocation-contract.md`
- 内容：确认实际源文件与候选证据，裁决矛盾、重叠及必要 repair；把已成立的验收 owner/执行劳动、能力限制与权限消费写成稳定事实，不写成 host 已实现能力。`AGENTS.md` 只澄清修复责任，保留 39 IDs、生成检查与 repo-maintenance 边界；`CLAUDE.md` 已是相对 symlink，不改链接。
- 完成与证据：V2/V3 检查职责和条件披露一致，无循环/重复流程或跨安装单元 reference；T7 不能让历史输入反向成为稳定真相。若需修复 T1–T6，仍在其准确写范围内，parent 决定执行方式并重验受影响证据。

### T8 — 生成、最终验证、条件修复与交付证据

- 依赖：T7 的汇合裁决与稳定真相；不能提前混合多个 worker 的生成物。
- 准确写入：仅由既有生成器拥有的 `skills/`、`skills.index.json`、`docs/architecture/diagrams/`、`docs/architecture/generated/`；以及本计划的进度/证据、`docs/plans/changes/2026-09-07-orchestrated-delivery-r1-verification.md`（未来新增）。生成范围不是手写或新增任意文件的授权。
- 行动：由一个 parent-controlled 操作序列运行仓库四项维护命令，核对生成 diff 仅投影 T1–T7；parent 独立验收。进行 V5 独立实现评审，裁决 findings；接受的修复归所属源任务，修改后重新生成并运行受影响与声明检查，不直接改 generated output。
- 完成：源码/契约/分发检查通过，设计验收场景已逐项分类，无未决 accepted finding；报告准确候选身份及证据缺口。`git diff --check` 与最终状态确认无越界变更。保留未执行真实 shell/续接/成本实验的限制；不自动 commit/push/install。

## E. 并行与委派安排

**E1：T1–T6 是事实独立组。** 各自 owner 和写集合不重叠，消费同一冻结设计即可启动；文档章节顺序不构成依赖。可按实际价值与 host 能力选取同一个 flat batch，或保留本地执行；不要求凑满六个 worker，不拆出专门跑一次命令的形式化任务。

**E2：T7/T8 保留 parent 汇合与最终判断。** 共享 generator、generated 目录、Git index/refs 及最终检查环境不交给并行 source workers。当前 host 策略限制 parent-owned verification/repair 的委派，执行时遵守；不能以未来共享技能的设计意图覆盖当前限制。其他兼容 host 即使允许执行劳动委派，最终证据接受仍属 parent。

本计划固定准确源码写集合，但**不声明 T1–T6 已对任意 host delegation-ready**：实际读范围、snapshot 内未提交文档可见性、命令能力、隔离方式与续接支持还需 T0/dispatch 核实。因此不虚构 worker handle 或给每项任务固化 profiles。若执行时声称 delegation-ready，按现行 `delegation-profiles.toml` 补齐 execution/reasoning profile、repository_owner、exact write_set、resource_locks、isolation、convergence_owner、verification、done_when、failure_policy；保持语义 provider-neutral。

共同约束：repository owner 为本仓库，convergence owner 为 active parent；worker 仅能写其 T 任务准确集合，不能写共享生成物、Git index/refs 或 sibling 仓库。默认 current checkout；host 需要私有隔离时消费其真实机制，不由 plan 指定宿主路径或静态工作流。运行命令造成的 cache/临时文件也要符合 host/state 边界。子任务交付候选和可核查证据，不拥有父任务通过或继续决定；无 shell 时不能把静态自检说成已运行测试。

后续如 host 支持原任务续接，由 parent 核实当前授权、工作状态、基线漂移与未裁决结果，再传增量 brief；不支持则准确标为本地处理或有界重建。当前会话不得改用外部 harness、隐藏 model fallback、raw session 恢复或工具重试来绕过限制。

## F. 验证策略与证据界限

### V1 — 结构与发布投影

既有检查负责 TOML/metadata、39 IDs、角色/权限、references、index 与 generated parity；不用新增自然语言关键词测试。每个源任务自查可访问引用和相关 contract，T8 统一执行：

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

### V2 — 文档与写范围

运行仓库 Markdown/prose 检查与 `git diff --check`，检查新增 references 在单个安装单元内闭合，根入口按条件披露；检查最终 diff、未跟踪文件与 symlink 状态。生成物只来自当前 authored source；stage 文档通过 `docs/.ignore` 排除默认搜索但保留 Git 可见性。T6 的 focused check 为 `uv run pytest tests/test_session_interaction_contracts.py`，使用与 `scripts/check.sh` 相同的仓库 cache/environment 约定，避免把运行环境写进源码树。

### V3 — 维护者场景审查

Parent 将设计第 12 节全部场景及第 15.9 节七项续接场景逐项映射到实际修改位置、预期反例与证据等级；保留场景原意，不把尚无 host 的运行要求删成“只要写了说明”。重点包含：

- 清晰任务直接实现；一个实质歧义最小澄清；局部事实/技术选择不交回用户；不触发默认 stress-test。
- 已有许可与任务范围匹配才推进；只 design 不部署；完整 push 历史和 CI/CD 副作用；不可重建数据保护；现存状态 migration 与恢复行为的区别。
- 独立 worker 内聚循环、真实依赖与 shared resources；普通 readiness/条件委派/精确 dispatch；一次 admission 失败不自动 takeover；无能力时如实适配。
- 有效局部测试复用；最终候选漂移使部分证据失效；组合验证与 parent 裁决；不能通过改 plan/oracle 制造通过。
- 原 worker 被打回、原 reviewer 定向复审、正常澄清往返、compaction、漂移/重建、必要 fresh review、host 尚不支持续接；禁止角色改名制造独立性或从陈旧 transcript 覆盖当前代码。
- 有新诊断则在原范围继续；实际预算/权限/能力阻塞准确报告；完成后不为调用量和复用率继续工作。

这些是有界语义审查，不证明 agent 实际遵守；不编写无真实 consumer 的 faux harness 来假装端到端验证。

### V4 — 测试完整性

T6 修改前记录断言分类，保留结构/routing 保护或指明现有 checker 的等价覆盖；修改后 focused test 与总套件均须通过。删除 prose snapshots 要接受 V5 的 elevated-risk oracle 审查，不把测试变少作为质量下降或收益证明，也不以失败为由降低 acceptance。

### V5 — 条件独立评审与裁决

本计划因跨 planning/implementation/review/session 的 ownership 与权限语义存在误导风险，选择有界独立 plan review；实现阶段同样要求对最终准确 diff 作一次有依据的独立 implementation review。Reviewer 只读，不能递归调查全仓、修复、改目标或替 parent 决定继续。当前 review 不审尚不存在的实现；未来 review 重点审权限消费、局部修复/最终裁决、续接证据、测试分类与防流程膨胀。

一次评审不是整个 change 的次数配额。Parent 独立裁决 accepted/rejected/deferred，接受项由所属 owner 在原范围修复；只有证据失效、未决独立问题或适用规则才定向复审。不能为了补齐日志重复全面 review；没有新证据不重开已裁决事项。

## G. 风险与恢复

| 风险 | 检测与最小处置 |
| --- | --- |
| 把 parent 负责理解成必须亲手执行，或反过来丢掉 parent 裁决 | T3/T7/V3 对照角色与决策边界；在原文件 fix-forward，不放宽 reviewer 权限。 |
| 过度委派、过细计划或重复 references | T1–T5 self-check 与 T7 汇合裁决；优先删重复方法而非新增统一 controller。 |
| 源码/生成物 drift、未提交 context 未进入 child snapshot | T0 与 dispatch 核实当前内容；暂停受影响写入，补可读摘录或协调归属，不 reset/stash 用户工作。 |
| 测试清理意外丢掉结构保护 | T6 分类与 V4/V5；恢复必要结构检查或使用已有 checker，不能回填 prose snapshots。 |
| 局部或总检查失败 | 保留命令与候选证据，所属 T 任务诊断 fix-forward，parent 裁决并重验；不得标记完成或固定两轮后放弃。 |
| 工具拒绝、不可续接、环境缺失 | 区分 admission/执行/导出/语义状态，原权限内可修复才继续；无可行路径准确 blocked，不隐藏扩大权限或假冒续接。 |
| 需要表外源码、契约、host 或安装变化 | 保留证据，暂停受影响任务并提出最小范围/授权决定；独立已授权任务可继续。 |

本计划不授权 destructive rollback。默认 fix-forward；缺有效诊断路径、用户取消或实际预算耗尽时报告真实不完整状态。若未来确需 guarded rollback，必须先明确并获准触发条件、准确目标和恢复验证，不能自动还原整个 checkout。

## H. 规划阶段证据（实施前历史）

- 设计输入已完整读取并迁移，保留 R1 新增需求，补充本地源码与 host 能力边界；未改 stable truth 或 Skills 源码。
- 独立评审：同一 flat batch 分别评审适配设计和本计划，两个只读 evaluator 均返回 `pass`、无候选 findings、无文件修改；run `a7f945a5-6211-43c0-9415-fa9f9b425574`。评审范围为各自文档及列明的权限/架构/规划支持材料，未评审尚不存在的实现或验证 host 运行能力。
- Parent 裁决：接受两项有界评估的结论，独立核对写范围、角色权限、依赖、证据等级与批准边界；无待修复 candidate。后续仅追加批准状态与已执行证据，未改变被评审任务和验收，不需要重新全面评审。
- 本次验证：Markdown normalizer `count`/`preview` 均为 0 hard-wrap，故未运行写回；`bash scripts/check.sh` 通过 contracts、root-flat parity、install surface、index、diagrams、ruff、ty、98 项测试及 Markdown 检查；`git diff --check` 通过。这里只验证阶段文档与现有仓库维护状态，不预报 T0–T8 已完成，也不证明未来语义的行为效果。
- 当前变更仅为迁移后的设计与新增计划两个未跟踪阶段文件；没有 Skills 源码、generated payload、稳定架构、配置、链接、Git index 或提交历史变更。本轮未运行生成器写模式；仓库检查使用其 `--check` 路径确认原有投影无漂移。
- 规划结束时待用户批准；此后用户已明确批准本设计适配范围与 T0–T8 实施，见顶部状态。commit/push、配置/安装或外部 host 开发仍不在授权内。

## I. 执行进度

T0 已核实：HEAD 仍为原基线，工作区仅两个本任务未跟踪阶段文件，`CLAUDE.md` 仍指向 `AGENTS.md`。使用当前 checkout，不建立 worktree/clone。当前 batch 工具无原 child continuation 参数；不尝试隐藏恢复或外部 harness。

T1、T2、T4、T5 分为一个独立 flat worker batch；每项 repository owner 均为本仓库，write_set 为其 D 节准确集合，resource lock 为该集合独占，禁止共享生成目录及 Git index/refs 操作。使用 host 管理的 isolated worker/export 边界；parent 在当前 checkout 检查最终 diff。execution profile 为 balanced，reasoning profile 为 standard。读入批准设计/计划及各自相关源码；brief 同时携带必要约束，不依赖未提交路径自动继承。worker 只返回源码候选与静态自检，未授予 shell 或最终验收；命令验证、裁决和 repair 决定保留 parent。完成条件为对应 T 任务场景语义齐全、引用闭合、无表外改动；能力不足或范围冲突须返回具体阻塞，不扩权。T3 与 T6 由 parent 实施，T7/T8 由 parent 汇合验证。

T1–T8 已完成：四项 worker 候选经 parent 核对与最小范围修正，三个新 reference 及相关入口/测试/稳定架构已落地；四项仓库生成/检查命令成功，最终 95 tests 通过（T6 按批准移除 prose snapshots，保留三项结构测试）。两个独立 implementation reviewers 均返回 pass，parent 裁决无未决 finding。评审候选 C1、最终候选 C2（仅补 Python 排版修复并重验）的身份、测试分类、设计 §12 与 §15.9 逐项语义验收及未验证能力见 [实施验证记录](2026-09-07-orchestrated-delivery-r1-verification.md)。未提交、推送、安装或修改外部 host；未声称真实跨调用续接或经济收益已验证。
