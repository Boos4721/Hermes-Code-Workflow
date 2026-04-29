---
name: hcw
description: "Use when coordinating coding work through Hermes Code Workflow: brainstorm designs, classify intent, route work to Claude Code, Codex, OpenCode, Gemini, or Agent Client Protocol workers, run Python adapters when useful, verify outputs with evidence, and iterate before reporting."
version: 0.3.0
author: Boos4721 + Hermes
license: MIT
metadata:
  hermes:
    tags: [workflow, orchestration, multi-agent, coding, verification, agent-client-protocol, software-development-kit, python, brainstorm]
    related_skills: [hermes-agent, claude-code, codex, opencode, hermes-agent-skill-authoring]
---

# Hermes Code Workflow

## Overview

Hermes Code Workflow is the house workflow for software development with Hermes as the control plane. It adapts the strongest ideas from Claude Code Workflow, Everything Claude Code, and Superpowers while staying native to Hermes: tool calls, skills, persistent memory, session search, cron jobs, delegation, terminal/process management, and Python helper adapters.

Core rule: **workers execute; Hermes accepts or rejects.** A coding agent, command-line interface, software development kit, or Agent Client Protocol session can implement, analyze, or review, but Hermes owns routing, scope control, verification, iteration, and user-facing reporting.

**Iron Law:** No completion claims without fresh verification evidence. If you haven't run the verification command in this turn, you cannot claim it passes.

## Inspirations

- **Claude Code Workflow:** intent classification, chain routing, wave execution, session artifacts, multi-tool orchestration, semantic command invocation, task JavaScript Object Notation schema, cross-validation between workers.
- **Everything Claude Code:** harness performance, cross-harness packaging, continuous learning, commands/skills/hooks/rules layering, token and context optimization, Codex/OpenCode/Gemini adapter patterns.
- **Superpowers:** mandatory brainstorm → plan → execute discipline, test-first development, subagent-driven development, two-stage review (spec compliance then code quality), verification before completion, parallel agent dispatch, worktree isolation.

## When to Use

Use Hermes Code Workflow when the user asks to:

- write, change, review, debug, test, refactor, or ship code
- "按 hermes-code-workflow 跑" / "走 Hermes Code Workflow" / "让 Claude Code 做，我来验"
- coordinate multiple workers such as Claude Code, Codex, OpenCode, Gemini command-line interface, Qwen, or other Agent Client Protocol/software development kit agents
- create a repeatable workflow rather than a one-off manual edit
- compare multiple implementations or ask one worker to review another
- turn a vague request into a plan, execution pass, validation loop, and final report

Do not use Hermes Code Workflow as a substitute for explicit user approval on risky actions. If the next step is destructive, deploys to production, exposes credentials, force-pushes, or commits files the user has marked local-only, stop and confirm scope.

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

Workers include coding command-line interfaces, software development kit-backed agents, Agent Client Protocol agents, and Hermes subagents. They may analyze, implement, review, test, or package work, but they do not self-certify completion.

Worker operational constraints:

- **Scope-locked.** Only touch files named in the brief. If a dependency is missing, report it; do not silently edit extra files.
- **Goal-faithful.** Implement exactly what the brief describes. Do not add features, refactor surrounding code, or "improve" things not in scope.
- **No self-certification.** Worker success claims are input to verification, never proof. The worker must paste evidence; Hermes re-runs the check.
- **No silent skipping.** If a step fails or is impossible, report what was tried, the exact error, and what is believed necessary. Never omit a step without explanation.
- **Preserve context.** When output is truncated or a command produces excessive logs, paste the last 20 lines (or enough to show the outcome) rather than summarizing.

## Brainstorm Phase

**Hard gate:** Do NOT dispatch any worker for implementation until the brainstorm phase is complete for non-trivial work. Quick chain (typos, single-line fixes, obvious changes) skips brainstorm.

### When to brainstorm

- New features, components, or significant behavior changes
- Multi-file refactoring or architectural changes
- Anything where "what exactly are we building?" is not 100% clear
- Bug fixes with unknown root cause

### Skip criteria — brainstorm may be skipped when ALL of these hold

