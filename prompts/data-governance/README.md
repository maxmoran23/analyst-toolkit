# Data governance prompts — for financial-crime systems

Screening, monitoring, and reporting are only as good as the data feeding them: a
blank name is never screened, a stale list screens against the past, and a silently
dropped record is invisible to every downstream control. These prompts cover the
data-governance work that keeps those failure modes visible — knowing which elements
matter, where they come from, how their quality is tested, and what to do when they
break. Each turns an AI assistant into a specific data-governance role with a defined
method, decision criteria, and a structured, severity-coded output.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | Data-governance teams that own the data the financial-crime systems run on. |
| **The question it answers** | Which data fields do our controls actually depend on, where do they come from, and are they fit to use? |
| **What these are** | Paste-ready prompt templates. Each file contains one fenced block that *is* the tool: copy it, replace the `{{PLACEHOLDERS}}`, paste it into whatever assistant you already have — Microsoft 365 Copilot, GitHub Copilot, Claude, ChatGPT. |
| **Setup required** | None. Nothing to install, no account, no integration, no repository access. A prompt works when pasted into a locked-down work machine with no file system. |
| **What you get** | A structured, sourced result with a defined method, a scoring rubric, and a fixed output shape — so two analysts running the same prompt produce comparable work. |
| **What they never do** | They draft, score, and structure. They do not decide. Every clear, escalate, block, reimburse, or file decision stays with a person, and an unverifiable claim is labelled or omitted rather than invented. |

### Using one, in about a minute

1. Open any prompt file in this folder and copy the single fenced block under `## The prompt`.
2. Replace every `{{PLACEHOLDER}}` — an unfilled one produces a vague answer.
3. Paste it into your assistant along with the case facts, document, or data.

Want a finished Word / Excel / PDF / dashboard deliverable out of it? Attach one more
file — [`BASE.md`](../../BASE.md) — which carries the writing voice, the quality floor,
and the renderer. **One prompt plus `BASE.md` is the entire system; there is never a
third file**, and a CI job fails the build if any prompt breaks that rule.

<!-- /STANDALONE-BRIEF -->

| Prompt | What it does |
|--------|--------------|
| [cde-inventory](cde-inventory.md) | Build or challenge a critical-data-element inventory: a disciplined criticality test from consuming-process dependency, per-CDE records (definition, owner, source of truth, quality thresholds, consuming controls), tiering, and a wave-based buildout plan |
| [data-lineage-mapping](data-lineage-mapping.md) | Map one critical data element from origin to every consuming process: hop table with owners and transformations, control assessment per handoff, break-risk register, lineage diagram description |
| [dq-rule-authoring](dq-rule-authoring.md) | Translate a CDE quality requirement into named, testable rules across five dimensions: plain-language plus pseudologic per rule, thresholds with rationale, a false-flag budget, and a rulebook table |
| [data-incident-triage](data-incident-triage.md) | Triage a fincrime-impacting data break: blast radius across screening/monitoring/reporting populations, lookback scoping, a regulatory-notification consideration checklist, interim compensating controls, and an incident record with severity and timeline |

The four chain in order: the inventory decides which elements deserve governance,
the lineage map shows where each can break, the rulebook makes its quality testable,
and the incident triage handles the day one of them breaks anyway.

**Who this is for:** data-governance analysts and data stewards supporting a
financial-crime program, owners of screening and monitoring feeds, compliance-testing
and internal-audit teams evidencing data controls, and anyone who has been asked
"can we trust the data behind this system" and needs a defensible answer rather
than an assurance.

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
