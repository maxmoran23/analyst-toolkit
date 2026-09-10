#!/usr/bin/env python3
"""Run the repository's local Python quality gates from any directory.

Default checks validate portable content, navigation, generation drift, and tooling
regressions. --full also reproduces framework evidence and reference data. Kotlin
parity and the presentation runtime remain dedicated CI jobs.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
CHECKS = [
    ("Tooling regression tests", ["-m", "unittest", "discover", "-s", "_tooling/tests", "-v"]),
    ("Framework input boundaries", ["-m", "unittest", "discover", "-s", "frameworks", "-p", "test_boundaries.py"]),
    ("Quant regressions", ["-m", "unittest", "discover", "-s", "quant", "-p", "test_*.py"]),
    ("Two-file rule", ["_tooling/validate_self_containment.py"]),
    ("BASE generation", ["_tooling/build_base.py", "--check"]),
    ("Standalone embedded code", ["_tooling/validate_embedded.py", "standalone"]),
    ("Methodology embedded code", ["_tooling/validate_embedded.py", "methodology"]),
    ("Relative links", ["_tooling/validate_links.py"]),
    ("Index and count claims", ["_tooling/validate_index.py"]),
    ("Public content hygiene", ["_tooling/validate_hygiene.py"]),
    ("Naming and cousin map", ["_tooling/validate_naming.py"]),
    ("Generated briefs", ["_tooling/build_briefs.py", "--check"]),
    ("Generated demos", ["_tooling/build_demos.py", "--check"]),
    ("Adaptive dashboard", ["_tooling/validate_adaptive_dashboard.py"]),
    ("Evidence index", ["_tooling/build_evidence_index.py", "--check"]),
]
FULL_CHECKS = [
    ("Evidence reproduction", ["_tooling/verify_evidence.py"]),
    ("Reference data reproduction", ["_tooling/build_reference_data.py", "--check"]),
]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="Reproduce all committed evidence and reference data")
    args = parser.parse_args(argv)
    checks = CHECKS + (FULL_CHECKS if args.full else [])
    failed = []
    for label, command in checks:
        print(f"\n--- {label} ---", flush=True)
        result = subprocess.run([sys.executable, *command], cwd=ROOT)
        if result.returncode:
            failed.append(label)
    print(f"\n{len(checks) - len(failed)}/{len(checks)} checks passed.", flush=True)
    if failed:
        print("Failed: " + ", ".join(failed), file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
