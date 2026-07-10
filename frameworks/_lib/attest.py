"""
Attestation primitives — provenance, statistical bounds, and evidence digests.

The frameworks pillar makes an empirical claim ("this engine never auto-cleared a
true positive") on synthetic data. Two things separate a defensible claim from a
"trust me":

1. **Provenance.** What code, what seed, what environment, how long it ran. Enough
   for a reviewer to reconstruct the exact run, and enough for a build to prove the
   committed evidence is what the current code produces.

2. **A statistical bound.** "Recall 1.0000, zero false negatives" is an *observation*,
   not a guarantee. Observing zero failures in n trials is consistent with a true
   failure rate anywhere from 0 up to a bound that depends on n. Reporting recall
   without that bound is the first thing a model validator will attack, and rightly:
   zero failures in 100 trials and zero in 100,000 are very different evidence.

This module supplies both. The bound is computed by the repository's own exact
attribute-sampling engine (`_lib/sampling.upper_deviation_limit`), so the statistics
that validate the screening engines are the same statistics the QA-sampling framework
ships to testers — one implementation, cross-checked in its own harness.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import platform
import subprocess
import sys
import time

from . import sampling

# Manifest keys that legitimately differ between two runs of identical code.
# `verify_evidence.py` strips these before comparing a fresh run to the committed
# pack: a different timestamp is not metric drift, a different recall is.
VOLATILE_MANIFEST_KEYS = (
    "generated_utc",
    "git_sha",
    "git_dirty",
    "wall_clock_seconds",
    "environment",
)


def git_sha(short: bool = True) -> str:
    cmd = ["git", "rev-parse"] + (["--short"] if short else []) + ["HEAD"]
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def git_dirty() -> bool:
    """True when the working tree has uncommitted changes — evidence generated from
    a dirty tree does not correspond to any commit, and says so."""
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"],
                                      stderr=subprocess.DEVNULL).decode().strip()
        return bool(out)
    except Exception:
        return False


def environment() -> dict:
    """The interpreter and platform that produced a run. Provenance, not a metric —
    a pure-stdlib deterministic engine yields identical numbers across all of these."""
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


def enrich_manifest(manifest: dict, started_at: float | None = None) -> dict:
    """Add the uniform provenance block every framework's run-manifest carries.

    Existing keys win — a harness that already recorded its own `git_sha` or
    `generated_utc` keeps them, so this is safe to apply to every harness.
    """
    manifest.setdefault("git_sha", git_sha())
    manifest.setdefault(
        "generated_utc",
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )
    manifest["git_dirty"] = git_dirty()
    manifest["environment"] = environment()
    if started_at is not None:
        manifest["wall_clock_seconds"] = round(time.time() - started_at, 2)
    return manifest


def false_negative_bound(true_positives: int, false_negatives: int,
                         confidence: float = 0.95) -> dict:
    """Exact one-sided upper confidence bound on the false-negative rate.

    Clopper-Pearson (binomial) inversion — the largest true FN rate not rejected by
    observing `false_negatives` failures in `true_positives` labelled true cases at
    the stated confidence. For zero observed failures this reduces to the familiar
    rule of three (~3/n) but is computed exactly, not approximated.

    Reported alongside recall, this converts "we saw no misses" into "the miss rate
    is below X% at 95% confidence, on this population" — a claim a validator can
    check and a number that honestly shrinks as the test population grows.
    """
    if true_positives < 1:
        raise ValueError("true_positives must be >= 1")
    upper = sampling.upper_deviation_limit(
        n=true_positives, k=false_negatives, confidence=confidence
    )
    return {
        "true_positives": true_positives,
        "false_negatives": false_negatives,
        "observed_fn_rate": false_negatives / true_positives,
        "confidence": confidence,
        "fn_rate_upper_bound": upper,
        "recall_lower_bound": 1.0 - upper,
        "method": "exact one-sided Clopper-Pearson upper limit (_lib/sampling)",
    }


def bound_sentence(true_positives: int, false_negatives: int,
                   confidence: float = 0.95, unit: str = "true positives") -> str:
    """The one-line statistical statement that belongs next to any recall claim.

    `unit` is the plural noun for the labelled positive class ("true positives",
    "critical deficiencies", "planted defects").
    """
    b = false_negative_bound(true_positives, false_negatives, confidence)
    pct = int(confidence * 100)
    return (
        f"**Statistical bound.** {b['false_negatives']} misses were observed among "
        f"{b['true_positives']:,} labelled {unit}. Observing zero failures is not a "
        f"guarantee of a zero failure rate: the exact one-sided {pct}% "
        f"Clopper-Pearson upper bound on the miss rate is "
        f"**{b['fn_rate_upper_bound']:.4%}** (recall at least "
        f"**{b['recall_lower_bound']:.4%}**) *on this synthetic population*. The bound "
        f"is a property of the sample size, not a promise about live data — it tightens "
        f"only by testing more true cases."
    )


def strip_volatile(metrics: dict) -> dict:
    """Return `metrics` with volatile manifest fields removed, so two runs of the
    same code compare equal."""
    out = json.loads(json.dumps(metrics, sort_keys=True, default=str))
    manifest = out.get("manifest")
    if isinstance(manifest, dict):
        for key in VOLATILE_MANIFEST_KEYS:
            manifest.pop(key, None)
    return out


def results_digest(metrics: dict) -> str:
    """SHA-256 over the substantive results — every metric, no volatile provenance.

    Two runs of identical code on identical seeds produce the same digest on any
    machine. A changed digest means a changed result, which is exactly what a
    reviewer wants to be able to check in one comparison.
    """
    canonical = json.dumps(strip_volatile(metrics), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


if __name__ == "__main__":  # tiny self-check: python3 -m _lib.attest
    for n in (997, 8996):
        b = false_negative_bound(n, 0)
        print(f"n={n:>6} k=0 -> FN rate <= {b['fn_rate_upper_bound']:.6f} "
              f"(recall >= {b['recall_lower_bound']:.6f})")
    print(json.dumps(environment(), indent=2))
    sys.exit(0)
