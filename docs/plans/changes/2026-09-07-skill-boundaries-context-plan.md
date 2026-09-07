# Skills 触发边界、验收收敛与渐进披露实施计划

日期：2026-09-07

状态：已获实施批准，初始 candidate 里程碑已完成；当前 checkout 整合、策略补充及 commit/push 按[用户已批准补充](2026-09-07-checkout-selection-amendment.md)执行。

目标仓库：`agent-skills`；唯一 writable repository owner 为该仓库。

设计输入：[本地适配设计](2026-09-07-skill-boundaries-context-design.md)；原始交接输入的 hash 保留在设计与审计中，不作为当前文件 hash。

现场基线：HEAD `809d8e44aac40fd507311bb267bc0400064e6077`。

核实记录：[现场审计](2026-09-07-skill-boundaries-context-audit.md)。

以下保留最初 candidate 计划及其当时权限记录，供追溯而非重复设 gate。C1 已满足；C2/T0/T6 的默认隔离和独立整合批准条件，以及 C5 的 commit/push 限制，已被关联补充中的用户明确决定替代。D1–D7、场景验收、数据保护和其他权限边界保持不变。

## P. 目标、范围与不变条件

### P1. 本次里程碑

交付与设计 D1–D7 一致、已生成并验证、可供用户审查和整合的 repository candidate：

- 普通实现 readiness 不依赖委派 profiles、parallel policy 或固定 review budget。
- 对已授权目标按验收和当前证据持续修复，允许必要定向复审，不设默认 repair 次数上限。
- discovery descriptions、正文和相关调用方按真实未决问题触发，不把 design/plan/oracle 设成直接实现的隐性前置步骤。
- worktrees 按操作读取引用并统一实际位置；analyze-project 按问题和证据展开取证。
- 保持生成投影、引用闭包和稳定架构说明一致，并将 workstation 审计与仓库修改分离。

设计前提仍成立，不要求新的 architecture/language decision。只是修改既有 Markdown/TOML 和机械生成投影，不创建服务、持久化工具或运行时边界。

### P2. 固定 acceptance baseline

基线为[本地适配设计](2026-09-07-skill-boundaries-context-design.md)第 1–10 节确认的方向、下文 V 场景及当前仓库授权/分发契约。实现细节可以调整，但不得删除失败要求、改变 non-goals、降低权限限制、放宽公共契约或改写设计/本计划的验收以制造通过。测试实现确实错误且有独立契约证据时，可在已获准的测试修改范围内纠正；修改“什么才算正确”必须交回用户。

保持 39 public IDs、source mapping、activation modes、mutation/spawn flags 与公共 skill 目录形状。reviewer 只读，active agent 负责判断、整合、验证、裁决、修复及最终答复。每次 review 只评价一个明确目标，并不等于整个 change 只能 review 一次。

### P3. Non-goals 与后续工作

不安装/重装、不修改任何 `~/.codex`、`~/.pi`、`~/.agents` 文件或其他工程 AGENTS；不创建缺失的 Codex AGENTS；不改路由模型配置、host profile、插件、hooks、session state 或 subagent executor。没有证据要求重写本仓库根 AGENTS。

不新增公共 skill、runtime gate/schema、orchestrator、attempt ledger、benchmark runner、模型矩阵、统计收益门槛、强制 router 或模型专属正文。不广泛重构其余 skills，不调整 `code-simplification` 的审计门槛和 disposition 枚举。不增加自然语言逐字/关键词/prose snapshot 测试。

用户级配置修复、host 提前结束诊断、受控行为评估及实际消费环境激活均为独立后续范围。它们不阻塞可以独立验证的 repository candidate。

## C. 前提与权限清单

