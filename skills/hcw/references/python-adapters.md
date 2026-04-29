# Hermes Code Workflow Python Adapter Notes

Python adapters let Hermes use Agent Client Protocol, command-line interface, and software development kit backed workers with structured inputs and outputs.

## Design goals

- Keep adapters thin and auditable.
- Prefer official software development kits or official command-line interfaces.
- Emit JavaScript Object Notation for Hermes to parse.
- Avoid storing secrets in files, logs, or summaries.
- Separate dispatch from verification.

## Recommended scripts

```text
scripts/hcw_dispatch.py
scripts/hcw_verify.py
scripts/hcw_session.py
scripts/hcw_summarize.py
```

## Adapter responsibilities

`hcw_dispatch.py`:

- read a task brief written in JavaScript Object Notation;
- launch the selected worker;
- capture standard output, standard error, and process status;
- emit normalized JavaScript Object Notation.

`hcw_verify.py`:

- run configured validation commands;
- collect repository status and diff metadata when needed;
- emit pass or fail evidence.

`hcw_session.py`:

- create the session directory;
- append worker events to a line-delimited event file;
- update the session manifest.

`hcw_summarize.py`:

- read workflow artifacts;
- produce concise final report input for Hermes.

## Minimal brief schema

```json
{
  "session_id": "Hermes-Code-Workflow-YYYYMMDD-HHMMSS",
  "repo": "/absolute/repo/path",
  "worker": "claude-code|codex|opencode|gemini-agent-client-protocol|hermes",
  "mode": "analyze|implement|review|test|debug",
  "goal": "string",
  "constraints": ["string"],
  "acceptance": ["string"],
  "files": ["path"]
}
```

## Minimal output schema

```json
{
  "ok": true,
  "worker": "claude-code",
  "mode": "implement",
  "changed_files": [],
  "checks": [
    {"command": "npm run build", "ok": true, "exit_code": 0}
  ],
  "summary": "string",
  "risks": [],
  "artifacts": []
}
```
