#!/usr/bin/env python3
"""Run verification commands and emit JSON evidence for Hermes Code Workflow."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_VERIFICATION_LEVELS = {"shallow", "standard", "deep"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Secret scanning
# ---------------------------------------------------------------------------

_SECRET_PATTERNS = [
    re.compile(r"""(?:api[_-]?key|apikey)\s*[:=]\s*['"]?([A-Za-z0-9_\-]{16,})""", re.IGNORECASE),
    re.compile(r"""(?:secret|password|passwd|pwd)\s*[:=]\s*['"]?([^\s'"]{8,})""", re.IGNORECASE),
    re.compile(r"""(?:token)\s*[:=]\s*['"]?([A-Za-z0-9_\-\.]{16,})""", re.IGNORECASE),
    re.compile(r"""(?:bearer)\s+([A-Za-z0-9_\-\.]{20,})""", re.IGNORECASE),
    re.compile(r"""(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}"""),
    re.compile(r"""(?:sk|pk)_(?:test|live)_[A-Za-z0-9]{20,}"""),
    re.compile(r"""(?:AKIA|ASIA)[A-Z0-9]{16}"""),
]


def scan_diff_for_secrets(diff_text: str) -> list[dict[str, str]]:
    """Return list of findings: {line, pattern, match}."""
    findings: list[dict[str, str]] = []
    for i, line in enumerate(diff_text.splitlines(), 1):
        if line.startswith("-"):
            continue
        for pat in _SECRET_PATTERNS:
            m = pat.search(line)
            if m:
                findings.append({"line": str(i), "pattern": pat.pattern[:60], "match": m.group(0)[:40]})
                break
    return findings


# ---------------------------------------------------------------------------
# Expect-pattern matching
# ---------------------------------------------------------------------------

_EXPECT_TARGETS = {"exit", "stdout", "stderr"}


def check_expectations(
    result: dict[str, Any], expectations: list[str]
) -> list[dict[str, str]]:
    """Check command result against expect patterns.

    Each expectation has the form ``target:pattern`` where *target* is one of
    ``exit``, ``stdout``, or ``stderr`` and *pattern* is a Python regular
    expression.  ``exit`` patterns are matched against the stringified exit
    code.

    Returns a list of failed expectations (empty means all passed).
    """
    failures: list[dict[str, str]] = []
    for expr in expectations:
        if ":" not in expr:
            failures.append({"expect": expr, "reason": "invalid format; expected target:pattern"})
            continue
        target, pattern = expr.split(":", 1)
        target = target.strip().lower()
        if target not in _EXPECT_TARGETS:
            failures.append({"expect": expr, "reason": f"unknown target {target!r}; expected exit|stdout|stderr"})
            continue
        if target == "exit":
            haystack = str(result.get("exit_code", ""))
        elif target == "stdout":
            haystack = result.get("stdout_tail", "")
        else:
            haystack = result.get("stderr_tail", "")
        if not re.search(pattern, haystack):
            failures.append({"expect": expr, "reason": f"pattern not found in {target}"})
    return failures


# ---------------------------------------------------------------------------
# Git diff scope check
# ---------------------------------------------------------------------------

