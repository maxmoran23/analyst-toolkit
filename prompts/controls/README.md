# Controls, testing & governance prompts

These prompts cover the second-line and assurance side of a compliance program: documenting the control environment, registering and scoring risk, testing controls independently, quality-checking analyst work, and governing the models, tools, and data the program runs on. Each turns an AI assistant into a specific assurance role with a defined method, scoring rubric, and structured output.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | Controls design, independent testing, QA, model governance, and internal audit. |
| **The question it answers** | Are the controls documented, tested, and evidenced well enough to survive an examination? |
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
| [control-matrix-builder](control-matrix-builder.md) | Build a six-domain AML/CFT control inventory from a program scope; 27-control reference framework, gap register, remediation view |
| [risk-register-builder](risk-register-builder.md) | Build a compliance risk register with inherent L×I scoring, control offset, residual ratings, appetite comparison, and dual heat maps |
| [independent-testing-workpaper](independent-testing-workpaper.md) | Design and document a control test to audit standard — sample methodology, attribute results, exceptions with root cause, effectiveness conclusion |
| [qa-review-scorecard](qa-review-scorecard.md) | Score completed work items against a weighted QA rubric; per-item scorecards, pass rate, error taxonomy, coaching themes |
| [model-governance-review](model-governance-review.md) | Assess a model, rule set, or AI-assisted tool against model-risk-management expectations; eight-dimension scorecard and governance recommendation |
| [data-quality-review](data-quality-review.md) | Assess a dataset or feed across six quality dimensions, map source-to-use lineage with handoff controls, and produce a defect log and remediation register |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
