# Presentation Templates

One domain-neutral tool for adding supplied material to an existing branded
PowerPoint template without changing its visual system.

| File | What it provides |
| --- | --- |
| [`theme_preserving_deck.py`](theme_preserving_deck.py) | `python-pptx` injector that selects template-owned layouts, adds slides through those layouts, and writes only into existing placeholders. |

## Contract

- Input: an existing `.pptx`/`.potx` and a normalized JSON slide plan.
- Output: a `.pptx` plus a layout/placeholder mapping audit.
- Preserved: themes, masters, layouts, theme colors, theme fonts, backgrounds,
  logos, and placeholder styling.
- Fallback: the nearest usable template layout, recorded in the audit; no
  fabricated layout or restyling.

The sample template, injected output, rendered previews, and package-level
preservation evidence are under [`../../samples/presentations/`](../../samples/presentations/).
The full reproduction pipeline for that sample set — fixture builder, CI-run
preservation verifier, and preview montage builder — is documented in
[`../../validation/README.md`](../../validation/README.md).

**Confidence: HIGH — the delivered sample passed exact theme-byte comparison,
semantic master/layout comparison, placeholder-only inspection, and independent
office rendering.**
