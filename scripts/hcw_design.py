#!/usr/bin/env python3
"""Design agent: structured architecture/design phase for Hermes Code Workflow.

Creates, explores, proposes, reviews, and finalizes design documents.
Integrates with hcw_session.py sessions for traceable design artifacts.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def session_id() -> str:
    return datetime.now(timezone.utc).strftime("DSN-%Y%m%d-%H%M%S")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# init — create design session
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> None:
    sid = args.session_id or session_id()
    session_dir = Path(args.output) if args.output.endswith(".md") else Path(args.output) / sid
    if str(session_dir).endswith(".md"):
        session_dir = session_dir.parent

    # Create artifact directories
    (session_dir / "exploration").mkdir(parents=True, exist_ok=True)

    manifest = {
        "session_id": sid,
        "type": "design",
        "created_at": now_iso(),
        "goal": args.goal,
        "context": args.context or "",
        "constraints": args.constraints or [],
        "status": "init",
        "artifact_paths": {
            "exploration_dir": str(session_dir / "exploration"),
            "proposals": str(session_dir / "proposals.json"),
            "design_md": str(session_dir / "design.md"),
            "review": str(session_dir / "review.json"),
        },
    }
    write_json(session_dir / "manifest.json", manifest)
    (session_dir / "events.jsonl").touch()

    print(json.dumps({
        "ok": True,
        "session_id": sid,
        "session_dir": str(session_dir),
        "goal": args.goal,
        "status": "init",
    }, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# explore — scan codebase for design context
# ---------------------------------------------------------------------------

_PROJECT_FILE_PATTERNS = [
    "**/*.py", "**/*.js", "**/*.ts", "**/*.tsx", "**/*.jsx",
    "**/*.rs", "**/*.go", "**/*.java", "**/*.kt",
    "**/*.yaml", "**/*.yml", "**/*.json", "**/*.toml",
    "**/Cargo.toml", "**/go.mod", "**/package.json",
    "**/*.md", "**/Dockerfile*", "**/docker-compose*",
    "**/Makefile", "**/*.mk",
    "**/*.sql", "**/*.prisma", "**/schema.prisma",
]

_EXCLUDE_PATTERNS = [
    ".git", "node_modules", "venv", ".venv", "__pycache__",
    "dist", "build", "target", ".next", ".hcw",
]


def _should_exclude(path: str) -> bool:
    parts = Path(path).parts
    return any(p in parts or p in path for p in _EXCLUDE_PATTERNS)


def cmd_explore(args: argparse.Namespace) -> None:
    target = Path(args.dir).resolve()
    if not target.is_dir():
        print(json.dumps({"ok": False, "error": f"not a directory: {target}"}), file=sys.stderr)
        raise SystemExit(1)

    # Collect project structure
    structure: dict[str, list[dict[str, Any]]] = {}
    total_files = 0
    for pattern in _PROJECT_FILE_PATTERNS:
        for f in sorted(target.rglob(pattern)):
            if _should_exclude(str(f)):
                continue
            rel = f.relative_to(target)
            ext = f.suffix.lower()
            structure.setdefault(ext, []).append({
                "path": str(rel),
                "size": f.stat().st_size,
            })
            total_files += 1
            if args.max_files and total_files >= args.max_files:
                break
        if args.max_files and total_files >= args.max_files:
            break

    # Detect language/runtime
    extensions = set(structure.keys())
    lang_hints: dict[str, list[str]] = {
        "Python": [".py", ".pyi"],
        "JavaScript": [".js", ".mjs", ".cjs"],
        "TypeScript": [".ts", ".tsx"],
        "Rust": [".rs"],
        "Go": [".go"],
        "Java": [".java", ".kt"],
        "YAML": [".yaml", ".yml"],
        "JSON": [".json"],
        "TOML": [".toml"],
        "Markdown": [".md"],
        "SQL": [".sql", ".prisma"],
        "Docker": [".dockerfile", ""],
    }
    detected: list[str] = []
    for lang, exts in lang_hints.items():
        if extensions & set(exts):
            detected.append(lang)

    # Structural overview by extension
    overview: dict[str, dict[str, Any]] = {}
    for ext, files in sorted(structure.items()):
        ext_name = ext if ext else "(no ext)"
        overview[ext_name] = {
            "count": len(files),
            "total_size_kb": round(sum(f["size"] for f in files) / 1024, 1),
            "sample_files": [f["path"] for f in files[:5]],
        }

    # Entry point detection
    entry_points: list[str] = []
    for marker in ("main.py", "app.py", "cli.py", "index.js", "index.ts", "main.rs", "main.go",
                   "manage.py", "wsgi.py", "asgi.py", "cmd/"):
        matches = list(target.rglob(marker))
        for m in matches:
            if not _should_exclude(str(m)):
                entry_points.append(str(m.relative_to(target)))

    # Dependency descriptors
    dep_files: list[str] = []
    for dep in ("requirements.txt", "pyproject.toml", "package.json", "Cargo.toml",
                "go.mod", "Gemfile", "build.gradle", "Pom.xml"):
        f = target / dep
        if f.exists():
            dep_files.append(dep)

    result = {
        "ok": True,
        "target": str(target),
        "total_files": min(total_files, args.max_files or total_files),
        "languages_detected": detected,
        "file_overview": overview,
        "entry_points": entry_points,
        "dependency_files": dep_files,
        "scanned_at": now_iso(),
    }

    # Save exploration artifact
    session_dir = None
    if args.session:
        session_dir = Path(args.session)
        session_dir.mkdir(parents=True, exist_ok=True)
        exp_dir = session_dir / "exploration"
        exp_dir.mkdir(parents=True, exist_ok=True)
        write_json(exp_dir / "codebase.json", result)
        write_json(session_dir / "events.jsonl", {
            "timestamp": now_iso(),
            "type": "exploration",
            "phase": "design",
            "data": {"files_scanned": result["total_files"], "languages": detected},
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# propose — generate structured design proposals based on goal + exploration
# ---------------------------------------------------------------------------

_DESIGN_APPROACH_FIELDS = [
    "name", "description", "pros", "cons", "complexity", "risk",
    "key_components", "data_flow", "open_questions",
]


def _approach_template(index: int) -> dict[str, Any]:
    return {
        "approach": index,
        "name": f"Approach {index}",
        "description": "",
        "pros": [],
        "cons": [],
        "complexity": "medium",
        "risk": "medium",
        "key_components": [],
        "data_flow": "",
        "open_questions": [],
    }


def cmd_propose(args: argparse.Namespace) -> None:
    proposals: list[dict[str, Any]] = []
    for i in range(1, max(2, min(args.approaches, 4)) + 1):
        proposals.append(_approach_template(i))

    proposal_set = {
        "session_id": args.session or "",
        "goal": args.goal,
        "context": args.context or "",
        "generated_at": now_iso(),
        "approach_count": len(proposals),
        "proposals": proposals,
        "recommendation": args.recommend if hasattr(args, "recommend") and args.recommend else None,
    }

    # Save proposals
    if args.session:
        session_dir = Path(args.session)
        session_dir.mkdir(parents=True, exist_ok=True)
        write_json(session_dir / "proposals.json", proposal_set)
        write_json(session_dir / "events.jsonl", {
            "timestamp": now_iso(),
            "type": "proposal",
            "phase": "design",
            "data": {"approach_count": len(proposals)},
        })

    print(json.dumps(proposal_set, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# review — check design.md for completeness
# ---------------------------------------------------------------------------

_DESIGN_REVIEW_CHECKS = [
    ("goal", "Goal is clearly stated and testable", True),
    ("scope", "Scope is bounded — files/components to change are listed", True),
    ("approach", "At least one design approach is described", True),
    ("tradeoffs", "Trade-offs or alternatives are discussed", False),
    ("constraints", "Constraints (performance, security, compatibility) are explicit", True),
    ("acceptance", "Acceptance criteria are defined and observable", True),
    ("open_questions", "Open questions are listed or explicitly excluded", False),
    ("data_flow", "Data flow or architecture diagram description exists", False),
]


def _read_design_md(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def cmd_review(args: argparse.Namespace) -> None:
    design_path = Path(args.design)
    content = _read_design_md(design_path)

    if content is None:
        print(json.dumps({
            "ok": False,
            "error": f"design file not found: {design_path}",
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)

    results: list[dict[str, Any]] = []
    passed = 0
    failed = 0

    for check_id, description, required in _DESIGN_REVIEW_CHECKS:
        # Simple heuristic presence checks
        found = False
        if check_id == "goal":
            found = bool(re.search(r"#+\s*Goal|##\s+Goal|Purpose|Objective", content, re.IGNORECASE))
        elif check_id == "scope":
            found = bool(re.search(r"#+\s*Scope|##\s+Scope|In scope|Out of scope|Files?", content, re.IGNORECASE))
        elif check_id == "approach":
            found = bool(re.search(r"#+\s*Approach|##\s+Approach|Architecture|Design", content, re.IGNORECASE))
        elif check_id == "tradeoffs":
            found = bool(re.search(r"trade.?off|alternative|compar|vs\.", content, re.IGNORECASE))
        elif check_id == "constraints":
            found = bool(re.search(r"#+\s*Constraint|##\s+Constraint|Limitation|Non.?functional|Security|Performance", content, re.IGNORECASE))
        elif check_id == "acceptance":
            found = bool(re.search(r"#+\s*Accept|##\s+Accept|Acceptance|Verification|Check", content, re.IGNORECASE))
        elif check_id == "open_questions":
            found = bool(re.search(r"#+\s*Open|##\s+Open|Question|Risk|Unknown|TODO", content, re.IGNORECASE))
        elif check_id == "data_flow":
            found = bool(re.search(r"#+\s*Data|##\s+Data|Flow|Architecture|Diagram|Sequence|Component", content, re.IGNORECASE))

        status = "pass" if found else ("fail" if required else "info")
        if found:
            passed += 1
        elif required:
            failed += 1

        results.append({
            "check": check_id,
            "description": description,
            "required": required,
            "status": status,
            "found": found,
        })

    # Keyword coverage check
    keywords = ["goal", "scope", "approach", "constraint", "accept"]
    keyword_hits = sum(1 for kw in keywords if re.search(rf"\b{kw}", content[:3000], re.IGNORECASE))
    coverage = round(keyword_hits / len(keywords) * 100)

    verdict = "pass" if failed == 0 else "needs-work"
    review_result = {
        "ok": verdict == "pass",
        "design_file": str(design_path),
        "reviewed_at": now_iso(),
        "checks": results,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": len(results),
            "keyword_coverage_pct": coverage,
        },
        "verdict": verdict,
    }

    # Save review
    if args.session:
        session_dir = Path(args.session)
        session_dir.mkdir(parents=True, exist_ok=True)
        write_json(session_dir / "review.json", review_result)
        write_json(session_dir / "events.jsonl", {
            "timestamp": now_iso(),
            "type": "design_review",
            "phase": "design",
            "data": {"verdict": verdict, "passed": passed, "failed": failed},
        })

    print(json.dumps(review_result, ensure_ascii=False, indent=2))
    if verdict != "pass":
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# finalize — produce final design.md from artifacts
# ---------------------------------------------------------------------------

_DESIGN_MD_TEMPLATE = """# Design: {goal}

