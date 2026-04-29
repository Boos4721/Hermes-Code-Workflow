---
name: hcw
description: "Use when coordinating coding work through Hermes-Code-Workflow: classify intent, route work to cc/Codex/OpenCode/Gemini/ACP workers, run Python adapters when useful, verify outputs, and iterate before reporting."
version: 0.2.0
author: Boos4721 + Hermes
license: MIT
metadata:
  hermes:
    tags: [workflow, orchestration, multi-agent, coding, verification, acp, sdk, python]
    related_skills: [hermes-agent, claude-code, codex, opencode, hermes-agent-skill-authoring]
---

# HCW — Hermes-Code-Workflow

## Overview

HCW is the house workflow for software development with Hermes as the control plane. It adapts the strongest ideas from CCW, ECC, and Superpowers while staying native to Hermes: tool calls, skills, persistent memory, session search, cron jobs, delegation, terminal/process management, and Python helper adapters.

Core rule: **workers execute; Hermes accepts or rejects.** A coding agent, CLI, SDK, or ACP session can implement, analyze, or review, but Hermes owns routing, scope control, verification, iteration, and user-facing reporting.

## Inspirations

- **CCW:** intent classification, chain routing, wave execution, session artifacts, multi-CLI orchestration.
- **ECC:** harness performance, cross-harness packaging, continuous learning, commands/skills/hooks/rules layering, token and context optimization.
- **Superpowers:** mandatory workflow discipline, brainstorm → plan → execute, TDD, subagent-driven development, two-stage review, verification before completion.

## When to Use

Use HCW when the user asks to:

- write, change, review, debug, test, refactor, or ship code
- “按 hcw 跑” / “走 HCW” / “让 cc 做，我来验”
- coordinate multiple workers such as `cc`, Codex, OpenCode, Gemini CLI, Qwen, or other ACP/SDK agents
- create a repeatable workflow rather than a one-off manual edit
- compare multiple implementations or ask one worker to review another
- turn a vague request into a plan, execution pass, validation loop, and final report

Do not use HCW as a substitute for explicit user approval on risky actions. If the next step is destructive, deploys to production, exposes credentials, force-pushes, or commits files the user has marked local-only, stop and confirm scope.

## Roles

### Human partner

- defines goals and final preferences
- approves high-risk changes and publishing decisions
- can override this workflow at any time

### Hermes

- clarifies only when ambiguity changes execution
- classifies intent and chooses workflow chain
- prepares worker briefs with constraints and acceptance checks
- runs or coordinates workers through native Hermes tools, ACP, official CLIs, or SDK adapters
- verifies observable results before declaring success
- captures durable lessons as skills when the work reveals a reusable pattern

### Workers

Workers include coding CLIs, SDK-backed agents, ACP agents, and Hermes subagents. They may analyze, implement, review, test, or package work, but they do not self-certify completion.

## Worker Transports

### ACP workers

Use ACP when the worker supports it and structured agent-process control helps.

Known pattern:

- `gemini-cli` can support ACP mode
- future ACP-compatible tools should be routed here

Hermes usage:

- Use `delegate_task` with `acp_command` / `acp_args` when the environment exposes the worker as ACP.
- Use ACP for long-lived structured worker conversations, strongly isolated tasks, and cross-model analysis.
- Ensure the prompt is self-contained because ACP/delegated workers do not inherit chat context.

### Official CLI / SDK workers

Use vendor-supported interfaces rather than ad-hoc wrappers.

Examples:

- `cc` / Claude Code: official CLI and official SDK-supported behavior where available
- Codex: official CLI / SDK-backed flow
- OpenCode: official CLI
- Other coding workers with official SDKs or CLIs

Hermes usage:

- Use `terminal` / `process` for CLI jobs.
- Use Python adapters under `scripts/` when SDK orchestration needs structured IO, retries, redaction, or result normalization.
- Prefer bounded one-shot modes for simple tasks and tmux/background sessions for multi-turn work.

