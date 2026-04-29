---
name: hcw
description: "Use when coordinating coding work through Hermes-Code-Workflow: brainstorm designs, classify intent, route work to cc/Codex/OpenCode/Gemini/ACP workers, run Python adapters when useful, verify outputs with evidence, and iterate before reporting."
version: 0.3.0
author: Boos4721 + Hermes
license: MIT
metadata:
  hermes:
    tags: [workflow, orchestration, multi-agent, coding, verification, acp, sdk, python, brainstorm]
    related_skills: [hermes-agent, claude-code, codex, opencode, hermes-agent-skill-authoring]
---

# HCW — Hermes-Code-Workflow

## Overview

HCW is the house workflow for software development with Hermes as the control plane. It adapts the strongest ideas from CCW, ECC, and Superpowers while staying native to Hermes: tool calls, skills, persistent memory, session search, cron jobs, delegation, terminal/process management, and Python helper adapters.

Core rule: **workers execute; Hermes accepts or rejects.** A coding agent, CLI, SDK, or ACP session can implement, analyze, or review, but Hermes owns routing, scope control, verification, iteration, and user-facing reporting.

**Iron Law:** No completion claims without fresh verification evidence. If you haven't run the verification command in this turn, you cannot claim it passes.

## Inspirations

- **CCW:** intent classification, chain routing, wave execution, session artifacts, multi-CLI orchestration, semantic CLI invocation, task JSON schema, cross-validation between workers.
- **ECC:** harness performance, cross-harness packaging, continuous learning, commands/skills/hooks/rules layering, token and context optimization, codex/opencode/gemini adapter patterns.
- **Superpowers:** mandatory brainstorm → plan → execute discipline, TDD, subagent-driven development, two-stage review (spec compliance then code quality), verification before completion, parallel agent dispatch, worktree isolation.

## When to Use

Use HCW when the user asks to:

- write, change, review, debug, test, refactor, or ship code
- "按 hcw 跑" / "走 HCW" / "让 cc 做，我来验"
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
- runs brainstorm phase for non-trivial work (see Brainstorm Phase below)
- prepares worker briefs with constraints and acceptance checks
- coordinates workers through native Hermes tools, Agent Client Protocol, official command-line interfaces, or software development kit adapters
- verifies observable results before declaring success (see Verification Gate below)
- captures durable lessons as skills when the work reveals a reusable pattern

### Workers

Workers include coding CLIs, SDK-backed agents, ACP agents, and Hermes subagents. They may analyze, implement, review, test, or package work, but they do not self-certify completion.

## Brainstorm Phase

**Hard gate:** Do NOT dispatch any worker for implementation until the brainstorm phase is complete for non-trivial work. Quick chain (typos, single-line fixes, obvious changes) skips brainstorm.

### When to brainstorm

- New features, components, or significant behavior changes
- Multi-file refactoring or architectural changes
- Anything where "what exactly are we building?" is not 100% clear
- Bug fixes with unknown root cause

### Brainstorm process

1. **Explore project context** — check files, docs, recent commits, existing patterns
2. **Ask clarifying questions** — one at a time, prefer multiple choice, understand purpose/constraints/success criteria
3. **Propose 2-3 approaches** — with trade-offs and your recommendation
4. **Present design** — sections scaled to complexity, get approval after each section
5. **Write design doc** — save to `.hcw/sessions/<session-id>/design.md`
6. **Spec self-review** — check for placeholders, contradictions, ambiguity, scope
7. **User reviews spec** — wait for approval before proceeding
8. **Transition to planning** — create implementation plan or dispatch to planning worker

### Brainstorm output

```text
.hcw/sessions/<session-id>/
  design.md          # approved design spec
  plan.md            # implementation plan (after brainstorm)
```

## Intent Classification

Before dispatching, classify the task. Use lightweight classification for simple requests; use a fuller chain for complex or risky work.

### Classification fields

- `action`: create | fix | analyze | plan | execute | debug | test | review | refactor | ship | brainstorm
- `object`: feature | bug | code | test | doc | ui | performance | security | architecture | project | workflow
- `style`: quick | documented | collaborative | structured | iterative | tdd | default
- `risk`: low | medium | high
- `worker_hint`: cc | codex | opencode | gemini | acp | sdk | auto

