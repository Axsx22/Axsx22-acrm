"""Adversarial validation for Session C's current architectural boundaries.

These tests intentionally exercise boundary conditions rather than redefining
Session C policy. They document what the current implementation does and make
future regressions visible.
"""

from datetime import datetime, timedelta, timezone

import pytest

from acrm_core.session_c.dynamic import (
    DynamicReadinessEvaluator,
    FieldEnvelopeEstimator,
    TrajectoryAnalyzer,
)
from acrm_core.session_c.observation import Observation, ObservationKind
from acrm_core.session_c.topic import FieldDrivenTopicEngine


def _obs(kind, value, offset=0):
    return Observation(
        observation_id=f"adv-{offset}-{kind.value}",
        kind=kind,
        description=f"adversarial {kind.value}",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=offset),
        context={"value": value},
        source="adversarial-test",
    )


def test_single_outlier_does_not_create_persistent_trajectory():
    observations = [
        _obs(ObservationKind.NORMAL, 1.0, 0),
        _obs(ObservationKind.NORMAL, 1.0, 1),
        _obs(ObservationKind.RUNTIME_PRESSURE, 100.0, 2),
        _obs(ObservationKind.NORMAL, 1.0, 3),
        _obs(ObservationKind.NORMAL, 1.0, 4),
    ]
    trajectory = TrajectoryAnalyzer().analyze(observations)
    assert trajectory.max_persistence < len(observations)


def test_gradual_drift_changes_envelope_without_fixed_global_threshold():
    estimator = FieldEnvelopeEstimator(min_samples=5)
    baseline = estimator.estimate([1.0, 1.0, 1.1, 1.0, 1.1])
    drifted = estimator.estimate([1.0, 1.2, 1.4, 1.6, 1.8])
    assert drifted.warning_limit >= baseline.warning_limit
    assert drifted.critical_limit >= baseline.critical_limit


def test_topic_engine_does_not_mutate_observations():
    observations = [
        _obs(ObservationKind.RUNTIME_PRESSURE, 1.0, 0),
        _obs(ObservationKind.THRESHOLD_EXHAUSTION, 1.0, 1),
    ]
    before = tuple(observations)
    topic = FieldDrivenTopicEngine().infer(observations)
    assert topic is not None
    assert tuple(observations) == before


def test_topic_engine_handles_competing_signal_families_deterministically():
    observations = [
        _obs(ObservationKind.RUNTIME_PRESSURE, 1.0, 0),
        _obs(ObservationKind.AMBIGUITY, 1.0, 1),
        _obs(ObservationKind.CAPABILITY_GAP, 1.0, 2),
    ]
    engine = FieldDrivenTopicEngine()
    first = engine.infer(observations)
    second = engine.infer(observations)
    assert first == second


def test_readiness_does_not_trigger_on_warning_without_persistence():
    observations = [
        _obs(ObservationKind.RUNTIME_PRESSURE, 1.0, 0),
        _obs(ObservationKind.NORMAL, 1.0, 1),
        _obs(ObservationKind.RUNTIME_PRESSURE, 1.0, 2),
        _obs(ObservationKind.NORMAL, 1.0, 3),
        _obs(ObservationKind.RUNTIME_PRESSURE, 1.0, 4),
    ]
    evaluator = DynamicReadinessEvaluator(min_persistence=3)
    result = evaluator.evaluate(observations)
    assert result.ready is False


def test_non_finite_envelope_inputs_are_rejected():
    estimator = FieldEnvelopeEstimator(min_samples=3)
    with pytest.raises((ValueError, TypeError)):
        estimator.estimate([1.0, float("nan"), 2.0])
