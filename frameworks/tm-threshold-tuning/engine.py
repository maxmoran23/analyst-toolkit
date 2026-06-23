"""
Transaction-monitoring threshold-tuning engine — reference implementation.

Where the other frameworks score alerts, this one validates and tunes the rules that
generate them. Given a monitoring rule's metric values over a population and a
ground-truth label of which activity is genuinely suspicious, it runs above- and
below-the-line (ATL/BTL) testing and recommends a threshold. The full methodology is
in METHODOLOGY.md; this file is its executable form. It is a thin, domain-framed
layer over `_lib/metrics.sweep` — the same confusion matrix the scoring frameworks
use, read with a tuning question.

The framing (a rule alerts when metric >= threshold):
  * Above-the-line (ATL) productivity = precision of the alerts (TP / alerts) — are
    the alerts worth an analyst's time?
  * Below-the-line (BTL) leakage = false negatives (suspicious activity below the
    threshold, undetected) — the regulator's real concern.

Tuning rule (the safety posture): recommend the HIGHEST threshold (least alert
volume) that still keeps detection (recall) at or above a required floor. Raising a
threshold past that point trades alert volume for missed suspicious activity, which
the engine never recommends. A rule whose CURRENT threshold already leaks below the
floor is recommended DOWN to recover detection.

Deterministic. Same inputs -> same recommendation.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib import metrics  # noqa: E402


@dataclass
class Config:
    recall_floor: float = 0.95     # required detection of suspicious activity
    keep_tolerance: float = 0.05   # relative threshold move below which action is KEEP
    n_candidates: int = 40         # threshold grid resolution


@dataclass
class Rule:
    name: str
    metric: str                 # what the rule measures (human description)
    current_threshold: float


@dataclass
class TuningResult:
    rule: str
    action: str                 # RAISE / LOWER / KEEP
    current_threshold: float
    recommended_threshold: float
    current: dict               # {alert_volume, productivity, detection_rate, btl_missed}
    recommended: dict
    sweep: list                 # ATL/BTL table across candidate thresholds
    reason: str

    def as_row(self) -> dict:
        return {"rule": self.rule, "action": self.action,
                "current_threshold": round(self.current_threshold, 2),
                "recommended_threshold": round(self.recommended_threshold, 2),
                "current_detection": self.current["detection_rate"],
                "recommended_detection": self.recommended["detection_rate"],
                "current_volume": self.current["alert_volume"],
                "recommended_volume": self.recommended["alert_volume"],
                "reason": self.reason}


def _stats_at(values, labels, threshold):
    y_pred = [1 if v >= threshold else 0 for v in values]
    c = metrics.confusion(labels, y_pred)
    return {"threshold": threshold, "alert_volume": c.tp + c.fp,
            "productivity": round(c.precision, 4), "detection_rate": round(c.recall, 4),
            "btl_missed": c.fn}


def _candidates(values, n):
    lo, hi = min(values), max(values)
    if hi <= lo:
        return [lo]
    step = (hi - lo) / n
    return [lo + step * i for i in range(n + 1)]


def tune_rule(rule: Rule, values, labels, config: Config = Config()) -> TuningResult:
    cands = _candidates(values, config.n_candidates)
    sweep = [_stats_at(values, labels, t) for t in cands]
    current = _stats_at(values, labels, rule.current_threshold)

    # recommend the HIGHEST threshold whose detection still meets the floor
    safe = [r for r in sweep if r["detection_rate"] >= config.recall_floor]
    rec = max(safe, key=lambda r: r["threshold"]) if safe else min(sweep, key=lambda r: r["threshold"])

    cur_thr, rec_thr = rule.current_threshold, rec["threshold"]
    if current["detection_rate"] < config.recall_floor:
        action = "LOWER"
        reason = (f"BTL leakage: current threshold detects only "
                  f"{current['detection_rate']:.0%} of suspicious activity (below the "
                  f"{config.recall_floor:.0%} floor); lower to recover detection.")
    elif rec_thr > cur_thr * (1 + config.keep_tolerance):
        action = "RAISE"
        reason = (f"ATL over-alerting: detection holds at "
                  f"{rec['detection_rate']:.0%} while alert volume falls "
                  f"{current['alert_volume'] - rec['alert_volume']:,} "
                  f"({1 - rec['alert_volume']/max(1,current['alert_volume']):.0%}); "
                  f"raise to cut unproductive alerts.")
    else:
        action = "KEEP"
        rec_thr = cur_thr
        rec = current
        reason = (f"Near-optimal: detection {current['detection_rate']:.0%} at the "
                  f"current threshold; no safe volume reduction available.")

    return TuningResult(rule=rule.name, action=action, current_threshold=cur_thr,
                        recommended_threshold=rec_thr, current=current, recommended=rec,
                        sweep=sweep, reason=reason)


if __name__ == "__main__":
    import json
    import random
    rng = random.Random(0)
    # a rule whose threshold is set too high (leaks suspicious activity below the line)
    vals, labs = [], []
    for _ in range(5000):
        suspicious = rng.random() < 0.04
        labs.append(1 if suspicious else 0)
        vals.append(rng.gauss(70, 15) if suspicious else rng.gauss(30, 15))
    res = tune_rule(Rule("cash-velocity", "monthly cash deposits", current_threshold=85),
                    vals, labs)
    print(json.dumps(res.as_row(), indent=2))