### Hermes-native workers

Use Hermes tools directly when that is simpler and safer:

- `delegate_task` for reasoning-heavy subagents and parallel analysis
- `terminal` for builds, tests, git, package managers, and CLIs
- `read_file`, `search_files`, `patch`, `write_file` for verification and controlled edits
- `todo` for workflow state
- `cronjob` only for durable scheduled follow-up, not recursive worker spawning

## Python Adapter Layer

HCW may include Python helper scripts to bridge Hermes with ACP/CLI/SDK workers. Python adapters should be small, auditable, and transport-focused.

Use Python adapters for:

- normalizing worker outputs into JSON
- launching SDK-backed agents with stable options
- adding timeout/retry/redaction around CLIs
- collecting repo context before dispatch
- writing session artifacts such as `artifacts/hcw/<session-id>/manifest.json`
- comparing worker results and producing a verification checklist

Do not use Python adapters to hide risky behavior. They must print the commands they run or write clear structured logs, and they must not embed secrets.

Recommended adapter conventions:

```text
scripts/
  hcw_dispatch.py      # run one worker from a JSON brief
  hcw_verify.py        # run configured validation checks and emit JSON
  hcw_session.py       # create/read/update HCW session artifacts
  hcw_summarize.py     # summarize artifacts for final report
```

Recommended JSON brief:

```json
{
  "session_id": "HCW-20260430-001",
  "repo": "/path/to/repo",
  "worker": "cc",
  "mode": "implement",
  "goal": "Add wallet connection status card",
  "constraints": ["do not commit local helper scripts", "preserve public terminology"],
  "acceptance": ["npm run build passes", "diff only touches approved files"],
  "files": ["src/components/WalletConnectCard.tsx"]
}
```

Adapter output should be JSON when possible:

```json
{
  "ok": true,
  "worker": "cc",
  "changed_files": ["src/components/WalletConnectCard.tsx"],
  "summary": "Implemented status card copy updates",
  "verification": [{"command": "npm run build", "ok": true}],
  "risks": []
}
```

## Intent Classification

Before dispatching, classify the task. Use lightweight classification for simple requests; use a fuller chain for complex or risky work.

Fields:

- `action`: create | fix | analyze | plan | execute | debug | test | review | refactor | ship
- `object`: feature | bug | code | test | doc | ui | performance | security | architecture | project | workflow
- `style`: quick | documented | collaborative | structured | iterative | tdd | default
- `risk`: low | medium | high
- `worker_hint`: cc | codex | opencode | gemini | acp | sdk | auto

## Default Routing

Unless the user explicitly chooses a worker:

1. **Implementation-heavy work:** route first to `cc`.
2. **Architecture, diagnosis, broad analysis:** route to Gemini/ACP or a Hermes reasoning subagent, then hand implementation to `cc`.
3. **Second opinion / review:** route to Codex or OpenCode.
4. **Provider fallback:** if one worker fails due to quota/provider/runtime issues, switch worker and preserve artifacts.
5. **Final acceptance:** Hermes verifies directly.

## Workflow Chains

### Quick chain

Use for small, low-risk changes.

1. Inspect relevant files and git status.
2. Dispatch one worker or edit directly only if user explicitly wants Hermes to do it.
3. Verify diff and run the smallest meaningful check.
4. Report changed files, checks, and risks.

### Plan-execute chain

Use for non-trivial features or multi-file changes.

1. Explore project context.
2. Produce a concise plan with files, steps, checks, and risks.
3. Dispatch `cc` or selected worker with the plan.
4. Verify results.
5. Iterate until acceptance or blocker.

### Multi-worker chain

Use when confidence matters.

1. Dispatch analysis to Gemini/ACP or another reviewer.
2. Dispatch implementation to `cc`.
3. Dispatch review to Codex/OpenCode or Hermes subagent.
4. Hermes reconciles findings and requests fixes if needed.
5. Verify final state.

### TDD chain

