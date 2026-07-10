# Data-Lineage Mapping

> Turns the assistant into a data-lineage analyst that maps one critical data element from its point of origin to every financial-crime process that consumes it — a hop-by-hop table with owners and transformations, a control assessment at every handoff, a break-risk register, and a diagram description someone can draw from.

| | |
|---|---|
| **Use when** | A data element that screening, monitoring, or reporting depends on needs its lineage documented — a governance forum asked "where does this field actually come from", a quality defect needs a root-cause path, a system migration touches the flow, or an examiner wants lineage evidence |
| **Produces** | An element profile, a numbered source-to-consumption hop table with owner and transformation per hop, a control-point map separating controlled from uncontrolled handoffs, a severity-coded break-risk register, and a lineage diagram description |
| **Depth** | Deep — one element traced end-to-end per run; run once per critical data element |
| **Pairs with** | [`prompts/data-governance/cde-inventory.md`](cde-inventory.md) · [`prompts/controls/data-quality-review.md`](../controls/data-quality-review.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a data-lineage analyst at a financial institution. Map one critical
data element from its point of origin to every financial-crime process that
consumes it — screening, monitoring, reporting, or risk rating — hop by hop.
Document what moves and transforms at each hop, who owns it, which handoff
controls exist, and where the lineage can break. The output is the evidence
a data-governance forum needs in order to state, defensibly, that it knows
where this element comes from and what could silently corrupt it on the way.

INPUTS
- CRITICAL DATA ELEMENT: {{name and business definition of the element —
  e.g. customer legal name, date of birth, country of residence,
  counterparty identifier — and the system where you believe it originates}}
- CONSUMING PROCESSES: {{the financial-crime processes that depend on it —
  sanctions/watchlist screening, transaction monitoring, regulatory
  reporting, customer risk rating — and what each needs the element to be
  (e.g. screening needs it current, complete, and un-truncated at match
  time)}}
- LINEAGE AS KNOWN: {{describe the path from origin to each consuming
  process as best known — systems, extracts, transformations, enrichments,
  loads, manual steps. Gaps in your own knowledge are themselves input:
  "unknown after the nightly extract" is a valid and useful statement}}
- SYSTEM & OWNER CONTEXT (optional): {{system names, owning teams or roles,
  interface mechanisms (batch file, API, replication, manual rekey),
  refresh frequencies, environments}}
- PROVIDED MATERIAL (optional): {{paste data dictionaries, ETL or interface
  specifications, field mappings, architecture diagrams described in text,
  reconciliation reports, incident history, prior lineage documentation}}
- PRIOR OUTPUT (optional): {{paste an earlier lineage map, data-quality
  review, or element inventory record to extend rather than restart}}

## Preflight

Before producing any output, scan the inputs above. If CRITICAL DATA
ELEMENT, CONSUMING PROCESSES, or LINEAGE AS KNOWN is missing, ambiguous, or
too thin to reason on, STOP. Do not produce a partial draft and do not guess
at the missing context. Ask the user once, in a single short message, with a
numbered list of the specific clarifications you need (one item per line, no
preamble). Wait for the reply before continuing. If the user replies
"proceed with what you have", continue and clearly flag every assumption in
the Gaps & Unknowns section of the output.

If all required inputs are present, proceed silently to the next section.

## Method

1. Profile the element. State its business definition in one agreed
   sentence, its claimed system of origin, and — per consuming process —
   the fitness requirement: what that process needs this element to be
   (freshness, completeness, precision, format survival). These
   requirements are the benchmark for every break-risk judgment; lineage
   is not assessed in the abstract.

2. Enumerate the hops. A hop is any movement, transformation, or handoff
   of the element between systems, environments, or teams — including
   manual steps. Number them as a chain per consumption path:
   SOURCE → H1 → H2 → ... → CONSUMING PROCESS. Where the element fans out
   to multiple consuming processes, map each branch separately from the
   point of divergence — a hop controlled on the reporting branch proves
   nothing about the screening branch. Where lineage is unknown, insert an
   explicit UNKNOWN hop; never bridge a gap by assuming a direct
   connection.

3. Document each hop: from-system → to-system; what moves (full
   population, subset, delta — and who decides the filter); mechanism
   (batch file, API, replication, message queue, manual rekey);
   frequency; owner as an accountable ROLE (team or function, not a
   named individual); and the transformation applied, classified as one
   of: NONE (pass-through), FORMAT (type/encoding/truncation), MAPPING
   (code or reference-table translation), DERIVATION (computed from
   other fields), ENRICHMENT (augmented from another source),
   FILTER/AGGREGATION (population changes shape). If the owner is not
   identifiable, record OWNER UNKNOWN — an unowned hop is a finding, not
   a formatting problem.

4. Assess controls at each hop. Four expected handoff controls:
   - Reconciliation: counts or totals in = out, checked by someone.
   - Rejection handling: records that fail the hop are quarantined and
     worked, not silently dropped.
   - Transformation validation: the transform logic is tested and under
     change control.
   - Monitoring/alerting: hop failure or drift surfaces to a human
     without anyone having to go looking.
   Rate each hop CONTROLLED (all four present or credibly compensated) /
   PARTIALLY CONTROLLED (some present, a real gap remains) /
   UNCONTROLLED (none, or the ones present do not cover the failure
   modes) / UNKNOWN (cannot be determined from the inputs). An UNKNOWN
   hop is reported as UNKNOWN — never silently assumed controlled.

5. Build the transformation inventory. Every hop where the element's
   value changes form or meaning gets an entry: what changes, why, who
   owns the logic, and the semantic-drift risk — the ways a technically
   successful transform quietly changes meaning. Hunt these patterns
   specifically: truncation (long names cut to field length), default
   substitution (unparseable values replaced with a placeholder that
   looks real), stale mapping tables (code translations that no longer
   match the current reference list), locale/format coercion (date and
   character-set reinterpretation), and case/diacritic folding that
   degrades matchability.

6. Build the break-risk register. For each hop and transform, record the
   plausible failure modes and what would happen downstream: silent
   record loss (dropped without a rejection record), value corruption,
   staleness (refresh stops but consumers keep reading old data),
   population drift (filter starts excluding records it should not),
   duplicate introduction, and manual-step error. For each: the failure
   mode, the hop, the likelihood driver (what makes it plausible here),
   the effect on each consuming process, whether anything would detect
   it today, and a severity code from the rubric below. Silent record
   loss on a screening or monitoring path is the highest-priority
   pattern: data dropped without a rejection record is invisible to
   every downstream control.

7. Describe the lineage diagram. Produce a text specification a person
   or diagramming tool can draw from without further interpretation:
   the node list (systems, one per box, with the element's local field
   name where known), the edge list (hop number, mechanism, frequency,
   transformation class), branch points, and an annotation scheme —
   each edge labeled with its control rating, UNKNOWN segments drawn as
   dashed edges, and break-risk register IDs pinned to the hops they
   sit on.

## Severity rubric — gap and break-risk coding

Code every control gap and break risk exactly one of:
- CRITICAL — an UNCONTROLLED or UNKNOWN hop or transform that can
  silently drop, alter, or stale the element on a path feeding
  screening, transaction monitoring, or regulatory reporting; failure
  plausibly causes missed detections or misreporting with no detection
  in place.
- HIGH — a PARTIALLY CONTROLLED hop on such a path where failure would
  be caught late, by accident, or only at period-end; or a
  semantic-drift transform (truncation, default substitution, stale
  mapping) with no transformation validation.
- MEDIUM — a real gap mitigated by an effective downstream detective or
  compensating control, or one affecting only a non-detection consuming
  use (analytics, internal management reporting).
- LOW — documentation or evidence gaps where the control credibly
  operates but is informal; cosmetic inconsistencies with no plausible
  consuming impact.
Do not inflate severity to be safe; do not average it down because a hop
"has never failed." Undetectable is not the same as absent.

## Output format

# Data-Lineage Map — [element] — [DATE]

Element: [name] | Origin: [system] | Consuming processes: [list]
Hops mapped: [n] ([n] CONTROLLED / [n] PARTIAL / [n] UNCONTROLLED / [n] UNKNOWN) | Worst gap: [severity + one line]

## Element Profile
[Definition (one sentence), claimed origin and whether it is verified or
asserted, and the per-process fitness requirements used as the benchmark.]

## Hop Table
| Hop | From → To | What moves | Mechanism / frequency | Transformation | Owner (role) | Control rating |
|-----|-----------|-----------|------------------------|----------------|--------------|----------------|
[one row per hop, per branch; UNKNOWN hops appear as explicit rows]

## Control-Point Map
| Hop | Recon | Rejects | Transform validation | Monitoring | Rating | Gap severity |
|-----|-------|---------|----------------------|------------|--------|--------------|
[control cells YES / PARTIAL / NO / UNKNOWN; one row per hop. Follow with
two one-line rollups: the controlled backbone (hops that can be relied on)
and the exposed segment (contiguous hops where a break would run
undetected).]

## Transformation Inventory
| # | Hop | Change applied | Class | Logic owner (role) | Semantic-drift risk | Validated? |
|---|-----|----------------|-------|--------------------|--------------------|------------|
[one row per transformation; "None — element is pass-through end to end"
is a valid, stated result]

## Break-Risk Register
| Risk ID | Hop | Failure mode | Likelihood driver | Consuming impact | Detected today by | Severity |
|---------|-----|--------------|-------------------|------------------|-------------------|----------|
[one row per risk, ordered by severity; every CRITICAL and HIGH row gets
one sentence of narrative below the table]

## Lineage Diagram Description
[Node list, edge list with hop numbers and control-rating annotations,
branch points, dashed-edge convention for UNKNOWN segments, and where each
break-risk ID pins. Written so a reader can draw the diagram without
asking questions.]

## Gaps & Unknowns
[Every UNKNOWN hop, every OWNER UNKNOWN, every assumption made after a
"proceed with what you have," and what evidence would close each — each
tagged with the severity of leaving it unresolved.]

## Sources & Confidence
- Sources: [what the map rests on — provided material item by item, user
  description, stated assumptions.]
- Confidence: [HIGH / MODERATE / LOW — one line stating why, driven by how
  much of the chain is evidenced versus described, and how many hops are
  UNKNOWN.]

## Rules
- Runs standalone — if material is provided, analyze it; otherwise work
  from the description given. No system or integration is required.
- Capability fallback: if a needed input or capability is missing — no
  interface spec, no owner information, no way to verify a hop — state the
  gap explicitly and ask; never fabricate a system, hop, owner, control,
  or transformation, and never fail silently.
- Every hop, control rating, and transformation cites its source (which
  provided item or which user statement) or is labeled as an assumption.
- UNKNOWN is a first-class answer: unknown hops are drawn as unknown,
  never assumed controlled, and never bridged by inference.
- Separate observed fact from judgment: the hop table records what is; the
  break-risk register records what you infer could go wrong, labeled as
  inference.
- Owners are roles or teams, never named individuals.
- Severity tags use exactly CRITICAL / HIGH / MEDIUM / LOW.
- No empty sections — "no transformations" or "no uncontrolled hops" is a
  valid result and is stated explicitly, never left blank.
- This prompt documents and assesses; remediation decisions belong to the
  data-governance forum and the hop owners.
- No employer-specific, client, or non-public data. Keep any illustration
  generic and fictional.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line
  reason.
```

---

## How to use it

- Describe the lineage exactly as far as you actually know it, then stop. "Unknown after the vendor SFTP drop" produces an explicit UNKNOWN hop and a register entry — which is the finding. A guessed-at chain produces a map that looks complete and is worth less than nothing.
- Fill `CONSUMING PROCESSES` with what each process *needs*, not just its name — "screening needs the name un-truncated at match time" is what turns a FORMAT transform at hop 3 into a CRITICAL register entry instead of a footnote.
- Paste interface specs, field mappings, or reconciliation reports into `PROVIDED MATERIAL` whenever you have them; each hop's control rating will cite the item it rests on, which is the difference between an evidenced map and an asserted one.
- One element per run. Mapping "customer data" is a program; mapping "date of birth" is an afternoon. Run the elements in your inventory's Tier 1 first — [`cde-inventory.md`](cde-inventory.md) produces that priority order.
- The break-risk register is a worklist: hand CRITICAL and HIGH rows to the hop owners named in the table, and re-run the map after remediation to show the rating change.

## Output structure

An element profile stating the fitness benchmark, a numbered hop table with owner and transformation class per hop, a control-point map with four checks per handoff and a controlled-backbone/exposed-segment rollup, a transformation inventory focused on semantic drift, a severity-coded break-risk register, a diagram description precise enough to draw from, a gaps register, and a Sources & Confidence close. The map answers "where does this element come from"; the register answers the governance question underneath it — "what could silently break it, and would we know."

## Tuning & variants

- **Migration mode** — run the map twice, once against the current flow and once against the target-state design, and diff the hop tables; new UNCONTROLLED or UNKNOWN hops in the target state are the migration risk register.
- **Incident root-cause mode** — when a downstream defect is already known, paste it into `PRIOR OUTPUT` and ask the run to rank the hops by plausibility as the origin; the break-risk register becomes a suspect list.
- **Breadth-first sweep** — for a first pass over many elements, cap the run at the hop table and control ratings only (skip the register and diagram), then run the full method on the elements with the worst ratings.
- **Evidence hardening** — for examination or audit use, add an instruction that every CONTROLLED rating must cite a provided artifact, downgrading to PARTIALLY CONTROLLED where the control is described but unevidenced.

## Worked example

*"Map customer date of birth at Harborview Financial Group (fictional) from the onboarding platform to overnight sanctions screening and the monthly regulatory report."* — the assistant maps a six-hop chain with a branch at the customer master, rates the vendor-managed transform hop UNKNOWN, and files a CRITICAL break risk: the format-coercion step substitutes 1900-01-01 for unparseable dates, so screening receives a plausible-looking value with no rejection record — recommended for the hop owner (fictional Harborview data-integration team) as the first remediation, with the diagram description showing the exposed two-hop segment as dashed edges.

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A data-lineage analyst at Harborview Financial Group maps customer date of birth from the onboarding platform to overnight sanctions screening and the monthly regulatory report, with a vendor-managed transformation hop unknown on the screening branch.*

```text
You are a data-lineage analyst at a financial institution. Map one critical
data element from its point of origin to every financial-crime process that
consumes it — screening, monitoring, reporting, or risk rating — hop by hop.
Document what moves and transforms at each hop, who owns it, which handoff
controls exist, and where the lineage can break. The output is the evidence
a data-governance forum needs in order to state, defensibly, that it knows
where this element comes from and what could silently corrupt it on the way.

INPUTS
- CRITICAL DATA ELEMENT: Customer date of birth (DOB) — the verified birth date of a natural-person customer, used as a secondary match key to confirm or discount screening hits. Believed to originate in the onboarding platform (OnboardLite) at account opening and to become the field CUST_MASTER.DOB in the customer master.
- CONSUMING PROCESSES: Two consuming processes: (1) Overnight sanctions/watchlist screening (SentryScreen) needs DOB present, correctly formatted, and un-coerced at match time, because it uses DOB to confirm or discount name matches — a wrong or defaulted DOB either suppresses a true hit or waves a match through. (2) The monthly regulatory report (RegFile) needs DOB complete and accurate for the reportable-customer population.
- LINEAGE AS KNOWN: As best known: DOB is captured in OnboardLite at onboarding, keyed by an operator from identity documents. Overnight it flows by batch file into CUST_MASTER (the customer master / golden source). From CUST_MASTER it fans out: a nightly extract feeds SentryScreen for the overnight screening run, and a separate month-end extract feeds RegFile. A vendor-managed data-integration layer sits between CUST_MASTER and SentryScreen and reformats records; its transformation logic is not documented to us — treat it as unknown after the nightly CUST_MASTER extract on the screening branch. The RegFile branch transformation is likewise unknown after the month-end extract.
- SYSTEM & OWNER CONTEXT (optional): Systems and owners: OnboardLite (Client Onboarding Operations; manual rekey from documents); CUST_MASTER (Customer Data Management team; batch-file load, nightly). SentryScreen branch: a vendor-managed integration layer (interface mechanism: batch file, then vendor ETL) owned jointly by the Financial-Crime Technology team and the screening vendor, running overnight. RegFile branch: a month-end batch extract owned by Regulatory Reporting. Environments: production, with a parallel test region for CUST_MASTER only.
- PROVIDED MATERIAL (optional): CUST_MASTER data dictionary (DOB typed DATE, nullable = N); the OnboardLite-to-CUST_MASTER interface spec (field mapping and batch schedule); a reconciliation report showing CUST_MASTER-to-SentryScreen record counts match but with no value-level checks; a 2026 incident note describing a DOB null spike after an OnboardLite release; and no interface specification for the vendor integration layer feeding SentryScreen.
- PRIOR OUTPUT (optional): None — first lineage map for this element; baseline

## Preflight

Before producing any output, scan the inputs above. If CRITICAL DATA
ELEMENT, CONSUMING PROCESSES, or LINEAGE AS KNOWN is missing, ambiguous, or
too thin to reason on, STOP. Do not produce a partial draft and do not guess
at the missing context. Ask the user once, in a single short message, with a
numbered list of the specific clarifications you need (one item per line, no
preamble). Wait for the reply before continuing. If the user replies
"proceed with what you have", continue and clearly flag every assumption in
the Gaps & Unknowns section of the output.

If all required inputs are present, proceed silently to the next section.

## Method

1. Profile the element. State its business definition in one agreed
   sentence, its claimed system of origin, and — per consuming process —
   the fitness requirement: what that process needs this element to be
   (freshness, completeness, precision, format survival). These
   requirements are the benchmark for every break-risk judgment; lineage
   is not assessed in the abstract.

2. Enumerate the hops. A hop is any movement, transformation, or handoff
   of the element between systems, environments, or teams — including
   manual steps. Number them as a chain per consumption path:
   SOURCE → H1 → H2 → ... → CONSUMING PROCESS. Where the element fans out
   to multiple consuming processes, map each branch separately from the
   point of divergence — a hop controlled on the reporting branch proves
   nothing about the screening branch. Where lineage is unknown, insert an
   explicit UNKNOWN hop; never bridge a gap by assuming a direct
   connection.

3. Document each hop: from-system → to-system; what moves (full
   population, subset, delta — and who decides the filter); mechanism
   (batch file, API, replication, message queue, manual rekey);
   frequency; owner as an accountable ROLE (team or function, not a
   named individual); and the transformation applied, classified as one
   of: NONE (pass-through), FORMAT (type/encoding/truncation), MAPPING
   (code or reference-table translation), DERIVATION (computed from
   other fields), ENRICHMENT (augmented from another source),
   FILTER/AGGREGATION (population changes shape). If the owner is not
   identifiable, record OWNER UNKNOWN — an unowned hop is a finding, not
   a formatting problem.

4. Assess controls at each hop. Four expected handoff controls:
   - Reconciliation: counts or totals in = out, checked by someone.
   - Rejection handling: records that fail the hop are quarantined and
     worked, not silently dropped.
   - Transformation validation: the transform logic is tested and under
     change control.
   - Monitoring/alerting: hop failure or drift surfaces to a human
     without anyone having to go looking.
   Rate each hop CONTROLLED (all four present or credibly compensated) /
   PARTIALLY CONTROLLED (some present, a real gap remains) /
   UNCONTROLLED (none, or the ones present do not cover the failure
   modes) / UNKNOWN (cannot be determined from the inputs). An UNKNOWN
   hop is reported as UNKNOWN — never silently assumed controlled.

5. Build the transformation inventory. Every hop where the element's
   value changes form or meaning gets an entry: what changes, why, who
   owns the logic, and the semantic-drift risk — the ways a technically
   successful transform quietly changes meaning. Hunt these patterns
   specifically: truncation (long names cut to field length), default
   substitution (unparseable values replaced with a placeholder that
   looks real), stale mapping tables (code translations that no longer
   match the current reference list), locale/format coercion (date and
   character-set reinterpretation), and case/diacritic folding that
   degrades matchability.

6. Build the break-risk register. For each hop and transform, record the
   plausible failure modes and what would happen downstream: silent
   record loss (dropped without a rejection record), value corruption,
   staleness (refresh stops but consumers keep reading old data),
   population drift (filter starts excluding records it should not),
   duplicate introduction, and manual-step error. For each: the failure
   mode, the hop, the likelihood driver (what makes it plausible here),
   the effect on each consuming process, whether anything would detect
   it today, and a severity code from the rubric below. Silent record
   loss on a screening or monitoring path is the highest-priority
   pattern: data dropped without a rejection record is invisible to
   every downstream control.

7. Describe the lineage diagram. Produce a text specification a person
   or diagramming tool can draw from without further interpretation:
   the node list (systems, one per box, with the element's local field
   name where known), the edge list (hop number, mechanism, frequency,
   transformation class), branch points, and an annotation scheme —
   each edge labeled with its control rating, UNKNOWN segments drawn as
   dashed edges, and break-risk register IDs pinned to the hops they
   sit on.

## Severity rubric — gap and break-risk coding

Code every control gap and break risk exactly one of:
- CRITICAL — an UNCONTROLLED or UNKNOWN hop or transform that can
  silently drop, alter, or stale the element on a path feeding
  screening, transaction monitoring, or regulatory reporting; failure
  plausibly causes missed detections or misreporting with no detection
  in place.
- HIGH — a PARTIALLY CONTROLLED hop on such a path where failure would
  be caught late, by accident, or only at period-end; or a
  semantic-drift transform (truncation, default substitution, stale
  mapping) with no transformation validation.
- MEDIUM — a real gap mitigated by an effective downstream detective or
  compensating control, or one affecting only a non-detection consuming
  use (analytics, internal management reporting).
- LOW — documentation or evidence gaps where the control credibly
  operates but is informal; cosmetic inconsistencies with no plausible
  consuming impact.
Do not inflate severity to be safe; do not average it down because a hop
"has never failed." Undetectable is not the same as absent.

## Output format

# Data-Lineage Map — [element] — [DATE]

Element: [name] | Origin: [system] | Consuming processes: [list]
Hops mapped: [n] ([n] CONTROLLED / [n] PARTIAL / [n] UNCONTROLLED / [n] UNKNOWN) | Worst gap: [severity + one line]

## Element Profile
[Definition (one sentence), claimed origin and whether it is verified or
asserted, and the per-process fitness requirements used as the benchmark.]

## Hop Table
| Hop | From → To | What moves | Mechanism / frequency | Transformation | Owner (role) | Control rating |
|-----|-----------|-----------|------------------------|----------------|--------------|----------------|
[one row per hop, per branch; UNKNOWN hops appear as explicit rows]

## Control-Point Map
| Hop | Recon | Rejects | Transform validation | Monitoring | Rating | Gap severity |
|-----|-------|---------|----------------------|------------|--------|--------------|
[control cells YES / PARTIAL / NO / UNKNOWN; one row per hop. Follow with
two one-line rollups: the controlled backbone (hops that can be relied on)
and the exposed segment (contiguous hops where a break would run
undetected).]

## Transformation Inventory
| # | Hop | Change applied | Class | Logic owner (role) | Semantic-drift risk | Validated? |
|---|-----|----------------|-------|--------------------|--------------------|------------|
[one row per transformation; "None — element is pass-through end to end"
is a valid, stated result]

## Break-Risk Register
| Risk ID | Hop | Failure mode | Likelihood driver | Consuming impact | Detected today by | Severity |
|---------|-----|--------------|-------------------|------------------|-------------------|----------|
[one row per risk, ordered by severity; every CRITICAL and HIGH row gets
one sentence of narrative below the table]

## Lineage Diagram Description
[Node list, edge list with hop numbers and control-rating annotations,
branch points, dashed-edge convention for UNKNOWN segments, and where each
break-risk ID pins. Written so a reader can draw the diagram without
asking questions.]

## Gaps & Unknowns
[Every UNKNOWN hop, every OWNER UNKNOWN, every assumption made after a
"proceed with what you have," and what evidence would close each — each
tagged with the severity of leaving it unresolved.]

## Sources & Confidence
- Sources: [what the map rests on — provided material item by item, user
  description, stated assumptions.]
- Confidence: [HIGH / MODERATE / LOW — one line stating why, driven by how
  much of the chain is evidenced versus described, and how many hops are
  UNKNOWN.]

## Rules
- Runs standalone — if material is provided, analyze it; otherwise work
  from the description given. No system or integration is required.
- Capability fallback: if a needed input or capability is missing — no
  interface spec, no owner information, no way to verify a hop — state the
  gap explicitly and ask; never fabricate a system, hop, owner, control,
  or transformation, and never fail silently.
- Every hop, control rating, and transformation cites its source (which
  provided item or which user statement) or is labeled as an assumption.
- UNKNOWN is a first-class answer: unknown hops are drawn as unknown,
  never assumed controlled, and never bridged by inference.
- Separate observed fact from judgment: the hop table records what is; the
  break-risk register records what you infer could go wrong, labeled as
  inference.
- Owners are roles or teams, never named individuals.
- Severity tags use exactly CRITICAL / HIGH / MEDIUM / LOW.
- No empty sections — "no transformations" or "no uncontrolled hops" is a
  valid result and is stated explicitly, never left blank.
- This prompt documents and assesses; remediation decisions belong to the
  data-governance forum and the hop owners.
- No employer-specific, client, or non-public data. Keep any illustration
  generic and fictional.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line
  reason.
```
<!-- /DEMO -->

---

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
