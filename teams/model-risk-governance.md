# Model Risk & Governance — team hub

> The independent control function accountable for governing and validating the models and AI tools used across financial-crime compliance.

## In one minute

This team is the independent check on every model and AI tool the financial-crime program relies on — transaction-monitoring scenarios, sanctions-screening matchers, risk-scoring engines, and the newer AI assistants used by analysts. The work is governance (does this tool have an owner, documented purpose, approval, and controls?) and validation (can we prove it actually works — that it catches what it should and is not silently failing?). "Good" looks like a defensible paper trail: every model has a tier, a current validation, evidence of outcomes testing (what the model flagged versus what it missed), and a monitoring plan that would catch performance drift before a regulator does. AI can accelerate the analytical legwork — drafting the governance review structure, assessing input data quality and lineage, and running reproducible outcomes analysis (above-the-line and below-the-line testing) at a scale a person cannot do by hand. AI cannot own the model, sign the validation, or decide a tool is fit for use — those are human accountabilities, and every output here is a draft for a qualified reviewer to challenge and approve.

> **In plain terms:** This team makes sure the program's models and AI tools are properly owned, documented, and proven to work — and the toolkit does the heavy analytical lifting so a human can review and sign off faster.

## What this team owns

- Model and AI-tool governance review — confirming each model has an owner, documented purpose, risk tier, approval, and proportionate controls (SR 11-7 style).
- Independent model validation — outcomes analysis that tests whether a model performs as intended, including what it flagged and what it missed.
- Performance and ongoing monitoring — tracking model behavior over time to catch drift, degradation, or breaks before they become findings.
- Input data-quality assessment — checking that the data feeding a model is complete, accurate, timely, and has traceable lineage.

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Run a model/AI-tool governance review | model-governance-review | prompt | [../prompts/controls/model-governance-review.md](../prompts/controls/model-governance-review.md) |
| Write the independent validation workpaper (SR 11-7 pillars) | model-validation-workpaper | prompt | [../prompts/controls/model-validation-workpaper.md](../prompts/controls/model-validation-workpaper.md) |
| Assess input data quality and lineage | data-quality-review | prompt | [../prompts/controls/data-quality-review.md](../prompts/controls/data-quality-review.md) |
| Productized model validation (ATL/BTL outcomes analysis) | tm-threshold-tuning | framework (runnable) | [../frameworks/tm-threshold-tuning/](../frameworks/tm-threshold-tuning/) |
| Thirteen worked, reproducible validation evidence packs | frameworks | framework pillar | [../frameworks/](../frameworks/) |
| The pillar-wide SR 11-7 governance framing | frameworks GOVERNANCE | reference | [../frameworks/GOVERNANCE.md](../frameworks/GOVERNANCE.md) |
| How every framework proves it works (the rigor contract) | RIGOR-CONTRACT | reference | [../frameworks/RIGOR-CONTRACT.md](../frameworks/RIGOR-CONTRACT.md) |

## How the pieces fit

The prompts handle ad-hoc, one-off analysis — point model-governance-review at a specific model to surface gaps in ownership, tiering, and approval; point data-quality-review at its inputs; and use model-validation-workpaper when the engagement calls for a full independent validation along the conceptual-soundness, ongoing-monitoring, and outcomes-analysis pillars, with the effective challenge documented rather than asserted. The tm-threshold-tuning framework is the runnable counterpart: it performs above-the-line and below-the-line outcomes analysis at scale and emits reproducible validation evidence, making it itself a worked example of a validated model a reviewer can study. So do the other twelve — every framework in this repository ships an `evidence/VALIDATION-REPORT.md` whose numbers are emitted by a script anyone can re-run from a fixed seed, which is what a validation function usually has to demand rather than inherit. The two reference documents sit underneath everything — GOVERNANCE.md supplies the SR 11-7 framing the prompts apply, and RIGOR-CONTRACT.md is the standard every framework must meet to claim it works. In practice: governance review -> data-quality assessment -> validation workpaper -> outcomes analysis -> human review and sign-off.

## Capabilities & limitations

**What these tools DO**

- Structure a governance review and surface gaps in ownership, documentation, tiering, and approval.
- Draft an independent validation workpaper against the SR 11-7 pillars, with a findings register and the effective challenge written down.
- Assess input data completeness, accuracy, timeliness, and lineage before a model is trusted.
- Run above-the-line and below-the-line outcomes analysis at scale and produce reproducible validation evidence.
- Give a non-technical reviewer a clear, citable trail to challenge and approve.

**What they deliberately do NOT do**

- They are reference implementations and analytical aids, not production controls or a system of record.
- They score, route, and document — but a qualified human owns the model, signs the validation, and decides fitness for use.
- They never auto-approve, auto-block, retire a model, or file anything; every output is a labeled draft for human review.

## Start here

If you do one thing, do this:

1. Read [../frameworks/GOVERNANCE.md](../frameworks/GOVERNANCE.md) to see the SR 11-7 framing this team applies — what governance and validation are expected to cover.
2. Open [../frameworks/tm-threshold-tuning/](../frameworks/tm-threshold-tuning/) and look at its evidence — it is a worked, validated model you can study end to end, and the proof standard it meets is defined in [../frameworks/RIGOR-CONTRACT.md](../frameworks/RIGOR-CONTRACT.md).
3. When you have a real model or AI tool to review, run the [../prompts/controls/model-governance-review.md](../prompts/controls/model-governance-review.md) prompt first, then [../prompts/controls/data-quality-review.md](../prompts/controls/data-quality-review.md) on its inputs. If the engagement is a full validation rather than a governance check, run [../prompts/controls/model-validation-workpaper.md](../prompts/controls/model-validation-workpaper.md) — and hand every draft to a qualified reviewer to challenge and sign.