- Change is a single file or a small, self-contained set of files (at most three)
- Goal is unambiguous: the user stated exactly what to change and what success looks like
- No architectural decision, dependency trade-off, or design question is open
- Risk is low: no security, data-migration, or public-facing contract change
- The quick chain is the intended chain (typos, config edits, obvious one-liners, renames)

If any condition fails, brainstorm is mandatory.

### Brainstorm process

1. **Explore project context** — check files, docs, recent commits, existing patterns
2. **Ask clarifying questions** — one at a time, prefer multiple choice, understand purpose/constraints/success criteria
3. **Propose 2-3 approaches** — with trade-offs and your recommendation
4. **Present design** — sections scaled to complexity, get approval after each section
5. **Write design doc** — save to `.hcw/sessions/<session-id>/design.md`
6. **Spec self-review** — check for placeholders, contradictions, ambiguity, scope
7. **User reviews spec** — wait for approval before proceeding
8. **Transition to planning** — create implementation plan or dispatch to planning worker

### Brainstorm done criteria

Brainstorm is complete and Hermes may proceed to planning or dispatch when **all** of the following are true:

1. **Goal is one sentence and testable.** The user has confirmed what success looks like in observable terms.
2. **Scope is bounded.** The files, components, or areas to change are listed. No open question about "where does this live?"
3. **Approach is chosen.** At least two approaches were compared (or one was presented and accepted). Trade-offs are recorded.
4. **Constraints are explicit.** Performance, security, compatibility, or style constraints are written down, not implied.
5. **Acceptance checks are defined.** At least one runnable command or observable outcome that proves the work is done.
6. **Open questions are resolved or parked.** No blocking question remains unanswered. Parked items are listed with an owner and a deadline or decision rule.
7. **User has approved the design.** Explicit approval, not silence. If the user said "looks good" or "go ahead," that counts. No response does not count.

If any item above is not met, Hermes must continue the brainstorm phase — ask the missing question, propose the missing approach, or request the missing approval — before dispatching any worker.

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
- `style`: quick | documented | collaborative | structured | iterative | test-first-development | default
- `risk`: low | medium | high
- `worker_hint`: Claude Code | Codex | OpenCode | Gemini | Agent Client Protocol | software development kit | auto

### Routing decision matrix

| Situation | Default worker | Rationale |
|-----------|---------------|-----------|
| Implementation-heavy work | Claude Code | Best coding model, official command-line interface |
| Architecture / broad analysis | Gemini/Agent Client Protocol → then Claude Code implement | Gemini for strategic view, Claude Code for execution |
| Second opinion / review | Codex or OpenCode | Independent perspective |
| test-first development / test-first | Claude Code with test-first development chain | Structured test-first flow |
| Debug unknown failure | Hermes reasoning → Claude Code fix | Hermes classifies, Claude Code implements |
| Quick fix / typo | Hermes direct | Skip worker overhead |
| Multi-worker confidence | Gemini analyze → Claude Code implement → Codex review | Three perspectives |

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

### Agent Client Protocol workers *(Planned — integration not yet wired)*

Use Agent Client Protocol when the worker supports it and structured agent-process control helps.

Known pattern:

- Gemini command-line interface can support Agent Client Protocol mode
- future Agent Client Protocol-compatible tools should be routed here

Hermes usage:

- Use `delegate_task` with Agent Client Protocol command fields when the environment exposes the worker as Agent Client Protocol.
- Use Agent Client Protocol for long-lived structured worker conversations, strongly isolated tasks, and cross-model analysis.
- Ensure the prompt is self-contained because Agent Client Protocol/delegated workers do not inherit chat context.

### Official command-line interface / software development kit workers

Use vendor-supported interfaces rather than ad-hoc wrappers.

Examples:

- Claude Code: official command-line interface and official software development kit-supported behavior where available
- Codex: official command-line interface / software development kit-backed flow
- OpenCode: official command-line interface
- Other coding workers with official software development kits or command-line interfaces

Hermes usage:

- Use `terminal` / `process` for command-line interface jobs.
- Use Python adapters under `scripts/` when software development kit orchestration needs structured input and output, retries, redaction, or result normalization.
- Prefer bounded one-shot modes for simple tasks and tmux/background sessions for multi-turn work.

### Semantic command-line interface invocation

Users can semantically specify command-line interface tools in prompts. Hermes auto-invokes the corresponding command-line interface:

