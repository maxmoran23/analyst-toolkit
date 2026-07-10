# Deployment — mapping to Microsoft Copilot Studio / Power Platform

Follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target
architecture. Like the watchlist knowledge base, this package has a real live mode
(fetching public data) in addition to the deployment mapping.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, this becomes
> the "pull the public blockchain evidence" button inside a case: an investigator's
> agent calls it with an address, gets back the stamped evidence annex and CSVs,
> and attaches them to the case file. The agent can explain every number because
> every number carries its source; and because the tool never says who owns an
> address, neither can the agent.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `engine.build_pack` (+ the live collectors) — captures in → annex, facts CSV, counterparty CSV, evidence manifest out | An **Azure Function** behind a **Power Platform custom connector**, called as a **Copilot Studio action/tool** from a case workflow | The evidence-pack builder, run server-side. The agent presents and files the pack; it never re-derives totals or re-states facts without their provenance. |
| `METHODOLOGY.md` — provenance model + no-attribution posture | The **agent instructions** + knowledge grounding | The agent's behavioural contract: cite `source_uri`/`retrieved_at_utc` when asked "where is this from"; refuse identity/ownership conclusions; route interpretation to the investigator. |
| `generate_synthetic_data.py` + `fixtures/sample/` + `evidence/` | **Test cases** + the pre-deployment validation pack | The fixture sets (with their adversarial plants) become the regression suite; the validation report is the governance artifact accompanying the agent into review. |

## The live-capture layer

In production the capture step is its own component (an Azure Function or Power
Automate flow calling the chosen public explorer), separated from normalization so
that: (a) the explorer choice, its usage terms, and its rate limits are an explicit
operator decision — this package ships **no default endpoint**; (b) captured raw
payloads and their sha256 digests are archived (e.g. Dataverse or blob storage) at
capture time, so the evidence chain starts at the source bytes; and (c) a fetch
failure degrades to "no pack" rather than a broken case step — the same
degrade-to-None posture the code enforces. Where a chain-analytics vendor connector
exists in the same tenant, it runs alongside: the vendor attributes and scores;
this tool evidences the public layer. They meet in the case file, not in each
other's logic.

## Properties that make this clean

- **Determinism is the integration contract** — same captures in, byte-identical
  annex out; the manifest's artifact digests let any reviewer verify what the
  agent filed.
- **The human boundary survives deployment** — the tool assembles evidence; case
  decisions, filings, and account actions stay with people.
- **The no-attribution posture is enforced upstream of the LLM** — the engine's
  output contains no identity claims, so the agent has none to repeat.

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform custom
connectors, Power Automate, Azure Functions, Dataverse. No integration is claimed
built; confirm current terminology against Microsoft Learn before implementation.