| 编号 | 状态 / 决定 |
| --- | --- |
| C1 · 当前权限 | 用户已授权现场核实和形成计划，未授权实施。只有用户批准范围并要求实施后才能开始 T0–T6；review 通过不能替代批准。 |
| C2 · Live-linked 整合 | 已确认 39 个安装链接指向当前 checkout 的 `skills/`。默认先在不被这些链接指向的隔离工作副本产生 candidate；无需修改任何发现路径。将 candidate 整合回链接目标 checkout 会改变安装内容的后续读取，必须由用户显式批准该影响。未批准时，里程碑在已验证 candidate/handoff 结束，不声称已更新当前安装。 |
| C3 · 非自动前提 | 本轮 candidate 的源码、设计、工具和本地检查均可访问，当前没有 account/login/license/hardware 前提。若执行时发现新的必要输入或权限，报告具体 `manual_checkpoint`，不把人工前提藏进任务。 |
| C4 · 测试权限 | 可在批准实施范围内使用只含合成文件的临时 Git fixtures、隔离副本及项目缓存；不访问生产、远端仓库、真实其他 worktrees 或云服务。临时资源不得出现在用户 skills 发现路径中。 |
| C5 · 外部动作 | 用户仓库的 commit、push、publish、deploy、远端 mutation、修改全局配置和删除用户 worktree 均未获授权。即使验收全部通过，也不执行。可整合的 diff 不依赖先 commit。V-Worktree 的 disposable fixture 可建立仅含合成数据的本地提交，这是测试 setup，不是用户仓库提交。 |

T0 保真带入 `docs/plans/changes/2026-09-07-skill-boundaries-context-design.md`、本计划、审计记录及必要当前文件，包括尚未跟踪的内容，记录当前 bytes/hash 和 baseline；不能假设只拷贝 HEAD 就足够。不得为了传递上下文要求唯一的“先 commit”路径。若没有可用的授权保真隔离方式，停止 candidate mutation 并报告具体缺口，不静默生成到 live-linked 目录。

## T. 实施任务

### T0 · 固定执行证据与隔离边界

**依赖**：C1 的实施授权；无其他实施任务依赖。

**写入边界**：隔离工作副本和临时 fixture 所需的本地资源；不改用户配置/安装链接。阶段证据后续由 T6 写入 `docs/plans/changes/2026-09-07-skill-boundaries-context-verification.md`。

**工作**：复核 HEAD、dirty state、design hash、安装链接目标；保真提供当前任务上下文；明确 candidate 不被消费者发现，记录 recovery owner 和资源清单。不指定 host 的目录 flag、scheduler、模型或快照协议。

**完成证据**：与现场基线的差异说明、必要上下文 hash 相等、candidate/source owner 明确、live target 未被修改。若基线新增用户修改，保留并判定影响，不覆盖。

**恢复**：`stop_and_diagnose`；未验证上下文和隔离前不做源码修改。只清理本任务新建且确认不含唯一工作或证据的资源。

### T1 · 统一触发、readiness 与验收驱动的 repair

**依赖**：T0 的可用 candidate 和冻结的验收基线。

**精确 authored 写集合**：

```text
src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md
src/skills/disciplines/testing-strategy/SKILL.md
src/skills/workflows/design-change/SKILL.md
src/skills/workflows/plan-change/SKILL.md
src/skills/workflows/implement-change/SKILL.md
src/skills/workflows/implement-change/references/repair-loop.md
src/skills/workflows/review-change/SKILL.md
src/skills/session/use-coding-skills/references/routing.toml
src/skills/disciplines/code-simplification/SKILL.md
src/skills/disciplines/code-simplification/references/candidate-evidence.md
```

**工作与完成条件**：

