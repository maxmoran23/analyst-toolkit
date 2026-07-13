"""Seeded, labelled synthetic population for the fraud-detection framework."""
from __future__ import annotations

import argparse
import json
import os
import random
from dataclasses import asdict

import scorer as S


TYPOLOGIES = (
    "account_takeover",
    "card_not_present",
    "first_party_bustout",
    "mule_inflow",
    "synthetic_identity",
)

LEGITIMATE_CATEGORIES = (
    "trusted_session_continuity",
    "new_device_travel_mimic",
    "high_value_known_payee_mimic",
    "cnp_recurring_burst_mimic",
    "young_account_payroll_mimic",
    "credit_rebuild_mimic",
    "identity_refresh_mimic",
)


def _baseline(index: int, rng: random.Random) -> S.CustomerBaseline:
    return S.CustomerBaseline(
        customer_id=f"CUSTOMER-{index:06d}",
        expected_amount=round(rng.uniform(35.0, 650.0), 2),
        expected_transaction_count_10m=float(rng.choice((1, 1, 1, 2, 2, 3))),
        tenure_days=rng.randint(30, 5000),
    )


def _base_event(event_id: str, baseline: S.CustomerBaseline, rng: random.Random) -> dict:
    return {
        "event_id": event_id,
        "customer_id": baseline.customer_id,
        "amount": round(baseline.expected_amount * rng.uniform(0.25, 1.40), 2),
        "transaction_count_10m": max(1, int(baseline.expected_transaction_count_10m)),
        "new_device": False,
        "failed_login_count": 0,
        "contact_change_hours": 9999,
        "cnp": rng.random() < 0.35,
        "cross_border": False,
        "merchant_trust": round(rng.uniform(0.70, 1.00), 3),
        "utilization_ratio": round(rng.uniform(0.05, 0.70), 3),
        "returned_payments_90d": 0,
        "inbound_senders_72h": rng.randint(0, 2),
        "inbound_amount_72h": 0.0,
        "same_day_outbound_amount": 0.0,
        "account_age_days": max(1, baseline.tenure_days),
        "identity_mismatch_count": 0,
        "identity_document_reused": False,
        "beneficiary_first_seen": False,
        "beneficiary_risk": round(rng.uniform(0.0, 0.30), 3),
        "trusted_device": True,
        "strong_authentication": True,
    }


def _plant_fraud(
    row: dict, typology: str, baseline: S.CustomerBaseline, rng: random.Random, boundary: bool
) -> None:
    row.update(trusted_device=False, strong_authentication=False, beneficiary_first_seen=True)
    if typology == "account_takeover":
        row.update(
            new_device=True,
            failed_login_count=3 if boundary else rng.randint(4, 8),
            contact_change_hours=24 if boundary else rng.randint(0, 12),
            amount=round(baseline.expected_amount * rng.uniform(2.0, 7.0), 2),
            beneficiary_risk=round(rng.uniform(0.70, 1.00), 3),
        )
    elif typology == "card_not_present":
        row.update(
            cnp=True,
            cross_border=True,
            amount=round(baseline.expected_amount * (4.0 if boundary else rng.uniform(4.2, 10.0)), 2),
            merchant_trust=0.25 if boundary else round(rng.uniform(0.0, 0.20), 3),
            beneficiary_risk=round(rng.uniform(0.60, 0.95), 3),
        )
    elif typology == "first_party_bustout":
        row.update(
            amount=round(baseline.expected_amount * (2.0 if boundary else rng.uniform(2.2, 6.0)), 2),
            utilization_ratio=0.95 if boundary else round(rng.uniform(0.97, 1.00), 3),
            returned_payments_90d=2 if boundary else rng.randint(3, 6),
            trusted_device=True,
            strong_authentication=True,
        )
    elif typology == "mule_inflow":
        inbound = round(rng.uniform(5000.0, 50000.0), 2)
        row.update(
            inbound_senders_72h=5 if boundary else rng.randint(6, 14),
            inbound_amount_72h=inbound,
            # Add one cent at the inclusive boundary so currency rounding cannot
            # turn a mathematically exact 0.90 case into 0.899999...
            same_day_outbound_amount=(
                round(inbound * 0.90 + 0.01, 2)
                if boundary
                else round(inbound * rng.uniform(0.92, 0.99), 2)
            ),
            account_age_days=180 if boundary else rng.randint(1, 120),
            beneficiary_risk=round(rng.uniform(0.70, 1.00), 3),
        )
    elif typology == "synthetic_identity":
        row.update(
            identity_mismatch_count=3 if boundary else rng.randint(4, 7),
            identity_document_reused=True,
            account_age_days=90 if boundary else rng.randint(1, 60),
            beneficiary_risk=round(rng.uniform(0.55, 0.90), 3),
        )


