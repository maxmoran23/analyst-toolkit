# How the analyst-toolkit works — a guide for reviewers

A plain-English walkthrough of the whole library, written for a senior reviewer who
needs to understand what it is, what it can and cannot do, and why its results can be
trusted — without reading any code or pasting any prompt. If you only read one
document in this repository, read this one.

> **In plain terms:** This repository is a library of two things — written
> instructions that make an AI assistant produce rigorous, sourced compliance work,
> and a handful of small, runnable engines that triage huge alert volumes with proof
> they don't miss real risk. Nothing here connects to a bank system, blocks a payment,
> or files a report. It drafts and it scores; a qualified person always decides.

---

## 1. What this is, in one page

It is a **library, not software**. There is nothing to install, no system to run, and
nothing you are required to connect it to. You do not deploy it; you *use* it:

- For most tasks, you copy a **prompt** — a page of written instructions — and paste it
  into an AI assistant (Microsoft 365 Copilot, GitHub Copilot, Claude, ChatGPT). The
  assistant produces a structured, sourced, audit-defensible result: an entity risk
  assessment, a sanctions screen, an alert disposition, a control-testing workpaper, a
  regulatory gap analysis, a committee reporting pack.
- For a few high-volume problems, you run a small **framework** — a transparent scoring
  engine that triages tens of thousands of alerts and comes with reproducible proof of
  how accurate it is.

Every instruction here was distilled from a working compliance-automation practice and
stripped to its portable core — the analytical method, the scoring logic, the output
structure, and the quality bar — so it travels to any assistant, any account, any
machine, with nothing proprietary attached.

The library covers every team in a financial-crime organization: sanctions and screening,
transaction monitoring, fraud, trade and communications surveillance, crypto/blockchain,
KYC/CDD, investigations and SAR, anti-bribery and third-party risk, risk assessment,
controls and testing, model governance, data governance, new-product approval, and
regulatory affairs.

---

## 2. The three kinds of things in here

Everything in the repository is one of three artifact classes. Knowing which is which
is most of what you need to navigate it.

### Prompts — the analyst's method, written down
A prompt is a self-contained page you paste into an AI assistant. It carries the method
(how to think about the task), the scoring rubric, the required output structure, and
the quality bar. There are 78 of them across 14 categories. You fill in a few
blanks (the entity, the document, the date) and run it. The work product is the prompt
itself — the discipline is baked in, so two different people get comparably rigorous
output. *What you'd use it for: any one-off analytical task — assess this counterparty,
screen this name, disposition this alert, extract the obligations from this rule.*

### Frameworks — small runnable engines, with proof they work
A framework is a different kind of thing: a transparent, runnable scoring engine for a
problem that is fundamentally about **volume** — sorting 50,000 sanctions or monitoring
alerts a month, where almost all are false positives. There are 15 of them. Each
framework comes with a methodology document (every weight and threshold written out),
the engine itself, a generator that creates realistic synthetic test data, and —
crucially — a **validation report with real numbers** showing how well it performs.
*What you'd use it for: the high-volume triage problems where an analyst cannot read
every item by hand.*

### Reference and templates — the knowledge and the formatting
The reference files are sourced domain cheat-sheets (money-laundering typologies, the
regulatory map, blockchain entity types). The templates are reusable output scaffolds
(dashboards, Word/Excel/PDF report formats, compliance-document specs) so a finished
deliverable looks consistent and professional. *What you'd use it for: grounding the
analysis in the right citations, and rendering the result into a polished document.*

---

## 3. What each financial-crime team gets (capability map)

Each team has a **hub page** under `teams/` that bundles everything relevant to it in
one place, in plain English. The short version:

| Team | What the toolkit gives them | One thing to remember |
|------|------------------------------|------------------------|
| **Sanctions & Screening** | A name-screening engine that clears ~92% of false-positive alerts with zero missed true matches, a PEP engine (~84% cut) that answers both "right party?" and "still material?", a watchlist knowledge base that keeps the list data deduplicated, plus ad-hoc screening prompts | It clears only alerts it can *name a reason* for; everything else goes to an analyst — and a current PEP is never auto-cleared |
| **Transaction Monitoring** | An alert-scoring engine (~85% false-positive cut) and a rule threshold-tuning engine (above/below-the-line testing) | It never auto-closes a recognised laundering pattern, and never files a SAR |
| **Crypto / Blockchain** | An on-chain address-risk engine (~88% false-positive cut), an OSINT evidence engine that stamps every captured fact with its source, retrieval time, and content hash, plus tracing/screening prompts and dedicated Travel Rule readiness, counterparty VASP assessment, stablecoin reserve review, and mixer/bridge exposure-disposition prompts | It distinguishes "near a mixer" from "six hops away through an exchange" — and it states observations, never attributions |
| **KYC / CDD / Onboarding** | A customer risk-rating engine and entity-assessment prompts | A customer with a serious red flag can *never* be rated low |
| **Adverse-Media Screening** | An engine that sorts negative-news hits by "right party?" and "really adverse?" | A bare common-name match with no identifier is never auto-cleared — it goes to a person |
| **Investigations & SAR** | Narrative drafting, SAR file/no-file decisioning, UBO unwinding, network link analysis, and a case-QA engine that gates files before closure | It drafts the narrative and the decision memo; the filing decision is human. A critically deficient case file can never pass QA |
| **Financial-Crime Risk Assessment** | Risk-register, control-matrix, and enterprise-wide risk assessment (EWRA) builders | Generic, bank-grade templates — not employer-specific |
| **Controls, Testing & QA** | Control-matrix, independent-testing, QA, and issue-remediation prompts, plus an attribute-sampling engine that computes sample size and the exact upper deviation limit | The sampling engine hands the tester the exact statistical statement; the tester still grades the control |
| **Model Risk & Governance** | Model-governance review and SR 11-7 validation-workpaper prompts, plus all 15 frameworks' validation evidence as worked examples | The frameworks *are* worked examples of validated models |
| **Regulatory Affairs & Exam** | Regulatory-scan, obligation-extraction, gap-analysis, and exam-response prompts | Reference tables are point-in-time; confirm against the source |
| **Fraud** | Scam (APP), wire, and check-fraud disposition prompts, mule-account review, and fraud-typology-to-detection-rule mapping | It prepares the case and frames the liability view; a human holds, recalls, reimburses, or files |
| **Trade & Communications Surveillance** | Trade-alert triage, flagged-communications review, and market-abuse case construction | It always weighs the legitimate-strategy alternative before concluding manipulation |
| **ABC, Third-Party & Correspondent** | Vendor diligence, bribery/corruption exposure, correspondent and nested-access risk, and TBML red-flag screening | Third-party risk is assessed on the relationship, not just the counterparty's paperwork |
| **Data Governance** | A data-quality engine that decides whether a customer extract is fit to screen against, plus CDE-inventory, lineage, rule-authoring, and incident-triage prompts | A feed whose screening-critical fields breach their ceiling can never pass — and nothing is ever silently repaired |
| **New-Product Approval** | A product-risk engine that tiers and routes a proposal pre-launch, plus assessment, launch-readiness, and post-implementation-review prompts | A proposal with a serious hard attribute can never be tiered low, and a prohibited activity is referred rather than scored |
| **Every team (communications automation)** | A domain-neutral automation lane: turn raw email or chat exports into structured, continuously-maintained markdown archives; refresh an existing report surgically from new communications; compose pre-populated `.eml` drafts; and a meta-prompt that turns any recurring review process into a configured pipeline spec | It maintains artifacts across runs — unchanged content is preserved byte-for-byte, anything unparsed is listed rather than dropped, and nothing is ever sent |

---

## 4. How we know it works — the trust model

This is the section a reviewer should weigh most. The library makes its quality
*checkable*, not just asserted.