### Routing decision matrix

| Situation | Default worker | Rationale |
|-----------|---------------|-----------|
| Implementation-heavy work | `cc` | Best coding model, official CLI |
| Architecture / broad analysis | Gemini/ACP → then `cc` implement | Gemini for strategic view, cc for execution |
| Second opinion / review | Codex or OpenCode | Independent perspective |
| TDD / test-first | `cc` with TDD chain | Structured test-first flow |
| Debug unknown failure | Hermes reasoning → `cc` fix | Hermes classifies, cc implements |
| Quick fix / typo | Hermes direct | Skip worker overhead |
| Multi-worker confidence | Gemini analyze → `cc` implement → Codex review | Three perspectives |

### Worker mode control

Each worker dispatch has a mode that governs permissions:

| Mode | Permission | When to use |
|------|-----------|-------------|
| `analyze` | Read-only | Review, exploration, diagnosis, architecture analysis |
| `implement` | Create/Modify/Delete | Implementation, bug fixes, refactoring |
| `review` | Read-only (git-aware) | Code review, diff analysis, spec compliance check |

### Fallback chain

Primary worker fails → next enabled worker → Hermes-native execution. Always preserve artifacts when switching workers.

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

### Semantic CLI invocation

Users can semantically specify CLI tools in prompts. Hermes auto-invokes the corresponding CLI:

| User phrase | Hermes action |
|-------------|--------------|
| "用 Gemini 分析 auth 模块" | Route to Gemini in `analyze` mode |
| "让 Codex review 这段代码" | Route to Codex in `review` mode |
| "Gemini 设计，cc 实现" | Multi-worker chain: Gemini analyze → cc implement |
| "三个工具都看看" | Parallel dispatch to Gemini, Codex, cc |

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
- writing session artifacts such as `.hcw/sessions/<session-id>/manifest.json`
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

See `references/python-adapters.md` for detailed scaffolding, JSON schemas, and implementation patterns.

## Default Routing

Unless the user explicitly chooses a worker:

1. **Implementation-heavy work:** route first to `cc`.
2. **Architecture, diagnosis, broad analysis:** route to Gemini/ACP or a Hermes reasoning subagent, then hand implementation to `cc`.
3. **Second opinion / review:** route to Codex or OpenCode.
4. **Provider fallback:** if one worker fails due to quota/provider/runtime issues, switch worker and preserve artifacts.
5. **Final acceptance:** Hermes verifies directly.

## Workflow Chains

### Quick chain

Use for small, low-risk changes. Skips brainstorm phase.

1. Inspect relevant files and git status.
2. Dispatch one worker or edit directly only if user explicitly wants Hermes to do it.
3. Verify diff and run the smallest meaningful check.
4. Report changed files, checks, and risks.

### Plan-execute chain

Use for non-trivial features or multi-file changes.

1. **Brainstorm** — explore context, clarify requirements, propose approaches, get design approval.
2. **Plan** — produce concise plan with files, steps, checks, and risks. Save to `.hcw/sessions/<id>/plan.md`.
3. **Dispatch** — `cc` or selected worker with the plan.
4. **Verify** — Hermes runs verification gate.
5. **Iterate** — until acceptance or blocker.

### Multi-worker chain

Use when confidence matters.

1. **Brainstorm** — design phase with Hermes.
2. **Analyze** — dispatch to Gemini/ACP for strategic analysis.
3. **Implement** — dispatch to `cc` with analysis output.
4. **Review** — dispatch to Codex/OpenCode for independent review.
5. **Cross-validate** — Hermes reconciles findings, requests fixes if needed.
6. **Verify** — final verification gate.

### Subagent-driven chain

Use for plans with multiple independent tasks. Inspired by Superpowers subagent-driven development.

