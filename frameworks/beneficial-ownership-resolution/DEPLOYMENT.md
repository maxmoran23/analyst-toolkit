# Deployment

## Runtime

- CPython 3.12; standard library only
- No network calls, package installation, external services, or model files
- Read-only code/reference directory; writable `data/` for controlled local outputs

## Offline verification

```bash
python3 -m unittest -v test_ownership.py
python3 run_validation.py --seed 42 --true-owners 160 --below 240 --unresolved 80 --trials 6
python3 scorer.py --input reference-data/sample-input.json --output data/sample-output.json
```

The validation command must exit `0`; both gates must be `PASS` in `evidence/metrics.json`. Verify code SHA-256 values, interpreter, platform, seed schedule, sizes, UTC timestamps, and `network_used: false` in `evidence/run-manifest.json`.

## Integration

Map authoritative records into the documented schema, preserve source and as-of provenance outside the sample contract, run the scorer, retain the complete calculation diagnostics, and route every `REVIEW` to trained analysts. Downstream systems must treat the output as a resolution record, not authorization to file, freeze, reject, off-board, or otherwise act.

## Controls

- Validate edge direction and convert percentages to fractions from 0 through 1.
- Require explicit, source-backed completeness/opacity/nominee declarations.
- Version threshold and control-prong policy by jurisdiction and use case.
- Restrict, encrypt, minimize, and retain legal-entity and natural-person data appropriately.
- Log input provenance, engine version, configuration, disposition, diagnostics, analyst override, and final outcome.
- Monitor disposition mix, review aging, graph depth, cycles, non-convergence, caps, opacity, control prongs, and overrides.
- Revalidate after any code, schema, threshold, prong, completeness, or source-system change.

## Rollback

Version the complete framework as one artifact. If either gate or a provenance control fails, disable auto-clearance, route affected candidates to `REVIEW`, restore the last validated artifact, and retain the failing graphs for investigation and adversarial regression testing.
