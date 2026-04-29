# Hermes Code Workflow

Language: English | [中文版](README.zh-CN.md)

Hermes Code Workflow is a practical software development workflow for Hermes Agent.

The purpose is simple: Hermes plans, coordinates, verifies, and reports. Coding workers such as Claude Code, Codex, OpenCode, Gemini command-line interface, and other agent processes perform bounded implementation, analysis, testing, or review work.

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

## Installation model

Hermes Code Workflow has one required layer and one recommended enhancement layer.

### Required in Hermes Agent

Install Hermes Code Workflow as a Hermes skill. This is enough to use the workflow from Hermes: Hermes can brainstorm, plan, dispatch workers, run Python adapters, verify evidence, and report results.

### Recommended in Claude Code

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

- `README.md`
  - English project introduction.
- `README.zh-CN.md`
  - Chinese project introduction.
- `skills/hcw/SKILL.md`
  - Main Hermes skill definition.
- `skills/hcw/references/python-adapters.md`
  - Design notes for Python adapters that connect Hermes with command-line tools, software development kits, and agent processes.
- `templates/brief.example.json`
  - Example task brief for dispatching a bounded worker job.
- `scripts/hcw_session.py`
  - Create, inspect, and append events to local workflow session artifacts.
- `scripts/hcw_verify.py`
  - Run verification commands and emit structured evidence in JavaScript Object Notation.
- `scripts/hcw_dispatch.py`
  - Dispatch a bounded task brief to a supported worker command.
- `scripts/hcw_summarize.py`
  - Summarize workflow artifacts into a final report draft.

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

- Gemini command-line interface
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
