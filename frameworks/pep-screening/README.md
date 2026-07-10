# PEP Screening Framework

A runnable, deterministic engine that dispositions politically-exposed-person
screening alerts on two axes — is the customer actually the listed person, and
does that entry still carry material PEP risk — clearing the provable false
positives while never auto-clearing a current PEP, a senior former one, or any
corroborated match.

> **In plain terms:** PEP screening drowns analysts two ways. First, name
> collisions: a customer named Kim, Park, Mohammed, or Garcia trips on every
> official who shares the name, and transliteration spellings multiply the
> problem. Second, scope creep: lists keep people for decades, so a customer who
> matches someone who was a small-town mayor eleven years ago raises the same
> alert as a sitting minister. This engine clears an alert only when it can write
> down proof — the date of birth AND nationality both contradict the entry (a
> different person), the match rests on a common name while the official's
> distinctive name went unmatched, or the entry is a former low-level official
> far past the documented step-down window with nothing adverse on file. A bare
> "David Kim" match with no identifying detail is **not** cleared — it might be
> your customer, so it goes to a person. And a former head of state is never
> status-cleared: once senior, the risk is lowered but never zero. On a
> 50,000-alert test it cut the human queue ~81% while missing zero genuine
> in-scope matches.

---

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Screening teams working politically-exposed-person alerts. |
| **The question it answers** | Is this customer actually the listed official, and does that listing still carry material risk? |
| **What it is** | A small, transparent, runnable scoring engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never auto-clears a currently-serving official, a senior former one, or any corroborated identity match — regardless of score. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/pep-screening
python3 run_validation.py --seed 42 --peps 8000 --alerts 50000
```

Pure Python standard library: nothing to install, no network access, about a second. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read "recall 1.0000" on this page

The engine missed **none** of the 2,021 true PEP matches planted in the test population. Read that the way you would read an attribute sample that came back with zero exceptions: you do not conclude the deviation rate is zero — you conclude it is **below 0.15% at 95% confidence**. That exact one-sided bound is published for every engine in [`../EVIDENCE.md`](../EVIDENCE.md), and it tightens only by testing more true cases. It is a property of this synthetic population, not a forecast about live data.

<!-- /STANDALONE-BRIEF -->

## What it produces

Per alert, a disposition (AUTO_CLEAR / ANALYST_REVIEW / ESCALATE_ENHANCED_REVIEW)
with a `match_strength` (confidence it is the right party), a `materiality`
(prominence tier x status decay x jurisdiction bucket), a `combined` ranking
score, and a named reason. The engine routes to humans; it never approves,
blocks, or closes a relationship.

## Validation result (seed 42, 50,000 alerts — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| Recall on genuine in-scope PEP matches (FN-safety) | **1.0000 — 0 false negatives** |
| False-positive reduction | **84.1%** |
| Human review-volume cut | **80.7%** (50,000 → 9,631 to a human) |
| Analyst queue precision lift | **4.0% → 21.0%** (~5.2×) |
| Stability | recall 1.0 across 6 seeds; FP-reduction 83.8–84.2% |
| Scale | 200,000 alerts in ~6s, same result |

Per-category clear rate: wrong_party_common_name 100% · wrong_party_translit
100% · generic_token 99.5% · out_of_scope_former 85.3% (the corroborated
minority is deliberately routed to a human) · common_name_ambiguous 0% (the
irreducible band — common-name matches with no identifier, left open by design).
FP reduction is bounded by those residuals rather than inflated past them.

## Run it

```bash
# from this directory
python3 generate_synthetic_data.py --seed 42 --peps 8000 --alerts 50000
python3 run_validation.py          --seed 42 --peps 8000 --alerts 50000
```

`run_validation.py` regenerates the population in-memory, scores it, writes the
evidence pack under `evidence/`, and **exits non-zero if any genuine in-scope
match is auto-cleared** (the false-negative safety gate). Same seed → identical
population → identical numbers. Optional: `--trials 6` (multi-seed stability),
`--alerts 200000` (scale).

Ad-hoc single check:

```bash
python3 scorer.py "DAVID KIM"
```

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — tier weights, decay horizons, jurisdiction buckets, disposition rules, SR 11-7 framing. `scorer.py` is its executable form. |
| [`scorer.py`](scorer.py) | The deterministic engine (reuses `../_lib/match` + `../_lib/text_normalize`; prominence/decay tiering lives here). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded fictional PEP list + labelled alerts, with adversarial plants. |
| [`run_validation.py`](run_validation.py) | Validation harness + evidence pack; FN-safety gate. |
| [`tuning.md`](tuning.md) | How to recalibrate the operating point for a real environment. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Copilot Studio / Power Platform mapping. |
| [`evidence/`](evidence/) | Committed real-run output — validation report, metrics, sweep, confusion matrix, run manifest. |

## Standing caveat

A transparent **reference implementation** chosen for auditability, not a
production control. The tier weights, step-down horizons, and jurisdiction
buckets are illustrative policy parameters — a real deployment sets them from
its own risk appetite and recalibrates against its own labelled alerts; the
scoring *contract* in `METHODOLOGY.md` is what travels. All data is synthetic
and fictional (invented officials of invented countries; the recurring
institution is **Harborview Financial Group**). Nothing here screens or
assesses any real person.
