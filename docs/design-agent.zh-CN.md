### Design 代理

`scripts/hcw_design.py` 为 HCW 增加结构化架构/设计阶段的自动化支持，
参考 [huashu-design](https://github.com/alchaincyf/huashu-design) 方法：

1. **深度扫描** — 提取代码库中的架构模式、配置精确值、依赖关系
2. **维度化方案** — 每个方案探索不同的架构轴（模块化、数据流、状态管理、容错等）
3. **Junior Designer 模式** — 先展示假设和开放问题再定稿
4. **5 维评审** — 从一致性、模块化、可扩展、可维护、可测试五个维度评分
5. **Quick Wins** — 评审输出按优先级排序的修复清单

```bash
# 1. 初始化 — 创建设计 session
python3 scripts/hcw_design.py init \
  --goal "为 API 网关添加限流功能" \
  --context "当前网关没有限流；高峰期 5000 req/s" \
  --constraints "必须使用 Redis" "延迟增加不超过 5ms" \
  --ask-questions

# 2. 探索 — 深度代码库扫描（提取配置值、架构标记）
python3 scripts/hcw_design.py explore \
  --dir . \
  --session .hcw/sessions/<session-id>

# 3. 提议 — 按不同架构维度生成 2-3 个方案
python3 scripts/hcw_design.py propose \
  --goal "为 API 网关添加限流" \
  --approaches 3 \
  --recommend 1 \
  --session .hcw/sessions/<session-id>

# 4. 假设 — 展示设计假设（Junior Designer 模式）
python3 scripts/hcw_design.py assumptions \
  --session .hcw/sessions/<session-id> \
  --items "scope_impact:只改 gateway/middleware" "performance:目标每请求 <5ms 额外开销" \
  --open-questions "限流超限错误怎么返回？" "窗口大小用什么值？"

# 5. 终稿 — 从所有 artifacts 生成 design.md
python3 scripts/hcw_design.py finalize \
  --session .hcw/sessions/<session-id> \
  --scope "gateway/middleware/ratelimit.py" "gateway/config.yaml" \
  --criteria "python3 -m pytest tests/test_ratelimit.py" "load-test --rps 6000"

# 6. 评审 — 5 维评分 + Quick Wins
python3 scripts/hcw_design.py review \
  --design .hcw/sessions/<session-id>/design.md \
  --scores "architectural_coherence:7" "modularity:8" "scalability:6" "maintainability:7" "testability:8" \
  --fixes "high|缺少错误处理|添加错误中间件" "medium|配置无兜底|添加默认值" \
  --session .hcw/sessions/<session-id>
```

**设计会话产物**：

```text
.hcw/sessions/<session-id>/
├── manifest.json           # 目标、上下文、假设、状态
├── events.jsonl            # 设计事件日志
├── exploration/
│   └── codebase.json       # 深度扫描结果（架构标记、配置值）
├── proposals.json          # 按架构轴划分的方案
├── assumptions.json        # 设计的假设 + 开放问题
├── review.json             # 5 维评分 + quick wins
└── design.md               # 最终设计文档
```

**5 个评审维度**：

| 维度 | 权重 | 评估内容 |
|------|------|---------|
| 架构一致性 | 25% | 架构风格统一，组件边界清晰 |
| 模块化程度 | 20% | 耦合度、内聚性、接口清晰度 |
| 可扩展性 | 20% | 新增功能的难度和影响范围 |
| 可维护性 | 20% | 错误处理、日志、调试难度 |
| 可测试性 | 15% | Mock 难度、依赖隔离程度 |
