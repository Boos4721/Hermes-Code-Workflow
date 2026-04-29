#!/usr/bin/env python3
"""Summarize Hermes Code Workflow session artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_events(session_dir: Path) -> list[dict]:
    events_path = session_dir / "events.jsonl"
    if not events_path.exists():
        return []
    events = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a Hermes Code Workflow session")
    parser.add_argument("session")
    args = parser.parse_args()

    session_dir = Path(args.session)
    manifest_path = session_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    events = load_events(session_dir)
    verifications = [e.get("data", {}) for e in events if e.get("type") == "verification"]
    dispatches = [e.get("data", {}) for e in events if e.get("type") == "dispatch"]

    lines = []
    lines.append("# Hermes Code Workflow Final Report Draft")
    lines.append("")
    lines.append(f"Session: `{manifest.get('session_id', session_dir.name)}`")
    lines.append(f"Goal: {manifest.get('goal', '(unknown)')}")
    lines.append(f"Repository: `{manifest.get('repo', '(unknown)')}`")
    lines.append("")
    lines.append("## Worker dispatches")
    if dispatches:
        for item in dispatches:
            lines.append(f"- Worker: `{item.get('worker')}`; mode: `{item.get('mode')}`; exit code: `{item.get('exit_code')}`; ok: `{item.get('ok')}`")
    else:
        lines.append("- No dispatch events recorded.")
    lines.append("")
    lines.append("## Verification evidence")
    if verifications:
        for item in verifications:
            lines.append(f"- `{item.get('command')}` → exit code `{item.get('exit_code')}`, ok: `{item.get('ok')}`")
    else:
        lines.append("- No verification events recorded.")
    lines.append("")
    lines.append("## Risks and follow-up")
    lines.append("- Fill this section after Hermes reviews the final diff and command output.")

    report = "\n".join(lines) + "\n"
    (session_dir / "final-report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