- 将 design/plan/oracle/testing descriptions 改为解决何种未决问题及最关键反例，正文一致。明确用户要求 design/plan 产物时仍交付产物，不自动实施；已有明确策略的常规测试不触发重新选择策略。
- selector 拥有 oracle 方法选择，而非普通实现准入 schema；本地实现只需相关目标、scope、保护边界、权限与验收证据。实际委派才消费 plan/implement 的 repository owner、write set、isolation、convergence 等事实；declared delegation-ready profiles 继续按既有条件提供。TDD 不等于委派。
- 删除普通 readiness 的 mandatory maximum review budget，以及将任何任务都指向 scheduler graph fixture 的暗示。保留真实 scheduler 产品选择 model/contract tests 的适用场景，不移除 host 的实际资源限制。
- implement 与 repair reference 覆盖 verification failures 和 accepted review findings；围绕当前验收、有效诊断和范围继续修复。旧 findings 有有效证据才复用；已裁决且无新证据的不重开，新回归不能被旧 review pass 掩盖。
- `non-convergent` 保留为兼容 outcome，但仅用于无新诊断证据且无合理范围内路径；不能定义成第 N 次失败。`blocked` 可表达显式预算/取消等未完成停止，必须写明实际原因、已完成/剩余工作，不把预算耗尽说成设计不可行或 pass。
- 存在矛盾验收、失效设计前提、新范围/权限需求时，保留证据并返回适用 replan/redesign/needs-authority，不自动修设计目标。无新变化、失败或风险且已通过时及时完成。
- design/plan 调用方允许定向 artifact repair/rereview，但不自动获得用户批准。review 入口保留一次一个目标、只读、无递归和 parent 裁决。
- 校准 router 的相应 negative cases，保留 direct-match bypass、单 primary owner 和 39 IDs。修正 simplification 两处无条件 design 交接以及 router 对应文本；候选审计本身不授权应用。

**验证**：逐项审查 V1–V9、V15；检查 frontmatter/TOML 可解析，审查相邻 evaluator、session guidance、provider metadata 无反向要求。搜索只是发现冲突的工具，不将“没有命中词语”作为语义通过标准。T4 生成后运行 V-Aggregate。

**恢复**：`fix_forward`。将越界 findings 交回 parent 裁决；不能通过扩大 scope、给 reviewer 写权限或放宽验收消除失败。

### T2 · 按操作拆分 git-worktrees 并统一位置策略

**依赖**：T0 的 candidate；不依赖 T1 的文字修改。

**精确 authored 写集合**：

```text
src/skills/git/git-worktrees/SKILL.md
src/skills/git/git-worktrees/references/create-and-context.md
src/skills/git/git-worktrees/references/compare.md
src/skills/git/git-worktrees/references/integrate.md
src/skills/git/git-worktrees/references/cleanup-and-repair.md
```

除根文件外均为新引用，名称在此冻结，不新增 public skill。

**工作与完成条件**：

- 根文件保留适用性、操作选择、最小 list、授权及防丢失共同约束；只读取所选分支的直接引用，不要求先读所有 references。Compare/List 不加载 creation/context-transfer/ignore-setup 前提。
- 创建分支先遵循适用 repository policy；无策略才取 `.agents/worktrees/<slug>`。只有请求与策略冲突不能自行解开、目标不明或不安全才暂停。
- 用已解析并引用保护的实际路径贯穿 add、status、ignore、compare、integrate、cleanup 和示例；不在后续逻辑硬编码默认位置。repo-local 嵌套路径检查 Git 与实际搜索工具的有效排除；repo 外部路径不要求虚构 repository `.ignore` 条目。不能仅检查某个 ignore 文件恰好含一行文本。
- bounded handoff 的 local-exclude 例外仅适用于已授权且可安全验证的 repo-local 临时路径；保留实际 Git common-dir/exclude 解析、防 symlink 和路径逃逸、不能为启动 handoff 改 tracked ignore 的限制。外部路径不套用该例外。
- context-transfer 保留必要文件的 committed 或显式授权保真转移二选一；未提交源/config 的 filesystem 需求仍必须真实满足。移除示例中“未提交一律先 commit”的矛盾，不放宽数据保护。
- integration 使用用户已选择的最小操作，冲突时保留状态；cleanup 检查 modified、staged、untracked、ignored、独有 commits 与本地 overrides。`--force` 不成为快捷默认；remove/prune/repair 只对已授权目标应用。

**验证**：V10–V12 与 V-Worktree；T4 reference closure、root-flat parity 必须覆盖新引用。逐操作审查未选择的分支不会被强制加载。

