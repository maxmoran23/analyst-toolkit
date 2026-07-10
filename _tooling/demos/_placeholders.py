#!/usr/bin/env python3
"""List the ordered placeholders in each prompt of a category, for demo authoring.

    python3 _tooling/demos/_placeholders.py <category>

Prints, per prompt, every {{PLACEHOLDER}} in order with its index — the exact
text a demo fill's `hint` must be a substring of. Read-only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PH = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    cat = ROOT / "prompts" / sys.argv[1]
    if not cat.is_dir():
        print(f"no such category: {cat}")
        return 2
    for f in sorted(cat.glob("*.md")):
        if f.name == "README.md":
            continue
        text = f.read_text(encoding="utf-8")
        idx = text.find("## The prompt")
        m = re.search(r"^```(\w+)\n(.*?)^```", text[idx:], re.DOTALL | re.MULTILINE)
        inner = m.group(2)
        phs = PH.findall(inner)
        print("=" * 78)
        print(f"{f.name}  ({len(phs)} placeholders)")
        for i, p in enumerate(phs, 1):
            print(f"  [{i}] {' '.join(p.split())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
