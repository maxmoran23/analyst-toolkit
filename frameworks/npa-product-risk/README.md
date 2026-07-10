# NPA Product-Risk Framework

A runnable, deterministic engine that assesses a new-product / new-activity (NPA)
proposal before launch: a 0-100 composite over nine documented risk factors, a
LOW / MEDIUM / HIGH tier with mandatory raise-only floors, and a routing map that
names the approval route, the mandatory pre-launch conditions, and the
post-launch review interval — validated for discrimination, monotonicity, floor
safety, and prohibited-list routing.

> **In plain terms:** Before a bank launches a new product, an approval committee
> needs a consistent picture of its risk — who it serves, where, settled in what,
> how new it is to the firm, and how attractive it would be to a money launderer —
> instead of a stack of ad-hoc memos. This engine produces that picture from the
> proposal's attributes, and guarantees three things a regulator asks about: a
> riskier proposal never scores lower than a safer one, a proposal with a serious
> hard attribute (a sanctions-exposed market, digital-asset custody the firm has
> never operated) can never be tiered LOW, and anything on the prohibited list is
> referred straight to the policy owner — it cannot be scored around. It routes
> the proposal; the committee still decides whether to launch.

---

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | The new-product approval committee and the financial-crime advisors who brief it. |
| **The question it answers** | Before we launch this product, how attractive is it to a launderer, and what must be in place first? |
| **What it is** | A small, transparent, runnable scoring engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never approves anything. It scores, routes, and names the mandatory pre-launch conditions; the committee decides whether to launch. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/npa-product-risk
python3 run_validation.py --seed 42 --products 50000
```

Pure Python standard library: nothing to install, no network access, well under a second. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page

The claim here is structural: **no proposal carrying a serious hard attribute was tiered LOW**, a prohibited activity is always referred rather than scored around, and worsening any factor never lowers the score. The run fails if any of the three breaks.

<!-- /STANDALONE-BRIEF -->

## What it produces

Per proposal, an `Assessment`: a 0-100 `score`, a `tier` (LOW / MEDIUM / HIGH), a
named `routing` (STANDARD_APPROVAL / ENHANCED_REVIEW / FULL_COMMITTEE /
REFER_PROHIBITED), the per-factor sub-scores, the floors applied, any prohibited
attributes, the named mandatory pre-launch conditions, the post-launch review
interval, and a reason naming the top risk drivers.

## Validation result (seed 42, 50,000 proposals — see [`evidence/`](evidence/))

| Property | Result |
|---|---|
| Floor safety (floor-triggered proposals tiered LOW) | **0 — none** (the under-tiering gate) |
| Prohibited routing (prohibited proposals routed past REFER_PROHIBITED) | **0 of 3,046** — never scored around |
| Discrimination (mean score by designed stratum) | **PASS** — low 17.3 < medium 39.8 < high 68.6 |
| Monotonicity (worsening any factor never lowers the score) | **PASS** — 300 random vectors × 9 factors |
| Tier distribution | LOW 49.2% · MEDIUM 25.5% · HIGH 25.2% (seed-stable) |
| Routing distribution | STANDARD_APPROVAL 49.2% · ENHANCED_REVIEW 25.5% · FULL_COMMITTEE 19.2% · REFER_PROHIBITED 6.1% |
| Scale | 200,000 proposals in ~3s |

Per designed stratum: designed_low → 100% LOW; designed_medium → LOW/MEDIUM mix
(the all-middling band-edge plants); designed_high (strong soft factors, no hard
attribute) → ~96% HIGH / 4% MEDIUM; hard_high (a benign profile with one buried
hard attribute — the composite alone would tier most of them LOW) → 0% LOW,
floored to MEDIUM (segment + geography combination) or HIGH; prohibited → 100%
REFER_PROHIBITED.

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --products 50000
python3 run_validation.py          --seed 42 --products 50000
```

`run_validation.py` regenerates the population in-memory, assesses it, writes the
evidence pack, and **exits non-zero if any floor-triggered proposal is tiered
LOW, or any prohibited proposal is routed past REFER_PROHIBITED, or
discrimination ordering fails, or monotonicity fails**. Optional: `--trials 6`,
`--products 200000`.

Ad-hoc: `python3 scorer.py` assesses four example proposals.

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — factors, weights, bands, floors, prohibited list, routing map, governance. |
| [`scorer.py`](scorer.py) | The deterministic assessment engine (pure stdlib + `../_lib/`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded proposals in designed-risk strata, with adversarial buried-attribute plants. |
| [`run_validation.py`](run_validation.py) | Discrimination / monotonicity / floor-safety / prohibited-routing harness + evidence. |
| [`tuning.md`](tuning.md) | Recalibration for a real environment. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Copilot Studio / Power Platform mapping. |
| [`evidence/`](evidence/) | Committed real-run output. |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. The factor weights, jurisdiction buckets, reference tables, and band
thresholds are illustrative — calibrate them against your own product-approval
methodology and history (the jurisdiction buckets must track current sanctions
programs and FATF lists), and carry your institution's full prohibited-product
register. The engine tiers and routes; the launch decision, condition waivers,
and any override are documented human actions. All data synthetic; nothing here
assesses a real product or institution.