**恢复**：只对本任务创建的 disposable fixtures 清理；真实 checkout 不执行 worktree merge/remove。fixture 失败先诊断命令/路径，不以 force、rm -rf 或全局 ignore 修改绕过。candidate 文本用 `fix_forward`。

### T3 · 让 analyze-project 的取证深度随问题展开

**依赖**：T0 的 candidate；与 T1/T2 无共享写文件。

**精确 authored 写集合**：

```text
src/skills/workflows/analyze-project/SKILL.md
src/skills/workflows/analyze-project/references/output-contract.md
src/skills/workflows/analyze-project/references/doc-health-and-drift.md
src/skills/workflows/analyze-project/references/full-audit-output.md
```

**工作与完成条件**：

- 根入口区分局部事实查询、证据不足后的定向扩展和用户要求的完整 audit。先遵循适用指令，定位足够的稳定事实源并必要核实；不固定先读所有 README/术语/健康度材料。
- 未知 owner、冲突事实或证据不足触发扩大调查；只有需要健康/漂移分类时读取对应引用。完整 audit 才使用 full-audit section 要求。内部读取和最后输出同样按范围缩放。
- 同步 output-contract 的 required axes 和 doc-health 的无条件报告措辞，避免将全量分析要求从根文件搬到必读 reference。
- 保持只读、稳定事实与阶段历史区别、搜索不命中不能证明隐藏文件不存在、领域 primary 的证据 overlay 和证据可信度说明。

**验证**：V13–V14；以一个明确局部事实和一个确需扩展的冲突问题作文本路径 walkthrough，记录实际应读 owner/reference，不运行全项目重建或模型实验。T4 检查引用闭包与生成一致性。

**恢复**：`fix_forward`；不能以少读为由忽略 applicable project policy，也不能因文档退化自动声称重建成功。

### T4 · 同步稳定 truth 并生成 candidate 投影

**依赖**：T1、T2、T3 的最终 authored diff，以及 parent 对三者交叉语义的汇合判断。该 parent 判断是真实串行边界，不投影为 worker hard edge。

**精确 authored 写集合**：

```text
docs/architecture/skill-composition.md
docs/architecture/invocation-contract.md
```

**机械生成表面**：上述 10 个受影响 public IDs 的 `skills/<id>/` payload（含新 references 和 generator-owned metadata）、`skills.index.json`；仅当相应生成源变化导致实际差异时保留 `docs/architecture/diagrams/skill-composition.puml` 与 `docs/architecture/generated/skill-composition.svg` 的生成变化。不得手改生成物。

**工作**：稳定文档只补直接进入实现、readiness 分层、按验收 repair/定向 review 的 durable 边界；不复制整篇设计/审计。当前 `contracts/skills.toml` 不需要修改：现有 identity/activation/permissions/dependencies 已足够表达新语义。`review-components`、AGENTS、provider manifests、generation scripts 和测试代码均不作为预设写集合。

**生成和验证**：在隔离 candidate 根运行以下 V-Aggregate 完整命令链。若 generator 触及其他公共 ID 或 contract/权限需要变更，先定位生成漂移/新需求；不得把它作为机械同步默认吸收进 scope。

**完成证据**：39 IDs 不变、投影 parity/reference closure 通过、默认发现反例在 description 可见、无必经 router/隐式批准；全部 generated diff 有 authored owner。

**恢复**：`fix_forward`，修 authored owner 后重新生成，不修安装副本。需要扩大契约或权限则 `replan`，不自动增加 gate 或依赖。

### T5 · 验证、独立 review 与范围内收敛

**依赖**：T4 的 converged candidate、V-Aggregate 输出、V 场景和 V-Worktree 证据。

**写入边界**：不新增产品写集合；accepted repair 仅使用 T1–T4 已批准文件，再生成其投影。所有命令执行和 acceptance 判断归 active parent。

