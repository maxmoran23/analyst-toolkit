# Reference data schema

`sample-input.json` is an unlabelled, deterministic input pack generated from seed 42. It contains no real people.

Top-level schema:

```json
{"schema_version":"1.0","queries":[{"query_id":"...","query":{},"candidates":[{}]}]}
```

An identity record must include at least one of `name`, `names`, or `aliases`. Supported optional fields are `dob`, `place_of_birth`, `nationality`, `passport`, `national_id`, `tax_id`, and `address`. Names, aliases, and strong identifiers may be strings or arrays. Candidate records may include `candidate_id`; unknown fields are ignored by the scorer.

DOB forms: `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`, with `-` or `/` separators and optional unknown components (`00`, `XX`, or `????`). Strings are expected to be UTF-8. Strong identifiers should include their full value; partial values are intentionally non-decisive.

The scorer returns a result per candidate. The sample pack is under 150 KB and exists only to demonstrate the contract; it is not validation evidence.
