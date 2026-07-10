"""
On-chain OSINT evidence engine — reference implementation.

Turns public block-explorer payloads for one address into an investigation-grade,
provenance-stamped evidence pack: every emitted fact carries its source URI,
retrieval timestamp, content sha256, and an origin locator (via `_lib/provenance`).
Full methodology in METHODOLOGY.md; this file is its executable form.

Inputs are capture sets — explorer API responses plus a capture manifest recording
where and when each was retrieved:
  EVM (Blockscout-style module API)   balance, txlist pages, tokentx pages
  BTC (mempool-style REST)            address summary, paginated transaction pages

What the engine does with them:
  * normalizes native transactions, token transfers, and the address summary into
    EvidenceFact records — case-folded addresses, exact integer amounts (wei/sats/
    raw token units + declared decimals), UTC times;
  * deduplicates pagination overlap on a provable named cause ONLY (an identical
    record repeated across page boundaries) — never drops a distinct record;
  * builds the counterparty rollup (in/out value, tx counts, first/last seen) and
    the directional flow summary;
  * flags simple STRUCTURAL OBSERVATIONS by named rule (dust spam, self-transfers,
    high-frequency same-counterparty). Observations are patterns in public
    transaction data — they are NEVER attributions. An address is not an identity;
  * renders the evidence annex (markdown), facts CSV, counterparty CSV, and the
    evidence-manifest JSON with reconciliation totals.

Design posture (same conservative stance as the rest of the pillar):
  * The engine assembles and routes evidence to a human investigator. It never
    auto-blocks, auto-files, or auto-approves anything, and it draws no conclusion
    about who controls an address or why.
  * Deterministic: the same captures produce byte-identical annex and CSVs. The
    run timestamp lives ONLY in the evidence manifest.
  * Offline/fixture mode is the default. Live mode (urllib against a user-supplied
    explorer base URL) degrades gracefully: any failure returns None, never raises.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.provenance import (EvidenceFact, build_manifest, combine_sha256,  # noqa: E402
                             completeness, sha256_bytes, sha256_text)

FRAMEWORK = "onchain-osint-evidence"

# Capture kinds the engine knows how to parse (recorded in each capture manifest).
EVM_KINDS = ("evm_balance", "evm_txlist", "evm_tokentx")
BTC_KINDS = ("btc_summary", "btc_txs")


@dataclass
class Config:
    # A token transfer is dust when quantity <= 10^-dust_token_exp units (includes
    # zero-value transfers, the airdrop-spam signature). 3 -> 0.001 units.
    dust_token_exp: int = 3
    dust_btc_sats_max: int = 1000        # BTC inbound output at/below this is dust
    dust_spam_min_count: int = 10        # inbound dust transfers to flag OBS_DUST_SPAM
    self_transfer_min_count: int = 1     # self-transfers to flag OBS_SELF_TRANSFER
    high_freq_min_tx: int = 25           # native txs w/ one counterparty to flag OBS_HIGH_FREQ
    annex_top_counterparties: int = 15   # rollup rows shown in the annex (all in the CSV)


@dataclass
class Capture:
    """One retrieved explorer payload + its capture provenance."""
    kind: str
    url: str
    retrieved_at_utc: str
    body: bytes
    file: str = ""
    _sha: str = field(default="", repr=False, compare=False)

    @property
    def sha256(self) -> str:
        if not self._sha:
            self._sha = sha256_bytes(self.body)
        return self._sha

    def payload(self):
        return json.loads(self.body.decode("utf-8"))


@dataclass
class FixtureSet:
    """All captures for one address — the unit the engine processes."""
    set_id: str
    address: str
    chain: str                     # "evm" | "btc"
    captures: list = field(default_factory=list)


@dataclass
class EvidencePack:
    """Everything the engine produces for one address."""
    set_id: str
    address: str
    chain: str
    facts: list
    flow: dict
    counterparties: list
    observations: list
    stats: dict                    # dedupe + tie-out reconciliation numbers
    annex_md: str
    facts_csv: str
    counterparties_csv: str
    manifest: dict


# --------------------------------------------------------------------------------
# fixture loading (offline mode — the default, and the only mode CI exercises)
# --------------------------------------------------------------------------------

def load_fixture_set(dir_path: str) -> FixtureSet:
    """Read one fixture directory: capture-manifest.json + the payload files it
    lists. The payload bytes are hashed exactly as stored — the same discipline a
    live capture applies to the response body it just fetched."""
    with open(os.path.join(dir_path, "capture-manifest.json"), "r") as fh:
        man = json.load(fh)
    caps = []
    for c in man["captures"]:
        with open(os.path.join(dir_path, c["file"]), "rb") as fh:
            body = fh.read()
        caps.append(Capture(kind=c["kind"], url=c["url"],
                            retrieved_at_utc=c["retrieved_at_utc"], body=body,
                            file=c["file"]))
    return FixtureSet(set_id=man["set_id"], address=man["address"],
                      chain=man["chain"], captures=caps)


def load_fixture_dir(root: str) -> list:
    """Load every fixture set under a root directory (sorted for determinism)."""
    sets = []
    for name in sorted(os.listdir(root)):
        sub = os.path.join(root, name)
        if os.path.isdir(sub) and os.path.exists(os.path.join(sub, "capture-manifest.json")):
            sets.append(load_fixture_set(sub))
    return sets


# --------------------------------------------------------------------------------
# amount + time formatting (exact — no floats anywhere in the money path)
# --------------------------------------------------------------------------------

def scale_amount(raw: int, decimals: int) -> str:
    """Render an integer base-unit amount at the declared decimals as an exact
    decimal string (pure integer arithmetic — a float here corrupts evidence)."""
    s = str(int(raw))
    if decimals <= 0:
        return s
    s = s.rjust(decimals + 1, "0")
    whole, frac = s[:-decimals], s[-decimals:]
    frac = frac.rstrip("0")
    return whole + ("." + frac if frac else "")


def utc_str(epoch: int) -> str:
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _is_dust_token(raw: int, decimals: int, config: Config) -> bool:
    # quantity <= 10^-dust_token_exp units  <=>  raw * 10^dust_token_exp <= 10^decimals
    return raw * (10 ** config.dust_token_exp) <= 10 ** decimals


# --------------------------------------------------------------------------------
# normalization — EVM (Blockscout-style module API)
# --------------------------------------------------------------------------------

def _lc(addr: str) -> str:
    """EVM address identity is case-insensitive hex: fold display case (checksummed
    or otherwise) to lowercase so the same address never splits a rollup."""
    return (addr or "").strip().lower()


def _derived_provenance(captures):
    """Provenance for a fact derived from several captures: joined URIs, latest
    retrieval time, combined digest of the exact source bytes."""
    uris = ";".join(sorted({c.url for c in captures}))
    at = max(c.retrieved_at_utc for c in captures)
    return uris, at, combine_sha256(c.sha256 for c in captures)


def _normalize_evm(fset: FixtureSet, config: Config):
    addr = _lc(fset.address)
    summary = None
    summary_cap = None
    native, tokens = [], []          # (record, capture) in first-seen page order
    raw_native = raw_token = 0
    for cap in fset.captures:
        p = cap.payload()
        if cap.kind == "evm_balance":
            summary = {"balance_wei": int(p["result"])}
            summary_cap = cap
        elif cap.kind == "evm_txlist":
            for r in p["result"]:
                raw_native += 1
                native.append((r, cap))
        elif cap.kind == "evm_tokentx":
            for r in p["result"]:
                raw_token += 1
                tokens.append((r, cap))

    # Dedupe pagination overlap — the only automated removal, and only on a
    # provable named cause: the identical record repeated across page boundaries.
    seen, uniq_native = set(), []
    for r, cap in native:
        key = _lc(r["hash"])
        if key in seen:
            continue
        seen.add(key)
        frm, to = _lc(r["from"]), _lc(r["to"])
        direction = "self" if (frm == addr and to == addr) else ("in" if to == addr else "out")
        cp = "" if direction == "self" else (frm if direction == "in" else to)
        uniq_native.append(({
            "tx_hash": _lc(r["hash"]), "block": int(r["blockNumber"]),
            "time_utc": utc_str(int(r["timeStamp"])), "epoch": int(r["timeStamp"]),
            "direction": direction, "counterparty": cp, "value_wei": int(r["value"]),
        }, cap))

    seen, uniq_token = set(), []
    for r, cap in tokens:
        frm, to = _lc(r["from"]), _lc(r["to"])
        contract = _lc(r["contractAddress"])
        raw_val = int(r["value"])
        key = (_lc(r["hash"]), frm, to, contract, raw_val)
        if key in seen:              # the module API has no log index; identity is
            continue                 # the full record (limitation in METHODOLOGY)
        seen.add(key)
        decimals = int(r["tokenDecimal"])
        direction = "self" if (frm == addr and to == addr) else ("in" if to == addr else "out")
        cp = "" if direction == "self" else (frm if direction == "in" else to)
        uniq_token.append(({
            "tx_hash": _lc(r["hash"]), "block": int(r["blockNumber"]),
            "time_utc": utc_str(int(r["timeStamp"])), "epoch": int(r["timeStamp"]),
            "direction": direction, "counterparty": cp, "contract": contract,
            "token_symbol": r.get("tokenSymbol", ""), "decimals": decimals,
            "raw_value": raw_val, "quantity": scale_amount(raw_val, decimals),
            "dust": _is_dust_token(raw_val, decimals, config),
        }, cap))

    stats = {"native_records_seen": raw_native, "native_unique": len(uniq_native),
             "token_records_seen": raw_token, "token_unique": len(uniq_token),
             "duplicates_removed": (raw_native - len(uniq_native)) + (raw_token - len(uniq_token)),
             "summary_ties_to_parsed": True}   # EVM balance is reported, not derived
    return summary, summary_cap, uniq_native, uniq_token, stats


# --------------------------------------------------------------------------------
# normalization — BTC (mempool-style REST)
# --------------------------------------------------------------------------------

def _normalize_btc(fset: FixtureSet, config: Config):
    addr = fset.address.strip()
    summary = None
    summary_cap = None
    txs = []
    raw_seen = 0
    for cap in fset.captures:
        p = cap.payload()
        if cap.kind == "btc_summary":
            cs = p["chain_stats"]
            summary = {"tx_count": int(cs["tx_count"]),
                       "funded_txo_sum_sats": int(cs["funded_txo_sum"]),
                       "spent_txo_sum_sats": int(cs["spent_txo_sum"])}
            summary_cap = cap
        elif cap.kind == "btc_txs":
            for r in p:
                raw_seen += 1
                txs.append((r, cap))

    seen, uniq = set(), []
    for r, cap in txs:
        key = r["txid"].lower()
        if key in seen:
            continue
        seen.add(key)
        vin_ours = sum(int(v["prevout"]["value"]) for v in r["vin"]
                       if v["prevout"]["scriptpubkey_address"] == addr)
        vout_ours = sum(int(v["value"]) for v in r["vout"]
                        if v["scriptpubkey_address"] == addr)
        ext_in = sorted({v["prevout"]["scriptpubkey_address"] for v in r["vin"]
                         if v["prevout"]["scriptpubkey_address"] != addr})
        ext_out = sorted({v["scriptpubkey_address"] for v in r["vout"]
                          if v["scriptpubkey_address"] != addr})
        is_self = not ext_in and not ext_out
        if is_self:
            direction, cp = "self", ""
        elif vin_ours > 0:
            direction, cp = "out", (ext_out[0] if ext_out else "")
        else:
            direction, cp = "in", (ext_in[0] if ext_in else "")
        dust_in = sum(1 for v in r["vout"]
                      if v["scriptpubkey_address"] == addr
                      and int(v["value"]) <= config.dust_btc_sats_max)
        uniq.append(({
            "tx_hash": r["txid"].lower(), "block": int(r["status"]["block_height"]),
            "time_utc": utc_str(int(r["status"]["block_time"])),
            "epoch": int(r["status"]["block_time"]),
            "direction": direction, "counterparty": cp,
            "value_in_sats": vout_ours, "value_out_sats": vin_ours,
            "dust_inbound_outputs": dust_in,
        }, cap))

    parsed_in = sum(t["value_in_sats"] for t, _ in uniq)
    parsed_out = sum(t["value_out_sats"] for t, _ in uniq)
    ties = (summary is not None
            and summary["tx_count"] == len(uniq)
            and summary["funded_txo_sum_sats"] == parsed_in
            and summary["spent_txo_sum_sats"] == parsed_out)
    stats = {"native_records_seen": raw_seen, "native_unique": len(uniq),
             "token_records_seen": 0, "token_unique": 0,
             "duplicates_removed": raw_seen - len(uniq),
             "summary_ties_to_parsed": bool(ties)}
    return summary, summary_cap, uniq, [], stats


# --------------------------------------------------------------------------------
# rollups, flow, observations
# --------------------------------------------------------------------------------

def _rollup_and_flow(chain, addr, native, tokens):
    cps = {}

    def cp_row(a):
        return cps.setdefault(a, {"counterparty": a, "native_tx_count": 0,
                                  "value_in": 0, "value_out": 0,
                                  "token_transfer_count": 0,
                                  "first_epoch": None, "last_epoch": None})

    def touch(row, epoch):
        row["first_epoch"] = epoch if row["first_epoch"] is None else min(row["first_epoch"], epoch)
        row["last_epoch"] = epoch if row["last_epoch"] is None else max(row["last_epoch"], epoch)

    flow = {"native_tx_count": len(native), "token_transfer_count": len(tokens),
            "in_count": 0, "out_count": 0, "self_count": 0,
            "value_in": 0, "value_out": 0, "self_value": 0,
            "zero_value_token_transfers": 0, "dust_token_transfers": 0}

    for t, _ in native:
        if chain == "evm":
            if t["direction"] == "self":
                flow["self_count"] += 1
                flow["self_value"] += t["value_wei"]
                continue
            row = cp_row(t["counterparty"])
            row["native_tx_count"] += 1
            touch(row, t["epoch"])
            if t["direction"] == "in":
                flow["in_count"] += 1
                flow["value_in"] += t["value_wei"]
                row["value_in"] += t["value_wei"]
            else:
                flow["out_count"] += 1
                flow["value_out"] += t["value_wei"]
                row["value_out"] += t["value_wei"]
        else:
            # BTC: UTXO semantics — value_in/value_out are funded/spent sums and
            # tie exactly to the explorer's own chain_stats (self txs included).
            flow["value_in"] += t["value_in_sats"]
            flow["value_out"] += t["value_out_sats"]
            if t["direction"] == "self":
                flow["self_count"] += 1
                flow["self_value"] += t["value_in_sats"]
                continue
            row = cp_row(t["counterparty"])
            row["native_tx_count"] += 1
            touch(row, t["epoch"])
            if t["direction"] == "in":
                flow["in_count"] += 1
                row["value_in"] += t["value_in_sats"]
            else:
                flow["out_count"] += 1
                row["value_out"] += t["value_out_sats"]

    for t, _ in tokens:
        if t["raw_value"] == 0:
            flow["zero_value_token_transfers"] += 1
        if t["dust"]:
            flow["dust_token_transfers"] += 1
        if t["direction"] == "self":
            continue
        row = cp_row(t["counterparty"])
        row["token_transfer_count"] += 1
        touch(row, t["epoch"])

    rows = []
    for a in sorted(cps, key=lambda a: (-(cps[a]["value_in"] + cps[a]["value_out"]), a)):
        r = cps[a]
        rows.append({"counterparty": a, "native_tx_count": r["native_tx_count"],
                     "value_in": r["value_in"], "value_out": r["value_out"],
                     "token_transfer_count": r["token_transfer_count"],
                     "first_seen_utc": utc_str(r["first_epoch"]),
                     "last_seen_utc": utc_str(r["last_epoch"])})
    flow["counterparty_count"] = len(rows)
    return rows, flow


def _observations(chain, native, tokens, rollup, flow, config: Config):
    """Named structural observations, in firing order. Each names its rule, its
    threshold, and the transactions behind it. None is an attribution: these are
    patterns in public transaction data, flagged for a human investigator."""
    obs = []

    # OBS_DUST_SPAM — many inbound dust/zero-value transfers (airdrop-spam pattern).
    if chain == "evm":
        dust_hashes = sorted(t["tx_hash"] for t, _ in tokens
                             if t["dust"] and t["direction"] == "in")
    else:
        dust_hashes = sorted(t["tx_hash"] for t, _ in native
                             if t["direction"] == "in" and t["dust_inbound_outputs"] > 0)
    if len(dust_hashes) >= config.dust_spam_min_count:
        obs.append({"id": "OBS_DUST_SPAM", "count": len(dust_hashes),
                    "sample_tx": dust_hashes[:5],
                    "note": ("%d inbound dust/zero-value transfers (threshold %d) — the "
                             "unsolicited dust/airdrop-spam pattern. Dust is sent BY third "
                             "parties; it says nothing about the address holder.")
                            % (len(dust_hashes), config.dust_spam_min_count)})

    # OBS_SELF_TRANSFER — transactions from the address to itself.
    self_hashes = sorted(t["tx_hash"] for t, _ in native if t["direction"] == "self")
    if len(self_hashes) >= config.self_transfer_min_count:
        obs.append({"id": "OBS_SELF_TRANSFER", "count": len(self_hashes),
                    "sample_tx": self_hashes[:5],
                    "note": ("%d self-transfer(s) (address pays itself). Consistent with "
                             "wallet management, consolidation, or testing — benign "
                             "explanations exist; flagged for context only.")
                            % len(self_hashes)})

    # OBS_HIGH_FREQ_SAME_COUNTERPARTY — repeated native activity with one counterparty.
    hot = [r for r in rollup if r["native_tx_count"] >= config.high_freq_min_tx]
    if hot:
        top = hot[0]
        obs.append({"id": "OBS_HIGH_FREQ_SAME_COUNTERPARTY",
                    "count": top["native_tx_count"],
                    "sample_tx": [top["counterparty"]],
                    "note": ("%d native transactions with a single counterparty %s "
                             "(threshold %d) — a concentrated bilateral relationship. "
                             "Could be an exchange deposit path, a payment channel, or "
                             "routine business; identifying WHICH requires evidence this "
                             "engine does not claim to have.")
                            % (top["native_tx_count"], top["counterparty"],
                               config.high_freq_min_tx)})
    return obs


# --------------------------------------------------------------------------------
# facts
# --------------------------------------------------------------------------------

def _build_facts(fset, summary, summary_cap, native, tokens, rollup, flow, obs):
    facts = []
    if summary is not None and summary_cap is not None:
        facts.append(EvidenceFact("address_summary", summary, summary_cap.url,
                                  summary_cap.retrieved_at_utc, summary_cap.sha256,
                                  "address:%s" % fset.address.lower()))
    for t, cap in native:
        v = {k: t[k] for k in t if k != "epoch"}
        facts.append(EvidenceFact("native_transaction", v, cap.url,
                                  cap.retrieved_at_utc, cap.sha256,
                                  "tx:%s" % t["tx_hash"]))
    for t, cap in tokens:
        v = {k: t[k] for k in t if k != "epoch"}
        oid = "transfer:%s:%s" % (t["tx_hash"], sha256_text(
            "%s|%s|%s|%d" % (t["counterparty"], t["contract"], t["direction"],
                             t["raw_value"]))[:12])
        facts.append(EvidenceFact("token_transfer", v, cap.url,
                                  cap.retrieved_at_utc, cap.sha256, oid))

    tx_caps = [c for c in fset.captures if c.kind in ("evm_txlist", "evm_tokentx", "btc_txs")]
    if tx_caps:
        d_uri, d_at, d_sha = _derived_provenance(tx_caps)
        for r in rollup:
            facts.append(EvidenceFact("counterparty_rollup", r, d_uri, d_at, d_sha,
                                      "counterparty:%s" % r["counterparty"]))
        facts.append(EvidenceFact("flow_summary", flow, d_uri, d_at, d_sha,
                                  "flow:%s" % fset.address.lower()))
        for o in obs:
            facts.append(EvidenceFact("structural_observation", o, d_uri, d_at, d_sha,
                                      "observation:%s" % o["id"]))
    facts.sort(key=lambda f: (f.fact_type, f.origin_id))
    return facts


# --------------------------------------------------------------------------------
# rendering (byte-deterministic — no run timestamps here)
# --------------------------------------------------------------------------------

def _csv_text(rows, columns):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def _unit(chain):
    return ("wei", "native units", 18) if chain == "evm" else ("sats", "BTC", 8)


def render_annex(fset, summary, flow, rollup, obs, stats, facts, config: Config):
    raw_u, disp_u, dec = _unit(fset.chain)
    L = []
    A = L.append
    A("# Evidence Annex — %s address `%s`" % (fset.chain.upper(), fset.address))
    A("")
    A("Assembled by the `%s` reference collector from the public explorer captures "
      "listed in section 1. Every figure below derives from a provenance-stamped "
      "fact (source URI, retrieval time, content sha256, origin) in the fact ledger. "
      "**Structural observations are patterns in public transaction data — they are "
      "not attributions of identity, ownership, or wrongdoing. An address is not an "
      "identity.**" % FRAMEWORK)
    A("")
    A("## 1. Source captures")
    A("")
    A("| # | endpoint | retrieved (UTC) | content sha256 (first 16) |")
    A("| --- | --- | --- | --- |")
    for i, c in enumerate(fset.captures, 1):
        A("| %d | `%s` | %s | `%s` |" % (i, c.url, c.retrieved_at_utc, c.sha256[:16]))
    A("")
    A("Full digests in `evidence-manifest.json`; recompute from the stored payloads "
      "to verify none was altered after capture.")
    A("")
    A("## 2. Address summary (as reported by the source)")
    A("")
    if fset.chain == "evm":
        A("| balance (%s) | balance (%s) |" % (raw_u, disp_u))
        A("| --- | --- |")
        A("| %d | %s |" % (summary["balance_wei"], scale_amount(summary["balance_wei"], dec)))
    else:
        A("| tx count | funded (%s) | spent (%s) | funded (%s) | spent (%s) |"
          % (raw_u, raw_u, disp_u, disp_u))
        A("| --- | --- | --- | --- | --- |")
        A("| %d | %d | %d | %s | %s |"
          % (summary["tx_count"], summary["funded_txo_sum_sats"],
             summary["spent_txo_sum_sats"],
             scale_amount(summary["funded_txo_sum_sats"], dec),
             scale_amount(summary["spent_txo_sum_sats"], dec)))
    A("")
    A("## 3. Directional flow summary")
    A("")
    A("| metric | value |")
    A("| --- | --- |")
    A("| native transactions (unique) | %d |" % flow["native_tx_count"])
    if fset.chain == "evm":
        A("| inbound / outbound / self | %d / %d / %d |"
          % (flow["in_count"], flow["out_count"], flow["self_count"]))
        A("| value in (%s) | %d (%s %s) |" % (raw_u, flow["value_in"],
                                              scale_amount(flow["value_in"], dec), disp_u))
        A("| value out (%s) | %d (%s %s) |" % (raw_u, flow["value_out"],
                                               scale_amount(flow["value_out"], dec), disp_u))
        A("| self-transfer value (%s) | %d |" % (raw_u, flow["self_value"]))
        A("| token transfers (unique) | %d |" % flow["token_transfer_count"])
        A("| zero-value token transfers | %d |" % flow["zero_value_token_transfers"])
        A("| dust token transfers | %d |" % flow["dust_token_transfers"])
    else:
        A("| inbound / outbound / self | %d / %d / %d |"
          % (flow["in_count"], flow["out_count"], flow["self_count"]))
        A("| funded (%s) | %d (%s %s) |" % (raw_u, flow["value_in"],
                                            scale_amount(flow["value_in"], dec), disp_u))
        A("| spent (%s) | %d (%s %s) |" % (raw_u, flow["value_out"],
                                           scale_amount(flow["value_out"], dec), disp_u))
    A("| distinct counterparties | %d |" % flow["counterparty_count"])
    A("| pagination duplicates removed | %d |" % stats["duplicates_removed"])
    A("")
    top = rollup[:config.annex_top_counterparties]
    A("## 4. Counterparty rollup (top %d of %d by total value; full set in "
      "`counterparties.csv`)" % (len(top), len(rollup)))
    A("")
    A("| counterparty | native txs | value in (%s) | value out (%s) | token transfers "
      "| first seen | last seen |" % (raw_u, raw_u))
    A("| --- | --- | --- | --- | --- | --- | --- |")
    for r in top:
        A("| `%s` | %d | %d | %d | %d | %s | %s |"
          % (r["counterparty"], r["native_tx_count"], r["value_in"], r["value_out"],
             r["token_transfer_count"], r["first_seen_utc"], r["last_seen_utc"]))
    A("")
    A("## 5. Structural observations")
    A("")
    if not obs:
        A("None flagged at the configured thresholds.")
    for o in obs:
        A("- **%s** (n=%d): %s Evidence: `%s`."
          % (o["id"], o["count"], o["note"], "`, `".join(o["sample_tx"])))
    A("")
    A("Observations are structural, named-rule flags for a human investigator. "
      "They are never attributions, and this annex draws no conclusion about who "
      "controls this address.")
    A("")
    A("## 6. Reconciliation")
    A("")
    A("| check | value |")
    A("| --- | --- |")
    A("| source records parsed | %d |" % (stats["native_records_seen"] + stats["token_records_seen"]))
    A("| unique records after pagination dedupe | %d |" % (stats["native_unique"] + stats["token_unique"]))
    A("| duplicates removed (identical record across page boundary — the only "
      "named cause for removal) | %d |" % stats["duplicates_removed"])
    if fset.chain == "btc":
        A("| parsed totals tie to the explorer's own chain_stats | %s |"
          % ("EXACT" if stats["summary_ties_to_parsed"] else "MISMATCH — investigate capture"))
    A("")
    A("Totals in this annex are required to equal the source-capture totals exactly "
      "— no silent drops, no double counting. The package validation harness "
      "re-verifies this tie-out against ground truth on every run.")
    A("")
    A("## 7. Fact ledger")
    A("")
    by_type = {}
    for f in facts:
        by_type[f.fact_type] = by_type.get(f.fact_type, 0) + 1
    A("| fact type | count |")
    A("| --- | --- |")
    for k in sorted(by_type):
        A("| %s | %d |" % (k, by_type[k]))
    A("")
    A("All %d facts carry full provenance (source URI, retrieval time, content "
      "sha256, origin id) — see `facts.csv` and `evidence-manifest.json`." % len(facts))
    A("")
    return "\n".join(L)


# --------------------------------------------------------------------------------
# the pipeline
# --------------------------------------------------------------------------------

FACT_COLUMNS = ["fact_type", "origin_id", "value", "source_uri", "retrieved_at_utc",
                "content_sha256"]
CP_COLUMNS = ["counterparty", "native_tx_count", "value_in", "value_out",
              "token_transfer_count", "first_seen_utc", "last_seen_utc"]


def build_pack(fset: FixtureSet, config: Config = None, generated_utc: str = "") -> EvidencePack:
    """Process one capture set into the full evidence pack. Deterministic: the
    annex and CSVs are byte-identical for the same captures; `generated_utc`
    (the run timestamp) appears ONLY in the manifest."""
    config = config or Config()
    if fset.chain == "evm":
        summary, scap, native, tokens, stats = _normalize_evm(fset, config)
    elif fset.chain == "btc":
        summary, scap, native, tokens, stats = _normalize_btc(fset, config)
    else:
        raise ValueError("unknown chain: %r" % fset.chain)

    rollup, flow = _rollup_and_flow(fset.chain, fset.address.lower(), native, tokens)
    obs = _observations(fset.chain, native, tokens, rollup, flow, config)
    facts = _build_facts(fset, summary, scap, native, tokens, rollup, flow, obs)

    annex = render_annex(fset, summary, flow, rollup, obs, stats, facts, config)
    facts_csv = _csv_text([f.as_row() for f in facts], FACT_COLUMNS)
    cp_csv = _csv_text(rollup, CP_COLUMNS)

    recon = dict(stats)
    recon.update({"value_in": flow["value_in"], "value_out": flow["value_out"],
                  "self_transfer_count": flow["self_count"],
                  "counterparty_count": flow["counterparty_count"]})
    manifest = build_manifest(
        FRAMEWORK, {"set_id": fset.set_id, "address": fset.address, "chain": fset.chain},
        facts,
        {"annex.md": sha256_text(annex), "facts.csv": sha256_text(facts_csv),
         "counterparties.csv": sha256_text(cp_csv)},
        recon, generated_utc=generated_utc)

    return EvidencePack(fset.set_id, fset.address, fset.chain, facts, flow, rollup,
                        obs, recon, annex, facts_csv, cp_csv, manifest)


def write_pack(pack: EvidencePack, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "annex.md"), "w").write(pack.annex_md)
    open(os.path.join(out_dir, "facts.csv"), "w").write(pack.facts_csv)
    open(os.path.join(out_dir, "counterparties.csv"), "w").write(pack.counterparties_csv)
    json.dump(pack.manifest, open(os.path.join(out_dir, "evidence-manifest.json"), "w"),
              indent=2)


# --------------------------------------------------------------------------------
# live mode (OPTIONAL — never exercised in CI; degrades gracefully offline)
# --------------------------------------------------------------------------------

def fetch_json(url: str, timeout: int = 30, offline: bool = False):
    """Fetch a URL and parse JSON. Returns (payload, body_bytes) on success or
    None on ANY failure (offline, timeout, HTTP error, bad JSON) — a fetch failure
    is a normal, handled condition, never an exception. With offline=True it
    returns None without touching the network at all."""
    if offline:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "analyst-toolkit-osint/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
        return json.loads(body.decode("utf-8")), body
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None


def _now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect_live_evm(base_url: str, address: str, offline: bool = False,
                     max_pages: int = 10, page_size: int = 100):
    """Capture one EVM address from a user-supplied Blockscout-style explorer.
    There is NO default endpoint — the caller chooses whom to query and owns that
    source's usage terms. Returns a FixtureSet, or None if anything fails."""
    if not base_url:
        return None
    caps = []

    def grab(kind, url):
        got = fetch_json(url, offline=offline)
        if got is None:
            return None
        _, body = got
        caps.append(Capture(kind=kind, url=url, retrieved_at_utc=_now_utc(), body=body))
        return got[0]

    p = grab("evm_balance", "%s/api?module=account&action=balance&address=%s" % (base_url, address))
    if p is None:
        return None
    for action, kind in (("txlist", "evm_txlist"), ("tokentx", "evm_tokentx")):
        for page in range(1, max_pages + 1):
            url = ("%s/api?module=account&action=%s&address=%s&page=%d&offset=%d&sort=asc"
                   % (base_url, action, address, page, page_size))
            p = grab(kind, url)
            if p is None:
                return None
            if len(p.get("result") or []) < page_size:
                break
    return FixtureSet(set_id="live-%s" % address.lower()[:12], address=address,
                      chain="evm", captures=caps)


