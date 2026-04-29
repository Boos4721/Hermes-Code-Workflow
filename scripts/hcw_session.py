#!/usr/bin/env python3
"""Create and maintain Hermes Code Workflow session artifacts."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def session_id() -> str:
    return datetime.now(timezone.utc).strftime("HCW-%Y%m%d-%H%M%S")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def create(args: argparse.Namespace) -> None:
    sid = args.session_id or session_id()
    root = Path(args.root)
    session_dir = root / sid
    session_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "session_id": sid,
        "created_at": now_iso(),
        "repo": str(Path(args.repo).resolve()),
        "goal": args.goal,
        "phase": "classify",
        "risk": args.risk,
        "chain": args.chain,
        "events_file": "events.jsonl",
    }
    write_json(session_dir / "manifest.json", manifest)
    (session_dir / "events.jsonl").touch()
    print(json.dumps({"ok": True, "session_dir": str(session_dir), **manifest}, ensure_ascii=False))


def append(args: argparse.Namespace) -> None:
    session_dir = Path(args.session)
    event = {
        "timestamp": now_iso(),
        "type": args.type,
        "phase": args.phase,
        "message": args.message,
    }
    if args.data:
        event["data"] = json.loads(args.data)
    with (session_dir / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": True, "event": event}, ensure_ascii=False))


def show(args: argparse.Namespace) -> None:
    session_dir = Path(args.session)
    manifest = read_json(session_dir / "manifest.json")
    events_path = session_dir / "events.jsonl"
    events = []
    if events_path.exists():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
    print(json.dumps({"manifest": manifest, "events": events}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Hermes Code Workflow session artifacts")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create", help="create a new workflow session")
    p.add_argument("--root", default=".hcw/sessions")
    p.add_argument("--session-id")
    p.add_argument("--repo", default=os.getcwd())
    p.add_argument("--goal", required=True)
    p.add_argument("--risk", default="medium", choices=["low", "medium", "high"])
    p.add_argument("--chain", default="plan-execute")
    p.set_defaults(func=create)

    p = sub.add_parser("append", help="append an event to a session")
    p.add_argument("session")
    p.add_argument("--type", required=True)
    p.add_argument("--phase", default="unknown")
    p.add_argument("--message", required=True)
    p.add_argument("--data", help="JSON object with additional event data")
    p.set_defaults(func=append)

    p = sub.add_parser("show", help="show a session manifest and events")
    p.add_argument("session")
    p.set_defaults(func=show)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
