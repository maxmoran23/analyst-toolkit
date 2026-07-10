# Start with your team — everything that applies to you, in one page

**Fifteen hub pages, one per team across a financial-crime organization.** Find your
function below, open its hub, and it tells you — in plain English — exactly which tools
apply to your work, what they do, what they refuse to do, and where to start. You do not
need to know how this repository is laid out, and you do not need to read any other part
of it.

The coverage spans the whole organization: the front-line and investigative teams, the
assurance and governance functions around them, and the data and product teams they all
depend on. Elsewhere the material is filed by *artifact type* — prompts in one place,
runnable engines in another. These hubs are a second view over the same content, filed by
**who does the work**.

> **In plain terms:** find your team below, open its hub, and it points you to exactly
> the prompts, engines, references, and templates you'd actually use — no need to know
> how the repo is laid out.

A hub is pure navigation and orientation: it contains no prompt text and no code, only
curated links into the by-type folders plus a plain-English walkthrough. The underlying
files stay the single source of truth.

## Team hubs

| Team | Accountable for | Maturity |
|------|------------------|----------|
| [Sanctions & Screening](sanctions-screening.md) | Screening customers/payments against sanctions, PEP & watchlist data; alert disposition | Mature — 3 engines + prompts |
| [Transaction Monitoring](transaction-monitoring.md) | Detecting & dispositioning suspicious activity; keeping rules calibrated | Mature — 2 engines + prompts |
| [Crypto / Blockchain Intelligence](crypto-blockchain.md) | Address, flow, token, and protocol risk; provenance-stamped on-chain evidence | Mature — 2 engines + prompts |
| [KYC / CDD / Onboarding](kyc-cdd-onboarding.md) | Customer risk rating; entity & counterparty assessment | Mature — engine + prompts |
| [Adverse-Media Screening](adverse-media-screening.md) | Is the negative-news hit the right party, and is it materially adverse? | Mature — engine |
| [Investigations & SAR](investigations-sar.md) | Case investigation, file/no-file decisioning, narratives, and second-line case QA | Mature — QA engine + 6 prompts |
| [Financial-Crime Risk Assessment](fincrime-risk-assessment.md) | Enterprise risk register, controls, residual exposure, EWRA roll-up | Mature — EWRA + register + control matrix |
| [Controls, Testing & QA](controls-testing-qa.md) | Control design, statistical sampling, independent testing, issue closure | Mature — 2 engines + full controls suite |
| [Model Risk & Governance](model-risk-governance.md) | Governing & validating models / AI tools | Mature — reviews, validation workpaper, 14 worked evidence packs |
| [Regulatory Affairs & Exam](regulatory-affairs-exam.md) | Regulatory tracking, obligations, gaps, exam response | Mature — full regulatory suite |
| [Fraud](fraud.md) | Scams, payment fraud, account misuse, mule detection | Covered — 5 prompts |
| [Trade & Communications Surveillance](trade-comms-surveillance.md) | Market abuse in trading and misconduct in communications | Covered — 3 prompts |
| [ABC, Third-Party & Correspondent Banking](abc-third-party.md) | Vendor/intermediary, bribery & corruption, correspondent/nested, TBML risk | Covered — 4 prompts |
| [Data Governance](data-governance.md) | The data the controls run on: critical data elements, lineage, quality rules, incidents | Mature — engine + 4 prompts |
| [New-Product Approval & Product Risk](npa-product-committee.md) | Pre-launch product risk, approval routing, launch readiness, post-implementation review | Mature — engine + 3 prompts |

## On the roadmap

Team coverage is complete, and the depth build-out that was queued here has shipped:
the watchlist knowledge base, the compliance prompts (SAR decisioning, UBO unwinding,
periodic-review triggers, case QA, network/link analysis), and the controls and
governance prompts (EWRA, SR 11-7 model-validation workpaper, issue/remediation
tracking) are all in the library now, alongside six additional runnable engines.

What remains is genuinely optional:

- **A fraud-detection engine** — the fraud team is covered by prompts; whether the
  mule-detection and scam-scoring problem warrants a runnable engine with its own
  validation evidence is an open call, not a commitment.

---

New to the repository, or briefing a non-technical audience? Start with
[How the system works](../docs/how-the-system-works.md) — a plain-English guide to the
whole library.
