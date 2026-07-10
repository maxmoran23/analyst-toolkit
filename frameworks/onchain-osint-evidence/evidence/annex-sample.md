# Evidence Annex — EVM address `0x000000068d116ece1738f7d93d9c172411e20b8f`

Assembled by the `onchain-osint-evidence` reference collector from the public explorer captures listed in section 1. Every figure below derives from a provenance-stamped fact (source URI, retrieval time, content sha256, origin) in the fact ledger. **Structural observations are patterns in public transaction data — they are not attributions of identity, ownership, or wrongdoing. An address is not an identity.**

## 1. Source captures

| # | endpoint | retrieved (UTC) | content sha256 (first 16) |
| --- | --- | --- | --- |
| 1 | `https://evm-explorer.example/api?module=account&action=balance&address=0x000000068d116ece1738f7d93d9c172411e20b8f` | 2026-02-11T14:00:00Z | `ebc9db56094ed616` |
| 2 | `https://evm-explorer.example/api?module=account&action=txlist&address=0x000000068d116ece1738f7d93d9c172411e20b8f&page=1&offset=20&sort=asc` | 2026-02-11T14:00:30Z | `22ee3e6c2211e0ed` |
| 3 | `https://evm-explorer.example/api?module=account&action=txlist&address=0x000000068d116ece1738f7d93d9c172411e20b8f&page=2&offset=20&sort=asc` | 2026-02-11T14:01:00Z | `cd1478295849dcaf` |
| 4 | `https://evm-explorer.example/api?module=account&action=txlist&address=0x000000068d116ece1738f7d93d9c172411e20b8f&page=3&offset=20&sort=asc` | 2026-02-11T14:01:30Z | `00f56a31cebff1ba` |
| 5 | `https://evm-explorer.example/api?module=account&action=txlist&address=0x000000068d116ece1738f7d93d9c172411e20b8f&page=4&offset=20&sort=asc` | 2026-02-11T14:02:00Z | `dc054ed6fc9d99a5` |
| 6 | `https://evm-explorer.example/api?module=account&action=txlist&address=0x000000068d116ece1738f7d93d9c172411e20b8f&page=5&offset=20&sort=asc` | 2026-02-11T14:02:30Z | `6cfdf8156f57c817` |
| 7 | `https://evm-explorer.example/api?module=account&action=tokentx&address=0x000000068d116ece1738f7d93d9c172411e20b8f&page=1&offset=20&sort=asc` | 2026-02-11T14:03:00Z | `632b205b18563d8d` |
| 8 | `https://evm-explorer.example/api?module=account&action=tokentx&address=0x000000068d116ece1738f7d93d9c172411e20b8f&page=2&offset=20&sort=asc` | 2026-02-11T14:03:30Z | `7c0addf20d14c6bc` |
| 9 | `https://evm-explorer.example/api?module=account&action=tokentx&address=0x000000068d116ece1738f7d93d9c172411e20b8f&page=3&offset=20&sort=asc` | 2026-02-11T14:04:00Z | `e0f5221f677afe9a` |

Full digests in `evidence-manifest.json`; recompute from the stored payloads to verify none was altered after capture.

## 2. Address summary (as reported by the source)

| balance (wei) | balance (native units) |
| --- | --- |
| 47110216241983413024 | 47.110216241983413024 |

## 3. Directional flow summary

| metric | value |
| --- | --- |
| native transactions (unique) | 84 |
| inbound / outbound / self | 43 / 40 / 1 |
| value in (wei) | 107039268654556066838 (107.039268654556066838 native units) |
| value out (wei) | 84719593470947046222 (84.719593470947046222 native units) |
| self-transfer value (wei) | 555916274539259230 |
| token transfers (unique) | 52 |
| zero-value token transfers | 10 |
| dust token transfers | 16 |
| distinct counterparties | 21 |
| pagination duplicates removed | 6 |

## 4. Counterparty rollup (top 15 of 21 by total value; full set in `counterparties.csv`)

