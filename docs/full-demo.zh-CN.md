# 完整 Demo

这份文档展示 Hermes Code Workflow 的完整闭环：从操作意图，到 worker handoff，再到 verification 和最终报告。

它的定位，正好在两者之间：

- 比 `docs/quick-start.zh-CN.md` 更完整
- 比 `docs/demo-session/` 下的产物说明更容易上手

## 这份 Demo 回答什么问题

如果一个新用户会问：

- Hermes 实际上做了什么？
- worker 在哪个环节接入？
- verification 到底怎么参与？
- 会留下哪些 artifacts？
- 最终报告是怎么生成的？

这份文档就是答案。

## 先看整个流程

HCW 的完整流程可以概括成 9 步：

1. Hermes 收到编码任务；
2. Hermes 判断风险和适合的 chain；
3. **（可选）Hermes 运行设计阶段** — 代码库探索、设计方案提出、架构审查，产出 `design.md`；
4. Hermes 创建 session；
5. Hermes 准备 bounded worker brief；
6. Hermes 派发 worker；
7. Hermes 运行 verification；
8. Hermes 汇总 artifacts；
9. Hermes 输出带证据的最终报告。

## 场景设定

我们用一个足够真实、又不会太复杂的例子：

> 改进一个小型 Python 服务的登录报错处理。

这个例子的目的不是模拟大型生产事故，而是把整个工作流的形状讲清楚。

## Phase 1：创建 session 状态

Hermes 做的第一件事，不是立刻让 worker 开干，而是先创建一份可追踪的 session。

```bash
python3 scripts/hcw_session.py create \
  --repo . \
  --goal "Improve login error handling" \
  --risk medium \
  --tier standard \
  --chain plan-execute
```

这一步会：

- 创建 `.hcw/sessions/<session-id>/`
- 写入 `manifest.json`
- 准备好 `events.jsonl` 用于记录后续事件

为什么重要：

- 这次工作开始有了 artifact trail
- verification 可以明确归属于某个 session
- 最终报告可以从 artifacts 生成，而不是靠记忆回忆

## Phase 2：准备 worker brief

Hermes 不应该对 worker 说一句模糊的话：

> 帮我把登录错误处理修一下

而应该把任务整理成一个有边界的 brief，例如 `templates/brief.example.json`。

查看它：

```bash
python3 -m json.tool templates/brief.example.json
```

一份强的 brief 至少包含：

- 一个可测试的 goal
- environment context
- relevant files
- constraints
- 明确的 acceptance checks

这是 HCW 从“像流程”变成“真能执行”的关键一步。

## Phase 3：在执行前校验 dispatch

在真的调用 worker 之前，先验证 brief 合不合格、prompt 是否合理。

```bash
python3 scripts/hcw_dispatch.py templates/brief.example.json --dry-run
```

这一步会证明：

- brief schema 是有效的
- tier 识别合理
- prompt 结构可用
- chain recommendation 逻辑正常工作
- decomposition hints 可供 Hermes 路由决策参考

输出里重点看这些内容：

- `chain_recommendation`
- `decomposition_hints`
- Goal / Constraints / Acceptance Checks / Required Output 等 section

## Phase 4：派发真实 worker

在真实使用中，Hermes 接下来会把任务交给 Claude Code、Codex、OpenCode 或其他 worker。

这个 handoff 的核心关系是：

- Hermes 仍然是 planner 和 verifier
- worker 负责执行有边界的实现、分析或审查
- worker 返回原始输出
- Hermes 不会因为 worker 说“做完了”就直接宣布完成

最后这一点非常关键：

**worker completion ≠ task completion**

HCW 里真正的完成，必须经过 verification。

## Phase 5：运行 verification

现在 Hermes 开始用真实命令验证结果。

轻量 verification 例子：

```bash
python3 scripts/hcw_verify.py \
  --repo . \
  --command "python3 -m py_compile scripts/*.py" \
  --label demo-verify
```

更深一点的 verification 例子：

```bash
python3 scripts/hcw_verify.py \
  --repo . \
  --command "python3 -m py_compile scripts/*.py" \
  --level deep \
  --label deep-demo \
  --expect "stdout:"
```

verification 能记录什么：

- command exit status
- stdout / stderr tail
- secret scan 结果
- diff-scope 合规性
- 通过 `--expect` 做输出模式断言

这一步为什么重要：

- 它把“看起来像没问题”变成“有证据表明通过”
- 它让失败可回看、可定位
- 它给 Hermes 提供了能真正对外汇报的依据

## Phase 6：汇总 artifacts

当 dispatch 和 verification 产物都存在以后，就可以生成 final report。

```bash
python3 scripts/hcw_summarize.py .hcw/sessions/<session-id>
```

这份 summary 来自这些 artifacts：

- `manifest.json`
- `events.jsonl`
- verification outputs
- worker 相关事件记录

这意味着最终报告：

- 可复现
- 可审计
- 不依赖 Hermes “记得自己做过什么”

## Phase 7：查看仓库自带的示例产物

仓库里已经有一套现成示例，在 `docs/demo-session/`。

建议从这里开始看：

- `docs/demo-session/README.md`
- `docs/demo-session/final-report.md`

这两份文件能让你看到真实 session 结束后，产物大概长什么样：

- session metadata
- dispatch events
- verification evidence
- Hermes 可对外输出的 report draft

## 完整 Demo 最终证明了什么

走完这份 Demo 后，用户应该能清楚理解：

HCW 不是“多接了几个 coding agent 的 Hermes”。

它是一套角色清晰、证据导向的闭环：

### Hermes

- 理解任务
- 选择 chain
- 写 brief
- 触发 verification
- 汇总 evidence
- 输出结果

### Worker

- 执行有边界的实现、分析、review 或 testing
- 尽量保持在 brief 限定范围内
- 返回供 Hermes 检查的原始输出

### Verification

- 判断工作是否真的通过检查
- 阻止“未验证就宣称完成”
- 生成结构化 evidence

## 一个典型 session 的产物路径

通常你会看到这样的 artifact trail：

```text
.hcw/sessions/<session-id>/
├── manifest.json
├── events.jsonl
└── verification.json
```

而从流程角度看，它对应的是：

```text
worker brief -> worker output -> verification evidence -> final report
```

## 什么时候最适合用这份文档

这份完整 Demo 特别适合：

- 向队友介绍 HCW
- 说明为什么 Hermes 是 orchestrator，而不是单纯 coder
- 解释 verification 为什么是硬步骤
- 证明这套流程是可复现、可展示的

如果你只是想快速跑通第一遍，优先看 `docs/quick-start.zh-CN.md`。

如果你想判断 HCW 是否适合自己的工作，优先看 `docs/real-world-use-cases.zh-CN.md`。

## 推荐阅读顺序

1. `README.zh-CN.md`
2. `docs/quick-start.zh-CN.md`
3. `docs/full-demo.zh-CN.md`
4. `docs/real-world-use-cases.zh-CN.md`
5. `docs/demo-session/README.md`

这是从“感兴趣”到“有信心使用”的最短路径。
