# Controls, testing & governance prompts

These prompts cover the second-line and assurance side of a compliance program: documenting the control environment, registering and scoring risk, testing controls independently, quality-checking analyst work, and governing the models, tools, and data the program runs on. Each turns an AI assistant into a specific assurance role with a defined method, scoring rubric, and structured output.

| Prompt | What it does |
|--------|--------------|
| [control-matrix-builder](control-matrix-builder.md) | Build a six-domain AML/CFT control inventory from a program scope; 27-control reference framework, gap register, remediation view |
| [risk-register-builder](risk-register-builder.md) | Build a compliance risk register with inherent L×I scoring, control offset, residual ratings, appetite comparison, and dual heat maps |
| [independent-testing-workpaper](independent-testing-workpaper.md) | Design and document a control test to audit standard — sample methodology, attribute results, exceptions with root cause, effectiveness conclusion |
| [qa-review-scorecard](qa-review-scorecard.md) | Score completed work items against a weighted QA rubric; per-item scorecards, pass rate, error taxonomy, coaching themes |
| [model-governance-review](model-governance-review.md) | Assess a model, rule set, or AI-assisted tool against model-risk-management expectations; eight-dimension scorecard and governance recommendation |
| [data-quality-review](data-quality-review.md) | Assess a dataset or feed across six quality dimensions, map source-to-use lineage with handoff controls, and produce a defect log and remediation register |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
