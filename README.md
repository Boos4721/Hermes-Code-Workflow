# Hermes Code Workflow

Language: English | [中文版](README.zh-CN.md)

Hermes Code Workflow is a practical software development workflow for Hermes Agent.

The purpose is simple: Hermes plans, coordinates, verifies, and reports. Coding workers such as Claude Code, Codex, OpenCode, Gemini, and other agent processes perform bounded implementation, analysis, testing, or review work.

## Start here

If you only read three things, read these:

- [Quick Start](docs/quick-start.md) — get the workflow running in about five minutes
- [Full Demo](docs/full-demo.md) — see the end-to-end loop from request to verified final report
- [Real-World Use Cases](docs/real-world-use-cases.md) — understand where HCW is actually useful in day-to-day work

These three documents are the fastest path from “this looks professional” to “I know how to use it”.

## 30-second demo

This is the shortest possible picture of how HCW feels in practice:

```bash
$ python3 scripts/hcw_session.py create --repo . --goal "Improve login error handling"
Created session: .hcw/sessions/HCW-20260430-041500

$ python3 scripts/hcw_dispatch.py templates/brief.example.json --dry-run
Brief valid. Recommended chain: plan-execute

$ python3 scripts/hcw_verify.py --repo . --command "python3 -m py_compile scripts/*.py"
PASS: exit_code=0

$ python3 scripts/hcw_summarize.py .hcw/sessions/HCW-20260430-041500
Generated final report from session artifacts
```

In one glance, you can see the whole loop:

- create a session
- prepare or validate a bounded brief
- verify with real commands
- generate a final report from artifacts

## Why this exists

Modern coding work often involves more than one assistant or command-line coding tool. Without a clear workflow, agents can edit too broadly, skip tests, claim success without proof, or lose context between sessions.

Hermes Code Workflow makes the process explicit:

1. Understand the request and risk.
2. Brainstorm alternatives when the task is not trivial.
3. Write a plan with acceptance criteria.
4. Dispatch a bounded worker brief.
5. Prefer test-first development for new logic and bug fixes.
6. Review non-trivial changes independently.
7. Verify with real commands and file inspection.
8. Report changed files, checks, risks, and follow-up work.

## What you can do with it

Hermes Code Workflow is especially useful when you want to:

- fix bugs without letting a worker over-edit the codebase;
- implement small features with explicit acceptance checks;
- separate implementation from review;
- verify worker claims with real commands;
- coordinate multiple coding workers while keeping Hermes as the orchestrator.

For concrete examples, see [Real-World Use Cases](docs/real-world-use-cases.md).

## Recommended reading order

1. [Quick Start](docs/quick-start.md)
2. [Full Demo](docs/full-demo.md)
3. [Real-World Use Cases](docs/real-world-use-cases.md)
4. [Demo Session Artifacts](docs/demo-session/README.md)

## Installation

Hermes Code Workflow has one required layer and one recommended enhancement layer.

### Install in Hermes Agent

Install the skill into Hermes so Hermes itself can use the workflow.

#### Option 1: install from a hosted SKILL.md URL

```bash
hermes skills install https://raw.githubusercontent.com/Boos4721/Hermes-Code-Workflow/master/skills/hcw/SKILL.md
```

#### Option 2: install from a local checkout

Hermes `skills install` currently accepts a hub identifier or an HTTP(S) URL, not a local file path. For a local checkout, copy the skill into your Hermes skills directory:

```bash
mkdir -p ~/.hermes/skills/software-development/hcw
cp skills/hcw/SKILL.md ~/.hermes/skills/software-development/hcw/SKILL.md
```

Then verify it is available:

```bash
hermes skills list | grep -i hcw
```

This is enough to use the workflow from Hermes: Hermes can brainstorm, plan, dispatch workers, run Python adapters, verify evidence, and report results.

### Recommended enhancement in Claude Code

For best results, also install these three Claude Code ecosystem workflows in the Claude Code environment:

- Claude Code Workflow
- Everything Claude Code
- Superpowers

They are not hard dependencies of Hermes Code Workflow. They are recommended because Claude Code itself will better understand chain execution, command and rule layering, test-first discipline, review gates, and verification-before-completion when Hermes delegates coding work to it.

Practical recommendation:

1. Install Hermes Code Workflow in Hermes Agent.
2. Install Claude Code Workflow, Everything Claude Code, and Superpowers in Claude Code.
3. Let Hermes remain the planner, router, verifier, and reporter.
4. Let Claude Code and other workers execute bounded coding or review tasks.

## Repository contents

- `.github/workflows/skill-review.yml`
  - Pull request review workflow for changes to `SKILL.md` files.
- `README.md`
  - English project introduction.
- `README.zh-CN.md`
  - Chinese project introduction.
- `docs/quick-start.md`
  - Fastest path to first success.
- `docs/full-demo.md`
  - End-to-end walkthrough of the full workflow loop.
- `docs/real-world-use-cases.md`
  - Practical scenarios for adoption and evaluation.
- `docs/demo-session/README.md`
  - Artifact-level example session walkthrough.
