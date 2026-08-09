# Deployment

## Runtime

- CPython 3.12; standard library only
- No network calls, package installation, external list service, or model files
- Read-only code/reference directory; writable `data/` for controlled local output

## Offline verification

```bash
python3 -m unittest -v test_sanctions_ownership.py
python3 run_validation.py --seed 42 --true-blocked 160 --below 240 --unresolved 80 --trials 6
python3 run_validation.py --seed 42 --true-blocked 160 --below 240 --unresolved 80 --trials 6 --out data/rederived
python3 scorer.py --input reference-data/sample-input.json --output data/sample-output.json
```

Production validation must exit `0`; both gates must pass. `--out DIR` supports CI re-derivation and writes at least `metrics.json` and deterministic `VALIDATION-REPORT.md`, plus the manifest and CSV evidence.

## Integration

In the live repo, replace or redirect the bundled `_lib/ownership.py` import to the shared `frameworks/_lib/ownership.py` module while preserving the validated SHA-256-compatible implementation. Map authoritative ownership and sanctions data into the documented schema, retain source/as-of provenance, score candidates, and preserve all path and resolution evidence.

Route `BLOCKED_BY_OWNERSHIP` and `REVIEW` to authorized human decision-makers under current policy. The engine itself must not block, freeze, reject, file, report, or off-board.

## Controls

- Refresh and reconcile sanctioned seed sets through an authorized external process.
- Validate ownership edge direction, fractional conversion, identity mapping, and as-of date.
- Require source-backed completeness, opacity, and nominee declarations.
- Version threshold/control policy and engine artifacts.
- Restrict, encrypt, minimize, and retain data appropriately.
- Monitor dispositions, path counts, aggregation-only blocks, cycles, caps, trace mismatches, opacity, control cases, reviews, and overrides.
- Revalidate after any code, shared-library, seed-source, schema, threshold, or policy change.

## Rollback

If either gate, evidence reconciliation, or provenance control fails, disable auto-clearance, route affected candidates to `REVIEW`, restore the last validated artifact, and preserve the failing graphs for investigation and regression testing.
