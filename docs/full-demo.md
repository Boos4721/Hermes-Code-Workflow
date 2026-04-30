# Full Demo

This document shows the complete Hermes Code Workflow loop from operator intent to final report.

It is the missing middle layer between a short quick start and the lower-level artifact reference in `docs/demo-session/`.

## What this demo answers

If a new user asks:

- What does Hermes actually do?
- Where does the worker fit?
- What gets verified?
- What artifacts are created?
- What does the final output look like?

This demo is the answer.

## The workflow in one picture

1. Hermes receives a coding task.
2. Hermes decides the chain and risk level.
3. Hermes creates a session.
4. Hermes prepares a bounded worker brief.
5. Hermes dispatches a worker.
6. Hermes runs verification.
7. Hermes summarizes artifacts.
8. Hermes reports evidence, risks, and next steps.

## Scenario

We will use a realistic example:

> Improve login error handling in a small Python service.

This is intentionally modest. The goal is to show the workflow shape clearly, not to simulate a giant production incident.

## Phase 1: Create session state

Hermes first creates a session so the work has a durable artifact trail.

```bash
python3 scripts/hcw_session.py create \
  --repo . \
  --goal "Improve login error handling" \
  --risk medium \
  --tier standard \
  --chain plan-execute
```

What this does:

- creates `.hcw/sessions/<session-id>/`
- writes a `manifest.json`
- prepares `events.jsonl` for workflow events

Why it matters:

- the work is now inspectable
- verification can be tied to a specific session
- final reporting can be generated from artifacts instead of memory

## Phase 2: Prepare the worker brief

Hermes should not send a worker a vague instruction like:

> please fix login handling

Instead, it prepares a bounded brief like `templates/brief.example.json`.

Inspect it:

```bash
python3 -m json.tool templates/brief.example.json
```

A strong brief includes:

- one testable goal
- environment context
- relevant files
- constraints
- explicit acceptance checks

This is where HCW starts to feel operational instead of aspirational.

## Phase 3: Validate dispatch before execution

Before calling a real worker, validate the brief and generated prompt.

```bash
python3 scripts/hcw_dispatch.py templates/brief.example.json --dry-run
```

This dry run proves:

- the brief schema is valid
- the tier is correct
- the prompt structure is usable
- the chain recommendation logic runs
- decomposition hints are available

What to inspect in the output:

- `chain_recommendation`
- `decomposition_hints`
- prompt sections such as Goal, Constraints, Acceptance Checks, and Required Output

## Phase 4: Dispatch a real worker

In a real session, Hermes would now dispatch a worker such as Claude Code, Codex, or OpenCode.

Conceptually, the handoff looks like this:

- Hermes remains the planner and verifier
- the worker performs bounded implementation or analysis
- the worker returns output
- Hermes does not trust the worker claim by default

That last point is the key: worker completion is not final completion.

## Phase 5: Run verification

Now Hermes validates the result with real commands.

Example lightweight verification:

```bash
python3 scripts/hcw_verify.py \
  --repo . \
  --command "python3 -m py_compile scripts/*.py" \
  --label demo-verify
```

Example deeper verification:

```bash
python3 scripts/hcw_verify.py \
  --repo . \
  --command "python3 -m py_compile scripts/*.py" \
  --level deep \
  --label deep-demo \
  --expect "stdout:"
```

What verification can capture:

- command exit status
- stdout / stderr tails
- secret scan results
- diff-scope compliance
- explicit pattern checks with `--expect`

Why this matters:

- it converts "seems okay" into evidence
- it makes failures inspectable
- it gives Hermes something concrete to report upstream

## Phase 6: Summarize artifacts

Once dispatch and verification artifacts exist, generate a final report.

```bash
python3 scripts/hcw_summarize.py .hcw/sessions/<session-id>
```

The summary is derived from artifacts such as:

- `manifest.json`
- `events.jsonl`
- verification outputs
- worker event records

This means the final report is reproducible and auditable.

## Phase 7: Inspect the bundled sample artifacts

The repository already includes a realistic sample under `docs/demo-session/`.

Start here:

- `docs/demo-session/README.md`
- `docs/demo-session/final-report.md`

Those files show the final shape of:

- session metadata
- dispatch events
- verification evidence
- a report draft Hermes could send to a user

## What the complete demo proves

After walking through the full demo, a user should understand that HCW is not just "Hermes plus coding agents".

It is a disciplined loop with clear roles:

### Hermes

- understands the task
- chooses the chain
- writes the brief
- triggers verification
- summarizes evidence
- reports results

### Worker

- performs bounded implementation, analysis, review, or testing
- stays within the brief constraints
- returns raw output for Hermes to inspect

### Verification

- decides whether the work actually passed checks
- prevents unverified completion claims
- produces structured evidence

## Typical output path

A normal session tends to produce this artifact trail:

```text
.hcw/sessions/<session-id>/
├── manifest.json
├── events.jsonl
└── verification.json        # when produced by verification runs
```

And this reporting path:

```text
worker brief -> worker output -> verification evidence -> final report
```

## How to use this in practice

Use this full demo when:

- introducing HCW to a teammate
- showing why Hermes is the orchestrator, not just another coder
- explaining why verification is a first-class step
- proving the workflow is reproducible

Use `docs/quick-start.md` when the user just wants to get to a first success fast.

Use `docs/real-world-use-cases.md` when the user asks whether HCW fits their actual work.

## Recommended reading order

1. `README.md`
2. `docs/quick-start.md`
3. `docs/full-demo.md`
4. `docs/real-world-use-cases.md`
5. `docs/demo-session/README.md`

That order gives the shortest path from interest to confidence.
