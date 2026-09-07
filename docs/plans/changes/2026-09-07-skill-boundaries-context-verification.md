# Skills 边界校准：候选实施与验证记录

日期：2026-09-07

初始 candidate outcome：`pass`。后续用户已批准当前 checkout 策略调整、整合、生成、commit/push；最新范围见[批准补充](2026-09-07-checkout-selection-amendment.md)，当前执行续记于本文末尾。

依据：[设计](2026-09-07-skill-boundaries-context-design.md)、[计划](2026-09-07-skill-boundaries-context-plan.md)、[现场审计](2026-09-07-skill-boundaries-context-audit.md)。

A–R 保留最初 candidate 交付时的事实；其中“未授权/未整合”的 C2 记录是历史状态，已被关联补充取代，不作为当前阻塞。

## A. 授权、版本与交付位置

用户已明确 `approve and $implement-change`，本次按计划 C1 完成 T0–T6 的 candidate 里程碑。计划保留原审批前记录，本文件记录本次批准与实际执行，不改写设计/计划的验收。C2 明确要求独立批准安装链接目标的整合影响，未从 C1 推导该权限。

- 原仓库 HEAD 与 candidate baseline 均为 `809d8e44aac40fd507311bb267bc0400064e6077`。
- Candidate：`/home/csheng/tmp/agent-skills/context-candidate-pAVsOI`。这是独立本地 Git 副本，无 configured remote，不被已安装 skills 链接指向；未在用户仓库或 candidate 创建提交。
- 完整产品 patch：`/home/csheng/tmp/agent-skills/context-candidate-pAVsOI.patch`，含 40 个源码/架构/生成文件的修改和新增文件，不含原工作区已有的三个阶段文档。校验清单与执行日志保留在同一 `~/tmp/agent-skills/` 目录；此记录另行保留在原仓库与 candidate 中。
- 原 checkout 已通过 `git apply --check` 对产品 patch 的可应用性检查；该命令未应用修改。新增交付记录后，两处 Markdown 检查通过（原仓库 303、candidate 311 个文件，均无 hard wrap）。
- 原仓库现有的 design/audit/plan 三个未跟踪文档已保真带入 candidate；未删除、覆盖或修改其内容。未读取凭据、修改用户配置/安装链接、执行模型行为实验、发布、推送或部署。

输入文件的当前 SHA-256：

| 文档 | SHA-256 |
| --- | --- |
| design | `8bff7421c3289d99dc9d835d53d76009b74631e998081cc0eb816fc0baa6b72d` |
| audit | `ac8d1d4cc2800748b0d3fd40250ac379034f1697dad69391923130f524bbded4` |
| plan | `c11aec1961529f7c36521ff6fa72e8c26cc8c2568ff5b8c18bd0bac8215ba38c` |

以上为迁移适配后的输入，不混用根 `design.md` 的旧 hash。

## B. 实施内容与范围核对

| 任务 | 实际修改与完成证据 |
| --- | --- |
| T0 | HEAD、dirty state、输入 hash 和链接目标已核实；创建未被消费链接指向的独立 candidate，保留用户文档。 |
| T1 | oracle/testing/design/plan 的触发入口按真实未决问题收紧；普通实现不受委派元数据门槛阻断；implement/repair/review 与 design/plan 调用方改为固定验收、证据驱动修复和必要定向复审；保留实际预算/取消/权限停止；同步 router 与 simplification 交接。 |
| T2 | worktrees 根文件只保留操作选择和共同约束，新增 create-and-context、compare、integrate、cleanup-and-repair 四个直接引用；实际路径贯穿操作，保留 context transfer、ignore、独有工作和删除权限边界。 |
| T3 | analyze-project 的局部问题、证据扩展与完整 audit 分支同时约束取证和输出；同步三个引用，去除 required axes 的隐性全量分析。 |
| T4 | 更新 skill-composition/invocation-contract 两个稳定文档并机械重生成；19 authored skill 文件、19 generated payload 文件与两个架构文档，共 40 个产品文件变化。 |
| T5 | 两个独立只读 reviewer 对互斥的 exact diff 切片分别返回实质 `pass`；parent 完成统一裁决，无 accepted review findings。 |
| T6 | 保留完整 candidate、可应用 patch、检查日志、fixture 源码与本记录；不整合 live-linked checkout。 |

受影响 public IDs 共 10 个：`analyze-project`、`code-simplification`、`design-change`、`executable-oracle-architecture-selector`、`git-worktrees`、`implement-change`、`plan-change`、`review-change`、`testing-strategy`、`use-coding-skills`。

