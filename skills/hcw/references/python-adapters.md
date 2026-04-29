# Hermes Code Workflow Python Adapter Notes

Python adapters let Hermes use Agent Client Protocol, command-line interface, and software development kit backed workers with structured inputs and outputs.

## Design goals

- Keep adapters thin and auditable.
- Prefer official software development kits or official command-line interfaces.
- Emit JavaScript Object Notation for Hermes to parse.
- Avoid storing secrets in files, logs, or summaries.
- Separate dispatch from verification.

## Scripts

```text
scripts/hcw_dispatch.py      # run one worker from a JSON brief
scripts/hcw_verify.py        # run verification checks and emit JSON evidence
scripts/hcw_session.py       # create/read/update session artifacts
scripts/hcw_summarize.py     # summarize artifacts for final report
```

## Adapter responsibilities

### hcw_dispatch.py

Read a task brief in JSON, validate required fields, build a prompt matching the SKILL.md Dispatch Brief Template, launch the selected worker, capture standard output and standard error, and emit normalized JSON.

Key features:

- **Brief tiering**: `--tier mini|standard|auto` selects prompt verbosity. Auto-detect checks whether `relevant_files`, `constraints`, and `environment_context` are all present.
- **Brief validation**: rejects missing required fields and unknown modes before launching the worker.
- **Mode-aware permissions**: Claude Code gets `--permission-mode plan` for analyze/review and `--permission-mode acceptEdits` for implement/test/debug.
- **Full prompt sections**: Goal, Environment Context, Relevant Files, Constraints, Acceptance Checks, Required Output, and When Stuck (standard tier only).

```text
usage: hcw_dispatch.py [-h] [--dry-run] [--timeout TIMEOUT]
                        [--tier {mini,standard,auto}] brief

positional arguments:
  brief                 JSON brief path

optional arguments:
  --dry-run             print prompt without executing
  --timeout TIMEOUT     worker timeout in seconds (default: 600)
  --tier {mini,standard,auto}
                        brief tier (default: auto)
```

### hcw_verify.py

Run configured validation commands, optionally scan git diff for secrets, optionally check diff scope against an allowed file list, and emit pass or fail evidence.

Key features:

- **Command verification**: runs each `--command` and records exit code, stdout tail, and stderr tail.
- **Secret scanning**: `--secret-scan` runs regex patterns against `git diff HEAD` to detect API keys, tokens, passwords, and cloud credentials.
- **Diff scope checking**: `--diff-scope FILE [FILE ...]` verifies that only allowed files were modified.
- **Labeled runs**: `--label` tags all events for easier filtering in the session log.

```text
usage: hcw_verify.py [-h] [--repo REPO] [--session SESSION]
                      [--timeout TIMEOUT] [--command COMMAND]
                      [--secret-scan] [--diff-scope [FILE ...]]
                      [--label LABEL]

at least one of --command, --secret-scan, or --diff-scope is required.
```

### hcw_session.py

Create the session directory, append worker events to a line-delimited event file, and display session summaries.

Key features:

- **Manifest fields**: session identifier, created timestamp, repository path, goal, phase, risk, tier, and chain.
- **Event append**: any event type (dispatch, verification, review, note) with optional JSON data.
- **Show with summary**: `show` displays manifest, event count, and event type breakdown. Add `--full` to include all events.

```text
usage: hcw_session.py {create,append,show} ...

create:
  --root ROOT           session root directory (default: .hcw/sessions)
  --session-id ID       custom session identifier
  --repo REPO           repository path (default: cwd)
  --goal GOAL           session goal (required)
  --risk {low,medium,high}
  --tier {mini,standard}
  --chain CHAIN         workflow chain name

append:
  session               session directory path
  --type TYPE           event type (required)
  --phase PHASE         workflow phase
  --message MESSAGE     event message (required)
  --data DATA           JSON object with additional data

show:
  session               session directory path
  --full                include all events in output
```

### hcw_summarize.py

Read session artifacts and produce a Markdown final report.

Key features:

- **Dispatch reporting**: shows worker, mode, tier, exit code, and duration.
- **Verification reporting**: shows command or check name, exit code, and pass/fail status with labels.
- **Review reporting**: captures review events with reviewer, verdict, and issue count.
- **Blocker and risk extraction**: scans worker stdout for blocker and risk sections.
- **Summary statistics**: counts dispatches, verifications (pass/fail), and reviews.

```text
usage: hcw_summarize.py session
```

## Brief schema (standard)

```json
{
  "session_id": "HCW-YYYYMMDD-HHMMSS",
  "repo": "/absolute/repo/path",
  "session": ".hcw/sessions/HCW-YYYYMMDD-HHMMSS",
  "worker": "Claude Code|Codex|OpenCode|Gemini",
  "phase": "implement",
  "mode": "analyze|implement|review|test|debug",
  "tier": "mini|standard",
  "goal": "one testable sentence",
  "environment_context": {
    "branch": "main",
    "language_runtime": "Python 3.11",
    "build_tool": "python -m build",
    "test_command": "pytest",
    "lint_command": "ruff check ."
  },
  "relevant_files": ["path/to/file.py"],
  "constraints": ["string"],
  "acceptance": ["runnable command with expected outcome"]
}
```

Mini brief requires only: `repo`, `session`, `mode`, `goal`, `acceptance`. The dispatch script auto-detects tier based on whether `relevant_files`, `constraints`, and `environment_context` are populated.

## Worker output schema

```json
{
  "ok": true,
  "worker": "Claude Code",
  "mode": "implement",
  "tier": "standard",
  "exit_code": 0,
  "started_at": "2026-04-30T03:00:00+00:00",
  "finished_at": "2026-04-30T03:05:00+00:00",
  "stdout_tail": "...",
  "stderr_tail": "",
  "needs_hermes_verification": true
}
```

## Event schema (events.jsonl)

Each line is a JSON object:

```json
{
  "timestamp": "2026-04-30T03:00:00+00:00",
  "type": "dispatch|verification|review|note",
  "phase": "dispatch|verify|review",
  "label": "optional label for filtering",
  "data": { "...type-specific fields..." }
}
```
