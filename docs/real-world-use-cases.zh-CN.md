# 真实案例

Hermes Code Workflow 最适合那些既想利用 coding agent 的速度，又不想放弃边界、验证和最终可汇报性的场景。

这份文档不是讲“它理论上能做什么”，而是讲“它在真实工作里适合怎么用”。

## 1. 修 bug，但要有证据

### 场景

用户报了一个 bug，问题本身不大，但你又不想让 worker 为了修这个点顺手改动太多无关代码。

### HCW 怎么帮你

Hermes 可以：

- 创建 session
- 写出范围清晰的 brief
- 限定 relevant files
- 指定可执行的 acceptance checks
- 在汇报成功之前先做 verification

### 为什么比随手用 agent 更好

如果没有 HCW，worker 可能会：

- 改到无关文件
- 不先复现问题
- 没有证据就说修好了

有了 HCW，修复过程就有范围，也有验证。

### 典型例子

- 修登录错误提示
- 验收：`pytest tests/test_auth.py -v` 返回 0
- diff scope：只允许 auth 模块及对应测试改动

## 2. 做小功能开发，但不想失控

### 场景

你想加一个范围明确的小功能，但又不希望执行过程一路膨胀成“大改造”。

### HCW 怎么帮你

Hermes 可以：

- 选择 plan-execute 或 test-first chain
- 给 worker 下发 standard brief
- 要求明确 acceptance checks
- 在实现后自动进入 verification

### 适合的功能类型

- 增加一个 settings toggle
- 增加一个 API 字段
- 增加一个 dashboard widget
- 增加一个 CLI flag

### 价值

功能保持小、边界可查、后续 review 也更容易。

## 3. 让实现和 review 分离

### 场景

代码已经写完了，但你希望再来一轮独立 review，而不是“自己改、自己说没问题”。

### HCW 怎么帮你

Hermes 可以把 worker 以 review mode 派发出去，并把 review 结果和原始实现放在同一 session artifact 轨道里。

这特别适合：

- 先做 spec compliance review
- 再做 code quality review
- 保留完整的 review artifact trail

### 适合的工作

- merge 前的高风险 patch 复查
- 让另一个 worker 提供第二意见
- 把“实现”和“评价”拆成两个角色

## 4. 做 pre-merge verification gate

### 场景

worker 说“已经完成了”，但你希望 merge 前有更硬的证据。

### HCW 怎么帮你

HCW 会把 verification 提升成独立 phase。

Hermes 可以运行：

- 测试命令
- build 命令
- lint 命令
- diff-scope 检查
- secret scan
- 输出模式断言

### 为什么这很重要

这一步正是 HCW 从“流程感很强”变成“真的有工程价值”的地方。

因为它提供的是一个真正的 gate，而不是一个形式化的结尾。

## 5. 多 worker 协作或对比

### 场景

你希望一个 worker 实现，另一个 worker 复核；或者你想比较两个方案谁更合理。

### HCW 怎么帮你

Hermes 负责稳定编排，worker 则保持可替换。

典型模式：

- worker A 负责实现
- worker B 负责 review
- Hermes 负责 final verification
- Hermes 汇总证据和取舍

### 特别适合

- 架构敏感变更
- 迁移类任务
- 棘手 bug
- 需要第二意见的实现任务

## 6. 调试失败时保留历史轨迹

### 场景

一次修复没成功，你想回头看前面到底试过什么，而不是从零重新猜。

### HCW 怎么帮你

因为 session artifacts 会被保留下来，Hermes 可以回看：

- 之前尝试过什么
- 跑过哪些命令
- 哪一步 verification 没过
- review 给了什么反馈

### 价值

这样你得到的是一条调试轨迹，而不是一堆零散记忆。

## 7. 向别人展示 agent workflow

### 场景

你需要向队友、客户、评估者说明：你的 agent workflow 到底是怎么工作的。

### HCW 怎么帮你

HCW 很适合 demo，因为它天然会留下 artifacts。

你可以直接展示：

- brief
- dispatch 逻辑
- verification evidence
- final report

这比一句“agent 已经处理好了”有说服力得多。

## 8. 更安全地采用 coding agents

### 场景

你想利用 coding agents 提速，但又不想给它们无限自由发挥空间。

### HCW 怎么帮你

HCW 补上的就是那层 guardrails：

- bounded briefs
- explicit constraints
- acceptance checks
- post-execution verification
- structured summaries

### 本质价值

很多时候，这恰恰就是采用 HCW 最核心的理由。

它不是替代 coding agents，而是让它们更容易被信任。

## 什么情况下 HCW 可能太重了

HCW 不是每个任务都必须上。

这些场景里，它可能有点过度：

- 只是一个一行改动
- 没有 worker handoff
- verification 极其直接
- 你不需要 artifact trail

这时一个 direct quick chain 往往就够了。

## 快速判断：你该不该用 HCW

如果你需要下面任意几项，HCW 通常就是合适的：

- 有边界的 delegation
- 可复现的 verification
- 实现与 review 分离
- 基于 artifacts 的最终汇报
- 更安全的 multi-agent coordination

如果这些正是你的需求，那 HCW 很可能就是对的。

## 建议下一步怎么读

- 新用户先看：`docs/quick-start.zh-CN.md`
- 想理解完整工作流：`docs/full-demo.zh-CN.md`
- 想直接看底层产物：`docs/demo-session/README.md`