Use for new logic, bug fixes, libraries, APIs, or anything where tests can be meaningful.

1. Define expected failing test.
2. Worker writes/runs failing test.
3. Worker implements minimal fix.
4. Worker runs tests to green.
5. Hermes verifies test evidence and diff.

### Debug chain

Use for failures and unknown root causes.

1. Reproduce or collect the exact failure.
2. Identify hypotheses; do not patch blindly.
3. Test the strongest hypothesis.
4. Implement the smallest fix.
5. Run regression checks.
6. Capture the root cause in final report.

### Ship chain

Use only when committing/pushing/releasing is in scope.

1. Inspect git status and ensure only approved files are included.
2. Run full project validation.
3. Prepare commit with configured identity and sign-off when required.
4. Push only when user has requested or approved it.
5. Report commit hash and remote branch.

## Session Artifacts

For substantial work, maintain artifacts under a local, gitignored path unless the repo intentionally tracks them:

```text
.hcw/
  sessions/
    HCW-YYYYMMDD-HHMMSS/
      brief.json
      plan.md
      workers.jsonl
      verification.json
      final-report.md
```

If a project already has an established planning/session directory, use that instead. Do not commit HCW artifacts unless the user asks.

## Dispatch Brief Template

Every worker brief should include:

```markdown
You are a worker in HCW. Hermes is the orchestrator and will verify your output.

Repo: <absolute path>
Mode: analyze | implement | review | test | debug
Goal: <exact goal>
Relevant files: <paths or discovery instructions>
Constraints:
- <forbidden changes>
- <style/project conventions>
Acceptance checks:
- <commands or observable checks>
Output required:
- summary
- files changed
- tests/checks run
- blockers/risks
Do not commit or push unless explicitly instructed.
```

## Verification Gate

Hermes must verify before final success:

- `git status --short` reviewed
- diff reviewed for scope and unintended changes
- requested behavior is observable or tests cover it
- build/test/lint command run when relevant
- worker claims backed by actual output
- no secrets exposed in summary
- no local-only helper/planning files committed without approval

If verification fails, use an iterative repair loop with the concrete failure message.

## Review Gate

For non-trivial code changes, use two review dimensions:

1. **Spec compliance:** Does the implementation satisfy the stated goal and constraints?
2. **Code quality:** Is it maintainable, safe, idiomatic, tested, and scoped?

Use separate workers or separate review passes when possible.

## Learning Loop

After difficult or repeated work:

- Save durable user preferences as memory if they will matter later.
- Save reusable procedures as skills, not memory.
- Patch stale skills immediately when a loaded skill is wrong or incomplete.
- Keep HCW itself generic; put project-specific conventions in project docs or separate skills.

## Common Pitfalls

1. **Letting a worker self-certify.** Worker success is input to verification, not proof.
2. **Skipping context discovery.** Always inspect enough repo state to avoid wrong assumptions.
3. **Over-orchestrating tiny tasks.** Use the quick chain when the scope is small.
4. **Under-orchestrating risky work.** Use plan/review/verification gates for production, security, data, and deployment changes.
5. **Mixing local artifacts into commits.** Keep HCW session files, helper scripts, and plans uncommitted unless approved.
6. **Using vague prompts.** Give workers exact goals, paths, constraints, and checks.
7. **Treating ACP/SDK/CLI as equivalent.** Pick the transport based on reliability, observability, and official support.

## Verification Checklist

- [ ] Relevant skills loaded before acting
- [ ] Intent classified and chain selected
- [ ] Worker transport chosen deliberately: ACP, official SDK/CLI, or Hermes-native
- [ ] Worker brief includes goal, repo, constraints, acceptance checks, and no-commit rule
- [ ] Artifacts recorded for substantial work
- [ ] Diff and git status reviewed
- [ ] Build/test/lint or equivalent validation run when relevant
- [ ] Failed validation triggers focused repair loop
- [ ] Final report states files changed, checks run, result, and risks
