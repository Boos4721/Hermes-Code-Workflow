# HCW Python Adapter Notes

Python adapters let Hermes use ACP/CLI/SDK-backed workers with structured inputs and outputs.

## Design goals

- Keep adapters thin and auditable.
- Prefer official SDKs or official CLIs.
- Emit JSON for Hermes to parse.
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
- read a JSON brief
- launch selected worker
- capture stdout/stderr/status
- emit normalized JSON

`hcw_verify.py`:
- run configured validation commands
- collect git status/diff metadata
- emit pass/fail JSON

`hcw_session.py`:
- create session directory
- append worker events to JSONL
- update manifest

`hcw_summarize.py`:
- read artifacts
- produce concise final report input for Hermes

## Minimal brief schema

```json
{
  "session_id": "HCW-YYYYMMDD-HHMMSS",
  "repo": "/absolute/repo/path",
  "worker": "cc|codex|opencode|gemini-acp|hermes",
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
  "worker": "cc",
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
