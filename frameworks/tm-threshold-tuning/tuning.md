# Tuning — configuring the tuner

This framework tunes monitoring rules, but it has its own small set of configuration
choices in `engine.Config`. The most consequential is the recall floor — a policy
choice, not a model output.

> **In plain terms:** The one dial that matters here is how much suspicious activity
> you require a rule to catch (the recall floor). Set it from your risk appetite and
> your regulators' expectations. The engine then finds the leanest threshold that
> still meets it. Don't let the engine pick that floor for you — own it.

## The dials

| Constant | Default | Effect |
|---|---|---|
| `recall_floor` | 0.95 | The required detection of suspicious activity. Higher = more conservative (lower thresholds, more alerts); lower = leaner but riskier. **A policy choice — set and own it.** |
| `keep_tolerance` | 0.05 | How far the recommended threshold must move from current before the action is RAISE rather than KEEP. |
| `n_candidates` | 40 | Sweep resolution. More candidates = finer threshold recommendations, slower. |

## The label dependency

ATL/BTL testing is only as good as the "suspicious" label. In production that label
is a historical analyst/SAR disposition, which carries its own error and survivorship
bias (you only know an alert was productive if it was *worked*). Real below-the-line
testing samples activity below the threshold and has it **manually reviewed** to
estimate the true suspicious share — the engine consumes those labels. Budget for
that manual BTL sampling; it is the evidence an examiner actually weighs.

## Procedure

1. For each rule, assemble a labelled population: the metric values and a suspicious
   label, including a manually-reviewed sample from below the current threshold (the
   BTL test).
2. Set `recall_floor` from policy. Run the engine.
3. Read the recommendations: LOWER any leaking rule first (these are the regulatory
   findings); RAISE the over-alerting rules to recover analyst capacity.
4. Treat each recommendation as a model-change proposal — approve, document, and
   re-test after the change lands.
5. Re-run on a fresh period regularly (ongoing monitoring); thresholds drift as
   customer behaviour and typologies change.

## What not to do

- Do not raise a threshold the engine did not recommend raising — that is how BTL
  leakage is introduced.
- Do not set `recall_floor` to hit a volume target; set it from risk appetite, then
  accept the volume it implies.
- Do not tune on alert-disposition labels alone without a below-the-line manual
  sample — you would be optimizing only the alerts you already see, never the risk
  you are missing.
