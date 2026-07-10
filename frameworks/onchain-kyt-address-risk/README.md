# On-Chain KYT Address-Risk Framework

A runnable, deterministic engine that dispositions blockchain-address KYT flags from
their tainted-path exposure to illicit entities — clearing the remote, immaterial,
benign, and intermediary-broken flags while never auto-clearing material, proximate,
unbroken exposure to a serious illicit source.

> **In plain terms:** Crypto-monitoring tools flag any address with a traceable link
> to bad money, which floods analysts with links that don't matter — bad money six
> hops away, a tiny sliver of funds, or funds that passed through a big exchange that
> scrambles the trail. This engine measures how close, how much, and whether an
> exchange broke the trail, then clears the flags it can prove are non-actionable and
> escalates direct, material exposure to sanctioned wallets, mixers, ransomware, and
> darknet markets. It never freezes funds or files a report — a person does that. On
> a 50,000-address test it cut the queue ~83% while missing zero genuinely risky
> addresses.

---

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Crypto and blockchain-analytics teams screening wallet activity. |
| **The question it answers** | How exposed is this blockchain address to illicit funds, and how close is that exposure? |
| **What it is** | A small, transparent, runnable scoring engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never freezes funds, blocks an address, or reports. It distinguishes 'one hop from a mixer' from 'six hops away through an exchange' and hands the analyst the reasoning. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/onchain-kyt-address-risk
python3 run_validation.py --seed 42 --addresses 50000
```

Pure Python standard library: nothing to install, no network access, well under a second. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read "recall 1.0000" on this page

The engine missed **none** of the 3,055 truly tainted addresses planted in the test population. Read that the way you would read an attribute sample that came back with zero exceptions: you do not conclude the deviation rate is zero — you conclude it is **below 0.10% at 95% confidence**. That exact one-sided bound is published for every engine in [`../EVIDENCE.md`](../EVIDENCE.md), and it tightens only by testing more true cases. It is a property of this synthetic population, not a forecast about live data.

<!-- /STANDALONE-BRIEF -->

## What it produces

Per flagged address, a disposition (AUTO_CLEAR / ANALYST_REVIEW / ESCALATE) with a
`risk` score and a named reason, from the address's strongest tainted-path exposure
(category severity, hop distance with decay, value share, intermediary breaks).

## Validation result (seed 42, 50,000 addresses — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| Recall on high-risk addresses (FN-safety) | **1.0000 — 0 false negatives** |
| False-positive reduction | **87.9%** |
| Human review-volume cut | **82.5%** (50,000 → 8,741 to a human) |
| Analyst queue precision lift | **6.1% → 35.0%** (~5.7×) |
| Stability | recall 1.0 across 6 seeds; FP-reduction 87.6–88.0% |
| Scale | 200,000 addresses in ~2s |

Per-category clear rate: benign_category 100% · broken_intermediary 100% ·
de_minimis 100% · diluted_distant 100% · ambiguous_residual 0% (the mid-severity band
left open for review).

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --addresses 50000
python3 run_validation.py          --seed 42 --addresses 50000
```

`run_validation.py` regenerates the population in-memory — deriving each address's
exposure features by running the real `../_lib/graph` taint propagation over a
constructed subgraph — scores it, writes the evidence pack, and **exits non-zero if
any high-risk address is auto-cleared**. Optional: `--trials 5`, `--addresses 200000`.

Ad-hoc: `python3 scorer.py` composes the graph layer with the engine on one example.

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — exposure features, disposition logic, governance. |
| [`scorer.py`](scorer.py) | The deterministic disposition engine (consumes graph-derived features). |
| [`../_lib/graph.py`](../_lib/graph.py) | Taint propagation with hop-decay + breaker nodes (the chain-analytics layer). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded addresses; features derived via the graph layer. |
| [`run_validation.py`](run_validation.py) | Validation harness + evidence; FN-safety gate. |
| [`tuning.md`](tuning.md) · [`DEPLOYMENT.md`](DEPLOYMENT.md) · [`evidence/`](evidence/) | Recalibration · Copilot mapping · committed run output. |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. In production the exposure features come from a chain-analytics vendor
(Chainalysis / TRM / Elliptic), whose cluster attribution accuracy must be validated
alongside this engine — a mis-attributed label propagates into the disposition. The
category severities, hop-decay, and thresholds are illustrative and configurable. All
data synthetic; nothing here screens a real address.
