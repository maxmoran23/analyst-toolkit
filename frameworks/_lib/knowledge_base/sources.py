"""
Public-list source registry + the parsers that normalize each list.

Each source declares its public URL, format, licence note, and a parser. Three parsers
are fully implemented, each written against the live published document and verified
against it, not against a guessed schema:

  * OFAC SDN consolidated CSV  — headerless positional layout (the reference parser)
  * UN Security Council consolidated XML — CONSOLIDATED_LIST/{INDIVIDUALS,ENTITIES}
  * UK OFSI ConList CSV — one row per *name variant*, grouped by `Group ID`

The EU consolidated list remains registered without a parser: its published endpoint
answers 403 to an unauthenticated request (it requires a caller token), so there is no
document to write a verified parser against. That is honest scoping — a configured
source, not a stub that pretends to parse.

All public lists carry their own usage terms; the licence note records them. Nothing
here redistributes list data — it fetches at run time, and the parser self-tests run
against synthetic documents that reproduce each schema rather than real excerpts.
"""
from __future__ import annotations

import csv
import io
import re
import xml.etree.ElementTree as ET

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


# --- UN Security Council consolidated XML ---------------------------------------
# Structure (verified against the live document): <CONSOLIDATED_LIST> holds
# <INDIVIDUALS><INDIVIDUAL> and <ENTITIES><ENTITY>. Individual names arrive split
# across FIRST_NAME..FOURTH_NAME; an entity carries its whole name in FIRST_NAME.
_UN_NAME_PARTS = ("FIRST_NAME", "SECOND_NAME", "THIRD_NAME", "FOURTH_NAME")

# TYPE_OF_DOCUMENT is free text in several languages and sometimes carries an
# embedded newline ("National Identification\n   Number"). Match on normalized
# substrings, never on equality.
_UN_PASSPORT_TOKENS = ("passport", "passeport", "pasaporte")
_UN_NATIONAL_ID_TOKENS = ("national identification", "identity card", "identification number")

_WS_RE = re.compile(r"\s+")

# Any DTD declaration in an ingested document is refused before parsing.
#
# `xml.etree.ElementTree` does NOT resolve external entities — an XXE payload raises
# ParseError("undefined entity") rather than reading the file. It DOES expand internal
# entities, which is the billion-laughs / quadratic-blowup denial-of-service vector.
# The usual mitigation (`defusedxml`) is a third-party package, and this pillar is
# pure standard library by contract, so the stdlib-only equivalent is to refuse any
# document that declares a DTD at all. Entity expansion is impossible without one.
# The published UN document contains neither declaration, so nothing legitimate is
# rejected; a document that grew one would be a signal worth failing on regardless.
_DTD_RE = re.compile(r"<!\s*(DOCTYPE|ENTITY)\b", re.IGNORECASE)


def _squash(value):
    """Collapse all runs of whitespace (including embedded newlines) to one space."""
    return _WS_RE.sub(" ", (value or "")).strip()


def _safe_fromstring(xml_text):
    """Parse XML, refusing any document that carries a DTD. See `_DTD_RE`."""
    if _DTD_RE.search(xml_text):
        raise ValueError(
            "refusing to parse XML containing a DTD or entity declaration "
            "(entity-expansion denial-of-service vector)"
        )
    return ET.fromstring(xml_text)


def _un_dob(individual):
    """Extract a date of birth. The element is one of three published shapes:
    an exact DATE, a bare YEAR, or a FROM_YEAR/TO_YEAR range."""
    for dob in individual.findall("INDIVIDUAL_DATE_OF_BIRTH"):
        exact = _squash(dob.findtext("DATE"))
        if exact:
            return exact
        year = _squash(dob.findtext("YEAR"))
        if year:
            return year
        frm, to = _squash(dob.findtext("FROM_YEAR")), _squash(dob.findtext("TO_YEAR"))
        if frm and to:
            return f"{frm}-{to}"
        if frm:
            return frm
    return ""


def _un_place_of_birth(individual):
    for pob in individual.findall("INDIVIDUAL_PLACE_OF_BIRTH"):
        parts = [_squash(pob.findtext(t)) for t in ("CITY", "STATE_PROVINCE", "COUNTRY")]
        joined = ", ".join(p for p in parts if p)
        if joined:
            return joined
    return ""


