# R1 实施验证记录

日期：2026-09-07。基线：`55fc1a56454679b3f83ea3d2f812fb256bf4f62f`。

范围：[批准设计](2026-09-07-orchestrated-delivery-r1-design.md) 与 [实施计划](2026-09-07-orchestrated-delivery-r1-plan.md) T0–T8。用户以 `approve and $implement-change` 授权本仓库实现；未授权提交、推送、部署、配置、安装或 sibling host 开发。

状态：`pass`（本仓库批准的语义与分发里程碑）。源码/生成、维护检查、逐项语义验收和独立评审均完成，parent 最终裁决通过，无未决 accepted finding。本文是阶段证据，不是新的契约、runtime ledger 或对真实行为效果的证明。

## 实施与候选身份

T1/T2/T4/T5 在一个 flat batch 中交给四个互不重叠的 source workers，run `06cb9c4f-0846-4022-b8dc-12b7621f4966`，报告四项成功、导出 12 个路径。Parent 核对实际变更而非直接接受状态；workers 明确未运行 shell 检查。工具返回与静态报告仅支持本次源码劳动已发生，不支持完整开发循环、跨调用续接、费用或 wall-time 改善。

T3/T6 由 parent 实施。汇合时 parent 删除重复入口说明，修正 T2 把“无 parent 决策”混成“无事实依赖”的措辞及强制 host 隔离误读，限定 migration evidence 为代表性既存状态而非暗示操作 live data。T7 同步已成立的共享语义；T8 仅通过生成器更新 root-flat。

评审候选 C1 由基线、tracked diff 和三个新增 authored references 标识；generated 新 reference 与源码一致由 flatten check 证明，无需先 commit：

- `git diff HEAD -- AGENTS.md src/skills tests/test_session_interaction_contracts.py skills skills.index.json docs/architecture` 的 SHA-256：`c7ab02384939198a02df7ebd6a3a5084da9f19fdb8cb8851691baafb863ce536`。
- `src/skills/workflows/design-change/references/goal-alignment.md`：`d307b8228dea22807624503cc9ba3df8cd92015c02c059ec685942e3df9246a5`。
- `src/skills/workflows/plan-change/references/delivery-and-delegation.md`：`aec3fcb4a6de7f3432810fb1624e61995283d12a683f4ce557b39e690834de63`。
- `src/skills/workflows/implement-change/references/delegated-execution.md`：`979056148243476f229b3724298e60ebc7f1c6ac12f64509c23cfd33bab888a0`。

身份不包括本设计/计划/验证记录的进度更新；任何源码修复必须记录新候选和受影响证据。

最终候选 C2：补充 `ruff format --check` 发现 T6 的 `next` 生成表达式应合并为一行，parent 仅修复此格式；没有断言或语义变化。以相同 tracked-diff 命令得到 SHA-256 `3dd5efb2d92865760301561291b44b0f2a28b8b187579e78e4f95f13823a4d44`，三个新增 references 哈希不变。随后重跑四项仓库生成/检查命令、T6 format/type 检查、diff 检查和三个 reference 的源码/生成物逐字比较均通过。

## 已执行检查

| 检查 | 结果与证据界限 |
| --- | --- |
| 修改后 T6 focused pytest | 3 passed；在生成前证明保留结构检查可在原分发基线上通过，不是新 prose 行为证明。 |
| T6 `ruff check` / `ruff format --check` / `ty check` | 均通过；format 初次失败后仅修复单行排版，C2 重验；使用仓库 uv 环境和 repo-external cache。 |
| `python3 scripts/generate-skills-index.py` | 成功；index 无实际 diff。 |
| `python3 scripts/flatten-skills.py --target root-flat` | 成功；仅投影获准源码变更及三个新 reference。 |
| `python3 scripts/generate-workflow-diagrams.py` | 成功；diagrams 无实际 diff。 |
| `bash scripts/check.sh` | contracts、root-flat parity、install surface、index、diagrams、ruff、ty、95 tests、Markdown 全通过；涵盖最终生成后的 T6 三项检查。 |
| Markdown/prose 与 `git diff --check` | 通过；无自然段 hard-wrap。 |