39 个公共 IDs、contracts、source mappings、activation/permission flags、测试代码和生成器均未改变。执行生成后 `skills.index.json` 和架构图无内容变化；没有为了“同步”制造空意义差异。没有手改 generated payload，也没有添加 prose snapshots 或 runtime schema。

## V. 实际验证

### V1. Aggregate checks

在 candidate 根完整执行：

```bash
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
```

结果：contract-package、root-flat parity、install-surface/reference closure、index、diagrams、Ruff、ty、pytest 和 Markdown 全部通过；**98 tests passed**。修复后的完整日志为 `~/tmp/agent-skills/context-candidate-pAVsOI-aggregate-final.log`。

这些是 candidate 当前源码与分发证据，不是重复引用旧 baseline。原 live checkout 的 source/generated/contracts/architecture/index diff 仍为空。

### V2. Worktree commands：失败、修复与复验

首轮真实 fixture 发现新文档示例的错误：`rg --files --hidden -- <ignored-root>` 会遍历显式传入的被忽略目录，不能用它证明默认搜索将排除该目录。记录保留于 `context-candidate-pAVsOI-worktree-fixtures.log`，未将该轮计为通过。

**修复**：create-and-context 引用改为从 repository root 获取 normal 与 `--no-ignore` inventories，比对 marker 的实际相对路径；明确禁止把 ignored root 作为该验证的显式搜索 operand。验收仍是 marker 在 unignored inventory 出现、normal inventory 不出现，并被 Git 排除，没有弱化 oracle。

修复后通过 **95 条真实 Git/rg/diff 命令观察**，覆盖：

- default repo-local、自定义含空格位置、明确 repo-external 位置和对应 add/status/compare/remove。
- 缺失排除规则、local-exclude 安全写入且不重复、真实搜索 re-include 冲突、Git-ignore metacharacters 的 literal pattern。
- exclude 文件自身 symlink/directory、路径越界和 ancestor symlink 的拒绝条件，以及 linked-worktree 中实际 common-dir/exclude 解析。
- modified/staged/untracked/ignored 四类必要上下文不自动继承，授权转移后的 bytes/hash 一致。
- dirty/ignored/独有 commit 可识别，目标碰撞不覆盖原文件，多个 worktrees 的比较目标不能当成唯一来源。
- restore、cherry-pick `--no-commit`、merge `--no-commit --no-ff` 保持未提交结果和预期 HEAD，targeted repair 与 prune preview/执行。

Fixtures 仅包含可丢弃合成数据；没有配置 remote、联网或修改用户 worktree。合成提交和一次 fixture-only reset 仅用于建立独立测试输入，不是用户仓库提交或恢复策略。危险 cleanup 分支未执行在唯一用户数据上；predicate 与命令证据不等于 agent 会执行正确的暂停判断。

范围限制：tracking 语法用已有 local ref 验证，未连接 remote；interactive `restore -p` 未执行；无全输入空间或真实模型遵循性证明。实现要求其实际交互选择与相应授权可用后再执行。

可复查材料：

- `~/tmp/agent-skills/verify-context-worktree-fixtures.py`
- `~/tmp/agent-skills/context-candidate-pAVsOI-worktree-fixtures-repaired.log`
- `~/tmp/agent-skills/context-candidate-pAVsOI-worktree-fixtures-final.log`

临时合成 repository 已由 fixture 生命周期清理；唯一候选源码和证据保留。

### V3. Embedded shell 与语义场景

17 个嵌入 Bash 片段通过 `bash -n` 与 ShellCheck；为正文声明的输入/输出排除 `SC2154`、`SC2034`，其他检查未关闭。此项证明语法和相应 lint 属性，不把独立片段当成可直接顺序运行的脚本。

计划 V1–V16 的 semantic walkthrough 完成：

| 场景 | 当前 evidence |
| --- | --- |
| V1–V5 | description/body/router 对 bounded implement、requested artifacts、实际决策缺口、known tests/TDD 和 conditional delegation 的边界一致；不要求先加载 router。 |
| V6–V9 | implement 和 repair 引用保留 acceptance integrity、后续有效诊断继续、当前版本复审、已裁决 findings 复用，以及真实 blocker/预算停止；reviewer 始终只读。 |
| V10–V12 | operation references 明确 actual location、授权保真 transfer、ignored/unique-work 保护；上述真实 Git fixtures 支持命令属性；List/Compare 不继承 creation gate。 |
| V13 | 局部问题“哪个文件拥有 public IDs”可只读适用指令和 `contracts/skills.toml` 的相应结构后回答，不展开术语、健康度或全部 README。 |
| V14 | 当稳定文档与契约冲突时，仅沿对应 owner 和必要实现扩展；需要 drift/health 判断才读该引用，不自动开启 full audit。 |
| V15 | simplification audit/dispositions 未改变，授权充分的应用转 implement，实质取舍转 design；审计推荐自身不授予修改权限。 |
| V16 | 当前 candidate 完成 required generation/checks 与 review；无新变化或风险后停止，没有用重复验证填充预算。 |

