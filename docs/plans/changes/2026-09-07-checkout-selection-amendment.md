# 当前 checkout 默认与隔离条件：已批准补充

日期：2026-09-07

状态：用户已接受建议并授权修改、flatten、commit、push。

关联：[原设计](2026-09-07-skill-boundaries-context-design.md)、[原计划](2026-09-07-skill-boundaries-context-plan.md)、[候选验证](2026-09-07-skill-boundaries-context-verification.md)。

## 已批准的调整

- 默认在当前 checkout 实施。只有本任务 design/plan/implementation/evidence dirty，或存在无关且不重叠的修改，都不要求创建 worktree、clone、branch 或先提交。
- 现有修改重叠时，先判断内容和归属；可安全保留就继续，无法安全处理才解决具体冲突。不自动 reset、stash 或隔离来获得 clean status。
- 用户明确要求、适用仓库规则、不同 branch state 的实际需求、已确认并发写冲突或无法原地保护的重叠状态，才支持选择隔离。隔离本身不解决归属和最终整合冲突。
- 并发判断依赖用户说明、可见且指向同一 checkout/write set 的 host 任务证据，或本任务期间意外出现的漂移。判断包含 generated roots、Git index/refs 等共享资源，而非仅比较文件名。
- 进程存在、dirty 或时间戳本身不是冲突证明；不为假设并发扫描整个 workstation 或新增协调系统。开始状态、写前内容、最终 diff 核对只能检测部分竞争，不是互斥锁，也不能证明没有其他 writer。
- 提交本任务文档是有授权时的可选持久化操作，不是实现前提或并发保护。本次用户已明确授权提交和推送全部已验证的本任务变更，不包括无关修改或强制推送。
- 批准修改 repository source 及 generated payload，覆盖既有 symlink 后续读取这些文件的预期变化。仅有链接存在不再制造单独安装批准门槛；修改 discovery links、用户配置、plugin install、外部部署及超出批准范围的真实副作用仍需对应授权。

## 与旧计划的关系

此补充由用户明确批准，不是为通过测试反向修改验收。原计划 D1–D7、V1–V16、39 IDs、权限/数据保护、reviewer 只读和验收完整性要求不变。

原计划 C1 已由 `approve and $implement-change` 满足；其 candidate-only 初始里程碑已完成。原 C2 及依赖它的 T0/T6 隔离、单独整合批准条件由本补充替代，不再作为继续执行的 gate。原 C5 中 commit/push 禁止已由本次具体用户授权解除；publish/deploy、强制推送、全局设置修改等权限不随之扩大。

之前实际使用独立本地 clone，而不是 Git worktree；保留其检查与失败/修复证据，不再创建额外隔离环境或做分支合并。将已审定 candidate authored diff 应用到当前 checkout，再校准上述语义并通过项目生成器生成实际 payload。

## 新增修改边界

在原批准源码及文档范围上，更新：

- `src/skills/workflows/implement-change/SKILL.md`：当前 checkout 与并发判断 owner。
- `src/skills/git/git-worktrees/SKILL.md`：进入隔离操作的条件，保留显式 worktree 请求与操作保护。
- `docs/architecture/skill-composition.md`：稳定的 checkout/concurrency 责任边界。
- `docs/architecture/install-surface.md`：既有 symlink 与 scoped payload 更新的授权关系。
- 本次 design/plan/audit/verification 阶段文档：标记旧隔离结论已被用户新决定取代，记录当前执行证据。
- 以上源码的 generator-owned payload；不改 contracts、public IDs、测试/生成器、用户配置或 host runtime。

## 验证与交付

在当前 checkout 运行 index、root-flat、diagram 生成和 `bash scripts/check.sh`，对新增隔离/授权语义做定向独立审查。现有 worktree command 示例不因本补充变化，可保留原 95 条命令观察和 17 个片段检查的适用证据；不重复构造无变化 fixtures 或新增 prose assertions。

新增场景：task-local dirty、无关 disjoint dirty、可保护/不可保护的 overlap、无依据的并发猜测、已知共享写冲突、明确 worktree 请求、预期 symlink payload 更新与真实外部副作用的区别。检查不得降低用户修改保护、Git authority 或声明不存在实际并发。

提交前核对 staged diff 仅含本任务，分支/remote/upstream 与目标一致；使用正常 commit/push，不自动 rebase、amend、强制推送或覆盖远端新提交。具体执行与验证结果续记于关联 verification 文档。
