"""ACRM calibration research artifact.

This module is deliberately outside ``acrm_core``.  It provides deterministic,
small calibration primitives so the epistemic-invariant harness can test an
actual API without promoting calibration semantics into the v8.5 core.

The functions are engineering contracts, not claims of scientific validity.
"""

from __future__ import annotations

import math
from typing import Sequence


class Calibration:
    """Deterministic calibration primitives used by the research harness."""

    @staticmethod
    def platt(raw: float, a: float = 1.0, b: float = 0.0) -> float:
        """Return Platt-style logistic calibration ``sigmoid(a*raw+b)``.

        The default contract requires ``a > 0`` so the mapping is monotone
        increasing.  Callers may supply a different positive slope after
        empirical calibration.
        """
        if not math.isfinite(raw) or not math.isfinite(a) or not math.isfinite(b):
            raise ValueError("raw, a, and b must be finite")
        if a <= 0:
            raise ValueError("a must be > 0 to preserve increasing monotonicity")
        z = a * raw + b
        if z >= 0:
            return 1.0 / (1.0 + math.exp(-z))
        ez = math.exp(z)
        return ez / (1.0 + ez)

    @staticmethod
    def sigmoid_risk(stability: float, k: float = 10.0, midpoint: float = 0.65) -> float:
        """Map stability to risk with an explicit Lipschitz bound.

        ``risk(S) = sigmoid(k*(midpoint-S))``.  For this logistic form the
        global Lipschitz constant is ``k/4``.
        """
        if not all(math.isfinite(x) for x in (stability, k, midpoint)):
            raise ValueError("stability, k, and midpoint must be finite")
        if k < 0:
            raise ValueError("k must be >= 0")
        z = k * (midpoint - stability)
        if z >= 0:
            return 1.0 / (1.0 + math.exp(-z))
        ez = math.exp(z)
        return ez / (1.0 + ez)

    @staticmethod
    def laplace(errors: int, total: int, alpha: float = 1.0, beta: float = 1.0) -> float:
        """Return Laplace-smoothed error probability.

        This is a Beta(alpha, beta) posterior-mean style estimator:
        ``(errors+alpha)/(total+alpha+beta)``.
        """
        if not isinstance(errors, int) or not isinstance(total, int):
            raise TypeError("errors and total must be integers")
        if errors < 0 or total < 0 or errors > total:
            raise ValueError("require 0 <= errors <= total")
        if alpha <= 0 or beta <= 0 or not math.isfinite(alpha + beta):
            raise ValueError("alpha and beta must be finite and > 0")
        return (errors + alpha) / (total + alpha + beta)

    @staticmethod
    def softmax(scores: Sequence[float], temperature: float = 1.0) -> list[float]:
        """Numerically stable softmax for finite scores."""
        if not scores:
            raise ValueError("scores must not be empty")
        if temperature <= 0 or not math.isfinite(temperature):
            raise ValueError("temperature must be finite and > 0")
        if not all(math.isfinite(x) for x in scores):
            raise ValueError("scores must be finite")
        scaled = [x / temperature for x in scores]
        maximum = max(scaled)
        exps = [math.exp(x - maximum) for x in scaled]
        total = math.fsum(exps)
        return [x / total for x in exps]

    @staticmethod
    def ensemble_weights(errors: Sequence[int], total: int) -> list[float]:
        """Convert smoothed error rates into normalized inverse-error weights."""
        if total <= 0:
            raise ValueError("total must be > 0")
        uncertainties = [Calibration.laplace(e, total) for e in errors]
        inverse = [1.0 / u for u in uncertainties]
        normalizer = math.fsum(inverse)
        return [w / normalizer for w in inverse]

    @staticmethod
    def risk_lipschitz_bound(k: float = 10.0) -> float:
        """Global Lipschitz constant for ``sigmoid(k*(midpoint-S))``."""
        if k < 0 or not math.isfinite(k):
            raise ValueError("k must be finite and >= 0")
        return k / 4.0
