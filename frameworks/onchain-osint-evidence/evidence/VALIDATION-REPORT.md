# Validation Report — On-Chain OSINT Evidence Framework

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the engine over a seeded population of synthetic explorer fixtures (Blockscout-style EVM and mempool-style BTC payloads) with known ground truth. No real address, transaction, or explorer is represented. Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 400 addresses (265 EVM / 135 BTC) · 54,915 unique transaction records (55,147 source records incl. planted duplicates) · git `d2f4ef1` · 2026-07-10 05:09 UTC

**Headline:** provenance completeness **100.0%** across **61,126 facts** (floor 100%), reconciliation **exact** — **0 dropped / 0 duplicated** (232 pagination duplicates planted, 232 removed), rendered evidence **byte-identical across repeat runs** (digest `14fbbfbb6c3c8058`).

## 1. What this validates
The engine turns public block-explorer payloads into an investigation-grade evidence pack: every fact provenance-stamped (source URI, retrieval time, content sha256, origin id), totals reconciled exactly to source, output deterministic, and structural patterns flagged by named rule without attribution. It assembles and routes evidence to a human investigator — it never blocks, files, or concludes who controls an address. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
400 fixture sets written to disk as explorer-shaped capture files and read back exactly as a user run would. Adversarial plants: multi-page pagination with boundary duplicates (dedupe exactly once), dust/airdrop spam, self-transfers, mixed-case display forms of one EVM address, token decimal traps (6/8/18), and zero-value transfers. Ground truth (counts, per-direction value sums, counterparties, planted duplicates, expected observations) is recorded at generation.

## 3. Provenance completeness (gate: 100%)
- Facts emitted: **61,126** — complete: **61,126** — incomplete: **0**
- Completeness: **1.0000** (floor 1.0). A fact missing any provenance field fails the build.

## 4. Reconciliation (gate: exact)
Engine totals vs fixture-source ground truth, aggregated over all sets (every set is also checked individually — 400/400 exact):

| chain | measure | source_truth | engine | delta |
| --- | --- | --- | --- | --- |
| btc | counterparty_count | 2172 | 2172 | 0 |
| btc | native_tx_count | 18680 | 18680 | 0 |
| btc | self_transfer_count | 33 | 33 | 0 |
| btc | token_transfer_count | 0 | 0 | 0 |
| btc | value_in | 2589899591276 | 2589899591276 | 0 |
| btc | value_out | 2236120303159 | 2236120303159 | 0 |
| evm | counterparty_count | 2994 | 2994 | 0 |
| evm | native_tx_count | 21494 | 21494 | 0 |
| evm | self_transfer_count | 128 | 128 | 0 |
| evm | token_transfer_count | 14741 | 14741 | 0 |
| evm | value_in | 26986758781956592624820 | 26986758781956592624820 | 0 |
| evm | value_out | 26646907606318957774387 | 26646907606318957774387 | 0 |
| all | pagination_duplicates | 232 | 232 | 0 |

- Records dropped: **0** · double-counted: **0** (tolerance 0)
- Pagination duplicates: planted 232, removed 232 — deduplicated exactly once, on the one named cause (identical record across a page boundary).
- BTC parsed totals tie to the explorer's own `chain_stats`: **EXACT**

## 5. Determinism (gate: byte-identical)
Two full passes over the same fixture files: annex + facts CSV + counterparty CSV digests **identical** (`14fbbfbb6c3c805807580335cbe0de7f`). The run timestamp exists only in the evidence manifest, never in rendered evidence.

## 6. Structural observations (planted vs detected)
- Planted: **245** · detected: **245** · missed: **0** · spurious: **0**
- Named rules: OBS_DUST_SPAM, OBS_SELF_TRANSFER, OBS_HIGH_FREQ_SAME_COUNTERPARTY. Observations are structural flags for a human — never attributions; an address is not an identity.

## 7. Committed sample fixtures
`fixtures/sample/` (3 sets, 284 facts) round-trips from disk against its committed truth: provenance 100.0%, 3/3 sets exact, deterministic: True. The rendered sample annex is committed at `evidence/annex-sample.md`.

## 8. Live-mode degradation
The optional live collectors (user-supplied explorer base URL; no default endpoint) degrade to None offline without raising: **True**. CI never touches the network.

## 9. Limitations
- Synthetic fixtures model the SHAPE of explorer payloads and their failure modes (pagination overlap, decimal traps, spam, case variance), not the full messiness of live explorer data. Validate live captures against the target explorer's current schema before reliance.
- Token metadata (symbol, name, decimals) is recorded as claimed by the source; a token contract can claim any symbol. Nothing here verifies a token's legitimacy.
- The Blockscout-style module API carries no per-transfer log index, so token-transfer identity is the full record; EIP-55 checksum validation is out of scope (identity is case-folded hex).
- Observations are structural, not attributions. Address does not equal identity; counterparty exposure and entity attribution remain the job of a chain-analytics vendor and a human investigator. This engine complements — never replaces — those.

## 10. Reproduction
```bash
python3 run_validation.py --seed 42 --addresses 400 --transactions 50000
```