1. **Read plan** — extract all tasks with full text and context.
2. **Per task:**
   a. Dispatch fresh implementer subagent (isolated context, no session pollution).
   b. Implementer reports: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED.
   c. Dispatch spec compliance reviewer subagent.
   d. If spec issues found → implementer fixes → re-review.
   e. Dispatch code quality reviewer subagent.
   f. If quality issues found → implementer fixes → re-review.
   g. Mark task complete.
3. **Final review** — dispatch reviewer for entire implementation.
4. **Verify** — Hermes runs verification gate.

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
      design.md           # brainstorm output (approved spec)
      plan.md             # implementation plan
      brief.json          # worker dispatch brief
      workers.jsonl       # worker event log
      verification.json   # verification results
      final-report.md     # summary for human
```

If a project already has an established planning/session directory, use that instead. Do not commit HCW artifacts unless the user asks.

## Dispatch Brief Template

Every worker brief should include:

```markdown
You are a worker in HCW. Hermes is the orchestrator and will verify your output.

Repo: <absolute path>
Mode: analyze | implement | review
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

**Iron Law:** No completion claims without fresh verification evidence.

Hermes must verify before final success:

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

### Verification checklist

- `git status --short` reviewed
- diff reviewed for scope and unintended changes
- requested behavior is observable or tests cover it
- build/test/lint command run when relevant
- worker claims backed by actual output
- no secrets exposed in summary
- no local-only helper/planning files committed without approval

### Red flags — STOP

| Claim | Requires | Not sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

If verification fails, use an iterative repair loop with the concrete failure message.

## Review Gate

For non-trivial code changes, use two review dimensions (inspired by Superpowers two-stage review):

1. **Spec compliance:** Does the implementation satisfy the stated goal and constraints? No over-building, no missing requirements.
2. **Code quality:** Is it maintainable, safe, idiomatic, tested, and scoped?

Use separate workers or separate review passes when possible. Spec compliance must pass before code quality review begins.

## Model Selection

Use the least powerful model that can handle each role to conserve cost and increase speed.

| Task type | Model tier | Examples |
|-----------|-----------|---------|
| Mechanical implementation (1-2 files, clear spec) | Fast/cheap | Isolated function, config change |
| Integration and judgment (multi-file) | Standard | Feature with dependencies |
| Architecture, design, review | Most capable | System design, security review |

## Learning Loop

After difficult or repeated work:

- Save durable user preferences as memory if they will matter later.
- Save reusable procedures as skills, not memory.
- Patch stale skills immediately when a loaded skill is wrong or incomplete.
- Keep HCW itself generic; put project-specific conventions in project docs or separate skills.

## Common Pitfalls

1. **Letting a worker self-certify.** Worker success is input to verification, not proof.
2. **Skipping context discovery.** Always inspect enough repo state to avoid wrong assumptions.
3. **Skipping brainstorm phase.** "Simple" projects are where unexamined assumptions cause the most wasted work.
4. **Over-orchestrating tiny tasks.** Use the quick chain when the scope is small.
5. **Under-orchestrating risky work.** Use plan/review/verification gates for production, security, data, and deployment changes.
6. **Mixing local artifacts into commits.** Keep HCW session files, helper scripts, and plans uncommitted unless approved.
7. **Using vague prompts.** Give workers exact goals, paths, constraints, and checks.
8. **Treating ACP/SDK/CLI as equivalent.** Pick the transport based on reliability, observability, and official support.
9. **Trusting agent success reports.** Always verify independently.
10. **Starting code quality review before spec compliance passes.** Wrong order — spec first, quality second.

## Verification Checklist

- [ ] Relevant skills loaded before acting
- [ ] Intent classified and chain selected
- [ ] Brainstorm phase completed for non-trivial work (design approved)
- [ ] Worker transport chosen deliberately: ACP, official SDK/CLI, or Hermes-native
- [ ] Worker brief includes goal, repo, constraints, acceptance checks, and no-commit rule
- [ ] Artifacts recorded for substantial work
- [ ] Diff and git status reviewed
- [ ] Build/test/lint or equivalent validation run when relevant
- [ ] Failed validation triggers focused repair loop
- [ ] Two-stage review completed (spec compliance → code quality) for non-trivial changes
- [ ] Final report states files changed, checks run, result, and risks
