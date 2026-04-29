# End-to-End Demo Session

This directory shows a realistic Hermes Code Workflow session from start to finish.

## Goal

Demonstrate how Hermes can:

1. create a workflow session;
2. record bounded dispatch and verification events;
3. run a verification pass with structured evidence;
4. summarize artifacts into a final report.

## Scenario

Example task: improve login error handling in a small Python service.

The demo is intentionally lightweight. It is not meant to prove a real code change shipped; it is meant to show the artifact flow and the shape of an HCW session.

## Files

- `manifest.json`
  - Example session metadata.
- `events.jsonl`
  - Example dispatch, verification, and review events.
- `verification.json`
  - Example structured verification evidence.
- `final-report.md`
  - Example final summary emitted by `scripts/hcw_summarize.py`.
- `brief.example.json`
  - Example worker brief for the demo session.

## Suggested walkthrough

```bash
python3 scripts/hcw_session.py create --repo . --goal "Improve login error handling" --risk medium --tier standard --chain plan-execute
python3 scripts/hcw_dispatch.py templates/brief.example.json --dry-run
python3 scripts/hcw_verify.py --repo . --session .hcw/sessions/<session-id> --command "python3 -m py_compile scripts/*.py" --secret-scan --label demo-verify
python3 scripts/hcw_summarize.py .hcw/sessions/<session-id>
```

## What this demonstrates

- Hermes owns the session state.
- Worker dispatch is bounded by a brief.
- Verification is recorded as evidence, not just prose.
- Final reporting is a structured transformation over artifacts.
