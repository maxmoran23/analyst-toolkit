#!/usr/bin/env python3
"""
Build (and verify) the committed per-framework reference-data packs. Run from the
repo root; `--check` exits non-zero on any drift (CI gate).

Why this exists
---------------
Each framework's full synthetic population lives in `data/`, which is `.gitignore`d
by design — credibility is reproduction-from-seed, not data-in-repo. That policy
left a usability gap: a reader browsing a single framework folder on GitHub had no
committed example of what the engine's input actually looks like. This script
closes the gap without weakening the policy. Every framework gets a SMALL, seeded,
deterministic `reference-data/` pack (roughly 1-5% of validation scale, capped at
~150 KB per framework) produced by the SAME generator that builds the validation
population — same code path, same seed discipline, just fewer rows. `data/`
remains gitignored and untouched.

What it does
------------
For each framework in REGISTRY:

  1. Run the framework's own `generate_synthetic_data.py` (or, for
     jurisdiction-risk, its in-process generator function) into a temporary
     directory with the registered small sizes and `--seed 42`.
  2. Build mode (default): copy the registered output files into
     `frameworks/<name>/reference-data/`. Hand-authored files there
     (`README.md`) are never touched.
  3. `--check` mode: byte-compare the fresh files against the committed ones,
     mirroring `verify_evidence.py` — a pack that no longer reproduces fails the
     build, naming the exact file that drifted.

Frameworks registered as POINTER packs (`onchain-osint-evidence`) commit their
sample inputs elsewhere inside their own folder (`fixtures/sample/`, refreshed by
their generator's `--write-sample`); for those this script only verifies that the
explanatory `reference-data/README.md` exists.

Determinism
-----------
Every generator is seeded (`--seed 42`) and pure-stdlib; two runs of identical
code produce identical bytes. That is what makes `--check` a meaningful gate
rather than a flake source.
"""
from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAMEWORKS = ROOT / "frameworks"
SEED = "42"

# Registered small sizes: roughly 1-5% of each harness's validation scale, tuned
# down further where per-row weight would push the pack past ~150 KB on disk
# (fraud-detection's JSONL events, qa-sampling's per-control item populations).
# Sizes are only ever set via generator arguments — files are never truncated.
REGISTRY: dict[str, dict] = {
    "adverse-media-screening": {
        "args": ["--subjects", "120", "--hits", "750"],
        "files": ["subjects.csv", "hits.csv"],
    },
    "customer-risk-rating": {
        "args": ["--customers", "800"],
        "files": ["customers.csv"],
    },
    "data-quality-rules": {
        "args": ["--records", "700"],
        "files": ["records.csv"],
    },
    "fraud-detection": {
        "args": ["--transactions", "150"],
        "files": ["baselines.json", "events.jsonl"],
    },
    "investigations-case-qa": {
        "args": ["--cases", "700"],
        "files": ["cases.csv"],
    },
    "jurisdiction-risk": {
        # The generator here is a library (no CLI/--out); build_jurisdiction_risk
        # calls its make_jurisdictions() directly and writes the CSV itself.
        "custom": "jurisdiction_risk",
        "files": ["jurisdictions.csv"],
    },
    "npa-product-risk": {
        "args": ["--products", "700"],
        "files": ["products.csv"],
    },
    "onchain-kyt-address-risk": {
        "args": ["--addresses", "800"],
        "files": ["addresses.csv"],
    },
    "onchain-osint-evidence": {
        # Pointer pack: committed sample inputs live in this framework's own
        # fixtures/sample/, maintained by generate_synthetic_data.py
        # --write-sample. reference-data/README.md documents that location.
        "pointer": True,
        "files": [],
    },
    "pep-screening": {
        "args": ["--peps", "150", "--alerts", "800"],
        "files": ["pep_list.csv", "alerts.csv"],
    },
    "qa-sampling": {
        "args": ["--controls", "12", "--population", "250"],
        "files": ["controls.csv", "items.csv"],
    },
    "sanctions-name-screening": {
        "args": ["--watchlist", "120", "--alerts", "800"],
        "files": ["watchlist.csv", "alerts.csv"],
    },
    "tm-threshold-tuning": {
        "args": ["--rules", "12", "--population", "600"],
        "files": ["rules.csv", "observations.csv"],
    },
    "transaction-monitoring": {
        "args": ["--customers", "120", "--alerts", "800"],
        "files": ["customers.csv", "alerts.csv"],
    },
    "watchlist-knowledge-base": {
        "args": ["--entities", "150"],
        "files": ["list_records.csv"],
    },
}