**工作**：因本变更涉及授权、终止条件与 Git 数据保护，要求一次独立 `review-change` 对当前 exact diff 评价；只给目标、设计/本计划、相关源码、场景矩阵、commands/results 和实际风险边界。reviewer 不修改、不递归、不另建上游产物。

parent 裁决每个 material finding；accepted in-scope defect 按固定验收持续诊断/修复，重跑受影响证据及必要 aggregate。修复使旧 review 证据失效或仍有独立判断需求时定向 rereview，不每次全仓复审。执行本次已批准 D2 的语义，不继续从旧安装文本继承默认一次 repair 限制。

**完成证据**：全部 required verification 通过，material accepted findings 解决，审查覆盖当前版本；未完成/不可取得的证据明确为未完成。工具报告 succeeded 但无实质评价时不能算 review pass，须获得有效评价或明确报告 review blocker。

**恢复**：按 X 条件收敛或停止；reviewer 的意见不改变验收权。本任务无固定默认次数预算，不会自动创建继续工作所需的外部权限。

### T6 · 形成可审查交付与条件整合

**依赖**：T5 的验证和裁决证据。

**精确阶段产物写集合**：

```text
docs/plans/changes/2026-09-07-skill-boundaries-context-verification.md
```

该文件记录真实 changed files、commands/results、V 覆盖、review 裁决、repair/stop 原因、设计/执行版本和 consumer 未实测限制，不成为下一次任务必读状态机。不得改写本计划或原设计的已批准验收。

**默认完成条件**：保留可应用的完整 candidate diff 和新引用/上下文文件，报告尚未修改 live-linked checkout；不以未获授权的安装激活阻塞 candidate 交付。不能为清理丢弃唯一 candidate。

**条件整合**：只有 C2 的额外影响获准后，parent 才复核 live target drift，保留新用户修改并整合同一审定 diff。整合后的 tree 若与验证版本不同，重跑受影响及 repository-required 检查；若字节、路径、权限及适用环境等价且无新风险，复用有效证据，不为消耗预算反复测试。新会话/reload/行为观察需要相应授权，未运行就不宣称 activation 成功。

## G. 顺序、并行与委派

事实顺序：`T0 → {T1, T2, T3} → parent 汇合 → T4 → T5 → T6`。

- T1/T2/T3 的设计决定已冻结，写集合互斥，可作为命名的独立候选组 `G-source`；它们没有叙事性 hard predecessor。
- 默认由主 agent 保有执行；本次用户没有要求 delegated implementation，本计划不宣称 delegation-ready，不要求填写 profiles。若实际委派，须先落实每片单仓 owner、精确 writes、隔离、共享资源 locks、completion evidence、failure policy 和 parent convergence；声明 delegation-ready 时按既有语义 vocabulary 提供 profiles。
- 子任务不得写 generated roots、架构汇合文件或彼此的 source；生成目录、index、diagrams 和 aggregate check 是 parent 共享资源，避免并行生成覆盖。
- T4/T5/T6 包含 parent synthesis、verification、authority、adjudication 或 continuation，不能交给 worker 或编码成无干预 hard chain。
- 当前探索工具出现“succeeded 但没有最终报告”的证据，故委派可用性仍需按每次实质输出判断。委派不是用户硬要求时允许主 agent 接回；若用户后续指定必需 host/route，不静默换模型、harness 或串行降级。

## V. 验证策略与 acceptance 场景

**Oracle 决定**：自然语言语义以固定设计与人工/独立场景审查为 substitute evidence；结构/分发用现有 parser、metadata、reference closure、generated parity 和 deterministic tests；worktree 示例用真实 Git 的 disposable command fixtures。不选模型 runner、prose snapshots、TDD readiness schema、性能对照或生产 probes，因为它们不能替代本次所有权问题，且不是本轮前置需求。

owner 均为 active implementing agent；reviewer 只提供独立证据。fast/local lane 先做范围内检查，merge-readiness lane 做完整项目 gates 与 exact diff review；无 release/runtime lane。

### V-Aggregate · 仓库声明检查

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

