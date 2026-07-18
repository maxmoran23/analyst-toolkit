#!/usr/bin/env python3
"""
Keep the navigation layer honest against the filesystem. Run from the repo root;
exits non-zero on any drift (CI gate).

Why this exists
---------------
This repository's recurring failure mode is not broken code — the framework
harnesses guard that. It is prose that quietly stops being true: a README that
advertises 39 prompts after 68 exist, a hub page promising a capability that
shipped two commits ago, an engine no index links to. Nothing read the prose, so
nothing caught it.

The fix mirrors the harness philosophy: derive the truth from the filesystem and
fail when a document disagrees.

Rules
-----
A. INDEX COMPLETENESS — every prompt file is linked from prompts/README.md;
   every prompt category is linked from prompts/README.md; every team hub is
   linked from teams/README.md; every framework package is linked from
   frameworks/README.md.

B. FRAMEWORK PACKAGE STANDARD — every frameworks/<pkg>/ ships the fixed set
   declared in frameworks/README.md: README.md, METHODOLOGY.md,
   run_validation.py, and a committed evidence/VALIDATION-REPORT.md.

C. DECLARED COUNTS — every registered numeric claim in the docs matches the
   count derived from disk. Claims are registered explicitly below rather than
   pattern-hunted, so a claim can never silently stop being checked: if someone
   rewords the sentence, the pattern stops matching and rule C fails loudly.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

WORD_NUMBERS = {
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
}


def counts() -> dict[str, int]:
    prompts_dir = ROOT / "prompts"
    categories = sorted(p for p in prompts_dir.iterdir() if p.is_dir())
    prompt_files = [
        f for c in categories for f in sorted(c.glob("*.md")) if f.name != "README.md"
    ]
    frameworks = sorted(
        p for p in (ROOT / "frameworks").iterdir() if p.is_dir() and p.name != "_lib"
    )
    hubs = [f for f in sorted((ROOT / "teams").glob("*.md")) if f.name != "README.md"]
    return {
        "prompts": len(prompt_files),
        "categories": len(categories),
        "frameworks": len(frameworks),
        "frameworks_minus_one": len(frameworks) - 1,
        "hubs": len(hubs),
    }


# (file, regex, [count-keys matched to capture groups in order])
# A capture group holding a word ("thirteen") is resolved through WORD_NUMBERS.
CLAIMS = [
    ("README.md", r"(\w+) \[team hubs\]\(teams/\)", ["hubs"]),
    ("README.md", r"(\w+) small, pure-standard-library scoring engines", ["frameworks"]),
    ("README.md", r"(\d+) paste-ready analytical prompt templates across (\d+) categories", ["prompts", "categories"]),
    ("README.md", r"\*\*(\d+) runnable scoring engines with validation evidence\*\*", ["frameworks"]),
    ("README.md", r"(\d+) hub pages, one per team", ["hubs"]),
    ("README.md", r"(\d+) prompts across (\d+) categories\.", ["prompts", "categories"]),
    ("prompts/README.md", r"(\d+) paste-ready analytical prompt templates across (\d+) categories", ["prompts", "categories"]),
    ("docs/how-the-system-works.md", r"There are (\d+) of them across (\d+) categories", ["prompts", "categories"]),
    ("docs/how-the-system-works.md", r"There are (\d+) of them\.", ["frameworks"]),
    ("docs/how-the-system-works.md", r"all (\d+) frameworks'", ["frameworks"]),
    ("docs/README.md", r"holds (\w+)\s+runnable scoring engines", ["frameworks"]),
    ("teams/README.md", r"(\d+) worked evidence packs", ["frameworks"]),
    ("teams/model-risk-governance.md", r"(\w+) worked, reproducible validation evidence packs", ["frameworks"]),
    ("teams/model-risk-governance.md", r"So do the other (\w+) —", ["frameworks_minus_one"]),
]

FRAMEWORK_REQUIRED = ["README.md", "METHODOLOGY.md", "run_validation.py", "evidence/VALIDATION-REPORT.md"]


def resolve(token: str) -> int | None:
    if token.isdigit():
        return int(token)
    return WORD_NUMBERS.get(token.lower())


def main() -> int:
    errors: list[str] = []
    n = counts()

    # --- Rule A: index completeness
    prompts_index = (ROOT / "prompts" / "README.md").read_text(encoding="utf-8")
    for category in sorted(p for p in (ROOT / "prompts").iterdir() if p.is_dir()):
        if f"{category.name}/" not in prompts_index:
            errors.append(f"RULE A prompts/README.md does not link category {category.name}/")
        for prompt in sorted(category.glob("*.md")):
            if prompt.name == "README.md":
                continue
            ref = f"{category.name}/{prompt.name}"
            if ref not in prompts_index:
                errors.append(f"RULE A prompts/README.md does not link {ref}")

    teams_index = (ROOT / "teams" / "README.md").read_text(encoding="utf-8")
    for hub in sorted((ROOT / "teams").glob("*.md")):
        if hub.name != "README.md" and f"({hub.name})" not in teams_index:
            errors.append(f"RULE A teams/README.md does not link {hub.name}")

    frameworks_index = (ROOT / "frameworks" / "README.md").read_text(encoding="utf-8")
    for pkg in sorted(p for p in (ROOT / "frameworks").iterdir() if p.is_dir() and p.name != "_lib"):
        if f"{pkg.name}/" not in frameworks_index:
            errors.append(f"RULE A frameworks/README.md does not link {pkg.name}/")

        # --- Rule B: package standard
        for required in FRAMEWORK_REQUIRED:
            if not (pkg / required).exists():
                errors.append(f"RULE B frameworks/{pkg.name}/ is missing {required}")

    # --- Rule C: declared counts
    checked = 0
    for rel, pattern, keys in CLAIMS:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"RULE C registered claim file missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(pattern, text)
        if not match:
            errors.append(
                f"RULE C {rel}: registered claim no longer matches — the sentence was "
                f"reworded, so its number stopped being checked. Pattern: {pattern!r}"
            )
            continue
        for group_index, key in enumerate(keys, start=1):
            claimed = resolve(match.group(group_index))
            checked += 1
            if claimed is None:
                errors.append(f"RULE C {rel}: cannot read number {match.group(group_index)!r}")
            elif claimed != n[key]:
                errors.append(
                    f"RULE C {rel}: claims {match.group(group_index)} for {key}, "
                    f"filesystem has {n[key]}"
                )

    print(
        f"Filesystem: {n['prompts']} prompts / {n['categories']} categories · "
        f"{n['frameworks']} frameworks · {n['hubs']} team hubs"
    )
    print(f"Registered numeric claims verified: {checked}")

    if errors:
        print(f"\nFAIL — {len(errors)} violation(s):")
        for e in errors:
            print(f"  {e}")
        return 1
    print("OK: indexes complete, package standard met, declared counts match disk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
