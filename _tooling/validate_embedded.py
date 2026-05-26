#!/usr/bin/env python3
"""
Extract every fenced code block from a standalone file and validate it:
  - python blocks: parse with ast
  - html blocks: load with html.parser
  - bash blocks: skipped (would need shellcheck)
Templates contain literal {{PLACEHOLDER}} tokens — these are valid Python
identifier characters surrounded by braces, but braces inside Python strings
are fine. We're checking for actual syntax errors, not template rendering.
"""
import ast
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

class Strict(HTMLParser):
    def __init__(self): super().__init__(); self.errors = []
    def error(self, msg): self.errors.append(msg)

def extract_blocks(text):
    pattern = r"```(\w+)\n(.*?)```"
    return [(lang, body) for lang, body in re.findall(pattern, text, flags=re.DOTALL)]

def validate(path):
    text = Path(path).read_text()
    blocks = extract_blocks(text)
    errors = []
    counts = {"python": 0, "html": 0, "bash": 0, "text": 0, "other": 0}
    for lang, body in blocks:
        counts[lang] = counts.get(lang, 0) + 1
        if lang == "python":
            try:
                ast.parse(body)
            except SyntaxError as e:
                errors.append(f"PYTHON SYNTAX in {path}: {e}")
        elif lang == "html":
            parser = Strict()
            try:
                parser.feed(body); parser.close()
            except Exception as e:
                errors.append(f"HTML PARSE in {path}: {e}")
            if parser.errors:
                errors.extend(f"HTML {path}: {e}" for e in parser.errors)
    return counts, errors

def main():
    standalone = Path(sys.argv[1] if len(sys.argv) > 1 else "standalone")
    total = {"python": 0, "html": 0, "bash": 0, "text": 0, "other": 0}
    all_errors = []
    for f in sorted(standalone.glob("*.md")):
        if f.name == "README.md": continue
        counts, errors = validate(f)
        for k,v in counts.items(): total[k] = total.get(k, 0) + v
        all_errors.extend(errors)
    print(f"Block counts across all standalone files: {total}")
    if all_errors:
        print(f"\n{len(all_errors)} errors:")
        for e in all_errors[:20]:
            print(f"  {e}")
        return 1
    print("\nAll embedded code blocks parsed cleanly.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
