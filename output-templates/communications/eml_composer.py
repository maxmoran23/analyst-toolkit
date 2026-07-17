#!/usr/bin/env python3
"""
Compose RFC 5322 .eml draft files from a JSON spec. Standard library only.

Usage
-----
    python3 eml_composer.py spec.json               # write drafts to ./drafts
    python3 eml_composer.py spec.json --outdir out  # choose the output folder
    python3 eml_composer.py --sample                # print a demo spec to stdout
    python3 eml_composer.py --sample > spec.json    # ...and save it to edit

Spec format
-----------
A JSON array of draft objects (or an object with a "drafts" array). Fields per
draft — only "subject" plus at least one of "to" / "text_body" is required:

    {
      "to": ["ada@example.com"],          # string or list
      "cc": [], "bcc": [],                # optional, string or list
      "from": "me@example.com",           # optional
      "subject": "Q2 numbers",
      "text_body": "Plain-text body.",    # optional if html_body given
      "html_body": "<p>HTML body.</p>",   # optional; makes multipart/alternative
      "in_reply_to": "<id@example.com>",  # optional reply threading
      "references": "<a@x> <id@x>",       # optional reply threading
      "headers": {"X-Case": "1042"},      # optional extra headers
      "date": "Tue, 03 Mar 2026 09:00:00 -0500",  # optional; omitted = no Date
      "filename": "custom-name"           # optional; ".eml" appended
    }

Guarantees
----------
- DRAFTS ONLY. This tool writes files; it never sends. There is no smtplib
  import and no network code of any kind.
- DETERMINISTIC. No Date header unless the spec supplies one, no generated
  Message-ID, and fixed sequential MIME boundaries — the same spec always
  produces byte-identical files, so output is diffable across runs.
- X-Unsent: 1 is added by default so clients that honor it (notably Outlook)
  open the file in compose mode as an editable draft. Disable with --no-unsent.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from email import policy
from email.generator import BytesGenerator
from email.message import EmailMessage
from pathlib import Path

SAMPLE_SPEC = [
    {
        "from": "analyst@example.com",
        "to": ["ops-lead@example.com"],
        "cc": ["team@example.com"],
        "subject": "Draft: weekly vendor status note",
        "text_body": "Three vendors in flight; one moved to contracting this week.\n\nFull tracker attached separately.",
        "html_body": "<p>Three vendors in flight; <strong>one moved to contracting</strong> this week.</p><p>Full tracker attached separately.</p>",
    },
    {
        "from": "analyst@example.com",
        "to": "counterparty@example.com",
        "subject": "Re: renewal terms",
        "text_body": "Confirming the multi-year option locks current rates. Seat count to follow Friday.",
        "in_reply_to": "<20260310091400.12345@example.com>",
        "references": "<20260309100000.11111@example.com> <20260310091400.12345@example.com>",
        "headers": {"X-Case": "vendor-renewal"},
    },
]


def as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    return [str(v) for v in value if str(v).strip()]


def slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len].rstrip("-") or "draft"


def build_message(draft: dict, index: int, unsent: bool) -> EmailMessage:
    msg = EmailMessage(policy=policy.SMTP)

    text_body = draft.get("text_body", "")
    html_body = draft.get("html_body")
    msg.set_content(text_body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")
        # Replace the random MIME boundary with a fixed one for determinism.
        msg.set_boundary(f"====draft-{index:04d}-alt====")

    for field, header in (("from", "From"), ("subject", "Subject")):
        if draft.get(field):
            msg[header] = draft[field]
    for field, header in (("to", "To"), ("cc", "Cc"), ("bcc", "Bcc")):
        addrs = as_list(draft.get(field))
        if addrs:
            msg[header] = ", ".join(addrs)
    for field, header in (
        ("in_reply_to", "In-Reply-To"),
        ("references", "References"),
        ("date", "Date"),
    ):
        if draft.get(field):
            msg[header] = draft[field]
    for name, value in (draft.get("headers") or {}).items():
        msg[name] = str(value)
    if unsent:
        msg["X-Unsent"] = "1"
    return msg


def draft_filename(draft: dict, index: int) -> str:
    base = draft.get("filename") or f"{index:02d}-{slugify(draft.get('subject', ''))}"
    return base if base.endswith(".eml") else base + ".eml"


def load_spec(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("drafts", [])
    if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
        raise SystemExit("spec must be a JSON array of draft objects (or {'drafts': [...]})")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compose .eml draft files from a JSON spec. Writes drafts; never sends."
    )
    parser.add_argument("spec", nargs="?", help="path to the JSON spec")
    parser.add_argument("--outdir", default="drafts", help="output folder (default: ./drafts)")
    parser.add_argument("--sample", action="store_true", help="print a demo spec to stdout and exit")
    parser.add_argument(
        "--no-unsent", action="store_true",
        help="omit the X-Unsent: 1 header (clients then open files as received mail)",
    )
    args = parser.parse_args()

    if args.sample:
        print(json.dumps(SAMPLE_SPEC, indent=2))
        return 0
    if not args.spec:
        parser.error("supply a spec path, or --sample to see the format")

    drafts = load_spec(Path(args.spec))
    if not drafts:
        raise SystemExit("spec contains no drafts")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for i, draft in enumerate(drafts, start=1):
        if not draft.get("subject") and not draft.get("to") and not draft.get("text_body"):
            raise SystemExit(f"draft {i}: needs at least a subject, a recipient, or a body")
        msg = build_message(draft, i, unsent=not args.no_unsent)
        path = outdir / draft_filename(draft, i)
        with path.open("wb") as fh:
            BytesGenerator(fh, policy=policy.SMTP).flatten(msg)
        print(f"wrote {path}")

    print(f"{len(drafts)} draft(s) written to {outdir}/ - nothing was sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
