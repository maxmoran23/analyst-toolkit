# Validation Scripts — Presentation-Sample Evidence

> **In plain terms:** Everything committed under [`../samples/presentations/`](../samples/presentations/)
> — the branded template, the injected output deck, the preview images, and the
> preservation report — can be rebuilt and re-checked with the scripts in this
> folder. Nothing in that sample set is a hand-made binary you have to take on
> trust.

## The scripts

| Script | Role | Dependencies |
| --- | --- | --- |
| [`scripts/create_branded_template.py`](scripts/create_branded_template.py) | Builds the fictional "Northstar Studio" branded `.pptx` fixture: custom theme colors and fonts, patched slide master with an embedded logo. | `python-pptx` |
| [`scripts/verify_theme_preservation.py`](scripts/verify_theme_preservation.py) | Package-level proof that an injected output deck left the template's theme, masters, layouts, fonts, colors, and logo unchanged — and that every added shape is a placeholder carrying the planned text. Run by CI on every push. | `python-pptx` |
| [`scripts/create_contact_sheet.py`](scripts/create_contact_sheet.py) | Deterministic RGB contact-sheet montage from rendered slide PNGs — produces the preview images committed alongside the sample decks. | `Pillow` |

## The reproduction pipeline

The committed sample set is the output of this sequence:

1. **Fixture** — `create_branded_template.py --logo <png> --output northstar-branded-template.pptx`
   builds the branded template. The committed template embeds the exact logo whose
   SHA-256 is recorded in the preservation report; to reproduce byte-comparable
   brand parts, extract it from the committed template first
   (`unzip -p northstar-branded-template.pptx ppt/media/northstar-logo.png`).
2. **Injection** — [`../output-templates/presentations/theme_preserving_deck.py`](../output-templates/presentations/theme_preserving_deck.py)
   adds the sample slide plan to the template, producing the injected output deck
   and its mapping audit.
3. **Verification** — `verify_theme_preservation.py --template ... --output ... --plan ... --json <out>.json --report <out>.md`
   compares the two packages part by part, writing the machine-readable check
   results (`--json`) and the markdown report behind
   [`../samples/presentations/THEME-PRESERVATION-REPORT.md`](../samples/presentations/THEME-PRESERVATION-REPORT.md) (`--report`).
   This step is wired into `.github/workflows/validate.yml`, so the committed
   template/output pair is re-proven on every push.
4. **Previews** — render each deck to per-slide PNGs with any Office-capable
   renderer (LibreOffice headless: `soffice --headless --convert-to png`), then
   `create_contact_sheet.py --input-dir <pngs> --output <montage>.png`.

Steps 1 and 4 are development-time only: CI re-runs the verification (step 3)
against the committed binaries, it does not rebuild them. The per-slide PNGs are
intermediate artifacts and are deliberately not committed — only the montages are.

## Why the fixture creator is a separate script

`create_branded_template.py` patches PowerPoint package XML directly (theme part,
slide master, relationships, content types) — that is the only way to construct a
custom-branded fixture from a stock template. The injector under
`output-templates/presentations/` never does this: it adds slides only through
template-owned layouts and writes only into existing placeholders. Keeping the
XML-patching code out of the injector is what makes the preservation claim
falsifiable — the tool being tested cannot touch the parts the verifier checks.

## Future hardening (roadmap, not built)

- **Layout-coverage benchmark** — score the injector against a library of
  synthetic branded templates and report fallback frequency by placeholder role,
  instead of proving preservation on one fixture.
- **Renderer round-trip in CI** — the committed sample was opened and exported by
  LibreOffice without repair; automating that round-trip would catch package
  corruption that part-level comparison cannot.

**Confidence: HIGH —** the committed sample set passed exact theme-byte
comparison, semantic master/layout comparison, placeholder-only inspection, and
independent office rendering; the pipeline above is the process that produced it.