| User phrase | Hermes action |
|-------------|--------------|
| "用 Gemini 分析 auth 模块" | Route to Gemini in `analyze` mode |
| "让 Codex review 这段代码" | Route to Codex in `review` mode |
| "Gemini 设计，Claude Code 实现" | Multi-worker chain: Gemini analyze → Claude Code implement |
| "三个工具都看看" | Parallel dispatch to Gemini, Codex, Claude Code |

### Hermes-native workers

Use Hermes tools directly when that is simpler and safer:

- `delegate_task` for reasoning-heavy subagents and parallel analysis
- `terminal` for builds, tests, git, package managers, and command-line interfaces
- `read_file`, `search_files`, `patch`, `write_file` for verification and controlled edits
- `todo` for workflow state
- `cronjob` only for durable scheduled follow-up, not recursive worker spawning

## Python Adapter Layer

Hermes Code Workflow may include Python helper scripts to bridge Hermes with Agent Client Protocol/command-line interface/software development kit workers. Python adapters should be small, auditable, and transport-focused.

Use Python adapters for:

- normalizing worker outputs into JavaScript Object Notation
- launching software development kit-backed agents with stable options
- adding timeout/retry/redaction around command-line interfaces
- collecting repo context before dispatch
- writing session artifacts such as `.hcw/sessions/<session-id>/manifest.json`
- comparing worker results and producing a verification checklist

Do not use Python adapters to hide risky behavior. They must print the commands they run or write clear structured logs, and they must not embed secrets.

Recommended adapter conventions:

```text
scripts/
  hcw_dispatch.py      # run one worker from a JSON brief
  hcw_verify.py        # run configured validation checks and emit JSON evidence
  hcw_session.py       # create/read/update Hermes Code Workflow session artifacts
  hcw_summarize.py     # summarize artifacts for final report
```

See `references/python-adapters.md` for detailed scaffolding, structured data schemas, and implementation patterns. *(Planned — file not yet written.)*

## Default Routing

Unless the user explicitly chooses a worker:

1. **Implementation-heavy work:** route first to Claude Code.
2. **Architecture, diagnosis, broad analysis:** route to Gemini/Agent Client Protocol or a Hermes reasoning subagent, then hand implementation to Claude Code.
3. **Second opinion / review:** route to Codex or OpenCode.
4. **Provider fallback:** if one worker fails due to quota/provider/runtime issues, switch worker and preserve artifacts.
5. **Final acceptance:** Hermes verifies directly.

## Chain Selection Decision Aid

Use this table to pick the right chain. Read top to bottom; the first matching row wins.

| Condition | Chain | Why |
|-----------|-------|-----|
| Committing, pushing, or releasing is the goal | **Ship chain** | Shipping has its own validation gates; skip it only if the user says "don't commit yet." |
| The task is a failure, crash, regression, or unknown root cause | **Debug chain** | Diagnosis before fixing; do not guess and patch. |
| The task is small, low-risk, single-file or trivially scoped, and the user did not ask for planning | **Quick chain** | Skip brainstorm and worker overhead. |
| Tests are meaningful for the new logic (new feature, bug fix with reproduction, library, application programming interface) | **test-first development chain** (compose with plan-execute or subagent-driven) | Write failing test first, then implement. |
| The plan has three or more independent tasks that can run in parallel | **Subagent-driven chain** | Fresh subagent per task, parallel execution, per-task review. |
| The user asked for multi-perspective analysis, second opinions, or high confidence | **Multi-worker chain** | Gemini analyze → Claude Code implement → Codex/OpenCode review. |
| Everything else (features, refactors, multi-file changes, non-trivial work) | **Plan-execute chain** | Brainstorm → plan → dispatch → verify → iterate. |

When in doubt, prefer **plan-execute chain** — it is the safe default. Compose chains when conditions overlap: for example, a non-trivial feature where tests matter uses plan-execute with test-first development embedded in the dispatch step.

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
2. **Plan** — produce concise plan with files, steps, checks, and risks. Save to `.hcw/sessions/<session-id>/plan.md`.
3. **Dispatch** — Claude Code or selected worker with the plan.
4. **Verify** — Hermes runs verification gate.
5. **Iterate** — until acceptance or blocker.

### Multi-worker chain

Use when confidence matters.

