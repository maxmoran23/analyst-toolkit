"""
Public-list source registry + the reference parser (OFAC SDN CSV).

Each source declares its public URL, format, licence note, and a parser. One parser
is fully implemented — the OFAC SDN consolidated CSV, whose layout is published and
stable — as the reference. Additional lists (EU, UN, UK OFSI) are registered with
their real URLs, formats, and licence notes and the same normalized target; a
deployment supplies their parser the same way (yield `normalize_record(...)` dicts).
This is honest scoping: one verified parser, the rest configured sources — not stubs
that pretend to parse.

All public lists carry their own usage terms; the licence note records them. Nothing
here redistributes list data — it fetches at run time.
"""
from __future__ import annotations

import csv
import io
import re

ID_FIELDS = ("dob", "nationality", "country", "place_of_birth", "passport",
             "national_id", "registration", "imo", "tail_number", "wallet")


def normalize_record(uid, name, entity_type, program="", aliases=None, ids=None,
                     source=""):
    """Build a normalized watchlist record (the WatchlistEntry shape the scorers
    consume). Names/programs are kept as published; ids are upper-cased for stable
    comparison."""
    clean_ids = {k: str(v).strip().upper() for k, v in (ids or {}).items()
                 if v and k in ID_FIELDS}
    return {
        "uid": str(uid), "name": (name or "").strip(),
        "entity_type": entity_type or "ENTITY", "program": (program or "").strip(),
        "aliases": [a.strip() for a in (aliases or []) if a and a.strip()],
        "ids": clean_ids, "source": source,
    }


# --- OFAC SDN consolidated CSV (the reference parser) ---------------------------
# Published headerless layout (sdn.csv): the empty marker is the literal "-0-".
_OFAC_COLS = ["ent_num", "name", "sdn_type", "program", "title", "call_sign",
              "vess_type", "tonnage", "grt", "vess_flag", "vess_owner", "remarks"]
_OFAC_TYPE = {"individual": "INDIVIDUAL", "vessel": "VESSEL", "aircraft": "AIRCRAFT"}
_BLANK = {"-0-", "", None}

_DOB_RE = re.compile(r"DOB\s+([0-9]{1,2}\s+\w+\s+[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{4})", re.I)
_NAT_RE = re.compile(r"[Nn]ationality\s+([A-Za-z ]+?)(?:;|\.|$)")
_PASS_RE = re.compile(r"[Pp]assport\s+([A-Z0-9]+)")
_POB_RE = re.compile(r"POB\s+([^;.]+)")
_IMO_RE = re.compile(r"IMO\s+([0-9]{7})")
_TAIL_RE = re.compile(r"Aircraft Tail Number\s+([A-Z0-9-]+)", re.I)


def _clean(v):
    v = (v or "").strip()
    return "" if v in _BLANK else v


def _ids_from_remarks(remarks):
    ids = {}
    if not remarks:
        return ids
    m = _DOB_RE.search(remarks)
    if m:
        ids["dob"] = m.group(1).strip()
    m = _NAT_RE.search(remarks)
    if m:
        ids["nationality"] = m.group(1).strip()
    m = _PASS_RE.search(remarks)
    if m:
        ids["passport"] = m.group(1).strip()
    m = _POB_RE.search(remarks)
    if m:
        ids["place_of_birth"] = m.group(1).strip()
    m = _IMO_RE.search(remarks)
    if m:
        ids["imo"] = m.group(1).strip()
    m = _TAIL_RE.search(remarks)
    if m:
        ids["tail_number"] = m.group(1).strip()
    return ids


def parse_ofac_sdn(main_csv_text, alt_csv_text=None):
    """Parse the OFAC SDN consolidated CSV (and optional alternate-names alt.csv)
    into normalized records. Handles the published headerless positional layout."""
    aliases_by_ent = {}
    if alt_csv_text:
        for row in csv.reader(io.StringIO(alt_csv_text)):
            if len(row) >= 4:
                ent, alt_name = row[0].strip(), _clean(row[3])
                if alt_name:
                    aliases_by_ent.setdefault(ent, []).append(alt_name)

    records = []
    for row in csv.reader(io.StringIO(main_csv_text)):
        if not row or not row[0].strip().isdigit():
            continue  # skip headers / blank lines
        r = {c: (row[i] if i < len(row) else "") for i, c in enumerate(_OFAC_COLS)}
        ent = r["ent_num"].strip()
        name = _clean(r["name"])
        if not name:
            continue
        sdn_type = _clean(r["sdn_type"]).lower()
        etype = _OFAC_TYPE.get(sdn_type, "ENTITY")
        ids = _ids_from_remarks(_clean(r["remarks"]))
        if _clean(r["vess_flag"]):
            ids.setdefault("country", _clean(r["vess_flag"]))
        records.append(normalize_record(
            uid=f"OFAC-{ent}", name=name, entity_type=etype,
            program=_clean(r["program"]), aliases=aliases_by_ent.get(ent, []),
            ids=ids, source="OFAC_SDN"))
    return records


# --- source registry ------------------------------------------------------------
SOURCES = {
    "OFAC_SDN": {
        "name": "OFAC Specially Designated Nationals (SDN) consolidated list",
        "url": "https://www.treasury.gov/ofac/downloads/sdn.csv",
        "alt_url": "https://www.treasury.gov/ofac/downloads/alt.csv",
        "format": "csv",
        "licence": "U.S. Treasury / OFAC — public domain; published for screening use.",
        "parser": parse_ofac_sdn,
    },
    "EU_CFSP": {
        "name": "EU Consolidated Financial Sanctions list",
        "url": "https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content",
        "format": "csv/xml",
        "licence": "European Union — reuse permitted with attribution; confirm current terms.",
        "parser": None,  # configure with the published EU FSD schema; normalize_record(...)
    },
    "UN_CONSOLIDATED": {
        "name": "UN Security Council Consolidated Sanctions list",
        "url": "https://scsanctions.un.org/resources/xml/en/consolidated.xml",
        "format": "xml",
        "licence": "United Nations — public; confirm current terms of use.",
        "parser": None,  # configure with the UN consolidated XML schema
    },
    "UK_OFSI": {
        "name": "UK OFSI Consolidated List of financial sanctions targets",
        "url": "https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.csv",
        "format": "csv",
        "licence": "UK HM Treasury / OFSI — Open Government Licence; confirm current terms.",
        "parser": None,  # configure with the OFSI ConList column layout
    },
}


def configured_sources():
    """Source keys that ship a working parser (can be ingested live today)."""
    return [k for k, s in SOURCES.items() if s.get("parser")]
