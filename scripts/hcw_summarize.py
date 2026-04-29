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


def load_verification_artifact(session_dir: Path) -> list[dict[str, Any]]:
    artifact_path = session_dir / "verification.json"
    if not artifact_path.exists():
        return []
    try:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def format_duration(started: str, finished: str) -> str:
    start_dt = parse_iso(started)
    finish_dt = parse_iso(finished)
    if not start_dt or not finish_dt:
        return ""
    return f" ({(finish_dt - start_dt).total_seconds():.0f}s)"


def summarize_chain_recommendation(data: dict[str, Any]) -> list[str]:
    chain = data.get("chain_recommendation") or {}
    decomposition = data.get("decomposition_hints") or {}
    if not chain and not decomposition:
        return []

    lines: list[str] = []
    if chain:
        dims = chain.get("dimensions") or {}
        lines.append(
            "  - Recommended chain: "
            f"`{chain.get('recommended_chain', '?')}` "
            f"(score `{chain.get('score', '?')}`)"
        )
        if dims:
            lines.append(
                "  - Dimensions: "
                f"risk={dims.get('risk', '?')} "
                f"scope={dims.get('scope', '?')} "
                f"test_leverage={dims.get('test_leverage', '?')} "
                f"parallelism={dims.get('parallelism', '?')}"
            )
    if decomposition:
        lines.append(
            "  - Decomposition: "
            f"{'yes' if decomposition.get('needs_decomposition') else 'no'}"
            f"; suggested subtasks={decomposition.get('suggested_subtasks', 0)}"
        )
        triggers = decomposition.get("triggers") or []
        if triggers:
            lines.append(f"  - Triggers: {', '.join(str(trigger) for trigger in triggers)}")
    return lines


def infer_verification_level(item: dict[str, Any]) -> str:
    data = item.get("data", {})
    label = str(item.get("label", ""))
    if data.get("check") == "secret_scan":
        return "deep"
    if data.get("stdout_tail") or data.get("stderr_tail"):
        return "standard"
    if ":secret_scan" in label or ":diff_scope" in label:
        return "deep"
    return "shallow"


