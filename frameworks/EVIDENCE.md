# Evidence archive — what is claimed, and how to check it yourself

> **Generated file.** Every figure below is read out of a committed `frameworks/<name>/evidence/metrics.json`; every confidence bound is recomputed from the observed counts. Regenerate with `python3 _tooling/build_evidence_index.py`. CI fails the build if this file has been edited by hand.

This repository makes an empirical claim about thirteen scoring engines. The claim is **not** "trust the report." It is: *here is the exact command, run it, and you will get these numbers.* This page is the contract that makes that checkable.

## Verify the whole pillar in one command

```bash
python3 _tooling/verify_evidence.py
```

This re-derives all thirteen evidence packs from seed, compares every metric to the committed values, and exits non-zero on any difference. It takes about twenty seconds and needs nothing but Python — the engines are pure standard library, and no run touches the network. It is also a CI job, so **every commit to `main` re-derives every number in this repository on a machine nobody here controls.** The green check on the latest commit is the attestation; it is not a claim made by the author.

To re-derive one framework by hand, run its command from its own directory:

| Framework | Reproduction command |
|---|---|
| [`adverse-media-screening/`](adverse-media-screening/) | `python3 run_validation.py --seed 42 --subjects 8000 --hits 50000` |
| [`customer-risk-rating/`](customer-risk-rating/) | `python3 run_validation.py --seed 42 --customers 50000` |
| [`data-quality-rules/`](data-quality-rules/) | `python3 run_validation.py --seed 42 --records 50000` |
| [`investigations-case-qa/`](investigations-case-qa/) | `python3 run_validation.py --seed 42 --cases 50000` |
| [`npa-product-risk/`](npa-product-risk/) | `python3 run_validation.py --seed 42 --products 50000` |
| [`onchain-kyt-address-risk/`](onchain-kyt-address-risk/) | `python3 run_validation.py --seed 42 --addresses 50000` |
| [`onchain-osint-evidence/`](onchain-osint-evidence/) | `python3 run_validation.py --seed 42 --addresses 400 --transactions 50000` |
| [`pep-screening/`](pep-screening/) | `python3 run_validation.py --seed 42 --peps 8000 --alerts 50000` |
| [`qa-sampling/`](qa-sampling/) | `python3 run_validation.py --seed 42 --controls 12 --population 40000` |
| [`sanctions-name-screening/`](sanctions-name-screening/) | `python3 run_validation.py --seed 42 --watchlist 4000 --alerts 50000` |
| [`tm-threshold-tuning/`](tm-threshold-tuning/) | `python3 run_validation.py --seed 42 --rules 12 --population 40000` |
| [`transaction-monitoring/`](transaction-monitoring/) | `python3 run_validation.py --seed 42 --customers 5000 --alerts 50000` |
| [`watchlist-knowledge-base/`](watchlist-knowledge-base/) | `python3 run_validation.py --seed 42 --entities 3000` |

## The safety claim, with its statistical bound

Seven engines make a false-negative safety claim: *the engine never auto-cleared a labelled true positive.* That is an **observation on a finite sample**, not a guarantee. Zero misses in 997 cases and zero in 8,996 are very different evidence, and a claim of "recall 1.0" that hides which one it is deserves the scepticism it will get.

So each is reported with the exact one-sided 95% Clopper-Pearson upper bound on the miss rate — the largest true failure rate consistent with observing zero failures in *n* trials. It is computed by [`_lib/sampling.py`](_lib/sampling.py), the same exact tail mathematics the [`qa-sampling/`](qa-sampling/) framework ships to testers, and it tightens only by testing more true cases.

| Framework | Positive class | n | Misses | Observed recall | Miss rate ≤ (95%) | Recall ≥ (95%) |
|---|---|---:|---:|---:|---:|---:|
| [`adverse-media-screening/`](adverse-media-screening/) | materially adverse true hits | 2,468 | 0 | 1.0000 | **0.1213%** | **99.8787%** |
| [`data-quality-rules/`](data-quality-rules/) | planted critical defects | 2,750 | 0 | 1.0000 | **0.1089%** | **99.8911%** |
| [`investigations-case-qa/`](investigations-case-qa/) | critical deficiencies | 8,996 | 0 | 1.0000 | **0.0333%** | **99.9667%** |
| [`onchain-kyt-address-risk/`](onchain-kyt-address-risk/) | truly tainted addresses | 3,055 | 0 | 1.0000 | **0.0980%** | **99.9020%** |
| [`pep-screening/`](pep-screening/) | true PEP matches | 2,021 | 0 | 1.0000 | **0.1481%** | **99.8519%** |
| [`sanctions-name-screening/`](sanctions-name-screening/) | true matches | 997 | 0 | 1.0000 | **0.3000%** | **99.7000%** |
| [`transaction-monitoring/`](transaction-monitoring/) | truly suspicious alerts | 2,052 | 0 | 1.0000 | **0.1459%** | **99.8541%** |

All 7 engines observed **zero** misses. Read the right-hand columns as the honest version of that: on these synthetic populations, the miss rate is bounded above by the stated figure at 95% confidence. The bound is a property of the sample size — it says nothing about live data, where the population, the adversary, and the label quality all differ.

## Provenance of each committed pack

The digest is a SHA-256 over the substantive metrics with volatile fields (timestamp, git SHA, wall clock, environment) removed, so two runs of identical code on identical seeds produce the same digest on any machine. Compare one hash instead of forty fields.

