# Design: [Design Goal]

- **Session**: `<session-id>`
- **Status**: `draft | finalized | approved`
- **Created**: `<timestamp>`

## Goal

One sentence describing what success looks like.
This goal must be testable.

## Context

- **Project**: link or path
- **Current state**: what exists today
- **Motivation**: why this design is needed
- **Dependencies**: what this design depends on

## Assumptions

> 开始前先确认这些假设（Junior Designer 模式）

- [scope_impact] 改动范围仅限于 XXX 模块
- [dependency] XXX 依赖已经就绪
- [performance] 预期 QPS XXX / 延迟 < XXXms

## Scope

### In scope

- Component/files to create or modify
- API contracts, data structures, interfaces
- Configuration changes

### Out of scope (explicitly)

- Things this design does NOT address

## Approach

### Approach N (Recommended)

**设计轴**: `模块拆分粒度` — Monolith vs micro-services vs modular monolith

**Description**: one paragraph explaining the approach.

**Key components**:

- `file1.py` — responsibility description
- `file2.rs` — responsibility description

**Data flow / Architecture**:

```text
[Component A] → (event/message) → [Component B] → (RPC call) → [Component C]
```

**Complexity**: `low | medium | high`

**Risk**: `low | medium | high`

### Alternatives considered

#### Approach M
设计轴: `数据流风格` — 同步 vs 事件驱动 vs CQRS
Brief description. Why not chosen.

## Constraints

- Performance: latency / throughput / memory budgets
- Security: auth, encryption, input validation requirements
- Compatibility: backwards compatibility, migration strategy
- Platform: supported OS / runtime / hardware

## Acceptance Criteria

- [ ] Criterion 1: runnable command and expected output
- [ ] Criterion 2: observable behavior outcome
- [ ] Criterion 3: non-functional requirement (performance, security)

## Open Questions

- Question 1 — proposed default: X, owner: Y, deadline: Z
- Question 2 — proposed default: A, owner: B, deadline: C

## Risks

- Risk 1: description and mitigation
- Risk 2: description and mitigation

## Review

- **Overall Score**: 7.2/10 (good)
- **Dimension Scores**
  - 架构一致性: 7/10 — 整体一致，偶有跨层引用
  - 模块化程度: 8/10 — 高内聚低耦合
  - 可扩展性: 6/10 — 新功能需改1-2处
  - 可维护性: 7/10 — 有错误处理
  - 可测试性: 8/10 — 大部分可 mock

### Quick Wins

- [high] 缺少错误中间件 | 添加统一的 error handling middleware
- [medium] 配置没有 fallback | 为所有配置项添加默认值
- [low] 部分函数 > 100 行 | 拆分为小函数
