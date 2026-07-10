# Runnable financial-crime engines, each with evidence you can re-derive

**Fourteen small, transparent scoring engines for the financial-crime problems that are
really a volume problem** — sorting 50,000 sanctions alerts a month, tuning a monitoring
rule's threshold, deciding whether a customer file is fit to screen against. Each one
ships the method written out in full, a generator that builds a realistic test population
with known answers, and a validation harness that measures how well the engine did and
**fails the build if it ever misses a true hit**.

> **In plain terms:** Most of this repository is *written instructions* you paste into an
> AI assistant. This folder is different — these are **working calculators**. You run one,
> and it scores tens of thousands of made-up-but-realistic cases and reports exactly how
> accurate it was, including that it never wrongly cleared a real match. Nothing is taken
> on trust: every number published here is re-derived from scratch by an automated check
> on every change to this repository.

**New here?** Pick the engine for your team from the table below and open its folder —
each one's page is written to be read on its own. Want the whole evidence picture in one
place, including the exact confidence bound behind every accuracy claim?
Read [`EVIDENCE.md`](EVIDENCE.md).

> **In plain terms:** The prompts elsewhere in this repo tell an AI assistant how to
> *think about* a task. The frameworks here are working calculators for the tasks
> where "did it get the answer right?" is a measurable question — like sorting
> 50,000 sanctions alerts. Each one comes with proof: a script anyone can re-run
> that scores tens of thousands of made-up-but-realistic cases and reports exactly
> how accurate it was, including that it never wrongly cleared a real hit.

## Why this is a separate pillar

These are code, not paste payloads, so the repository's two-file rule (which keeps
every pasted prompt self-contained) does not apply to them — exactly as it does not
apply to [`quant/`](../quant/). A framework is multi-file by design: a methodology
spec, an engine, a data generator, a validation harness, and an evidence pack.
Pure Python standard library only — no numpy, no pandas, no third-party package of
any kind — so a framework runs unchanged on a locked-down machine.

### On network access

**No framework requires the network, and no validation run touches it.** Every
harness, every metric, and every committed evidence pack is produced offline from a
seeded synthetic population; that is what makes the evidence reproducible.

Two frameworks additionally expose an **optional, opt-in live-ingest path**, isolated
in a single module each and reachable only when a caller explicitly asks for it:

| Framework | Module | What it may fetch | Default |
|---|---|---|---|
| [`watchlist-knowledge-base/`](watchlist-knowledge-base/) | [`_lib/knowledge_base/ingest.py`](_lib/knowledge_base/ingest.py) | The public OFAC SDN CSV, UN consolidated XML, and UK OFSI ConList CSV — each parser written against the live document. The EU list is registered without a parser: its endpoint answers 403 unauthenticated | Harness passes `offline=True`; nothing is cached or redistributed |
| [`onchain-osint-evidence/`](onchain-osint-evidence/) | [`engine.py`](onchain-osint-evidence/engine.py) (`fetch_json`) | Public block-explorer JSON responses | Harness runs from committed fixtures |

Both fetchers **degrade gracefully rather than raise**: on `offline=True`, a timeout,
an HTTP error, or an unparseable body they return `None`, and the caller falls back to
the synthetic or fixture path so the pipeline always completes. The watchlist harness
asserts this explicitly — it fails the build if any source raises instead of degrading
when offline. Nothing else in `frameworks/` imports `urllib`.

Note the direct-call default: `ingest_source(key)` uses `offline=False`, so calling it
yourself will attempt a fetch. Pass `offline=True` on a machine where egress is
restricted or where a reproducible run matters.

## The package standard

Every `frameworks/<domain>/` package contains the same fixed set, so once you have
read one you can navigate any other:

| File | Role |
|---|---|
| `README.md` | Two-audience front door: plain-terms summary + technical overview + run commands + headline result. |
| `METHODOLOGY.md` | The regulator-facing spec — every input, weight, threshold, and named decision rule, in firing order, with rationale, plus the SR 11-7 framing. The engine is its executable form. |
| `scorer.py` (or engine) | The deterministic reference implementation. Pure stdlib + `_lib/`. Named-reason dispositions; auto-clear only on a provable cause; never auto-block or auto-file. |
| `generate_synthetic_data.py` | Seeded, labelled, scalable population. Every negative carries a category; the design plants adversarial cases. |
| `run_validation.py` | Runs the engine over the population, computes the metrics, writes the evidence pack, and **exits non-zero if a false-negative-safety invariant is violated**. |
| `tuning.md` | How to recalibrate the operating point for a real environment. |
| `DEPLOYMENT.md` | How the engine maps onto a Microsoft Copilot Studio / Power Platform deployment. |
| `evidence/` | The committed real-run output: validation report, metrics JSON, threshold sweep, confusion matrix, run manifest. |
| `data/` | `.gitignore`d — regenerated from seed, never committed. Credibility is reproduction-from-seed, not data-in-repo. |

Shared across the pillar:

