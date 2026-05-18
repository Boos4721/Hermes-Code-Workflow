---
name: hcw
description: "Use when coordinating coding work through Hermes Code Workflow: brainstorm designs, classify intent, route work to Claude Code, Codex, OpenCode, Gemini, or Agent Client Protocol workers, run Python adapters when useful, verify outputs with evidence, and iterate before reporting."
version: 0.4.0
author: Boos4721 + Hermes
license: MIT
metadata:
  hermes:
    tags: [workflow, orchestration, multi-agent, coding, verification, agent-client-protocol, software-development-kit, python, brainstorm]
    related_skills: [hermes-agent, claude-code, codex, opencode, hermes-agent-skill-authoring]
---

# Hermes Code Workflow

## Related House Workflows

### CCW as historical sibling
A narrower sibling once focused on Claude-Code-centric workflow patterns. Treat that material as part of the broader Hermes Code Workflow class rather than a separate discoverability target. If you encounter a `ccw` artifact in the user-local skill tree, absorb any unique heuristics into this section or a support file and archive the narrow sibling.

### Multi-agent workflow notes
Use this umbrella alongside `multi-agent-dev-workflow` / `subagent-driven-development` style support material when the task is specifically about delegation topology or review stages, but keep the main discoverability surface here at the class level.

##

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
- coordinate multiple workers such as Claude Code, Codex, OpenCode, Gemini, Qwen, or other Agent Client Protocol/software development kit agents
- create a repeatable workflow rather than a one-off manual edit
- compare multiple implementations or ask one worker to review another
- turn a vague request into a plan, execution pass, validation loop, and final report

Do not use Hermes Code Workflow as a substitute for explicit user approval on risky actions. If the next step is destructive, deploys to production, exposes credentials, force-pushes, or commits files the user has marked local-only, stop and confirm scope.

## Roles

### Human partner

- defines goals and final preferences
- approves high-risk changes and publishing decisions
- can override this workflow at any time

**⚠️ Publishing rule (user correction):** NEVER auto-publish content (articles, posts, social media) without explicit user confirmation. Always preview first, wait for "发"/"ok"/"publish", then publish to draft — not directly to production. User has been burned by auto-publishing resulting in published content that couldn't be easily modified.

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

