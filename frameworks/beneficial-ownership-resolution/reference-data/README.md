# Reference input schema

`sample-input.json` is a deterministic seed-42 pack containing synthetic entities and people only. It is under 150 KB and demonstrates the scorer contract; it is not validation evidence.

```json
{
  "schema_version": "1.0",
  "threshold": 0.25,
  "graphs": [{
    "graph_id": "example",
    "target_entity": "target",
    "nodes": [{"id":"person","type":"person"},{"id":"target","type":"entity","ownership_complete":true}],
    "ownership_edges": [{"owner":"person","owned":"target","fraction":0.30}],
    "control_relationships": [],
    "candidates": ["person"]
  }]
}
```

Every node requires a unique `id` and `type` (`person` or `entity`). Optional integrity flags are `resolved`, `opaque`, `nominee`, and `ownership_complete`. Every ownership edge requires known `owner` and entity `owned` IDs plus a numeric `fraction` from 0 through 1. Control relationships require a person, entity, and `prong`; optional qualifiers include `decisive`, `sole_authority`, `sole_director`, and `voting_fraction`.

Top-level or per-graph configuration may specify `threshold`, `near_threshold_margin`, `convergence_tolerance`, and `max_iterations`. If `candidates` is omitted, all person nodes are scored. Unknown fields are ignored.