前三项只能在满足 C2 隔离/授权条件的目标执行。`check.sh` 已包含 contracts、root-flat/index/diagrams `--check`、install surface、Ruff、ty、pytest 和 Markdown。受影响结构检查可先针对 `tests/test_skill_routing_contracts.py`、`tests/test_semantic_skill_contracts.py`、`tests/test_skill_workflow_contracts.py`、`tests/test_skill_activation_contracts.py` 与 `tests/test_runtime_distribution_contracts.py` 定向运行；最终不能用定向子集替代 aggregate。

现有测试不逐字冻结 repair/description，现有 checker 已验证引用闭包，本计划不要求增加测试代码。若实际暴露新的可执行接口回归，先报告具体接口与需要增加的精确测试写集合；不得静默加 prose keyword tests，也不删除有效既有 oracle。缺少环境能力须保留失败输出，不能跳过后报 pass。

### V-Worktree · 真实命令证据

在候选实现的 disposable 合成 Git repository 运行实际文档中的命令分支；不调用 agent runner。只允许为该 fixture 建立本地合成提交，不 commit 用户仓库、不设置 remote、不联网。将所有命令、输入参数和退出状态记录为阶段证据，临时 shell 逻辑不得进入公共 skill runtime。

| fixture | 证据要求 |
| --- | --- |
| 无 repo 位置策略，默认 repo-local path | add/status/list 使用已解析默认路径；Git 和所用 rg/fd 的真实 inventory 不包含 disposable marker。 |
| repo 明确自定义 repo-local 位置，含空格 | 相同操作及 ignore 检查消费实际路径，不能仍验证默认目录；在冲突未出现时不因不同位置停止。 |
| repo 明确 repo 外部位置 | add/status/compare/remove 在该目标工作；不虚构仓库内部 ignore 设置；不静默 fallback。 |
| 缺失/冲突 ignore，普通创建 vs 已授权 isolated handoff | 普通创建需明确决定；handoff 只用允许的 local-exclude，验证 symlink/越界拒绝及实际 search exclusion，不修改 tracked ignore。 |
| modified/staged/untracked/ignored context | 对照源与接收上下文 bytes/hash；缺失 required filesystem 状态的反例不被声明完整。 |
| dirty/ignored/独有 commit 的 cleanup，源不明的 compare，target collision | 用 status、ignored inventory、commit reachability 和目标检查证明危险输入可识别；不得真的执行数据丢失分支。策略是否正确要求停下由语义审查确认，Git fixture 本身不证明 agent 会遵守。 |

只读 List/Compare 的 walkthrough 单独验证不需要创建位置、ignore setup 或 context transfer。嵌入命令的执行证据与 agent 行为声明严格区分。

### V-Scenarios · 语义回归矩阵

| ID | 情境与验收 | 任务 |
| --- | --- | --- |
| V1 | 范围/目标/验收明确且获实现授权：直接 implement，不先 design 来获得 no-design。 | T1 |
| V2 | 明确要求 design 或 plan 文件：交付产物，不重新发明决定，不自动实施。 | T1 |
| V3 | 直接执行途中发现矛盾接口/权限：指出最小真实决定，不越界。 | T1 |
| V4 | 本地主 agent 跑已知命令、按既定契约补测试或 TDD：无 profiles/parallel/budget 元数据门槛。 | T1 |
| V5 | 委派隔离/write set/convergence 不明：不能报可委派；用户允许时本地执行，硬要求不满足时报具体 blocker。 | T1 |
| V6 | 第二次或后续仍有范围内缺陷和新诊断：继续相同验收，不按次数停，不反改 plan。 | T1/T5 |
| V7 | 修复引入回归或旧 review 证据失效：修新缺陷并在必要时定向复审；不机械重开已裁决问题。 | T1/T5 |
| V8 | 验收前提无效、无可行诊断、缺权限、预算/取消：区分原因，保留证据与剩余工作，不报 pass。 | T1/T5 |
| V9 | 既有、不相关、无新证据或 reviewer 偏好：有依据地裁决，不自动扩大 scope；reviewer 仍只读。 | T1/T5 |
| V10 | repo 自定义位置：全分支使用实际位置，适用 ignore 跟随操作/路径而不是硬编码默认。 | T2 |
| V11 | 未提交必要上下文：已有授权且保真转移可继续，缺 filesystem 状态才阻塞；无需强制 commit。 | T2 |
| V12 | cleanup 含 unique work/ignored overrides：不丢失数据；List/Compare 不被 creation gate 阻塞。 | T2 |
| V13 | 局部项目事实问题：只取足够稳定事实并针对核实，不能固定做全项目健康审计。 | T3 |
| V14 | 证据冲突或不足：按需要扩展，完整 audit 按用户范围；保持 scoped instructions 和搜索边界。 | T3 |
| V15 | 已授权的 simplification candidate 应用 vs 尚有实质取舍：分别转 implement/design；审计不产生授权。 | T1 |
| V16 | 修改 authored skills：执行必要生成/检查；已满足全部要求且无新变化：完成，不重复测试或 review。 | T4–T6 |

