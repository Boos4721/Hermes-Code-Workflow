#!/usr/bin/env python3
"""Design agent: structured architecture/design phase for Hermes Code Workflow.

Inspired by huashu-design methodology:
  - design-context: deep codebase scan → extract exact architecture values
  - Junior Designer: surface assumptions before committing to design
  - Variations by dimension: each approach explores a distinct architectural axis
  - Structured critique: 5-dimension scoring with prioritized fixes
  - Quick Wins: review output includes highest-impact repair list

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
# init — create design session (huashu: start with context questions)
# ---------------------------------------------------------------------------

_DESIGN_QUESTIONS = [
    "你有现成的设计文档/架构图吗？在哪？",
    "有 codebase 可以读吗？关键目录在哪？",
    "有性能/安全/兼容性方面的硬约束吗？",
    "有参考竞品或已有实现吗？",
    "scope：改动多少文件？影响哪些模块？",
]


def cmd_init(args: argparse.Namespace) -> None:
    sid = args.session_id or session_id()
    session_dir = Path(args.output) if args.output.endswith(".md") else Path(args.output) / sid
    if str(session_dir).endswith(".md"):
        session_dir = session_dir.parent

    (session_dir / "exploration").mkdir(parents=True, exist_ok=True)

    manifest = {
        "session_id": sid,
        "type": "design",
        "created_at": now_iso(),
        "goal": args.goal,
        "context": args.context or "",
        "constraints": args.constraints or [],
        "assumptions": [],
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

    # Junior Designer: always surface questions
    output = {
        "ok": True,
        "session_id": sid,
        "session_dir": str(session_dir),
        "goal": args.goal,
        "status": "init",
    }
    if args.ask_questions:
        output["questions"] = _DESIGN_QUESTIONS

    print(json.dumps(output, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# explore — deep codebase scan (huashu: extract exact values from codebase)
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

_ARCHITECTURE_MARKERS = {
    "routes": [r"router\.(get|post|put|delete|patch)\(", r"@app\.(get|post|put|delete)"],
    "models": [r"class \w+\(.*Model.*\)", r"@dataclass", r"@Entity"],
    "services": [r"class \w+Service", r"def \w+_service"],
    "middleware": [r"@app\.middleware", r"middleware", r"interceptor"],
    "handlers": [r"def handle[r]?\(", r"async def \w+\(.*Request"],
    "config": [r"(DATABASE|API|SECRET|HOST|PORT|DEBUG)\s*[:=]"],
    "errors": [r"class \w+Error\b", r"raise\s+\w+Error"],
    "tests": [r"(def test_|class \w+Test)"],
}


def _should_exclude(path: str) -> bool:
    parts = Path(path).parts
    return any(p in parts or p in path for p in _EXCLUDE_PATTERNS)


def _read_file_safe(path: Path) -> str | None:
    try:
        if path.stat().st_size > 256 * 1024:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None


def cmd_explore(args: argparse.Namespace) -> None:
    target = Path(args.dir).resolve()
    if not target.is_dir():
        print(json.dumps({"ok": False, "error": f"not a directory: {target}"}), file=sys.stderr)
        raise SystemExit(1)

    structure: dict[str, list[dict[str, Any]]] = {}
    all_files: list[Path] = []
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
            all_files.append(f)
            total_files += 1
            if args.max_files and total_files >= args.max_files:
                break
        if args.max_files and total_files >= args.max_files:
            break

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
    }
    detected: list[str] = []
    for lang, exts in lang_hints.items():
        if extensions & set(exts):
            detected.append(lang)

    # File overview by extension
    overview: dict[str, dict[str, Any]] = {}
    for ext, files in sorted(structure.items()):
        ext_name = ext if ext else "(no ext)"
        overview[ext_name] = {
            "count": len(files),
            "total_size_kb": round(sum(f["size"] for f in files) / 1024, 1),
            "sample_files": [f["path"] for f in files[:5]],
        }

    # Entry points
    entry_points: list[str] = []
    for marker in ("main.py", "app.py", "cli.py", "index.js", "index.ts", "main.rs", "main.go",
                   "manage.py", "wsgi.py", "asgi.py", "cmd/"):
        matches = list(target.rglob(marker))
        for m in matches:
            if not _should_exclude(str(m)):
                entry_points.append(str(m.relative_to(target)))

    # Dependency files
    dep_files: list[str] = []
    for dep in ("requirements.txt", "pyproject.toml", "package.json", "Cargo.toml",
                "go.mod", "Gemfile", "build.gradle", "pom.xml"):
        f = target / dep
        if f.exists():
            dep_files.append(dep)

    # ----- huashu: deep architecture scan — extract exact values -----
    arch_scan: dict[str, list[dict[str, Any]]] = {}
    code_files = [f for f in all_files if f.suffix in (".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".java", ".kt")]
    for f in code_files:
        content = _read_file_safe(f)
        if not content:
            continue
        rel = str(f.relative_to(target))
        for category, patterns in _ARCHITECTURE_MARKERS.items():
            for pat in patterns:
                for m in re.finditer(pat, content, re.MULTILINE):
                    line_num = content[:m.start()].count("\n") + 1
                    arch_scan.setdefault(category, []).append({
                        "file": rel,
                        "line": line_num,
                        "match": m.group(0)[:120],
                    })

    # ----- huashu: config extraction — lift exact values -----
    config_values: dict[str, str] = {}
    config_files = list(target.rglob("*.yaml")) + list(target.rglob("*.yml")) + \
                   list(target.rglob("*.toml")) + list(target.rglob("*.json")) + \
                   list(target.rglob("*.env")) + list(target.rglob(".env.example"))
    for cf in config_files:
        if _should_exclude(str(cf)):
            continue
        content = _read_file_safe(cf)
        if not content:
            continue
        # Extract key=value pairs from env-like files
        for m in re.finditer(r'^\s*(\w+)\s*[=:]\s*(.+?)\s*$', content, re.MULTILINE):
            k, v = m.group(1), m.group(2).strip().strip('"').strip("'")
            if k.startswith("#") or len(v) > 60:
                continue
            if k in ("SECRET_KEY", "API_KEY", "PASSWORD", "TOKEN"):
                continue
            config_values[k] = v

    result = {
        "ok": True,
        "target": str(target),
        "total_files": min(total_files, args.max_files or total_files),
        "languages_detected": detected,
        "file_overview": overview,
        "entry_points": entry_points,
        "dependency_files": dep_files,
        "architecture_scan": {k: v[:20] for k, v in arch_scan.items()},
        "config_values": config_values,
        "scanned_at": now_iso(),
    }

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
            "data": {
                "files_scanned": result["total_files"],
                "languages": detected,
                "config_keys": list(config_values.keys()),
                "arch_categories": list(arch_scan.keys()),
            },
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# propose — generate approach stubs with distinct architectural dimensions
# (huashu: variations explore different axes, not just numbered alternatives)
# ---------------------------------------------------------------------------

_ARCHITECTURAL_DIMENSIONS = [
    {
        "id": "modularity",
        "label": "模块拆分粒度",
        "description": "Monolith vs micro-services vs modular monolith",
    },
    {
        "id": "data_flow",
        "label": "数据流风格",
        "description": "同步请求-响应 vs 事件驱动 vs CQRS vs 流式",
    },
    {
        "id": "state_management",
        "label": "状态管理",
        "description": "无状态 + 外部存储 vs 有状态 vs 分布式缓存",
    },
    {
        "id": "error_resilience",
        "label": "容错策略",
        "description": "fail-fast vs graceful degradation vs circuit breaker",
    },
    {
        "id": "extensibility",
        "label": "扩展方式",
        "description": "插件系统 vs 配置驱动 vs 继承/多态",
    },
    {
        "id": "testing",
        "label": "测试策略",
        "description": "单元测试为主 vs 集成测试为主 vs 契约测试",
    },
]


def _approach_template(index: int, dimension: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "approach": index,
        "name": f"Approach {index}",
        "dimension": dimension or {"id": "", "label": "", "description": ""},
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
    count = max(2, min(args.approaches, 4))
    proposals: list[dict[str, Any]] = []

    for i in range(count):
        dim = _ARCHITECTURAL_DIMENSIONS[i % len(_ARCHITECTURAL_DIMENSIONS)] if count > 1 else None
        proposals.append(_approach_template(i + 1, dim))

    proposal_set = {
        "session_id": args.session or "",
        "goal": args.goal,
        "context": args.context or "",
        "generated_at": now_iso(),
        "approach_count": count,
        "available_dimensions": _ARCHITECTURAL_DIMENSIONS,
        "proposals": proposals,
        "recommendation": args.recommend if hasattr(args, "recommend") and args.recommend else None,
    }

    if args.session:
        session_dir = Path(args.session)
        session_dir.mkdir(parents=True, exist_ok=True)
        write_json(session_dir / "proposals.json", proposal_set)
        write_json(session_dir / "events.jsonl", {
            "timestamp": now_iso(),
            "type": "proposal",
            "phase": "design",
            "data": {
                "approach_count": count,
                "dimensions": [d["dimension"]["id"] for d in proposals if d.get("dimension")],
            },
        })

    print(json.dumps(proposal_set, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# assumptions — surface design assumptions before finalizing
# (huashu: Junior Designer shows assumptions before committing)
# ---------------------------------------------------------------------------

_ASSUMPTION_CATEGORIES = [
    "scope_impact",
    "dependency_assumptions",
    "performance_expectations",
    "compatibility_requirements",
    "deployment_model",
    "data_volume_projection",
]


def cmd_assumptions(args: argparse.Namespace) -> None:
    assumptions: list[dict[str, str]] = []
    if args.items:
        for item in args.items:
            parts = item.split(":", 1)
            if len(parts) == 2:
                assumptions.append({"category": parts[0], "assumption": parts[1]})
            else:
                assumptions.append({"category": "general", "assumption": parts[0]})

    open_questions: list[str] = args.open_questions or []

    result = {
        "session_id": args.session or "",
        "assumptions": assumptions,
        "open_questions": open_questions,
        "categories": _ASSUMPTION_CATEGORIES,
        "generated_at": now_iso(),
    }

    if args.session:
        session_dir = Path(args.session)
        session_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = session_dir / "manifest.json"
        if manifest_path.exists():
            manifest = read_json(manifest_path)
            manifest["assumptions"] = assumptions
            manifest["open_questions"] = open_questions
            write_json(manifest_path, manifest)
        write_json(session_dir / "assumptions.json", result)
        write_json(session_dir / "events.jsonl", {
            "timestamp": now_iso(), "type": "assumptions",
            "phase": "design",
            "data": {"assumption_count": len(assumptions), "question_count": len(open_questions)},
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# review — 5-dimension structured critique (huashu: multi-dim scoring + quick wins)
# ---------------------------------------------------------------------------

_DESIGN_DIMENSION_CHECKS = [
    {
        "id": "architectural_coherence",
        "label": "架构一致性",
        "weight": 0.25,
        "description": "整体架构风格是否统一，组件职责是否清晰",
        "scoring": {
            9: "所有组件有明确职责边界，无跨层调用，架构风格纯粹",
            7: "整体一致，偶有1-2处跨层引用",
            5: "能看出架构意图但执行不彻底，混合了多种风格",
            3: "职责混乱，组件间耦合严重",
            1: "没有清晰的架构",
        },
    },
    {
        "id": "modularity",
        "label": "模块化程度",
        "weight": 0.20,
        "description": "模块间耦合度、内聚性、接口清晰度",
        "scoring": {
            9: "高内聚低耦合，接口契约清晰，可独立测试每个模块",
            7: "模块化好，偶有循环依赖或模糊边界",
            5: "有模块划分但耦合度偏高，接口不够稳定",
            3: "模块界限模糊，大量跨模块引用",
            1: "单块代码，无模块划分",
        },
    },
    {
        "id": "scalability",
        "label": "可扩展性",
        "weight": 0.20,
        "description": "新增功能/组件的难度、对现有代码的影响范围",
        "scoring": {
            9: "新功能只需新增文件，不修改现有核心代码",
            7: "新功能可能改1-2处现有代码，影响可控",
            5: "新功能需要修改多处现有代码",
            3: "每次变更都会引起连锁修改",
            1: "无法扩展，任何新增都需要重写",
        },
    },
    {
        "id": "maintainability",
        "label": "可维护性",
        "weight": 0.20,
        "description": "代码可读性、调试难度、文档完整度",
        "scoring": {
            9: "有完整的错误处理/日志/指标，组件可独立排查问题",
            7: "有错误处理和日志，debug信息涵盖主要场景",
            5: "基本错误处理，异常场景覆盖不全",
            3: "错误处理缺失，debug困难",
            1: "没有错误处理机制",
        },
    },
    {
        "id": "testability",
        "label": "可测试性",
        "weight": 0.15,
        "description": "单元测试/集成测试的便利性、mock难度",
        "scoring": {
            9: "所有依赖可mock，纯函数比例高，可写无状态测试",
            7: "大部分组件可mock，次要组件耦合度高",
            5: "需要真实依赖才能测试，集成测试为主",
            3: "测试困难，需要大量环境准备",
            1: "几乎不可测试",
        },
    },
]


def cmd_review(args: argparse.Namespace) -> None:
    design_path = Path(args.design)
    if not design_path.exists():
        print(json.dumps({"ok": False, "error": f"design file not found: {design_path}"}),
              file=sys.stderr)
        raise SystemExit(1)

    content = design_path.read_text(encoding="utf-8")

    # Score each dimension
    scores: list[dict[str, Any]] = []
    total_weighted = 0.0
    total_weight = 0.0

    for dim in _DESIGN_DIMENSION_CHECKS:
        score = args.scores.get(dim["id"]) if hasattr(args, "scores") else None
        if not score:
            score = 5
        scores.append({
            "dimension": dim["id"],
            "label": dim["label"],
            "score": score,
            "weight": dim["weight"],
            "max_score": 10,
            "description": dim["description"],
            "scoring_guide": dim["scoring"],
        })
        total_weighted += score * dim["weight"]
        total_weight += dim["weight"]

    overall = round(total_weighted / total_weight, 1) if total_weight > 0 else 0

    # Quick wins — highest-impact fixes (huashu: prioritized fix list)
    quick_wins: list[dict[str, str]] = []
    if args.fixes:
        for fix in args.fixes:
            parts = fix.split("|", 2)
            entry = {
                "priority": parts[0] if len(parts) >= 1 else "medium",
                "issue": parts[1] if len(parts) >= 2 else "",
                "fix": parts[2] if len(parts) >= 3 else "",
            }
            quick_wins.append(entry)

    verdict = "excellent" if overall >= 8 else "good" if overall >= 6 else "needs-work" if overall >= 4 else "poor"

    review_result = {
        "ok": verdict not in ("needs-work", "poor"),
        "design_file": str(design_path),
        "overall_score": overall,
        "max_score": 10,
        "verdict": verdict,
        "dimensions": scores,
        "quick_wins": quick_wins,
        "reviewed_at": now_iso(),
    }

    if args.session:
        session_dir = Path(args.session)
        session_dir.mkdir(parents=True, exist_ok=True)
        write_json(session_dir / "review.json", review_result)
        write_json(session_dir / "events.jsonl", {
            "timestamp": now_iso(), "type": "design_review",
            "phase": "design",
            "data": {"verdict": verdict, "overall_score": overall, "quick_wins": len(quick_wins)},
        })

    print(json.dumps(review_result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# finalize — produce design.md with assumptions + quick wins
# (huashu: include context, assumptions, and action items)
# ---------------------------------------------------------------------------

_DESIGN_MD_TEMPLATE = """# Design: {goal}

