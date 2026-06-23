# Methodology — On-Chain KYT Address-Risk Engine

The regulator-facing specification of the scoring and disposition logic. Every input,
threshold, and rule below exists as a named construct in [`scorer.py`](scorer.py) and
[`../_lib/graph.py`](../_lib/graph.py); those files are the executable form. Evidence:
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md). Shared governance:
[`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** A crypto-monitoring tool flags an address whenever it can trace
> a connection to bad money — a sanctioned wallet, a mixer, a darknet market. But a
> connection isn't the same as risk: the bad money might be six hops away, a tiny
> sliver of the funds, or have passed through a big exchange that scrambles the
> trail. This engine reads how *close*, how *much*, and whether an exchange *broke*
> the trail, then sorts each flag — clear it (with a concrete reason), review it, or
> escalate it (material, direct, unbroken exposure to something serious). It scores
> and routes; it never freezes funds or files a report on its own.

---

## 1. Problem framing and error posture

A KYT / chain-analytics tool flags an address that has any traceable exposure to an
illicit entity. Most flags are not actionable: the exposure is remote, immaterial,
to a benign category, or broken by a commingling intermediary. The error costs are
asymmetric, as in the other frameworks: a **false negative** (clearing material,
proximate exposure to a serious illicit source) is a regulatory failure with zero
tolerance; a **false positive** (keeping a non-actionable flag) is operational cost.

## 2. Exposure features (from the graph layer)

For each address, the chain-analytics layer (`_lib/graph.propagate_taint`) propagates
severity-weighted taint forward from labeled illicit **seed** addresses, decaying
with each hop and each edge's transfer fraction, and stopping at **breaker** nodes
(high-throughput commingling services). It yields the address's strongest exposure:

- `top_category` — the illicit (or benign) category of the strongest exposure.
- `exposure` ∈ [0,1] — `seed_severity × Π(transfer_fraction × hop_decay)` along the
  best path; encodes severity, distance, and value attenuation together.
- `hops` — distance to the seed.
- `amount_fraction` — the traceable value share (∏ of edge value-fractions).
- `via_breaker` — the address is reachable from illicit funds **only** through a
  commingling intermediary, so the taint is not attributable to it.
- `direction` — inbound (received from) or outbound (sent to the illicit entity).

Category severities (illustrative; configure to your analytics taxonomy): sanctioned
/ terrorism-financing 1.0, ransomware / darknet 0.95, mixer 0.92, stolen-funds 0.88,
fraud-proceeds 0.80, scam 0.78, high-risk-exchange 0.60, gambling 0.40, unhosted 0.30;
benign categories (licensed exchange, blue-chip DeFi, merchant, mining pool) 0.0.

## 3. Disposition rules (in firing order)

Named clear causes first; the risk score only ranks what survives.

1. **AUTO_CLEAR — benign_category.** The category severity is 0 (a licensed exchange,
   blue-chip DeFi, merchant) — the exposure is not illicit at all.
2. **AUTO_CLEAR — broken_intermediary.** `via_breaker` — illicit funds reach the
   address only through a commingling service; attribution is broken downstream.
3. **AUTO_CLEAR — de_minimis.** `amount_fraction < deminimis_fraction` (0.02) — the
   traceable value share is below materiality.
4. **AUTO_CLEAR — diluted_distant.** No path, or `hops > max_actionable_hops` (4), or
   `exposure < dilution_floor` (0.04) — the illicit source is too remote.
5. **ESCALATE.** `exposure ≥ escalate_floor` (0.30) — material, proximate, unbroken
   exposure to a serious category; routed for investigation / a SAR or freeze
   decision.
6. **ANALYST_REVIEW** — everything else, priority by risk (HIGH ≥ 0.12, MEDIUM ≥
   0.05, else LOW). Includes the mid-severity ambiguous residual that is neither
   clearable nor escalatable.

### Why false-negative safety is structural

Material, proximate, unbroken exposure to a serious illicit category cannot satisfy
any clear cause: the category is not benign, the trail is not broken, the value is
not de-minimis, and the source is not diluted/distant. So a genuinely high-risk
address is never auto-cleared. The validation harness enforces this as a build gate
(recall floor 1.0).

## 4. Tunable constants

`scorer.Config`: `deminimis_fraction` (0.02), `max_actionable_hops` (4),
`dilution_floor` (0.04), `escalate_floor` (0.30), review bands. The category
severities and the propagation `hop_decay` are the deeper calibration surface. See
[`tuning.md`](tuning.md).

## 5. Governance and boundaries

Mapped to public guidance per [`../GOVERNANCE.md`](../GOVERNANCE.md) — SR 11-7, FFIEC,
**FATF Recommendation 15 / 16** (virtual assets and the Travel Rule), and Wolfsberg.
The engine dispositions; the freeze / SAR / off-boarding decision is a documented
human action. Note the dependency: the exposure features come from an upstream
chain-analytics vendor whose attribution accuracy must be validated alongside this
engine — a mis-attributed cluster label propagates into this engine's output.