def collect_verification_runs(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    runs: dict[str, dict[str, Any]] = {}
    for item in items:
        label = str(item.get("label", "verify"))
        base_label = label.split(":", 1)[0]
        run = runs.setdefault(base_label, {"items": [], "level": "shallow"})
        run["items"].append(item)
        level = infer_verification_level(item)
        order = {"shallow": 1, "standard": 2, "deep": 3}
        if order[level] > order[run["level"]]:
            run["level"] = level
    return runs


def evidence_excerpt(data: dict[str, Any]) -> str:
    for key in ("stderr_tail", "stdout_tail"):
        text = str(data.get(key, "")).strip()
        if text:
            excerpt = " ".join(line.strip() for line in text.splitlines()[-3:])
            return excerpt[:240]
    return ""


def format_dispatch(item: dict[str, Any]) -> str:
    data = item.get("data", {})
    worker = data.get("worker", "?")
    mode = data.get("mode", "?")
    tier = data.get("tier", "?")
    exit_code = data.get("exit_code", "?")
    ok = data.get("ok", False)
    started = data.get("started_at", "")
    finished = data.get("finished_at", "")
    duration = format_duration(started, finished)
    return f"- Worker `{worker}` | mode `{mode}` | tier `{tier}` | exit `{exit_code}` | ok `{ok}`{duration}"


def format_verification(item: dict[str, Any]) -> str:
    data = item.get("data", {})
    label = item.get("label", "")
    prefix = f"[{label}] " if label else ""
    if data.get("check") == "secret_scan":
        findings = data.get("findings", [])
        return (
            f"- `{prefix}secret_scan` -> ok `{data.get('ok', False)}` | "
            f"lines `{data.get('lines_scanned', '?')}` | findings `{len(findings)}`"
        )
    if data.get("check") == "diff_scope":
        changed = data.get("changed_files", [])
        unexpected = data.get("unexpected_files", [])
        line = (
            f"- `{prefix}diff_scope` -> ok `{data.get('ok', False)}` | "
            f"changed `{len(changed)}`"
        )
        if unexpected:
            line += f" | unexpected: {', '.join(unexpected)}"
        return line

    command = data.get("command", data.get("check", "?"))
    exit_code = data.get("exit_code", data.get("ok", "?"))
    ok = data.get("ok", False)
    duration = format_duration(data.get("started_at", ""), data.get("finished_at", ""))
    line = f"- `{prefix}{command}` -> exit `{exit_code}`, ok `{ok}`{duration}"
    if data.get("expect_failures"):
        failures = "; ".join(
            f"{entry.get('expect', '?')} ({entry.get('reason', '?')})"
            for entry in data.get("expect_failures", [])
        )
        line += f" | expect failures: {failures}"
    excerpt = evidence_excerpt(data)
    if excerpt:
        line += f" | evidence: {excerpt}"
    return line


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
    verification_artifact = load_verification_artifact(session_dir)

    verifications = [e for e in events if e.get("type") == "verification"]
    dispatches = [e for e in events if e.get("type") == "dispatch"]
    reviews = [e for e in events if e.get("type") == "review"]
    if verification_artifact:
        verifications = verification_artifact

    verification_runs = collect_verification_runs(verifications)

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

    verify_pass = sum(1 for e in verifications if e.get("data", {}).get("ok", False))
    verify_fail = sum(1 for e in verifications if not e.get("data", {}).get("ok", True))
    verify_command = [e for e in verifications if e.get("data", {}).get("command")]
    verify_secret = [e for e in verifications if e.get("data", {}).get("check") == "secret_scan"]
    verify_scope = [e for e in verifications if e.get("data", {}).get("check") == "diff_scope"]

    dispatch_recommendations: list[str] = []
    dispatch_mismatches: list[str] = []
    manifest_chain = manifest.get("chain")
    for item in dispatches:
        chain_info = item.get("data", {}).get("chain_recommendation") or {}
        recommended = chain_info.get("recommended_chain")
        score = chain_info.get("score")
        if recommended:
            dispatch_recommendations.append(f"{recommended} (score {score})")
            if manifest_chain and manifest_chain != recommended:
                dispatch_mismatches.append(
                    f"manifest chain `{manifest_chain}` differs from dispatch recommendation `{recommended}`"
                )

    lines: list[str] = []
    lines.append("# Hermes Code Workflow Final Report")
    lines.append("")
    lines.append(f"Session: `{manifest.get('session_id', session_dir.name)}`")
    lines.append(f"Goal: {manifest.get('goal', '(unknown)')}")
    lines.append(f"Repository: `{manifest.get('repo', '(unknown)')}`")
    lines.append(f"Risk: `{manifest.get('risk', '?')}` | Tier: `{manifest.get('tier', '?')}` | Chain: `{manifest.get('chain', '?')}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Dispatches: {len(dispatches)}")
    lines.append(f"- Verifications: {len(verifications)} (pass: {verify_pass}, fail: {verify_fail})")
    lines.append(f"  - Command checks: {len(verify_command)}")
    lines.append(f"  - Secret scans: {len(verify_secret)}")
    lines.append(f"  - Diff-scope checks: {len(verify_scope)}")
    lines.append(f"- Reviews: {len(reviews)}")
    lines.append("")

    lines.append("## Dispatch planning")
    if manifest_chain:
        lines.append(f"- Session chain: `{manifest_chain}`")
    if dispatch_recommendations:
        lines.append(f"- Dispatch recommendations observed: {', '.join(dispatch_recommendations)}")
    else:
        lines.append("- No dispatch recommendations recorded.")
    if dispatch_mismatches:
        for mismatch in dispatch_mismatches:
            lines.append(f"- Follow-up: {mismatch}")
    lines.append("")

    lines.append("## Worker dispatches")
    if dispatches:
        for item in dispatches:
            lines.append(format_dispatch(item))
            lines.extend(summarize_chain_recommendation(item.get("data", {})))
    else:
        lines.append("- No dispatch events recorded.")
    lines.append("")

    lines.append("## Verification evidence")
    if verification_runs:
        for label, run in verification_runs.items():
            lines.append(
                f"- Verification run `{label}` | level `{run.get('level', 'shallow')}` | "
                f"events `{len(run.get('items', []))}`"
            )
            for item in run.get("items", []):
                lines.append(f"  {format_verification(item)[2:]}")
    else:
        lines.append("- No verification events recorded.")
    lines.append("")

    if reviews:
        lines.append("## Reviews")
        for item in reviews:
            lines.append(format_review(item))
        lines.append("")

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

    failed_verifications = [item for item in verifications if not item.get("data", {}).get("ok", True)]
    if failed_verifications:
        lines.append("- Verification failures require follow-up:")
        for item in failed_verifications[:5]:
            lines.append(f"  - {format_verification(item)[2:]}")

    report = "\n".join(lines) + "\n"
    (session_dir / "final-report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
