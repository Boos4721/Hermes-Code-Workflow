#!/usr/bin/env python3
"""Dispatch a bounded Hermes Code Workflow brief to a command-line worker."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_prompt(brief: dict[str, Any]) -> str:
    lines = [
        "You are a worker in Hermes Code Workflow.",
        "Hermes is the orchestrator and will verify your output.",
        "Do not commit, push, install global packages, or access secrets unless the brief explicitly authorizes it.",
        "",
        f"Mode: {brief.get('mode', 'analyze')}",
        f"Goal: {brief.get('goal', '')}",
        f"Repository: {brief.get('repo', '.')}",
        "",
        "Constraints:",
    ]
    for item in brief.get("constraints", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Acceptance criteria:")
    for item in brief.get("acceptance", brief.get("acceptance_criteria", [])):
        lines.append(f"- {item}")
    lines.extend([
        "",
        "Required output:",
        "- summary",
        "- files changed",
        "- commands/checks run",
        "- blockers or risks",
        "- unverified claims, if any",
    ])
    return "\n".join(lines)


def worker_command(worker: str, prompt: str) -> list[str]:
    if worker in {"cc", "claude", "claude-code"}:
        return ["claude", "-p", prompt, "--max-turns", "12", "--permission-mode", "acceptEdits"]
    if worker == "codex":
        return ["codex", "exec", prompt]
    if worker == "opencode":
        return ["opencode", "run", prompt]
    if worker in {"gemini", "gemini-cli"}:
        return ["gemini", "--prompt", prompt]
    raise ValueError(f"unsupported worker: {worker}")


def append_event(session: str | None, event: dict[str, Any]) -> None:
    if not session:
        return
    session_dir = Path(session)
    session_dir.mkdir(parents=True, exist_ok=True)
    with (session_dir / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch a Hermes Code Workflow brief")
    parser.add_argument("brief", help="JSON brief path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    brief_path = Path(args.brief)
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    prompt = build_prompt(brief)
    worker = brief.get("worker", "cc")
    command = worker_command(worker, prompt)
    repo = brief.get("repo", ".")

    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "command": command, "prompt": prompt}, ensure_ascii=False, indent=2))
        return

    started = now_iso()
    proc = subprocess.run(
        command,
        cwd=repo,
        timeout=args.timeout,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    result = {
        "ok": proc.returncode == 0,
        "worker": worker,
        "mode": brief.get("mode", "analyze"),
        "command_display": " ".join(shlex.quote(x) for x in command[:2]) + " <prompt>",
        "started_at": started,
        "finished_at": now_iso(),
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-12000:],
        "stderr_tail": proc.stderr[-12000:],
        "needs_hermes_verification": True,
    }
    append_event(brief.get("session"), {"timestamp": now_iso(), "type": "dispatch", "phase": brief.get("phase", "dispatch"), "data": result})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