def _un_documents(individual):
    """Map INDIVIDUAL_DOCUMENT entries onto the passport / national_id id fields."""
    ids = {}
    for doc in individual.findall("INDIVIDUAL_DOCUMENT"):
        number = _squash(doc.findtext("NUMBER"))
        if not number:
            continue
        kind = _squash(doc.findtext("TYPE_OF_DOCUMENT")).lower()
        if any(tok in kind for tok in _UN_PASSPORT_TOKENS):
            ids.setdefault("passport", number)
        elif any(tok in kind for tok in _UN_NATIONAL_ID_TOKENS):
            ids.setdefault("national_id", number)
    return ids


def _un_aliases(node, tag):
    """Alias elements are frequently present but empty — 168 of them in the live
    document. Skip the empties rather than emitting blank aliases."""
    out = []
    for alias in node.findall(tag):
        name = _squash(alias.findtext("ALIAS_NAME"))
        if name:
            out.append(name)
    return out


def parse_un_consolidated(xml_text, _alt_text=None):
    """Parse the UN Security Council consolidated sanctions XML into normalized
    records. Individuals and entities are both emitted; the UN list type (e.g.
    'DRC', 'Al-Qaida') is carried as the program.

    `_alt_text` is unused — `ingest_source` invokes every parser as
    `parser(main, alt)`, so the second parameter is part of the parser contract.
    """
    root = _safe_fromstring(xml_text)
    records = []

    for ind in root.findall("./INDIVIDUALS/INDIVIDUAL"):
        name = " ".join(
            p for p in (_squash(ind.findtext(t)) for t in _UN_NAME_PARTS) if p
        )
        if not name:
            continue
        ids = _un_documents(ind)
        nationality = ""
        nat = ind.find("NATIONALITY")
        if nat is not None:
            nationality = _squash(nat.findtext("VALUE"))
        if nationality:
            ids["nationality"] = nationality
        dob = _un_dob(ind)
        if dob:
            ids["dob"] = dob
        pob = _un_place_of_birth(ind)
        if pob:
            ids["place_of_birth"] = pob
        for addr in ind.findall("INDIVIDUAL_ADDRESS"):
            country = _squash(addr.findtext("COUNTRY"))
            if country:
                ids.setdefault("country", country)
                break
        records.append(normalize_record(
            uid=f"UN-{_squash(ind.findtext('DATAID'))}", name=name,
            entity_type="INDIVIDUAL", program=_squash(ind.findtext("UN_LIST_TYPE")),
            aliases=_un_aliases(ind, "INDIVIDUAL_ALIAS"), ids=ids,
            source="UN_CONSOLIDATED"))

    for ent in root.findall("./ENTITIES/ENTITY"):
        name = _squash(ent.findtext("FIRST_NAME"))
        if not name:
            continue
        ids = {}
        for addr in ent.findall("ENTITY_ADDRESS"):
            country = _squash(addr.findtext("COUNTRY"))
            if country:
                ids["country"] = country
                break
        records.append(normalize_record(
            uid=f"UN-{_squash(ent.findtext('DATAID'))}", name=name,
            entity_type="ENTITY", program=_squash(ent.findtext("UN_LIST_TYPE")),
            aliases=_un_aliases(ent, "ENTITY_ALIAS"), ids=ids,
            source="UN_CONSOLIDATED"))

    return records


# --- UK OFSI consolidated list (ConList.csv) ------------------------------------
# The published file opens with a "Last Updated,<date>" metadata line before the
# real header row. Each subsequent row is ONE NAME VARIANT, not one target: the
# live file carries ~19.7k rows across ~5.1k designations, keyed by `Group ID`.
# Parsing row-per-target is the single mistake that matters here — it would inflate
# the watchlist roughly fourfold with duplicate parties.
#
# `Alias Type` distinguishes the variants ('Primary name', 'Primary name variation',
# 'AKA', 'FKA'). A group is NOT guaranteed exactly one primary row: in the live file
# most have one, 297 have two, one has eighty, and two have none. So the canonical
# name is the FIRST primary-name row in file order, falling back to the group's first
# row; every other variant becomes an alias. That rule is total and deterministic.
_UK_TYPE = {"individual": "INDIVIDUAL", "entity": "ENTITY", "ship": "VESSEL"}
_UK_GIVEN_NAMES = ("Name 1", "Name 2", "Name 3", "Name 4", "Name 5")
_UK_FAMILY_NAME = "Name 6"
_UK_ID_COLUMNS = {
    "dob": "DOB",
    "nationality": "Nationality",
    "place_of_birth": "Town of Birth",
    "passport": "Passport Number",
    "national_id": "National Identification Number",
    "country": "Country",
}


