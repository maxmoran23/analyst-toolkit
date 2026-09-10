# Input contracts and boundary regressions

Synthetic accuracy results measure the populations registered in [REPRODUCE.json](REPRODUCE.json). They do not establish correctness for malformed integration inputs. [test_boundaries.py](test_boundaries.py) separately exercises input failures and numerical edge cases using only synthetic records.

## Scoring inputs

The shared [numeric validator](_lib/validation.py) checks declared integer, floating-point and boolean dataclass fields before the sanctions, PEP, adverse-media, customer-risk, jurisdiction-risk, product-risk, investigation-QA, transaction-monitoring, fraud and KYT scorers apply their decision rules. Numeric strings, booleans passed as numbers, nonfinite floats and string boolean flags raise `ValueError`. Per-engine ranges and categorical taxonomies remain separate contracts; the common validator does not establish that every integration field is valid.

Customer-risk and NPA rating entry points normalize categorical case and surrounding whitespace against their configured reference tables, using copies rather than mutating caller records. Unknown customer types, channels, products, NPA categories, or country codes raise `ValueError`; they no longer receive fallback scores. Collection inputs must be lists or tuples of registered values. The country tables are limited illustrative mappings, not global coverage or current regulatory determinations. An unregistered country requires an explicit methodology and reference-table update before scoring. Existing empty product, operating-country, or target-jurisdiction lists retain their documented implementation defaults; acceptance of those defaults does not establish source completeness.

Customer opacity/activity and NPA privacy/cash/cross-border inputs must lie in `[0, 1]`. Jurisdiction input scores must lie in their declared `[0, 100]` domains, except the Basel input in `[0, 10]`. Invalid values raise errors rather than being clipped into a favorable score. Missing jurisdiction dimensions must name unique registered dimensions, and at least one dimension must remain assessed. Missing labels normalize case and whitespace without changing the supplied list; numeric placeholders still must satisfy the dataclass contract, even for excluded dimensions.

Customer, jurisdiction and NPA floor configuration cannot fall below the minimum tiers published by each engine. Stronger floor settings remain valid. Score bands and NPA condition thresholds must remain within their declared scales; NPA review intervals require a positive integer for every tier. These checks constrain configuration syntax and mandatory floors, not the suitability of a deployment's calibration.

The feature-only `score_features` interfaces require every documented customer-risk or NPA factor exactly once; missing or additional keys raise `ValueError`. Jurisdiction feature scoring permits a nonempty subset of documented dimensions and rejects unknown keys. All three interfaces require finite numeric sub-scores in `[0, 100]`, excluding booleans. These functions compute a composite only; mandatory floors and routing require the full `rate` or `assess` entry point and its categorical inputs.

KYT exposure and traceable-value fractions and TM pass-through and high-risk-geography fractions must lie in `[0, 1]`. KYT hop distance is a nonnegative integer or `None`; absent distance retains its existing manual-review treatment when exposure is material and unbroken. KYT fraction/score configuration remains in `[0, 1]` and its maximum actionable hop count is nonnegative.

Transaction-monitoring alerts and fraud events must match the customer identifier of their supplied baseline. Positive activity against a zero baseline remains maximally anomalous; its bounded severity is finite. Rule callbacks must return a boolean fired flag and finite severity in `[0, 1]`.

Data-quality feed assessment rejects an empty population, blank or repeated record identifiers, invalid as-of calendar dates and malformed numeric configuration. Record identifiers must be unique because the engine aggregates defect rates by record identity. Repeated customer identifiers remain valid inputs to the duplicate-detection rules.

An ownership entity must explicitly declare the boolean `ownership_complete: true` before graph resolution can support auto-clearance. An absent, false or string-valued completeness declaration routes unresolved ownership to review. A known threshold crossing or qualifying control relationship remains reportable despite incomplete ownership elsewhere.

## Evidence and calibration

- Provenance timestamps must parse to actual UTC instants. Canonical evidence JSON rejects NaN and infinity.
- Confusion matrices reject unequal label counts and nonbinary labels. Threshold sweeps materialize iterables once so each threshold evaluates the same population.
- TM calibration requires positive labelled cases to establish recall. Its safety floor uses the unrounded ratio; four-decimal display rounding cannot turn a below-floor result into an acceptable recommendation.
- Sampling rejects duplicate population identifiers, including identifiers repeated across strata, and rejects misaligned parallel stratum labels. Selection remains seeded and reproducible.

## Graph propagation

The graph layer checks finite `[0, 1]` edge fractions, severities and hop decay. Seed queries compare their direct zero-hop severity with attributable propagated exposure and retain the stronger result with its source and hop metadata. The two attribution passes consume the same materialized edges, including when the caller supplies a generator. Propagation retains the strongest state at each node and depth, avoiding redundant path replay while preserving shorter paths with remaining hop budget.

## Run the checks

From the repository root:

```sh
python3 -m unittest discover -s frameworks -p 'test_boundaries.py'
python3 _tooling/verify_evidence.py
```

The first command tests boundary behavior. The second re-derives every registered evidence pack and checks it against the committed output. Neither check substitutes for validation on a deployment's own labelled population and input schema.
