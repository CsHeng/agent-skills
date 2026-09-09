# 目标驱动、风险适配与执行裁量实施计划

日期：2026-09-09。基线：`024312cbb1007c3578d5257d03301e184f041bf9`。

设计入口：[已确认方向的设计](2026-09-09-goal-driven-risk-adaptive-delivery-design.md)。状态：`completed`；实施 `pass`；设计/计划及有界实施审查已完成。用户已通过“approve and $implement-change”批准本计划的本地实施范围，不包含安装或外部变更。

## A. 里程碑与非目标

交付设计 A–F 定义的共享语义、相关 overlays 校准、精简计划/收尾表达、正反行为案例及 Pi 会话挖掘支持，并完成 authored/generated 一致性与必要验证。主目标是有裁量且有边界的连续交付，不是零询问、最大执行量、最大测试量或零风险。

设计 C1–C6 承接用户已确认的标准，不再以“补全每个降级 feature”作为本计划前置。本地源码实施已按批准范围完成。所有下列任务都属于批准后应交付的范围，可选真实模型效果实验不在任务列表，不成为中途审批卡点。

保留 39 public IDs、角色/权限/语义依赖、直接触发、conditional review、parent 裁决、现有结果枚举及当前 checkout 默认。不改 `contracts/skills.toml`、routing/profile 词汇、生成器、插件 metadata、Go/Python 具体库政策或外部项目。只对本变更触及的安全示例和 miner 旧建议做必要修正，不开展通用安全重写或全仓历史清理。

## B. 已知前提与实施自由

当前工作区在文档编写前为 clean。已有 Python 3.11+ stdlib scanner、同目录 unittest CLI 测试、根仓库 `uv`/pytest 与生成检查；Pi 的格式来自已查阅的 v3 session-format 文档（本机 Pi 0.85.1 文档），它是解析输入而非运行时依赖。现有 `testing-strategy/references/agent-skill-evaluation.md` 已存在，无需新建效果评估引擎。

没有已知账号、硬件、生产权限或真实 session 数据前置。计划批准后无需另行允许普通文件细化、合成 fixtures、检查、审查和有界修复。未确认的技术细节留给实施，例如 Pi 计数键、内部 scanner helpers 和正文组织；这些不得破坏设计 E 的兼容、安全与报告语义。

继续当前 checkout，保留本次设计/计划和无关不冲突修改。只在真实写冲突、明确仓库政策或用户要求下隔离，不把 dirty、未提交阶段文档或 agent 进程当作新审批原因。委派是否可用只影响劳动分配，不阻塞可由 parent 完成的本地工作。

## C. 任务与写入范围

下列范围是本仓库的 authored 模块/文件边界，不是 host dispatch payload。模块内可细化必要 references、段落和既有测试；不得借此修改其他 Skills 或增加新公共能力。未来实际 worker 仍需 parent 提供准确排他的 write paths；共享生成物和架构汇合由 parent 统一处理。

### T0 — 核对批准与当前源码

- 依赖：用户批准本计划的本地实施范围。
- 写入：无；读取设计、计划、当前 AGENTS/HEAD/status 和下列目标。
- 完成：识别真实漂移和冲突，确认本次目标、裁量、禁止动作与技术检查可执行；未发生实质边界变化即继续 T1–T3，不重复调研全部历史会话。

### T1 — 统一目标、续接、评审与报告语义

