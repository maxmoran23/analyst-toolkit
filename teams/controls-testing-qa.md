# Controls, Testing & QA — team hub

> This team designs the AML/CFT controls the program relies on and independently tests that those controls — and the models behind them — actually work.

## In one minute

This team sits one step back from front-line investigation work. It defines what the controls are supposed to do, writes them down in a structured control matrix, and then independently checks whether they hold up — by testing samples, reviewing analyst output, examining the data feeding the controls, and scrutinizing the models and AI tools in use. "Good" looks like clear, traceable evidence: every control has an owner and a test, every test has a documented sample and result, and every exception is tracked to resolution so an examiner or auditor can follow the chain end to end. AI in this toolkit can accelerate the drafting and structuring of that evidence — building the matrix, framing test procedures, scoring analyst files against a rubric, and producing reproducible threshold-test output — which removes the blank-page and formatting burden. AI cannot decide whether a control passes, sign the workpaper, or set a threshold; those judgments stay with the tester, and the frameworks here are reference implementations, not live production controls.

> **In plain terms:** the tools draft the testing paperwork and crunch the threshold math; a person still reads the evidence and decides whether the control works.

## What this team owns

- AML/CFT control matrix — the structured inventory of controls across CDD, transaction monitoring, sanctions, SAR filing, and governance
- Independent control-testing workpaper — sampling, test procedures, and exception tracking that evidence whether controls operate as designed
- QA review of analyst work — scoring completed analyst files for quality, consistency, and defensibility
- Data-quality & lineage review — checking the completeness, accuracy, and traceability of the data that feeds the controls
- Model / AI-tool governance review — assessing how monitoring models and AI tools are validated, documented, and overseen
- Rule / threshold testing (ATL/BTL) — above-the-line and below-the-line testing to evidence that monitoring thresholds are set defensibly

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Build a control matrix | control-matrix-builder | prompt | [../prompts/controls/control-matrix-builder.md](../prompts/controls/control-matrix-builder.md) |
| Build an independent testing workpaper | independent-testing-workpaper | prompt | [../prompts/controls/independent-testing-workpaper.md](../prompts/controls/independent-testing-workpaper.md) |
| QA-score analyst files | qa-review-scorecard | prompt | [../prompts/controls/qa-review-scorecard.md](../prompts/controls/qa-review-scorecard.md) |
| Review data quality & lineage | data-quality-review | prompt | [../prompts/controls/data-quality-review.md](../prompts/controls/data-quality-review.md) |
| Review model/AI-tool governance | model-governance-review | prompt | [../prompts/controls/model-governance-review.md](../prompts/controls/model-governance-review.md) |
| Test & tune monitoring thresholds (ATL/BTL) | tm-threshold-tuning | framework (runnable) | [../frameworks/tm-threshold-tuning/](../frameworks/tm-threshold-tuning/) |
| Testing-workpaper spec | testing-workpaper | template | [../output-templates/compliance-docs/testing-workpaper.md](../output-templates/compliance-docs/testing-workpaper.md) |

## How the pieces fit

The prompts handle ad-hoc, document-by-document work — drafting the control matrix, framing a testing workpaper, scoring an analyst file, or reviewing data lineage or model governance one engagement at a time. The runnable framework is what produces worked, reproducible evidence at scale: it tests monitoring thresholds (above- and below-the-line) and generates output a reviewer can re-run and verify. The template defines the shape of the final testing deliverable so the prompt-drafted and framework-generated evidence land in a consistent, examiner-ready format. In sequence: define controls (control-matrix-builder) -> design the test (independent-testing-workpaper + testing-workpaper template) -> generate threshold evidence at scale (tm-threshold-tuning) -> QA the resulting analyst output (qa-review-scorecard) -> support it all with data-quality and model-governance reviews.

## Capabilities & limitations

**What these tools DO**

- Draft and structure the control matrix, testing workpaper, and review write-ups so the team starts from a complete skeleton, not a blank page
- Score analyst files against a consistent rubric to surface gaps and inconsistencies
- Produce reproducible above-the-line / below-the-line threshold-test evidence that a reviewer can re-run
- Frame data-quality, lineage, and model-governance questions into a repeatable review structure

**What they deliberately do NOT do**

- They are reference implementations and drafting aids, not production controls or a system of record
- They score and route, but a human decides pass/fail, sets thresholds, and signs the workpaper
- They never auto-block, auto-file, or take any external action on their own
- They do not validate a model or certify a control on their own authority — that judgment stays with the tester

## Start here

1. Open [control-matrix-builder](../prompts/controls/control-matrix-builder.md) and draft (or refresh) the control matrix — it is the inventory everything else tests against.
2. Pick one control and run [independent-testing-workpaper](../prompts/controls/independent-testing-workpaper.md), shaping the output to the [testing-workpaper](../output-templates/compliance-docs/testing-workpaper.md) spec, to see what a defensible test looks like end to end.
3. For threshold work, open the [tm-threshold-tuning](../frameworks/tm-threshold-tuning/) framework and read its README to run the ATL/BTL test and inspect the reproducible evidence it generates.
