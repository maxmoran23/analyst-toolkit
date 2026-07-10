"""
Provenance primitives for evidence-grade OSINT collection.

An investigation artifact is only as defensible as its provenance. When an analyst
assembles open-source evidence by hand — screenshots of a block explorer, copied
transaction hashes — the source URL, the retrieval time, and any proof the content
was not altered are usually lost. These primitives make provenance a structural
property of every emitted fact instead of an afterthought:

    EvidenceFact     one atomic, provenance-stamped statement of fact. Five
                     mandatory provenance fields ride along with the value itself:
                     fact_type, source_uri, retrieved_at_utc, content_sha256,
                     origin_id. A fact missing any of them is INCOMPLETE and a
                     consuming harness should refuse it.
    sha256 helpers   stamp raw capture bytes, text, or canonical JSON; combine
                     several digests into one order-independent digest for facts
                     DERIVED from multiple captures (a rollup row traces to the
                     exact source bytes it was computed from).
    completeness     the checker a validation harness gates on: every fact carries
                     every provenance field, well-formed.
    build_manifest   the evidence-manifest builder: fact census by type,
                     completeness, artifact digests, and reconciliation totals in
                     one machine-readable record that travels with the annex.

Pure standard library. Deterministic: the only wall-clock timestamp is the one the
caller explicitly injects into a manifest — nothing here reads the clock on its own,
so rendered evidence can be byte-identical across runs.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field

# The five provenance fields every fact must carry (value is the payload, not
# provenance). Order is the canonical CSV/report order.
PROVENANCE_FIELDS = ("fact_type", "origin_id", "source_uri", "retrieved_at_utc",
                     "content_sha256")

_SHA256_HEX_LEN = 64
_HEX_DIGITS = set("0123456789abcdef")


# --------------------------------------------------------------------------------
# sha256 stamping helpers
# --------------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    """Digest of raw capture bytes — stamp the response body exactly as retrieved."""
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_json(obj) -> str:
    """One canonical serialization (sorted keys, compact separators) so the same
    value always hashes and renders identically."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_json(obj) -> str:
    return sha256_text(canonical_json(obj))


def combine_sha256(digests) -> str:
    """One digest for a fact DERIVED from several source captures (a counterparty
    rollup, a flow summary). Sorted before hashing so the combined digest is
    order-independent: the same set of source captures always yields the same
    combined digest, and any change to any underlying capture changes it."""
    return sha256_text("\n".join(sorted(digests)))


# --------------------------------------------------------------------------------
# the fact record
# --------------------------------------------------------------------------------

@dataclass
class EvidenceFact:
    """One atomic, provenance-stamped fact extracted or derived from a capture.

    fact_type        what kind of statement this is (e.g. address_summary,
                     native_transaction, token_transfer, counterparty_rollup,
                     flow_summary, structural_observation)
    value            the normalized content (JSON-serializable; no floats — keep
                     amounts as integers or exact decimal strings)
    source_uri       the URI the content was retrieved from; for derived facts,
                     the contributing capture URIs joined with ";"
    retrieved_at_utc when the source content was retrieved (capture time, NOT run
                     time); for derived facts, the latest contributing capture time
    content_sha256   digest of the source capture bytes (or combine_sha256 of the
                     contributing captures for a derived fact) — the tamper-evidence
                     link from the fact back to the exact bytes it came from
    origin_id        locator of the originating element inside the source (e.g.
                     "tx:<hash>", "address:<addr>", "counterparty:<addr>")
    """
    fact_type: str
    value: object
    source_uri: str
    retrieved_at_utc: str
    content_sha256: str
    origin_id: str

    def missing_fields(self) -> list:
        """Provenance fields that are absent or malformed on this fact."""
        missing = []
        for f in PROVENANCE_FIELDS:
            v = getattr(self, f)
            if not isinstance(v, str) or not v.strip():
                missing.append(f)
        if "content_sha256" not in missing:
            h = self.content_sha256.lower()
            if len(h) != _SHA256_HEX_LEN or not set(h) <= _HEX_DIGITS:
                missing.append("content_sha256")
        return missing

    def is_complete(self) -> bool:
        return not self.missing_fields()

    def as_row(self) -> dict:
        """Flat row for a facts CSV: provenance fields + the canonical value."""
        return {
            "fact_type": self.fact_type,
            "origin_id": self.origin_id,
            "value": canonical_json(self.value),
            "source_uri": self.source_uri,
            "retrieved_at_utc": self.retrieved_at_utc,
            "content_sha256": self.content_sha256,
        }


# --------------------------------------------------------------------------------
# provenance-completeness checker (the gate)
# --------------------------------------------------------------------------------

def completeness(facts) -> dict:
    """Check that EVERY fact carries every provenance field, well-formed.

    Returns totals, the complete rate, and examples of incomplete facts — the
    validation harness gates on complete_rate == 1.0 (an unprovenance'd fact is
    not evidence, it is an assertion)."""
    facts = list(facts)
    incomplete = []
    for f in facts:
        miss = f.missing_fields()
        if miss:
            incomplete.append({"fact_type": f.fact_type, "origin_id": f.origin_id,
                               "missing": miss})
    total = len(facts)
    n_bad = len(incomplete)
    return {
        "total_facts": total,
        "complete": total - n_bad,
        "incomplete": n_bad,
        "complete_rate": round((total - n_bad) / total, 6) if total else 1.0,
        "incomplete_examples": incomplete[:5],
    }


# --------------------------------------------------------------------------------
# evidence-manifest builder
# --------------------------------------------------------------------------------

def build_manifest(framework: str, subject: dict, facts, artifact_digests: dict,
                   reconciliation: dict, generated_utc: str = "") -> dict:
    """Assemble the machine-readable evidence manifest that travels with an annex.

    subject            what the evidence pack is about (e.g. {"address":..., "chain":...})
    facts              the emitted EvidenceFact records
    artifact_digests   {artifact_name: sha256} of every rendered output file, so a
                       reviewer can verify the annex/CSVs they hold are the ones
                       this manifest describes
    reconciliation     the engine's tie-out totals (records seen, unique, duplicates
                       removed, value sums) — the numbers the harness verifies
                       against source truth
    generated_utc      the ONLY place a run timestamp belongs. The annex and CSVs
                       must stay byte-identical across runs; the manifest carries
                       the when. Caller-supplied so tests can pin it.
    """
    facts = list(facts)
    comp = completeness(facts)
    by_type = Counter(f.fact_type for f in facts)
    return {
        "framework": framework,
        "subject": dict(subject),
        "generated_utc": generated_utc,
        "facts": {
            "total": comp["total_facts"],
            "by_type": dict(sorted(by_type.items())),
            "provenance_complete": comp["complete"],
            "provenance_complete_rate": comp["complete_rate"],
        },
        "artifacts": dict(sorted(artifact_digests.items())),
        "reconciliation": dict(reconciliation),
    }
