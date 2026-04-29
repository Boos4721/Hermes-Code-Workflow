#!/usr/bin/env python3
"""Run verification commands and emit JSON evidence for Hermes Code Workflow."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_command(command: str, cwd: str | None, timeout: int) -> dict[str, Any]:
    started = now_iso()
    proc = subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        timeout=timeout,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "command": command,
        "cwd": cwd,
        "started_at": started,
        "finished_at": now_iso(),
        "exit_code": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout_tail": proc.stdout[-8000:],
        "stderr_tail": proc.stderr[-8000:],
    }


def append_event(session: str | None, event: dict[str, Any]) -> None:
    if not session:
        return
    session_dir = Path(session)
    session_dir.mkdir(parents=True, exist_ok=True)
    with (session_dir / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    evidence_path = session_dir / "verification.json"
    existing = []
    if evidence_path.exists():
        existing = json.loads(evidence_path.read_text(encoding="utf-8"))
    existing.append(event)
    evidence_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run verification commands with structured evidence")
    parser.add_argument("--repo", default=".", help="working directory for commands")
    parser.add_argument("--session", help="optional .hcw session directory")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--command", action="append", required=True, help="verification command; may be repeated")
    args = parser.parse_args()

    results = []
    for command in args.command:
        result = run_command(command, args.repo, args.timeout)
        event = {"timestamp": now_iso(), "type": "verification", "phase": "verify", "data": result}
        append_event(args.session, event)
        results.append(result)
        if not result["ok"]:
            break

    output = {"ok": all(r["ok"] for r in results), "results": results}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(0 if output["ok"] else 1)


if __name__ == "__main__":
    main()
