# `_tooling/` — maintenance scripts and CI gates

Two kinds of script live here: **builders** that maintain generated files (`standalone/`, `BASE.md`, the run-time contract), and **validators** that fail the build when something drifts. End users need neither — `standalone/*.md` and `BASE.md` are already fully populated.

## What's here

### Builders

| File | Purpose |
|---|---|
| `append_renderer.py` | Idempotent script that re-builds every `standalone/*.md` by appending the renderer block (extracted from `methodology/report-templates.md` between `<!-- BEGIN_RENDERER_APPENDIX -->` and `<!-- END_RENDERER_APPENDIX -->` sentinels) plus a per-file customization block. Per-file customizations are inline in the script's `PER_FILE` dict. Safe to re-run — replaces the prior appendix in each file rather than duplicating it. |
| `build_base.py` | Assembles the repo-root `BASE.md` (the single universal companion file) from the four `methodology/` sources — the three discipline files concatenated as Parts 1-3 with sibling links rewritten to in-file references, plus the sentinel-delimited renderer block as Part 4. `--check` mode rebuilds in memory and exits non-zero if `BASE.md` has drifted (CI gate). Never hand-edit `BASE.md`. |
| `apply_runtime_contract.py` | Idempotently stamps every `prompts/<category>/*.md` with the two-file-rule contract: a `**Run-time needs**` row in the metadata table and a `<!-- RUNTIME_CONTRACT -->` footer. Re-run after adding or editing any prompt file. |

### Validators (all are CI gates; all exit non-zero on violation)

| File | Guards | Purpose |
|---|---|---|
| `validate_embedded.py` | the templates | Sanity-checks every fenced code block in a directory: Python blocks parse with `ast`, HTML blocks parse with `html.parser`. Catches syntax drift in the embedded templates. Run against `standalone/` or `methodology/`. |
| `validate_self_containment.py` | the two-file rule | No repo-file references inside any paste payload, the run-time contract present in every prompt file, standalone files reference nothing, and no file instructs attaching a companion other than `BASE.md`. Prints the per-feature pairing budget (must be ≤ 2 everywhere). |
| `validate_links.py` | navigation | Every relative markdown link in the repository resolves to a real path. The `teams/` hubs and prompt catalogs are pure navigation; a renamed target breaks them silently, because markdown still renders a dead link. |
| `validate_index.py` | the indexes and the counts | Every prompt, hub, and framework is linked from its index; every framework package ships the fixed file set; and every registered numeric claim in the docs (`68 prompts`, `13 categories`, `13 engines`, `15 hubs`) matches the count derived from disk. Claims are registered explicitly, so rewording a sentence fails the gate rather than silently un-checking its number. |
| `validate_hygiene.py` | the public surface | No leak shapes anywhere (Slack workspace IDs, home-directory paths, private-fleet paths, credential shapes) and no emoji on the portable text surface. Rendered sample dashboards are exempt from the emoji rule for a documented reason, reported on every run rather than hidden. |

### Why the validators exist

The framework harnesses under `frameworks/*/run_validation.py` guard the *engines* — they fail the build if a scoring engine ever auto-clears a true positive. Nothing guarded the *prose about* the engines. Every defect the three navigation validators catch has shipped to `main` at least once: a README advertising 39 prompts after 68 existed, a team hub promising a capability that had already shipped, an engine no index linked to. They apply the harness philosophy to documentation — derive the truth from the filesystem, then fail when a document disagrees.

Run them all locally before a push:

```bash
python3 _tooling/validate_self_containment.py
python3 _tooling/validate_links.py
python3 _tooling/validate_index.py
python3 _tooling/validate_hygiene.py
python3 _tooling/build_base.py --check
```

The renderer content itself **lives in `methodology/report-templates.md`** (the 4th methodology file), not here. That file is the single source of truth — the script extracts its body between the sentinels and embeds that body into every standalone file.

## When to re-run

- After editing the renderer section in `methodology/report-templates.md` (style change, new color, palette update, fix to a code skeleton): `python3 _tooling/append_renderer.py .` from the repo root.
- After editing a per-file customization in `append_renderer.py`'s `PER_FILE` dict: same command.
- Before committing changes to `standalone/` or `methodology/report-templates.md`: `python3 _tooling/validate_embedded.py standalone` and `python3 _tooling/validate_embedded.py methodology` to make sure nothing parses badly.

## Why the script approach instead of hand-editing each standalone file

The universal appendix is ~700 lines and identical across 9 files. Hand-editing it 9 times invites drift — a small change to a Python skeleton or a hex color in one file but not the others, and the library becomes inconsistent. The script keeps the universal block authoritative in one place; each standalone file is the universal block + a small per-file customization at the end. Re-running the script after any change keeps everything in sync.

## Optional install for testing the generated artifacts

```bash
pip install python-docx openpyxl reportlab
```

Then to actually run one of the Word / Excel / PDF generators from any standalone file end-to-end:

```bash
# Extract a python block and run it in a temp dir
python3 -c "
import re, subprocess, tempfile, pathlib
text = pathlib.Path('standalone/entity-risk-assessment.md').read_text()
blocks = re.findall(r'\`\`\`python\n(.*?)\`\`\`', text, flags=re.DOTALL)
with tempfile.TemporaryDirectory() as td:
    s = pathlib.Path(td)/'gen.py'; s.write_text(blocks[0])
    print(subprocess.run(['python3', str(s)], cwd=td, capture_output=True, text=True).stdout)
    print('produced:', list(pathlib.Path(td).iterdir()))
"
```
