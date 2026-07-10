# Methodology — Jurisdiction-Risk Framework

The regulator-facing specification of the engine: every dimension, its normalization
from a raw public index, the weighting, the tier bands, and the hard-risk floors. The
engine in [`scorer.py`](scorer.py) is the executable form of this document; nothing it
does is outside this spec.

The engine rates **inherent geographic risk**. It does not decide whether to enter,
exit, bank, or de-risk a market, and it is not a political judgement about a country.

---

## 1. The seven dimensions

Each dimension is normalized onto a common 0-100 **risk** scale (higher = more risk).
The public source each is drawn from — with URL, edition cadence, and retrieval
discipline — is in [`SOURCE-LIBRARY.md`](SOURCE-LIBRARY.md).

| Dimension | Weight | Raw public index | Normalization (raw → 0-100 risk) |
|---|---:|---|---|
| AML/CFT deficiency | 0.30 | Basel AML Index (0-10, higher worse) | `risk = value × 10` |
| Corruption | 0.22 | TI CPI (0-100, higher cleaner) + WGI control-of-corruption percentile | `risk = mean(100 − CPI, 100 − CoC percentile)` |
| Governance | 0.16 | WGI rule-of-law percentile (0-100, higher better) | `risk = 100 − percentile` |
| Financial secrecy | 0.14 | Tax Justice Financial Secrecy Index (0-100, higher more secret) | `risk = secrecy score` |
| Organized crime | 0.08 | Global Organized Crime Index (0-100 risk) | `risk = score` |
| Terrorism | 0.05 | Global Terrorism Index (0-100 risk) | `risk = score` |
| Instability | 0.05 | Fragile States / political-instability measure (0-100 risk) | `risk = score` |

The weights are relative importances; the composite normalizes across whatever
dimensions are present, so a missing dimension is **excluded and the remaining weights
renormalized** — never scored as zero or a midpoint. Weights sum to 1.00 by design but
need not; the engine normalizes.

## 2. The composite

```
composite = Σ (dimension_risk × weight)  /  Σ (weight, over present dimensions)
```

A pure, non-negative weighted mean. This is the `score_features` function the
monotonicity property test runs against, and the unit a deployment exposes as a tool.

## 3. Tier bands

| Composite | Tier |
|---|---|
| 0 – 39.9 | LOW |
| 40 – 59.9 | MEDIUM |
| 60 – 79.9 | HIGH |
| 80 – 100 | CRITICAL |

## 4. Hard-risk floors (the overrides)

Categorical designations force a minimum tier that the weighted mean cannot undercut.
The final tier is the **worse** of the weighted-band tier and the highest floor
triggered. A floor can only raise a tier, never lower it — which is why the model stays
monotonic.

| Designation | Floor |
|---|---|
| Comprehensive sanctions program on the jurisdiction | CRITICAL |
| FATF "black list" (call for action) | CRITICAL |
| FATF "grey list" (increased monitoring) | HIGH |
| EU list of high-risk third countries | HIGH |
| INCSR "primary money-laundering concern" | HIGH |

The rationale: these designations are authoritative categorical determinations of
elevated risk. A jurisdiction can score well on corruption or governance and still be
grey-listed for specific AML/CFT deficiencies; the floor ensures a single flattering
index can never talk it below the tier its designation requires.

## 5. What the validation proves

The harness ([`run_validation.py`](run_validation.py)) validates a rating model the way
a rating model must be validated — not against a fabricated "true tier", but on three
structural properties, each a build gate:

1. **Discrimination.** Mean composite rises across the designed soft strata
   (designed_low < designed_medium < designed_high). If it does not, the engine is not
   separating risk and the build fails.
2. **Floor safety** (the analogue of false-negative safety). No comprehensively-
   sanctioned or FATF-black-listed jurisdiction is rated below CRITICAL; no FATF-grey /
   EU-high-risk / INCSR-primary jurisdiction is rated below HIGH. Computed over the
   actual designated jurisdictions, not the stratum label, so it holds however the
   population was built. A single breach fails the build.
3. **Monotonicity.** Raising any one dimension sub-score never lowers the composite,
   tested over 300 random base vectors across all seven dimensions. A structural
   property of the non-negative weighted sum and the raise-only floors.

The population is fully synthetic and every jurisdiction fictional, so ground truth
(the designed stratum, the designations planted) is known — which is exactly what makes
it a test rather than a sample of the real world.

## 6. Governance and limitations

- **Not a production control.** A transparent reference implementation chosen for
  auditability. The scoring *contract* in this document is what travels, not a turnkey
  system.
- **Weights and bands are illustrative.** Calibrate them to your own geographic-risk
  methodology and risk appetite ([`tuning.md`](tuning.md)).
- **Designations are time-sensitive.** FATF, EU, INCSR, and sanctions statuses change
  on their own cadences; a deployment refreshes them against the authoritative source
  at time of use. The engine applies whatever designation it is given.
- **Inherent, not residual.** This scores the jurisdiction's inherent risk. Residual
  risk depends on the controls a firm applies, which is a separate assessment.
- **A human decides.** The rating drives the intensity of due diligence and monitoring;
  the market and onboarding decisions, and any documented override, are human acts.
