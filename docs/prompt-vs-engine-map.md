# What am I looking at? — prompts vs. engines, and the names that rhyme

This repository holds more than one **kind** of thing, and a few of them cover the
same subject from different angles. A reader browsing the file tree can reasonably
wonder why there is both a `customer-file-review` and a `customer-risk-rating`, or a
`sanctions-watchlist-screen` and a `sanctions-name-screening`. This page answers that
once, so no filename has to.

> **In plain terms:** same subject, different tool. A **prompt** works *one case* and
> explains its reasoning. An **engine** triages *tens of thousands* of cases and ships
> proof of how accurately it does it. Neither replaces the other; they sit at opposite
> ends of the same workflow.

## The one rule that resolves most of it

Every path in this repo belongs to exactly one artifact class. Tell them apart by the
top-level folder:

| You are in… | Artifact class | What it is | How you use it |
|---|---|---|---|
| [`prompts/`](../prompts/) | **Paste-prompt** | A page of instructions that turns any AI assistant into a specific analyst | Copy the block, fill the `{{PLACEHOLDERS}}`, paste. Works **one case**, shows its reasoning. |
| [`standalone/`](../standalone/) | **Paste-prompt (self-contained)** | The same, but the whole file *is* the prompt and it embeds the multi-format renderer | Paste one file. No companion needed. |
| [`frameworks/`](../frameworks/) | **Runnable engine** | A pure-Python scoring/triage engine with a false-negative gate and reproducible evidence | Run it offline from a seed. Works **at volume**, publishes accuracy. |
| [`reference/`](../reference/) | **Cheat-sheet** | Domain knowledge — typologies, entity types, source libraries | Read it. Nothing to run or paste. |
| [`quant/`](../quant/), [`quant-jvm/`](../quant-jvm/) | **Library** | Dependency-free financial math, Python and its Kotlin parity port | Import it into your own code. |

If you remember one thing: **a `prompts/` name and a `frameworks/` name that sound alike
are cousins, not duplicates — one dispositions a single item with a written rationale,
the other dispositions a queue and proves its hit rate.**

## The cousin pairs

These are the names that rhyme across the prompt and engine classes. Each row is the
same domain problem at two scales.

| Domain | Prompt — *one case, with reasoning* | Engine — *volume, with evidence* |
|---|---|---|
| Sanctions / watchlist | [`compliance/sanctions-watchlist-screen`](../prompts/compliance/sanctions-watchlist-screen.md) | [`sanctions-name-screening`](../frameworks/sanctions-name-screening/) |
| PEP | [`compliance/pep-screening-disposition`](../prompts/compliance/pep-screening-disposition.md) | [`pep-screening`](../frameworks/pep-screening/) |
| Customer risk | [`compliance/customer-file-review`](../prompts/compliance/customer-file-review.md) — *review one file's defensibility* | [`customer-risk-rating`](../frameworks/customer-risk-rating/) — *rate a whole book* |
| Transaction monitoring | [`compliance/alert-triage`](../prompts/compliance/alert-triage.md) — *work one alert* | [`transaction-monitoring`](../frameworks/transaction-monitoring/) — *score the queue* · [`tm-threshold-tuning`](../frameworks/tm-threshold-tuning/) — *tune the rules* |
| Case QA | [`compliance/case-qa-review`](../prompts/compliance/case-qa-review.md) · [`controls/qa-review-scorecard`](../prompts/controls/qa-review-scorecard.md) | [`investigations-case-qa`](../frameworks/investigations-case-qa/) — *file-level gate* · [`qa-sampling`](../frameworks/qa-sampling/) — *sample plan* |
| Data quality | [`controls/data-quality-review`](../prompts/controls/data-quality-review.md) · [`data-governance/dq-rule-authoring`](../prompts/data-governance/dq-rule-authoring.md) | [`data-quality-rules`](../frameworks/data-quality-rules/) — *inspect a feed* |
| On-chain | [`blockchain/onchain-sanctions-monitor`](../prompts/blockchain/onchain-sanctions-monitor.md) | [`onchain-kyt-address-risk`](../frameworks/onchain-kyt-address-risk/) · [`onchain-osint-evidence`](../frameworks/onchain-osint-evidence/) |
| New-product approval | [`npa/npa-risk-assessment`](../prompts/npa/npa-risk-assessment.md) | [`npa-product-risk`](../frameworks/npa-product-risk/) |
| Jurisdiction risk | [`regulatory/geopolitical-risk-monitor`](../prompts/regulatory/geopolitical-risk-monitor.md) | [`jurisdiction-risk`](../frameworks/jurisdiction-risk/) |
| Fraud | [`fraud/`](../prompts/fraud/) *(five case-level prompts)* | [`fraud-detection`](../frameworks/fraud-detection/) |
| Beneficial ownership | [`compliance/ubo-beneficial-ownership`](../prompts/compliance/ubo-beneficial-ownership.md) — *unwind one chain* | `beneficial-ownership-resolution` *(engine in progress — resolves at volume with a false-negative gate)* |

## The mirror pairs (not cousins — the same prompt, twice)

Five prompts exist under **both** [`prompts/`](../prompts/) and [`standalone/`](../standalone/)
with the same filename. These are not two different things; they are the same method
offered in two workflows — the catalog version (a prompt block among how-to and tuning
notes) and the standalone version (the whole file is the prompt, renderer embedded). Same
name is deliberate:

`entity-risk-assessment` · `control-matrix-builder` · `committee-reporting-pack` ·
`breaking-news-scan` · `alert-triage`

## How this page stays true

This is not just prose. [`_tooling/validate_naming.py`](../_tooling/validate_naming.py)
reads the registry below on every CI run and fails the build if:

1. a new filename collides across artifact classes without being a structural file, a
   declared mirror, or a registered exception here, or
2. any cousin pair registered here stops resolving on disk (a file was renamed or removed).

So the map cannot advertise a pairing that no longer exists, and a future contributor
cannot quietly introduce a confusingly reused name.

<!-- NAMING-REGISTRY:cousins — machine-read by _tooling/validate_naming.py; format: <prompt path .md> <-> <framework dir> -->
```registry
prompts/compliance/sanctions-watchlist-screen.md <-> frameworks/sanctions-name-screening
prompts/compliance/pep-screening-disposition.md <-> frameworks/pep-screening
prompts/compliance/customer-file-review.md <-> frameworks/customer-risk-rating
prompts/compliance/alert-triage.md <-> frameworks/transaction-monitoring
prompts/compliance/case-qa-review.md <-> frameworks/investigations-case-qa
prompts/controls/qa-review-scorecard.md <-> frameworks/qa-sampling
prompts/controls/data-quality-review.md <-> frameworks/data-quality-rules
prompts/blockchain/onchain-sanctions-monitor.md <-> frameworks/onchain-kyt-address-risk
prompts/npa/npa-risk-assessment.md <-> frameworks/npa-product-risk
prompts/regulatory/geopolitical-risk-monitor.md <-> frameworks/jurisdiction-risk
```
<!-- /NAMING-REGISTRY:cousins -->