没有修改 contracts、profiles、routing、插件或安装链接；39 public IDs、角色与权限、语义依赖保持原值。没有建立新 worktree/clone，没有 Git index/ref 操作。已有安装 symlink 后续读取生成内容的预期变化属于本次授权源码/分发更新，不等于已验证所有现存 child 都加载了新内容。

## T6 逐类裁决与覆盖归属

原文件有六项测试，最终保留/重组为三项；总套件从 98 降到 95，不为计数补测试。

| 原断言 | 裁决 | 现有覆盖 / 替代证据 |
| --- | --- | --- |
| `Ask one decision-changing question…` 缺席、Frontier 标题与 field 关键词 | 删除 prose snapshots | 设计显式 stress-test 场景审查；不再用词语代表语义。 |
| prerequisites/whole frontier/recompute/completion 文本位置、Q 正则、总结短语 | 删除语义顺序/措辞快照 | Parent 对原 frontier、稳定 Q 与显式触发逐项核对，独立评审承接；不新增自然语言模型测试。 |
| SKILL 内精确 reference 路径 | 保留稳定路径标识检查 | `test_session_skill_references_the_phase_boundary_document`；这不是固定自然语言。 |
| PB reference 文件存在 | 保留，合并 stress-test 文件存在检查 | `test_installed_session_references_exist`。 |
| PB1–PB5 标题/顺序列表、Entry/Compact 等标题与短语 | 删除 prose snapshots | Parent 核对既有分支顺序未变；参考闭包/投影由 `check-contracts.py` 与 flatten check 保护。 |
| `/compact`/`/clear`/token 阈值缺席、许可短语存在 | 删除自然语言或示例词汇含义冻结 | review 确认无宿主命令、阈值或权限增量；不把缩小关键词集合当修复。 |
| routing case `session-boundary-handoff` 的 owner | 保留 TOML 结构断言 | `test_existing_session_boundary_trigger_owner_is_unchanged`，以及既有 routing/semantic suite。 |

删除依据是已批准 T6 和既有 testing-strategy 的 docs oracle 规则，不是测试失败或改验收求通过；没有业务可执行 oracle 被删除。

## 设计 §12 的逐项语义验收

下表全部为 **S：源码语义检查**，不是 **B：真实 agent 行为实验**。位置为 authored owner；维护检查只证明结构和投影。所有对应真实行为效果仍未验证，不把 S 等同 B。

| 场景（沿用设计顺序） | 实际落点与反例边界 | 证据 |
| --- | --- | --- |
| 明确局部执行请求 | design/implement 的入口排除；plan 普通 readiness 不要求 dispatch metadata | S：不经访谈/design/plan/oracle 门槛。 |
| 一个影响验收的歧义 | design 的 goal-alignment reference | S：最小决定、有依据推荐、足以推进即停。 |
| 普通技术选择 | goal-alignment 与 delivery-and-delegation | S：交给范围内 executor，不因换模型重问用户。 |
| 实现交付且已有有效许可 | plan/implement/close authority 条款 | S：消费匹配任务、目标、副作用的许可；完整 push 历史与 CI/CD 不遗漏。 |
| 只 design 但有常设部署许可 | goal/delivery references 与 close | S：任务/授权/能力独立，不实施部署。 |
| 未商业化但有不可重建数据 | oracle/testing state evidence | S：阶段标签不能降低数据保护。 |
| 普通逻辑不影响恢复 | oracle/testing state evidence | S：不附加恢复仪式，仍遵守适用项目要求和必要行为检查。 |
| 两个独立内聚切片需多轮反馈 | plan 与 delegated-execution | S：优先有价值并行，worker 包含局部循环；本次四个源码 worker 不构成 shell-loop 实验。 |
| 一个有价值 slice | delivery-and-delegation 与 delegated-execution | S：singleton 受实际 host 政策限制，不凑数。 |
| 实现前调查局部调用方 | 同上 | S：worker 自行调查，explorer 非必经前置。 |
| host 无所需能力 | implement 与 delegated-execution | S：如实适配/本地执行/报告缺口，不假装有 shell 或续接。 |
| 准确 write set 范围内协调 | planning two-stage 与 dispatch brief | S：parent 可细化批准模块范围，child 不扩写；已准确批准集合保持不变。 |
| 无启动参数错误或工具拒绝 | delegated-execution Invocation Recovery | S：区分 admission、安全、环境、报告、导出和业务失败；原权限内修正，不自动 takeover。 |
| 最终候选有可靠局部证据 | implement step 7 与 delegated-execution | S：候选关联、有效部分复用、补组合验证；丢弃临时源码后绿灯失效。 |
| reviewer 建议放宽验收 | implement Acceptance Integrity 与 repair/review | S：parent 裁决，oracle 不反向改写。 |
| parent compaction | session/memory 与 delegated-execution | S：先核对实际结果/执行者/批准，不重复派发或全量重载。 |
| 多次修复仍有有效诊断 | repair-loop | S：无默认次数上限；保留真实预算/权限/能力/无路径停止。 |
| 目标与证据全部满足 | implement step 12、repair、evaluation | S：结束，不为调用数/复用率/额外 review 继续。 |

