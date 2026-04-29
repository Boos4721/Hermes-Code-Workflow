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
# Chain recommendation scoring (mirrors SKILL.md heuristic)
# ---------------------------------------------------------------------------

_RISK_MAP = {"low": 1, "medium": 2, "high": 3}


def _estimate_scope(brief: dict[str, Any]) -> int:
    """Estimate scope dimension (1-3) from brief fields."""
    files = brief.get("relevant_files", brief.get("files", []))
    n = len(files) if isinstance(files, list) else 0
    if n <= 1:
        return 1
    if n <= 3:
        return 2
    return 3


def _estimate_test_leverage(brief: dict[str, Any]) -> int:
    """Estimate test-leverage dimension (1-3) from brief fields."""
    acceptance = brief.get("acceptance", [])
    test_cmds = [c for c in acceptance if isinstance(c, str) and any(
        k in c.lower() for k in ("test", "pytest", "jest", "cargo test", "go test", "npm test")
    )]
    if not test_cmds:
        return 1
    if len(test_cmds) == 1:
        return 2
    return 3


def _estimate_parallelism(brief: dict[str, Any]) -> int:
    """Estimate parallelism dimension (1-3) from brief fields."""
    files = brief.get("relevant_files", brief.get("files", []))
    n = len(files) if isinstance(files, list) else 0
    if n <= 1:
        return 1
    if n <= 3:
        return 2
    return 3


def compute_chain_score(brief: dict[str, Any]) -> dict[str, Any]:
    """Compute the weighted chain-selection score and recommend a chain."""
    risk_str = brief.get("risk", "medium")
    risk = _RISK_MAP.get(risk_str, 2)
    scope = _estimate_scope(brief)
    test_lev = _estimate_test_leverage(brief)
    parallelism = _estimate_parallelism(brief)

    score = 0.35 * risk + 0.25 * scope + 0.20 * test_lev + 0.20 * parallelism

    # Recommend chain based on score
    if score <= 0.90:
        chain = "quick"
    elif score <= 1.60:
        chain = "plan-execute"
    elif score <= 2.10:
        chain = "plan-execute" if test_lev <= 1 else "test-first-development"
    elif score <= 2.50:
        chain = "multi-worker"
    else:
        chain = "subagent-driven" if parallelism >= 2 else "multi-worker"

    # Tie-breaker: risk=3 forces at least plan-execute
    if risk == 3 and chain == "quick":
        chain = "plan-execute"

    return {
        "score": round(score, 2),
        "dimensions": {
            "risk": risk,
            "scope": scope,
            "test_leverage": test_lev,
            "parallelism": parallelism,
        },
        "recommended_chain": chain,
    }


# ---------------------------------------------------------------------------
# Decomposition hints
# ---------------------------------------------------------------------------

def compute_decomposition_hints(brief: dict[str, Any]) -> dict[str, Any]:
    """Produce lightweight decomposition hints from brief fields."""
    files = brief.get("relevant_files", brief.get("files", []))
    file_count = len(files) if isinstance(files, list) else 0
    acceptance = brief.get("acceptance", [])
    acceptance_count = len(acceptance) if isinstance(acceptance, list) else 0

    triggers: list[str] = []
    if file_count > 10:
        triggers.append(f"file count ({file_count}) exceeds 10")
    if acceptance_count > 5:
        triggers.append(f"acceptance checks ({acceptance_count}) exceed 5")

    # Check for multi-language hints
    extensions: set[str] = set()
    for f in files if isinstance(files, list) else []:
        if isinstance(f, str) and "." in f:
            extensions.add(f.rsplit(".", 1)[-1])
    lang_groups = {
        "python": {"py"},
        "javascript": {"js", "jsx", "mjs", "cjs"},
        "typescript": {"ts", "tsx"},
        "rust": {"rs"},
        "go": {"go"},
        "java": {"java", "kt"},
    }
    detected_langs = sum(1 for langs in lang_groups.values() if extensions & langs)
    if detected_langs > 2:
        triggers.append(f"spans {detected_langs} language groups")

    needs_decomposition = len(triggers) > 0

    suggested_subtasks = 0
    if needs_decomposition:
        # Suggest 3-7 sub-tasks based on file count
        suggested_subtasks = min(7, max(3, file_count // 3))

    return {
        "needs_decomposition": needs_decomposition,
        "triggers": triggers,
        "file_count": file_count,
        "acceptance_count": acceptance_count,
        "suggested_subtasks": suggested_subtasks,
    }


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

    chain_info = compute_chain_score(brief)
    decomposition = compute_decomposition_hints(brief)

    if args.dry_run:
        print(json.dumps({
            "ok": True,
            "dry_run": True,
            "tier": tier,
            "worker": worker,
            "mode": mode,
            "command": command,
            "prompt": prompt,
            "chain_recommendation": chain_info,
            "decomposition_hints": decomposition,
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
        "chain_recommendation": chain_info,
        "decomposition_hints": decomposition,
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