def _uk_full_name(row, col):
    parts = [row[col[c]].strip() for c in _UK_GIVEN_NAMES if c in col]
    family = row[col[_UK_FAMILY_NAME]].strip() if _UK_FAMILY_NAME in col else ""
    if family:
        parts.append(family)
    return " ".join(p for p in parts if p)


def parse_uk_ofsi(csv_text, _alt_text=None):
    """Parse the UK OFSI consolidated list CSV into normalized records, one record
    per `Group ID` (a designated target) rather than one per name variant.

    `_alt_text` is unused — see `parse_un_consolidated` on the parser contract.
    """
    rows_by_group = {}
    order = []
    header = None
    col = {}

    for row in csv.reader(io.StringIO(csv_text)):
        if header is None:
            # Skip the leading "Last Updated" metadata line; the header is the first
            # row that declares Group ID.
            if "Group ID" in row:
                header = row
                col = {name: i for i, name in enumerate(header)}
            continue
        if not row or len(row) < len(header) or not any(c.strip() for c in row):
            continue
        gid = row[col["Group ID"]].strip()
        if not gid:
            continue
        if gid not in rows_by_group:
            rows_by_group[gid] = []
            order.append(gid)
        rows_by_group[gid].append(row)

    if header is None:
        return []

    records = []
    for gid in order:
        group = rows_by_group[gid]
        primary = next(
            (r for r in group if r[col["Alias Type"]].strip() == "Primary name"),
            group[0],
        )
        name = _uk_full_name(primary, col)
        if not name:
            continue

        aliases, seen = [], {name}
        for row in group:
            variant = _uk_full_name(row, col)
            if variant and variant not in seen:
                seen.add(variant)
                aliases.append(variant)

        # Take each identifier from the primary row, falling back to the first
        # variant row that supplies one — designation detail is often carried on a
        # non-primary row.
        ids = {}
        for field, column in _UK_ID_COLUMNS.items():
            if column not in col:
                continue
            value = primary[col[column]].strip()
            if not value:
                value = next((r[col[column]].strip() for r in group if r[col[column]].strip()), "")
            if value:
                ids[field] = value

        group_type = primary[col["Group Type"]].strip().lower() if "Group Type" in col else ""
        records.append(normalize_record(
            uid=f"UK-{gid}", name=name, entity_type=_UK_TYPE.get(group_type, "ENTITY"),
            program=primary[col["Regime"]].strip() if "Regime" in col else "",
            aliases=aliases, ids=ids, source="UK_OFSI"))

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
        # No parser by design, not by omission: the endpoint answers 403 to an
        # unauthenticated request (the EU FSD requires a caller token), so there is no
        # published document to verify a parser against. Supply a token and the FSD
        # schema, then a parser that yields normalize_record(...) dicts.
        "parser": None,
    },
    "UN_CONSOLIDATED": {
        "name": "UN Security Council Consolidated Sanctions list",
        "url": "https://scsanctions.un.org/resources/xml/en/consolidated.xml",
        "format": "xml",
        "licence": "United Nations — public; confirm current terms of use.",
        "parser": parse_un_consolidated,
    },
    "UK_OFSI": {
        "name": "UK OFSI Consolidated List of financial sanctions targets",
        "url": "https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.csv",
        "format": "csv",
        "licence": "UK HM Treasury / OFSI — Open Government Licence; confirm current terms.",
        "parser": parse_uk_ofsi,
    },
}


def configured_sources():
    """Source keys that ship a working parser (can be ingested live today)."""
    return [k for k, s in SOURCES.items() if s.get("parser")]
