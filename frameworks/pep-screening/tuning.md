# Tuning — recalibrating the operating point

The thresholds in `scorer.Config` and the Axis B constants (tier weights, decay
floors, step-down horizons, jurisdiction bucket weights) are a deliberately
conservative posture validated on synthetic data. They are a **starting point,
not a production calibration**. Before relying on this engine, recalibrate
against a labelled sample of your own alerts and record every change with its
justification.

> **In plain terms:** The dials below control two different things — how sure
> the engine must be that a name really is the listed person, and how long a
> former official stays "risky" after leaving office. The first set is tuned by
> testing against alerts your analysts already decided. The second set is not a
> statistics question at all: it is written risk appetite, and it should be set
> by policy, documented, and re-reviewed on a schedule.

## The dials

**Config (Axis A / disposition thresholds):**

| Constant | Default | Raise it → |
|---|---|---|
| `generic_max_share` | 0.005 | more name tokens treated as common → more generic-token clears, higher FN risk |
| `no_name_match` | 0.15 | more low-overlap alerts cleared as wrong party (riskier) |
| `common_name_cap` | 0.50 | uncorroborated common-name matches rank higher in the queue |
| `escalate_strength` / `escalate_materiality` | 0.60 / 0.40 | fewer escalations |
| `review_high` / `review_medium` | 0.35 / 0.15 | shift analyst priority bands |

**Axis B (policy parameters — set by governance, not by sweep):**

| Constant | Default | Meaning |
|---|---|---|
| `TIER_WEIGHT` / `RCA_FRACTION` | 1.0 / 0.8 / 0.55 · 0.60 | relative prominence; RCA inheritance fraction |
| `TIER1_FLOOR` / `TIER2_FLOOR` | 0.40 / 0.15 | the never-zero residual for former senior officials |
| `TIER3_HORIZON_YEARS` | 5.0 | the documented step-down horizon for mid-level officials |
| `RCA_HORIZON_FACTOR` | 0.5 | RCA decays in half the principal's window |
| `ADVERSE_DECAY_FLOOR` | 0.5 | how strongly an adverse indicator suspends step-down |
| `JURISDICTION_WEIGHT` | 1.0 / 0.75 / 0.55 | ILLUSTRATIVE bucket weights |

The dial that moves the false-negative/false-positive trade-off hardest is
`TIER3_HORIZON_YEARS` — every year removed clears more former-official volume
and widens the window in which a still-relevant former official is cleared.
Treat it as a policy change with sign-off, not a tuning knob.

## Calibrate the pieces against the right sources

- **Genericness** (`generic_max_share`, and the `TokenStats` corpus): build the
  token-rarity model from the names you actually screen — your customer
  population — not only the PEP list. A name's collision risk is a property of
  *your* book. Re-confirm that the common-name band (the Kim/Park/Mohammed/
  Garcia problem in your population) lands above the threshold.
- **Jurisdiction buckets**: the HIGH/MEDIUM/LOW assignment is upstream
  configuration. Source it from a documented public index, record the vintage,
  and refresh on a schedule — indices move, and a stale bucket map is a silent
  calibration drift.
- **Step-down horizons and floors**: these encode "once a PEP, always a PEP?"
  as explicit, documented policy. Public guidance treats former-PEP status as a
  risk-based question; whatever horizon your institution adopts, the value of
  this engine is that the horizon is written down, versioned, and applied
  uniformly rather than re-litigated per alert.
- **List-vendor fields**: tier, status, and adverse flags arrive from the list
  vendor. Sample-test their accuracy; a wrong `status=FORMER` or a missing
  adverse flag upstream becomes a wrong disposition here.

## Procedure

1. **Assemble a labelled sample.** A few thousand historical PEP alerts a
   qualified analyst has dispositioned (right party / wrong party, and the
   in-scope determination), including known former-official cases.
2. **Run the sweep.** Score the sample and read the threshold-sensitivity
   table (`run_validation.py` produces this shape). Find where recall on
   in-scope matches first drops below 1.0 — the hard ceiling.
3. **Pick the Axis A operating point** that holds recall at the floor while
   minimizing the residual queue. Expect a common-name-ambiguous band that
   stays open — do not tune it away; it is unresolvable by construction.
4. **Set the Axis B parameters by policy**, with governance sign-off: horizons,
   floors, RCA fraction, bucket weights. Then re-run the gate.
5. **Re-run the false-negative gate after any change.** A change that
   auto-clears any labelled in-scope match is rejected.
6. **Record it.** Constant changed, old/new values, labelled-sample result
   before and after, rationale, approver. This is the model-change-management
   evidence an examiner expects.

## What not to do

- Do not clear common-name matches with no identifier to cut volume — that is
  exactly the move that clears a real PEP who banks under a common name.
- Do not shorten `TIER3_HORIZON_YEARS` (or raise `RCA_HORIZON_FACTOR`'s effect)
  as a queue-management measure. Horizon changes are policy changes.
- Do not auto-clear on the `combined` score alone. The sweep in the validation
  report shows why: the lowest-scoring true matches are decayed-but-in-scope
  former senior officials, precisely the band a bare threshold clears first.
- Do not trust list-vendor tier/status/adverse fields blindly — a vendor error
  upstream becomes a false negative here.
- Do not treat the synthetic-data operating point as production-ready.