def collect_live_btc(base_url: str, address: str, offline: bool = False,
                     max_pages: int = 10):
    """Capture one BTC address from a user-supplied mempool-style explorer.
    Same posture as collect_live_evm: no default endpoint, None on any failure."""
    if not base_url:
        return None
    caps = []
    url = "%s/api/address/%s" % (base_url, address)
    got = fetch_json(url, offline=offline)
    if got is None:
        return None
    caps.append(Capture(kind="btc_summary", url=url, retrieved_at_utc=_now_utc(),
                        body=got[1]))
    last_txid = None
    for _ in range(max_pages):
        url = "%s/api/address/%s/txs" % (base_url, address)
        if last_txid:
            url += "/chain/%s" % last_txid
        got = fetch_json(url, offline=offline)
        if got is None:
            return None
        payload, body = got
        caps.append(Capture(kind="btc_txs", url=url, retrieved_at_utc=_now_utc(),
                            body=body))
        if not payload:
            break
        last_txid = payload[-1]["txid"]
        if len(payload) < 25:
            break
    return FixtureSet(set_id="live-%s" % address.lower()[:12], address=address,
                      chain="btc", captures=caps)


# --------------------------------------------------------------------------------
# CLI — process one fixture set ad hoc
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    HERE = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Build an evidence pack from one fixture set.")
    ap.add_argument("fixture_dir", nargs="?",
                    default=os.path.join(HERE, "fixtures", "sample", "evm-sample-01"),
                    help="fixture set directory (default: the committed EVM sample)")
    ap.add_argument("--out", default=None, help="write annex/CSVs/manifest here")
    args = ap.parse_args()
    fs = load_fixture_set(args.fixture_dir)
    pk = build_pack(fs, Config(), generated_utc=_now_utc())
    comp = completeness(pk.facts)
    print("set %s (%s %s): %d facts (provenance complete %.1f%%), "
          "%d counterparties, %d observations, %d duplicates removed"
          % (pk.set_id, pk.chain, pk.address, comp["total_facts"],
             100 * comp["complete_rate"], len(pk.counterparties),
             len(pk.observations), pk.stats["duplicates_removed"]))
    if args.out:
        write_pack(pk, args.out)
        print("evidence pack written ->", args.out)
    else:
        print()
        print(pk.annex_md)