- 依赖：T0；消费设计 C1/C3/C6/D，不等待 T2 的文字实现。
- 写入模块：`src/skills/workflows/design-change/`（SKILL 与 `references/goal-alignment.md`）；`src/skills/workflows/plan-change/`（SKILL 与 `references/delivery-and-delegation.md`）；`src/skills/workflows/implement-change/`（SKILL、repair-loop、delegated-execution）；`src/skills/workflows/review-change/SKILL.md`；`src/skills/review-components/review-{design,plan,implementation}/SKILL.md`；`src/skills/workflows/close-change/SKILL.md`；`src/skills/workflows/sync-truth/SKILL.md`。
- 配套写入：`src/skills/disciplines/organize-docs/SKILL.md`、`src/skills/session/output-styles/references/implementation-closeout.md`。不修改 stress-test、router 或其状态词汇。
- 工作：让已授权 best-effort 次要目标取舍属于实施裁量；保护主目标/必要条件/指定技术；澄清完成即恢复任务；已批准部署不重复审批；真实生产影响变化仅暂停相关动作。Brief 携带主目标、取舍边界及环境事实，而非让 child 自授权限。审查同时找目标漏项和过强 gate；收尾承认有披露的合法取舍，不新增 outcome。
- 工作：批准摘要区分人类决定、事实调查、实施产物和技术验证；精简当前有效计划，历史使用短引用，不复制旧 gate 豁免。语义在各 Skill 独立可用，不形成强制统一配置或生命周期。
- 完成证据：逐条对照设计 F 的相关正反例，明确何时继续、何时局部停；不以 Markdown 关键字测试证明行为。限定相关引用闭合、prose 检查及有证据的局部修复。

### T2 — 校准风险、恢复、验证与安全建议

- 依赖：T0；消费设计 C2/C4/C5/F，与 T1 无文件重叠。
- 写入：`src/skills/policies/development-standards/SKILL.md`；`src/skills/policies/security-guardrails/`（SKILL、`references/examples-python.md`、`references/infra-security.md`）；`src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md`；`src/skills/disciplines/testing-strategy/SKILL.md`、其现有 `references/agent-skill-evaluation.md` 及新增 `references/goal-and-risk-cases.md`；`src/skills/disciplines/infrastructure-triage/SKILL.md`；`src/skills/disciplines/error-patterns/SKILL.md` 与 `references/debugging-tight-loop.md`。
- 工作：按实际暴露/可利用性/损失/状态价值/控制成本选措施，开发部署不自动升为生产；已授权可丢弃状态允许重建，重要状态局部保护，真实生产破坏性动作保留必要恢复证据。去掉普通失败默认 backup 的过宽要求，按旧证据是否失效重验，不能按 revision 反复全套演练。
- 工作：风险/oracle 标签不产生固定 review 或全矩阵；测试主路径和真实用户目标，保留必达 oracle，允许已批准适配结果。局部诊断不能因无法构造完美 agent-runnable reproducer 就冻结其他工作，也不以固定假设数或测试数定义努力程度。
- 工作：条件化 security 清单并消除直接矛盾的示例；可以删除误导性代码或缩成有前提的示例，而非建设新加固产品。保留有效安全机制，尤其不能用低效检测套路代替真正防线。指定库保持，glue 归实施；不设置新的语言/库偏好。
- 工作：把设计 F 转为简洁通用正反场景并连接现有 evaluation reference。场景是离线审查/未来可选比较材料，不是机器审批表、必跑 live case 或对私有会话的复制。
- 完成证据：覆盖激进开发正例与生产/重要数据反例、恢复证据复用和必要失效、主目标用户场景；检查 root 与相关 reference 不相互推翻。若保留/修改可执行示例，执行与该片段目的相称的验证；不为示例构建完整服务、容器或 CI 环境。其他无关历史示例问题不扩入。

### T3 — 增加 Pi 只读输入与结构化回归

