from datetime import datetime, timedelta, timezone

import pytest

from acrm_core.evolution.session_c import EvolutionObservation, ObservationKind
from acrm_core.session_c.dynamic import (
    DynamicReadinessEvaluator,
    FieldEnvelopeEstimator,
    TrajectoryAnalyzer,
)
from acrm_core.session_c.topic import FieldDrivenTopicEngine


def obs(i, kind, load):
    return EvolutionObservation(
        observation_id=f"o-{i}",
        kind=kind,
        description=f"observation {i}",
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
        + timedelta(minutes=i),
        context={"load": load},
    )


def test_trajectory_is_temporal_and_neutral():
    profile = TrajectoryAnalyzer().profile(
        (
            obs(0, ObservationKind.PRESSURE, 1),
            obs(1, ObservationKind.PRESSURE, 2),
            obs(2, ObservationKind.AMBIGUITY, 3),
        )
    )
    assert profile.observation_count == 3
    assert profile.by_kind[ObservationKind.PRESSURE] == 2
    assert profile.persistence == 0.5
    assert profile.first_observed_at < profile.last_observed_at


def test_envelope_is_derived_from_field_history():
    envelope = FieldEnvelopeEstimator().estimate(
        tuple(obs(i, ObservationKind.PRESSURE, float(i)) for i in range(10)),
        metric_name="load",
    )
    assert envelope.sample_count == 10
    assert envelope.warning_limit < envelope.critical_limit
    assert envelope.baseline == 4.5


def test_envelope_rejects_invalid_quantile_order():
    items = (obs(0, ObservationKind.PRESSURE, 1),)
    with pytest.raises(ValueError, match="quantiles"):
        FieldEnvelopeEstimator().estimate(
            items,
            metric_name="load",
            warning_quantile=0.9,
            critical_quantile=0.8,
        )


def test_envelope_ignores_non_numeric_and_non_finite_values():
    valid = obs(0, ObservationKind.PRESSURE, 2.0)
    text = obs(1, ObservationKind.PRESSURE, 3.0)
    text.context["load"] = "not-a-number"
    nan_value = obs(2, ObservationKind.PRESSURE, 4.0)
    nan_value.context["load"] = float("nan")

    envelope = FieldEnvelopeEstimator().estimate(
        (valid, text, nan_value), metric_name="load"
    )
    assert envelope.sample_count == 1
    assert envelope.baseline == 2.0
    assert envelope.warning_limit == 2.0
    assert envelope.critical_limit == 2.0


def test_warning_does_not_imply_evolution_without_persistence():
    items = (
        obs(0, ObservationKind.PRESSURE, 1),
        obs(1, ObservationKind.AMBIGUITY, 2),
        obs(2, ObservationKind.MISSING_CAPABILITY, 3),
    )
    envelope = FieldEnvelopeEstimator().estimate(
        items, metric_name="load", warning_quantile=0.5, critical_quantile=1.0
    )
    result = DynamicReadinessEvaluator().evaluate(
        items, envelope=envelope, current_value=2.0, persistence_floor=0.8
    )
    assert result.state == "WARNING"
    assert result.ready is False


def test_persistent_approach_can_prepare_before_critical():
    items = tuple(obs(i, ObservationKind.PRESSURE, float(i)) for i in range(10))
    envelope = FieldEnvelopeEstimator().estimate(items, metric_name="load")
    result = DynamicReadinessEvaluator().evaluate(
        items,
        envelope=envelope,
        current_value=envelope.warning_limit,
        persistence_floor=0.5,
    )
    assert result.state == "WARNING"
    assert result.ready is True


def test_low_direction_supports_lower_is_worse_signals():
    items = tuple(obs(i, ObservationKind.PRESSURE, float(10 - i)) for i in range(10))
    envelope = FieldEnvelopeEstimator().estimate(items, metric_name="load")
    result = DynamicReadinessEvaluator().evaluate(
        items,
        envelope=envelope,
        current_value=envelope.warning_limit,
        persistence_floor=0.5,
        direction="low",
    )
    assert result.state == "WARNING"
    assert result.ready is True
    assert result.approach.distance_to_critical >= 0.0


def test_invalid_signal_direction_is_rejected():
    items = tuple(obs(i, ObservationKind.PRESSURE, float(i)) for i in range(3))
    envelope = FieldEnvelopeEstimator().estimate(items, metric_name="load")
    with pytest.raises(ValueError, match="direction"):
        DynamicReadinessEvaluator().evaluate(
            items,
            envelope=envelope,
            current_value=2.0,
            direction="sideways",
        )


def test_topic_is_inferred_from_accumulated_signals():
    items = tuple(
        obs(i, ObservationKind.PRESSURE, float(i)) for i in range(4)
    ) + (obs(4, ObservationKind.AMBIGUITY, 4),)
    profile = FieldDrivenTopicEngine().infer(items)
    assert profile.dominant is not None
    assert profile.dominant.topic == "capacity_stability"
    assert profile.dominant.support == 0.8
