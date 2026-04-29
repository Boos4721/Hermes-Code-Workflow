# Hermes-Code-Workflow

HCW (Hermes-Code-Workflow) is our Hermes-centered coding workflow.

It adapts ideas from:
- CCW (Claude Code Workflow): intent classification, workflow chains, wave execution, session artifacts
- ECC (Everything Claude Code): harness performance, cross-agent ergonomics, verification loops, continuous learning
- Superpowers: brainstorm → plan → execute discipline, TDD, subagent-driven development, verification before completion

## Core philosophy

- Hermes is the orchestrator and final verifier.
- cc / Codex / OpenCode / Gemini CLI / ACP or SDK-backed workers execute bounded tasks.
- Gemini can be routed through ACP when available.
- cc, Codex, and similar tools should use official SDK/CLI paths where possible.
- Python adapters may bridge Hermes to ACP/CLI/SDK workers with structured JSON, retries, and validation.
- Execution is not acceptance; Hermes verifies before reporting success.

## Layout

- `skills/hcw/SKILL.md` — main HCW skill definition
- `skills/hcw/references/python-adapters.md` — Python adapter guidance for Hermes integration
- `docs.md` — authoring notes

## Intended use

Use HCW when a coding task needs repeatable routing, execution, validation, and reporting:

- “按 hcw 跑这个需求”
- “先让 gemini-cli 分析，再让 cc 实现”
- “让 cc 改，Codex/OpenCode review，你验收”
- “这个 bug 按 hcw 修到测试过”
