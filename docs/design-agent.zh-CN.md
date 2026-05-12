### Design 代理

`scripts/hcw_design.py` 为 HCW 增加结构化架构/设计阶段的自动化支持。

```bash
# 1. 初始化 — 创建设计 session
python3 scripts/hcw_design.py init \
  --goal "为 API 网关添加限流功能" \
  --context "当前网关没有限流" \
  --constraints "必须使用 Redis" "不能增加延迟"

# 2. 探索 — 扫描代码库获取设计上下文
python3 scripts/hcw_design.py explore \
  --dir . \
  --session .hcw/sessions/<session-id>

# 3. 提议 — 生成设计方案草稿（2-3 个方案）
python3 scripts/hcw_design.py propose \
  --goal "添加限流功能" \
  --approaches 2 \
  --recommend 1 \
  --session .hcw/sessions/<session-id>

# 4. 终稿 — 从 artifacts 生成 design.md
python3 scripts/hcw_design.py finalize \
  --session .hcw/sessions/<session-id> \
  --scope "gateway/middleware/ratelimit.py" "gateway/config.yaml" \
  --criteria "python3 -m pytest tests/test_ratelimit.py" "wrk -c 100 -d 10s http://localhost:8080"

# 5. 审查 — 检查 design.md 完整性
python3 scripts/hcw_design.py review \
  --design .hcw/sessions/<session-id>/design.md
```

**设计会话产物**：

```text
.hcw/sessions/<session-id>/
├── manifest.json           # 目标、上下文、状态
├── events.jsonl            # 设计事件日志
├── exploration/
│   └── codebase.json       # 代码库扫描结果
├── proposals.json          # 设计方案及权衡
├── review.json             # 审查结果
└── design.md               # 最终设计文档
```

**集成点**：
- `hcw_session.py` — 设计 session 可作为实现 session 的前置输入
- `hcw_summarize.py` — 设计产物出现在最终报告中
- `hcw_update.py` — 同步 design 脚本 + 模板

**何时运行**：创建实现 brief 之前。设计阶段产出的 spec 是实现 brief 的输入。
