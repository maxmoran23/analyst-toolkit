# Tuning — calibrating the evidence engine

The provenance, reconciliation, and determinism disciplines are NOT tunable — they
are the point of the artifact. The dials below govern only the structural
observations and presentation, and the live-capture envelope. Recalibrate the
observation thresholds against your own dispositioned cases before reliance.

> **In plain terms:** How the tool stamps, adds up, and reproduces evidence is
> fixed — loosening any of that would defeat the purpose. What you can tune is
> when it raises its hand: how many spam-dust transfers, or how many repeat
> transactions with one counterparty, count as "worth mentioning to an analyst."
> Set those from cases your team has already worked, and write down why.

## The dials (`engine.Config`)

| Constant | Default | Effect of raising it |
|---|---|---|
| `dust_spam_min_count` | 10 | Fewer OBS_DUST_SPAM flags (more spam tolerated before mention). |
| `dust_token_exp` | 3 (≤ 0.001 units) | Larger token amounts counted as dust — more transfers classed as spam. |
| `dust_btc_sats_max` | 1,000 sats | Larger BTC outputs counted as dust. |
| `self_transfer_min_count` | 1 | Self-transfers unmentioned until the count is reached. |
| `high_freq_min_tx` | 25 | Fewer OBS_HIGH_FREQ_SAME_COUNTERPARTY flags (stronger concentration required). |
| `annex_top_counterparties` | 15 | More rollup rows in the annex (all rows are always in the CSV). |

Live-capture envelope: `max_pages` and `page_size` on the collectors bound how much
history a live run pulls; a partial window is a stated property of the pack, not an
error.

## Procedure

1. Assemble a labelled sample of addresses your investigators have already worked,
   with their notes on which structural patterns mattered.
2. Run the engine over captures for those addresses and compare flagged
   observations against the notes: thresholds too low bury the annex in
   non-findings; too high and patterns your team relies on go unmentioned.
3. Set the dust definitions from observed spam on the chains you actually work —
   dust conventions differ by chain and era.
4. Re-run `run_validation.py` after any change; the provenance / reconciliation /
   determinism gates must still pass (they are threshold-independent, so a failure
   indicates a code change, not a calibration choice).
5. Record the change, old/new values, the labelled-sample result, and the
   rationale — observation thresholds are model parameters in the SR 11-7 sense.

## What not to do

- Do not add an observation rule that asserts identity, ownership, or intent — the
  no-attribution boundary is the artifact's credibility. New rules must be
  structural, named, threshold-stated, and evidence-cited.
- Do not relax the dedupe rule beyond identical-record pagination overlap; any
  fuzzier "duplicate" definition risks silently erasing distinct transactions.
- Do not move amounts through floats anywhere in the pipeline — one rounding
  artifact breaks exact reconciliation and the evidence claim with it.
- Do not point live mode at an explorer whose usage terms you have not read, and
  do not raise the page envelope to bulk-scrape — this is a per-case evidence
  tool, not a crawler.
- Do not present an annex from a partial capture as a complete history — the
  capture list in section 1 of the annex defines exactly what was evidenced.
