"""
Evaluation metrics for screening / triage validation.

The vocabulary here is deliberately framed for a sanctions/AML context, where the
asymmetry of errors is the whole point:

  - A FALSE NEGATIVE (a true match wrongly cleared) is a compliance failure with
    regulatory and legal consequence. Recall on true matches must be ~1.0.
  - A FALSE POSITIVE (a non-match escalated) is operational cost — the 50k/month
    alert backlog. Reducing it is the business value, but never at the expense
    of the metric above.

`confusion`, `summary`, and `sweep` are the three entry points. `sweep` walks a
decision threshold and reports how the two error rates trade off, which is the
calibration evidence an independent model review (SR 11-7 style) expects.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from itertools import zip_longest
import math


@dataclass
class Confusion:
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def precision(self) -> float:
        d = self.tp + self.fp
        return self.tp / d if d else 1.0

    @property
    def recall(self) -> float:
        """Sensitivity / true-positive rate — the regulator-critical metric."""
        d = self.tp + self.fn
        return self.tp / d if d else 1.0

    @property
    def specificity(self) -> float:
        d = self.tn + self.fp
        return self.tn / d if d else 1.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def false_negative_rate(self) -> float:
        d = self.tp + self.fn
        return self.fn / d if d else 0.0

    @property
    def false_positive_rate(self) -> float:
        d = self.fp + self.tn
        return self.fp / d if d else 0.0

    def as_dict(self) -> dict:
        d = asdict(self)
        d.update(
            precision=round(self.precision, 4),
            recall=round(self.recall, 4),
            specificity=round(self.specificity, 4),
            f1=round(self.f1, 4),
            false_negative_rate=round(self.false_negative_rate, 4),
            false_positive_rate=round(self.false_positive_rate, 4),
        )
        return d


def confusion(y_true, y_pred) -> Confusion:
    """y_true / y_pred are iterables of 1 (positive/match) or 0 (negative)."""
    tp = fp = tn = fn = 0
    absent = object()
    for t, p in zip_longest(y_true, y_pred, fillvalue=absent):
        if t is absent or p is absent:
            raise ValueError("true and predicted label counts must match")
        if type(t) not in (int, bool) or type(p) not in (int, bool) or t not in (0, 1) or p not in (0, 1):
            raise ValueError("labels must be binary integers or booleans")
        if p:
            if t:
                tp += 1
            else:
                fp += 1
        else:
            if t:
                fn += 1
            else:
                tn += 1
    return Confusion(tp=tp, fp=fp, tn=tn, fn=fn)


def summary(y_true, y_pred) -> dict:
    return confusion(y_true, y_pred).as_dict()


def sweep(y_true, scores, thresholds):
    """For each threshold, predict positive when score >= threshold and report
    the confusion stats. Returns a list of dicts, one per threshold, suitable for
    writing straight to a CSV threshold-sensitivity table.

    A higher threshold here means 'more confident before we keep an alert open',
    so it raises the auto-clear volume; the columns let a reviewer read the
    false-negative leakage that buys each unit of false-positive reduction.
    """
    y_true, scores = list(y_true), list(scores)
    if len(y_true) != len(scores) or any(not math.isfinite(value) for value in scores):
        raise ValueError("scores must be finite and align with true labels")
    rows = []
    for thr in thresholds:
        if not math.isfinite(thr):
            raise ValueError("threshold must be finite")
        y_pred = [1 if s >= thr else 0 for s in scores]
        c = confusion(y_true, y_pred)
        row = {"threshold": round(thr, 4)}
        row.update(c.as_dict())
        rows.append(row)
    return rows


def markdown_table(rows, columns=None) -> str:
    """Render a list-of-dicts as a GitHub markdown table."""
    if not rows:
        return "_(no rows)_"
    columns = columns or list(rows[0].keys())
    head = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = "\n".join(
        "| " + " | ".join(str(r.get(c, "")) for c in columns) + " |" for r in rows
    )
    return "\n".join([head, sep, body])
