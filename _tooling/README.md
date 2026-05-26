# `_tooling/` — maintenance scripts

These scripts maintain the `standalone/` directory. End users do not need to run them — `standalone/*.md` files are already fully populated.

## What's here

| File | Purpose |
|---|---|
| `universal_renderer_appendix.md` | The "Render as a formatted deliverable" block (~700 lines) appended to every standalone file. Edit this single file to evolve the Word / Excel / PDF / HTML rendering instructions across the whole library at once. |
| `append_renderer.py` | Idempotent script that re-builds every `standalone/*.md` by appending the universal appendix + per-file customization block. Per-file customizations are inline in the script's `PER_FILE` dict. Safe to re-run — replaces the prior appendix in each file rather than duplicating it. |
| `validate_embedded.py` | Sanity-checks every fenced code block in `standalone/*.md`: Python blocks parse with `ast`, HTML blocks parse with `html.parser`. Catches syntax drift in the embedded templates. |

## When to re-run

- After editing `universal_renderer_appendix.md` (style change, new color, palette update): `python3 _tooling/append_renderer.py .` from the repo root.
- After editing a per-file customization in `append_renderer.py`'s `PER_FILE` dict: same command.
- Before committing changes to `standalone/`: `python3 _tooling/validate_embedded.py standalone/` to make sure nothing parses badly.

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