| Framework | Population | Seed | Wall clock | Generated at commit | Results digest |
|---|---|---:|---:|---|---|
| [`adverse-media-screening/`](adverse-media-screening/) | 50,000 | 42 | 1.15s | `d2f4ef1` · 2026-07-10 05:09 UTC | `c8c6d4a94091abf7` |
| [`customer-risk-rating/`](customer-risk-rating/) | 50,000 | 42 | 0.55s | `d2f4ef1` · 2026-07-10 05:09 UTC | `2289abbaef5813f2` |
| [`data-quality-rules/`](data-quality-rules/) | 50,000 | 42 | 2.86s | `d2f4ef1` · 2026-07-10 05:09 UTC | `6f6c9df784f391d9` |
| [`investigations-case-qa/`](investigations-case-qa/) | 50,000 | 42 | 1.13s | `d2f4ef1` · 2026-07-10 05:09 UTC | `0adfa7eb40d35f11` |
| [`npa-product-risk/`](npa-product-risk/) | 50,000 | 42 | 0.69s | `d2f4ef1` · 2026-07-10 05:09 UTC | `0a05434c0ea578b2` |
| [`onchain-kyt-address-risk/`](onchain-kyt-address-risk/) | 50,000 | 42 | 0.53s | `d2f4ef1` · 2026-07-10 05:09 UTC | `36430cd5379711c3` |
| [`onchain-osint-evidence/`](onchain-osint-evidence/) | 400 | 42 | 3.46s | `d2f4ef1` · 2026-07-10 05:09 UTC | `23f2f8c77e1c3737` |
| [`pep-screening/`](pep-screening/) | 50,000 | 42 | 1.47s | `d2f4ef1` · 2026-07-10 05:09 UTC | `ed1e0a4129cfe2b2` |
| [`qa-sampling/`](qa-sampling/) | — | 42 | 0.47s | `d2f4ef1` · 2026-07-10 05:09 UTC | `6c864d42c901e2ef` |
| [`sanctions-name-screening/`](sanctions-name-screening/) | 50,000 | 42 | 2.49s | `d2f4ef1` · 2026-07-10 05:09 UTC | `94abc04ba1d4c354` |
| [`tm-threshold-tuning/`](tm-threshold-tuning/) | — | 42 | 1.27s | `d2f4ef1` · 2026-07-10 05:10 UTC | `288b273adb50c058` |
| [`transaction-monitoring/`](transaction-monitoring/) | 50,000 | 42 | 0.65s | `d2f4ef1` · 2026-07-10 05:10 UTC | `72260f724af88900` |
| [`watchlist-knowledge-base/`](watchlist-knowledge-base/) | 3,000 | 42 | 0.31s | `d2f4ef1` · 2026-07-10 05:10 UTC | `a6357027fa3d0ea7` |

## What this evidence does and does not establish

**It establishes:**

- The numbers in every `VALIDATION-REPORT.md` are emitted by a harness, not typed by a person, and they re-derive exactly from a fixed seed on any machine.
- Each engine's safety invariant is enforced as a **build gate**: the harness exits non-zero if the engine ever auto-clears a labelled true positive, rates a hard-risk case low, or passes a critically deficient item. A regression cannot be merged quietly, because CI re-runs all of it.
- The engines are deterministic and dependency-free, so "it works on my machine" is not part of the argument.

**It does not establish:**

- **Any claim about live performance.** Every population here is synthetic and every entity fictional. The generators model the *shape* of real variation — false-positive dominance, transliteration noise, adversarial near-misses — not its full messiness. A real deployment must recalibrate against its own labelled data.
- **That the synthetic population is representative.** It is constructed, so ground truth is known; that is exactly what makes it *not* a sample of the real world. The generator plants the adversarial cases the author thought of. It cannot plant the ones nobody thought of.
- **That these are production controls.** They are transparent reference implementations chosen for auditability. The scoring *contract* in each `METHODOLOGY.md` is what travels, not a turnkey system.
- **Fitness for use.** No engine here decides anything. Each scores, routes, or documents; a qualified human clears, blocks, files, and signs.

## The attestation chain

```
seed  ->  generate_synthetic_data.py   (labelled population, ground truth known)
      ->  scorer / engine              (pure stdlib, deterministic, no network)
      ->  run_validation.py            (computes metrics; EXITS NON-ZERO on a
                                        safety breach — the gate, not a sentence)
      ->  evidence/                    (report + metrics + manifest, all emitted)
      ->  _tooling/verify_evidence.py  (re-derives and diffs against committed)
      ->  GitHub Actions               (runs the above on every commit to main)
```

Each link is checkable independently. The last one is checkable by someone who does not trust the author at all: the workflow definition is [`.github/workflows/validate.yml`](../.github/workflows/validate.yml), and its run history is public.

## Reading the reports

Each `evidence/VALIDATION-REPORT.md` follows a fixed section order — methodology, population construction, operating point, per-category performance, threshold sensitivity, the safety argument (with its statistical bound), volume impact, limitations, reproduction. The standard every harness must meet is [`RIGOR-CONTRACT.md`](RIGOR-CONTRACT.md); the model-risk framing is [`GOVERNANCE.md`](GOVERNANCE.md).

---

*Synthetic data throughout. No real person, entity, vessel, address, or list entry is represented; the recurring institution is the fictional Harborview Financial Group. Nothing here is legal advice or a production control.*