**The prompts are disciplined and self-contained.** Every prompt is built to a fixed
quality bar: a defined severity scale, a source hierarchy (prefer the original record;
cite the rule before the violation), a strict separation of what is *observed* from what
is *alleged* or *projected*, and a confidence rating on every output. A prompt is also
**self-contained** — when you paste it into a locked-down work machine with no file
access, nothing it relies on is missing. A continuous-integration check enforces this on
every change: it fails the build if a prompt ever references a file that wouldn't travel
with it.

**The frameworks are deterministic, reproducible, and validated.** Each scoring engine
is plain, readable code — no black box. The same inputs always produce the same result.
Each one ships a validation report whose numbers are *emitted by a script anyone can
re-run from a fixed seed*, not typed in by hand. Each framework folder is also
**self-contained**: alongside its evidence pack it carries a `reference-data/` folder of
small, seeded, synthetic sample-input files with a documented schema — so you can see
exactly what the engine consumes without leaving the folder, and a build check fails if
those samples ever drift from what the generators produce. And each one is held to a hard safety
rule appropriate to compliance: **the cost of a false negative is treated as
unacceptable.** Concretely:

- A screening or monitoring engine must never auto-clear a genuine match or a genuinely
  suspicious case. This is enforced as a *build gate* — the validation run fails if the
  engine ever clears a single planted true positive. The reported recall on true
  positives is **1.000 with zero false negatives** across every screening/monitoring
  framework.
- The scoring engines must never rate a known-high-risk case "low," and their scores must
  never fall when risk rises (they are mathematically monotonic). This holds for the
  customer risk-rating engine and for the new-product engine, where a proposal carrying a
  serious hard attribute can never be tiered LOW and a prohibited activity is referred to
  the policy owner rather than scored around. Both properties are tested.
- The same rule holds wherever a "pass" is consequential: a critically deficient
  investigation case file can never pass QA, and a customer feed whose screening-critical
  data elements breach their documented ceiling can never be passed to screening. Each is
  a hard gate, not a weight — no composite score can outvote it.
- An engine only auto-clears an alert when it can state a **named, provable reason** (a
  contradicting date of birth, an entity-type mismatch, exposure broken by an exchange).
  It never clears something merely because a score was low. That is the difference
  between a decision that survives an examination and one that does not.
- Where the output is evidence rather than a score, the guarantees are evidentiary: every
  captured fact carries its source, retrieval time, and content hash; totals reconcile
  exactly to the captures with nothing dropped or double-counted; and the same captures
  re-render byte-identically on every run. The sampling engine's statistical conclusions
  are cross-checked against an independent computation rather than a lookup table.