- 依赖：T0；设计 E 是稳定输入，不依赖 T1/T2 源码或外部 Extensions。
- 写入：`src/skills/disciplines/skill-miner/SKILL.md`、`scripts/extract-session-signals.py`、`tests/test_extract_session_signals.py`，后两项相对该 Skill 目录。
- 工作：新增 `pi`/`--pi-home`/默认 home 与 source，保持现有输出兼容；正常和 skill-usage-only 模式都支持 Pi，保持日期与 include-output 约定。独立 scanner 消费消息树、compaction 和 role/stop/model 元数据，剥离注入正文而保留真实请求。候选“继续”关系不能升级为提前停机/完成判断；修正同文件已发现的旧 gate/reviewer 建议。
- 测试：合成 homes 覆盖 current/all scope、多 home、默认与显式 source、JSON/Markdown、缺失/坏行/未知格式、分支与不完整祖先、compaction/retainedTail 去重、fork 限制、模型切换、各 stopReason、注入与真实 user 尾部、skill usage/日期/output 开关、默认无原文与正数 limit 下敏感内容边界。以假秘密标记证明报告不输出 thinking/图片/原始 payload 或受限内容；fixture 不含真实秘密。
- 兼容：现有 Codex/Claude/Grok 用例与 schema 语义保持；只做 Pi 增量和直接相关的过时推荐修正，不重构所有旧 scanner。所有测试显式隔离数据源/homes，不能因 Pi 被加入默认 sources 而扫描操作者历史。
- 完成证据：在测试临时目录通过 CLI 验证预期报告；现有及新增 scanner tests 通过。Python stdlib 和当前 unittest CLI 模式不迁移，源码/测试不依赖真实 Pi、网络、模型或新增第三方包。

### T4 — 汇合审查、稳定真相与分发验收

- 依赖：T1/T2/T3 候选及各自适用证据；跨切片裁决、最终接受归 parent，不是 worker 硬依赖链。
- 写入：上述已列源码的有因果修复；`docs/architecture/skill-composition.md`、`invocation-contract.md`、`maintenance-contract.md`；本设计/计划的当前状态；必要时新增同主题短验证记录。`skills/`、`skills.index.json`、架构 diagrams/generated 仅通过现有生成器写入。
- 工作：检查 workflow、risk/security/test overlays、报告和 miner 建议一致，不新增强制 router/实验/审批结构。对实际候选做有界独立审查，parent 裁决及修复；仅当证据失效或仍有独立问题才定向复审，不固定循环次数。
- 工作：据已验证源码更新稳定真相的目标/裁量/环境职责与维护证据边界，不把 stage 记录升级为运行时契约。生成一次汇合候选并运行 D 的必需检查；修复后按变化重跑相关项，最终候选仍须满足仓库既定验收。
- 完成：39 IDs 与生成一致性成立，无已接受的阻塞缺陷；Pi 结构化行为已验证；提示变更仅宣称源码/场景审查通过，不宣称真实模型效果。最终报告列修改、证据、取舍及未执行的动作。

## D. 实际依赖、验证与恢复

执行关系：`T0 → {T1, T2, T3} → T4`。T1–T3 共享本设计已经确认的语义，而不消费彼此未产出的文件，可在准确写集、host 能力和资源安全时用一个平铺批次；也可本地完成。没有额外模型选择、delegation profile 或容器前置，不能把普通序号变成串行依赖。Parent 统一共享生成物、稳定真相及最终裁决。