- **Session**: `{session_id}`
- **Status**: {status}
- **Created**: {created_at}

## Goal

{goal}

{context_section}
## Scope

{scope_section}

## Approach {approach_index}

{approach_description}

### Key Components

{components_section}

### Data Flow / Architecture

{data_flow_section}

## Alternatives Considered

{alternatives_section}

## Constraints

{constraints_section}

## Acceptance Criteria

{criteria_section}

## Open Questions

{questions_section}

## Risks

{risks_section}
"""


def cmd_finalize(args: argparse.Namespace) -> None:
    session_dir = Path(args.session)
    manifest_path = session_dir / "manifest.json"
    proposals_path = session_dir / "proposals.json"
    review_path = session_dir / "review.json"

    manifest = read_json(manifest_path) if manifest_path.exists() else {}
    proposals = read_json(proposals_path) if proposals_path.exists() else {}
    review = read_json(review_path) if review_path.exists() else {}

    goal = manifest.get("goal", args.goal or "(goal not set)")
    constraints = manifest.get("constraints", [])

    chosen_approach = 1
    if proposals.get("proposals"):
        chosen_approach = proposals.get("recommendation") or 1

    approach = {}
    for p in proposals.get("proposals", []):
        if p.get("approach") == chosen_approach:
            approach = p
            break

    context_section = manifest.get("context", "") or ""
    if context_section:
        context_section = f"## Context\n\n{context_section}\n"

    scope_lines = []
    if args.scope:
        scope_lines = [f"- {s}" for s in args.scope]
    elif approach.get("key_components"):
        scope_lines = [f"- {c}" for c in approach["key_components"]]
    scope_section = "\n".join(scope_lines) if scope_lines else "TBD — define in implementation phase."

    components = approach.get("key_components", [])
    components_section = "\n".join(f"- {c}" for c in components) if components else "TBD"

    data_flow = approach.get("data_flow", "") or ""
    if not data_flow:
        data_flow = "TBD — see implementation plan."

    alternatives = []
    for p in proposals.get("proposals", []):
        if p.get("approach") != chosen_approach:
            pname = p.get("name") or "Approach %d" % p.get("approach", 0)
            pdesc = p.get("description", "") or ""
            alternatives.append("### %s\n%s" % (pname, pdesc))
    alternatives_section = "\n\n".join(alternatives) if alternatives else "None documented."

    constraints_section = "\n".join(f"- {c}" for c in constraints) if constraints else "TBD — document during implementation."

    criteria_lines = []
    if args.criteria:
        criteria_lines = [f"- [ ] {c}" for c in args.criteria]
    criteria_section = "\n".join(criteria_lines) if criteria_lines else "- [ ] TBD"

    questions = approach.get("open_questions", [])
    questions_section = "\n".join(f"- {q}" for q in questions) if questions else "None."

    risks_lines = []
    risk_text = approach.get("risk", "")
    if risk_text:
        risks_lines.append(f"- Risk level: {risk_text}")
    if proposals.get("proposals"):
        for p in proposals["proposals"]:
            if p.get("approach") == chosen_approach:
                for risk_item in p.get("cons", []):
                    risks_lines.append(f"- {risk_item}")
    risks_section = "\n".join(risks_lines) if risks_lines else "Document during implementation."

    design_md = _DESIGN_MD_TEMPLATE.format(
        session_id=session_dir.name,
        goal=goal,
        status=review.get("verdict", "pending") if args.include_review else "draft",
        created_at=now_iso(),
        context_section=context_section,
        scope_section=scope_section,
        approach_index=chosen_approach,
        approach_description=approach.get("description", "TBD"),
        components_section=components_section,
        data_flow_section=data_flow,
        alternatives_section=alternatives_section,
        constraints_section=constraints_section,
        criteria_section=criteria_section,
        questions_section=questions_section,
        risks_section=risks_section,
    )

    # Write design.md
    design_path = session_dir / "design.md"
    write_text(design_path, design_md)

    # Update manifest
    manifest["status"] = review.get("verdict", "finalized")
    manifest["design_md"] = str(design_path)
    write_json(manifest_path, manifest)

    # Log event
    write_json(session_dir / "events.jsonl", {
        "timestamp": now_iso(),
        "type": "design_finalized",
        "phase": "design",
        "data": {
            "design_path": str(design_path),
            "chosen_approach": chosen_approach,
            "review_verdict": review.get("verdict", "none"),
        },
    })

    print(json.dumps({
        "ok": True,
        "design_path": str(design_path),
        "session_dir": str(session_dir),
        "chosen_approach": chosen_approach,
        "review_verdict": review.get("verdict", "none"),
        "design_md": design_md,
    }, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Design agent: structured architecture/design for HCW",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # init
    p = sub.add_parser("init", help="Create a new design session")
    p.add_argument("--goal", required=True, help="What we're designing")
    p.add_argument("--context", help="Project context / constraints")
    p.add_argument("--constraints", nargs="*", default=[], help="Design constraints")
    p.add_argument("--output", default=".hcw/sessions", help="Output directory")
    p.add_argument("--session-id", help="Override session ID")
    p.set_defaults(func=cmd_init)

    # explore
    p = sub.add_parser("explore", help="Scan codebase for design context")
    p.add_argument("--dir", required=True, help="Target project directory")
    p.add_argument("--session", help="Design session directory to save artifacts")
    p.add_argument("--max-files", type=int, default=500, help="Max files to scan")
    p.set_defaults(func=cmd_explore)

    # propose
    p = sub.add_parser("propose", help="Generate design proposal stubs")
    p.add_argument("--goal", required=True, help="Design goal")
    p.add_argument("--context", help="Design context")
    p.add_argument("--approaches", type=int, default=2, help="Number of approaches (2-3)")
    p.add_argument("--session", help="Design session directory")
    p.add_argument("--recommend", type=int, help="Recommended approach index")
    p.set_defaults(func=cmd_propose)

    # review
    p = sub.add_parser("review", help="Review a design.md for completeness")
    p.add_argument("--design", required=True, help="Path to design.md")
    p.add_argument("--session", help="Design session directory to save review")
    p.set_defaults(func=cmd_review)

    # finalize
    p = sub.add_parser("finalize", help="Produce final design.md from artifacts")
    p.add_argument("--session", required=True, help="Design session directory")
    p.add_argument("--goal", help="Override goal from manifest")
    p.add_argument("--scope", nargs="*", help="Scope items")
    p.add_argument("--criteria", nargs="*", help="Acceptance criteria")
    p.add_argument("--include-review", action="store_true", help="Include review verdict in status")
    p.set_defaults(func=cmd_finalize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