- `skills/hcw/SKILL.md`
  - Main Hermes skill definition, including chain selection guidance, brainstorm and repair-loop guards, brief tiering, review templates, and practical orchestration heuristics.
- `skills/hcw/references/python-adapters.md`
  - Python adapter reference with dispatch, verification, session, and summarization conventions aligned to the current workflow.
- `templates/brief.example.json`
  - Example bounded worker brief that includes `tier`, environment context, constraints, and acceptance checks.
- `scripts/hcw_session.py`
  - Create, inspect, and append events to local workflow session artifacts.
- `scripts/hcw_verify.py`
  - Run verification commands, diff-scope checks, and secret scanning, then emit structured evidence in JavaScript Object Notation.
- `scripts/hcw_dispatch.py`
  - Validate a mini or standard brief, build a worker prompt, and dispatch a bounded task to a supported worker command.
- `scripts/hcw_summarize.py`
  - Summarize workflow artifacts into a final report draft.

## Workflow heuristics and enforcement

The workflow now includes practical decision rules so Hermes can operate more consistently:

- **Chain selection guidance**
  - A decision aid and a weighted heuristic help choose between quick, plan-execute, test-first development, multi-worker, subagent-driven, debug, and ship chains.
- **Brainstorm guardrails**
  - Clear skip criteria, done criteria, and hard termination guards prevent brainstorm loops from dragging on without resolution.
- **Repair-loop guardrails**
  - Focused repair rounds are capped, regressions are tracked separately, and no-progress detection stops repeated ineffective retries.
- **Dispatch brief tiering**
  - Hermes can choose between `mini` and `standard` briefs depending on scope, risk, and review needs.
- **Review and verification discipline**
  - Spec compliance review comes before code quality review, and claim-to-evidence mappings make verification more operational.
- **Recursive decomposition and depth limits**
  - Large tasks can be split into independently verifiable sub-tasks, while orchestration depth is capped by risk so the workflow does not over-nest.

## Scripted workflow support

The repository scripts are designed to mirror the workflow rules in `SKILL.md`:

- `hcw_dispatch.py`
  - Validates brief structure, auto-detects mini versus standard tier when needed, and emits prompts that match the current dispatch template. Also computes a weighted chain-selection score and lightweight decomposition hints so Hermes can make routing decisions before dispatch.
- `hcw_verify.py`
  - Records structured verification events, supports command-based evidence, optional diff-scope enforcement, and secret scanning on diffs. Verification levels (shallow, standard, deep) control output detail, and expect-pattern matching can assert specific patterns in command output.
- `hcw_session.py`
  - Maintains session artifacts under `.hcw/sessions/...` for plans, verification output, and event history.
- `hcw_summarize.py`
  - Converts collected artifacts into a concise final report draft for Hermes to review before reporting upstream.

## Relationship to reference workflows

Hermes Code Workflow learns from three systems but is not a copy of them.

- Claude Code Workflow contributes intent classification, chain selection, wave execution, session artifacts, and command-line orchestration ideas.
- Everything Claude Code contributes harness performance thinking, command and rule layering, verification loops, and cross-agent packaging ideas.
- Superpowers contributes strong workflow discipline: brainstorm, plan, execute, test-first development, systematic debugging, independent review, and verification before completion.

## Worker model

Hermes Code Workflow separates orchestration from execution.

- Hermes Agent
  - Plans the task.
  - Chooses the worker.
  - Writes the task brief.
  - Verifies the result.
  - Reports to the user.

- Claude Code
  - Default implementation worker for coding-heavy tasks.

- Codex
  - Useful for independent implementation, review, or second opinion.

- OpenCode
  - Useful as a provider-independent coding worker or fallback.

- Gemini
  - Useful for broad analysis, architecture discussion, diagnosis, and Agent Client Protocol style execution when available.

## Python adapter layer

The `scripts/` directory provides small Python utilities that make worker orchestration easier to observe and verify.

Python adapters should:

- read task briefs written in JavaScript Object Notation;
- run a selected command or verification check;
- capture exit codes, standard output, and standard error;
- write structured event records;
- avoid secrets in logs;
- keep dispatch and verification separate.

## Example session

Create a session:

```bash
python3 scripts/hcw_session.py create --repo . --goal "Improve login error handling"
```

Run verification:

```bash
python3 scripts/hcw_verify.py --session .hcw/sessions/<session-id> --command "npm test" --command "npm run build"
```

Dispatch a worker from a task brief:

```bash
python3 scripts/hcw_dispatch.py templates/brief.example.json
```

Summarize artifacts:

```bash
python3 scripts/hcw_summarize.py .hcw/sessions/<session-id>
```

See `docs/demo-session/` for a concrete end-to-end example session with sample artifacts, a worker brief, verification evidence, and a final report.

## Completion standard

A task is not complete because a worker says it is complete.

A task is complete only when Hermes has verified the result with evidence.

The final report should include:

- files changed;
- commands run;
- command results;
- skipped checks and reasons;
- known risks;
- follow-up recommendations.
