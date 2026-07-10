# Data Governance — team hub

> This team owns the data that financial-crime screening, monitoring, and regulatory reporting depend on: which fields are critical, where they come from, whether they are fit to use, and what happens when they break.

## In one minute

Sanctions screening cannot match a name that is blank. Transaction monitoring cannot
baseline a customer whose onboarding date parses as a future date. A regulatory report
cannot be filed against an identifier that fails its own check digit. This team is the
reason those things do not happen: it names the critical data elements (CDEs) the
financial-crime controls actually depend on, traces each one from its origin system to
every control that consumes it, writes the quality rules that make "fit to screen
against" a testable condition rather than an opinion, and works the incident when a feed
breaks anyway. "Good" looks like every screening-critical field having a named owner, a
named source of truth, a named threshold, and a defect list nobody has to argue about.
AI and the runnable engine here do the volume work — testing every record against named
rules, grading each critical field, and dispositioning the feed with a written reason —
which is the part no human can do by hand across a million-record extract. What they do
not do is repair anything: a broken feed is never silently imputed, dropped, or
corrected. It routes to a person with the evidence attached.

> **In plain terms:** screening and monitoring are only as good as the names, dates,
> countries, and ID numbers they are fed. This team makes sure those fields are right,
> and the tools inspect every record and say plainly whether the file is safe to use.

## What this team owns

- Critical-data-element (CDE) inventory — naming the fields the financial-crime controls depend on, each with an owner and a source of truth
- Lineage — tracing each CDE from its origin system through every transformation to every consuming control, and exposing the hops nobody controls
- Data-quality rules and thresholds — turning "fit for screening" into named, testable rules with criticality and pass thresholds
- Feed fitness — deciding whether a given extract is fit to screen against, before it reaches the screening engine
- Data incidents — triaging a break that has already reached financial-crime systems: blast radius, lookback scoping, interim compensating controls

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Decide whether a customer extract is fit to screen against | data-quality-rules | framework (runnable, critical-defect recall 1.0, 0 false flags, hard feed gate) | [../frameworks/data-quality-rules/](../frameworks/data-quality-rules/) |
| Name the fields the controls actually depend on | cde-inventory | prompt | [../prompts/data-governance/cde-inventory.md](../prompts/data-governance/cde-inventory.md) |
| Trace one CDE from origin to every consuming control | data-lineage-mapping | prompt | [../prompts/data-governance/data-lineage-mapping.md](../prompts/data-governance/data-lineage-mapping.md) |
| Turn a quality requirement into named, testable rules | dq-rule-authoring | prompt | [../prompts/data-governance/dq-rule-authoring.md](../prompts/data-governance/dq-rule-authoring.md) |
| Work a data break that reached financial-crime systems | data-incident-triage | prompt | [../prompts/data-governance/data-incident-triage.md](../prompts/data-governance/data-incident-triage.md) |
| Assess a dataset across six quality dimensions for an engagement | data-quality-review | prompt | [../prompts/controls/data-quality-review.md](../prompts/controls/data-quality-review.md) |
| Render any output as Word/Excel/PDF/HTML | BASE.md | companion | [../BASE.md](../BASE.md) |

## How the pieces fit

The four data-governance prompts run in the order the work actually happens.
cde-inventory names what matters, working backwards from the controls that consume it.
data-lineage-mapping follows each named CDE hop by hop to its origin and flags the
transformations nobody owns. dq-rule-authoring turns each requirement into a named rule
with a dimension, a threshold, and a criticality. The data-quality-rules framework is
those rules made runnable: it executes them across an entire extract, produces a defect
list per record and a scorecard per critical field, and dispositions the whole feed as
FEED_PASS, INVESTIGATE, or BLOCK — where a screening-critical field over its documented
ceiling is a hard gate, not a weight. When something breaks in production,
data-incident-triage scopes the blast radius and the lookback. data-quality-review is the
engagement-level version for a one-off assessment of a dataset or feed. Flow: name the
CDEs -> map the lineage -> author the rules -> run the feed through the engine -> triage
the break. Everything downstream — sanctions, monitoring, reporting — inherits the result.

## Capabilities & limitations

**What these tools DO**

- Test every record against named rules across completeness, validity, consistency, uniqueness, and timeliness, and name the rule that fired
- Grade each critical data element and disposition the whole feed with a written, provable reason
- Hold a hard gate: a feed whose screening-critical fields breach their documented ceiling can never pass to screening, whatever the composite score says
- Expose uncontrolled lineage hops and the break risk each one carries
- Convert a quality requirement into implementable rules with thresholds, criticality, and a rulebook a tester can run

**What they deliberately do NOT do**

- They never drop, impute, repair, or silently correct a record — a failing feed routes to a person with its full defect list
- The framework is a reference implementation, not a production data-quality platform or a system of record
- They do not connect to source systems, and they do not certify a feed for use — a data owner does
- Lookback scope, notification, and remediation acceptance are human decisions the incident prompt frames but never makes

## Start here

1. Open [../frameworks/data-quality-rules/](../frameworks/data-quality-rules/) and read its README — the three feed dispositions and the hard screening-critical gate are the mental model everything else in this hub serves.
2. Run [cde-inventory](../prompts/data-governance/cde-inventory.md) on one control you already understand (sanctions name screening is the easiest), then [data-lineage-mapping](../prompts/data-governance/data-lineage-mapping.md) on the single most critical field it produced.
3. Turn that field's requirement into rules with [dq-rule-authoring](../prompts/data-governance/dq-rule-authoring.md), and keep [data-incident-triage](../prompts/data-governance/data-incident-triage.md) ready for the day a feed breaks — render any of it with [../BASE.md](../BASE.md).