Migration 的补充反例由 oracle/testing 明确保护：空库初始化不等于代表性既存状态升级；修改 backup/restore 时恢复本身是产品行为，必须对应验证，不授权操作 live data。

## 设计 §15.9 的逐项续接验收

| 场景 | 实际落点与反例边界 | 证据 |
| --- | --- | --- |
| Worker 返回后打回范围内问题 | delegated-execution Same-Task Continuation、repair-loop | S：优先有效原 worker，增量 brief，保留原基线；B 未验证。 |
| Reviewer 复审修复版本 | review-change Reviewer Continuity、review-implementation | S：原 findings/裁决与真实新候选并存，检查相关回归，不从零全面审计；B 未验证。 |
| 正常澄清往返 | delegated-execution | S：parent 回答后原任务续接，协调缺口非自动人类审批/永久失败；B 未验证。 |
| Parent 压缩后继续 | session/memory、delegated-execution | S：核实 executor 与待裁决状态，无重复创建/执行/导出；B 未验证。 |
| 状态漂移/会话不可恢复 | delegated-execution、memory | S：协调基线后安全续接或明确重建，不凭旧 transcript 覆盖源码；B 未验证。 |
| 新独立审查有实质需要 | review-change | S：覆盖/判断问题、重要边界变化或显式请求允许 fresh review；不得改名 worker 制造独立性；B 未验证。 |
| Host 暂不支持续接 | delegated-execution 与 session | S：准确报告，获准本地/重建可继续；不宣布跨仓库运行能力完成。当前 batch 工具没有 continuation 参数。 |

## 独立评审与 parent 裁决

Run `b3520cd8-0158-4a0f-989a-31d0dfb43531` 的两个只读 reviewer 均返回 `pass`、无候选 findings、无文件修改：

- execution slice：T2/T3/T4/T7 的准确变更与新增 references；核对两次具体化、完整局部劳动/parent 决策、续接/证据/漂移、只读角色与 no-runtime 边界。
- goal/oracle slice：T1/T5/T6；核对最小目标校准、显式 frontier 与 Q IDs、完整交付授权/状态敏感证据，以及删除 prose snapshots 后保留的结构 oracle。

Parent 接受两项有界评审结论并结合实际 diff、三个新增 reference、生成一致性和独立执行检查完成裁决。无接受后待修复项，不需为换 reviewer 重跑全面审查。评审未独立运行命令或重算哈希，采用 parent 提供的 C1 证据；不能证明未运行的 host 能力或成本效果。评审后的 C2 仅作上文记录的 Python 排版修复与阶段进度更新，C1 的语义评审证据仍适用。Parent 核对无断言或行为变更并重跑检查；不以纯格式变化触发新的全面审查。

## 剩余限制

- 本轮未实现或验证 child bash、private reviewer commands、跨调用 native-session/workspace 延续、后台 steering 或 compaction 因果效果。
- 无对照实验或完整费用账目；四个 worker 并发的事实不推出成本更低、交付更快或全部模型已遵循新语义。
- 除本次实际源码委派外，场景表为静态语义证据；安装链接存在/分发一致不证明当前所有主/子会话实际加载版本。
