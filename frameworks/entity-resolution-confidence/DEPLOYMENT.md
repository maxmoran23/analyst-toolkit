# Deployment

## Runtime

- CPython 3.12; standard library only
- No network calls, package installation, model files, or external services
- Read-only code/reference directory; writable `data/` for local outputs

## Offline verification

```bash
python3 -m unittest -v test_identity.py
python3 run_validation.py --seed 42 --same 160 --different 240 --name-only 80 --trials 6
python3 scorer.py --input reference-data/sample-input.json --output data/sample-output.json
```

The validation command must exit `0`. Confirm the SHA-256 values and runtime provenance in `evidence/run-manifest.json`, and confirm that both gates are `PASS` in `evidence/metrics.json`.

## Integration pattern

Validate input against `reference-data/README.md`, call `score_payload()` or the CLI, retain the complete evidence object, and route all `REVIEW` results to trained analysts. Treat `SAME` and `DIFFERENT` as dispositions subject to the source-system and use-case controls—not as proof of identity or non-identity.

## Operational controls

- Restrict access to identity data; encrypt it at rest and in transit outside this offline sample.
- Minimize fields, define retention, log access, and prohibit reuse beyond the declared purpose.
- Keep query/candidate source provenance and immutable decision logs.
- Require analyst approval for conflicting strong evidence and high-impact downstream actions.
- Monitor input missingness, disposition rates, overrides, common-name segments, scripts/romanizations, and data-source drift.
- Revalidate after any code, configuration, field taxonomy, normalization, or reference-data change.
- Never use synthetic evidence as a substitute for representative production validation.

## Rollback

Version the entire folder as one artifact. If a gate, monitoring threshold, or provenance check fails, stop automatic dispositioning, route all pairs to `REVIEW`, restore the last validated artifact, and preserve the failing inputs for effective challenge.
