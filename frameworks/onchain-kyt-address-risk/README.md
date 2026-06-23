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
