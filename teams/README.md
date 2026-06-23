# teams/ — the toolkit, organized by who does the work

The rest of this repository is organized by *artifact type* — prompts here, runnable
frameworks there, reference and templates elsewhere. These hub pages are a second view
over the same content, organized by **financial-crime team**: each one bundles everything relevant
to a team in one place, in plain English, so you can start from your function instead of
the file layout.

> **In plain terms:** find your team below, open its hub, and it points you to exactly
> the prompts, engines, references, and templates you'd actually use — no need to know
> how the repo is laid out.

A hub is pure navigation and orientation: it contains no prompt text and no code, only
curated links into the by-type folders plus a plain-English walkthrough. The underlying
files stay the single source of truth.

## Team hubs

| Team | Accountable for | Maturity |
|------|------------------|----------|
| [Sanctions & Screening](sanctions-screening.md) | Screening customers/payments against sanctions & watchlists; alert disposition | Mature — engine + prompts |
| [Transaction Monitoring](transaction-monitoring.md) | Detecting & dispositioning suspicious activity; keeping rules calibrated | Mature — 2 engines + prompts |
| [Crypto / Blockchain Intelligence](crypto-blockchain.md) | Address, flow, token, and protocol risk | Mature — engine + prompts |
| [KYC / CDD / Onboarding](kyc-cdd-onboarding.md) | Customer risk rating; entity & counterparty assessment | Mature — engine + prompts |
| [Adverse-Media Screening](adverse-media-screening.md) | Is the negative-news hit the right party, and is it materially adverse? | Mature — engine |
| [Investigations & SAR](investigations-sar.md) | Case investigation & suspicious-activity narratives | Core covered — narrative; SAR decisioning on roadmap |
| [Financial-Crime Risk Assessment](fincrime-risk-assessment.md) | Enterprise risk register, controls, residual exposure | Covered — register + control matrix |
| [Controls, Testing & QA](controls-testing-qa.md) | Control design and independent testing | Mature — full controls suite |
| [Model Risk & Governance](model-risk-governance.md) | Governing & validating models / AI tools | Strong — reviews + worked validation evidence |
| [Regulatory Affairs & Exam](regulatory-affairs-exam.md) | Regulatory tracking, obligations, gaps, exam response | Mature — full regulatory suite |

## On the roadmap

Three teams have content in active development — the prompts and engines for them are
being built out next, and a hub will be added as each lands:

- **Fraud** — APP/scam, wire/check, account-takeover and mule detection.
- **Trade & Communications Surveillance** — market-abuse (spoofing/layering) and
  comms-lexicon screening.
- **ABC / Third-Party / Correspondent Banking** — anti-bribery & corruption, vendor due
  diligence, nested-account / correspondent risk, and trade-based money laundering.

---

New to the repository, or briefing a non-technical audience? Start with
[How the system works](../docs/how-the-system-works.md) — a plain-English guide to the
whole library.
