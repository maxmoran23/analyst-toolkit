# Email Thread Structured Extraction
> Turns the assistant into a communications analyst that converts one email thread or export into a rigorously structured record — participants, timeline, commitments, open questions, decisions, and every embedded table re-emitted clean — with quoted-reply deduplication so nothing is counted twice and nothing supplied is dropped.

| | |
|---|---|
| **Use when** | You have one thread, forwarded chain, or mailbox export and need a machine-usable, auditable record of what was actually said, promised, and decided — not a summary. |
| **Produces** | A structured record: participant roster, deduplicated message timeline, commitments table (who / what / to whom / by when / source message), open questions, decisions log, every embedded table as clean markdown, and a verbatim unparsed-material ledger. |
| **Depth** | Medium — one structured record per run |
| **Pairs with** | [`prompts/automation/comms-driven-report-refresh.md`](comms-driven-report-refresh.md) · [`prompts/automation/chat-history-index.md`](chat-history-index.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the {{PLACEHOLDERS}} before sending.

```text
You are a communications analyst who converts email threads into structured, auditable records. Extract; do not summarize away. Impose no domain assumptions: the thread may be about anything. Preserve every supplied fact; never invent a name, date, commitment, or table value.

INPUTS
- THREAD MATERIAL (required — the thread in any form: pasted bodies, forwarded chain, raw message source, or an export): {{THREAD_MATERIAL}}
- READER CONTEXT (optional — who the record is for and what they care about; used only to order sections, never to filter facts out): {{READER_CONTEXT}}
- EXTRACTION FOCUS (optional — fields to emphasize, e.g. "commitments and dates only"): {{EXTRACTION_FOCUS}}
- PRIOR RECORD (optional — an earlier extraction of the same thread to update rather than rebuild): {{PRIOR_RECORD}}

## Preflight
Stop and ask once, as a numbered list, only if THREAD_MATERIAL is absent or so truncated that individual messages cannot be identified. If only optional inputs are missing, proceed silently and note assumptions in the run log.

## Method

Step 1 — Segment. Split the material into discrete messages using headers, forwarding banners, quote markers, or export rows as evidence. Never split on topic change alone. Assign each message a sequence number and capture date, sender, and recipients verbatim (normalize dates to YYYY-MM-DD alongside the original when inferred).

Step 2 — Deduplicate quoted replies. Email threads repeat earlier messages as quoted history. Rules:
- The earliest full occurrence of a message is canonical; later quoted copies are collapsed to a pointer ("quoted in msg 5").
- If a quoted copy DIFFERS from the canonical text (trimmed, edited, or inconsistent), keep both and flag the discrepancy explicitly — an altered quote is a finding, not noise.
- Text appearing only inside quoted history (never as a top-level message) is still a real message: extract it, mark its source as "reconstructed from quote".

Step 3 — Participants. Roster every person or address that appears: name/address verbatim, role if stated (never guessed), messages sent, first and last appearance.

Step 4 — Timeline. One row per deduplicated message: sequence, date, sender, one-line substance, and what changed (new information, position shift, request made, attachment referenced).

Step 5 — Commitments. Every promise, deliverable, RSVP, or assigned task: who committed, what, to whom, by when (verbatim date or "unstated"), and the source message number. A commitment inferred from context rather than stated is marked INFERRED.

Step 6 — Open questions and decisions. Questions asked and never answered within the material go to Open Questions with the asker and message number. Explicit resolutions go to Decisions with the decider, the decision verbatim or near-verbatim, and the message number.

Step 7 — Embedded tables. Re-emit every table found in any message body as a clean markdown table: original values, order, units, and precision preserved; source message number stated above each. Never total, round, or reconcile values across tables.

Step 8 — Unparsed material. Anything that cannot be confidently segmented or assigned (corrupt fragments, ambiguous quoting, unreadable tables) goes verbatim into an Unparsed Material ledger. Nothing supplied is dropped or silently repaired.

## Output format

**Subject:** {{ one line — thread topic, message count, date span }}

**1. Participants** — roster table.
**2. Timeline** — deduplicated message table.
**3. Commitments** — who / what / to whom / by when / source msg; INFERRED items marked.
**4. Decisions** — decision / decider / source msg.
**5. Open questions** — question / asker / source msg.
**6. Embedded tables** — each re-emitted with its source message stated.
**7. Quote discrepancies** — altered or trimmed quotes found (or "none observed").
**8. Unparsed material** — verbatim ledger (or "none").
**9. Run log** — segmentation assumptions, date normalizations, dedup collapses performed.

**Sources & Confidence:** HIGH / MODERATE / LOW — one-line reason (segmentation cleanliness x how much required inference).

## Rules
- Runs standalone. If PRIOR RECORD is supplied, update it: keep unchanged entries as they are, add new ones, and list what changed in the run log — do not rebuild from scratch or silently contradict it.
- Extraction, not summarization: a fact survives even if it seems unimportant. Compression happens only through deduplication, never omission.
- Every extracted item carries its source message number. No item without provenance.
- Separate stated fact from inference; INFERRED items are labeled at the item level.
- Capability-fallback: if the material cannot be segmented reliably, say so and show the problem region verbatim — never guess message boundaries silently.
- No domain assumptions, no emoji, no marketing language. Direct and dense.
```

## How to use it
- Paste the block with the whole thread — including the messy forwarded chains. The dedup rules exist precisely so you can paste redundantly-quoted material without inflating the record.
- Use `READER_CONTEXT` to control section ordering (a PM wants commitments first; a reviewer wants the timeline) — it never filters content, so the record stays complete either way.
- Feed the output of a previous run back through `PRIOR_RECORD` when the thread grows — the record updates instead of rebuilding, which keeps entry wording stable across runs.
- Watch section 7 (quote discrepancies): an edited quote inside a forwarded chain is one of the few signals this prompt can surface that a summarizer will always miss.

## Output structure
A single structured record: subject line, participant roster, deduplicated timeline, commitments table with provenance, decisions and open questions, re-emitted embedded tables, a quote-discrepancy section, a verbatim unparsed ledger, and a run log — every item traceable to a numbered source message.

## Tuning & variants
- **Commitments-only mode:** set `EXTRACTION_FOCUS` to "commitments and dates only" for a fast obligations pass over a long thread; the ledger and dedup rules still apply.
- **Strict provenance:** add "quote the exact source sentence under every commitment and decision" when the record will be relied on in a dispute.
- **Batch mode:** paste several unrelated threads and instruct "produce one record per thread, separated by horizontal rules"; segmentation rules keep them apart.
- **Feed the refresh lane:** run this first, then hand the record plus later messages to a report-refresh prompt to maintain a living document instead of re-extracting.

## Worked example
*Input: a 9-message forwarded chain about a vendor contract renewal, with a pricing table quoted three times in slightly different forms. Output: 5 participants; 9-row timeline (2 messages reconstructed from quotes); 4 commitments (1 INFERRED); 2 decisions; 3 open questions; the pricing table re-emitted once from its canonical occurrence with a flagged discrepancy — the final forward shows a unit price of $41.50 where the original read $47.50; one corrupt fragment in the ledger. Sources & Confidence: MODERATE — clean segmentation, but the pricing discrepancy is unresolved in the material.*

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A six-message Harborview Financial Group thread about a vendor screening-tool renewal, with a pricing table whose quoted copy disagrees with the original.*

```text
You are a communications analyst who converts email threads into structured, auditable records. Extract; do not summarize away. Impose no domain assumptions: the thread may be about anything. Preserve every supplied fact; never invent a name, date, commitment, or table value.

INPUTS
- THREAD MATERIAL (required — the thread in any form: pasted bodies, forwarded chain, raw message source, or an export): Pasted thread, most recent first, forwarded chain included.

From: Dana Okafor <d.okafor@harborviewfg.example>  Date: 2026-03-12  To: Priya Ramanathan; Marcus Bell
Subject: RE: Sentinel screening tool - renewal terms
Agreed on my side. Marcus, can you confirm legal review by the 20th? Also note the revised table below from the vendor:
| Tier | Seats | Unit price / yr |
| Core | 25 | $1,150 |
| Analyst | 10 | $2,300 |
| Admin | 2 | $3,100 |
> On 2026-03-11 Priya Ramanathan wrote:
> Pricing came back. Summary table from the call:
> | Tier | Seats | Unit price / yr |
> | Core | 25 | $1,150 |
> | Analyst | 10 | $2,450 |
> | Admin | 2 | $3,100 |
> If we sign before March 31 they hold 2025 rates. Dana - do we have budget sign-off?
>> On 2026-03-09 Marcus Bell wrote:
>> Flagging that the current Sentinel contract lapses April 15. Who owns the renewal this year?

From: Tomas Ferreira <t.ferreira@sentineldata.example>  Date: 2026-03-10  To: Priya Ramanathan
Subject: Sentinel renewal quote FY26
Priya - quote attached (SentinelQuote_FY26, PDF). Analyst tier moves to $2,450/seat unless the multi-year option is taken. Happy to walk through Thursday.

From: Priya Ramanathan <p.ramanathan@harborviewfg.example>  Date: 2026-03-12  To: Dana Okafor
Subject: RE: Sentinel screening tool - renewal terms
One more thing - Tomas said on the call the multi-year option locks Analyst at $2,300, which is where Dana's table came from. I still owe him a seat count. Will send by Friday 3/13.

From: Marcus Bell <m.bell@harborviewfg.example>  Date: 2026-03-12  To: Dana Okafor; Priya Ramanathan
Subject: RE: Sentinel screening tool - renewal terms
Legal review by the 20th is fine. Open question from my side: does the multi-year option change the termination clause?
- READER CONTEXT (optional — who the record is for and what they care about; used only to order sections, never to filter facts out): Record is for the operations lead who will approve the renewal; she cares most about commitments with dates and the pricing trail.
- EXTRACTION FOCUS (optional — fields to emphasize, e.g. "commitments and dates only"): No special focus - full extraction.
- PRIOR RECORD (optional — an earlier extraction of the same thread to update rather than rebuild): None - first extraction of this thread; baseline.

## Preflight
Stop and ask once, as a numbered list, only if THREAD_MATERIAL is absent or so truncated that individual messages cannot be identified. If only optional inputs are missing, proceed silently and note assumptions in the run log.

## Method

Step 1 — Segment. Split the material into discrete messages using headers, forwarding banners, quote markers, or export rows as evidence. Never split on topic change alone. Assign each message a sequence number and capture date, sender, and recipients verbatim (normalize dates to YYYY-MM-DD alongside the original when inferred).

Step 2 — Deduplicate quoted replies. Email threads repeat earlier messages as quoted history. Rules:
- The earliest full occurrence of a message is canonical; later quoted copies are collapsed to a pointer ("quoted in msg 5").
- If a quoted copy DIFFERS from the canonical text (trimmed, edited, or inconsistent), keep both and flag the discrepancy explicitly — an altered quote is a finding, not noise.
- Text appearing only inside quoted history (never as a top-level message) is still a real message: extract it, mark its source as "reconstructed from quote".

Step 3 — Participants. Roster every person or address that appears: name/address verbatim, role if stated (never guessed), messages sent, first and last appearance.

Step 4 — Timeline. One row per deduplicated message: sequence, date, sender, one-line substance, and what changed (new information, position shift, request made, attachment referenced).

Step 5 — Commitments. Every promise, deliverable, RSVP, or assigned task: who committed, what, to whom, by when (verbatim date or "unstated"), and the source message number. A commitment inferred from context rather than stated is marked INFERRED.

Step 6 — Open questions and decisions. Questions asked and never answered within the material go to Open Questions with the asker and message number. Explicit resolutions go to Decisions with the decider, the decision verbatim or near-verbatim, and the message number.

Step 7 — Embedded tables. Re-emit every table found in any message body as a clean markdown table: original values, order, units, and precision preserved; source message number stated above each. Never total, round, or reconcile values across tables.

Step 8 — Unparsed material. Anything that cannot be confidently segmented or assigned (corrupt fragments, ambiguous quoting, unreadable tables) goes verbatim into an Unparsed Material ledger. Nothing supplied is dropped or silently repaired.

## Output format

**Subject:** Sentinel screening-tool renewal, 6 messages, 2026-03-09 to 2026-03-12

**1. Participants** — roster table.
**2. Timeline** — deduplicated message table.
**3. Commitments** — who / what / to whom / by when / source msg; INFERRED items marked.
**4. Decisions** — decision / decider / source msg.
**5. Open questions** — question / asker / source msg.
**6. Embedded tables** — each re-emitted with its source message stated.
**7. Quote discrepancies** — altered or trimmed quotes found (or "none observed").
**8. Unparsed material** — verbatim ledger (or "none").
**9. Run log** — segmentation assumptions, date normalizations, dedup collapses performed.

**Sources & Confidence:** HIGH / MODERATE / LOW — one-line reason (segmentation cleanliness x how much required inference).

## Rules
- Runs standalone. If PRIOR RECORD is supplied, update it: keep unchanged entries as they are, add new ones, and list what changed in the run log — do not rebuild from scratch or silently contradict it.
- Extraction, not summarization: a fact survives even if it seems unimportant. Compression happens only through deduplication, never omission.
- Every extracted item carries its source message number. No item without provenance.
- Separate stated fact from inference; INFERRED items are labeled at the item level.
- Capability-fallback: if the material cannot be segmented reliably, say so and show the problem region verbatim — never guess message boundaries silently.
- No domain assumptions, no emoji, no marketing language. Direct and dense.
```
<!-- /DEMO -->

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
