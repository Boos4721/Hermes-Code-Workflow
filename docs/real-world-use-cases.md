# Real-World Use Cases

Hermes Code Workflow is most useful when you care about bounded execution, reproducible verification, and clear final reporting.

This page shows where it fits in real work.

## 1. Bug fix with proof

### Situation

A user reports a bug, but the fix is small enough that a coding agent could accidentally over-edit the codebase.

### How HCW helps

Hermes:

- creates a session
- writes a narrowly scoped brief
- limits relevant files
- requires a concrete acceptance check
- verifies the result before reporting success

### Why this is better than ad hoc agent use

Without HCW, the worker might:

- change unrelated files
- skip reproducing the bug
- claim success without evidence

With HCW, the work is bounded and verifiable.

### Example

- Fix login error messaging
- Acceptance: `pytest tests/test_auth.py -v` exits 0
- Diff scope: only auth module and its tests

## 2. Small feature implementation

### Situation

You want to add a contained feature without letting the implementation sprawl.

### How HCW helps

Hermes can:

- choose a plan-execute or test-first chain
- send a standard brief to a worker
- require explicit acceptance checks
- run verification after implementation

### Good fit

- add a settings toggle
- add a new API field
- add a dashboard widget
- add a CLI flag

### Why it matters

The workflow keeps the feature small, inspectable, and easy to review.

## 3. Independent code review

### Situation

The code is already written, but you want a separate review pass with structure.

### How HCW helps

Hermes can dispatch a worker in review mode, then record review events alongside the implementation session.

This works well when you want:

- spec compliance review first
- code quality review second
- a durable artifact trail for findings

### Good fit

- review a risky patch before merge
- get a second opinion from a different worker
- separate implementation from evaluation

## 4. Pre-merge verification gate

### Situation

A worker changed files and says everything is complete. You need stronger proof.

### How HCW helps

HCW turns verification into a first-class phase.

Hermes can run:

- test commands
- build commands
- lint commands
- diff-scope checks
- secret scans
- output pattern assertions

### Why this is valuable

This is where HCW becomes operationally useful rather than just process-heavy.

It gives you a real gate before saying:

> yes, this is ready

## 5. Multi-worker comparison

### Situation

You want one worker to implement and another to review, or you want two candidate approaches compared.

### How HCW helps

Hermes remains the stable orchestrator while workers stay replaceable.

Possible pattern:

- worker A implements
- worker B reviews
- Hermes verifies the final result
- Hermes reports evidence and trade-offs

### Good fit

- architecture-sensitive changes
- migrations
- tricky bug fixes
- tasks where you want a second opinion

## 6. Debugging with artifact history

### Situation

A fix attempt failed and you need to understand what happened across iterations.

### How HCW helps

Because session artifacts are recorded, Hermes can inspect:

- what was attempted
- what commands were run
- what failed verification
- what the review feedback said

### Why this matters

Instead of re-debugging from memory, you get a concrete session trail.

## 7. Demoing an agent workflow to others

### Situation

You need to explain to a teammate, client, or evaluator how your agent workflow actually works.

### How HCW helps

HCW is demo-friendly because it produces artifacts.

You can show:

- the brief
- the dispatch logic
- the verification evidence
- the final report

That is much more convincing than saying "the agent handled it".

## 8. Safer adoption of coding agents

### Situation

You want the speed of coding agents without giving them unlimited room to improvise.

### How HCW helps

HCW adds guardrails:

- bounded briefs
- explicit constraints
- acceptance checks
- post-execution verification
- structured summaries

### Best use

This is often the strongest reason to adopt HCW at all.

It does not try to replace coding agents. It makes them safer and easier to trust.

## When HCW is probably overkill

HCW is not mandatory for every task.

You may not need it when:

- the task is a one-line local edit
- no worker handoff is involved
- verification is trivial and immediate
- you do not need an artifact trail

In those cases, a direct quick chain may be enough.

## Quick selection guide

Use HCW when you need one or more of these:

- scoped delegation
- reproducible verification
- review separation
- artifact-based reporting
- safer multi-agent coordination

If that sounds like your workflow, HCW is a strong fit.

## Recommended next step

- New user: start with `docs/quick-start.md`
- Evaluating the workflow: read `docs/full-demo.md`
- Ready to inspect raw artifacts: open `docs/demo-session/README.md`
