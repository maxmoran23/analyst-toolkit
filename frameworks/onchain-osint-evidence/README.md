# On-Chain OSINT Evidence Framework

A runnable, deterministic engine that turns public block-explorer data into an
investigation-grade, provenance-stamped evidence pack — every fact carries its
source URI, retrieval timestamp, content hash, and origin locator; every total
reconciles exactly to the source captures; and the rendered annex is byte-identical
on every re-run over the same captures.

> **In plain terms:** When an investigator works an address on a public block
> explorer today, the evidence trail is screenshots and copied hashes — and the
> proof of where each number came from, when it was pulled, and that nobody altered
> it afterwards is usually lost. This tool does that workflow defensibly: it takes
> the explorer's own responses, turns each transaction into a fact stamped with its
> source link, retrieval time, and a fingerprint of the exact bytes it came from,
> adds up the flows and counterparties without dropping or double-counting anything
> (even across paginated pages that repeat records), flags a few tell-tale patterns
> like dust spam by name — and writes the evidence annex an investigations team at
> Harborview Financial Group could hand to a reviewer. It never says who owns an
> address or whether anything is wrong; a person does that.

---

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Crypto investigators and anyone who must hand blockchain evidence to a reviewer or a court. |
| **The question it answers** | Where exactly did each fact in this evidence pack come from, when was it pulled, and can anyone re-check it? |
| **What it is** | A small, transparent, runnable evidence-capture engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never says who owns an address or whether anything is wrong. It records observations with provenance; attribution is a human act. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/onchain-osint-evidence
python3 run_validation.py --seed 42 --addresses 400 --transactions 50000
```

Pure Python standard library: nothing to install, no network access, about 3 seconds. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page

The claim here is evidentiary, not statistical: **every captured fact carries its source, retrieval time, and a hash of the exact bytes**; the totals reconcile to the captures with nothing dropped or double-counted; and the same captures re-render byte-for-byte identically months later.

<!-- /STANDALONE-BRIEF -->

## What it produces

Per address, an evidence pack: a markdown **annex** (source captures, address
summary, directional flow, counterparty rollup, named structural observations,
reconciliation statement), a **facts CSV** (every fact + full provenance), a
**counterparty CSV**, and an **evidence-manifest JSON** (fact census, artifact
digests, reconciliation totals — the only place the run timestamp appears).

## Validation result (seed 42, 400 addresses, 54,915 transaction records — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| Provenance completeness (all 5 fields on every fact) | **100.0% of 61,126 facts** — enforced at floor 1.0 |
| Reconciliation vs fixture-source ground truth | **exact — 0 dropped, 0 double-counted** (400/400 sets) |
| Pagination-overlap dedupe | **232 planted boundary duplicates, 232 removed** — exactly once |
| Determinism | **byte-identical annex + CSVs across repeat runs** (single digest) |
| Planted structural observations detected | **245 / 245 — 0 missed, 0 spurious** |
| BTC parsed totals tie to the explorer's own summary | **exact** |
| Stability | all gates hold across 6 additional seeds (58,912–61,662 facts) |
| Scale | 1,200 addresses / 181,461 facts in ~10s |

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --addresses 400 --transactions 50000
python3 run_validation.py          --seed 42 --addresses 400 --transactions 50000
```

`run_validation.py` writes the seeded synthetic explorer fixtures to disk, runs the
engine over those files (offline — CI never touches the network), writes the
evidence pack, and **exits non-zero if any fact lacks a provenance field, any total
fails to reconcile exactly, output is not byte-identical across repeat runs, an
observation is missed or spurious, or the live collectors fail to degrade offline**.
Optional: `--trials 6`, `--addresses 1200 --transactions 150000`.

Ad-hoc, against the committed sample fixtures:

```bash
python3 engine.py fixtures/sample/evm-sample-01                # print the annex
python3 engine.py fixtures/sample/btc-sample-01 --out /tmp/pk  # write the full pack
```

Live mode is optional and never exercised in CI — you supply the explorer base URL
(there is no default endpoint), and any failure degrades to `None` rather than
raising:

```python
from engine import collect_live_evm, build_pack
fset = collect_live_evm("https://<your-explorer-host>", "0x...")  # None if offline/failed
pack = build_pack(fset) if fset else None
```

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — provenance model, normalization rules, observation rules, reconciliation discipline, governance. |
| [`engine.py`](engine.py) | The deterministic collector/normalizer/renderer (fixture mode default; optional live mode). |
| [`../_lib/provenance.py`](../_lib/provenance.py) | The provenance layer: `EvidenceFact`, sha256 stamping, completeness checker, evidence-manifest builder. |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded explorer-shaped fixtures with ground truth + adversarial plants; `--write-sample` refreshes `fixtures/sample/`. |
| [`fixtures/sample/`](fixtures/sample/) | Small committed fixture sets (EVM with every plant, clean EVM, BTC) used by the walkthrough and re-verified on every validation run. |
| [`run_validation.py`](run_validation.py) | Validation harness + evidence; the provenance / reconciliation / determinism gates. |
| [`tuning.md`](tuning.md) · [`DEPLOYMENT.md`](DEPLOYMENT.md) · [`evidence/`](evidence/) | Recalibration · Copilot mapping · committed run output (incl. a rendered sample annex). |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. It normalizes and evidences public explorer data; it does not attribute
addresses to entities, score risk, or replace a chain-analytics vendor — it
complements them by making the public-source layer of an investigation provable.
Observation thresholds are illustrative; recalibrate against your own labelled
cases (`tuning.md`). All fixtures are synthetic and every address, transaction,
token, and explorer host is fictional; nothing here queries or represents any real
party. The scoring contract in `METHODOLOGY.md` is what travels.