以上语义证据来自原设计、当前源码和独立评审，不来自自然语言关键词单元断言，也不是一次受控模型行为实验。

## R. 独立评审、裁决与结论

一次 flat reviewer batch 分成两个独立、无共享写入的 evaluation slices：

- Lifecycle：D1–D3、repair/acceptance、router、simplification 和稳定架构；**pass**，无 material candidate finding。
- Disclosure：worktrees 与 analyze-project、实际路径/数据保护、渐进披露；**pass**，无 material candidate finding。

Reviewer 读取 candidate 的 exact authored patches 和有界 supporting references；没有执行验证、修改文件、递归委派或获得最终裁决权。parent 接受这两个有实质报告的结论，合成为当前 exact diff 的 review `pass`。没有 accepted review finding，也没有 post-review 源码修复；先前 rg fixture 修复在独立评审前已完成并复验。

独立评审覆盖的总 authored patch SHA-256：`8e6f1e45b96a3a30b476033d564f24081874fe0c91213ca1305205bb8a55794e`，该 patch 不含 generated 副本；generated parity 由项目检查单独证明。

**初始交付判断**：T0–T6 的 candidate milestone 已满足验收。该阶段未整合 live-linked checkout，未执行 install、commit、push、publish、deploy 或任何全局设置修改。后续权限与执行如下，不将这个历史状态作为当前阻塞。

## S. 用户批准补充后的当前 checkout 交付

用户随后接受 current-checkout 默认、证据驱动隔离及既有 symlink 预期读取不单独设安装 gate 的建议，并明确要求修改、flatten、commit、push。按关联补充执行，而非为通过验收自行改写计划。

- 整合前：当前 `main`、configured upstream `origin/main`、远端 `refs/heads/main` 与原 candidate baseline 均为 `809d8e44aac40fd507311bb267bc0400064e6077`。工作区仅有本任务四个未跟踪阶段文档，无其他用户代码修改。
- 已在当前 checkout 应用通过评审的 authored diff，未新建 worktree/clone/branch 或进行分支合并；generated payload 由项目生成器重新生成，不手工移植旧副本。
- 新策略写入 implement-change、git-worktrees 两个根 skill；skill-composition 与 install-surface 记录稳定责任/授权边界。原设计、计划、审计和本记录明确 supersession，新增用户批准补充文档；原候选 hash 和失败/修复轨迹仍表示当时版本，不用于校验后续已批准改动。
- 已在当前 checkout 完整执行 index、root-flat、diagram 生成与 `bash scripts/check.sh`：全部通过，**98 tests passed**，Markdown 312 files、0 hard wrap。contracts、测试代码、生成器、public IDs、权限字段、index 内容及图内容无变化。
- 两个独立只读 reviewer 对新增 checkout/concurrency 语义与 installation authority/truth supersession 分别返回实质 **pass**，无 material findings。parent 接受结论，无 accepted repair；此前 candidate review 和未改变的 command fixtures 证据仍适用。
- 新增场景核查通过：task-local dirty、无关 disjoint dirty 均可原地实施；overlap 先判断归属；有共享写冲突证据才评估隔离；进程/时间戳/dirty 不证明并发，检测不等于互斥；显式 worktree 请求仍被尊重；提交文档不是前提；预期 symlink payload 更新不扩大到配置、安装或部署权限。
- 原有 95 条 Git command observations 和 17 个 shell fragment checks 的命令示例未被本补充改变，因此保留其有效证据，不重复运行无变化 fixtures。没有模型行为或经济收益实测。

当前实现与生成物的验收结果为 `pass`。本次 commit/push 权限来自用户明确请求；仅提交本任务完整已验证变更，使用已确认的 `main → origin/main`，不包含原隔离 clone、临时日志/fixtures，不 force、不改写历史。具体提交对象和远端结果以 Git 记录及最终答复为准；没有授权或执行全局配置变更、额外安装或部署。
