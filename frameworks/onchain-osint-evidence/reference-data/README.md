# Reference data — on-chain OSINT evidence

This framework's committed sample inputs do NOT live in this folder — they live in
[`../fixtures/sample/`](../fixtures/sample/), inside this same framework directory.
This file exists so every framework package presents the same `reference-data/`
entry point; the invariant it serves is that no framework refers outside its own
folder for sample data.

> **In plain terms:** The other frameworks keep a small committed sample spreadsheet
> here. This one already ships something better — a full set of fake block-explorer
> responses, checked into `fixtures/sample/` one directory up — so this page just
> points you at it rather than committing the same thing twice.

## Where the sample inputs live

| Location | Contents |
|---|---|
| `../fixtures/sample/evm-sample-01/` | EVM capture set: `capture-manifest.json` plus Blockscout-style `balance` / `txlist` / `tokentx` response pages. |
| `../fixtures/sample/evm-sample-02/` | Second EVM capture set (different pagination / token-decimal traps). |
| `../fixtures/sample/btc-sample-01/` | BTC capture set: `capture-manifest.json`, mempool-style address `summary.json`, and paginated `txs-p*.json`. |
| `../fixtures/sample/truth.json` | Ground truth per capture set (expected counts, planted duplicates) so reconciliation can be scored exactly. |

Every capture set is fully synthetic — all addresses, hashes, tokens, and hosts are
fictional (RFC 2606 `.example` domains) — and each `capture-manifest.json` stamps
the provenance the engine requires. The validation harness runs from these same
committed fixtures, so what you see here is exactly what CI exercises.

## Regeneration

From this framework's directory:

```bash
python3 generate_synthetic_data.py --write-sample
```

This refreshes `fixtures/sample/` deterministically from its fixed seed. The
repo-level builder (`python3 _tooling/build_reference_data.py --only
onchain-osint-evidence`) intentionally generates nothing for this framework; its
`--check` mode verifies only that this README exists.

All records are seeded synthetic data. No real person, entity, address, or
transaction is represented.

**Confidence: HIGH — the committed fixtures are the exact inputs the CI validation harness runs from, refreshed deterministically from a fixed seed.**
