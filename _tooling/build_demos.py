#!/usr/bin/env python3
"""
Render a "Try it now" paste-ready demo onto every prompt page. Run from repo root.

    python3 _tooling/build_demos.py            # write the demo blocks
    python3 _tooling/build_demos.py --check    # CI: fail if any demo has drifted

Why this exists
---------------
Every prompt file ships a shell block under `## The prompt` whose inputs are
`{{PLACEHOLDERS}}` a user replaces before sending. That is right for real work,
but it makes the library hard to *evaluate*: to see what a prompt produces, a
reader who has no data in front of them must first invent synthetic inputs to
fill the placeholders. Most never do, so they never see the depth on offer —
and pasted into a weaker, tenant-wrapped assistant a half-filled prompt degrades
silently.

This generator closes that gap. For each prompt it takes the canonical prompt
block, substitutes a set of fictional demo inputs authored in
`_tooling/demos/<category>.json`, and emits a second fenced block a reader can
paste with zero edits into any assistant to get the full deliverable. Because the
demo is *derived* from the prompt block rather than hand-written, its method text
is byte-identical to `## The prompt` and cannot drift; `--check` re-derives it on
every build and fails if a committed demo disagrees.

The contract the demo upholds
-----------------------------
1. NOTHING TO FILL. The emitted block contains no `{{...}}` placeholder. Every
   one in the source is mapped to a fictional value, or the build fails.
2. SELF-CONTAINED. The block is a copy of the prompt block with inputs filled;
   it references no other repo file (the two-file rule scans it like any fence).
3. ALL FICTIONAL. Demo data uses the repository's standing fictional universe —
   "Harborview Financial Group", "Meridian Digital Exchange", invented people,
   synthetic (lowercase-hex) addresses. The hygiene gate scans it for leak
   shapes and emoji like any other page.
4. ALIGNED. Each fill declares a hint that must appear in the placeholder it
   targets, so a miscount or reordering fails loudly instead of quietly pairing
   the wrong value to the wrong input.

Everything outside the `<!-- DEMO -->` / `<!-- /DEMO -->` markers is hand-written
and never touched.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
DEMOS = Path(__file__).resolve().parent / "demos"

START = "<!-- DEMO -->"
END = "<!-- /DEMO -->"
ANCHOR = "<!-- RUNTIME_CONTRACT -->"

PLACEHOLDER_RE = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)

PREAMBLE = (
    "## Try it now — paste this, nothing to fill in\n\n"
    "The block below is the prompt above with every input already filled with "
    "**fictional demo data** — Harborview Financial Group, its counterparties, "
    "and every name, figure, and address in it are invented and synthetic. Paste "
    "it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, "
    "ChatGPT) exactly as it is, with no edits, and you get the complete "
    "deliverable this prompt produces — the full method, rubric, and output "
    "structure, at depth. It is here so you can judge the quality before you ever "
    "supply your own material. When you run it for real, use the shell prompt "
    "above and put your own inputs in its place.\n"
)


def prompt_files() -> list[Path]:
    cats = sorted(p for p in PROMPTS.iterdir() if p.is_dir())
    return [f for c in cats for f in sorted(c.glob("*.md")) if f.name != "README.md"]


def extract_prompt_block(text: str, rel: str) -> tuple[str, str]:
    """Return (fence_lang, inner) for the single ```<lang>``` block under `## The prompt`."""
    idx = text.find("## The prompt")
    if idx == -1:
        raise SystemExit(f"{rel}: no '## The prompt' section")
    m = re.search(r"^```(\w+)\n(.*?)^```", text[idx:], re.DOTALL | re.MULTILINE)
    if not m:
        raise SystemExit(f"{rel}: no fenced block under '## The prompt'")
    return m.group(1), m.group(2)


def build_block(rel: str, prompt_inner: str, entry: dict) -> str:
    """Substitute the entry's fills into the prompt block, in order, with guards."""
    placeholders = PLACEHOLDER_RE.findall(prompt_inner)
    fills = entry.get("fills", [])
    if len(placeholders) != len(fills):
        raise SystemExit(
            f"{rel}: prompt has {len(placeholders)} placeholder(s) but demo "
            f"provides {len(fills)} fill(s) — they must match one-to-one"
        )

    out = prompt_inner
    for i, (ph, fill) in enumerate(zip(placeholders, fills), start=1):
        if not (isinstance(fill, list) and len(fill) == 2):
            raise SystemExit(f"{rel}: fill #{i} must be a [hint, value] pair")
        hint, value = fill
        if hint.lower() not in ph.lower():
            raise SystemExit(
                f"{rel}: fill #{i} hint {hint!r} not found in the placeholder it "
                f"targets ({ph.strip()[:70]!r}) — a fill is out of order or missing"
            )
        if "```" in value:
            raise SystemExit(f"{rel}: fill #{i} contains a code fence; would break the block")
        # Replace only the first remaining occurrence, left to right.
        out = out.replace("{{" + ph + "}}", value, 1)

    if "{{" in out or "}}" in out:
        raise SystemExit(f"{rel}: an unfilled placeholder survived substitution")
    return out


def render_section(fence_lang: str, scenario: str, block: str) -> str:
    scenario_line = f"*Scenario: {scenario}*\n\n" if scenario else ""
    body = f"```{fence_lang}\n{block}```"
    if not body.endswith("\n"):
        body += "\n"
    return f"{START}\n{PREAMBLE}\n{scenario_line}{body}{END}"


def splice(text: str, section: str, rel: str) -> str:
    if START in text and END in text:
        pre = text[: text.index(START)]
        post = text[text.index(END) + len(END):]
        return pre + section + post
    if ANCHOR not in text:
        raise SystemExit(f"{rel}: no {ANCHOR} anchor to insert the demo before")
    at = text.index(ANCHOR)
    return text[:at] + section + "\n\n---\n\n" + text[at:]


def load_registry() -> dict:
    reg: dict[str, dict] = {}
    for jf in sorted(DEMOS.glob("*.json")):
        cat = jf.stem
        data = json.loads(jf.read_text(encoding="utf-8"))
        for name, entry in data.items():
            reg[f"{cat}/{name}"] = entry
    return reg


def main() -> int:
    check = "--check" in sys.argv
    registry = load_registry()
    files = prompt_files()

    missing: list[str] = []
    drifted: list[str] = []
    wrote = 0

    for f in files:
        rel = f"{f.parent.name}/{f.name}"
        text = f.read_text(encoding="utf-8")
        entry = registry.get(rel)
        if entry is None:
            missing.append(rel)
            continue
        lang, inner = extract_prompt_block(text, rel)
        block = build_block(rel, inner, entry)
        section = render_section(lang, entry.get("scenario", ""), block)
        new_text = splice(text, section, rel)
        if new_text != text:
            if check:
                drifted.append(rel)
            else:
                f.write_text(new_text, encoding="utf-8")
                wrote += 1

    if check:
        problems = []
        if missing:
            problems.append(f"{len(missing)} prompt(s) have no demo entry: " + ", ".join(missing))
        if drifted:
            problems.append(f"{len(drifted)} demo(s) drifted (re-run build_demos.py): " + ", ".join(drifted))
        if problems:
            print("FAIL — demo blocks out of sync:")
            for p in problems:
                print("  " + p)
            return 1
        print(f"OK: {len(files)} prompt demos current with their registry.")
        return 0

    print(f"Wrote/updated {wrote} demo block(s).")
    if missing:
        print(f"NOTE: {len(missing)} prompt(s) still have no demo entry:")
        for m in missing:
            print("  " + m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
