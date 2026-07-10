# Adverse-Media Source Library & Sourcing Methodology

A focused whitelist and sourcing method for negative-news screening — the source layer that
sits under the [scoring engine](README.md). The engine dispositions hits you already have;
*this* document is about where credible hits come from, how far to trust each, and what to do
next with each tier. The cross-workflow master is
[`../../reference/osint-source-library.md`](../../reference/osint-source-library.md).

> Public sources only. Nothing here is a licensed feed (Dow Jones, LexisNexis, Refinitiv) or
> employer-specific. Those commercial tools sit *on top of* this free baseline; the sourcing
> discipline below is identical whichever you use.

---

## The one rule that governs everything

**Prefer the primary source of the underlying event over the reporting about it.** A DOJ
indictment is stronger than a news article summarizing the indictment; a court judgment is
stronger than a blog citing it. Reporting is for corroboration and context — the finding
should rest on the primary act.

---

## Tiered source whitelist

### Tier 1 — primary / authoritative (a finding may rest here, once identity is resolved)

| Source | URL | Establishes |
|--------|-----|-------------|
| DOJ press & enforcement | `justice.gov/news` | Charges, indictments, pleas, convictions |
| SEC press & litigation | `sec.gov/news/pressreleases`, `sec.gov/litigation` | Securities enforcement (civil) |
| CFTC enforcement | `cftc.gov` | Derivatives/commodities enforcement |
| FinCEN news room | `fincen.gov/news-room` | AML enforcement, advisories, penalties |
| FCA / FINRA / other regulators | `fca.org.uk/news`, `finra.org` | Non-US and SRO enforcement |
| Court dockets & judgments | see [master §5](../../reference/osint-source-library.md#5-court-records--litigation) | The legal action itself; allegation vs. finding |
| OFAC / sanctions lists | see [master §1](../../reference/osint-source-library.md#1-sanctions--watchlist-screening) | Designation (a distinct, strict-liability track) |

### Tier 2 — reputable secondary (a strong lead; corroborate to a T1 primary)

| Source | URL | Best for |
|--------|-----|----------|
| Established newswires | Reuters, AP, Bloomberg, FT | Timely, accountable reporting |
| Investigative consortia | ICIJ `icij.org`, OCCRP `occrp.org`, bellingcat | Structured, sourced investigations |
| GDELT event index | `gdeltproject.org` | Screening news events at scale; timelines |
| OpenSanctions | `opensanctions.org` | Cross-referencing subjects to lists/PEP data |

### Tier 3 — open / user-generated (a lead only; never a finding alone)

Search engines, wikis, forums, social media, company-review sites. Use for discovery and to
find the T1/T2 source — cite the source it leads you to, not the aggregator.

---

## Sourcing method (per subject)

1. **Fix identity first.** Collect the identifiers you will match on (full legal name and
   known variants, date of birth, jurisdiction, entity registration number, role). Adverse
   media without identity resolution is noise.
2. **Sweep primary sources.** Query the Tier-1 regulator and court sources for the name and
   its variants. Anything here is the strongest possible hit.
3. **Sweep reputable secondary.** Newswire and investigative outlets for corroboration and for
   events the regulators have not (yet) acted on.
4. **Use open search for leads only**, then chase each lead back to a T1/T2 source.
5. **Classify every hit** on the four axes the engine scores — record them so the disposition
   is reproducible:
   - **Right party?** Does an identifier tie the article to *your* subject, or only the name?
   - **Adverse?** Is the subject the wrongdoer — not the victim, witness, expert, or namesake?
   - **Serious?** Predicate relevance (fraud, ML, corruption, sanctions, trafficking) vs. minor.
   - **Recent / material?** Weigh stale, minor, or resolved matters down; live, serious ones up.

---

## Action-item scoping — what each outcome triggers

| Screening outcome | Action |
|-------------------|--------|
| **Confirmed adverse, serious, recent, right party (T1)** | Escalate. Document the primary source `[S#]`, open or continue an EDD or investigation, and consider SAR relevance (a human decides the filing). |
| **Right party but stale / minor / resolved** | Record with rationale; usually monitor rather than escalate. Note the step-down reason. |
| **Adverse but identity unresolved (name-only)** | Do **not** clear and do **not** escalate on the name alone — seek an identifier (DOB, registration, jurisdiction). This is the irreducible common-name band the engine routes to a human. |
| **Not adverse (subject is victim/witness), or not the subject** | Clear with the disqualifying reason recorded (`wrong_entity`, `not_adverse`, `low_role`). |
| **Sanctions/PEP signal surfaced in the sweep** | Route to the dedicated track — [sanctions](../sanctions-name-screening/) / [PEP](../pep-screening/) — not the adverse-media disposition. |

Every escalation and every clear carries its `[S#]` provenance and its axis scores, so a
reviewer can re-walk the decision. Nothing here off-boards, files, or designates on its own —
a qualified human decides.