本轮只写阶段文档时：独立文档审查、prose、相关相对链接和 `git diff --check` 足够，不因写计划重跑产品/安装/恢复全链路。未来实施的必需验证如下，从仓库根运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s src/skills/disciplines/skill-miner/tests -p 'test_*.py'
python3 scripts/generate-skills-index.py
python3 scripts/flatten-skills.py --target root-flat
python3 scripts/generate-workflow-diagrams.py
bash scripts/check.sh
git diff --check
```

第一条补足根 `pyproject.toml` 的 `testpaths = ["tests"]` 不包含 Skill 内 scanner tests 的边界，不替换根仓库检查。使用仓库既有工具环境和缓存策略，不为本任务安装新的全局工具、增加普遍 lint gate 或清理无关旧代码。已有 `scripts/check.sh` 负责其声明的 lint/types/tests/prose；新增 Python 代码仍遵守现行语言规范。

提示语义通过有界 review 和设计 F 的场景辨析验证，不添加自然语言 snapshot/关键词断言。真实 A/B 需要单独的运行范围和成本许可，不属于 T4 的成功条件，也不把“未测得省时”解释成源码未完成。

默认 fix-forward：保留用户修改和失败证据，修复本范围缺陷。无效 Pi 输入是 scanner 应报告的条件，不是全任务 gate；不支持真实模型实验只限制效果结论。遇到主目标/硬边界冲突、确实超出写入范围或新外部效果才返回具体决定；无新证据且无可行路径时如实报告受影响部分。不得弱化必达 oracle、自动删除用户状态或通过改配置/安装消除失败。

## E. 当前实施证据

T0–T4 已完成，交付终点为当前本地工作树。基线 `024312c`；已跟踪 authored diff 的 SHA256 为 `d0dac6a6fd81fcc9419f2e12fdf14d07ce5dfeb5583770dd7cab90ff1f9796d3`，新增 `goal-and-risk-cases.md` 的 SHA256 前缀为 `1df119fe9772`。状态记录更新不改变设计或验收边界。

- **实现与真相**：工作流/评审/收尾、风险/安全/恢复/测试 overlays、离线正反场景与 Pi miner 已交付；三份稳定架构文档已同步。39 public IDs、角色与权限保持，`contracts/skills.toml` 未改；分发面仅由现有生成器刷新。
- **验证**：独立执行的 scanner CLI suite 为 **15 tests passed**，覆盖原有三种来源及 Pi；root `bash scripts/check.sh` 为 **95 tests passed**，contracts、root-flat、install-surface、index、diagrams、现有 Ruff/type gates、prose 全通过。最终 prose 为 325 个 Markdown、0 hard-wrap。4 个 stdlib 安全片段已通过真实行为检查，Shell 示例通过语法检查；没有为片段创建服务或 CI。
- **修复证据**：同文件 symlink alias 重复计数先出现 `2 != 1`，修复后通过；独立 Pi 审查发现 evidence line 错用分支序号，parent `accepted`，回归先出现 `[1,2] != [2,6]`，修复为物理 JSONL 行号后全部 15 tests 通过。未弱化原有 oracle。
- **审查裁决**：前置 design/plan 均 `pass`。实施语义评估 `pass`；Pi 的唯一候选已修复，定向静态复审未发现残留缺陷。评估器没有执行工具或独立核验 hash；定向复审误用测试相对路径而未读到 fixture，parent 已核对正确文件并执行该回归，因此不把评估器报告当作独立测试证据。
- **委派恢复**：平铺批次完成 T1/T2；T3 超时无导出后，仅重建该切片的保留会话，恢复部分候选并补测试/修复。Parent 导入后补足验证与修复，没有重跑已完成切片、借超时要求新用户批准或接受未验证候选。
- **取舍与结论边界**：Pi 样例采用类别摘要而非任意原文脱敏；v1/v2、不完整分支及无法证明唯一性的跨文件 fork 关系保留限制，不自动判断任务完成/提前停止。未重放真实私有会话、运行 live-model 效果实验或证明中断率改善。未 commit、push、安装、变更用户配置或部署。

## F. 实施批准摘要

- **本轮已覆盖**：用户批准的 T0–T4 本地源码实施、审查、修复、真相同步与分发验收均已完成。
- **已批准实施范围**：实施本计划，覆盖 T0–T4 所列本仓库 authored sources、相关测试/参考资料、稳定真相、生成输出、合成临时 fixtures、必要验证、独立审查和因果修复；交付终点是本地已验证工作树。
- **没有额外人工前置**：无已知账号、密钥、设备或生产材料需求。Pi 支持用合成数据验收，实际 scanner helpers、计数键及段落组织由执行者决定，不逐项审批。
- **连续执行范围**：批准后完成 T0–T4。普通调查、模块内文件细化、已授权技术取舍、绑定/生成物、验证与修复不再索要“继续”；缺少可选 delegation 或真实模型比较不阻断本地交付。
- **再次暂停条件**：主目标或明确边界被证据推翻，必须改变 public IDs/角色/权限/CLI 既有兼容语义，出现无法保留的用户冲突，或需要表外项目/全局/生产操作时，只提出受影响的窄决定。
- **明确排除**：commit、push、merge、历史改写、发布、安装/更新 discovery 链接、用户配置、真实模型实验/数据上传、生产部署与任何外部数据重建/删除。前面对开发风险的原则认可不等于这些动作已属于本任务。