**Nothing here uses real data.** Every example and every test dataset is synthetic, and
every entity assessed is fictional (the recurring institution is "Harborview Financial
Group," the recurring counterparty "Meridian Digital Exchange"). The library is built
from generic, public knowledge — public regulatory bodies and public guidance only. No
validation run touches the network: the numbers in every evidence pack are computed
offline from a fixed seed, which is what makes them reproducible. Two frameworks offer
an optional, opt-in path to fetch a *public* list or block-explorer response at run
time; it is never exercised by a validation run, it caches and redistributes nothing,
and it degrades to the synthetic path when unreachable.

---

## 5. What it deliberately does NOT do

Being clear about the boundaries is part of the trust model.

- **It does not connect to bank systems, block payments, file SARs, or off-board
  customers.** It drafts and it scores. Every consequential action remains a documented
  human decision.
- **The frameworks are reference implementations, not production controls.** They show a
  defensible method and prove it on synthetic data. A real deployment would swap the
  internals for the institution's own systems and recalibrate the thresholds against its
  own labelled data — the *method* is what travels, not a turnkey system.
- **It does not replace the analyst or the model-validation function.** It makes both
  faster and more consistent; it does not remove the judgment, the override, or the
  sign-off.
- **The reference tables are point-in-time.** Sanctions lists, high-risk jurisdictions,
  and regulations move; confirm the current state against the issuing body before
  relying on any specific item.

---

## 6. How a piece of work actually flows — one walkthrough

Follow a single example end to end, using the fictional cast.

A payment involving **Harborview Financial Group**'s client "Meridian Capital Partners"
trips the sanctions filter because an SDN entry also contains the word "Capital."

1. **Intake.** The screening filter produces the alert — one of ~50,000 that month,
   almost all false positives.
2. **Triage (framework).** The sanctions name-screening engine reads the alert. It sees
   the match is only on the common token "Capital," that the designated party's
   distinctive name is absent, and that the client's country contradicts the SDN entry.
   It auto-clears the alert with a written reason — "generic-token-only match; the
   designated party's distinctive name was not present." Tens of thousands of such alerts
   clear this way, each with its own reason, leaving a small ranked queue.
3. **Human review (prompt).** For an alert the engine *keeps*, an analyst pastes the
   sanctions-screening prompt, supplies the identifiers, and gets a structured
   disposition memo with a point-by-point comparison.
4. **Escalation.** A confirmed match is routed — with the evidence assembled — to a
   compliance officer, who makes the blocking and reporting decision. The engine never
   makes it.
5. **Deliverable (template).** The disposition is rendered into a Word memo or a
   dashboard using the shared output templates, in a consistent house style.

The same shape — *intake → score/triage → human review → escalate → render* — recurs
across every team.

---

## 7. Glossary

- **ATL / BTL (above/below-the-line)** — testing whether a monitoring rule's threshold is
  set right: are the alerts it fires productive (above the line), and is real risk
  slipping past undetected (below the line)?
- **CDE** — Critical Data Element; a field (name, date of birth, country, identifier) that
  a financial-crime control depends on to work at all.
- **EWRA** — Enterprise-Wide Risk Assessment, the institution's top-level AML risk picture.
- **NPA** — New Product Approval; the committee process that assesses a product's
  financial-crime risk before it launches.
- **False negative** — a real match or real suspicious case wrongly cleared. The
  catastrophic error this library is built to avoid.
- **KYT** — Know Your Transaction; risk-scoring blockchain addresses and flows.
- **PEP** — Politically Exposed Person; a mandatory elevated-risk factor.
- **Recall** — the share of true positives the engine catches. Held at 100% by design.
- **SAR** — Suspicious Activity Report, the regulatory filing a human decides to make.
- **SR 11-7** — the U.S. supervisory guidance on model risk management; the frameworks are
  documented to its four pillars (conceptual soundness, outcomes analysis, ongoing
  monitoring, limitations).
- **UBO** — Ultimate Beneficial Owner; the real person behind a legal structure.
- **VASP** — Virtual Asset Service Provider (e.g., a crypto exchange).

---

## 8. Where to go next, by role

- **If you run reviews or triage:** open your team's hub under `teams/`, then the prompt
  or framework it points to.
- **If you need to check the numbers rather than believe them:** read
  [`frameworks/EVIDENCE.md`](../frameworks/EVIDENCE.md) — the reproduction command for
  every engine, the exact confidence bound behind every safety claim, and a plain
  statement of what the evidence does not establish. One command re-derives all of it.
- **If you sign off on models:** read [`frameworks/GOVERNANCE.md`](../frameworks/GOVERNANCE.md)
  and any one framework's `evidence/VALIDATION-REPORT.md` — they are worked, reproducible
  model-validation artifacts.
- **If you brief the board or an examiner:** this document plus the
  [`frameworks/`](../frameworks/) overview and the rendered [`samples/`](../samples/) make
  the case that the work is rigorous, sourced, and bounded.
- **If you want the full map:** the repository [`README`](../README.md) indexes every
  directory; the [`teams/`](../teams/) hubs organize it by who does the work.

---

*This guide describes a generic, public methodology library. It is not legal advice, and
it contains no employer-specific, client, or non-public information. Confirm the current
state of any regulation, list, or designation against the issuing body before relying on
it.*