1. **Brainstorm** — design phase with Hermes.
2. **Analyze** — dispatch to Gemini/Agent Client Protocol for strategic analysis.
3. **Implement** — dispatch to Claude Code with analysis output.
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

### test-first development chain

Use for new logic, bug fixes, libraries, application programming interfaces, or anything where tests can be meaningful.

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

## Failure Routing

When a chain step fails, Hermes decides the next action based on the failure type. Do not re-dispatch blindly; route based on what actually happened.

| Failure type | Symptom | Hermes action |
|---|---|---|
| **Worker runtime crash** | Worker process exits non-zero, times out, or produces no output | Retry once with the same brief. If it fails again, switch to the fallback worker and preserve any partial artifacts. |
| **Acceptance check failure** | Worker output claims success but the command fails or output does not match | Send the exact failure message back to the same worker with a focused repair brief (not the original full brief). Limit to three repair rounds. |
| **Spec compliance failure** | Reviewer finds the implementation does not match the goal or violates constraints | Return specific gaps to the implementer with line references. Re-run spec compliance review after fixes. |
| **Code quality failure** | Reviewer finds maintainability, safety, or idiomatic issues | Return issues to the implementer. If issues are low severity and the user wants speed, flag them as known and proceed. |
| **Scope creep** | Worker modified files or behavior outside the brief | Revert out-of-scope changes. Re-dispatch with a tighter brief or add the scope explicitly if the change is justified. |
| **Ambiguous or missing context** | Worker reports it cannot proceed because the brief is incomplete | Hermes gathers the missing context, updates the brief, and re-dispatches. |

After three repair rounds on the same failure, stop and escalate to the human partner with a summary of what was tried and the persistent failure.

## Session Artifacts

For substantial work, maintain artifacts under a local, gitignored path unless the repo intentionally tracks them:

```text
.hcw/
  sessions/
    Hermes-Code-Workflow-YYYYMMDD-HHMMSS/
      design.md           # brainstorm output (approved spec)
      plan.md             # implementation plan
      brief.json          # worker dispatch brief
      workers.jsonl       # worker event log
      verification.json   # verification results
      final-report.md     # summary for human
```

If a project already has an established planning/session directory, use that instead. Do not commit Hermes Code Workflow artifacts unless the user asks.

## Dispatch Brief Template

Every worker brief should include the sections below. Hermes fills every bracket before sending; no field may be left as a placeholder.

```markdown
You are a worker in Hermes Code Workflow. Hermes is the orchestrator and will verify your output.
Do not commit, push, or publish unless the brief explicitly says so.

Repository: <absolute path>
Session: <session identifier>
Mode: analyze | implement | review

## Goal

<one precise sentence describing what success looks like>

## Environment Context

- Branch: <current branch>
- Language/runtime: <primary language and version>
- Build tool: <build command>
- Test command: <test command>
- Lint/format command: <command or "none">

## Relevant Files

<list every file the worker should read or modify, with absolute paths>
<if discovery is needed, state exactly what to search for and where>

## Constraints

- Only modify files listed above unless discovery reveals a necessary dependency; if so, list it in your output.
- Follow project conventions for naming, structure, and error handling.
- <project-specific style rules, if any>
- <forbidden areas: generated code, vendored dependencies, lock files, etc.>

## Acceptance Checks

<list concrete commands the worker must run and what success looks like for each>
Example:
- `npm run build` exits 0 with no errors
- `pytest tests/test_auth.py` exits 0 with 0 failures
- Diff touches only files under src/auth/

## Required Output

When finished, produce this exact structure:

- **summary**: one paragraph describing what was done
- **files changed**: list of file paths with one-line description per file
- **checks run**: each command executed, its exit code, and outcome (pass/fail)
- **evidence**: paste the last 10 lines of test or build output showing the result
- **blockers**: anything that prevented full completion, with what was attempted and what actually happened
- **risks**: anything the orchestrator should verify or watch for

If you cannot complete a step, report what you tried, the exact error, and what you believe is needed. Do not skip silently.

## When Stuck

1. Report the blocker with the exact error message or unexpected behavior.
2. State what you tried and why you expected it to work.
3. Propose one or two next steps.
4. Do not guess or patch blindly; the orchestrator will decide how to proceed.
```

### Brief quality checklist (Hermes checks before dispatch)

