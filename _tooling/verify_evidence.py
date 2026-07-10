#!/usr/bin/env python3
"""
Re-derive every framework's evidence pack and prove the committed numbers are what
the current code actually produces. Run from the repo root; exits non-zero on any
substantive difference (CI gate).

Why this exists
---------------
The frameworks pillar claims its numbers are "emitted by a script anyone can re-run,
not authored." Until now nothing checked that. CI ran each harness with `--no-write`
— confirming the safety gate still passed — but never compared the fresh result to
the committed `evidence/` pack. So a committed VALIDATION-REPORT could drift away
from the engine it describes and no build would notice. `RIGOR-CONTRACT.md` called
for this check and marked it "optional". It is not optional: it is the difference
between evidence and assertion.

What it does
------------
For each framework in `frameworks/REPRODUCE.json`:

  1. Run the registered reproduction command into a temporary directory.
  2. Compare the fresh `metrics.json` to the committed one, field by field,
     after stripping the volatile provenance keys (`_lib/attest.VOLATILE_MANIFEST_KEYS`
     — timestamp, git SHA, wall clock, environment). A different timestamp is not
     metric drift; a different recall is.
  3. Compare the fresh `VALIDATION-REPORT.md` to the committed one, ignoring the
     provenance lines. The rigor contract says the report is rendered from the
     computed numbers so prose and metrics cannot diverge; this is what checks it.
  4. Report the results digest, so a reviewer can compare one hash instead of
     forty fields.

A framework whose committed evidence no longer reproduces fails the build, naming
the exact metric that moved and both values.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
sys.path.insert(0, str(ROOT / "frameworks"))

from _lib import attest  # noqa: E402


def flatten(obj, prefix=""):
    out = {}
    for key, value in obj.items():
        if isinstance(value, dict):
            out.update(flatten(value, f"{prefix}{key}."))
        else:
            out[f"{prefix}{key}"] = value
    return out


def report_lines(text: str) -> list[str]:
    """Report content with the provenance lines removed — those legitimately differ
    between two runs of identical code (timestamp, git SHA, wall clock)."""
    return [
        line for line in text.splitlines()
        if "UTC" not in line and "git `" not in line
    ]


def main() -> int:
    registry = json.loads((ROOT / "frameworks" / "REPRODUCE.json").read_text())["frameworks"]
    failures: list[str] = []
    verified = 0

    print(f"Re-deriving {len(registry)} evidence packs from seed\n")

    for name in sorted(registry):
        pkg = ROOT / "frameworks" / name
        committed_path = pkg / "evidence" / "metrics.json"
        if not committed_path.exists():
            failures.append(f"{name}: no committed evidence/metrics.json")
            continue

        command = registry[name]["command"].split()
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                command + ["--out", tmp],
                cwd=pkg, capture_output=True, text=True,
            )
            if proc.returncode != 0:
                failures.append(
                    f"{name}: harness exited {proc.returncode} "
                    f"(safety gate or crash) — {proc.stdout.strip()[-200:]}"
                )
                continue
            fresh_path = Path(tmp) / "metrics.json"
            if not fresh_path.exists():
                failures.append(f"{name}: harness wrote no metrics.json to --out")
                continue
            fresh = json.loads(fresh_path.read_text())
            fresh_report_path = Path(tmp) / "VALIDATION-REPORT.md"
            fresh_report = fresh_report_path.read_text() if fresh_report_path.exists() else None

        committed = json.loads(committed_path.read_text())
        a = flatten(attest.strip_volatile(committed))
        b = flatten(attest.strip_volatile(fresh))

        drift = [k for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
        digest = attest.results_digest(fresh)[:16]

        report_drift = 0
        committed_report_path = pkg / "evidence" / "VALIDATION-REPORT.md"
        if fresh_report is not None and committed_report_path.exists():
            old = report_lines(committed_report_path.read_text())
            new = report_lines(fresh_report)
            if old != new:
                report_drift = sum(1 for x, y in zip(old, new) if x != y) + abs(len(old) - len(new))

        if drift or report_drift:
            print(f"  FAIL  {name:<28} {len(drift)} metric(s), {report_drift} report line(s) drifted")
            for key in drift[:6]:
                print(f"          {key}: committed={a.get(key)!r} regenerated={b.get(key)!r}")
            if len(drift) > 6:
                print(f"          ... and {len(drift) - 6} more")
            if report_drift:
                print(f"          VALIDATION-REPORT.md differs from what the harness renders")
            failures.append(
                f"{name}: {len(drift)} metric(s) and {report_drift} report line(s) "
                f"differ from committed evidence"
            )
        else:
            verified += 1
            print(f"  OK    {name:<28} {len(a):>3} metrics + report reproduce · digest {digest}")

    print()
    if failures:
        print(f"FAIL — {len(failures)} framework(s) do not reproduce:")
        for f in failures:
            print(f"  {f}")
        print("\nRegenerate the pack (run its REPRODUCE.json command without --out) and "
              "commit the result, or fix the engine.")
        return 1

    print(f"OK: all {verified} evidence packs re-derived from seed and match the "
          f"committed numbers exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
