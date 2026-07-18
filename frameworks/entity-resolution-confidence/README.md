# Entity Resolution Confidence

A conservative, standard-library-only Python 3.12 engine for deciding whether a query identity and each candidate record are the `SAME` person, `DIFFERENT` people, or require `REVIEW`.

The engine is designed for symmetric-cost identity decisions: a false clearance and a false merge can both cause material harm. It therefore makes uncertainty explicit. An exact name—even a rare one—is not an identifier.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Sanctions and PEP hit adjudicators, KYC identity-resolution and customer-dedup teams. |
| **The question it answers** | Are these two identity records the same person, different people, or genuinely indeterminate on the evidence? |
| **What it is** | A small, transparent, runnable identity-resolution engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never clears a hit because two names are spelled differently, and it never merges two records on a name alone — auto-SAME requires a shared strong identifier. Indeterminate routes to review, not to a clear. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/entity-resolution-confidence
python3 run_validation.py --seed 42 --same 160 --different 240 --name-only 80 --trials 6
```

Pure Python standard library: nothing to install, no network access, a few seconds. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page



<!-- /STANDALONE-BRIEF -->

## Safety invariants

- `SAME` requires an exact normalized match on a strong identifier: passport, national ID, or tax ID.
- Name-only evidence always returns `REVIEW`; common-name exact matches receive an additional confidence cap.
- Transliteration variants and name-order swaps are non-differences.
- Partial DOBs, short identifiers, and adjacent-character transpositions are data-quality flags, not decisive contradictions.
- Conflicting strong evidence returns `REVIEW` when one strong identifier matches and another conflicts.
- `run_validation.py` exits non-zero if any labelled true match is declared `DIFFERENT` or any distinct/name-only pair is auto-merged.

## Quick start

```bash
python3 scorer.py --input reference-data/sample-input.json --output data/sample-output.json
python3 run_validation.py --seed 42 --same 160 --different 240 --name-only 80 --trials 6
```

No dependency installation or network access is required.

## Input and output

The input is a JSON object containing one or more query records and candidate arrays. Each identity must contain `name`, `names`, or `aliases`; all other fields are optional. See `reference-data/README.md` and `reference-data/sample-input.json`.

Every candidate output contains:

- `disposition`: `SAME`, `DIFFERENT`, or `REVIEW`
- `reason`: the governing rule
- `shared_strong_identifier`: the auditable SAME gate
- `name`: calibrated name comparison, equivalence type, and common-name flag
- `evidence`: field-level strength, result, weight, and detail
- `scores` and `quality_flags`

## Files

- `_lib/identity.py`: core comparison and disposition engine
- `scorer.py`: production CLI
- `generate_synthetic_data.py`: seeded labelled corpus and sample-pack generator
- `run_validation.py`: unit tests, stability trials, evidence emission, and fail-closed gates
- `negative_control_scorer.py`: deliberately unsafe test double proving the gates are live
- `METHODOLOGY.md`: full rules, thresholds, weights, limitations, and SR 11-7-style model-risk framing
- `DEPLOYMENT.md`: offline deployment and operational controls
- `evidence/`: harness-emitted evidence

## Scope

This is a deterministic candidate-disposition aid, not a universal identity oracle. It does not retrieve records, infer protected traits, validate document authenticity, or replace analyst review. Production deployment requires jurisdiction-specific privacy, retention, access, and adverse-action controls.
