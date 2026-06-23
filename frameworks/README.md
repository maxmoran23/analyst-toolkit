# frameworks/ — runnable scoring engines with validation evidence

A different artifact class from the rest of this repository. Where [`prompts/`](../prompts/)
and [`standalone/`](../standalone/) are **paste payloads** — text you drop into an
AI assistant — `frameworks/` are **things you run**: small, deterministic,
pure-standard-library reference engines for the financial-crime problems that are
genuinely a *scoring / triage / matching* problem with a measurable error rate.
Each ships with a seeded synthetic-data generator and a validation harness that
produces **real, reproducible evidence** that the engine performs as specified.

> **In plain terms:** The prompts elsewhere in this repo tell an AI assistant how to
> *think about* a task. The frameworks here are working calculators for the tasks
> where "did it get the answer right?" is a measurable question — like sorting
> 50,000 sanctions alerts. Each one comes with proof: a script anyone can re-run
> that scores tens of thousands of made-up-but-realistic cases and reports exactly
> how accurate it was, including that it never wrongly cleared a real hit.

## Why this is a separate pillar

These are code, not paste payloads, so the repository's two-file rule (which keeps
every pasted prompt self-contained) does not apply to them — exactly as it does not
apply to [`quant/`](../quant/). A framework is multi-file by design: a methodology
spec, an engine, a data generator, a validation harness, and an evidence pack.
Pure Python standard library only (no numpy, no pandas, no network), so a framework
runs unchanged on a locked-down machine.

## The package standard

Every `frameworks/<domain>/` package contains the same fixed set, so once you have
read one you can navigate any other:

| File | Role |
|---|---|
| `README.md` | Two-audience front door: plain-terms summary + technical overview + run commands + headline result. |
| `METHODOLOGY.md` | The regulator-facing spec — every input, weight, threshold, and named decision rule, in firing order, with rationale, plus the SR 11-7 framing. The engine is its executable form. |
| `scorer.py` (or engine) | The deterministic reference implementation. Pure stdlib + `_lib/`. Named-reason dispositions; auto-clear only on a provable cause; never auto-block or auto-file. |
| `generate_synthetic_data.py` | Seeded, labelled, scalable population. Every negative carries a category; the design plants adversarial cases. |
| `run_validation.py` | Runs the engine over the population, computes the metrics, writes the evidence pack, and **exits non-zero if a false-negative-safety invariant is violated**. |
| `tuning.md` | How to recalibrate the operating point for a real environment. |
| `DEPLOYMENT.md` | How the engine maps onto a Microsoft Copilot Studio / Power Platform deployment. |
| `evidence/` | The committed real-run output: validation report, metrics JSON, threshold sweep, confusion matrix, run manifest. |
| `data/` | `.gitignore`d — regenerated from seed, never committed. Credibility is reproduction-from-seed, not data-in-repo. |

Shared across the pillar:

| File | Role |
|---|---|
| [`GOVERNANCE.md`](GOVERNANCE.md) | The SR 11-7 / model-risk framing every framework instantiates. |
| [`DEPLOYMENT-PATTERN.md`](DEPLOYMENT-PATTERN.md) | The reusable Copilot Studio mapping. |
| [`RIGOR-CONTRACT.md`](RIGOR-CONTRACT.md) | What `run_validation.py` must enforce and how it wires into CI. |
| [`_lib/`](_lib/) | Shared pure-stdlib primitives — name normalization + token rarity, matching (Jaro-Winkler / Soundex / IDF-weighted token-set), evaluation metrics. |

## Frameworks

| Framework | Problem | Status |
|---|---|---|
| [`sanctions-name-screening/`](sanctions-name-screening/) | Disposition sanctions-screening alerts (the ~50k/month false-positive backlog) | **Built & validated** — recall 1.0 (0 FN), 92% FP-reduction, evidence committed |
| [`transaction-monitoring/`](transaction-monitoring/) | Score & triage TM alerts (structuring, funnel, pass-through, velocity, geography) against the customer baseline | **Built & validated** — recall 1.0 (0 FN), 85% FP-reduction, evidence committed |
| [`customer-risk-rating/`](customer-risk-rating/) | Weighted customer risk score + LOW/MEDIUM/HIGH tiering with mandatory floors | **Built & validated** — 0 hard-risk customers rated LOW, monotonic, discriminating, evidence committed |
| [`adverse-media-screening/`](adverse-media-screening/) | Disposition negative-news hits on two axes (right party? materially adverse?) | **Built & validated** — recall 1.0 (0 FN), 80% FP-reduction, evidence committed |
| _onchain-kyt-address-risk_ | Blockchain address risk scoring | planned |

## Standing caveat

Each framework is a transparent **reference implementation** chosen for
auditability, not a production control. A real deployment swaps internals and
recalibrates against its own labelled data; the scoring *contract* in each
`METHODOLOGY.md` is what travels. All data is synthetic; entities are fictional
(the recurring institution is **Harborview Financial Group**). Nothing here
screens or assesses any real party.
