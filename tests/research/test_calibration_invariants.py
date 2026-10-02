"""Behavioral contracts for the ACRM calibration research artifact."""

import math
import sys
from pathlib import Path

# ``research`` is intentionally not part of the v8.5 package.
sys.path.insert(0, str(Path(__file__).parents[2]))

from research.calibration import Calibration


def test_platt_monotonicity_interior_equality_and_descending():
    cases = [(0.1, 0.2), (0.3, 0.5), (0.8, 0.9), (0.5, 0.5), (0.2, 0.1)]
    for raw1, raw2 in cases:
        p1, p2 = Calibration.platt(raw1), Calibration.platt(raw2)
        if raw1 > raw2:
            assert p1 >= p2
        elif raw1 == raw2:
            assert p1 == p2
        else:
            assert p1 <= p2


def test_risk_smoothness_uses_derived_lipschitz_bound():
    s1, s2, k = 0.64, 0.66, 10.0
    r1 = Calibration.sigmoid_risk(s1, k=k)
    r2 = Calibration.sigmoid_risk(s2, k=k)
    delta_s = abs(s2 - s1)
    bound = Calibration.risk_lipschitz_bound(k) * delta_s
    assert abs(r2 - r1) <= bound + 1e-12


def test_laplace_boundary_stability():
    zero_error = Calibration.laplace(0, 100)
    all_error = Calibration.laplace(100, 100)
    assert zero_error > 0.0
    assert all_error < 1.0
    assert all_error > 0.99


def test_softmax_is_normalized_nonnegative_and_order_preserving():
    scores = [1.0, 2.0, 0.5, 1.5, 0.1]
    probs = Calibration.softmax(scores)
    assert math.isclose(math.fsum(probs), 1.0, rel_tol=0.0, abs_tol=1e-12)
    assert all(p >= 0.0 for p in probs)
    score_order = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)
    prob_order = sorted(range(len(probs)), key=probs.__getitem__, reverse=True)
    assert score_order == prob_order


def test_softmax_remains_stable_for_large_magnitude_inputs():
    probs = Calibration.softmax([10000.0, 9999.0, -10000.0])
    assert math.isclose(math.fsum(probs), 1.0, abs_tol=1e-12)
    assert all(math.isfinite(p) and p >= 0.0 for p in probs)


def test_monotone_scaling_preserves_platt_ranking_not_probability_values():
    raw = [0.1, 0.3, 0.5, 0.7, 0.9]
    scaled = [2.0 * x for x in raw]
    rank1 = sorted(range(len(raw)), key=lambda i: Calibration.platt(raw[i]), reverse=True)
    rank2 = sorted(range(len(raw)), key=lambda i: Calibration.platt(scaled[i]), reverse=True)
    assert rank1 == rank2
    assert any(Calibration.platt(a) != Calibration.platt(b) for a, b in zip(raw, scaled))


def test_ensemble_weights_are_normalized_finite_nonnegative_and_monotone_in_error():
    errors = [3, 5, 7]
    weights = Calibration.ensemble_weights(errors, total=10)
    assert math.isclose(math.fsum(weights), 1.0, abs_tol=1e-12)
    assert all(math.isfinite(w) and w >= 0.0 for w in weights)
    assert weights[0] > weights[1] > weights[2]


def test_calibration_rejects_nonfinite_and_invalid_domains():
    for value in (math.nan, math.inf, -math.inf):
        try:
            Calibration.platt(value)
        except ValueError:
            pass
        else:
            raise AssertionError("non-finite Platt input was accepted")

    for bad in ((-1, 10), (11, 10)):
        try:
            Calibration.laplace(*bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid Laplace domain was accepted")
