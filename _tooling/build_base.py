#!/usr/bin/env python3
"""
Assemble BASE.md — the single universal companion file — from the four
methodology sources.

BASE.md is GENERATED. Never hand-edit it. The methodology/ files are the
authoritative sources; this script concatenates them into one attachable
file, rewrites sibling cross-links into in-file "Part N" references, and
appends the universal renderer block (the same sentinel-delimited block
that append_renderer.py embeds into every standalone/ file).

Usage:
    python3 _tooling/build_base.py            # (re)write BASE.md
    python3 _tooling/build_base.py --check    # exit 1 if BASE.md is out of sync (CI)
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "BASE.md"

SENTINEL_BEGIN = "<!-- BEGIN_RENDERER_APPENDIX -->"
SENTINEL_END = "<!-- END_RENDERER_APPENDIX -->"

# (source file, original H1, Part heading that replaces it)
PARTS = [
    (
        "audit-defensible-writing.md",
        "# Audit-Defensible Writing",
        "# Part 1 — Voice: Audit-Defensible Writing",
    ),
    (
        "analytical-patterns.md",
        "# Analytical Patterns",
        "# Part 2 — Method: Analytical Patterns",
    ),
    (
        "output-quality-standards.md",
        "# Output Quality Standards",
        "# Part 3 — Quality Bar: Output Standards",
    ),
]

# How sibling-file mentions read once everything lives in one file.
PART_NAMES = {
    "audit-defensible-writing.md": "Part 1 — Voice (in this file)",
    "analytical-patterns.md": "Part 2 — Method (in this file)",
    "output-quality-standards.md": "Part 3 — Quality Bar (in this file)",
    "report-templates.md": "Part 4 — Renderer (in this file)",
}

HEADER = """\
# BASE — the universal companion file

> **The two-file rule.** Any prompt in this toolkit works pasted on its own.
> Attach **this one file** alongside it and you get the full quality system —
> the audit-defensible voice, the analytical discipline, the per-deliverable
> quality floor, and the Word / Excel / PDF / HTML renderer. One prompt +
> `BASE.md`. **Never a third file.**

This file is the entire `methodology/` framework consolidated into a single
attachable document, for environments where attaching multiple files is
costly or impossible — a Copilot chat with no file system, a locked-down work
machine, a one-shot share with a teammate.

**Three ways to load it:**

1. **Attach per task** — attach this file plus one prompt file (or paste both). Done.
2. **Set once as agent instructions** — paste this file into Copilot agent custom
   instructions, Claude Project instructions, or a ChatGPT custom GPT. Every task
   after that needs only the thin prompt.
3. **Repo-level** — drop the contents into `.github/copilot-instructions.md` in a
   working repository.

| Part | What it governs |
|------|-----------------|
| **Part 1 — Voice** | How findings are written down: sourcing, hedging, fact vs. allegation |
| **Part 2 — Method** | How analysis is structured: severity, source hierarchy, confidence, fallbacks |
| **Part 3 — Quality Bar** | The floor every deliverable type must clear before it ships |
| **Part 4 — Renderer** | How to produce a Word / Excel / PDF / interactive-HTML deliverable |

When this file accompanies a task prompt, treat every rule below as binding
instructions, not background reading. Where a task prompt and this file
conflict, the task prompt wins — it carries the task-specific scope.

---

"""

FOOTER = """

---

*GENERATED FILE — do not hand-edit. Sources: [`methodology/`](methodology/)
(`audit-defensible-writing.md`, `analytical-patterns.md`,
`output-quality-standards.md`, and the renderer block of
`report-templates.md`). Rebuild: `python3 _tooling/build_base.py` from the
repo root. CI fails if this file drifts from its sources.*
"""


def _rewrite_sibling_links(text: str) -> str:
    """Rewrite links/mentions of sibling methodology files into Part references."""
    for fname, part in PART_NAMES.items():
        # Markdown links whose target is the sibling file (any label form)
        text = re.sub(
            r"\[[^\]]*\]\((?:\./)?" + re.escape(fname) + r"\)",
            f"**{part}**",
            text,
        )
        # Bare backticked mentions
        text = text.replace(f"`{fname}`", f"**{part}**")
    return text


def _part_body(fname: str, h1: str, new_h1: str) -> str:
    text = (ROOT / "methodology" / fname).read_text()
    if h1 not in text:
        raise SystemExit(f"FATAL: expected H1 {h1!r} not found in methodology/{fname}")
    text = text.replace(h1, new_h1, 1)
    return _rewrite_sibling_links(text).strip("\n")


def _renderer_block() -> str:
    text = (ROOT / "methodology" / "report-templates.md").read_text()
    start = text.find(SENTINEL_BEGIN)
    end = text.find(SENTINEL_END)
    if start == -1 or end == -1 or end < start:
        raise SystemExit(
            "FATAL: renderer sentinels not found in methodology/report-templates.md"
        )
    inner = text[start + len(SENTINEL_BEGIN): end].strip("\n")
    return _rewrite_sibling_links(inner)


def build() -> str:
    sections = [HEADER]
    for fname, h1, new_h1 in PARTS:
        sections.append(_part_body(fname, h1, new_h1))
        sections.append("\n\n---\n\n")
    sections.append(
        "# Part 4 — Renderer: Word / Excel / PDF / HTML deliverables\n\n"
        "When the user asks for a formatted deliverable, apply the renderer "
        "below to the analysis already produced. It defines four modes, a "
        "shared style standard, and working code skeletons.\n\n"
    )
    sections.append(_renderer_block())
    sections.append(FOOTER)
    return "".join(sections)


def main() -> int:
    content = build()
    if "--check" in sys.argv:
        if not OUT.exists():
            print("FAIL: BASE.md does not exist. Run: python3 _tooling/build_base.py")
            return 1
        if OUT.read_text() != content:
            print("FAIL: BASE.md is out of sync with methodology/ sources. "
                  "Run: python3 _tooling/build_base.py")
            return 1
        print("OK: BASE.md is in sync with methodology/ sources.")
        return 0
    OUT.write_text(content)
    lines = content.count("\n")
    print(f"wrote BASE.md ({lines} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
