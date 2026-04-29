#!/usr/bin/env python3
"""Dispatch a bounded Hermes Code Workflow brief to a command-line worker."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Brief validation
# ---------------------------------------------------------------------------

_REQUIRED_MINI = {"repo", "session", "mode", "goal", "acceptance"}
_REQUIRED_STANDARD = _REQUIRED_MINI | {"constraints", "relevant_files"}


def validate_brief(brief: dict[str, Any], tier: str) -> list[str]:
    """Return a list of validation errors; empty means valid."""
    required = _REQUIRED_MINI if tier == "mini" else _REQUIRED_STANDARD
    errors: list[str] = []
    for field in sorted(required):
        value = brief.get(field)
        if value is None or value == "" or value == []:
            errors.append(f"missing or empty required field: {field}")
    acceptance = brief.get("acceptance", [])
    if not isinstance(acceptance, list) or not acceptance:
        errors.append("acceptance must be a non-empty list of runnable commands")
    mode = brief.get("mode", "")
    if mode not in {"analyze", "implement", "review", "test", "debug"}:
        errors.append(f"unknown mode: {mode!r}; expected analyze|implement|review|test|debug")
    return errors


# ---------------------------------------------------------------------------
# Prompt construction — matches SKILL.md Dispatch Brief Template
# ---------------------------------------------------------------------------

def build_prompt(brief: dict[str, Any], tier: str) -> str:
    """Build a worker prompt from the brief, respecting tier."""
    mode = brief.get("mode", "analyze")
    repo = brief.get("repo", ".")
    session = brief.get("session", "")
    goal = brief.get("goal", "")

    lines = [
        "You are a worker in Hermes Code Workflow.",
        "Hermes is the orchestrator and will verify your output.",
        "Do not commit, push, or publish unless the brief explicitly says so.",
        "",
        f"Repository: {repo}",
        f"Session: {session}",
        f"Mode: {mode}",
        "",
        "## Goal",
        "",
        goal,
    ]

    # Environment Context — always included in standard, optional in mini
    env_ctx = brief.get("environment_context")
    if env_ctx or tier == "standard":
        env_ctx = env_ctx or {}
        lines.extend([
            "",
            "## Environment Context",
            "",
            f"- Branch: {env_ctx.get('branch', 'unknown')}",
            f"- Language/runtime: {env_ctx.get('language_runtime', 'unknown')}",
            f"- Build tool: {env_ctx.get('build_tool', 'unknown')}",
            f"- Test command: {env_ctx.get('test_command', 'unknown')}",
            f"- Lint/format command: {env_ctx.get('lint_command', 'none')}",
        ])

    # Relevant Files
    relevant = brief.get("relevant_files", brief.get("files", []))
    if relevant:
        lines.extend(["", "## Relevant Files", ""])
        for item in relevant:
            lines.append(f"- {item}")

    # Constraints
    constraints = brief.get("constraints", [])
    if constraints:
        lines.extend(["", "## Constraints", ""])
        for item in constraints:
            lines.append(f"- {item}")
    elif tier == "mini":
        lines.extend([
            "",
            "## Constraints",
            "",
            "- Follow existing project conventions. Only modify files listed above.",
        ])

    # Acceptance Checks
    acceptance = brief.get("acceptance", brief.get("acceptance_criteria", []))
    lines.extend(["", "## Acceptance Checks", ""])
    if acceptance:
        for item in acceptance:
            lines.append(f"- {item}")
    else:
        lines.append("- (none specified; report what you verified)")

    # Required Output — full for standard, reduced for mini
    lines.extend(["", "## Required Output", ""])
    if tier == "mini":
        lines.extend([
            "When finished, produce:",
            "- **summary**: one paragraph describing what was done",
            "- **files changed**: list of file paths with one-line description per file",
            "- **checks run**: each command executed, its exit code, and outcome (pass/fail)",
            "- **evidence**: paste the last 10 lines of test or build output showing the result",
        ])
    else:
        lines.extend([
            "When finished, produce this exact structure:",
            "",
            "- **summary**: one paragraph describing what was done",
            "- **files changed**: list of file paths with one-line description per file",
            "- **checks run**: each command executed, its exit code, and outcome (pass/fail)",
            "- **evidence**: paste the last 10 lines of test or build output showing the result",
            "- **blockers**: anything that prevented full completion, with what was attempted and what actually happened",
            "- **risks**: anything the orchestrator should verify or watch for",
            "",
            "If you cannot complete a step, report what you tried, the exact error, and what you believe is needed. Do not skip silently.",
        ])

    # When Stuck — standard only
    if tier == "standard":
        lines.extend([
            "",
            "## When Stuck",
            "",
            "1. Report the blocker with the exact error message or unexpected behavior.",
            "2. State what you tried and why you expected it to work.",
            "3. Propose one or two next steps.",
            "4. Do not guess or patch blindly; the orchestrator will decide how to proceed.",
        ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Worker command construction — mode-aware
# ---------------------------------------------------------------------------

def worker_command(worker: str, prompt: str, mode: str) -> list[str]:
    """Build the CLI command for the selected worker and mode."""
    if worker in {"cc", "claude", "claude-code"}:
        cmd = ["claude", "-p", prompt, "--max-turns", "12"]
        if mode in {"analyze", "review"}:
            cmd.extend(["--permission-mode", "plan"])
        else:
            cmd.extend(["--permission-mode", "acceptEdits"])
        return cmd
    if worker == "codex":
        return ["codex", "exec", prompt]
    if worker == "opencode":
        return ["opencode", "run", prompt]
    if worker in {"gemini", "gemini-cli"}:
        return ["gemini", "--prompt", prompt]
    raise ValueError(f"unsupported worker: {worker}")


# ---------------------------------------------------------------------------
# Event logging
# ---------------------------------------------------------------------------

def append_event(session: str | None, event: dict[str, Any]) -> None:
    if not session:
        return
    session_dir = Path(session)
    session_dir.mkdir(parents=True, exist_ok=True)
    with (session_dir / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch a Hermes Code Workflow brief")
    parser.add_argument("brief", help="JSON brief path")
    parser.add_argument("--dry-run", action="store_true", help="print prompt without executing")
    parser.add_argument("--timeout", type=int, default=600, help="worker timeout in seconds")
    parser.add_argument("--tier", choices=["mini", "standard", "auto"], default="auto",
                        help="brief tier: mini, standard, or auto-detect from content")
    args = parser.parse_args()

    brief_path = Path(args.brief)
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    worker = brief.get("worker", "cc")
    mode = brief.get("mode", "analyze")
    repo = brief.get("repo", ".")

    # Determine tier
    tier = args.tier
    if tier == "auto":
        has_relevant = bool(brief.get("relevant_files", brief.get("files", [])))
        has_constraints = bool(brief.get("constraints"))
        has_env = bool(brief.get("environment_context"))
        if has_relevant and has_constraints and has_env:
            tier = "standard"
        else:
            tier = "mini"

    # Validate brief
    errors = validate_brief(brief, tier)
    if errors:
        print(json.dumps({"ok": False, "errors": errors, "tier": tier}, ensure_ascii=False, indent=2),
              file=sys.stderr)
        raise SystemExit(2)

    prompt = build_prompt(brief, tier)
    command = worker_command(worker, prompt, mode)

    if args.dry_run:
        print(json.dumps({
            "ok": True,
            "dry_run": True,
            "tier": tier,
            "worker": worker,
            "mode": mode,
            "command": command,
            "prompt": prompt,
        }, ensure_ascii=False, indent=2))
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
        "mode": mode,
        "tier": tier,
        "command_display": " ".join(shlex.quote(x) for x in command[:2]) + " <prompt>",
        "started_at": started,
        "finished_at": now_iso(),
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-12000:],
        "stderr_tail": proc.stderr[-12000:],
        "needs_hermes_verification": True,
    }
    append_event(brief.get("session"), {
        "timestamp": now_iso(),
        "type": "dispatch",
        "phase": brief.get("phase", "dispatch"),
        "data": result,
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