| counterparty | native txs | value in (wei) | value out (wei) | token transfers | first seen | last seen |
| --- | --- | --- | --- | --- | --- | --- |
| `0x0000004319918b8a7a243b324990c224a1dbbd89` | 29 | 30779921562071463068 | 39550642296503914571 | 0 | 2025-01-14 03:56:34 UTC | 2025-12-21 23:52:11 UTC |
| `0x00000008a09f76b5a170b33839263059f28c105d` | 9 | 16399511123008756297 | 10641688412690701495 | 6 | 2025-01-24 10:20:00 UTC | 2025-12-17 21:15:45 UTC |
| `0x0000000af9ebdacc0cb1e29c658cda1495e60af5` | 9 | 18894218175556548641 | 5947856272631366875 | 4 | 2025-01-31 02:05:22 UTC | 2025-12-21 04:16:57 UTC |
| `0x0000000993bd04cf0fd630f1f29d0da9953f48f1` | 9 | 12810655211609533584 | 7560094037088945250 | 6 | 2025-01-13 02:26:13 UTC | 2025-12-10 23:16:30 UTC |
| `0x0000000bdbc496cb8e81973e0becd7b03898d190` | 9 | 7788742443809393284 | 9829258505010932979 | 9 | 2025-01-24 13:24:05 UTC | 2025-12-27 23:22:49 UTC |
| `0x000000071fb17c2390c192cfd3ac94af0f21ddb6` | 9 | 11003369966974181433 | 6285436794854636780 | 5 | 2025-01-11 20:23:32 UTC | 2025-10-04 00:14:50 UTC |
| `0x0000000c24ede6a46b4cb2424a23d5962217bead` | 9 | 9362850171526190531 | 4904617152166548272 | 8 | 2025-01-10 19:44:53 UTC | 2025-12-26 12:04:58 UTC |
| `0x00000088198be25079cba4698ee1be8702507735` | 0 | 0 | 0 | 1 | 2025-09-12 12:24:28 UTC | 2025-09-12 12:24:28 UTC |
| `0x0000008ac731e82c59cfdf89076f5c3c874ba543` | 0 | 0 | 0 | 1 | 2025-10-03 14:15:24 UTC | 2025-10-03 14:15:24 UTC |
| `0x0000008ca8344af1f1e84978602524a9eb4c14e3` | 0 | 0 | 0 | 1 | 2025-09-01 13:12:27 UTC | 2025-09-01 13:12:27 UTC |
| `0x0000008e54df086716a38a5b48563de04cd2595c` | 0 | 0 | 0 | 1 | 2025-01-02 12:38:56 UTC | 2025-01-02 12:38:56 UTC |
| `0x0000009026e4bfc91c8f1931ce15d2100640a87d` | 0 | 0 | 0 | 1 | 2025-12-21 10:57:00 UTC | 2025-12-21 10:57:00 UTC |
| `0x0000009293296b9a3b4c057e985db3c4813953eb` | 0 | 0 | 0 | 1 | 2025-06-17 04:30:57 UTC | 2025-06-17 04:30:57 UTC |
| `0x00000094f7ae1f2eda69ca8837133e01f87213ce` | 0 | 0 | 0 | 1 | 2025-12-09 23:35:46 UTC | 2025-12-09 23:35:46 UTC |
| `0x000000966b4d5b9d8a3d3a9d5179d5076c05af54` | 0 | 0 | 0 | 1 | 2025-05-29 17:35:29 UTC | 2025-05-29 17:35:29 UTC |

## 5. Structural observations

- **OBS_DUST_SPAM** (n=16): 16 inbound dust/zero-value transfers (threshold 10) — the unsolicited dust/airdrop-spam pattern. Dust is sent BY third parties; it says nothing about the address holder. Evidence: `0x0000000000000086a7729aa0906b6ef7511fd02eecdfbd220696f541037b4b62`, `0x0000000000000087bdb79e573ae17b8854b1e39d93317ed19a006f57fb3c8f31`, `0x0000000000000089fd51855f268d45995cccb8c5fa1338f6c62f9ab0cf278c96`, `0x000000000000008b3690096b7fba5cbddc1e2282fb7a0e0c7109e1cd3e1a14f2`, `0x000000000000008d432774b70550de69407e676707dc63c8395d7d4ddc3ed57c`.
- **OBS_SELF_TRANSFER** (n=1): 1 self-transfer(s) (address pays itself). Consistent with wallet management, consolidation, or testing — benign explanations exist; flagged for context only. Evidence: `0x0000000000000061ea0f771824a56eddcebbdcb73d0b8c4370fe98a02b27df87`.
- **OBS_HIGH_FREQ_SAME_COUNTERPARTY** (n=29): 29 native transactions with a single counterparty 0x0000004319918b8a7a243b324990c224a1dbbd89 (threshold 25) — a concentrated bilateral relationship. Could be an exchange deposit path, a payment channel, or routine business; identifying WHICH requires evidence this engine does not claim to have. Evidence: `0x0000004319918b8a7a243b324990c224a1dbbd89`.

Observations are structural, named-rule flags for a human investigator. They are never attributions, and this annex draws no conclusion about who controls this address.

## 6. Reconciliation

| check | value |
| --- | --- |
| source records parsed | 142 |
| unique records after pagination dedupe | 136 |
| duplicates removed (identical record across page boundary — the only named cause for removal) | 6 |

Totals in this annex are required to equal the source-capture totals exactly — no silent drops, no double counting. The package validation harness re-verifies this tie-out against ground truth on every run.

## 7. Fact ledger

| fact type | count |
| --- | --- |
| address_summary | 1 |
| counterparty_rollup | 21 |
| flow_summary | 1 |
| native_transaction | 84 |
| structural_observation | 3 |
| token_transfer | 52 |

All 162 facts carry full provenance (source URI, retrieval time, content sha256, origin id) — see `facts.csv` and `evidence-manifest.json`.