JURISDICTION_COUNT = 600  # 1.5% of the 40,000-jurisdiction validation population


def build_jurisdiction_risk(out_dir: Path) -> None:
    """jurisdiction-risk's generator exposes make_jurisdictions() with no file
    writer; produce the CSV here, in the module's own field order."""
    import csv
    import random

    gen_path = FRAMEWORKS / "jurisdiction-risk" / "generate_synthetic_data.py"
    spec = importlib.util.spec_from_file_location("jr_generate", gen_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    rows = module.make_jurisdictions(JURISDICTION_COUNT, random.Random(int(SEED)))
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "jurisdictions.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=module.FIELDS)
        writer.writeheader()
        writer.writerows(rows)


CUSTOM_BUILDERS = {"jurisdiction_risk": build_jurisdiction_risk}


def generate(name: str, spec: dict, out_dir: Path) -> None:
    """Run the framework's generator into out_dir with the registered sizes."""
    if "custom" in spec:
        CUSTOM_BUILDERS[spec["custom"]](out_dir)
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(FRAMEWORKS / name / "generate_synthetic_data.py"),
        *spec["args"],
        "--seed", SEED,
        "--out", str(out_dir),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def build(names: list[str]) -> int:
    for name in names:
        spec = REGISTRY[name]
        dest = FRAMEWORKS / name / "reference-data"
        if spec.get("pointer"):
            print(f"  {name}: pointer pack (see its reference-data/README.md) — nothing generated")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            generate(name, spec, Path(tmp))
            dest.mkdir(parents=True, exist_ok=True)
            total = 0
            for fname in spec["files"]:
                src = Path(tmp) / fname
                shutil.copyfile(src, dest / fname)
                total += src.stat().st_size
        print(f"  {name}: {len(spec['files'])} file(s), {total / 1024:.0f} KB -> {dest.relative_to(ROOT)}/")
    return 0


def check(names: list[str]) -> int:
    failures: list[str] = []
    verified = 0
    for name in names:
        spec = REGISTRY[name]
        dest = FRAMEWORKS / name / "reference-data"
        readme = dest / "README.md"
        if not readme.exists():
            failures.append(f"{name}: missing reference-data/README.md")
        if spec.get("pointer"):
            if readme.exists():
                verified += 1
                print(f"  OK    {name} (pointer pack; README present)")
            continue
        drifted: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            generate(name, spec, Path(tmp))
            for fname in spec["files"]:
                committed = dest / fname
                fresh = Path(tmp) / fname
                if not committed.exists():
                    drifted.append(f"{fname} (not committed)")
                elif committed.read_bytes() != fresh.read_bytes():
                    drifted.append(f"{fname} (bytes differ)")
        if drifted:
            failures.append(f"{name}: {', '.join(drifted)}")
            print(f"  DRIFT {name}: {', '.join(drifted)}")
        else:
            verified += 1
            print(f"  OK    {name}")

    print()
    if failures:
        print(f"{len(failures)} reference-data pack(s) failed to reproduce:")
        for failure in failures:
            print(f"  - {failure}")
        print("\nRe-run `python3 _tooling/build_reference_data.py` and commit the result,")
        print("or fix the generator change that moved the bytes.")
        return 1
    print(f"All {verified} reference-data packs reproduce byte-identically from seed.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="regenerate into a temp dir and diff against committed packs")
    ap.add_argument("--only", metavar="FRAMEWORK",
                    help="restrict to a single framework package")
    args = ap.parse_args()

    if args.only:
        if args.only not in REGISTRY:
            print(f"unknown framework: {args.only}")
            print("known: " + ", ".join(sorted(REGISTRY)))
            return 2
        names = [args.only]
    else:
        names = sorted(REGISTRY)

    if args.check:
        print(f"Verifying {len(names)} reference-data pack(s) against seed {SEED}\n")
        return check(names)
    print(f"Building {len(names)} reference-data pack(s) with seed {SEED}\n")
    return build(names)


if __name__ == "__main__":
    raise SystemExit(main())
