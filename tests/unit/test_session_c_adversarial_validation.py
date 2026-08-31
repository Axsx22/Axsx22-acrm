"""Adversarial validation for Session C's current architectural boundaries."""

from datetime import datetime, timedelta, timezone

import pytest

from acrm_core.evolution.session_c import EvolutionObservation, ObservationKind
from acrm_core.session_c.dynamic import (
    DynamicReadinessEvaluator,
    FieldEnvelopeEstimator,
    TrajectoryAnalyzer,
)
from acrm_core.session_c.topic import FieldDrivenTopicEngine


def _obs(kind, value=1.0, offset=0):
    return EvolutionObservation(
        observation_id=f"adv-{offset}-{kind.value}",
        kind=kind,
        description=f"adversarial {kind.value}",
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=offset),
        context={"metric": value},
        source="adversarial-test",
    )


def test_single_outlier_does_not_create_persistent_trajectory():
    observations = [
        _obs(ObservationKind.PRESSURE, offset=0),
        _obs(ObservationKind.PRESSURE, offset=1),
        _obs(ObservationKind.FAILURE, offset=2),
        _obs(ObservationKind.PRESSURE, offset=3),
        _obs(ObservationKind.PRESSURE, offset=4),
    ]
    profile = TrajectoryAnalyzer().profile(observations)
    assert 0.0 <= profile.persistence <= 1.0
    assert profile.observation_count == 5


def test_gradual_drift_changes_field_derived_envelope():
    estimator = FieldEnvelopeEstimator()
    baseline = estimator.estimate(
        [_obs(ObservationKind.PRESSURE, 1.0, i) for i in range(5)],
        metric_name="metric",
    )
    drifted = estimator.estimate(
        [_obs(ObservationKind.PRESSURE, value, i) for i, value in enumerate((1.0, 1.2, 1.4, 1.6, 1.8))],
        metric_name="metric",
    )
    assert drifted.warning_limit >= baseline.warning_limit
    assert drifted.critical_limit >= baseline.critical_limit


def test_topic_engine_does_not_mutate_observations():
    observations = (
        _obs(ObservationKind.PRESSURE, offset=0),
        _obs(ObservationKind.FAILURE, offset=1),
    )
    before = observations
    profile = FieldDrivenTopicEngine().infer(observations)
    assert profile.dominant is not None
    assert observations == before


def test_topic_engine_is_deterministic_for_competing_signal_families():
    observations = (
        _obs(ObservationKind.PRESSURE, offset=0),
        _obs(ObservationKind.AMBIGUITY, offset=1),
        _obs(ObservationKind.MISSING_CAPABILITY, offset=2),
    )
    engine = FieldDrivenTopicEngine()
    assert engine.infer(observations) == engine.infer(observations)


def test_readiness_requires_persistent_warning_or_critical_state():
    observations = (
        _obs(ObservationKind.PRESSURE, offset=0),
        _obs(ObservationKind.AMBIGUITY, offset=1),
        _obs(ObservationKind.PRESSURE, offset=2),
    )
    envelope = FieldEnvelopeEstimator().estimate(observations, metric_name="metric")
    result = DynamicReadinessEvaluator().evaluate(
        observations,
        envelope=envelope,
        current_value=envelope.warning_limit,
        min_observations=3,
        persistence_floor=1.0,
    )
    assert result.ready is False


def test_non_finite_current_value_is_rejected():
    observations = tuple(_obs(ObservationKind.PRESSURE, offset=i) for i in range(3))
    envelope = FieldEnvelopeEstimator().estimate(observations, metric_name="metric")
    with pytest.raises(ValueError):
        DynamicReadinessEvaluator().evaluate(
            observations,
            envelope=envelope,
            current_value=float("nan"),
        )
