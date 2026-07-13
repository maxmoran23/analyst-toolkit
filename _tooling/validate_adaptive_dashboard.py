#!/usr/bin/env python3
"""Static, deterministic checks for the adaptive dashboard deliverables."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from build_adaptive_dashboard_samples import END, FIXTURES, ROOT, SAMPLES, START, render


TEMPLATE = ROOT / "output-templates" / "dashboards" / "adaptive-dashboard.html"
PROMPT = ROOT / "standalone" / "data-to-dashboard.md"
EXACT_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"


def check(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS: {message}")
    else:
        failures.append(message)
        print(f"FAIL: {message}")


def embedded_value(html: str) -> object:
    _prefix, marker, remainder = html.partition(START)
    if not marker:
        raise ValueError("embedded input marker missing")
    payload, end, _suffix = remainder.partition(END)
    if not end:
        raise ValueError("embedded input terminator missing")
    return json.loads(payload)


def main() -> int:
    failures: list[str] = []
    check(TEMPLATE.is_file(), "adaptive template exists", failures)
    check(PROMPT.is_file(), "standalone paste payload exists", failures)
    if not TEMPLATE.is_file():
        return 1

    template = TEMPLATE.read_text(encoding="utf-8")
    forbidden_dom_api = "inner" + "HTML"
    check(forbidden_dom_api not in template, "template avoids string-to-markup DOM mutation", failures)
    check("document.createElement" in template and ".textContent" in template, "dynamic content uses element creation and text nodes", failures)
    check(template.count(EXACT_CDN) == 1, "Chart.js is pinned to 4.4.1", failures)
    check("width: min(100%, 1400px)" in template, "shell is capped at 1400px", failures)
    breakpoint_patterns = [
        r"grid-template-columns:\s*repeat\(5,\s*minmax\(0,\s*1fr\)\)",
        r"@media \(max-width:\s*1200px\).*?repeat\(3,\s*minmax\(0,\s*1fr\)\)",
        r"@media \(max-width:\s*900px\).*?repeat\(2,\s*minmax\(0,\s*1fr\)\)",
        r"@media \(max-width:\s*600px\).*?grid-template-columns:\s*minmax\(0,\s*1fr\)",
    ]
    check(all(re.search(pattern, template, re.S) for pattern in breakpoint_patterns), "responsive grid is exactly 5 -> 3 -> 2 -> 1", failures)
    check("data-theme=\"dark\"" in template and "theme-toggle" in template, "dark default and theme toggle are present", failures)
    check("Unparsed material" in template and "Source value ledger" in template, "lossless and unparsed fallbacks are present", failures)
    check(all(token not in template for token in ["document.write", "fetch(", "XMLHttpRequest", "WebSocket(", "eval(", "new Function("]), "template contains no active remote-data or code-evaluation APIs", failures)

    for fixture_name, sample_name in SAMPLES.items():
        fixture_path = FIXTURES / fixture_name
        sample_path = ROOT / "samples" / "dashboards" / sample_name
        check(fixture_path.is_file(), f"fixture exists: {fixture_name}", failures)
        check(sample_path.is_file(), f"sample exists: {sample_name}", failures)
        if not fixture_path.is_file() or not sample_path.is_file():
            continue
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        sample = sample_path.read_text(encoding="utf-8")
        check(sample == render(template, fixture), f"sample is deterministic and current: {sample_name}", failures)
        check(embedded_value(sample) == fixture, f"sample round-trips every source value: {sample_name}", failures)
        check(forbidden_dom_api not in sample, f"sample avoids string-to-markup DOM mutation: {sample_name}", failures)
        check(sample.count(EXACT_CDN) == 1, f"sample uses exact Chart.js pin: {sample_name}", failures)

    mixed_sample = ROOT / "samples" / "dashboards" / SAMPLES["mixed-material.json"]
    if mixed_sample.is_file():
        mixed_text = mixed_sample.read_text(encoding="utf-8")
        check("Preserve <not markup>" not in mixed_text and "Preserve \\u003cnot markup>" in mixed_text, "literal less-than characters are escaped inside script data", failures)

    if failures:
        print(f"\n{len(failures)} validation check(s) failed.", file=sys.stderr)
        return 1
    print("\nAll adaptive-dashboard static checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