def check_diff_scope(repo: str, allowed_files: list[str]) -> dict[str, Any]:
    """Check that git diff only touches allowed files."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=repo, text=True, capture_output=True, timeout=30,
        )
        changed = [f for f in proc.stdout.strip().splitlines() if f]
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    if not allowed_files:
        return {"ok": True, "changed_files": changed, "message": "no allowlist specified"}

    allowed_set = set(allowed_files)
    unexpected = [f for f in changed if f not in allowed_set]
    return {
        "ok": len(unexpected) == 0,
        "changed_files": changed,
        "unexpected_files": unexpected,
    }


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------

def run_command(command: str, cwd: str | None, timeout: int, level: str = "standard") -> dict[str, Any]:
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
    result: dict[str, Any] = {
        "command": command,
        "cwd": cwd,
        "started_at": started,
        "finished_at": now_iso(),
        "exit_code": proc.returncode,
        "ok": proc.returncode == 0,
    }
    if level in {"standard", "deep"}:
        result["stdout_tail"] = proc.stdout[-8000:]
        result["stderr_tail"] = proc.stderr[-8000:]
    else:
        result["stdout_tail"] = ""
        result["stderr_tail"] = ""
    return result


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
    evidence_path = session_dir / "verification.json"
    existing: list[dict[str, Any]] = []
    if evidence_path.exists():
        try:
            existing = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            existing = []
    existing.append(event)
    evidence_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Run verification commands with structured evidence")
    parser.add_argument("--repo", default=".", help="working directory for commands")
    parser.add_argument("--session", help="optional .hcw session directory")
    parser.add_argument("--timeout", type=int, default=300, help="per-command timeout in seconds")
    parser.add_argument("--command", action="append", default=[], help="verification command; may be repeated")
    parser.add_argument("--secret-scan", action="store_true", help="scan git diff for secret patterns")
    parser.add_argument("--diff-scope", nargs="*", metavar="FILE",
                        help="check that git diff only touches these files")
    parser.add_argument("--label", default="verify", help="label for this verification run")
    parser.add_argument("--level", choices=sorted(_VERIFICATION_LEVELS), default="standard",
                        help="verification depth: shallow (exit code only), standard (exit code + output tails), "
                             "deep (standard + auto secret-scan and diff-scope)")
    parser.add_argument("--expect", action="append", default=[],
                        metavar="TARGET:PATTERN",
                        help="expect pattern for command output (target:regex); may be repeated. "
                             "Targets: exit, stdout, stderr. Example: --expect 'stdout:0 failures'")
    args = parser.parse_args()

    # Deep level implies secret-scan and diff-scope (if files were given)
    if args.level == "deep":
        args.secret_scan = True

    if not args.command and not args.secret_scan and args.diff_scope is None:
        parser.error("at least one of --command, --secret-scan, or --diff-scope is required")

    results: list[dict[str, Any]] = []
    all_ok = True

    # Run verification commands
    for command in args.command:
        result = run_command(command, args.repo, args.timeout, level=args.level)
        # Check expect patterns when commands ran successfully
        if result["ok"] and args.expect:
            expect_failures = check_expectations(result, args.expect)
            if expect_failures:
                result["ok"] = False
                result["expect_failures"] = expect_failures
        event = {
            "timestamp": now_iso(),
            "type": "verification",
            "phase": "verify",
            "label": args.label,
            "data": result,
        }
        append_event(args.session, event)
        results.append(result)
        if not result["ok"]:
            all_ok = False
            break

    # Secret scan
    if args.secret_scan and all_ok:
        try:
            diff_proc = subprocess.run(
                ["git", "diff", "HEAD"],
                cwd=args.repo, text=True, capture_output=True, timeout=30,
            )
            findings = scan_diff_for_secrets(diff_proc.stdout)
            scan_result = {
                "check": "secret_scan",
                "ok": len(findings) == 0,
                "findings": findings,
                "lines_scanned": len(diff_proc.stdout.splitlines()),
            }
        except Exception as exc:
            scan_result = {"check": "secret_scan", "ok": False, "error": str(exc)}

        event = {
            "timestamp": now_iso(),
            "type": "verification",
            "phase": "verify",
            "label": f"{args.label}:secret_scan",
            "data": scan_result,
        }
        append_event(args.session, event)
        results.append(scan_result)
        if not scan_result["ok"]:
            all_ok = False

    # Diff scope check
    if args.diff_scope is not None and all_ok:
        scope_result = check_diff_scope(args.repo, args.diff_scope)
        scope_result["check"] = "diff_scope"
        event = {
            "timestamp": now_iso(),
            "type": "verification",
            "phase": "verify",
            "label": f"{args.label}:diff_scope",
            "data": scope_result,
        }
        append_event(args.session, event)
        results.append(scope_result)
        if not scope_result["ok"]:
            all_ok = False

    output = {
        "ok": all_ok,
        "label": args.label,
        "level": args.level,
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
