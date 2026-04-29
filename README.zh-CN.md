# Hermes 代码工作流

语言：[English](README.md) | 中文

Hermes 代码工作流是一套面向 Hermes Agent 的实用软件开发工作流。

它的目标很简单：Hermes 负责规划、编排、校验和汇报；Claude Code、Codex、OpenCode、Gemini 以及其他智能体进程负责执行有边界的实现、分析、测试或审查任务。

## 为什么需要它

现代代码工作经常会同时使用多个助手或命令行编码工具。如果没有固定工作流，智能体容易改动过宽、跳过测试、没有证据就声称完成，或者在不同会话之间丢失上下文。

Hermes 代码工作流把流程显式化：

1. 理解需求和风险。
2. 非简单任务先做头脑风暴，比较不同方案。
3. 写出带验收标准的计划。
4. 给执行智能体下发边界清晰的任务说明。
5. 新逻辑和缺陷修复优先采用先写测试的开发方式。
6. 对非简单改动进行独立审查。
7. 用真实命令和文件检查来验证结果。
8. 汇报改动文件、检查结果、风险和后续事项。

## 安装

Hermes 代码工作流分为一个必需层和一个推荐增强层。

### 安装到 Hermes Agent

先把这个技能安装到 Hermes 里，这样 Hermes 自己就能直接使用这套工作流。

#### 方式 1：通过托管的 SKILL.md 链接安装

```bash
hermes skills install https://<your-host-or-raw-url>/hcw/SKILL.md
```

#### 方式 2：通过本地仓库安装

Hermes `skills install` 目前接受技能标识符或 HTTP(S) 链接，不直接接受本地文件路径。对于本地仓库，请把技能文件复制到 Hermes 的本地技能目录：

```bash
mkdir -p ~/.hermes/skills/software-development/hcw
cp skills/hcw/SKILL.md ~/.hermes/skills/software-development/hcw/SKILL.md
```

然后验证技能已经可用：

```bash
hermes skills list | grep -i hcw
```

这样就足够从 Hermes 侧使用完整流程：Hermes 可以头脑风暴、规划、派发执行者、运行 Python 适配器、验证证据并汇报结果。

### Claude Code 里的推荐增强层

为了获得最佳效果，建议同时在 Claude Code 环境里安装这三个 Claude Code 生态工作流：

- Claude Code Workflow
- Everything Claude Code
- Superpowers

它们不是 Hermes 代码工作流的硬依赖。推荐安装它们，是因为当 Hermes 把编码任务交给 Claude Code 时，Claude Code 自己会更理解链式执行、命令与规则分层、先写测试的纪律、审查门禁和完成前验证。

实际建议：

1. 在 Hermes Agent 里安装 Hermes 代码工作流。
2. 在 Claude Code 里安装 Claude Code Workflow、Everything Claude Code 和 Superpowers。
3. 让 Hermes 继续负责规划、路由、验证和汇报。
4. 让 Claude Code 以及其他执行者负责有边界的编码或审查任务。

## 仓库内容

- `.github/workflows/skill-review.yml`
  - 用于审查 `SKILL.md` 变更的拉取请求工作流。
- `README.md`
  - 英文项目介绍。
- `README.zh-CN.md`
  - 中文项目介绍。
- `skills/hcw/SKILL.md`
  - Hermes 主技能定义，包含链路选择指导、头脑风暴与修复循环守卫、简报分级、审查模板以及实用编排启发式规则。
- `skills/hcw/references/python-adapters.md`
  - Python 适配器参考文档，整理了派发、验证、会话和汇总脚本与当前工作流之间的对齐约定。
- `templates/brief.example.json`
  - 有边界执行任务的示例简报，包含 `tier`、环境上下文、约束和验收检查。
- `scripts/hcw_session.py`
  - 创建、查看并追加本地工作流会话记录。
- `scripts/hcw_verify.py`
  - 运行验证命令、diff 范围检查与密钥扫描，并输出结构化证据。支持验证级别（shallow、standard、deep）和期望模式匹配，可对命令输出做模式断言。
- `scripts/hcw_dispatch.py`
  - 校验 mini 或 standard 简报、构建执行提示词，并将任务派发给受支持的执行者命令。可输出链路推荐评分和轻量分解提示，帮助 Hermes 在派发前做出路由决策。
- `scripts/hcw_summarize.py`
  - 将工作流记录汇总成最终报告草稿。

