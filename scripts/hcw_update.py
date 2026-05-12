#!/usr/bin/env python3
"""Update the installed Hermes Code Workflow skill from GitHub."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_RAW_BASE = "https://raw.githubusercontent.com/Boos4721/Hermes-Code-Workflow/master"
DEFAULT_SKILL_DEST = Path.home() / ".hermes/skills/software-development/hcw"

FILES_TO_SYNC = {
    "SKILL.md": "skills/hcw/SKILL.md",
    "references/python-adapters.md": "skills/hcw/references/python-adapters.md",
    "scripts/hcw_design.py": "scripts/hcw_design.py",
    "templates/design.template.md": "templates/design.template.md",
}


def fetch_text(url: str, timeout: int) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hcw_update/1.0",
            "Accept": "text/plain, text/markdown;q=0.9, */*;q=0.1",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def summarize_change(old: str | None, new: str) -> str:
    if old is None:
        return "created"
    if old == new:
        return "unchanged"
    return "updated"


def update_files(raw_base: str, dest: Path, timeout: int) -> dict[str, Any]:
    files: list[dict[str, str]] = []
    changed = False

    for relative_dest, relative_src in FILES_TO_SYNC.items():
        url = f"{raw_base.rstrip('/')}/{relative_src}"
        target = dest / relative_dest
        old_content = target.read_text(encoding="utf-8") if target.exists() else None
        new_content = fetch_text(url, timeout)
        status = summarize_change(old_content, new_content)
        if status in {"created", "updated"}:
            write_text(target, new_content)
            changed = True
        files.append({
            "path": str(target),
            "source": url,
            "status": status,
        })

    return {
        "ok": True,
        "changed": changed,
        "destination": str(dest),
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update the installed Hermes Code Workflow skill from GitHub"
    )
    parser.add_argument(
        "--raw-base",
        default=DEFAULT_RAW_BASE,
        help="raw GitHub base URL for this repo (default: %(default)s)",
    )
    parser.add_argument(
        "--dest",
        default=str(DEFAULT_SKILL_DEST),
        help="local Hermes skill directory to update (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="per-file HTTP timeout in seconds (default: %(default)s)",
    )
    args = parser.parse_args()

    try:
        result = update_files(args.raw_base, Path(args.dest).expanduser(), args.timeout)
    except urllib.error.HTTPError as exc:
        print(json.dumps({
            "ok": False,
            "error": f"HTTP {exc.code} while fetching {exc.url}",
        }, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    except urllib.error.URLError as exc:
        print(json.dumps({
            "ok": False,
            "error": f"network error: {exc.reason}",
        }, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
        }, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0)


if __name__ == "__main__":
    main()