本次 baseline `bash scripts/check.sh` 已通过，98 tests passed。候选语义、命令示例和新投影尚未实施/验证；不能将 baseline 结果记成新版本通过，更不能宣称模型已减少误触发或节约成本。

## X. 继续、停止与恢复

- X1：有有效新证据且范围内可修复，继续 `fix_forward`；必要复审限定当前版本、修复和受影响边界，无默认固定次数限制。
- X2：验收矛盾或批准 premise 失效，返回具体 `replan`/`redesign` 决定；不回写设计或弱化 oracle。
- X3：权限、输入、host 能力或隔离不足，停止该受阻分支并报告；可以独立完成的授权工作继续，整体不报 pass。
- X4：只有重复诊断且无新证据/合理路径，说明已排除项和缺失信息后报 `non-convergent`，不按失败计数命名。
- X5：显式预算耗尽或用户取消，遵守真实限制，保留当前 diff/证据并报告未完成；不把预算停止等同于不可实现。
- X6：live target drift 或出现计划外生成/权限变化，parent 先裁决，不覆盖用户修改，不做 destructive reset/clean，不自动修改全局配置。

不设 guarded rollback：当前没有证据证明破坏性回退比修正文案/重新生成更安全。临时资源仅在无唯一工作和证据的条件下清理；撤销当前切片也只能撤销本任务拥有的修改。

## R. 计划评审与批准记录

**Review decision：required。** 风险依据是 readiness/continuation/批准边界联动、worktree 防丢失规则迁移及 live-linked 分发影响。评审目标仅为本计划与现场证据，不要求先实现或构造模型实验。

**独立评审 verdict：`pass`，无 material candidate findings。** 本次通过 `review-change` 的 bounded evaluator 对内联提供的 P/C/T/G/V/X 计划边界摘录及明确标注的现场事实进行只读评价，覆盖 candidate/live-linked 权限分离、任务事实依赖、readiness、修复/停止和证据架构。没有以工具 `succeeded` 代替实质报告。

**Parent adjudication**：接受本次 bounded pass；无 accepted findings，无需计划 repair。parent 已直接核实源码 owner、精确写集合、生成命令、基线结果与新文档一致性。评审未独立核验实现代码、candidate 命令结果或 consumer 行为，因此不将其扩大为整个未来实现通过。T5 仍需对实际 candidate diff 做独立评价。

文档归档适配：原始根设计已迁入同目录的 `2026-09-07-skill-boundaries-context-design.md`，补入已核实状态并更新交接引用；D1–D7、任务写集合、验收和权限均未改变，既有计划边界评审仍适用。实施时记录适配后设计的当前 hash，不使用原始输入 hash 校验新文件。

最初计划提交时待定的是 C1 与 C2；后续批准及 C2 的替代决定见文首关联补充。全局配置修改、行为实验和部署仍不纳入本次范围。
