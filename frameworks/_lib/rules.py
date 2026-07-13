"""
A named-rule mechanism for behavioral scoring.

A `Rule` pairs a name and an optional typology tag with a test function that, given
a feature dict, returns (fired, severity, detail). A `RuleSet` evaluates them all
and exposes the fired rules and the subset that carry a money-laundering typology.

The point of routing rules through this mechanism rather than ad-hoc `if` blocks is
the audit trail: every disposition can name the exact rules that drove it and the
detail string each produced, and the same mechanism is reused across frameworks
(transaction monitoring now, fraud later) so a reviewer learns one shape.

Severity is a [0,1] contribution used by the consuming engine; a non-fired rule
contributes 0. A rule with a `typology` tag asserts a recognised laundering
pattern, which is the signal an engine uses to refuse to auto-close (see each
framework's METHODOLOGY.md).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class RuleResult:
    name: str
    fired: bool
    severity: float   # 0..1 contribution (0 when not fired)
    typology: str     # "" when the rule carries no typology
    detail: str       # human-readable reason, for the audit trail
    corroborating_causes: tuple[str, ...] = ()


@dataclass
class Rule:
    name: str
    # test(features) -> (fired: bool, severity: float in [0,1], detail: str)
    test: Callable
    typology: str = ""

    def evaluate(self, features: dict) -> RuleResult:
        evaluated = self.test(features)
        if len(evaluated) == 3:
            fired, severity, detail = evaluated
            corroborating_causes = ()
        elif len(evaluated) == 4:
            fired, severity, detail, corroborating_causes = evaluated
        else:
            raise ValueError(
                f"rule {self.name!r} must return (fired, severity, detail) "
                "or (fired, severity, detail, corroborating_causes)"
            )
        return RuleResult(
            name=self.name,
            fired=bool(fired),
            severity=float(severity) if fired else 0.0,
            typology=self.typology if fired else "",
            detail=detail,
            corroborating_causes=tuple(corroborating_causes) if fired else (),
        )


@dataclass
class RuleSet:
    rules: list = field(default_factory=list)

    def evaluate(self, features: dict) -> list:
        return [r.evaluate(features) for r in self.rules]

    @staticmethod
    def fired(results) -> list:
        return [r for r in results if r.fired]

    @staticmethod
    def typology_hits(results) -> list:
        """Fired rules that assert a recognised typology — the signal that an
        alert cannot be safely auto-closed."""
        return [r for r in results if r.fired and r.typology]

    @staticmethod
    def max_severity(results) -> float:
        return max((r.severity for r in results), default=0.0)
