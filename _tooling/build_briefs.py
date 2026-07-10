#!/usr/bin/env python3
"""
Render the standalone brief onto every entry page. Run from the repo root.

    python3 _tooling/build_briefs.py            # write the briefs
    python3 _tooling/build_briefs.py --check    # CI: fail if a brief has drifted

Why this exists
---------------
A reader is rarely sent the repository. They are sent a *link* — to
`frameworks/tm-threshold-tuning/` or `prompts/fraud/`. Whatever GitHub renders at that
path is the whole of their first impression, and until now those pages assumed the
reader had already browsed everything else. `frameworks/README.md` literally opened
with "A different artifact class from the rest of this repository," which means nothing
to someone who has seen no other part of it.

Every entry page now carries a brief that answers, without a single click: who this is
for, the question it answers, what it never does, whether the data is real, and how to
check the numbers rather than believe them.

The brief is generated from the registries (`frameworks/REPRODUCE.json`,
`prompts/CATEGORIES.json`) and inserted between markers, so it stays consistent across
26 pages and cannot quietly rot. Everything outside the markers is hand-written and is
never touched.

Audience note
-------------
These pages are read by financial-crime and AML compliance professionals. They do not
need "SAR" or "PEP" explained to them; that would be condescending. They *do* deserve
plain language for the statistics and the engineering — so the recall claim is
explained in the vocabulary they already own: an attribute sample returning zero
exceptions does not prove a zero deviation rate, it bounds it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "frameworks"))

from _lib import attest  # noqa: E402

START = "<!-- STANDALONE-BRIEF -->"
END = "<!-- /STANDALONE-BRIEF -->"

SYNTHETIC = ('100% synthetic. Every person, entity, and account is fictional — the '
             'recurring institution is "Harborview Financial Group". No real customer, '
             'list entry, or transaction appears anywhere in this repository.')


def splice(text: str, block: str) -> str:
    """Insert or replace the marked block, leaving all hand-written prose untouched."""
    if START in text and END in text:
        head = text.split(START)[0]
        tail = text.split(END, 1)[1].lstrip("\n")
        return f"{head}{block}\n\n{tail}"
    # First insert: place it after the title matter, immediately before the first
    # `## ` section heading — the natural spot for an orientation block.
    # Anchor on whichever comes first: a `## ` section heading, or the start of the
    # first markdown table. Prompt-category pages have no headings — their content is
    # a single table — so anchoring only on `## ` would append the brief to the bottom,
    # which is exactly where a reader arriving from a direct link will not look.
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("## ") or line.startswith("|"):
            return "".join(lines[:i]) + block + "\n\n" + "".join(lines[i:])
    return text.rstrip("\n") + "\n\n" + block


def framework_brief(name: str, entry: dict) -> str:
    brief = entry["brief"]
    metrics = json.loads((ROOT / "frameworks" / name / "evidence" / "metrics.json").read_text())
    manifest = metrics.get("manifest", {})
    wall = manifest.get("wall_clock_seconds")
    if not wall:
        runtime = "a few seconds"
    elif wall < 1.5:
        runtime = "well under a second" if wall < 1 else "about a second"
    else:
        runtime = f"about {wall:.0f} seconds"

    conf = (metrics.get("operating_point") or {}).get("confusion")
    if conf and "tp" in conf and "fn" in conf and conf["fn"] == 0:
        b = attest.false_negative_bound(conf["tp"], conf["fn"])
        cls = entry.get("positive_class", "true positives")
        how_to_read = (
            f'### How to read "recall 1.0000" on this page\n\n'
            f"The engine missed **none** of the {b['true_positives']:,} {cls} planted in the "
            f"test population. Read that the way you would read an attribute sample that "
            f"came back with zero exceptions: you do not conclude the deviation rate is "
            f"zero — you conclude it is **below {b['fn_rate_upper_bound']:.2%} at 95% "
            f"confidence**. That exact one-sided bound is published for every engine in "
            f"[`../EVIDENCE.md`](../EVIDENCE.md), and it tightens only by testing more true "
            f"cases. It is a property of this synthetic population, not a forecast about "
            f"live data.\n"
        )
    else:
        how_to_read = (
            "### How to read the result on this page\n\n"
            + brief.get("structural_claim", "") + "\n"
        )

    kind = brief.get("kind", "scoring engine")
    return f"""{START}
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | {brief['audience']} |
| **The question it answers** | {brief['question']} |
| **What it is** | A small, transparent, runnable {kind}. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | {brief['never']} |
| **The data** | {SYNTHETIC} |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/{name}
{entry['command']}
```

Pure Python standard library: nothing to install, no network access, {runtime}. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

{how_to_read}
{END}"""


def category_brief(name: str, entry: dict) -> str:
    return f"""{START}
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | {entry['audience']} |
| **The question it answers** | {entry['question']} |
| **What these are** | Paste-ready prompt templates. Each file contains one fenced block that *is* the tool: copy it, replace the `{{{{PLACEHOLDERS}}}}`, paste it into whatever assistant you already have — Microsoft 365 Copilot, GitHub Copilot, Claude, ChatGPT. |
| **Setup required** | None. Nothing to install, no account, no integration, no repository access. A prompt works when pasted into a locked-down work machine with no file system. |
| **What you get** | A structured, sourced result with a defined method, a scoring rubric, and a fixed output shape — so two analysts running the same prompt produce comparable work. |
| **What they never do** | They draft, score, and structure. They do not decide. Every clear, escalate, block, reimburse, or file decision stays with a person, and an unverifiable claim is labelled or omitted rather than invented. |

### Using one, in about a minute

1. Open any prompt file in this folder and copy the single fenced block under `## The prompt`.
2. Replace every `{{{{PLACEHOLDER}}}}` — an unfilled one produces a vague answer.
3. Paste it into your assistant along with the case facts, document, or data.

Want a finished Word / Excel / PDF / dashboard deliverable out of it? Attach one more
file — [`BASE.md`](../../BASE.md) — which carries the writing voice, the quality floor,
and the renderer. **One prompt plus `BASE.md` is the entire system; there is never a
third file**, and a CI job fails the build if any prompt breaks that rule.

{END}"""


def main() -> int:
    check = "--check" in sys.argv[1:]
    fw = json.loads((ROOT / "frameworks" / "REPRODUCE.json").read_text())["frameworks"]
    cats = json.loads((ROOT / "prompts" / "CATEGORIES.json").read_text())["categories"]

    targets: list[tuple[Path, str]] = []
    for name in sorted(fw):
        targets.append((ROOT / "frameworks" / name / "README.md", framework_brief(name, fw[name])))
    for name in sorted(cats):
        targets.append((ROOT / "prompts" / name / "README.md", category_brief(name, cats[name])))

    stale: list[str] = []
    for path, block in targets:
        if not path.exists():
            stale.append(f"{path.relative_to(ROOT)} does not exist")
            continue
        current = path.read_text()
        updated = splice(current, block)
        if current == updated:
            continue
        if check:
            stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(updated)

    if check:
        if stale:
            print(f"FAIL — {len(stale)} standalone brief(s) drifted from the registries:")
            for s in stale:
                print(f"  {s}")
            print("\nRegenerate: python3 _tooling/build_briefs.py")
            return 1
        print(f"OK: all {len(targets)} standalone briefs match the registries.")
        return 0

    print(f"wrote standalone briefs onto {len(targets)} entry pages "
          f"({len(fw)} frameworks, {len(cats)} prompt categories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
