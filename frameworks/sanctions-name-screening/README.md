# Sanctions Name-Screening Framework

A runnable, deterministic reference engine that triages sanctions-screening alerts:
it suppresses the false positives it can *prove* are false, ranks the rest for
analysts, and escalates the likely true matches — with reproducible validation
evidence that it does so without ever auto-clearing a genuine match.

> **In plain terms:** Sanctions filters generate enormous volumes of alerts —
> roughly 50,000 a month at a mid-size institution — and 95%+ are coincidences
> where a customer or payment simply shares a common word (CAPITAL, ROAD, GLOBAL)
> with a name on a list. Analysts drown in them. This engine reads every alert and
> clears the provable coincidences automatically, **but only when it can write down
> a concrete reason** ("matched only on CAPITAL; the sanctioned party's distinctive
> name was not present"). Anything it cannot prove is a coincidence goes to a
> person, ranked most-concerning-first. It never clears a real match, never blocks
> a payment, and never files a report — those stay human decisions. On a 50,000-alert
> test it cut the human queue by ~90% while missing zero true matches.

---

## What it produces

For each alert (a payment/customer party an upstream filter matched to a watchlist
entry), a disposition:

- **AUTO_CLEAR** — a provable false positive. Cleared only with a named cause:
  generic-token-only, entity-type-incompatible, or a contradicting hard identifier.
- **ANALYST_REVIEW** — genuine name overlap, insufficient identifier evidence to
  confirm or clear. Priority HIGH / MEDIUM / LOW by score.
- **ESCALATE** — name and identifiers both align; likely a true match, routed to a
  compliance officer with the evidence assembled.

Every disposition carries a **named reason** and a full component breakdown for the
audit trail. The engine never blocks or files.

## Validation result (seed 42, 50,000 alerts — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| Recall on true matches (false-negative safety) | **1.0000 — 0 false negatives** |
| False-positive reduction | **92.2%** |
| Human review-volume cut | **90.4%** (50,000 → 4,801 to a human) |
| Analyst queue precision lift | **2% → 21%** real-match hit rate (~10×) |
| Stability | recall 1.0 across 6 seeds; FP-reduction 92.0–92.9% |
| Scale | 250,000 alerts in ~14s, same result |

Per-category clear rate: generic 99.3% · type-incompatible 100% · identifier-discriminated
95.8% · weak-residual 14.6% (the irreducible band that needs a human).

## Run it

```bash
# from this directory
python3 generate_synthetic_data.py --seed 42 --watchlist 4000 --alerts 50000
python3 run_validation.py          --seed 42 --watchlist 4000 --alerts 50000
```

`run_validation.py` regenerates the population in-memory, scores it, writes the
evidence pack under `evidence/`, and **exits non-zero if any true match is
auto-cleared** (the false-negative safety gate). Same seed → identical population →
identical numbers. Optional: `--trials 5` (multi-seed stability), `--alerts 250000`
(scale).

Ad-hoc single check:

```bash
python3 scorer.py "HARBORVIEW CAPITAL PARTNERS" ENTITY
```

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — every weight, threshold, and rule, plus the SR 11-7 framing. `scorer.py` is its executable form. |
| [`scorer.py`](scorer.py) | The deterministic disposition engine (pure stdlib + `../_lib/`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded, labelled, scalable synthetic population. |
| [`run_validation.py`](run_validation.py) | The validation harness; emits the evidence pack; enforces the FN-safety gate. |
| [`tuning.md`](tuning.md) | How to recalibrate the operating point for a real environment. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | How the engine maps onto a Microsoft Copilot Studio / Power Platform deployment. |
| [`evidence/`](evidence/) | The committed real-run output — validation report, metrics, sweep, confusion matrix, run manifest. |

## Standing caveat

This is a transparent **reference implementation** chosen for auditability, not a
production control. A real deployment swaps internals (its own matching/indexing
stack) and recalibrates the operating point against its own labelled data; the
scoring *contract* in `METHODOLOGY.md` is what travels. All data here is synthetic;
the fictional institution is **Harborview Financial Group**. Nothing in this
package screens or assesses any real party.
