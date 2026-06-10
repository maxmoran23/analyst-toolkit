#!/usr/bin/env python3
"""
Apply the run-time contract to every prompts/<category>/*.md file (READMEs
excluded). Idempotent — safe to re-run after editing any prompt file.

Two insertions per file:

1. A `**Run-time needs**` row in the metadata table, directly below the
   existing `**Pairs with**` row. If the row already exists it is replaced.

2. A run-time contract footer at end of file, delimited by the
   `<!-- RUNTIME_CONTRACT -->` sentinel. If the sentinel exists, everything
   from it to EOF is replaced.

Why: these files are read in two very different situations — browsed on
GitHub (where the cross-links are useful navigation) and attached cold to an
assistant with no file system (where an unexplained link reads as a missing
dependency). The contract makes the second case unambiguous: the prompt block
is complete as pasted, and BASE.md is the only companion file that ever adds
anything.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

RUNTIME_ROW = (
    "| **Run-time needs** | **None — the prompt block below is fully "
    "self-contained.** For the strict voice + a Word / Excel / PDF / HTML "
    "deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + "
    "`BASE.md`, never a third file. |"
)

SENTINEL = "<!-- RUNTIME_CONTRACT -->"

FOOTER = f"""{SENTINEL}

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
"""


def apply(path: Path) -> str:
    text = path.read_text()
    changed = []

    # 1. Run-time needs row — replace if present, else insert under Pairs with.
    row_pattern = re.compile(r"^\| \*\*Run-time needs\*\* \|.*\|$", re.M)
    if row_pattern.search(text):
        new = row_pattern.sub(RUNTIME_ROW, text)
        if new != text:
            changed.append("row updated")
        text = new
    else:
        pairs_pattern = re.compile(r"^(\| \*\*Pairs with\*\* \|.*\|)$", re.M)
        m = pairs_pattern.search(text)
        if not m:
            raise SystemExit(f"FATAL: no **Pairs with** row in {path}")
        text = text[: m.end()] + "\n" + RUNTIME_ROW + text[m.end():]
        changed.append("row inserted")

    # 2. Footer — replace from sentinel to EOF, else append.
    idx = text.find(SENTINEL)
    if idx != -1:
        new = text[:idx] + FOOTER
        if new != text:
            changed.append("footer updated")
        text = new
    else:
        text = text.rstrip("\n") + "\n\n" + FOOTER
        changed.append("footer appended")

    path.write_text(text)
    return ", ".join(changed) if changed else "no change"


def main() -> int:
    files = sorted(
        p for p in (ROOT / "prompts").glob("*/*.md") if p.name != "README.md"
    )
    if not files:
        raise SystemExit("FATAL: no prompt files found — run from the repo root")
    for p in files:
        print(f"{p.relative_to(ROOT)}: {apply(p)}")
    print(f"\n{len(files)} prompt files processed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
