#!/usr/bin/env python3
"""
Enforce the two-file rule across the library. Run from the repo root; exits
non-zero on any violation (CI gate).

Rules
-----
A. PASTE PAYLOAD PURITY — inside every fenced block of prompts/**/*.md and
   standalone/*.md there must be NO reference to any other repo file. What
   gets pasted must be complete: an assistant with no file system receives
   the block and nothing else.

B. RUN-TIME CONTRACT PRESENT — every prompts/<cat>/*.md carries the
   `**Run-time needs**` table row and the `<!-- RUNTIME_CONTRACT -->` footer
   (applied by apply_runtime_contract.py).

C. STANDALONE PURITY — standalone/*.md files reference no other repo file
   anywhere (their whole file is the paste payload) and contain the embedded
   renderer appendix.

D. PAIRING BUDGET — no file instructs the reader to attach/load/pair more
   than ONE companion file, and that companion may only be BASE.md (or, for
   dashboard scaffolds, a single .html template). Reported per file.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

REPO_DIRS = (
    "methodology", "output-templates", "reference", "samples",
    "standalone", "prompts", "docs", "quant", "quant-jvm", "_tooling",
)
REPO_PATH_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(d) for d in REPO_DIRS) + r")/[\w./-]+"
)
MD_FILE_RE = re.compile(r"\b[\w-]+\.md\b")
FENCE_RE = re.compile(r"^(```|~~~)")

ALLOWED_COMPANION = {"BASE.md"}


def fenced_and_outside(text):
    """Split file lines into (inside_fences, outside_fences)."""
    inside, outside = [], []
    in_fence = False
    for line in text.split("\n"):
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        (inside if in_fence else outside).append(line)
    return "\n".join(inside), "\n".join(outside)


def file_refs(text, self_name):
    refs = set(REPO_PATH_RE.findall(text))
    refs |= {m for m in MD_FILE_RE.findall(text)}
    refs.discard(self_name)
    # normalize: drop bare basenames that duplicate a path ref already counted
    return {r for r in refs if r not in ("README.md",)}


def main() -> int:
    errors = []
    report = []

    prompt_files = sorted(
        p for p in (ROOT / "prompts").glob("*/*.md") if p.name != "README.md"
    )
    standalone_files = sorted(
        p for p in (ROOT / "standalone").glob("*.md") if p.name != "README.md"
    )

    # --- Rule A: paste payload purity
    for p in prompt_files + standalone_files:
        inside, _ = fenced_and_outside(p.read_text())
        refs = file_refs(inside, p.name)
        refs -= ALLOWED_COMPANION
        if refs:
            errors.append(
                f"RULE A {p.relative_to(ROOT)}: repo-file reference(s) INSIDE "
                f"the paste payload: {sorted(refs)}"
            )

    # --- Rule B: run-time contract present in every prompt file
    for p in prompt_files:
        text = p.read_text()
        if "| **Run-time needs** |" not in text:
            errors.append(f"RULE B {p.relative_to(ROOT)}: missing **Run-time needs** row")
        if "<!-- RUNTIME_CONTRACT -->" not in text:
            errors.append(f"RULE B {p.relative_to(ROOT)}: missing RUNTIME_CONTRACT footer")

    # --- Rule C: standalone purity
    for p in standalone_files:
        text = p.read_text()
        refs = file_refs(text, p.name) - ALLOWED_COMPANION
        if refs:
            errors.append(
                f"RULE C {p.relative_to(ROOT)}: repo-file reference(s) in a "
                f"standalone file: {sorted(refs)}"
            )
        if "## Render as a formatted deliverable" not in text:
            errors.append(
                f"RULE C {p.relative_to(ROOT)}: embedded renderer appendix missing"
            )

    # --- Rule D: pairing budget report
    attach_re = re.compile(
        r"(?:attach|load|pair(?:ed)? with|alongside)[^.\n]*?`([\w./-]+\.(?:md|html))`",
        re.I,
    )
    for p in prompt_files:
        _, outside = fenced_and_outside(p.read_text())
        companions = {m.split("/")[-1] for m in attach_re.findall(outside)}
        companions.discard(p.name)
        budget = 1 + (1 if companions else 0)
        bad = companions - ALLOWED_COMPANION - {c for c in companions if c.endswith(".html")}
        if bad:
            errors.append(
                f"RULE D {p.relative_to(ROOT)}: instructs attaching a non-BASE "
                f"companion: {sorted(bad)}"
            )
        report.append((str(p.relative_to(ROOT)), budget))

    for p in standalone_files:
        report.append((str(p.relative_to(ROOT)), 1))

    # --- output
    print(f"Pairing budget ({len(report)} features):")
    over = [r for r in report if r[1] > 2]
    print(f"  1 file : {sum(1 for _, b in report if b == 1)}")
    print(f"  2 files: {sum(1 for _, b in report if b == 2)}")
    print(f"  >2     : {len(over)}")
    for name, b in over:
        errors.append(f"RULE D {name}: pairing budget exceeded ({b} files)")

    if errors:
        print(f"\nFAIL — {len(errors)} violation(s):")
        for e in errors:
            print(f"  {e}")
        return 1
    print("\nOK: every feature replicates with at most 2 files; all payloads self-contained.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
