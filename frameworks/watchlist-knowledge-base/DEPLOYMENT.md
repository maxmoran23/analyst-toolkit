# Deployment — running the knowledge base live, and feeding Copilot Studio

Follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md), with
one difference: this package fetches public data, so it has a real live mode in addition
to the deployment mapping.

> **In plain terms:** Today it runs on a schedule on any machine: it pulls the public
> lists, builds the deduplicated database, and hands it to the screening engines. When
> the bank's Microsoft tooling is on, the same pipeline becomes a scheduled flow whose
> output a Copilot Studio screening agent reads — and whose change feed alerts the team.

## Live mode (today)

The pipeline runs on a schedule (e.g. daily): `ingest_all()` fetches each configured
source, `dedup.resolve(...)` consolidates, `delta.diff(...)` against the prior snapshot
emits the change feed, and the resolved entities become the watchlist the sanctions and
adverse-media engines screen against. OFAC SDN ships a working parser; add the other
lists' parsers per their schemas. Network is optional — offline, it degrades to the
synthetic generator so downstream never blocks.

## Copilot Studio / Power Platform mapping

| This package | Target | Becomes |
|---|---|---|
| The pipeline (ingest → dedup → delta) | A **Power Automate** scheduled flow calling an **Azure Function** | The job that refreshes the watchlist and emits the change delta on a cadence. |
| The resolved watchlist | A **Dataverse table** / dataset behind a **custom connector** | The live list the Copilot Studio screening agent (the sanctions framework's tool) queries. |
| The delta feed | A Power Automate notification / governance log | Added / removed / amended designations, routed to monitoring and to the model-governance record (ongoing-monitoring evidence). |
| Review candidates | A worklist (Dataverse / Planner) | Name-only possible-duplicates routed to analysts; their dispositions feed the feedback loop. |

## Properties that make this clean

- **Determinism + offline degrade** — same inputs → same resolved base; a fetch failure
  degrades to synthetic rather than breaking the chain.
- **Structural safety travels** — auto-merge-only-on-unique-identifier holds wherever the
  pipeline runs, so the deployed list never merges away a designation.
- **Feeds the screening tools directly** — the output schema is exactly what the
  sanctions and adverse-media connectors consume; one watchlist serves both.

Real Microsoft surfaces only — Power Automate, Azure Functions, Dataverse, Copilot Studio
custom connectors. No integration is claimed built; the source-list usage terms and the
current Microsoft surface names should be confirmed before implementation.