| File | Role |
|---|---|
| [`EVIDENCE.md`](EVIDENCE.md) | **The evidence archive** — the reproduction command per framework, the exact confidence bound behind every safety claim, a results digest per pack, and what the evidence does *not* establish. Generated from the committed packs; CI fails if hand-edited. |
| [`REPRODUCE.json`](REPRODUCE.json) | Single source of truth for the command that re-derives each evidence pack. |
| [`GOVERNANCE.md`](GOVERNANCE.md) | The SR 11-7 / model-risk framing every framework instantiates. |
| [`DEPLOYMENT-PATTERN.md`](DEPLOYMENT-PATTERN.md) | The reusable Copilot Studio mapping. |
| [`RIGOR-CONTRACT.md`](RIGOR-CONTRACT.md) | What `run_validation.py` must enforce and how it wires into CI. |
| [`_lib/`](_lib/) | Shared pure-stdlib primitives, reused across frameworks: name normalization + token rarity, matching (Jaro-Winkler / Soundex / IDF-weighted token-set), evaluation metrics, deviation/aggregation stats, a named-rule mechanism, weighted-composite scoring + monotonicity, content relevance, transaction-graph taint propagation, provenance-stamped evidence records, and exact attribute-sampling statistics (binomial/hypergeometric tails, upper deviation limit). |

## Frameworks

| Framework | Problem | Status |
|---|---|---|
| [`sanctions-name-screening/`](sanctions-name-screening/) | Disposition sanctions-screening alerts (the ~50k/month false-positive backlog) | **Built & validated** — recall 1.0 (0 FN), 92% FP-reduction, evidence committed |
| [`transaction-monitoring/`](transaction-monitoring/) | Score & triage TM alerts (structuring, funnel, pass-through, velocity, geography) against the customer baseline | **Built & validated** — recall 1.0 (0 FN), 85% FP-reduction, evidence committed |
| [`customer-risk-rating/`](customer-risk-rating/) | Weighted customer risk score + LOW/MEDIUM/HIGH tiering with mandatory floors | **Built & validated** — 0 hard-risk customers rated LOW, monotonic, discriminating, evidence committed |
| [`adverse-media-screening/`](adverse-media-screening/) | Disposition negative-news hits on two axes (right party? materially adverse?) | **Built & validated** — recall 1.0 (0 FN), 80% FP-reduction, evidence committed |
| [`onchain-kyt-address-risk/`](onchain-kyt-address-risk/) | Score blockchain-address KYT flags by tainted-path exposure (hop distance, value share, commingling breaks) | **Built & validated** — recall 1.0 (0 FN), 88% FP-reduction, evidence committed |
| [`tm-threshold-tuning/`](tm-threshold-tuning/) | Above/below-the-line testing — validate & tune monitoring-rule thresholds (the model-validation framework) | **Built & validated** — every recommendation holds detection ≥95% floor, all leaks remediated, 67% volume cut, evidence committed |
| [`watchlist-knowledge-base/`](watchlist-knowledge-base/) | Self-maintaining watchlist — ingest public lists (OFAC/EU/UN/UK), dedupe across them, track changes, learn from false positives | **Built & validated** — 0 false merges (structural), auto-merge recall 1.0, change-delta exact, feedback gated; evidence committed |
| [`pep-screening/`](pep-screening/) | Disposition PEP-screening alerts on two axes (right party? in-scope status?) — prominence tiers, step-down decay, jurisdiction buckets | **Built & validated** — recall 1.0 (0 FN), 84% FP-reduction, evidence committed |
| [`investigations-case-qa/`](investigations-case-qa/) | Second-line QA scoring of completed investigation case files before closure (completeness, evidence support, consistency, timeliness, narrative) | **Built & validated** — critical-deficiency recall 1.0 (0 deficient files passed QA), 100% clean-file pass rate, evidence committed |
| [`onchain-osint-evidence/`](onchain-osint-evidence/) | Turn public block-explorer data into a provenance-stamped, investigation-grade evidence pack (annex + facts + counterparty rollup; observations, never attributions) | **Built & validated** — provenance completeness 100%, reconciliation exact (0 dropped / 0 duplicated), byte-identical output, evidence committed |
| [`npa-product-risk/`](npa-product-risk/) | Score & route new-product / new-activity proposals pre-launch — tier, named approval route, mandatory conditions, review interval | **Built & validated** — 0 floor-triggered proposals tiered LOW, prohibited list never scored around, monotonic, discriminating, evidence committed |
| [`data-quality-rules/`](data-quality-rules/) | Assess the critical data elements feeding screening/monitoring (name, DOB, country, identifier, uniqueness, staleness) — "is this feed fit to screen against?" | **Built & validated** — critical-defect recall 1.0 (0 missed), 0 false flags on clean records, hard feed gate holds (no breached feed passes), evidence committed |
| [`qa-sampling/`](qa-sampling/) | Statistical attribute sampling for independent testing / QA — plan, select, and evaluate tests of controls from exact tail math instead of lookup tables | **Built & validated** — upper-deviation-limit cross-check exact (max divergence 5.4e-12), 0 structural breaches, measured false-assurance 0/150 within design risk, solver monotone, evidence committed |
| [`jurisdiction-risk/`](jurisdiction-risk/) | Composite a country/territory's inherent risk from seven public indices (FATF, Basel, CPI, WGI, secrecy, organized crime, terrorism) with hard-risk floors — LOW/MEDIUM/HIGH/CRITICAL | **Built & validated** — 0 hard-designated jurisdictions rated below floor, monotonic, discriminating, evidence committed |

## Standing caveat

Each framework is a transparent **reference implementation** chosen for
auditability, not a production control. A real deployment swaps internals and
recalibrates against its own labelled data; the scoring *contract* in each
`METHODOLOGY.md` is what travels. All data is synthetic; entities are fictional
(the recurring institution is **Harborview Financial Group**). Nothing here
screens or assesses any real party.