1. **Explore project context** — check files, docs, recent commits, existing patterns. For deeper context, see [huashu methodology: deep context gathering](references/huashu-methodology.md#pattern-1-deep-context-gathering) — scan for exact config values, architecture markers, entry points, and dependency descriptors.
2. **Ask clarifying questions** — one at a time, prefer multiple choice, understand purpose/constraints/success criteria
3. **Propose 2-3 approaches** — with trade-offs and your recommendation. Use [huashu methodology: variations by dimension](references/huashu-methodology.md#pattern-3-variations-by-dimension) to ensure each approach explores a distinct architectural axis, not just cosmetic differences.
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

### Brainstorm termination guard

Brainstorm must not loop indefinitely. Apply these hard stops:

- **Question round limit.** After 5 rounds of clarifying questions without reaching done criteria, stop. Present the human partner with a summary of what is resolved, what remains open, and a recommended default for each open item. Ask the partner to decide: accept defaults, answer remaining questions, or simplify scope.
- **Time budget.** If the brainstorm phase has consumed more than 15 minutes of wall-clock time (or 20 conversational turns), pause and present the same summary. The partner may extend, simplify, or cancel.
- **Repeated question detection.** If the same question is asked twice without a new answer, Hermes must stop and propose a default instead of asking again.
- **Scope growth detection.** If the scope has grown by more than 50% compared to the original request (measured by number of files, components, or acceptance checks), stop and ask the partner whether to split into multiple sessions.

When any termination guard triggers, Hermes must not silently continue. Present the state and let the partner choose the next action.

### Repair-loop termination guard

Repair loops in the dispatch-verify-iterate cycle are bounded:

- **Maximum repair rounds.** Three rounds per failure type. A "round" is one dispatch of a focused repair brief followed by one verification attempt. After three rounds on the same failure, escalate to the human partner with a summary: original failure, what each round tried, and the persistent symptom.
- **Regression detection.** If a repair round fixes the original failure but introduces a new failure in a previously passing check, count that as a new failure type with its own three-round budget. If two or more regressions accumulate, stop and escalate.
- **No-progress detection.** If two consecutive repair rounds produce identical verification output (same error message, same exit code, same failure line), stop immediately. Repeating the same repair is a signal that the brief or approach is wrong, not that more attempts will help.
- **Total repair budget.** Across all failure types, a session must not exceed 8 total repair rounds. After 8 rounds, escalate regardless of progress.

When escalating, include: the original goal, each failure type encountered, what was tried per round, and what verification evidence was collected.

### Brainstorm output

```text
.hcw/sessions/<session-id>/
  design.md          # approved design spec
  plan.md            # implementation plan (after brainstorm)
```

### Automation: Design Agent script

For projects that include HCW's `scripts/` directory, use `hcw_design.py` to automate the design phase.
The script implements patterns from [huashu-design methodology](references/huashu-methodology.md):
deep context scanning, variations by architectural dimension, Junior Designer assumptions,
structured 5-dimension critique with Quick Wins.

```bash
# 1. Create design session with goal + constraints
python3 scripts/hcw_design.py init \
  --goal "Add rate limiting to gateway" \
  --constraints "Must use Redis" "Must not add latency"

# 2. Scan codebase for structure, languages, entry points
python3 scripts/hcw_design.py explore --dir . --session .hcw/sessions/<id>

# 3. Generate 2-3 design proposals with trade-off stubs
python3 scripts/hcw_design.py propose \
  --goal "Add rate limiting" --approaches 2 --session .hcw/sessions/<id>

# 4. Produce final design.md from artifacts
python3 scripts/hcw_design.py finalize \
  --session .hcw/sessions/<id> \
  --scope "gateway/middleware/ratelimit.py" \
  --criteria "pytest tests/test_ratelimit.py"

# 5. Review design.md for completeness (8 checks)
python3 scripts/hcw_design.py review --design .hcw/sessions/<id>/design.md
```

Also see `templates/design.template.md` for a standalone design-document template.

### Visual Design: huashu-design integration

When the task is UI/UX prototype, slide deck, animation, infographic, or design critique,
the submodule at `skills/huashu-design/` provides a complete visual design skill.
Use `hcw_design.py visual` to create structured briefs:

```bash
# List 7 available capabilities
python3 scripts/hcw_design.py visual --list-capabilities --goal x

# List 5 schools × 20 design philosophies
python3 scripts/hcw_design.py visual --list-styles --goal x

# Create session + print agent-ready brief
python3 scripts/hcw_design.py visual \
  --goal "跑步记录 App 原型, 5 屏, iOS" \
  --capability prototype \
  --style "Kenya Hara" \
  --print-brief
```

Capabilities: `prototype` (interactive HTML), `slides` (HTML deck + PPTX),
`animation` (MP4 + GIF + BGM), `variations` (side-by-side + Tweaks),
`infographic` (PDF/PNG/SVG), `direction` (3 parallel direction demos),
`critique` (5-dim radar chart with quick wins).

Requirements: `git submodule update --init skills/huashu-design` to clone the submodule.
Methodology patterns (deep context, Junior Designer, 5-dim critique) documented in
`references/huashu-methodology.md`.

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

- **Model dispatch** — calling a specific model (e.g. gpt-5.5) when the session model is wrong. See `references/model-dispatch-python-adapter.md` for the full recipe.
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
  hcw_design.py        # automated design phase: explore, propose, review, finalize
  hcw_summarize.py     # summarize artifacts for final report
```

See `references/model-dispatch-python-adapter.md` for the model-dispatch adapter pattern (calling a specific model when the session model is wrong). See `references/huashu-methodology.md` for scaffolded design-agent adapters.

### Dispatching to a specific model via Python adapter

When Hermes is running on model X but the task explicitly requires model Y (user preference, special capability, cost constraint), use a Python adapter to call the target model's API directly — do not use the session's model as a fallback.

**When to use this pattern:**
- The user says "用 <model>" and that model differs from the session model
- Worker CLIs (Codex, Claude Code, OpenCode) don't support the target API endpoint
- The task is prompt-based (document rewrite, analysis, generation) — not code execution
- You've been corrected for using the wrong model earlier in the session

**Procedure:**
1. Discover available models via `GET /v1/models` with the user's API key
2. Test with a minimal prompt before the full task (saves minutes on bad model names)
3. Write a Python adapter using stdlib `urllib` (no pip needed) — see `references/model-dispatch-python-adapter.md` for a complete recipe
4. Run via `execute_code` (clean, isolated, no side effects)
5. Verify output quality before claiming completion

**Key constraint:** The adapter is for prompt-based LLM work. For code-heavy tasks (builds, tests, multi-file changes), use existing worker CLIs. If no CLI supports the required model, decompose the task: use Hermes for prompts and CLI workers for code.

## Default Routing

Unless the user explicitly chooses a worker:

1. **Implementation-heavy work:** route first to Claude Code.
2. **Architecture, diagnosis, broad analysis:** route to Gemini/Agent Client Protocol or a Hermes reasoning subagent, then hand implementation to Claude Code.
3. **Second opinion / review:** route to Codex or OpenCode.
4. **Provider fallback:** if one worker fails due to quota/provider/runtime issues, switch worker and preserve artifacts.
5. **Final acceptance:** Hermes verifies directly.

### Greenfield project bootstrap under HCW

When the user asks to create a brand-new project from an existing upstream implementation or reference repo, treat it as a **plan-execute chain with mandatory brainstorm** even if the end goal sounds straightforward.

Required sequence:

1. Inspect the upstream/reference repo directly with tools before proposing architecture.
2. Create the target project directory immediately when the user has already named it and there is no destructive ambiguity.
3. Save a concrete implementation plan under the new project's local planning path, for example `docs/plans/...`.
4. Prefer a **first-pass parity port** before cleanup when the user explicitly wants a reimplementation of an existing tool. Preserve behavior first; refactor second.
5. Be explicit about the verification boundary. For exploit, privilege, kernel, or destructive tooling, distinguish:
   - build/test verification you can safely run now
   - live runtime validation you are intentionally not executing
6. If subagents are used in parallel on the same new repo, reconcile their outputs against the actual working tree before reporting status. Do not trust a subagent summary that says the repo is still scaffold-only once local file inspection shows implementation landed.

Recommended user-choice frame when the target is a port/rewrite:
- A: 1:1 behavior-first port
- B: idiomatic rewrite with behavior parity
- C: minimal single-arch/single-mode starter
- D: 1:1 first, then refactor

Default recommendation: **D** when the user wants an HCW-style implementation of an existing upstream tool and future cleanup is acceptable.

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

### Chain-selection scoring heuristic

When the decision matrix above does not produce a clear winner, score each candidate chain on four dimensions. Weights reflect operational impact: getting the chain wrong on a high-risk task costs more than picking a slightly slower chain on a trivial one.

| Dimension | Weight | What to measure |
|-----------|--------|-----------------|
| Risk | 0.35 | Security, data integrity, public-facing contract, production deployment. Low = 1, Medium = 2, High = 3. |
| Scope | 0.25 | Number of files and cross-module dependencies. 1 file = 1, 2-3 files = 2, 4+ files or cross-module = 3. |
| Test leverage | 0.20 | How much value tests add. No meaningful tests = 1, regression guard = 2, core correctness proof = 3. |
| Parallelism | 0.20 | Number of independent sub-tasks. Single task = 1, 2 tasks = 2, 3+ independent tasks = 3. |

Score formula: `score = 0.35 * risk + 0.25 * scope + 0.20 * test_leverage + 0.20 * parallelism`

| Score range | Recommended chain |
|-------------|-------------------|
| 1.0 -- 1.5 | Quick chain |
| 1.6 -- 2.1 | Plan-execute chain |
| 2.2 -- 2.6 | Plan-execute with test-first development embedded |
| 2.7 -- 3.0 | Multi-worker chain or subagent-driven chain |

Tie-breaking: when two chains score within 0.3 of each other, prefer the chain with more verification stages. When the risk dimension alone is 3 (high), always use at least plan-execute regardless of the total score.

### Recursive decomposition heuristic

When a task is too large for a single worker dispatch, decompose it. Use these thresholds to decide when decomposition is needed and when to stop:

**Decompose when any of these hold:**

- The plan has more than 7 discrete steps.
- The brief would need to list more than 10 relevant files.
- The estimated worker time exceeds 20 minutes (or 30 conversational turns).
- The task spans more than two distinct programming languages or frameworks.
- The acceptance checks require more than 5 distinct commands.

**Decomposition procedure:**

1. Split along module, file-group, or concern boundaries — not along temporal steps.
2. Each sub-task must have its own goal sentence, relevant files list, and acceptance checks.
3. Sub-tasks should be independently verifiable. If sub-task B cannot be verified without sub-task A completing first, they are sequential steps, not decomposition targets.
4. Target 3-7 sub-tasks per decomposition. Fewer than 3 means the task was not actually too large. More than 7 means the decomposition itself needs further splitting.

**Stop decomposing when:**

- Each sub-task fits within a single mini brief (1-2 files, one sentence goal, 1-2 acceptance checks).
- The sub-task can be completed by one worker in under 10 minutes.
- Further splitting would create sub-tasks with no independent verification value.

**Decomposition output format:**

```text
.hcw/sessions/<session-id>/
  decomposition.md    # list of sub-tasks with dependencies, ordering, and per-task acceptance checks
```

### Orchestration depth limit

Orchestration depth is the number of nested delegation layers: Hermes dispatches a worker, which may internally spawn subagents, which may spawn further subagents. Depth is measured from the original user request to the leaf worker.

| Task risk | Maximum depth | Rationale |
|-----------|---------------|-----------|
| Low | 3 layers | Simple tasks need minimal delegation overhead. |
| Medium | 4 layers | Multi-step work may need subagent splitting. |
| High | 5 layers | Complex, high-stakes work benefits from deep specialization, but each layer adds verification cost. |

**Depth counting rules:**

- Hermes dispatching a worker counts as layer 1.
- A worker spawning a subagent counts as layer 2, and so on.
- Hermes-native tool calls (read_file, search_files, terminal) do not count as depth layers — they are direct actions, not delegation.
- Parallel dispatches at the same depth count as one layer, not one per dispatch.

**When the depth limit is reached:**

- Do not spawn another delegation layer. Instead, the current worker must complete the task using its own tools and reasoning.
- If the worker cannot proceed without deeper delegation, it must report this as a blocker with the specific capability gap.
- Hermes may then restructure the task (re-decompose, change chain, or escalate to the human partner).

**Depth escalation path:**

If a task's natural decomposition requires more depth than the risk level allows, Hermes should either:
- Increase the risk classification (and document why), or
- Flatten the decomposition (merge sub-tasks to reduce nesting), or
- Escalate to the human partner with a recommendation.

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

### Design session artifacts (when using hcw_design.py)

When the design phase runs before implementation, it produces its own session tree that feeds into the implementation session above:

```text
.hcw/sessions/DSN-YYYYMMDD-HHMMSS/
  manifest.json       # goal, context, constraints, status
  events.jsonl        # design event log
  exploration/
    codebase.json     # codebase scan: structure, languages, entry points
  proposals.json      # 2-3 design approaches with trade-offs
  review.json         # review verdict and check results
  design.md           # final design document
```

If a project already has an established planning/session directory, use that instead. Do not commit Hermes Code Workflow artifacts unless the user asks.

## Agent Development Brief (multi-phase, agent-to-agent handoff)

For large-scale rewrites, ports, or greenfield builds that span multiple phases and will be handed to another agent for execution, use **Agent Development Brief** format — not the standard Dispatch Brief.

### When to use

- Full-stack rewrite (e.g., Node.js → Go backend)
- Multi-month refactoring projects
- Any task the user says "给agent去开发" or explicitly wants a self-contained document for another agent
- Projects requiring from-scratch setup instructions

### Format differences from standard brief

| Dimension | Standard Brief | Agent Development Brief |
|-----------|---------------|------------------------|
| Audience | Subagent in this session | Another agent instance (fresh context) |
| Scope | Single task/phase | Full project, multiple phases |
| Language | User's language (e.g., Chinese) | **English** (user preference: "最好硬英语") |
| Setup | Assumes repo is ready | **From-scratch bootstrap** (clone, build, verify) |
| Detail | Minimal context (goal + files + checks) | Full architecture, interface specs, code templates |
| Tasks | One dispatch unit | Phase-by-phase with 10-60+ tasks |
| Tests | Mentioned as checks | Full test templates with httptest/mock examples |
| Docs | Not included | Documentation requirements per task |

### Required sections

1. **Getting Started (from scratch)** — clone, checkout, build, smoke test, dev loop
2. **Architecture** — ascii/mermaid diagram + directory layout with every file's purpose
3. **Golden Rules** — hard constraints the agent must follow
4. **Phases** — each phase has:
   - Task list with file paths, Go interface signatures, code templates
   - Provider/API priority matrix
   - Testing requirements with examples
5. **Documentation requirements** — GoDoc, API comments, user-facing docs per task
6. **Build & Run** — compile, test, vet, docker commands
7. **Pre-commit checklist** — vet, test, format, secrets scan

### Example

The Go backend rewrite plan at `plan/go-backend-rewrite.md` in the BoosAPI repo demonstrates this format. It includes:
- Bootstrap steps (clone → build → curl healthz)
- 60+ tasks across 5 phases with Go interface signatures
- Provider priority matrix
- httptest test templates
- Documentation requirements per task
- Pre-commit checklist
- All in English

### User preference embed

When the user says "合并成一个文档", "写好提示词", or "给agent去开发":
- Merge all separate plan docs into ONE English markdown file
- Include from-scratch bootstrap steps (clone, install deps, build, smoke test)
- Lead with Golden Rules the agent must follow
- Keep task descriptions concrete (file paths, function signatures, expected output)
- Save as `plan/<descriptive-name>.md` and commit if the user wants it tracked

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

## Chain Selection Scoring Heuristic

Use the decision aid above first. When multiple chains still look plausible, score the task so Hermes has a repeatable tie-breaker.

### Inputs

Rate each dimension from 0 to 3:

- **risk** — security, data, deployment, and public-surface impact
- **scope** — number of files, components, and moving parts
- **test leverage** — how much confidence can be gained from writing or running tests early
- **parallelism** — how naturally the task splits into independent tracks

### Weighted score

```text
score = 0.35 * risk + 0.25 * scope + 0.20 * test_leverage + 0.20 * parallelism
```

### Interpretation

- **0.00-0.90** → quick chain, unless another hard rule forbids it
- **0.91-1.60** → plan-execute chain
- **1.61-2.10** → test-first development chain when tests are meaningful; otherwise plan-execute chain
- **2.11-2.50** → multi-worker chain when a second perspective materially reduces risk
- **2.51-3.00** → subagent-driven chain if the work also decomposes into independent tasks; otherwise multi-worker chain

### Tie-breakers

- If `risk = 3`, never use the quick chain. Minimum chain is plan-execute.
- If two chains are tied, prefer the chain with the stronger verification phase.
- If tests are weak or unavailable, reduce `test leverage` by 1 before final scoring.
- If the user explicitly asks for shipping, the ship chain overrides the score.

## Recursive Decomposition Heuristic

When a task is too large for one bounded worker brief, Hermes should decompose it recursively instead of sending an oversized prompt.

### Trigger conditions

Decompose when **any** of these are true:

- the plan has more than 7 steps
- the likely change touches more than 10 files
- the work is expected to take more than 20 minutes of focused implementation time
- the task spans more than 2 languages, runtimes, or subsystems
- acceptance requires more than 5 commands or observability checks

### Decomposition goals

Split the task into **3 to 7** child tasks where possible. Each child task should have:

- one sentence goal
- bounded file scope
- at least one independent acceptance check
- a clear owner or worker mode

### Stop splitting when

Stop decomposition when **all** of these are true for a child task:

- it is suitable for a mini brief or a narrowly scoped standard brief
- a competent worker could likely finish it in about 10 minutes
- further splitting would not create independently verifiable units

If decomposition still does not yield bounded tasks, escalate to the human partner and propose a narrower milestone.

## Orchestration Depth Limit

Hermes must limit how many orchestration layers a task can accumulate.

### Depth budget by risk

- **low risk** → maximum depth 3
- **medium risk** → maximum depth 4
- **high risk** → maximum depth 5

### Counting rules

- Direct Hermes-native file edits and verification commands do **not** count toward depth.
- A worker dispatched by Hermes counts as **one** layer.
- Parallel workers launched from the same level still count as **one** additional layer.
- Review after implementation counts as another layer only if it is a separately dispatched worker.

### What to do at the limit

When the depth limit is reached:

- do not spawn another worker just to keep the pattern going
- either finish with the current worker set and Hermes-native verification
- or escalate to the human partner with the exact capability gap

Depth limits exist to prevent ornate orchestration from replacing actual progress.

## Learning Loop

After difficult or repeated work:

- Save durable user preferences as memory if they will matter later.
- Save reusable procedures as skills, not memory.
- Patch stale skills immediately when a loaded skill is wrong or incomplete.
- Keep Hermes Code Workflow itself generic; put project-specific conventions in project docs or separate skills.

Project integration patterns (BoosAPI route registration, ComfyUI reverse proxy, Gitea CI/CD, notification service, AI video agent architecture, internal rename, SSE agent pattern, and agent development briefs) are documented in:
- `references/metapi-integration.md` — BoosAPI-specific patterns
- `references/agent-development-brief.md` — agent-to-agent handoff brief format
- `references/model-dispatch-python-adapter.md` — dispatching to a specific LLM model via Python adapter when the session model doesn't match the task requirement

## Common Pitfalls

1. **Letting a worker self-certify.** Worker success is input to verification, not proof.
1b. **Forgetting bilingual docs (zh-CN).** When the user's project maintains `en/zh-CN` doc pairs (README.md + README.zh-CN.md, docs/*.md + docs/*.zh-CN.md), updating only the English variant is an incomplete change. Always mirror the update to the Chinese counterpart in the same commit. This applies to `Hermes-Code-Workflow` and any project that follows the same pattern.
2. **Skipping context discovery.** Always inspect enough repo state to avoid wrong assumptions.
3. **Skipping brainstorm phase.** "Simple" projects are where unexamined assumptions cause the most wasted work.
4. **Over-orchestrating tiny tasks.** Use the quick chain when the scope is small.
5. **Under-orchestrating risky work.** Use plan/review/verification gates for production, security, data, and deployment changes.
6. **Mixing local artifacts into commits.** Keep Hermes Code Workflow session files, helper scripts, and plans uncommitted unless approved.
7. **Using vague prompts.** Give workers exact goals, paths, constraints, and checks.
8. **Treating Agent Client Protocol/software development kit/command-line interface as equivalent.** Pick the transport based on reliability, observability, and official support.
9. **Trusting agent success reports.** Always verify independently.
10. **Starting code quality review before spec compliance passes.** Wrong order — spec first, quality second.
11. **Don't delete apparently-unused files without understanding context.** A file that isn't imported anywhere may still be valuable (Web3 providers, app-wide wrappers, layout components). Before removing, check:
    - Is the file part of a pattern (e.g. providers → layout → app)?
    - Does it export something that could be used dynamically or via config?
    - If unsure, ask the user — do not assume "unused = safe to delete."
    - When you do get corrected, restore the file AND its deps, then build.

12. **Leaking real IPs, names, or credentials in test data.** Never use real IP addresses, hostnames, usernames, or other sensitive identifiers in test code, examples, or YAML configs committed to git. Use placeholder values (10.0.0.x, node-a/node-b, example.com, test-user). If sensitive data was committed:
   - **Single recent commit**: `git commit --amend && git push --force-with-lease`
   - **Multiple commits / full history cleanup**: `git checkout --orphan clean-branch && git add -A && git commit -m "..." && git branch -D main && git branch -m clean-branch main && git push -f origin main` — this creates a single clean commit with no history
    - **Single commit:** `git commit --amend && git push --force-with-lease`
    - **Multiple commits (full history wipe preferred):** `git checkout --orphan clean-branch && git add -A && git commit -m "..." && git branch -D main && git branch -m clean-branch main && git push -f origin main`
    - A new commit on top still exposes the old data in git history — force push is required.

13. **Confusing agent-local plans with team-facing plans.** In projects with a dual-plan convention (e.g. BoosAPI/metapi):
    - `docs/plans/` (gitignored) = agent/developer pre-implementation design, spec, decomposition.
    - `plan/` (committed) = team-facing session summaries, decisions, outcomes — Chinese markdown.
    - When the user says "写进plan", look for a top-level `plan/` directory. When they say "规划" or "设计文档", use `docs/plans/` or `.hcw/sessions/`.
    - If unsure which to use, ask — mixing them up wastes time.

14. **Using the wrong model for HCW tasks.** When Hermes is running on model X but the user's workflow requires model Y, dispatching or executing work with model X is a workflow error — expect a correction. Before dispatching any worker or doing Hermes-native execution, check whether the session model matches the user's expected model for this task. If it doesn't match:
    - Use a Python adapter to call the target model's API directly (see `references/model-dispatch-python-adapter.md`)
    - Do not ask "should I switch models" — figure it out from context or user preference
    - Check User-specific workflow notes below for this user's model preference
    - **Live example of this failure:** user said "等等 怎么是用deepseek-v4写的啊" after HCW dispatched work with the wrong session default instead of gpt-5.5. This is a first-class correction signal — update HCW's model handling if it happens more than once.

## User-specific workflow notes

### Gitea-only project infrastructure

This project runs entirely on self-hosted **Gitea** at `git.boos.lat`. All documentation, plan files, code module paths, Go import paths, and repository URLs must reference the Gitea instance only — never GitHub. When the user says "不要出现github的 只用我们自己的gitea", that means:
- `go.mod` module path: `git.boos.lat/boos/boosapi` (not `github.com/...`)
- All Git remotes: `git.boos.lat/...`
- All documentation URLs: `git.boos.lat/...` or `boosapi.cita777.me`
- Docker images: `1467078763/boosapi` (if on a registry), not `github/...`
- Remove GitHub badges, links, and references from any doc files

### User prefers ultra-brief communication
用户（Boos4721）沟通极端简洁，通常只给几个字（"头脑风暴"、"2 4 主要是4"、"继续弄"）。不需要完整句子解释、也不需要确认性提问。精简所有输出：
- 分析结果直接列要点，不要铺垫
- 选项用编号 1/2/3 而非段落
- 不清楚时先做判断再问，不要把问题抛回去
- 修完直接报结果，不要问"这样可以吗"

### Model preference: gpt-5.5 for HCW tasks

This user expects **gpt-5.5** (via `api.boos.lat/v1`, key `sk-boos4721`) for any development/documentation work dispatched through HCW. If the session model is gpt-5.5, dispatch workers directly. If it is something else (e.g. deepseek-v4-flash, any other default), use the Python adapter pattern (`references/model-dispatch-python-adapter.md`) to call gpt-5.5 directly — do not use the session's model for HCW tasks.

**Live example from this user's sessions:** User said "等等 怎么是用deepseek-v4写的啊" after HCW dispatched work using the session default model instead of gpt-5.5. The fix was a Python adapter calling gpt-5.5 directly via the OpenAI-compatible API at `api.boos.lat/v1`.

### Scope discipline: "全部写完" means ALL items in the plan

When the user says "全部写完" (write all of them), "全部", or references a plan with an expectation of full implementation, implement EVERY outstanding item listed in the plan — do not pick a subset. This user's communication is ultra-brief; if they reference a plan's remaining items list and say "全部写完", they mean implement every uncompleted item, not just the first one or the easiest ones. If the scope is too large for a single session, mention the total items and ask "一个一个来还是全部?" rather than silently choosing a subset.

### High-risk local exploit validation on real hosts

When the user asks to validate a local exploit or privilege-escalation proof of concept on the current machine, do not stop at build success or theoretical analysis. If the user explicitly requests a live test, Hermes should:

1. perform prerequisite environment discovery first:
   - identify the target binary path and whether it is a symlink
   - inspect the live file permissions and readability as the intended unprivileged user
   - check whether the implementation's file-open strategy matches the real target layout
2. create a dedicated unprivileged demo user when safe and appropriate for local testing
3. run the binary as that demo user and collect real evidence
4. if it fails, use `strace` or equivalent syscall tracing to locate the exact failing syscall before proposing fixes
5. report clearly whether the failure is:
   - an implementation bug
   - an environment incompatibility
   - or a target precondition mismatch

Important pitfall discovered in practice:
- On Alpine/BusyBox-style systems, `/bin/su` may be a symlink to `/bin/bbsuid` with mode `4111` (`---s--x--x`), which means an unprivileged user can execute it but cannot open it read-only.
- A copy-fail style implementation that assumes `File::open("/bin/su")` or equivalent `O_RDONLY` access will fail early with `EACCES` before reaching the AF_ALG / `splice` overwrite path.
- In that environment, the right next step is to compare with the reference implementation and/or add explicit preflight checks for target readability and target-path compatibility instead of claiming the exploit path itself failed.

Verification pattern to preserve:
- build the candidate binary
- create a dedicated demo user
- execute the binary as that user against the live target
- if failure occurs, capture the exact syscall transcript showing the failure point
- include the target file mode, symlink resolution, and the failing syscall in the final report


### Gemini dispatch with prompt review

When dispatching Gemini (gemini CLI = Claude Code) for BoosAPI coding tasks:

1. **Prompt must be reviewed.** Before launching Gemini, present the prompt text to the user for approval. Wait for explicit go-ahead before running.
2. **Use pty mode.** Always launch Gemini with `pty=true` and `background=true` — the CLI requires a pseudo-terminal.
3. **Alpine quirk.** Gemini's `run_shell_command` tool is not available on Alpine Linux. If it gets stuck on that error, kill the process and do the remaining fixes manually.
4. **Prompt style.** Keep prompts concise (bullet points), list exact files to modify, and include acceptance checks (e.g. `cargo check`). Gemini has already explored the project structure, so no need to re-explain the full codebase.
5. **Monitor progress.** After dispatching, use `process(action='wait')` or `process(action='poll')` to track progress. Gemini runs can take 2-10 minutes.
6. **Verify after completion.** Always run `cargo check` / `npx tsc --noEmit` after Gemini finishes. Fix any compilation errors it introduced.

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
