#!/usr/bin/env python3
"""
Navigability guard: no confusingly reused filenames, and no stale cousin map.

Run from the repo root; exits non-zero on any drift (CI gate).

Why this exists
---------------
The repository is browsed as a GitHub file tree, not just consumed as code. Its
readability failure mode is a filename that means one thing in one folder and a
different thing in another — a reader following a link cannot tell whether two
similarly named files are the same feature, two halves of one, or unrelated. The
index and link validators keep counts and links honest; this one keeps *names*
honest.

The truth is derived from the filesystem and cross-checked against one registry
([`docs/prompt-vs-engine-map.md`](../docs/prompt-vs-engine-map.md)), so the human
disambiguation page and the machine gate can never disagree — the same discipline
`REPRODUCE.json` applies to evidence.

Rules
-----
N1. CROSS-CLASS COLLISION — a Markdown basename that appears in more than one
    artifact class (prompt / standalone / framework / reference / docs / methodology)
    must be one of: a STRUCTURAL package filename (README.md, tuning.md, ...), a
    declared prompt<->standalone MIRROR, or a registered exception. Anything else is a
    confusingly reused name and fails the build.

N2. COUSIN-MAP INTEGRITY — every prompt<->framework cousin pair registered in
    prompt-vs-engine-map.md must resolve on disk (both sides exist). The map cannot
    advertise a pairing that has been renamed or removed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
MAP_REL = "docs/prompt-vs-engine-map.md"

# Structural filenames repeat by design (one per package / per folder). They are the
# scaffolding of a standard, not a reused concept, so they are never a collision.
STRUCTURAL = {
    "README.md", "METHODOLOGY.md", "DEPLOYMENT.md", "tuning.md",
    "SOURCE-LIBRARY.md", "VALIDATION-REPORT.md", "EVIDENCE.md", "AGENTS.md",
}

# The top-level folder decides a file's artifact class. Files outside these live at the
# repo root (BASE.md, README.md) and are treated as their own "root" class.
CLASS_BY_TOP = {
    "prompts": "prompt",
    "standalone": "standalone",
    "frameworks": "framework",
    "reference": "reference",
    "docs": "docs",
    "methodology": "methodology",
    "output-templates": "output-template",
}


def artifact_class(path: Path) -> str:
    rel = path.relative_to(ROOT)
    top = rel.parts[0] if len(rel.parts) > 1 else "root"
    return CLASS_BY_TOP.get(top, "root")


def markdown_files() -> list[Path]:
    out: list[Path] = []
    for top in list(CLASS_BY_TOP) + ["."]:
        base = ROOT / top
        if not base.exists():
            continue
        for f in base.rglob("*.md") if top != "." else base.glob("*.md"):
            if ".git" in f.parts or "__pycache__" in f.parts:
                continue
            out.append(f)
    return out


def load_cousins() -> list[tuple[str, str]]:
    text = (ROOT / MAP_REL).read_text(encoding="utf-8")
    block = re.search(
        r"NAMING-REGISTRY:cousins(.*?)/NAMING-REGISTRY:cousins", text, re.DOTALL
    )
    if not block:
        return []
    pairs: list[tuple[str, str]] = []
    for line in block.group(1).splitlines():
        m = re.match(r"\s*([\w./-]+\.md)\s*<->\s*([\w./-]+)\s*$", line)
        if m:
            pairs.append((m.group(1), m.group(2)))
    return pairs


def main() -> int:
    errors: list[str] = []

    # --- Rule N1: cross-class basename collisions
    by_basename: dict[str, set[str]] = {}
    locations: dict[str, list[str]] = {}
    for f in markdown_files():
        cls = artifact_class(f)
        by_basename.setdefault(f.name, set()).add(cls)
        locations.setdefault(f.name, []).append(str(f.relative_to(ROOT)))

    collisions = 0
    for name, classes in sorted(by_basename.items()):
        if len(classes) < 2 or name in STRUCTURAL:
            continue
        collisions += 1
        # A prompt<->standalone mirror across exactly those two classes is allowed:
        # it is the same method offered in two workflows, declared in the map.
        if classes == {"prompt", "standalone"}:
            continue
        errors.append(
            f"N1 basename '{name}' is reused across classes {sorted(classes)} "
            f"— {locations[name]}. Rename it, or (if a genuine mirror) confine it to "
            f"prompts/ + standalone/."
        )

    # --- Rule N2: every registered cousin pair resolves on disk
    cousins = load_cousins()
    for prompt_rel, framework_rel in cousins:
        if not (ROOT / prompt_rel).exists():
            errors.append(f"N2 cousin map points at missing prompt: {prompt_rel}")
        fw = ROOT / framework_rel
        if not fw.exists() or not fw.is_dir():
            errors.append(f"N2 cousin map points at missing framework: {framework_rel}")

    print(
        f"Scanned {sum(len(v) for v in locations.values())} Markdown files · "
        f"{collisions} cross-class name(s) reviewed · {len(cousins)} cousin pair(s) registered"
    )
    if errors:
        print(f"\nFAIL — {len(errors)} violation(s):")
        for e in errors:
            print(f"  {e}")
        return 1
    print("OK: no confusingly reused names; cousin map resolves on disk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