- [ ] Every bracket in the template above is filled with a concrete value
- [ ] Goal is one sentence, testable, and scoped to what the worker can observe
- [ ] Relevant files list is complete; no discovery left implicit
- [ ] Acceptance checks are runnable commands, not vague descriptions
- [ ] Constraints call out every forbidden directory or file pattern
- [ ] No secrets, tokens, or environment variables are embedded in the brief

## Dispatch Brief Tiering

Hermes chooses between two brief tiers based on task complexity. The tier decision is made before filling the template.

### Mini brief — use when ALL of these hold

- Single file or at most two closely related files
- Goal fits in one sentence with no open design questions
- No architectural decision or dependency trade-off
- Acceptance checks are one or two commands at most
- Risk is low: no security, data-migration, or public-facing contract change

What the mini brief **omits** compared to the standard brief:

| Section | Mini brief treatment |
|---------|---------------------|
| Environment Context | Omit build tool, lint command, and language/runtime if the worker can infer them from the repo |
| Relevant Files | May list a single file or directory instead of every path |
| Constraints | May collapse to one line: "Follow existing project conventions. Only modify files listed above." |
| Required Output | May reduce to: summary, files changed, checks run, evidence |
| When Stuck | May omit entirely for trivial tasks |

The mini brief **always** includes: Repository, Session, Mode, Goal, and Acceptance Checks. These five fields are never optional.

### Standard brief — use for everything else

Use the full template defined above. When in doubt, use the standard brief; a slightly longer brief costs less than a failed dispatch and repair loop.

### Tier selection rules

1. If the quick chain is the intended chain, default to mini brief.
2. If brainstorm was required, default to standard brief.
3. If the worker is in `review` mode and the diff is small (under 50 lines), a mini brief is acceptable.
4. If the task involves more than two files, always use the standard brief.
5. If the task touches security-sensitive code, always use the standard brief with the full Constraints section.

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

### Red flags — STOP

| Claim | Requires | Not sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Agent completed | version control system diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

### Verification mapping — claim to evidence

| Claim type | Hermes must run | Acceptable evidence |
|---|---|---|
| Tests pass | The test command from the brief (e.g. `npm test`, `pytest`) | Exit code 0, zero failures, output matches expected count |
| Build succeeds | The build command from the brief (e.g. `npm run build`, `cargo build`) | Exit code 0, no errors in stderr or stdout |
| Lint/format clean | The lint or format-check command | Exit code 0, no warnings or errors reported |
| Bug is fixed | A reproduction command or test that previously failed | Exit code 0, output no longer shows the original symptom |
| Files changed as expected | `git diff --name-only` | Only files listed in the brief appear; no unintended additions or deletions |
| No secrets in diff | `git diff` scan for token/key patterns | No matches for common secret patterns (API keys, passwords, tokens) |
| Feature works end-to-end | The acceptance check commands from the brief | All commands exit 0 with expected output |
| Dependency install succeeds | Package manager install command | Exit code 0, lock file updated if applicable |

If a claim type is not listed above, Hermes must define the verification command before accepting the claim.

If verification fails, use an iterative repair loop with the concrete failure message.

## Review Gate

For non-trivial code changes, use two review dimensions (inspired by Superpowers two-stage review):

1. **Spec compliance:** Does the implementation satisfy the stated goal and constraints? No over-building, no missing requirements.
2. **Code quality:** Is it maintainable, safe, idiomatic, tested, and scoped?

Use separate workers or separate review passes when possible. Spec compliance must pass before code quality review begins.

### Spec compliance checklist (run first; must pass before code quality review)

```markdown
## Spec Compliance Review

Reviewer: <worker or Hermes>
Session: <session identifier>
Brief goal: <copy the one-sentence goal from the brief>

### Goal coverage

- [ ] Every acceptance check in the brief was run and passes
- [ ] The implemented behavior matches the stated goal — not more, not less
- [ ] No requirements from the brief are missing

### Scope discipline

- [ ] Only files listed in the brief (or justified dependencies) were modified
- [ ] No unrelated refactors, style changes, or "while I was here" edits
- [ ] No new dependencies added without being listed in constraints

### Constraint adherence

- [ ] Every constraint from the brief is satisfied
- [ ] Forbidden files, directories, or patterns were not touched
- [ ] Project-specific style rules (if any) were followed

### Acceptance evidence

- [ ] Worker pasted command output (not a summary) for every acceptance check
- [ ] Exit codes match what Hermes observes when re-running the same commands
- [ ] No placeholder or stale evidence (output is from this run, not a previous one)

### Verdict

PASS — proceed to code quality review.
FAIL — return specific gaps with line references to the implementer for repair.
```

