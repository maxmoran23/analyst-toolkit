#!/usr/bin/env python3
"""
Generate `frameworks/EVIDENCE.md` — the auditor-facing archive record — from the
committed evidence packs. Run from the repo root.

    python3 _tooling/build_evidence_index.py           # write the file
    python3 _tooling/build_evidence_index.py --check    # CI: fail if it has drifted

Why generated, not written
--------------------------
An evidence index that a human types is another claim to audit. This one is derived:
every number in it is read out of a committed `evidence/metrics.json`, and every
confidence bound is recomputed from the observed counts by the repository's own exact
sampling engine. Nothing in it can say something the evidence packs do not.

`--check` makes that a build gate: edit a number by hand and the build fails.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "frameworks"))

from _lib import attest  # noqa: E402

OUT = ROOT / "frameworks" / "EVIDENCE.md"


def load(name: str) -> dict:
    return json.loads((ROOT / "frameworks" / name / "evidence" / "metrics.json").read_text())


def confusion_of(metrics: dict):
    op = metrics.get("operating_point") or {}
    conf = op.get("confusion")
    if isinstance(conf, dict) and "tp" in conf and "fn" in conf:
        return conf
    return None


def fmt_int(v):
    return f"{v:,}" if isinstance(v, int) else str(v)


def build() -> str:
    registry = json.loads((ROOT / "frameworks" / "REPRODUCE.json").read_text())["frameworks"]
    L: list[str] = []
    A = L.append

    A("# Evidence archive — what is claimed, and how to check it yourself")
    A("")
    A("> **Generated file.** Every figure below is read out of a committed "
      "`frameworks/<name>/evidence/metrics.json`; every confidence bound is recomputed "
      "from the observed counts. Regenerate with "
      "`python3 _tooling/build_evidence_index.py`. CI fails the build if this file has "
      "been edited by hand.")
    A("")
    A("This repository makes an empirical claim about thirteen scoring engines. The claim "
      "is **not** \"trust the report.\" It is: *here is the exact command, run it, and you "
      "will get these numbers.* This page is the contract that makes that checkable.")
    A("")

    A("## Verify the whole pillar in one command")
    A("")
    A("```bash")
    A("python3 _tooling/verify_evidence.py")
    A("```")
    A("")
    A("This re-derives all thirteen evidence packs from seed, compares every metric to "
      "the committed values, and exits non-zero on any difference. It takes about twenty "
      "seconds and needs nothing but Python — the engines are pure standard library, and "
      "no run touches the network. It is also a CI job, so **every commit to `main` "
      "re-derives every number in this repository on a machine nobody here controls.** "
      "The green check on the latest commit is the attestation; it is not a claim made by "
      "the author.")
    A("")
    A("To re-derive one framework by hand, run its command from its own directory:")
    A("")
    A("| Framework | Reproduction command |")
    A("|---|---|")
    for name in sorted(registry):
        A(f"| [`{name}/`]({name}/) | `{registry[name]['command']}` |")
    A("")

    A("## The safety claim, with its statistical bound")
    A("")
    A("Seven engines make a false-negative safety claim: *the engine never auto-cleared a "
      "labelled true positive.* That is an **observation on a finite sample**, not a "
      "guarantee. Zero misses in 997 cases and zero in 8,996 are very different evidence, "
      "and a claim of \"recall 1.0\" that hides which one it is deserves the scepticism it "
      "will get.")
    A("")
    A("So each is reported with the exact one-sided 95% Clopper-Pearson upper bound on the "
      "miss rate — the largest true failure rate consistent with observing zero failures in "
      "*n* trials. It is computed by [`_lib/sampling.py`](_lib/sampling.py), the same exact "
      "tail mathematics the [`qa-sampling/`](qa-sampling/) framework ships to testers, and "
      "it tightens only by testing more true cases.")
    A("")
    A("| Framework | Positive class | n | Misses | Observed recall | Miss rate ≤ (95%) | Recall ≥ (95%) |")
    A("|---|---|---:|---:|---:|---:|---:|")
    bounded = 0
    for name in sorted(registry):
        conf = confusion_of(load(name))
        if not conf:
            continue
        bounded += 1
        b = attest.false_negative_bound(conf["tp"], conf["fn"])
        cls = registry[name].get("positive_class", "true positives")
        A(f"| [`{name}/`]({name}/) | {cls} | {b['true_positives']:,} | {b['false_negatives']} | "
          f"{conf['recall']:.4f} | **{b['fn_rate_upper_bound']:.4%}** | "
          f"**{b['recall_lower_bound']:.4%}** |")
    A("")
    A(f"All {bounded} engines observed **zero** misses. Read the right-hand columns as the "
      "honest version of that: on these synthetic populations, the miss rate is bounded "
      "above by the stated figure at 95% confidence. The bound is a property of the sample "
      "size — it says nothing about live data, where the population, the adversary, and the "
      "label quality all differ.")
    A("")

    A("## Provenance of each committed pack")
    A("")
    A("The digest is a SHA-256 over the substantive metrics with volatile fields "
      "(timestamp, git SHA, wall clock, environment) removed, so two runs of identical "
      "code on identical seeds produce the same digest on any machine. Compare one hash "
      "instead of forty fields.")
    A("")
    A("| Framework | Population | Seed | Wall clock | Generated at commit | Results digest |")
    A("|---|---|---:|---:|---|---|")
    for name in sorted(registry):
        m = load(name)
        man = m.get("manifest", {})
        pop = next((fmt_int(man[k]) for k in
                    ("alerts", "records", "cases", "customers", "addresses", "products",
                     "hits", "population", "entities", "transactions")
                    if k in man), "—")
        wall = man.get("wall_clock_seconds")
        wall = f"{wall}s" if wall is not None else "—"
        dirty = " (dirty tree)" if man.get("git_dirty") else ""
        A(f"| [`{name}/`]({name}/) | {pop} | {man.get('seed', '—')} | {wall} | "
          f"`{man.get('git_sha', '—')}`{dirty} · {man.get('generated_utc', '—')} | "
          f"`{attest.results_digest(m)[:16]}` |")
    A("")

    A("## What this evidence does and does not establish")
    A("")
    A("**It establishes:**")
    A("")
    A("- The numbers in every `VALIDATION-REPORT.md` are emitted by a harness, not typed "
      "by a person, and they re-derive exactly from a fixed seed on any machine.")
    A("- Each engine's safety invariant is enforced as a **build gate**: the harness exits "
      "non-zero if the engine ever auto-clears a labelled true positive, rates a "
      "hard-risk case low, or passes a critically deficient item. A regression cannot be "
      "merged quietly, because CI re-runs all of it.")
    A("- The engines are deterministic and dependency-free, so \"it works on my machine\" is "
      "not part of the argument.")
    A("")
    A("**It does not establish:**")
    A("")
    A("- **Any claim about live performance.** Every population here is synthetic and every "
      "entity fictional. The generators model the *shape* of real variation — "
      "false-positive dominance, transliteration noise, adversarial near-misses — not its "
      "full messiness. A real deployment must recalibrate against its own labelled data.")
    A("- **That the synthetic population is representative.** It is constructed, so ground "
      "truth is known; that is exactly what makes it *not* a sample of the real world. The "
      "generator plants the adversarial cases the author thought of. It cannot plant the "
      "ones nobody thought of.")
    A("- **That these are production controls.** They are transparent reference "
      "implementations chosen for auditability. The scoring *contract* in each "
      "`METHODOLOGY.md` is what travels, not a turnkey system.")
    A("- **Fitness for use.** No engine here decides anything. Each scores, routes, or "
      "documents; a qualified human clears, blocks, files, and signs.")
    A("")
    A("## The attestation chain")
    A("")
    A("```")
    A("seed  ->  generate_synthetic_data.py   (labelled population, ground truth known)")
    A("      ->  scorer / engine              (pure stdlib, deterministic, no network)")
    A("      ->  run_validation.py            (computes metrics; EXITS NON-ZERO on a")
    A("                                        safety breach — the gate, not a sentence)")
    A("      ->  evidence/                    (report + metrics + manifest, all emitted)")
    A("      ->  _tooling/verify_evidence.py  (re-derives and diffs against committed)")
    A("      ->  GitHub Actions               (runs the above on every commit to main)")
    A("```")
    A("")
    A("Each link is checkable independently. The last one is checkable by someone who does "
      "not trust the author at all: the workflow definition is "
      "[`.github/workflows/validate.yml`](../.github/workflows/validate.yml), and its run "
      "history is public.")
    A("")
    A("## Reading the reports")
    A("")
    A("Each `evidence/VALIDATION-REPORT.md` follows a fixed section order — methodology, "
      "population construction, operating point, per-category performance, threshold "
      "sensitivity, the safety argument (with its statistical bound), volume impact, "
      "limitations, reproduction. The standard every harness must meet is "
      "[`RIGOR-CONTRACT.md`](RIGOR-CONTRACT.md); the model-risk framing is "
      "[`GOVERNANCE.md`](GOVERNANCE.md).")
    A("")
    A("---")
    A("")
    A("*Synthetic data throughout. No real person, entity, vessel, address, or list entry "
      "is represented; the recurring institution is the fictional Harborview Financial "
      "Group. Nothing here is legal advice or a production control.*")
    return "\n".join(L) + "\n"


def main() -> int:
    content = build()
    check = "--check" in sys.argv[1:]
    if check:
        if not OUT.exists():
            print("FAIL: frameworks/EVIDENCE.md missing — run build_evidence_index.py")
            return 1
        if OUT.read_text() != content:
            print("FAIL: frameworks/EVIDENCE.md has drifted from the committed evidence packs.")
            print("      Regenerate: python3 _tooling/build_evidence_index.py")
            return 1
        print("OK: frameworks/EVIDENCE.md matches the committed evidence packs.")
        return 0
    OUT.write_text(content)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(content.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
