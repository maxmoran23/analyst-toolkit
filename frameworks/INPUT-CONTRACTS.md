# Input contracts and boundary regressions

Synthetic accuracy results measure the populations registered in [REPRODUCE.json](REPRODUCE.json). They do not establish correctness for malformed integration inputs. [test_boundaries.py](test_boundaries.py) separately exercises input failures and numerical edge cases using only synthetic records.

## Scoring inputs

The shared [numeric validator](_lib/validation.py) checks declared integer, floating-point and boolean dataclass fields before the sanctions, PEP, adverse-media, customer-risk, jurisdiction-risk, product-risk, investigation-QA, transaction-monitoring, fraud and KYT scorers apply their decision rules. Numeric strings, booleans passed as numbers, nonfinite floats and string boolean flags raise `ValueError`. Per-engine ranges and categorical taxonomies remain separate contracts; the common validator does not establish that every integration field is valid.

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
