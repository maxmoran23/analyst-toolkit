# Reference input schema

`sample-input.json` is a deterministic synthetic seed-42 pack under 150 KB. It demonstrates the input contract and contains no real parties or current sanctions data.

```json
{
  "schema_version": "1.0",
  "graphs": [{
    "graph_id": "example",
    "nodes": [{"id":"s1","type":"person"},{"id":"target","type":"entity","ownership_complete":true}],
    "ownership_edges": [{"owner":"s1","owned":"target","fraction":0.30}],
    "sanctioned_parties": ["s1"],
    "control_relationships": [],
    "candidates": ["target"]
  }]
}
```

Every node requires a unique `id` and type (`person` or `entity`). Integrity flags are `resolved`, `opaque`, `nominee`, and `ownership_complete`. Edges require known owner/owned IDs, an entity-owned endpoint, and a numeric fraction from 0 through 1. Sanctioned parties may be person or entity node IDs. Candidates must be entity IDs.

Control relationships use `person`, `entity`, and `prong`, with optional `decisive`, `sole_authority`, `sole_director`, and `voting_fraction`. Configuration may be supplied top-level or per graph: `blocked_threshold`, `review_floor`, `near_threshold_margin`, `convergence_tolerance`, and `max_iterations`.

Generate another pack offline with:

```bash
python3 generate_synthetic_data.py --seed 42 --true-blocked 160 --below 240 --unresolved 80 --out data/generated
```
