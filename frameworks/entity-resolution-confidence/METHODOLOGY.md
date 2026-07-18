# Methodology

## Decision objective

For every query–candidate pair, the engine chooses `SAME`, `DIFFERENT`, or `REVIEW`. The loss function is deliberately symmetric: both false negatives (clearing a true match) and false merges (combining distinct people) are controlled. `REVIEW` is the correct result when available evidence cannot carry either conclusion.

This follows an SR 11-7-style model-risk frame: documented purpose and limitations; transparent design; independent, repeatable validation; outcomes analysis; change control; effective challenge through adversarial negative controls; and ongoing monitoring. It is framing, not a representation that this engine has received regulatory validation.

## Normalization and name treatment

Text is Unicode NFKD folded, case-folded, punctuation-normalized, whitespace-collapsed, and tokenized. Identifier normalization removes punctuation and spacing but performs no fuzzy repair.

Name comparison evaluates every supplied primary name and alias using:

| Primitive | Use |
|---|---|
| IDF token-set overlap | Token inclusion and reordering |
| Jaro-Winkler | Conservative sequence similarity |
| Soundex | Limited phonetic support for the final token |
| Curated equivalence groups | Known romanization variants such as Mohammed/Muhammad and Zhang/Chang |

Canonical token-set equality makes name-order swaps and curated transliterations non-differences. The raw name score is `1.0` for these equivalences. The decision score is capped at `0.78` for other names and `0.45` when a common given-name and common family-name combination is present. Names never open a path to `SAME`; the caps communicate base-rate limits only.

## Identifier taxonomy and weights

Weights express comparative discriminating power and drive only documented contradiction rules. They are not probabilities.

| Field | Strength | Match/contradiction weight |
|---|---|---:|
| Passport | Strong | 1.00 |
| National ID | Strong | 1.00 |
| Tax ID | Strong | 0.98 |
| Full DOB | Moderate | 0.70 |
| Partial DOB with agreeing known components | Moderate support | 0.30 |
| Place of birth | Moderate | 0.45 |
| Address | Moderate | 0.35 |
| Nationality | Weak | 0.15 |

Text-field match thresholds are `0.90` Jaro-Winkler for place of birth, `0.92` for address, and `0.92` for nationality. The decisive unopposed moderate-contradiction threshold is `1.00`; name context must have a raw score of at least `0.50`. Nationality is never part of the decisive moderate-contradiction sum.

## Field comparison rules

Strong IDs match only when normalized values are exact. Full non-matching values of six or more characters contradict. Short/partial values and adjacent-character transpositions become flags. DOB accepts `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, `/` separators, and unknown components. Agreeing known components support but do not prove identity. Adjacent digit swaps and a one-year/same-month-day variant are flagged rather than contradicted.

## Disposition rules, in order

1. A shared strong identifier and no strong conflict → `SAME`.
2. A shared strong identifier plus any strong conflict → `REVIEW`.
3. A clean strong-identifier conflict and no strong match → `DIFFERENT`.
4. Moderate contradictions totaling at least `1.00`, no moderate corroboration, and raw name context at least `0.50` → `DIFFERENT`.
5. Everything else → `REVIEW`.

The implementation asserts after decisioning that every `SAME` output carries `shared_strong_identifier=true`. This makes name-only auto-merge structurally unreachable in the production resolver.

## Validation design

The seeded generator labels pairs before scoring and plants these true-match categories: transliteration variants; name-order swaps; distinct romanizations sharing a passport; partial-DOB-only records; DOB digit transpositions; and address drift with a shared national ID. It also plants distinct people with the same common name and no identifier, clean strong-ID conflicts, exact-name moderate contradictions, passport conflicts, and sparse unrelated records.

The harness runs unit tests, generates each trial independently from its seed, scores every labelled pair, emits trial and aggregate metrics, sweeps the moderate threshold, and applies two non-negotiable gates:

- False-negative gate: no TRUE-SAME pair may be declared `DIFFERENT`.
- False-merge gate: no distinct pair may be declared `SAME`; no name-only distinct pair may be merged; and no `SAME` output may lack a shared strong identifier.

The exact one-sided 95% Clopper-Pearson upper bound is calculated by binomial-CDF inversion (with the closed form for zero events). Every zero-event false-negative statement identifies the numerator, sample size, and the fact that the bound is a sample-size property.

## Limitations and monitoring

The variant table is intentionally small, Soundex is English-centric, addresses lack jurisdiction-specific parsing, and exact identifier matches can still reflect upstream data contamination or identifier reuse. The synthetic corpus demonstrates invariants; it does not estimate production prevalence or demographic performance. Before deployment, validate on legally obtained, representative records; stratify by script, jurisdiction, data source, and missingness; monitor review volumes and overrides; and rerun both gates after every code, threshold, normalization, or reference-data change.
