# 快速开始

用大约五分钟，把 Hermes Code Workflow 从“看过介绍”变成“亲手跑通一次”。

## 你会完成什么

这份快速开始会带你完成一个最小闭环：

1. 创建 workflow session；
2. 查看有边界的 worker brief；
3. 运行一次 dry-run dispatch；
4. 执行 verification；
5. 生成最终 summary。

跑完之后，你会真正理解 HCW 的核心：**Hermes 负责编排和验证，worker 负责执行，完成标准来自证据而不是口头声明。**

## 前置条件

你需要：

- 已安装 Hermes Agent
- 本仓库已经 clone 到本地
- 系统里可以使用 `python3`

可选但推荐：

- 已将 `hcw` skill 安装到 Hermes
- 后续准备至少一个 coding worker，例如 Claude Code、Codex 或 OpenCode

## 1. 进入仓库

```bash
cd Hermes-Code-Workflow
```

## 2. 创建一个 demo session

这一步会在 `.hcw/sessions/` 下创建一次本地工作流会话。

```bash
python3 scripts/hcw_session.py create \
  --repo . \
  --goal "Learn the Hermes Code Workflow artifact flow" \
  --risk low \
  --tier standard \
  --chain plan-execute
```

预期结果：

- 终端打印出新的 session ID
- `.hcw/sessions/<session-id>/` 目录被创建
- `manifest.json` 和 `events.jsonl` 出现

## 3. 查看示例 worker brief

这份 brief 展示了 Hermes 会如何把一个任务整理成“有边界、可验证”的说明，再交给 worker。

```bash
python3 -m json.tool templates/brief.example.json
```

重点看这些字段：

- `goal`
- `environment_context`
- `relevant_files`
- `constraints`
- `acceptance`

这正是 HCW 的核心纪律之一：**worker 不是拿到一句模糊需求，而是拿到一份范围清晰、约束明确、验收可执行的 brief。**

## 4. 运行一次 dry-run dispatch

这一步不会真的调用 worker，而是先校验 brief 并展示将要生成的 prompt。

```bash
python3 scripts/hcw_dispatch.py templates/brief.example.json --dry-run
```

你应该关注：

- brief 是否校验通过
- tier 是否识别正确
- 是否包含 chain recommendation
- 是否包含 decomposition hints
- 生成的 prompt 是否结构清晰、边界明确

如果 dry run 看起来合理，Hermes 才适合继续派发真实 worker。

## 5. 执行 verification

现在运行一个轻量 verification，把结果记录成结构化证据。

```bash
python3 scripts/hcw_verify.py \
  --repo . \
  --command "python3 -m py_compile scripts/*.py" \
  --label quickstart-verify
```

预期结果：

- 退出码为 `0`
- 输出结构化 JSON
- 记录 stdout/stderr tail

这一步体现的是 HCW 的另一个核心：**完成不是因为 worker 说 done，而是因为 verification 给出了证据。**

## 6. 生成 summary report

把第 2 步创建的 session 目录路径替换进去，然后汇总本次会话。

```bash
python3 scripts/hcw_summarize.py .hcw/sessions/<session-id>
```

预期结果：

- 输出一份 Markdown final report
- 如果已有 dispatch / verification / review 事件，会分段汇总
- 生成的内容可以被 Hermes 直接拿去整理成对用户的最终汇报

## 7. 查看仓库自带的完整示例

如果你想看一套已经准备好的端到端示例，请继续读：

- `docs/demo-session/README.md`
- `docs/demo-session/final-report.md`

这些文件展示的是“dispatch 和 verification 已经发生之后”的真实产物长什么样。

## 到这里你已经证明了什么

在几分钟里，你已经验证 HCW 至少能做到：

- 创建 session artifacts
- 用 bounded brief 表达工作
- 在执行前校验 dispatch 结构
- 用结构化 evidence 记录 verification
- 从 artifacts 生成最终 report

这就是 HCW 的最小闭环。

## 下一步读什么

根据你的目标继续：

- 想看完整操作闭环：读 `docs/full-demo.zh-CN.md`
- 想看适用场景：读 `docs/real-world-use-cases.zh-CN.md`
- 想直接安装 skill 到 Hermes：看 `README.zh-CN.md` 里的安装部分

## 新手最常见的三个错误

### 过早调用真实 worker

先跑 `--dry-run`，确认 brief 范围合理、acceptance checks 有意义，再交给真实 worker。

### 把 verification 当成可选项

不要跳过 verification。HCW 的价值，很大一部分正来自“用证据验证结果”。

### goal 写得太空

好的 goal 应该是具体、可测试、可观察的。goal 如果模糊，worker 的输出大概率也会模糊。

## 五分钟成功标准

满足下面三点，就算跑通了 quick start：

- `.hcw/sessions/` 下出现 session 目录
- `hcw_verify.py` 成功返回
- `hcw_summarize.py` 生成 summary
