#!/usr/bin/env python3
"""
Content-hygiene gate for a public repository generalized from private tooling.
Run from the repo root; exits non-zero on any violation (CI gate).

Why this exists
---------------
This library was extracted from a private, employer-adjacent automation practice.
The two ways that leaks in are (1) an identifier shape copied across verbatim — a
workspace ID, a home-directory path, a credential — and (2) house style from the
private tooling that does not belong in a professional public artifact.

The companion repo (Claude-Agent-Fleet) enforces the same class of rules in
`tests/test_examples.py`. This is the analyst-toolkit equivalent; without it the
two repos hold their shared content to different bars.

Rules
-----
A. LEAK SHAPES (repo-wide, every text file) — no Slack workspace/channel/user ID
   shapes, no local home-directory paths, no private-fleet paths, no credential
   shapes. These are shapes, not names: the check is deliberately blind to intent.

B. NO EMOJI on the portable text surface (markdown + Python across the library).
   Typographic symbols the library legitimately uses are allowed: em/en dashes,
   arrows, box drawing, math operators, Greek letters. Pictographs, dingbats and
   check marks are not.

   Documented exemption: `samples/dashboards/*.html` are *rendered artifacts*, not
   prose. Their emoji are UI affordances (a light/dark toggle glyph, section
   icons), and the committed PNG previews under `samples/previews/` were
   screenshotted from them — stripping the glyphs would desync the images without
   re-rendering. The exemption is reported on every run, never silent.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

IGNORED_DIRS = {".git", "__pycache__", "node_modules", ".venv", "data", "previews"}
TEXT_SUFFIXES = {".md", ".py", ".html", ".kt", ".yml", ".yaml", ".txt", ".json"}

# Rendered artifacts, exempt from rule B only. See the module docstring.
EMOJI_EXEMPT = {"samples/dashboards"}

# Rule B applies to the prose/code surface, not to rendered output.
EMOJI_SUFFIXES = {".md", ".py", ".kt"}

LEAK_PATTERNS = [
    (r"\b[CFTUD]0[A-Z0-9]{8,}\b", "Slack workspace/channel/user ID shape"),
    (r"/Users/[a-z][\w.-]+", "local home-directory path"),
    (r"\bDesktop/Agents\b", "private-fleet path"),
    (r"\bsk-ant-[\w-]{8,}", "Anthropic API key shape"),
    (r"\bAKIA[0-9A-Z]{12,}", "AWS access-key shape"),
    (r"\bghp_[A-Za-z0-9]{20,}", "GitHub token shape"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}", "Slack token shape"),
]

# Pictographs, dingbats (incl. check marks), symbols-and-arrows supplements,
# regional indicators, and the emoji-presentation variation selector.
# Deliberately excludes the typographic symbols the library uses on purpose.
EMOJI_RE = re.compile(
    "["
    "\U0001f000-\U0001faff"
    "☀-➿"
    "⬀-⯿"
    "\U0001f1e6-\U0001f1ff"
    "️"
    "]"
)


def is_ignored(rel: Path) -> bool:
    return any(part in IGNORED_DIRS for part in rel.parts)


def is_emoji_exempt(rel: Path) -> bool:
    return any(str(rel).startswith(prefix) for prefix in EMOJI_EXEMPT)


def main() -> int:
    errors: list[str] = []
    self_path = Path(__file__).resolve()
    scanned = 0
    exempted: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(ROOT)
        if is_ignored(rel):
            continue
        # This file necessarily contains the very shapes it hunts for.
        if path.resolve() == self_path:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scanned += 1

        for pattern, label in LEAK_PATTERNS:
            for match in re.finditer(pattern, text):
                line = text[: match.start()].count("\n") + 1
                errors.append(f"RULE A {rel}:{line} {label}: {match.group()!r}")

        if path.suffix in EMOJI_SUFFIXES:
            found = sorted({c for c in EMOJI_RE.findall(text)})
            if found:
                codepoints = ", ".join(f"U+{ord(c):04X}" for c in found)
                errors.append(f"RULE B {rel}: emoji present ({codepoints})")
        elif is_emoji_exempt(rel) and EMOJI_RE.search(text):
            exempted.append(str(rel))

    print(f"Hygiene: scanned {scanned} text files")
    if exempted:
        print(f"Rule B exemptions in effect ({len(exempted)} rendered artifact(s)):")
        for item in sorted(exempted):
            print(f"  {item} — UI glyphs; PNG previews were screenshotted from these")

    if errors:
        print(f"\nFAIL — {len(errors)} violation(s):")
        for e in errors:
            print(f"  {e}")
        return 1
    print("OK: no leak shapes; no emoji on the portable text surface.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
