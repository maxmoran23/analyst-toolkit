"""Deterministic transaction/session fraud triage with named disposition causes."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from _lib import aggregations
from _lib.rules import Rule, RuleResult, RuleSet


class Disposition(str, Enum):
    APPROVE = "APPROVE"
    STEP_UP_AUTH = "STEP_UP_AUTH"
    DECLINE_PENDING_REVIEW = "DECLINE_PENDING_REVIEW"
    REFER_FOR_BLOCK_CONFIRMATION = "REFER_FOR_BLOCK_CONFIRMATION"


@dataclass(frozen=True)
class FraudEvent:
    event_id: str
    customer_id: str
    amount: float
    transaction_count_10m: int
    new_device: bool
    failed_login_count: int
    contact_change_hours: int
    cnp: bool
    cross_border: bool
    merchant_trust: float
    utilization_ratio: float
    returned_payments_90d: int
    inbound_senders_72h: int
    inbound_amount_72h: float
    same_day_outbound_amount: float
    account_age_days: int
    identity_mismatch_count: int
    identity_document_reused: bool
    beneficiary_first_seen: bool
    beneficiary_risk: float
    trusted_device: bool
    strong_authentication: bool


@dataclass(frozen=True)
class CustomerBaseline:
    customer_id: str
    expected_amount: float
    expected_transaction_count_10m: float
    tenure_days: int


@dataclass(frozen=True)
class Config:
    ato_failed_logins: int = 3
    ato_contact_change_hours: int = 24
    cnp_amount_ratio: float = 4.0
    cnp_merchant_trust_ceiling: float = 0.25
    bustout_utilization: float = 0.95
    bustout_returns: int = 2
    bustout_amount_ratio: float = 2.0
    mule_inbound_senders: int = 5
    mule_flowthrough_ratio: float = 0.90
    mule_account_age_days: int = 180
    synthetic_identity_mismatches: int = 3
    synthetic_account_age_days: int = 90
    refer_severity: float = 0.88


@dataclass(frozen=True)
class ScoreResult:
    event_id: str
    disposition: Disposition
    score: float
    named_cause: str
    risk_floor: Disposition
    fired_rules: tuple[RuleResult, ...]
    corroborating_causes: tuple[str, ...]
    detail: str


_DISPOSITION_RANK = {
    Disposition.APPROVE: 0,
    Disposition.STEP_UP_AUTH: 1,
    Disposition.DECLINE_PENDING_REVIEW: 2,
    Disposition.REFER_FOR_BLOCK_CONFIRMATION: 3,
}


def _max_disposition(left: Disposition, right: Disposition) -> Disposition:
    """Raise-only floor: a later mitigant can never lower a hard disposition."""
    return left if _DISPOSITION_RANK[left] >= _DISPOSITION_RANK[right] else right


def _features(event: FraudEvent, baseline: CustomerBaseline) -> dict:
    flowthrough = aggregations.safe_div(
        event.same_day_outbound_amount, event.inbound_amount_72h, 0.0
    )
    return {
        "event": event,
        "baseline": baseline,
        "amount_ratio": aggregations.ratio_to_expected(event.amount, baseline.expected_amount),
        "velocity_ratio": aggregations.ratio_to_expected(
            event.transaction_count_10m, baseline.expected_transaction_count_10m
        ),
        "flowthrough_ratio": flowthrough,
    }


@lru_cache(maxsize=16)
def _rule_set(config: Config) -> RuleSet:
    def account_takeover(features):
        event = features["event"]
        causes = []
        if event.new_device:
            causes.append("new_device")
        if event.failed_login_count >= config.ato_failed_logins:
            causes.append("credential_failures")
        if event.contact_change_hours <= config.ato_contact_change_hours:
            causes.append("recent_contact_change")
        fired = len(causes) == 3
        severity = min(1.0, 0.88 + 0.02 * (event.failed_login_count - 3))
        detail = (
            f"new_device={event.new_device}; failed_logins={event.failed_login_count}; "
            f"contact_change_hours={event.contact_change_hours}"
        )
        return fired, severity, detail, causes

    def card_not_present(features):
        event = features["event"]
        ratio = features["amount_ratio"]
        causes = []
        if event.cnp:
            causes.append("card_not_present")
        if event.cross_border:
            causes.append("cross_border_merchant")
        if ratio >= config.cnp_amount_ratio:
            causes.append("amount_profile_break")
        if event.merchant_trust <= config.cnp_merchant_trust_ceiling:
            causes.append("low_trust_merchant")
        fired = len(causes) == 4
        severity = min(0.87, 0.76 + 0.015 * max(0.0, ratio - config.cnp_amount_ratio))
        detail = (
            f"cnp={event.cnp}; cross_border={event.cross_border}; "
            f"amount_ratio={ratio:.3f}; merchant_trust={event.merchant_trust:.3f}"
        )
        return fired, severity, detail, causes

    def first_party_bustout(features):
        event = features["event"]
        ratio = features["amount_ratio"]
        causes = []
        if event.utilization_ratio >= config.bustout_utilization:
            causes.append("near_limit_utilization")
        if event.returned_payments_90d >= config.bustout_returns:
            causes.append("repeated_returned_payments")
        if ratio >= config.bustout_amount_ratio:
            causes.append("spend_profile_break")
        fired = len(causes) == 3
        severity = min(0.87, 0.81 + 0.02 * (event.returned_payments_90d - 2))
        detail = (
            f"utilization={event.utilization_ratio:.3f}; "
            f"returned_payments={event.returned_payments_90d}; amount_ratio={ratio:.3f}"
        )
        return fired, severity, detail, causes

    def mule_inflow(features):
        event = features["event"]
        ratio = features["flowthrough_ratio"]
        causes = []
        if event.inbound_senders_72h >= config.mule_inbound_senders:
            causes.append("unrelated_sender_fanin")
        if ratio >= config.mule_flowthrough_ratio:
            causes.append("same_day_flowthrough")
        if event.account_age_days <= config.mule_account_age_days:
            causes.append("young_account")
        fired = len(causes) == 3
        severity = min(1.0, 0.90 + 0.01 * (event.inbound_senders_72h - 5))
        detail = (
            f"inbound_senders_72h={event.inbound_senders_72h}; "
            f"flowthrough_ratio={ratio:.3f}; account_age_days={event.account_age_days}"
        )
        return fired, severity, detail, causes

    def synthetic_identity(features):
        event = features["event"]
        causes = []
        if event.identity_mismatch_count >= config.synthetic_identity_mismatches:
            causes.append("identity_attribute_conflicts")
        if event.identity_document_reused:
            causes.append("reused_identity_document")
        if event.account_age_days <= config.synthetic_account_age_days:
            causes.append("new_identity_relationship")
        fired = len(causes) == 3
        severity = min(1.0, 0.94 + 0.01 * (event.identity_mismatch_count - 3))
        detail = (
            f"identity_mismatches={event.identity_mismatch_count}; "
            f"document_reused={event.identity_document_reused}; "
            f"account_age_days={event.account_age_days}"
        )
        return fired, severity, detail, causes

    return RuleSet(
        [
            Rule("account_takeover", account_takeover, "ACCOUNT_TAKEOVER"),
            Rule("card_not_present", card_not_present, "CARD_NOT_PRESENT"),
            Rule("first_party_bustout", first_party_bustout, "FIRST_PARTY_BUSTOUT"),
            Rule("mule_inflow", mule_inflow, "MULE_INFLOW"),
            Rule("synthetic_identity", synthetic_identity, "SYNTHETIC_IDENTITY"),
        ]
    )


def score_event(
    event: FraudEvent, baseline: CustomerBaseline, config: Config | None = None
) -> ScoreResult:
    """Score one event and return a routing recommendation, never an executed action."""
    config = config or Config()
    features = _features(event, baseline)
    rule_results = _rule_set(config).evaluate(features)
    fired = tuple(RuleSet.fired(rule_results))
    typology_hits = RuleSet.typology_hits(rule_results)

    deviation = aggregations.saturating(
        max(0.0, features["amount_ratio"] - 1.0)
        + max(0.0, features["velocity_ratio"] - 1.0),
        4.0,
    )
    score = aggregations.clamp(max(RuleSet.max_severity(rule_results), deviation))

    # Every hard outcome requires a fired named typology and at least two named,
    # corroborating causes. Score is only a ranking aid and never decides alone.
    if typology_hits:
        strongest = max(typology_hits, key=lambda result: (result.severity, result.name))
        causes = tuple(sorted(set(strongest.corroborating_causes)))
        if len(causes) < 2:
            disposition = Disposition.STEP_UP_AUTH
            floor = Disposition.STEP_UP_AUTH
            named_cause = "fraud_signal_without_corroboration"
        elif strongest.severity >= config.refer_severity:
            disposition = Disposition.REFER_FOR_BLOCK_CONFIRMATION
            floor = Disposition.REFER_FOR_BLOCK_CONFIRMATION
            named_cause = f"corroborated_{strongest.name}"
        else:
            disposition = Disposition.DECLINE_PENDING_REVIEW
            floor = Disposition.DECLINE_PENDING_REVIEW
            named_cause = f"corroborated_{strongest.name}"
        # This explicit max is the raise-only control: no session-continuity or
        # authentication signal below this point can reduce the typology floor.
        disposition = _max_disposition(disposition, floor)
        detail = strongest.detail
    else:
        causes = ()
        trusted_session = (
            event.trusted_device
            and event.strong_authentication
            and not event.new_device
            and event.failed_login_count == 0
            and event.contact_change_hours > config.ato_contact_change_hours
            and not event.beneficiary_first_seen
            and event.beneficiary_risk < 0.50
            and event.identity_mismatch_count == 0
            and not event.identity_document_reused
            and features["amount_ratio"] <= 1.50
            and features["velocity_ratio"] <= 1.50
        )
        if trusted_session:
            disposition = Disposition.APPROVE
            floor = Disposition.APPROVE
            named_cause = "trusted_session_continuity"
            detail = "known device, strong authentication, stable profile, and no fired fraud rule"
        else:
            disposition = Disposition.STEP_UP_AUTH
            floor = Disposition.STEP_UP_AUTH
            named_cause = "behavioral_deviation_without_corroboration"
            detail = "one or more contextual signals require authentication; no hard rule fired"

    return ScoreResult(
        event_id=event.event_id,
        disposition=disposition,
        score=round(score, 6),
        named_cause=named_cause,
        risk_floor=floor,
        fired_rules=fired,
        corroborating_causes=causes,
        detail=detail,
    )


if __name__ == "__main__":
    sample = FraudEvent(
        event_id="FRAUD-DEMO-0001",
        customer_id="CUSTOMER-DEMO",
        amount=1800.0,
        transaction_count_10m=2,
        new_device=True,
        failed_login_count=4,
        contact_change_hours=2,
        cnp=False,
        cross_border=False,
        merchant_trust=0.9,
        utilization_ratio=0.2,
        returned_payments_90d=0,
        inbound_senders_72h=1,
        inbound_amount_72h=0.0,
        same_day_outbound_amount=0.0,
        account_age_days=900,
        identity_mismatch_count=0,
        identity_document_reused=False,
        beneficiary_first_seen=True,
        beneficiary_risk=0.8,
        trusted_device=False,
        strong_authentication=False,
    )
    baseline = CustomerBaseline("CUSTOMER-DEMO", 120.0, 1.0, 900)
    print(score_event(sample, baseline))
