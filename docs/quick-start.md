# Quick Start

Get Hermes Code Workflow running end-to-end in about five minutes.

## What you will do

In this quick start, you will:

1. create a workflow session;
2. inspect a bounded worker brief;
3. run a dry-run dispatch;
4. run verification commands;
5. generate a final summary.

By the end, you will have seen the complete HCW artifact flow without needing a real production repository.

## Prerequisites

You need:

- Hermes Agent installed
- this repository checked out locally
- Python 3 available as `python3`

Optional but recommended:

- the `hcw` skill installed in Hermes
- at least one coding worker available later, such as Claude Code, Codex, or OpenCode

## 1. Enter the repository

```bash
cd Hermes-Code-Workflow
```

## 2. Create a demo workflow session

This creates a local session directory under `.hcw/sessions/`.

```bash
python3 scripts/hcw_session.py create \
  --repo . \
  --goal "Learn the Hermes Code Workflow artifact flow" \
  --risk low \
  --tier standard \
  --chain plan-execute
```

Expected result:

- a new session ID is printed
- a directory appears under `.hcw/sessions/<session-id>/`
- `manifest.json` and `events.jsonl` are created

## 3. Inspect the example worker brief

The brief shows the shape of a bounded task Hermes would send to a worker.

```bash
python3 -m json.tool templates/brief.example.json
```

Look for these fields:

- `goal`
- `environment_context`
- `relevant_files`
- `constraints`
- `acceptance`

This is the core discipline of HCW: the worker does not get an open-ended request. It gets a scoped brief with explicit checks.

## 4. Run a dry-run dispatch

This does not call a worker. It only validates the brief and shows the generated prompt.

```bash
python3 scripts/hcw_dispatch.py templates/brief.example.json --dry-run
```

What to look for:

- brief validation passes
- tier is detected correctly
- a chain recommendation is included
- decomposition hints are included
- the generated prompt is structured and bounded

If this dry run looks good, Hermes can safely dispatch a real worker later.

## 5. Run a verification pass

Now run a lightweight verification command and record structured evidence.

```bash
python3 scripts/hcw_verify.py \
  --repo . \
  --command "python3 -m py_compile scripts/*.py" \
  --label quickstart-verify
```

Expected result:

- exit code `0`
- structured JSON output
- stdout/stderr tails captured

This is the other core discipline of HCW: completion is based on evidence, not on a worker saying "done".

## 6. Generate a summary report

Pick the session directory created in step 2 and summarize it.

```bash
python3 scripts/hcw_summarize.py .hcw/sessions/<session-id>
```

Expected result:

- a Markdown final report
- dispatch / verification / review sections when artifacts exist
- summary statistics that Hermes can use in its final user-facing response

## 7. View the bundled end-to-end sample

If you want a prebuilt example with sample artifacts, read:

- `docs/demo-session/README.md`
- `docs/demo-session/final-report.md`

These files show what a realistic session looks like after dispatch and verification have already happened.

## What you just proved

In a few minutes, you verified that HCW can:

- create session artifacts
- represent work as a bounded brief
- validate dispatch structure before execution
- record verification evidence in structured form
- summarize workflow artifacts into a report

That is the core loop.

## What to do next

Choose the next document based on what you need:

- Want the full operator walkthrough? Read `docs/full-demo.md`
- Want practical adoption ideas? Read `docs/real-world-use-cases.md`
- Want to install the skill into Hermes? See the installation section in `README.md`
- Want to refresh a locally copied HCW skill from GitHub later? Run `python3 scripts/hcw_update.py`

## Common first mistakes

### Running a real worker too early

Start with `--dry-run` first. Make sure the brief is scoped and the acceptance checks are meaningful.

### Treating verification as optional

Do not skip verification. HCW is valuable because Hermes verifies claims with evidence.

### Using open-ended goals

A good brief goal is specific, testable, and observable. If the goal is vague, the worker output will be vague too.

## Five-minute success criteria

You are done with quick start when you have all three:

- a session directory under `.hcw/sessions/`
- a successful `hcw_verify.py` result
- a generated summary from `hcw_summarize.py`
