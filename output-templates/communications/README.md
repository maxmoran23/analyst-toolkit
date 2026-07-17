# Communication Templates

Templates and formatting standards for sharing analytical work with other people —
by email or in a team channel. Both are reusable design systems: you bring the content,
the template supplies the structure.

## What's here

| File | What it is |
|------|------------|
| `html-email-template.md` | A design system for HTML emails — dark header, indigo accent, table-based layout that renders reliably across email clients. Includes a color palette, typography scale, a copy-paste base template, a component library (data tables, severity badges, callout boxes, metric rows, checklists), and example section layouts for daily briefs, digests, weekly reviews, and report deliveries. |
| `structured-update-formatting.md` | A formatting standard for posting a status update or analytical finding to a team channel (Slack, Teams, Discord, a wiki). Covers the header line, summary dashboard, score bars, finding cards, data tables, alerts, threading discipline, and persistent-dashboard formatting — all in plain markdown that renders anywhere. |
| `eml_composer.py` | A runnable, stdlib-only Python composer: reads a JSON spec (array of drafts — to/cc/bcc/subject/text and optional HTML body, reply-threading headers) and writes one RFC 5322 `.eml` file per draft, openable as an editable draft in any standards-compliant mail client. Deterministic output (no auto-generated Date or Message-ID, fixed MIME boundaries) so re-runs are diffable. `--sample` prints a demo spec. Drafts only — it contains no sending code. |

## How to use with an AI assistant

Each file is a spec, not a finished message. Hand it to an AI assistant along with your
content:

- *"Build an HTML email using this design system — header 'Q2 Review', a summary box, a
  findings section as a bullet list with severity badges, and a comparison table. Inline
  all styles."*
- *"Format this analysis as a structured channel update following this guide — header
  line, summary dashboard, three finding cards, and a footer."*

The assistant assembles the message from the components; you review and send.

## Choosing between them

- **Email** — formal delivery, an external or wide audience, a deliverable that should
  look polished in an inbox, or anything that needs to stand alone outside a chat tool.
- **Structured channel update** — a team workspace, a recurring status post, a quick
  finding, or anything where scannability in the channel feed matters most.

A common pattern: post the structured update to the team channel for visibility, and
send the email version for the formal record or the wider distribution.

## Note on rendering

Email clients and chat platforms each render differently. The HTML email template uses
table-based layout and inline styles specifically for cross-client reliability — still,
test in your target client before sending. The structured-update format uses only basic
markdown so it degrades gracefully across platforms.
