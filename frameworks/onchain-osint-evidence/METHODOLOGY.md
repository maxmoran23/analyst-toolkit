# Methodology — On-Chain OSINT Evidence Engine

The regulator-facing specification of the collection, normalization, and evidencing
logic. Every field, threshold, and named rule below exists as a named construct in
[`engine.py`](engine.py) and [`../_lib/provenance.py`](../_lib/provenance.py); those
files are the executable form. Evidence:
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md). Shared governance:
[`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** Investigators already use public block explorers as an
> open-source intelligence source — but by hand: screenshots, copied hashes, notes.
> That evidence rarely survives scrutiny, because nobody can prove where a number
> came from, when it was pulled, or that it was not altered. This spec defines the
> disciplined version: every fact keeps its source link, retrieval time, and a
> cryptographic fingerprint of the exact bytes it came from; the totals must add up
> to the source exactly; running it twice produces the identical document; and the
> tool flags patterns (like spam dust) by name without ever claiming to know who
> owns an address.

---

## 1. Why this exists

Public block-explorer data is legitimate open-source intelligence for a
financial-crime organization: it corroborates vendor findings, supports requests
for information, and documents activity around an address that surfaced in a case.
Done by hand, the workflow has three defects this engine removes: **lost
provenance** (no source URI / retrieval time / integrity proof per fact),
**silent arithmetic errors** (records dropped or double-counted across paginated
pages, token amounts scaled at the wrong decimals), and **attribution creep**
(notes that quietly treat an address as a person). The engine is the disciplined
form: provenance is structural, reconciliation is exact and machine-checked, and
the output language is built to not over-claim.

## 2. The provenance model

Every emitted fact is an `EvidenceFact` carrying five mandatory provenance fields
alongside its value (`_lib/provenance.py`):

| Field | Meaning |
|---|---|
| `fact_type` | What kind of statement: `address_summary`, `native_transaction`, `token_transfer`, `counterparty_rollup`, `flow_summary`, `structural_observation`. |
| `source_uri` | The endpoint the content was retrieved from; for derived facts, all contributing capture URIs joined. |
| `retrieved_at_utc` | The capture time (never the run time). |
| `content_sha256` | Digest of the raw source bytes — for derived facts, an order-independent combined digest of every contributing capture, so the fact traces to the exact bytes it was computed from. |
| `origin_id` | Locator of the originating element (`tx:<hash>`, `address:<addr>`, `counterparty:<addr>`, `observation:<id>`). |

A fact missing any field is incomplete, and the validation harness fails the build
if completeness is below 100% (`PROVENANCE_FLOOR = 1.0`). Rationale: an
unprovenance'd fact is an assertion, not evidence, and one is enough to taint an
annex.

## 3. Sources and modes

Inputs are **capture sets** — explorer API payloads plus a capture manifest
recording each payload's URL and retrieval time (the same record a disciplined
manual capture keeps). Two payload families are parsed:

- **EVM, Blockscout-style module API** — `balance`, paginated `txlist`, paginated
  `tokentx`.
- **BTC, mempool-style REST** — address summary (`chain_stats`) and paginated
  transaction pages (`vin`/`vout`).

**Fixture mode is the default and the only mode CI exercises**: the engine reads
capture files from disk; no network exists anywhere in the validation path.
**Live mode is optional**: `urllib` against a **user-supplied** explorer base URL —
there is no default endpoint, so nothing here hammers any real service, and the
operator owns the chosen source's usage terms. Any live failure (offline, timeout,
HTTP error, malformed body) returns `None` — graceful degrade, never an exception —
which the harness verifies offline.

## 4. Normalization rules (in firing order)

1. **Hash the capture first.** `content_sha256` is computed over the raw response
   bytes before any parsing, so every downstream fact can be tied to unaltered
   source content.
2. **Case-fold EVM address identity.** Explorers render the same address in
   checksummed and lowercase forms; identity is lowercased hex, so one counterparty
   never splits into several. (EIP-55 checksum *validation* is out of scope — a
   stated limitation.) BTC addresses are case-significant and used verbatim.
3. **Keep amounts exact.** Values stay integers end-to-end (wei, sats, raw token
   units); display quantities are produced by exact integer scaling at the
   token's **declared** decimals (`scale_amount`) — never floats. The fixture
   population plants 6/8/18-decimal tokens and zero-value transfers to prove this
   path.
4. **Deduplicate on a provable named cause ONLY.** Offset pagination routinely
   repeats a boundary record on the next page. The engine removes a record only
   when it is an identical repeat — native transactions by hash, token transfers
   by full record identity (the module API exposes no per-transfer log index, so
   the full record IS the identity; limitation stated). This is the package's only
   automated removal, mirroring the pillar's named-cause discipline: it never
   drops a distinct record, and the validation proves planted duplicates are
   removed exactly once.
5. **Classify direction.** `in` / `out` / `self` per record against the folded
   subject address. Flow semantics are per-chain and stated: EVM directional sums
   exclude self-transfers (tracked separately); BTC sums are UTXO funded/spent
   totals, which include self-spends and must tie **exactly** to the explorer's
   own `chain_stats` — an internal cross-source consistency check the harness
   enforces.

## 5. Counterparty rollup and flow summary

Per counterparty (case-folded, excluding self): native transaction count, value in,
value out, token-transfer count, first/last seen (UTC). Per address: directional
counts and sums, token-transfer counts (with zero-value and dust called out),
distinct counterparty count, and duplicates removed. Both are emitted as derived
facts with combined-digest provenance (§2) and rendered in the annex; the full
rollup goes to `counterparties.csv`.

## 6. Structural observations (named rules, in firing order)

Observations flag patterns worth an investigator's attention. Three properties are
non-negotiable: each fires on a **named rule with a stated threshold**, each cites
the transactions behind it, and **none is an attribution** — an address is not an
identity, and no rule here concludes ownership, purpose, or wrongdoing.

1. **OBS_DUST_SPAM** — at least `dust_spam_min_count` (10) inbound dust transfers:
   EVM token transfers at/below 10^-`dust_token_exp` units (0.001, including
   zero-value); BTC inbound outputs at/below `dust_btc_sats_max` (1,000 sats).
   Rationale: the unsolicited dust/airdrop-spam pattern is sent BY third parties
   and says nothing about the address holder — flagging it prevents spam from
   polluting flow analysis or being misread as real activity.
2. **OBS_SELF_TRANSFER** — at least `self_transfer_min_count` (1) transaction from
   the address to itself. Rationale: consistent with wallet management or
   consolidation; benign explanations exist, so it is context, not suspicion.
3. **OBS_HIGH_FREQ_SAME_COUNTERPARTY** — any single counterparty with at least
   `high_freq_min_tx` (25) native transactions. Rationale: a concentrated
   bilateral relationship (exchange deposit path, payment channel, routine
   business) that shapes how the flows should be read — identifying WHICH requires
   evidence this engine does not claim to have.

The engine assembles evidence and routes it to a human. It never auto-blocks,
auto-files, or auto-approves; there is no auto-clear path because there is no
disposition — every pack goes to an investigator.

## 7. Reconciliation discipline

Annex totals must equal source-capture totals **exactly** — transaction counts,
per-direction value sums, token-transfer counts, counterparty counts — with zero
records dropped and zero double-counted, pagination handled. The validation harness
enforces this against constructed ground truth per address, plus the BTC
summary tie-out (§4.5), as a build gate with tolerance 0. Rationale: an evidence
annex that is even one record off is not evidence; "approximately reconciled" is
not a category this artifact recognizes.

## 8. Determinism

The same captures produce byte-identical annex, facts CSV, and counterparty CSV —
enforced by digest comparison across repeat runs. The run timestamp exists only in
`evidence-manifest.json`, which also records the sha256 of each rendered artifact
so a reviewer can verify the documents they hold are the ones the manifest
describes. Rationale: deterministic output is what makes independent reproduction
of an evidence pack meaningful.

## 9. Governance and boundaries

Mapped to public guidance per [`../GOVERNANCE.md`](../GOVERNANCE.md) — SR 11-7 /
OCC 2011-12 (conceptual soundness: this spec; outcomes analysis: the harness and
committed evidence; ongoing monitoring: the gates and multi-seed runs; limitations:
§10), FFIEC expectations that tooling logic be documented and understood, and
**FATF Recommendations 15/16** for the virtual-asset context. Boundaries:

- **Public sources only.** The engine consumes public explorer data; nothing here
  accesses non-public information.
- **No attribution.** Address does not equal identity. Cluster attribution and
  entity identification are the province of chain-analytics vendors and human
  investigation; this engine **complements — never replaces —** those
  (vendor-independence is the point: it evidences the public layer regardless of
  which vendor sits alongside).
- **Human decisions.** Escalation, filing, and account actions are documented human
  decisions taken outside this tool.

## 10. Limitations

- Synthetic fixtures model the shape and failure modes of explorer payloads, not
  live-data messiness; validate live captures against the target explorer's
  current schema before reliance.
- Token metadata (symbol, name, decimals) is recorded **as claimed by the source**;
  a token contract can claim any symbol, so nothing here verifies a token's
  legitimacy — a known spam/impersonation vector.
- The module API's lack of a per-transfer log index means token-transfer identity
  is the full record; a genuinely identical duplicate transfer inside one
  transaction would be conflated (not observed in practice for distinct transfers,
  which differ in value or party).
- The balance / chain-stats summary is a point-in-time claim by the explorer,
  reported (with provenance) rather than derived; only BTC offers an internal
  tie-out to parsed transactions.
- A capture window is partial by nature: the pack evidences what the source
  returned, not the address's complete history.
