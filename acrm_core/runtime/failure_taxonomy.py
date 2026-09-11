"""Failure-mode and calibration layer derived from the ACRM v7 runtime artifact.

The v7 dashboard defined a 17-node failure-mode field and six calibration
checks. This module promotes that computational lineage into testable Python
without carrying over browser/UI state or simulated presentation values.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Any, Sequence


class FailureSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class FailureMode:
    id: str
    name: str
    severity: FailureSeverity
    domain: str
    causal: tuple[str, ...] = ()


FAILURE_MODES: tuple[FailureMode, ...] = (
    FailureMode("FM-01", "Monotonicity Violation", FailureSeverity.CRITICAL, "calibration", ("FM-04", "FM-07")),
    FailureMode("FM-02", "Lipschitz Breach", FailureSeverity.HIGH, "risk", ("FM-05", "FM-08")),
    FailureMode("FM-03", "Boundary Collapse", FailureSeverity.HIGH, "uncertainty", ("FM-06", "FM-09")),
    FailureMode("FM-04", "Normalization Drift", FailureSeverity.MEDIUM, "distribution", ("FM-10", "FM-11")),
    FailureMode("FM-05", "Ranking Instability", FailureSeverity.MEDIUM, "invariance", ("FM-01", "FM-12")),
    FailureMode("FM-06", "Weight Inversion", FailureSeverity.MEDIUM, "ensemble", ("FM-03", "FM-13")),
    FailureMode("FM-07", "Confidence Decay", FailureSeverity.LOW, "calibration", ("FM-14",)),
    FailureMode("FM-08", "Threshold Sensitivity", FailureSeverity.LOW, "risk", ("FM-15",)),
    FailureMode("FM-09", "Prior Dominance", FailureSeverity.LOW, "uncertainty", ("FM-16",)),
    FailureMode("FM-10", "Overflow/Underflow", FailureSeverity.CRITICAL, "distribution", ("FM-17",)),
    FailureMode("FM-11", "Zero Division", FailureSeverity.HIGH, "distribution", ("FM-10",)),
    FailureMode("FM-12", "Scale Sensitivity", FailureSeverity.LOW, "invariance", ()),
    FailureMode("FM-13", "Error Miscount", FailureSeverity.MEDIUM, "ensemble", ("FM-06",)),
    FailureMode("FM-14", "Sigmoid Saturation", FailureSeverity.LOW, "calibration", ("FM-07",)),
    FailureMode("FM-15", "Gradient Explosion", FailureSeverity.HIGH, "risk", ("FM-02",)),
    FailureMode("FM-16", "Sample Starvation", FailureSeverity.MEDIUM, "uncertainty", ("FM-09",)),
    FailureMode("FM-17", "Numerical Precision", FailureSeverity.CRITICAL, "distribution", ("FM-10", "FM-11")),
)


class Calibration:
    """Numerically stable calibration functions used by the v7 test field."""

    PLATT_A = 4.0
    PLATT_B = -2.0
    RISK_K = 10.0
    RISK_S0 = 0.65

    @staticmethod
    def _sigmoid(z: float) -> float:
        z = max(-500.0, min(500.0, float(z)))
        return 1.0 / (1.0 + math.exp(-z))

    @classmethod
    def platt(cls, raw: float) -> float:
        return cls._sigmoid(cls.PLATT_A * float(raw) + cls.PLATT_B)

    @classmethod
    def sigmoid_risk(cls, stability: float) -> float:
        return cls._sigmoid(cls.RISK_K * (float(stability) - cls.RISK_S0))

    @staticmethod
    def laplace(errors: int, total: int) -> float:
        if total < 0 or errors < 0:
            raise ValueError("errors and total must be non-negative")
        if total == 0:
            return 1.0
        return (errors + 1) / (total + 2)

    @staticmethod
    def softmax(scores: Sequence[float]) -> tuple[float, ...]:
        if not scores:
            raise ValueError("softmax input cannot be empty")
        values = [float(s) for s in scores]
        if not all(math.isfinite(s) for s in values):
            raise ValueError("softmax scores must be finite")
        maximum = max(values)
        exponentials = [math.exp(s - maximum) for s in values]
        total = sum(exponentials)
        return tuple(x / total for x in exponentials)


def run_calibration_checks() -> dict[str, bool]:
    """Run the six computational checks represented by the v7 runtime UI."""
    raw = (0.1, 0.3, 0.5, 0.7, 0.9)
    platt = tuple(Calibration.platt(x) for x in raw)
    monotonic = all(a < b for a, b in zip(platt, platt[1:]))

    s1, s2 = 0.64, 0.66
    slope = abs(Calibration.sigmoid_risk(s2) - Calibration.sigmoid_risk(s1)) / (s2 - s1)
    smooth = slope <= Calibration.RISK_K * 1.5

    laplace_cases = ((0, 100), (5, 100), (0, 0), (99, 100))
    laplace_ok = all(
        (value == 1.0 if total == 0 else 0.0 < value < 1.0)
        for errors, total in laplace_cases
        for value in (Calibration.laplace(errors, total),)
    )

    softmax_ok = all(abs(sum(Calibration.softmax(values)) - 1.0) < 1e-9 for values in ((1, 2, 3), (0.1, 0.2, 0.3), (10, 20, 30), (-1, -2, -3)))

    scaled = tuple(x * 2 for x in raw)
    scaled_probs = tuple(Calibration.platt(x) for x in scaled)
    invariant = all((platt[i] < platt[i + 1]) == (scaled_probs[i] < scaled_probs[i + 1]) for i in range(len(raw) - 1))

    models = ((0.1, 0.9), (0.3, 0.7), (0.2, 0.8))
    denom = sum(1 - err for err, _ in models)
    weights = tuple((1 - err) / denom for err, _ in models)
    ensemble = abs(sum(weights) - 1.0) < 1e-9 and weights[0] > weights[2] > weights[1]

    return {
        "platt_monotonicity": monotonic,
        "risk_smoothness": smooth,
        "laplace_stability": laplace_ok,
        "softmax_consistency": softmax_ok,
        "calibration_invariance": invariant,
        "ensemble_sanity": ensemble,
    }