## 工作流启发式与约束

现在这套工作流已经包含一组更实用的决策规则，帮助 Hermes 更稳定地执行：

- **链路选择指导**
  - 既有决策辅助表，也有加权启发式，帮助在 quick、plan-execute、test-first development、multi-worker、subagent-driven、debug 和 ship 链之间选择。
- **头脑风暴守卫**
  - 明确了 skip criteria、done criteria 和 termination guard，避免头脑风暴无限拉长却没有结论。
- **修复循环守卫**
  - 限制聚焦修复轮次，单独追踪回归问题，并在连续无进展时主动停止重复尝试。
- **简报分级**
  - Hermes 可以根据范围、风险和审查需求，在 `mini` 与 `standard` 简报之间切换。
- **审查与验证纪律**
  - 先做规格符合性审查，再做代码质量审查；同时用 claim-to-evidence 映射把验证动作具体化。
- **递归分解与深度限制**
  - 大任务可以拆成可独立验证的子任务，同时根据风险限制编排深度，避免工作流无限嵌套。

## 脚本化工作流支持

仓库中的脚本会尽量与 `SKILL.md` 里的规则保持一致：

- `hcw_dispatch.py`
  - 校验简报结构，在需要时自动判断 mini 还是 standard，并生成与当前 dispatch template 一致的提示词。同时计算加权链路选择评分和轻量分解提示，让 Hermes 在派发前做出路由决策。
- `hcw_verify.py`
  - 记录结构化验证事件，支持命令式证据、可选的 diff 范围校验，以及 diff 密钥扫描。验证级别（shallow、standard、deep）控制输出详细程度，期望模式匹配可对命令输出做模式断言。
- `hcw_session.py`
  - 维护 `.hcw/sessions/...` 下的会话产物，包括计划、验证输出和事件历史。
- `hcw_summarize.py`
  - 将已有产物整理成简洁的最终报告草稿，供 Hermes 在对外汇报前复核。

## 与参考工作流的关系

Hermes 代码工作流参考了三套系统，但不是简单复制。

- Claude Code Workflow 提供了意图分类、链路选择、分批执行、会话产物和命令行编排思路。
- Everything Claude Code 提供了执行框架性能、命令与规则分层、验证循环和跨智能体打包思路。
- Superpowers 提供了强纪律流程：头脑风暴、计划、执行、先写测试、系统化调试、独立审查和完成前验证。

## 执行者模型

Hermes 代码工作流将“编排”和“执行”分离。

- Hermes Agent
  - 制定任务计划。
  - 选择执行者。
  - 编写任务说明。
  - 验证结果。
  - 向用户汇报。

- Claude Code
  - 代码实现任务的默认主力执行者。

- Codex
  - 适合独立实现、审查或提供第二意见。

- OpenCode
  - 适合作为相对独立的编码执行者或备用执行者。

- Gemini 命令行工具
  - 适合宽范围分析、架构讨论、诊断，以及在可用时通过 Agent Client Protocol 风格执行。

## Python 适配层

`scripts/` 目录提供了一组小型 Python 工具，让执行者编排更容易观察和验证。

Python 适配器应该：

- 读取任务说明；
- 运行选定的命令或验证检查；
- 捕获退出码、标准输出和标准错误；
- 写入结构化事件记录；
- 避免在日志中写入密钥；
- 将派发执行和结果验证分开。

## 示例会话

创建会话：

```bash
python3 scripts/hcw_session.py create --repo . --goal "Improve login error handling"
```

运行验证：

```bash
python3 scripts/hcw_verify.py --session .hcw/sessions/<session-id> --command "npm test" --command "npm run build"
```

根据任务说明派发执行者：

```bash
python3 scripts/hcw_dispatch.py templates/brief.example.json
```

汇总工作流记录：

```bash
python3 scripts/hcw_summarize.py .hcw/sessions/<session-id>
```

可以查看 `docs/demo-session/` 目录，其中放了一套完整的端到端示例产物，包括示例会话、执行简报、验证证据和最终报告。

## 完成标准

任务不会因为某个执行智能体说“完成了”就算完成。

只有 Hermes 用证据验证结果后，任务才算完成。

最终报告应该包括：

- 改动文件；
- 运行过的命令；
- 命令结果；
- 跳过的检查以及原因；
- 已知风险；
- 后续建议。
