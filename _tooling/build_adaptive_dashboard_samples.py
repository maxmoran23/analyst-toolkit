#!/usr/bin/env python3
"""Build deterministic adaptive-dashboard samples from synthetic JSON fixtures."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "output-templates" / "dashboards" / "adaptive-dashboard.html"
FIXTURES = ROOT / "samples" / "dashboards" / "fixtures"
SAMPLES = {
    "24-month-time-series.json": "24-month-time-series-sample.html",
    "four-column-categories.json": "four-column-categories-sample.html",
    "mixed-material.json": "mixed-material-sample.html",
}
START = "const EMBEDDED_INPUT = /*__EMBEDDED_INPUT__*/ "
END = ";\nconst RAW_INPUT = window.ADAPTIVE_DASHBOARD_INPUT || EMBEDDED_INPUT;"


def safe_script_json(value: object) -> str:
    """Serialize data for a script element without allowing an end-tag breakout."""

    return (
        json.dumps(value, ensure_ascii=False, indent=2)
        .replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render(template: str, value: object) -> str:
    prefix, marker, remainder = template.partition(START)
    if not marker:
        raise ValueError(f"input marker missing from {TEMPLATE}")
    _default, end, suffix = remainder.partition(END)
    if not end:
        raise ValueError(f"input terminator missing from {TEMPLATE}")
    return prefix + START + safe_script_json(value) + END + suffix


def main() -> int:
    template = TEMPLATE.read_text(encoding="utf-8")
    destination = ROOT / "samples" / "dashboards"
    destination.mkdir(parents=True, exist_ok=True)
    for fixture_name, sample_name in SAMPLES.items():
        value = json.loads((FIXTURES / fixture_name).read_text(encoding="utf-8"))
        output = destination / sample_name
        output.write_text(render(template, value), encoding="utf-8")
        print(f"wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

