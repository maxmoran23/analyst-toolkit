"""
Snapshot delta detection.

A knowledge base earns "self-maintaining" by tracking what changed between refreshes:
which designations were ADDED, which were REMOVED (delisted), and which were AMENDED
(a new alias, a new program, a new identifier). This is also the ongoing-monitoring
evidence a reviewer expects — proof the list is refreshed and its changes are logged.

Each resolved entity gets a stable identity KEY (a strong identifier if it has one,
else its normalized canonical name) and a content FINGERPRINT (everything else). Same
key + changed fingerprint = an amendment.
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from _lib.text_normalize import normalize  # noqa: E402

_STRONG = ("passport", "national_id", "registration", "imo", "tail_number", "wallet", "dob")


def identity_key(entity):
    for f in _STRONG:
        v = entity.get("ids", {}).get(f)
        if v:
            return f"{f}:{v}"
    return f"name:{normalize(entity['name'])}"


def fingerprint(entity):
    parts = [
        entity.get("entity_type", ""),
        entity.get("program", ""),
        "|".join(sorted(f"{k}={v}" for k, v in entity.get("ids", {}).items())),
        "|".join(sorted(normalize(a) for a in entity.get("aliases", []))),
        normalize(entity["name"]),
    ]
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]


def diff(prev_entities, new_entities):
    """Return {added, removed, amended}. `amended` items carry the key and a short
    list of what changed (program / aliases / ids / name)."""
    prev = {identity_key(e): e for e in prev_entities}
    new = {identity_key(e): e for e in new_entities}
    added = [new[k] for k in new if k not in prev]
    removed = [prev[k] for k in prev if k not in new]
    amended = []
    for k in new:
        if k in prev and fingerprint(prev[k]) != fingerprint(new[k]):
            a, b = prev[k], new[k]
            changes = []
            if a.get("program") != b.get("program"):
                changes.append("program")
            if set(map(normalize, a.get("aliases", []))) != set(map(normalize, b.get("aliases", []))):
                changes.append("aliases")
            if a.get("ids") != b.get("ids"):
                changes.append("identifiers")
            if normalize(a["name"]) != normalize(b["name"]):
                changes.append("name")
            amended.append({"key": k, "name": b["name"], "changes": changes})
    return {"added": added, "removed": removed, "amended": amended}


def summary(d):
    return {"added": len(d["added"]), "removed": len(d["removed"]), "amended": len(d["amended"])}
