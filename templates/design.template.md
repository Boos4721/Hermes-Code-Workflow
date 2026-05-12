# Design: [Design Goal]

- **Session**: `<session-id>`
- **Status**: `draft | finalized | approved`
- **Created**: `<timestamp>`

## Goal

One sentence describing what success looks like.
This goal must be testable — at the end, a clear yes/no verdict should be possible.

## Context

- **Project**: link or path
- **Current state**: what exists today
- **Motivation**: why this design is needed
- **Dependencies**: what this design depends on

## Scope

### In scope

- Component / files to create or modify
- API contracts, data structures, interfaces
- Configuration changes

### Out of scope (explicitly)

- Things this design does NOT address
- Future phases that are explicitly deferred

## Approach

### Approach N (Recommended)

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

Brief description. Why not chosen: trade-off explanation.

## Constraints

- Performance: latency / throughput / memory budgets
- Security: auth, encryption, input validation requirements
- Compatibility: backwards compatibility, migration strategy
- Platform: supported OS / runtime / hardware
- Style: project conventions, naming, error handling patterns

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
