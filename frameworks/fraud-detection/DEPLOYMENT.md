# Deployment — Fraud-Detection Reference Engine

> **In plain terms:** Deploy the deterministic scorer behind a governed service,
> feed it validated fraud features, and treat its output as a recommendation to an
> authenticated workflow. Do not let an agent or connector reinterpret the rules or
> execute a customer action by itself.

## Component mapping

| Package asset | Deployment role | Boundary |
| --- | --- | --- |
| `scorer.py` | Versioned Python service or Azure Function behind an authenticated custom connector | Same typed input must produce the same output; the service recommends routing only. |
| `METHODOLOGY.md` | Model inventory, control specification, reviewer instructions, and explainability basis | Instructions must not re-implement or override the scorer. |
| `generate_synthetic_data.py` and `evidence/` | Predeployment regression pack and CI gate | Synthetic results prove implementation behavior, not live performance. |
| Disposition output | Copilot Studio action or Power Automate case-routing input | A governed human/system checkpoint owns every hard action. |

## Required upstream validation

Validate device identity, authentication strength, contact-change timestamps,
merchant trust, beneficiary risk, customer baselines, returned-payment logic,
flow-through aggregation, account age, and identity-resolution signals. Specify
missing/stale-value behavior before integration; silently substituting a benign
value can invalidate the structural rules.

## Required downstream controls

- Authenticate and authorize every caller; log input version, source timestamps,
  configuration version, result, fired rules, corroborating causes, human decision,
  and override reason.
- Keep `DECLINE_PENDING_REVIEW` and `REFER_FOR_BLOCK_CONFIRMATION` behind governed
  human confirmation appropriate to the institution's policy and legal obligations.
- Prevent the connector, agent, or flow from filing, freezing, blocking, or
  communicating with a customer solely from this output.
- Fail closed to a review queue when required inputs are absent or invalid; do not
  fabricate trusted-session continuity.
- Shadow-run, back-test, validate latency/capacity, stage rollout, monitor both
  safety outcomes, and maintain rollback and incident procedures.

CI should run `run_validation.py --seed 42 --transactions 50000 --trials 6` on
every change and compare regenerated deterministic evidence to the reviewed pack.
A live deployment additionally needs institution-specific outcome monitoring and
periodic independent validation.

**Confidence rating: MODERATE —** the technical boundary is explicit, but no tenant,
connector, upstream source, policy workflow, or production capacity has been tested.

