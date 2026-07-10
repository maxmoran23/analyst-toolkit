"""
Synthetic explorer-fixture generator for the on-chain OSINT evidence framework.

Builds capture sets exactly as they would come back from public block explorers —
EVM (Blockscout-style module API: balance / txlist / tokentx, paginated) and BTC
(mempool-style REST: address summary / transaction pages) — with KNOWN ground truth
per address so the engine's reconciliation can be scored exactly.

Adversarial plants (each targets a way hand-built OSINT goes wrong):
  * multi-page pagination — totals must survive page reassembly;
  * duplicate records across page boundaries (the classic offset-pagination
    overlap) — must be deduplicated EXACTLY once, never zero, never twice;
  * dust / airdrop spam — floods of zero-value and dust transfers from distinct
    senders that must be counted, flagged, and never mistaken for real flow;
  * self-transfers — the address paying itself;
  * mixed-case display forms of the same EVM address — a naive rollup splits one
    counterparty into several;
  * token decimal traps — the same raw integer means wildly different quantities
    at 6 / 8 / 18 decimals; a divide-by-1e18 habit corrupts amounts;
  * zero-value token transfers — must not crash or skew anything.

All addresses, hashes, tokens, and hosts are fictional (RFC 2606 `.example`
domains). Seeded and deterministic: same seed, same bytes.

Usage:
    python3 generate_synthetic_data.py --seed 42 --addresses 400 --transactions 50000
    python3 generate_synthetic_data.py --write-sample     # refresh fixtures/sample/
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as E  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

EVM_HOST = "https://evm-explorer.example"
BTC_HOST = "https://btc-explorer.example"
SAMPLE_SEED = 7

# Fixed retrieval epoch — capture timestamps are part of the deterministic fixture
# content (the run timestamp lives only in the evidence manifest).
_RETRIEVAL_BASE = datetime(2026, 2, 11, 14, 0, 0, tzinfo=timezone.utc)
_BLOCK_EPOCH_LO = 1735689600            # 2025-01-01 UTC
_BLOCK_EPOCH_HI = 1766966400            # 2025-12-29 UTC

# Fictional token catalog — the decimal traps. (symbol, name, decimals)
_TOKEN_DEFS = [("HVUSD", "Harborview USD", 6), ("OCTAV", "Octavia Exchange Token", 8),
               ("MERID", "Meridian Governance", 18), ("ANCHR", "Anchorage Credit", 18)]
_SPAM_TOKEN = ("SPAMX", "FREE-AIRDROP-CLAIM.example", 18)

_BTC_CHARS = "023456789acdefghjklmnpqrstuvwxyz"

# Plants stay clear of the engine's default observation thresholds on BOTH sides:
# planted counts always trigger; unplanted addresses can never trigger by accident
# (normal counterparties are capped at _NORMAL_CP_MAX native txs < high_freq_min_tx,
# and at most _MAX_ZERO_PLANT zero-value transfers < dust_spam_min_count).
_NORMAL_CP_MAX = 12
_MAX_ZERO_PLANT = 2


class _UidGen:
    """Guaranteed-unique fictional identifiers (counter salt + rng bits)."""

    def __init__(self, rng):
        self.rng = rng
        self.n = 0

    def evm_addr(self):
        self.n += 1
        return "0x%08x%032x" % (self.n, self.rng.getrandbits(128))

    def btc_addr(self):
        self.n += 1
        core = "".join(self.rng.choice(_BTC_CHARS) for _ in range(26))
        return "bc1q%06d%s" % (self.n, core)

    def tx_hash(self):
        self.n += 1
        return "%016x%048x" % (self.n, self.rng.getrandbits(192))


def _mixcase(addr, rng):
    """A mixed-case display form of an EVM address (checksum-style casing without
    claiming EIP-55 validity — the engine folds case either way)."""
    out = []
    for ch in addr:
        out.append(ch.upper() if ch in "abcdef" and rng.random() < 0.5 else ch)
    return "".join(out)


def _retrieved_at(set_idx, cap_idx):
    t = _RETRIEVAL_BASE + timedelta(seconds=set_idx * 600 + cap_idx * 30)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _paginate(records, page_size, plant_dups):
    """Chunk into pages; when planting, repeat each page-boundary record at the top
    of the next page (offset-pagination overlap). Returns (pages, dups_planted)."""
    pages = [records[i:i + page_size] for i in range(0, len(records), page_size)] or [[]]
    dups = 0
    if plant_dups and len(pages) > 1:
        for p in range(1, len(pages)):
            pages[p] = [pages[p - 1][-1]] + pages[p]
            dups += 1
    return pages, dups


def _encode(payload, pretty):
    if pretty:
        return (json.dumps(payload, indent=1, sort_keys=True) + "\n").encode("utf-8")
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


# --------------------------------------------------------------------------------
# EVM set builder
# --------------------------------------------------------------------------------

def _build_evm_set(set_id, set_idx, rng, uid, tokens, n_tx, plants, page_size):
    addr = uid.evm_addr()
    n_native = max(2, int(n_tx * 0.6))
    n_token = max(1, n_tx - n_native)
    n_cp = max(math.ceil(n_native / _NORMAL_CP_MAX), rng.randint(3, 8))
    cps = [uid.evm_addr() for _ in range(n_cp)]

    def disp(a):
        return _mixcase(a, rng) if plants["mixedcase"] and rng.random() < 0.5 else a

    truth = {"chain": "evm", "address": addr, "native_tx_count": 0,
             "token_transfer_count": 0, "value_in": 0, "value_out": 0,
             "self_transfer_count": 0, "counterparty_count": 0,
             "duplicates_planted": 0, "expected_observations": []}
    cp_seen = set()
    native, token = [], []

    def native_tx(cp, direction, value):
        ep = rng.randint(_BLOCK_EPOCH_LO, _BLOCK_EPOCH_HI)
        frm, to = (cp, addr) if direction == "in" else (addr, cp)
        if direction == "self":
            frm = to = addr
        native.append({"blockNumber": str((ep - _BLOCK_EPOCH_LO) // 12 + 21000000),
                       "timeStamp": str(ep), "hash": "0x" + uid.tx_hash(),
                       "from": disp(frm), "to": disp(to), "value": str(value),
                       "isError": "0"})
        truth["native_tx_count"] += 1
        if direction == "self":
            truth["self_transfer_count"] += 1
        else:
            cp_seen.add(cp)
            truth["value_in" if direction == "in" else "value_out"] += value

    def token_tx(tok, cp, direction, raw):
        sym, name, dec, contract = tok
        ep = rng.randint(_BLOCK_EPOCH_LO, _BLOCK_EPOCH_HI)
        frm, to = (cp, addr) if direction == "in" else (addr, cp)
        token.append({"blockNumber": str((ep - _BLOCK_EPOCH_LO) // 12 + 21000000),
                      "timeStamp": str(ep), "hash": "0x" + uid.tx_hash(),
                      "from": disp(frm), "to": disp(to), "value": str(raw),
                      "contractAddress": disp(contract), "tokenName": name,
                      "tokenSymbol": sym, "tokenDecimal": str(dec)})
        truth["token_transfer_count"] += 1
        cp_seen.add(cp)

    for i in range(n_native):
        native_tx(cps[i % n_cp], rng.choice(["in", "out"]),
                  rng.randint(10 ** 15, 5 * 10 ** 18))
    if plants["highfreq"]:
        hf_cp = uid.evm_addr()
        for _ in range(rng.randint(25, 40)):
            native_tx(hf_cp, rng.choice(["in", "out"]),
                      rng.randint(10 ** 15, 5 * 10 ** 18))
        truth["expected_observations"].append("OBS_HIGH_FREQ_SAME_COUNTERPARTY")
    if plants["self"]:
        for _ in range(rng.randint(1, 3)):
            native_tx(None, "self", rng.randint(10 ** 15, 10 ** 18))
        truth["expected_observations"].append("OBS_SELF_TRANSFER")

    for _ in range(n_token):
        tok = rng.choice(tokens)
        raw = rng.randint(10 ** tok[2] // 2, 5000 * 10 ** tok[2])   # >= 0.5 units: never dust
        token_tx(tok, rng.choice(cps), rng.choice(["in", "out"]), raw)
    if plants["zero"]:
        for _ in range(rng.randint(1, _MAX_ZERO_PLANT)):
            token_tx(rng.choice(tokens), rng.choice(cps), "in", 0)
    if plants["dust"]:
        spam = tokens[-1]                                            # SPAMX, 18 decimals
        for _ in range(rng.randint(10, 24)):
            raw = 0 if rng.random() < 0.5 else rng.randint(1, 10 ** (spam[2] - 3))
            token_tx(spam, uid.evm_addr(), "in", raw)                # distinct spam senders
        truth["expected_observations"].append("OBS_DUST_SPAM")

    truth["counterparty_count"] = len(cp_seen)
    truth["expected_observations"].sort()

    native.sort(key=lambda r: (int(r["timeStamp"]), r["hash"]))
    token.sort(key=lambda r: (int(r["timeStamp"]), r["hash"]))
    n_pages, d1 = _paginate(native, page_size, plants["dup"])
    t_pages, d2 = _paginate(token, page_size, plants["dup"])
    truth["duplicates_planted"] = d1 + d2

    captures, ci = [], 0

    def add(kind, file, url, payload):
        nonlocal ci
        captures.append({"kind": kind, "file": file, "url": url,
                         "retrieved_at_utc": _retrieved_at(set_idx, ci),
                         "payload": payload})
        ci += 1

    add("evm_balance", "balance.json",
        "%s/api?module=account&action=balance&address=%s" % (EVM_HOST, addr),
        {"status": "1", "message": "OK", "result": str(rng.randint(0, 10 ** 20))})
    for p, page in enumerate(n_pages, 1):
        add("evm_txlist", "txlist-p%d.json" % p,
            "%s/api?module=account&action=txlist&address=%s&page=%d&offset=%d&sort=asc"
            % (EVM_HOST, addr, p, page_size),
            {"status": "1", "message": "OK", "result": page})
    for p, page in enumerate(t_pages, 1):
        add("evm_tokentx", "tokentx-p%d.json" % p,
            "%s/api?module=account&action=tokentx&address=%s&page=%d&offset=%d&sort=asc"
            % (EVM_HOST, addr, p, page_size),
            {"status": "1", "message": "OK", "result": page})

    return {"set_id": set_id, "address": addr, "chain": "evm", "captures": captures}, truth


# --------------------------------------------------------------------------------
# BTC set builder
# --------------------------------------------------------------------------------

def _build_btc_set(set_id, set_idx, rng, uid, n_tx, plants, page_size):
    addr = uid.btc_addr()
    n_cp = max(math.ceil(n_tx / _NORMAL_CP_MAX), rng.randint(4, 9))
    cps = [uid.btc_addr() for _ in range(n_cp)]

    truth = {"chain": "btc", "address": addr, "native_tx_count": 0,
             "token_transfer_count": 0, "value_in": 0, "value_out": 0,
             "self_transfer_count": 0, "counterparty_count": 0,
             "duplicates_planted": 0, "expected_observations": []}
    cp_seen = set()
    txs = []
    funded_ct = spent_ct = 0

    def btc_tx(vin, vout):
        nonlocal funded_ct, spent_ct
        ep = rng.randint(_BLOCK_EPOCH_LO, _BLOCK_EPOCH_HI)
        txs.append({"txid": uid.tx_hash(),
                    "status": {"confirmed": True,
                               "block_height": (ep - _BLOCK_EPOCH_LO) // 600 + 870000,
                               "block_time": ep},
                    "vin": [{"prevout": {"scriptpubkey_address": a, "value": v}}
                            for a, v in vin],
                    "vout": [{"scriptpubkey_address": a, "value": v} for a, v in vout]})
        truth["native_tx_count"] += 1
        for a, v in vout:
            if a == addr:
                truth["value_in"] += v
                funded_ct += 1
        for a, v in vin:
            if a == addr:
                truth["value_out"] += v
                spent_ct += 1

    def received(cp, v):
        btc_tx([(cp, v)], [(addr, v)])
        cp_seen.add(cp)

    def spent(cp, v):
        change = 0 if rng.random() < 0.4 else rng.randint(5000, max(5001, v // 2))
        vout = [(cp, v - change)] + ([(addr, change)] if change else [])
        btc_tx([(addr, v)], vout)
        cp_seen.add(cp)

    for i in range(n_tx):
        cp, v = cps[i % n_cp], rng.randint(50_000, 500_000_000)
        (received if rng.random() < 0.5 else spent)(cp, v)
    if plants["highfreq"]:
        hf_cp = uid.btc_addr()
        for _ in range(rng.randint(25, 40)):
            v = rng.randint(50_000, 500_000_000)
            (received if rng.random() < 0.5 else spent)(hf_cp, v)
        truth["expected_observations"].append("OBS_HIGH_FREQ_SAME_COUNTERPARTY")
    if plants["self"]:
        for _ in range(rng.randint(1, 2)):
            v = rng.randint(50_000, 500_000_000)
            btc_tx([(addr, v)], [(addr, v)])
            truth["self_transfer_count"] += 1
    if truth["self_transfer_count"]:
        truth["expected_observations"].append("OBS_SELF_TRANSFER")
    if plants["dust"]:
        for _ in range(rng.randint(10, 20)):
            received(uid.btc_addr(), 546)                            # distinct dusters
        truth["expected_observations"].append("OBS_DUST_SPAM")

    truth["counterparty_count"] = len(cp_seen)
    truth["expected_observations"].sort()

    txs.sort(key=lambda r: (r["status"]["block_time"], r["txid"]))
    pages, dups = _paginate(txs, page_size, plants["dup"])
    truth["duplicates_planted"] = dups

    captures = [{"kind": "btc_summary", "file": "summary.json",
                 "url": "%s/api/address/%s" % (BTC_HOST, addr),
                 "retrieved_at_utc": _retrieved_at(set_idx, 0),
                 "payload": {"address": addr,
                             "chain_stats": {"funded_txo_count": funded_ct,
                                             "funded_txo_sum": truth["value_in"],
                                             "spent_txo_count": spent_ct,
                                             "spent_txo_sum": truth["value_out"],
                                             "tx_count": truth["native_tx_count"]}}}]
    for p, page in enumerate(pages, 1):
        captures.append({"kind": "btc_txs", "file": "txs-p%d.json" % p,
                         "url": "%s/api/address/%s/txs?page=%d" % (BTC_HOST, addr, p),
                         "retrieved_at_utc": _retrieved_at(set_idx, p),
                         "payload": page})

    return {"set_id": set_id, "address": addr, "chain": "btc", "captures": captures}, truth


# --------------------------------------------------------------------------------
# population
# --------------------------------------------------------------------------------

def _token_catalog(uid):
    return [(sym, name, dec, uid.evm_addr()) for sym, name, dec in
            _TOKEN_DEFS] + [(_SPAM_TOKEN[0], _SPAM_TOKEN[1], _SPAM_TOKEN[2], uid.evm_addr())]


def _draw_plants(rng, chain):
    return {"dup": rng.random() < 0.35, "dust": rng.random() < 0.25,
            "self": rng.random() < 0.20, "highfreq": rng.random() < 0.18,
            "mixedcase": chain == "evm" and rng.random() < 0.30,
            "zero": chain == "evm" and rng.random() < 0.40}


def build_population(n_addresses, n_transactions, rng,
                     evm_page_size=100, btc_page_size=25):
    """Build the full seeded population of capture sets + per-set ground truth."""
    uid = _UidGen(rng)
    tokens = _token_catalog(uid)
    avg = max(6, n_transactions // max(1, n_addresses))
    specs, truths = [], {}
    for i in range(n_addresses):
        chain = "evm" if rng.random() < 0.7 else "btc"
        n_tx = rng.randint(max(4, avg // 2), max(6, avg * 3 // 2))
        plants = _draw_plants(rng, chain)
        if chain == "evm":
            spec, truth = _build_evm_set("evm-%04d" % i, i, rng, uid, tokens,
                                         n_tx, plants, evm_page_size)
        else:
            spec, truth = _build_btc_set("btc-%04d" % i, i, rng, uid,
                                         n_tx, plants, btc_page_size)
        specs.append(spec)
        truths[spec["set_id"]] = truth
    return specs, truths


def build_sample():
    """The small committed fixture set under fixtures/sample/ — one EVM set with
    every adversarial plant, one clean EVM set, one BTC set with plants. Fixed
    seed, small page sizes so pagination + boundary duplicates appear at sample
    scale. Regenerating with the same code yields identical bytes."""
    rng = random.Random(SAMPLE_SEED)
    uid = _UidGen(rng)
    tokens = _token_catalog(uid)
    all_on = {"dup": True, "dust": True, "self": True, "highfreq": True,
              "mixedcase": True, "zero": True}
    none_on = {k: False for k in all_on}
    specs, truths = [], {}
    for spec, truth in (
            _build_evm_set("evm-sample-01", 0, rng, uid, tokens, 90, all_on, 20),
            _build_evm_set("evm-sample-02", 1, rng, uid, tokens, 12, none_on, 20),
            _build_btc_set("btc-sample-01", 2, rng, uid, 14,
                           dict(all_on, mixedcase=False, zero=False), 10)):
        specs.append(spec)
        truths[spec["set_id"]] = truth
    return specs, truths


# --------------------------------------------------------------------------------
# materialization — to disk (fixture files) or in-memory engine sets
# --------------------------------------------------------------------------------

def write_fixtures(specs, out_dir, pretty=False):
    """Write one fixture directory per set: capture-manifest.json + the payload
    files it lists, byte-for-byte what the in-memory path hands the engine."""
    for spec in specs:
        d = os.path.join(out_dir, spec["set_id"])
        os.makedirs(d, exist_ok=True)
        man = {"set_id": spec["set_id"], "address": spec["address"],
               "chain": spec["chain"],
               "captures": [{k: c[k] for k in ("kind", "file", "url", "retrieved_at_utc")}
                            for c in spec["captures"]]}
        with open(os.path.join(d, "capture-manifest.json"), "w") as fh:
            json.dump(man, fh, indent=2)
        for c in spec["captures"]:
            with open(os.path.join(d, c["file"]), "wb") as fh:
                fh.write(_encode(c["payload"], pretty))


def write_truth(truths, out_dir):
    with open(os.path.join(out_dir, "truth.json"), "w") as fh:
        json.dump(truths, fh, indent=2, sort_keys=True)


def to_engine_sets(specs, pretty=False):
    """The in-memory equivalent of write_fixtures + engine.load_fixture_dir —
    identical bytes, no disk."""
    sets = []
    for spec in specs:
        caps = [E.Capture(kind=c["kind"], url=c["url"],
                          retrieved_at_utc=c["retrieved_at_utc"],
                          body=_encode(c["payload"], pretty), file=c["file"])
                for c in spec["captures"]]
        sets.append(E.FixtureSet(set_id=spec["set_id"], address=spec["address"],
                                 chain=spec["chain"], captures=caps))
    return sets


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--addresses", type=int, default=400)
    ap.add_argument("--transactions", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(HERE, "data", "fixtures"))
    ap.add_argument("--write-sample", action="store_true",
                    help="refresh the committed fixtures/sample/ set and exit")
    args = ap.parse_args()

    if args.write_sample:
        out = os.path.join(HERE, "fixtures", "sample")
        shutil.rmtree(out, ignore_errors=True)
        specs, truths = build_sample()
        write_fixtures(specs, out, pretty=True)
        write_truth(truths, out)
        n = sum(t["native_tx_count"] + t["token_transfer_count"] for t in truths.values())
        print("sample fixtures: %d sets, %d unique records -> %s/   [seed=%d]"
              % (len(specs), n, out, SAMPLE_SEED))
        return

    rng = random.Random(args.seed)
    specs, truths = build_population(args.addresses, args.transactions, rng)
    shutil.rmtree(args.out, ignore_errors=True)
    write_fixtures(specs, args.out)
    write_truth(truths, args.out)
    n = sum(t["native_tx_count"] + t["token_transfer_count"] for t in truths.values())
    d = sum(t["duplicates_planted"] for t in truths.values())
    print("fixtures: %d sets (%d unique records, %d boundary duplicates planted) -> %s/"
          "   [seed=%d]" % (len(specs), n, d, args.out, args.seed))


if __name__ == "__main__":
    main()
