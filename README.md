# Hermes Code Workflow / Hermes 代码工作流

Hermes Code Workflow is a practical software development workflow for Hermes Agent.

Hermes Code Workflow 是一套面向 Hermes Agent 的实用软件开发工作流。

Its purpose is simple: Hermes plans, coordinates, verifies, and reports; coding workers such as Claude Code, Codex, OpenCode, Gemini command-line interface, and other agent processes do the bounded implementation or review work.

它的目标很简单：Hermes 负责规划、编排、校验和汇报；Claude Code、Codex、OpenCode、Gemini 命令行工具以及其他智能体进程负责执行有边界的实现或审查任务。

## Why this exists / 为什么需要它

Modern coding work often involves more than one assistant or command-line coding tool. Without a workflow, agents can edit too broadly, skip tests, claim success without proof, or lose context between sessions.

现代代码工作经常会同时使用多个助手或命令行编码工具。如果没有固定工作流，智能体容易改动过宽、跳过测试、没有证据就声称完成，或者在不同会话之间丢失上下文。

Hermes Code Workflow makes the process explicit:

Hermes 代码工作流把流程显式化：

1. Understand the request and risk.
2. Brainstorm alternatives when the task is not trivial.
3. Write a plan with acceptance criteria.
4. Dispatch a bounded worker brief.
5. Prefer test-first development for new logic and bug fixes.
6. Review non-trivial changes independently.
7. Verify with real commands and file inspection.
8. Report changed files, checks, risks, and follow-up work.

对应中文流程：

1. 理解需求和风险。
2. 非简单任务先做头脑风暴，比较不同方案。
3. 写出带验收标准的计划。
4. 给执行智能体下发边界清晰的任务说明。
5. 新逻辑和缺陷修复优先采用先写测试的开发方式。
6. 对非简单改动进行独立审查。
7. 用真实命令和文件检查来验证结果。
8. 汇报改动文件、检查结果、风险和后续事项。

## What is included / 仓库内容

- `skills/hcw/SKILL.md`
  - Main Hermes skill definition.
  - Hermes 主技能定义。
- `skills/hcw/references/python-adapters.md`
  - Design notes for Python adapters that connect Hermes with command-line tools, software development kits, and agent processes.
  - Python 适配器设计说明，用于连接 Hermes、命令行工具、软件开发工具包和智能体进程。
- `templates/brief.example.json`
  - Example task brief for dispatching a bounded worker job.
  - 用于派发有边界执行任务的 JSON 示例。
- `scripts/hcw_session.py`
  - Create, inspect, and append events to local workflow session artifacts.
  - 创建、查看并追加本地工作流会话记录。
- `scripts/hcw_verify.py`
  - Run verification commands and emit structured JSON evidence.
  - 运行验证命令并输出结构化证据。
- `scripts/hcw_dispatch.py`
  - Dispatch a bounded task brief to a supported worker command.
  - 将边界清晰的任务说明派发给受支持的执行命令。
- `scripts/hcw_summarize.py`
  - Summarize workflow artifacts into a final report draft.
  - 将工作流记录汇总成最终报告草稿。

## Relationship to reference workflows / 与参考工作流的关系

Hermes Code Workflow learns from three systems but is not a copy of them.

Hermes 代码工作流参考了三套系统，但不是简单复制。

- Claude Code Workflow contributes intent classification, chain selection, wave execution, session artifacts, and command-line orchestration ideas.
- Everything Claude Code contributes harness performance thinking, command and rule layering, verification loops, and cross-agent packaging ideas.
- Superpowers contributes strong workflow discipline: brainstorm, plan, execute, test-first development, systematic debugging, independent review, and verification before completion.

中文说明：

- Claude Code Workflow 提供了意图分类、链路选择、分批执行、会话产物和命令行编排思路。
- Everything Claude Code 提供了执行框架性能、命令与规则分层、验证循环和跨智能体打包思路。
- Superpowers 提供了强纪律流程：头脑风暴、计划、执行、先写测试、系统化调试、独立审查和完成前验证。

## Worker model / 执行者模型

Hermes Code Workflow separates orchestration from execution.

Hermes 代码工作流将“编排”和“执行”分离。

- Hermes Agent
  - Plans the task.
  - Chooses the worker.
  - Writes the task brief.
  - Verifies the result.
  - Reports to the user.

- Hermes Agent 中文职责
  - 制定任务计划。
  - 选择执行者。
  - 编写任务说明。
  - 验证结果。
  - 向用户汇报。

- Claude Code
  - Default implementation worker for coding-heavy tasks.
  - 代码实现任务的默认主力执行者。

- Codex
  - Useful for independent implementation, review, or second opinion.
  - 适合独立实现、审查或提供第二意见。

- OpenCode
  - Useful as a provider-independent coding worker or fallback.
  - 适合作为相对独立的编码执行者或备用执行者。

- Gemini command-line interface
  - Useful for broad analysis, architecture discussion, diagnosis, and Agent Client Protocol style execution when available.
  - 适合宽范围分析、架构讨论、诊断，以及在可用时通过 Agent Client Protocol 风格执行。

## Python adapter layer / Python 适配层

The `scripts/` directory provides small Python utilities that make worker orchestration easier to observe and verify.

`scripts/` 目录提供了一组小型 Python 工具，让执行者编排更容易观察和验证。

Python adapters should:

Python 适配器应该：

- read JSON task briefs;
- run a selected command or verification check;
- capture exit codes, standard output, and standard error;
- write structured JSON events;
- avoid secrets in logs;
- keep dispatch and verification separate.

对应中文：

- 读取 JSON 格式任务说明；
- 运行选定的命令或验证检查；
- 捕获退出码、标准输出和标准错误；
- 写入结构化 JSON 事件；
- 避免在日志中写入密钥；
- 将派发执行和结果验证分开。

## Example session / 示例会话

Create a session:

创建会话：

```bash
python3 scripts/hcw_session.py create --repo . --goal "Improve login error handling"
```

Run verification:

运行验证：

```bash
python3 scripts/hcw_verify.py --session .hcw/sessions/<session-id> --command "npm test" --command "npm run build"
```

Dispatch a worker from a JSON brief:

根据 JSON 任务说明派发执行者：

```bash
python3 scripts/hcw_dispatch.py brief.json
```

Summarize artifacts:

汇总工作流记录：

```bash
python3 scripts/hcw_summarize.py .hcw/sessions/<session-id>
```

## Completion standard / 完成标准

A task is not complete because a worker says it is complete.

任务不会因为某个执行智能体说“完成了”就算完成。

A task is complete only when Hermes has verified the result with evidence.

只有 Hermes 用证据验证结果后，任务才算完成。

The final report should include:

最终报告应该包括：

- files changed;
- commands run;
- command results;
- skipped checks and reasons;
- known risks;
- follow-up recommendations.

对应中文：

- 改动文件；
- 运行过的命令；
- 命令结果；
- 跳过的检查以及原因；
- 已知风险；
- 后续建议。