### Code quality checklist (run after spec compliance passes)

```markdown
## Code Quality Review

Reviewer: <worker or Hermes>
Session: <session identifier>

### Correctness

- [ ] Logic is correct for all expected inputs and edge cases
- [ ] Error handling is explicit — no silent swallowing, no empty catch blocks
- [ ] No hardcoded secrets, credentials, or tokens

### Safety

- [ ] User input is validated at system boundaries
- [ ] No injection risks (command, SQL, path traversal, cross-site scripting)
- [ ] No unsafe type casts, unchecked array access, or off-by-one errors in security-sensitive paths

### Maintainability

- [ ] Functions are focused (under 50 lines preferred)
- [ ] Files are cohesive (under 800 lines preferred)
- [ ] No deep nesting (under 5 levels)
- [ ] Names are descriptive; no single-letter variables outside loops
- [ ] No dead code, commented-out blocks, or debug statements left behind

### Testing

- [ ] New or changed logic has test coverage
- [ ] Tests cover the happy path and at least one failure or edge case
- [ ] Tests are deterministic — no reliance on external state, order, or timing

### Verdict

PASS — implementation is ready for final report.
FAIL — return issues to the implementer. If issues are low severity and the user wants speed, flag them as known and proceed.
```

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
- Keep Hermes Code Workflow itself generic; put project-specific conventions in project docs or separate skills.

## Common Pitfalls

1. **Letting a worker self-certify.** Worker success is input to verification, not proof.
2. **Skipping context discovery.** Always inspect enough repo state to avoid wrong assumptions.
3. **Skipping brainstorm phase.** "Simple" projects are where unexamined assumptions cause the most wasted work.
4. **Over-orchestrating tiny tasks.** Use the quick chain when the scope is small.
5. **Under-orchestrating risky work.** Use plan/review/verification gates for production, security, data, and deployment changes.
6. **Mixing local artifacts into commits.** Keep Hermes Code Workflow session files, helper scripts, and plans uncommitted unless approved.
7. **Using vague prompts.** Give workers exact goals, paths, constraints, and checks.
8. **Treating Agent Client Protocol/software development kit/command-line interface as equivalent.** Pick the transport based on reliability, observability, and official support.
9. **Trusting agent success reports.** Always verify independently.
10. **Starting code quality review before spec compliance passes.** Wrong order — spec first, quality second.

## Verification Checklist

### Pre-dispatch (before sending the brief)

- [ ] Relevant skills loaded before acting
- [ ] Intent classified and chain selected
- [ ] Brainstorm phase completed for non-trivial work (design approved)
- [ ] Worker transport chosen deliberately: Agent Client Protocol, official software development kit/command-line interface, or Hermes-native
- [ ] Brief passes the [brief quality checklist](#brief-quality-checklist-hermes-checks-before-dispatch) above
- [ ] Every acceptance check in the brief is a runnable command with a defined pass condition
- [ ] Session artifact directory created

### Post-dispatch (after receiving worker output)

- [ ] Worker output includes all required fields: summary, files changed, checks run, evidence, blockers, risks
- [ ] `git status --short` reviewed; no unexpected files staged or modified
- [ ] Diff reviewed for scope: only intended files changed, no unintended deletions or additions
- [ ] Every acceptance check from the brief was actually run; exit codes and output match claimed results
- [ ] Evidence lines pasted by the worker match what Hermes observes when re-running the same command
- [ ] No secrets, tokens, or credentials appear in the diff or worker output
- [ ] Build/test/lint (or equivalent validation) confirmed by Hermes independently, not trusted from worker report alone
- [ ] Failed validation triggers a focused repair loop with the concrete failure message, not a re-dispatch of the full brief
- [ ] Two-stage review completed for non-trivial changes: spec compliance first, code quality second
- [ ] Final report states files changed, checks run with exit codes, overall result, and remaining risks
