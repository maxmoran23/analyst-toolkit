# Tuning — calibrating the knowledge base

The defaults prioritize the zero-false-merge guarantee over dedup completeness — the
right priority for a watchlist. Calibrate against your own data before reliance.

> **In plain terms:** The safe default is to combine records only when they share a
> unique identifier, and to flag everything else for a person. If you want more
> automatic merging you can loosen that, but every loosening trades away the guarantee
> that you never merge two different parties — so loosen carefully, with a labelled
> sample.

## The dials (`_lib/knowledge_base/dedup.Config`)

| Constant | Default | Effect |
|---|---|---|
| (auto-merge basis) | shared strong identifier only | The conservative default. Auto-merge never fires on name alone — name matches become review candidates. |
| `name_merge_floor` | 0.85 | Min distinctive name score for a pair to be surfaced as a review candidate. |
| `char_floor` | 0.94 | Min character similarity (Jaro-Winkler) for a review candidate — guards against coarse Soundex coincidences. |
| `generic_max_share` | 0.005 | Genericness threshold for token weighting (shared with the matcher). |
| `feedback.min_count` | 25 | False-positive count before a token is considered for the learned-generic set. |

## Production steps

1. **Configure the source parsers.** OFAC SDN ships a working parser; add EU / UN / UK
   parsers against their current published schemas, each yielding `normalize_record(...)`
   dicts. Validate each parser against a freshly downloaded file — list layouts change.
2. **Schedule ingest + delta.** Run on the cadence the lists update (often daily). Each
   run produces a snapshot; `delta.diff` against the prior snapshot is your change feed
   to monitoring and to a governance log.
3. **Decide the merge posture.** The default (strong-id-only auto-merge) is recommended.
   If you choose to auto-merge some name-only matches, calibrate `char_floor` against a
   labelled sample and accept that the zero-false-merge guarantee weakens accordingly —
   measure the false-merge rate explicitly.
4. **Route review candidates** to analysts; their dispositions feed the feedback loop.
5. **Re-run the validation gate** on your calibrated configuration; a false merge must
   remain impossible.

## What not to do

- Do not auto-merge on name similarity to raise the dedup rate — a duplicate entry is
  harmless; a merged-away designation is a screening failure.
- Do not promote DOB (or any non-unique field) to a strong identifier — many parties
  share a birthdate.
- Do not let the feedback loop genericize a token without the protection gate — that is
  the one path by which it could lower recall.
- Do not ship a source parser unvalidated against the list's current published schema.