def _plant_legitimate_mimic(
    row: dict, category: str, baseline: S.CustomerBaseline, rng: random.Random, boundary: bool
) -> None:
    if category == "trusted_session_continuity":
        return
    row.update(trusted_device=False, beneficiary_first_seen=True)
    if category == "new_device_travel_mimic":
        row.update(new_device=True, failed_login_count=0, contact_change_hours=9999,
                   cross_border=True, strong_authentication=True)
    elif category == "high_value_known_payee_mimic":
        row.update(amount=round(baseline.expected_amount * rng.uniform(4.0, 8.0), 2),
                   trusted_device=True, beneficiary_first_seen=False, strong_authentication=True)
    elif category == "cnp_recurring_burst_mimic":
        row.update(cnp=True, cross_border=True,
                   amount=round(baseline.expected_amount * (3.99 if boundary else rng.uniform(1.5, 3.8)), 2),
                   merchant_trust=round(rng.uniform(0.65, 0.95), 3))
    elif category == "young_account_payroll_mimic":
        inbound = round(rng.uniform(3000.0, 12000.0), 2)
        row.update(account_age_days=rng.randint(1, 90), inbound_senders_72h=1,
                   inbound_amount_72h=inbound, same_day_outbound_amount=round(inbound * 0.95, 2))
    elif category == "credit_rebuild_mimic":
        row.update(utilization_ratio=0.94 if boundary else round(rng.uniform(0.75, 0.92), 3),
                   returned_payments_90d=0,
                   amount=round(baseline.expected_amount * rng.uniform(1.2, 1.9), 2),
                   trusted_device=True, beneficiary_first_seen=False)
    elif category == "identity_refresh_mimic":
        row.update(identity_mismatch_count=2, identity_document_reused=False,
                   account_age_days=rng.randint(1, 90), strong_authentication=True)


def make_population(transactions: int, rng: random.Random) -> tuple[dict, list[dict]]:
    """Build an 8% fraud population with all typologies and labelled mimics."""
    if transactions < 100:
        raise ValueError("transactions must be >= 100")
    fraud_count = round(transactions * 0.08)
    fraud_flags = [True] * fraud_count + [False] * (transactions - fraud_count)
    rng.shuffle(fraud_flags)
    baselines = {}
    events = []
    fraud_index = legit_index = 0
    legitimate_category_counts = {name: 0 for name in LEGITIMATE_CATEGORIES}
    for index, is_fraud in enumerate(fraud_flags):
        baseline = _baseline(index, rng)
        baselines[baseline.customer_id] = asdict(baseline)
        event_id = f"EVENT-{index:07d}"
        row = _base_event(event_id, baseline, rng)
        if is_fraud:
            typology = TYPOLOGIES[fraud_index % len(TYPOLOGIES)]
            boundary = fraud_index < len(TYPOLOGIES) * 2
            _plant_fraud(row, typology, baseline, rng, boundary)
            row.update(label=1, typology=typology,
                       category=f"{typology}_{'boundary' if boundary else 'confirmed'}",
                       boundary_case=boundary)
            fraud_index += 1
        else:
            # 72% of legitimate sessions are provable continuity; the remainder
            # are deliberately realistic mimics routed to step-up, never hard decline.
            if legit_index % 25 < 18:
                category = "trusted_session_continuity"
            else:
                category = LEGITIMATE_CATEGORIES[1 + (legit_index % (len(LEGITIMATE_CATEGORIES) - 1))]
            boundary = (
                category != "trusted_session_continuity"
                and legitimate_category_counts[category] == 0
            )
            _plant_legitimate_mimic(row, category, baseline, rng, boundary)
            row.update(label=0, typology="", category=category, boundary_case=boundary)
            legitimate_category_counts[category] += 1
            legit_index += 1
        events.append(row)
    return baselines, events


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transactions", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = parser.parse_args()
    baselines, events = make_population(args.transactions, random.Random(args.seed))
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "baselines.json"), "w", encoding="utf-8") as handle:
        json.dump(baselines, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with open(os.path.join(args.out, "events.jsonl"), "w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
    fraud = sum(event["label"] for event in events)
    print(
        f"transactions: {len(events):,}; confirmed_fraud: {fraud:,} "
        f"({fraud / len(events):.2%}); seed: {args.seed}; output: {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
