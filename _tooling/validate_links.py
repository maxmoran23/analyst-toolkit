#!/usr/bin/env python3
"""
Verify every relative markdown link in the repository resolves to a real path.
Run from the repo root; exits non-zero on any broken link (CI gate).

Why this exists
---------------
The `teams/` hubs, the prompt catalogs, and the docs are pure navigation layers
over the by-type folders. A renamed or deleted target breaks them silently: the
markdown still renders, the link just 404s on GitHub. Nothing else in CI reads
prose, so nothing else catches it.

Scope
-----
Checked:   relative link targets in every tracked *.md file.
Skipped:   absolute URLs (http/https/mailto), bare in-page anchors (#section),
           and anything under an ignored directory.

Anchors are stripped before resolution — this validates that the *file* exists,
not that a heading inside it does.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

IGNORED_DIRS = {".git", "__pycache__", "node_modules", ".venv", "data"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def main() -> int:
    broken: list[str] = []
    checked = 0
    files = 0

    for md in sorted(ROOT.rglob("*.md")):
        if is_ignored(md.relative_to(ROOT)):
            continue
        files += 1
        text = md.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if target.startswith(EXTERNAL_PREFIXES):
                continue
            # Drop any markdown link title (`path "Title"`) and the anchor.
            target = target.split(" ", 1)[0]
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            checked += 1
            if not (md.parent / path_part).resolve().exists():
                line = text[: match.start()].count("\n") + 1
                broken.append(f"{md.relative_to(ROOT)}:{line} -> {target}")

    print(f"Relative links: {checked} across {files} markdown files")
    if broken:
        print(f"\nFAIL — {len(broken)} broken link(s):")
        for item in broken:
            print(f"  {item}")
        return 1
    print("OK: every relative link resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
