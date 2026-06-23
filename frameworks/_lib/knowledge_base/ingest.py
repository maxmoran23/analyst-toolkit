"""
Fetch + parse a public list into normalized records, with graceful degradation.

Network is optional and isolated here. `ingest_source` returns a list of normalized
records on success, or None when the source cannot be ingested (offline, fetch
failure, or no configured parser) — the caller then falls back to synthetic data so
the pipeline always runs. Nothing here caches or redistributes list data.
"""
from __future__ import annotations

import urllib.request
import urllib.error

from .sources import SOURCES


def fetch_text(url, timeout=30):
    """Fetch a URL as text. Returns None on any failure (offline, timeout, HTTP
    error) — fetch failure is a normal, handled condition, not an exception."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "analyst-toolkit-kb/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None


def ingest_source(key, offline=False, timeout=30):
    """Ingest one registered source into normalized records.

    Returns None (signalling "fall back to synthetic / skip") when offline, when the
    source has no configured parser yet, or when the fetch or parse fails. Returns a
    list of records on success.
    """
    src = SOURCES.get(key)
    if not src:
        raise KeyError(f"unknown source: {key}")
    if offline or not src.get("parser"):
        return None
    main = fetch_text(src["url"], timeout)
    if main is None:
        return None
    alt = fetch_text(src["alt_url"], timeout) if src.get("alt_url") else None
    try:
        return src["parser"](main, alt)
    except Exception:
        return None


def ingest_all(offline=False, timeout=30):
    """Ingest every configured source. Returns {source_key: records} for those that
    ingested successfully (sources that return None are omitted)."""
    out = {}
    for key in SOURCES:
        recs = ingest_source(key, offline=offline, timeout=timeout)
        if recs:
            out[key] = recs
    return out