- **Session**: `{session_id}`
- **Status**: {status}
- **Created**: {created_at}

## Goal

{goal}

{context_section}
## Assumptions

{assumptions_section}

## Scope

{scope_section}

## Approach {approach_index}: {approach_name}

{dimension_section}
### Description

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

## Review

- **Overall Score**: {review_score}/10 ({review_verdict})
- **Quick Wins**:
{quick_wins_section}
"""


def cmd_finalize(args: argparse.Namespace) -> None:
    session_dir = Path(args.session)
    manifest_path = session_dir / "manifest.json"
    proposals_path = session_dir / "proposals.json"
    review_path = session_dir / "review.json"
    assumptions_path = session_dir / "assumptions.json"

    manifest = read_json(manifest_path) if manifest_path.exists() else {}

    proposals_data = {}
    if proposals_path.exists():
        try:
            proposals_data = read_json(proposals_path)
        except Exception:
            proposals_data = {}

    review = {}
    if review_path.exists():
        try:
            review = read_json(review_path)
        except Exception:
            review = {}

    assumptions_data = {}
    if assumptions_path.exists():
        try:
            assumptions_data = read_json(assumptions_path)
        except Exception:
            assumptions_data = {}

    goal = manifest.get("goal", args.goal or "(goal not set)")
    constraints = manifest.get("constraints", [])

    chosen_approach = 1
    if proposals_data.get("proposals"):
        chosen_approach = proposals_data.get("recommendation") or 1

    approach = {}
    for p in proposals_data.get("proposals", []):
        if p.get("approach") == chosen_approach:
            approach = p
            break

    context_section = manifest.get("context", "") or ""
    if context_section:
        context_section = "## Context\n\n%s\n" % context_section

    # Assumptions (huashu: Junior Designer surfaces them)
    all_assumptions = manifest.get("assumptions", assumptions_data.get("assumptions", []))
    if all_assumptions:
        assumptions_section = "\n".join("- [%s] %s" % (a.get("category", "?"), a.get("assumption", ""))
                                       for a in all_assumptions)
    else:
        assumptions_section = "TBD — document before implementation."

    scope_lines = []
    if args.scope:
        scope_lines = ["- " + s for s in args.scope]
    elif approach.get("key_components"):
        scope_lines = ["- " + c for c in approach["key_components"]]
    scope_section = "\n".join(scope_lines) if scope_lines else "TBD — define in implementation phase."

    approach_name = approach.get("name", "Approach %d" % chosen_approach)

    dimension = approach.get("dimension", {})
    if dimension and dimension.get("label"):
        dimension_section = "**设计轴**: %s — %s\n" % (dimension["label"], dimension.get("description", ""))
    else:
        dimension_section = ""

    components = approach.get("key_components", [])
    components_section = "\n".join("- " + c for c in components) if components else "TBD"

    data_flow = approach.get("data_flow", "") or ""
    if not data_flow:
        data_flow = "TBD — see implementation plan."

    alternatives = []
    for p in proposals_data.get("proposals", []):
        if p.get("approach") != chosen_approach:
            pname = p.get("name") or "Approach %d" % p.get("approach", 0)
            pdesc = p.get("description", "") or ""
            alternatives.append("### %s\n%s" % (pname, pdesc))
    alternatives_section = "\n\n".join(alternatives) if alternatives else "None documented."

    cstr_section = "\n".join("- " + c for c in constraints) if constraints else "TBD — document during implementation."

    criteria_lines = []
    if args.criteria:
        criteria_lines = ["- [ ] " + c for c in args.criteria]
    criteria_section = "\n".join(criteria_lines) if criteria_lines else "- [ ] TBD"

    questions = approach.get("open_questions", [])
    questions_section = "\n".join("- " + q for q in questions) if questions else "None."
    all_questions = assumptions_data.get("open_questions", [])
    if all_questions:
        qs = "\n".join("- " + q for q in all_questions)
        if questions_section == "None.":
            questions_section = qs
        else:
            questions_section += "\n" + qs

    risks_lines = []
    risk_text = approach.get("risk", "")
    if risk_text:
        risks_lines.append("- Risk level: %s" % risk_text)
    if proposals_data.get("proposals"):
        for p in proposals_data["proposals"]:
            if p.get("approach") == chosen_approach:
                for risk_item in p.get("cons", []):
                    risks_lines.append("- " + risk_item)
    risks_section = "\n".join(risks_lines) if risks_lines else "Document during implementation."

    # Review section
    score_dims = review.get("dimensions", [])
    overall_score = review.get("overall_score", "?")
    review_verdict = review.get("verdict", "pending")
    quick_wins = review.get("quick_wins", [])

    if quick_wins:
        qw_lines = []
        for qw in quick_wins:
            pri = qw.get("priority", "medium")
            issue = qw.get("issue", "")
            fix = qw.get("fix", "")
            qw_lines.append("  - [%s] %s: %s" % (pri, issue, fix))
        quick_wins_section = "\n".join(qw_lines)
    else:
        quick_wins_section = "  - (none documented)"

    design_md = _DESIGN_MD_TEMPLATE.format(
        session_id=session_dir.name,
        goal=goal,
        status=review.get("verdict", "draft") if args.include_review else "draft",
        created_at=now_iso(),
        context_section=context_section,
        assumptions_section=assumptions_section,
        scope_section=scope_section,
        approach_index=chosen_approach,
        approach_name=approach_name,
        dimension_section=dimension_section,
        approach_description=approach.get("description", "TBD"),
        components_section=components_section,
        data_flow_section=data_flow,
        alternatives_section=alternatives_section,
        constraints_section=cstr_section,
        criteria_section=criteria_section,
        questions_section=questions_section,
        risks_section=risks_section,
        review_score=overall_score,
        review_verdict=review_verdict,
        quick_wins_section=quick_wins_section,
    )

    design_path = session_dir / "design.md"
    write_text(design_path, design_md)

    manifest["status"] = review.get("verdict", "finalized")
    manifest["design_md"] = str(design_path)
    write_json(manifest_path, manifest)

    write_json(session_dir / "events.jsonl", {
        "timestamp": now_iso(), "type": "design_finalized",
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
    }, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Design agent: structured architecture/design for HCW (huashu-inspired)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # init
    p = sub.add_parser("init", help="Create a new design session")
    p.add_argument("--goal", required=True, help="What we're designing")
    p.add_argument("--context", help="Project context / constraints")
    p.add_argument("--constraints", nargs="*", default=[], help="Design constraints")
    p.add_argument("--output", default=".hcw/sessions", help="Output directory")
    p.add_argument("--session-id", help="Override session ID")
    p.add_argument("--ask-questions", action="store_true",
                   help="Print context-gathering questions (huashu: always ask)")
    p.set_defaults(func=cmd_init)

    # explore
    p = sub.add_parser("explore", help="Scan codebase for design context (huashu: deep scan)")
    p.add_argument("--dir", required=True, help="Target project directory")
    p.add_argument("--session", help="Design session directory to save artifacts")
    p.add_argument("--max-files", type=int, default=500, help="Max files to scan")
    p.set_defaults(func=cmd_explore)

    # propose
    p = sub.add_parser("propose", help="Generate design proposals by architectural dimension")
    p.add_argument("--goal", required=True, help="Design goal")
    p.add_argument("--context", help="Design context")
    p.add_argument("--approaches", type=int, default=2, help="Number of approaches (2-3)")
    p.add_argument("--session", help="Design session directory")
    p.add_argument("--recommend", type=int, help="Recommended approach index")
    p.set_defaults(func=cmd_propose)

    # assumptions (huashu: Junior Designer mode)
    p = sub.add_parser("assumptions", help="Surface design assumptions and open questions")
    p.add_argument("--session", required=True, help="Design session directory")
    p.add_argument("--items", nargs="*",
                   help="Assumptions as category:statement (e.g. 'scope_impact:only touches auth module')")
    p.add_argument("--open-questions", nargs="*", help="Open questions")
    p.set_defaults(func=cmd_assumptions)

    # review
    p = sub.add_parser("review", help="5-dimension design critique with scoring")
    p.add_argument("--design", required=True, help="Path to design.md")
    p.add_argument("--session", help="Design session directory")
    p.add_argument("--scores", nargs="*", default=[],
                   help="Dimension scores as dimension:score (e.g. modularity:7)")
    p.add_argument("--fixes", nargs="*", default=[],
                   help="Quick wins as priority|issue|fix (e.g. 'high|missing error handling|add error middleware')")
    p.set_defaults(func=cmd_review)

    # finalize
    p = sub.add_parser("finalize", help="Produce final design.md from all artifacts")
    p.add_argument("--session", required=True, help="Design session directory")
    p.add_argument("--goal", help="Override goal from manifest")
    p.add_argument("--scope", nargs="*", help="Scope items")
    p.add_argument("--criteria", nargs="*", help="Acceptance criteria")
    p.add_argument("--include-review", action="store_true", help="Include review verdict in status")
    p.set_defaults(func=cmd_finalize)

    args = parser.parse_args()

    # Pre-process scores for review command
    if args.cmd == "review" and args.scores:
        score_map: dict[str, int] = {}
        for s in args.scores:
            if ":" in s:
                k, v = s.split(":", 1)
                try:
                    score_map[k.strip()] = int(v.strip())
                except ValueError:
                    pass
        args.scores = score_map
    else:
        args.scores = {}

    args.func(args)


if __name__ == "__main__":
    main()
