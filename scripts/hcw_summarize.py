#!/usr/bin/env python3
"""Summarize Hermes Code Workflow session artifacts into a final report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_events(session_dir: Path) -> list[dict[str, Any]]:
    events_path = session_dir / "events.jsonl"
    if not events_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def format_dispatch(item: dict[str, Any]) -> str:
    data = item.get("data", {})
    worker = data.get("worker", "?")
    mode = data.get("mode", "?")
    tier = data.get("tier", "?")
    exit_code = data.get("exit_code", "?")
    ok = data.get("ok", False)
    started = data.get("started_at", "")
    finished = data.get("finished_at", "")
    duration = ""
    if started and finished:
        try:
            s = datetime.fromisoformat(started)
            f = datetime.fromisoformat(finished)
            duration = f" ({(f - s).total_seconds():.0f}s)"
        except (ValueError, TypeError):
            pass
    return f"- Worker `{worker}` | mode `{mode}` | tier `{tier}` | exit `{exit_code}` | ok `{ok}`{duration}"


def format_verification(item: dict[str, Any]) -> str:
    data = item.get("data", {})
    command = data.get("command", data.get("check", "?"))
    exit_code = data.get("exit_code", data.get("ok", "?"))
    ok = data.get("ok", False)
    label = item.get("label", "")
    prefix = f"[{label}] " if label else ""
    return f"- `{prefix}{command}` -> exit `{exit_code}`, ok `{ok}`"


def format_review(item: dict[str, Any]) -> str:
    data = item.get("data", {})
    reviewer = data.get("reviewer", "?")
    verdict = data.get("verdict", "?")
    kind = data.get("kind", item.get("label", "review"))
    issues = data.get("issues_count", 0)
    return f"- {kind} by `{reviewer}`: verdict `{verdict}` ({issues} issue(s))"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a Hermes Code Workflow session")
    parser.add_argument("session")
    args = parser.parse_args()

    session_dir = Path(args.session)
    manifest_path = session_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    events = load_events(session_dir)

    verifications = [e for e in events if e.get("type") == "verification"]
    dispatches = [e for e in events if e.get("type") == "dispatch"]
    reviews = [e for e in events if e.get("type") == "review"]

    # Collect blockers and risks from dispatch results
    blockers: list[str] = []
    risks: list[str] = []
    for e in dispatches:
        data = e.get("data", {})
        if data.get("stdout_tail"):
            tail = data["stdout_tail"]
            for line in tail.splitlines():
                low = line.lower().strip()
                if low.startswith("- **blockers**:") or low.startswith("blockers:"):
                    blockers.append(line.strip())
                elif low.startswith("- **risks**:") or low.startswith("risks:"):
                    risks.append(line.strip())

    # Count verification pass/fail
    verify_pass = sum(1 for e in verifications if e.get("data", {}).get("ok", False))
    verify_fail = sum(1 for e in verifications if not e.get("data", {}).get("ok", True))

    lines: list[str] = []
    lines.append("# Hermes Code Workflow Final Report")
    lines.append("")
    lines.append(f"Session: `{manifest.get('session_id', session_dir.name)}`")
    lines.append(f"Goal: {manifest.get('goal', '(unknown)')}")
    lines.append(f"Repository: `{manifest.get('repo', '(unknown)')}`")
    lines.append(f"Risk: `{manifest.get('risk', '?')}` | Tier: `{manifest.get('tier', '?')}` | Chain: `{manifest.get('chain', '?')}`")
    lines.append("")

    # Summary stats
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Dispatches: {len(dispatches)}")
    lines.append(f"- Verifications: {len(verifications)} (pass: {verify_pass}, fail: {verify_fail})")
    lines.append(f"- Reviews: {len(reviews)}")
    lines.append("")

    # Dispatches
    lines.append("## Worker dispatches")
    if dispatches:
        for item in dispatches:
            lines.append(format_dispatch(item))
    else:
        lines.append("- No dispatch events recorded.")
    lines.append("")

    # Verifications
    lines.append("## Verification evidence")
    if verifications:
        for item in verifications:
            lines.append(format_verification(item))
    else:
        lines.append("- No verification events recorded.")
    lines.append("")

    # Reviews
    if reviews:
        lines.append("## Reviews")
        for item in reviews:
            lines.append(format_review(item))
        lines.append("")

    # Blockers and risks
    lines.append("## Risks and follow-up")
    if blockers:
        lines.append("### Blockers reported by workers")
        for b in blockers:
            lines.append(f"  {b}")
    if risks:
        lines.append("### Risks reported by workers")
        for r in risks:
            lines.append(f"  {r}")
    if not blockers and not risks:
        lines.append("- Fill this section after Hermes reviews the final diff and command output.")

    report = "\n".join(lines) + "\n"
    (session_dir / "final-report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
