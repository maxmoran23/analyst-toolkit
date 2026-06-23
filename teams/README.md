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
| [Fraud](fraud.md) | Scams, payment fraud, account misuse, mule detection | Covered — 5 prompts |
| [Trade & Communications Surveillance](trade-comms-surveillance.md) | Market abuse in trading and misconduct in communications | Covered — 3 prompts |
| [ABC, Third-Party & Correspondent Banking](abc-third-party.md) | Vendor/intermediary, bribery & corruption, correspondent/nested, TBML risk | Covered — 4 prompts |

## On the roadmap

The team coverage above is complete. Remaining build-out is additive depth within
existing teams rather than new teams:

- **More compliance prompts** — SAR decisioning (file vs no-file), UBO / beneficial-ownership unwinding, periodic-review triggers, case-QA orchestration, network/link analysis.
- **More controls/governance prompts** — enterprise-wide risk assessment (EWRA), SR 11-7 model-validation workpaper, issue/remediation tracking.
- **A self-updating watchlist knowledge base** — ingesting public OFAC/EU/UN/UK lists with dedup and change detection to feed the screening frameworks.

---

New to the repository, or briefing a non-technical audience? Start with
[How the system works](../docs/how-the-system-works.md) — a plain-English guide to the
whole library.
