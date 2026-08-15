from datetime import datetime, timezone
from dataclasses import FrozenInstanceError

import pytest

from acrm_core.field.state import FieldState


def test_create_field_state():
    timestamp = datetime(
        2026,
        8,
        14,
        12,
        0,
        tzinfo=timezone.utc,
    )

    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=0,
        timestamp=timestamp,
        metrics={
            "S": 0.91,
            "rho": 0.22,
            "ARQ": 0.74,
        },
        state="HEALTHY",
        governance_confidence=0.95,
    )

    assert state.field_id == "field-001"
    assert state.session_id == "session-001"
    assert state.sequence == 0
    assert state.state == "HEALTHY"
    assert state.metric("S") == 0.91
    assert state.metric("rho") == 0.22
    assert state.metric("ARQ") == 0.74
    assert state.governance_confidence == 0.95
    assert state.timestamp == timestamp
    assert state.timestamp.tzinfo == timezone.utc


def test_create_uses_utc_timestamp_when_not_supplied():
    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=0,
    )

    assert state.timestamp.tzinfo == timezone.utc
    assert state.timestamp.utcoffset().total_seconds() == 0


def test_missing_metric_returns_none():
    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=1,
    )

    assert state.metric("S") is None


def test_failure_mode_detection():
    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=2,
        active_failure_modes=("FM-01", "FM-07"),
    )

    assert state.has_failure_mode("FM-01")
    assert state.has_failure_mode("FM-07")
    assert not state.has_failure_mode("FM-99")


def test_invalid_sequence_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=-1,
        )


def test_non_integer_sequence_rejected():
    with pytest.raises(TypeError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=1.5,
        )


def test_boolean_sequence_rejected():
    with pytest.raises(TypeError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=True,
        )


def test_invalid_confidence_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            governance_confidence=1.5,
        )


@pytest.mark.parametrize("value", [-0.1, float("inf"), float("-inf"), float("nan")])
def test_non_finite_or_out_of_range_confidence_rejected(value):
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            governance_confidence=value,
        )


def test_boolean_confidence_rejected():
    with pytest.raises(TypeError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            governance_confidence=True,
        )


def test_empty_field_id_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="",
            session_id="session-001",
            sequence=0,
        )


def test_whitespace_field_id_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="   ",
            session_id="session-001",
            sequence=0,
        )


def test_empty_session_id_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="",
            sequence=0,
        )


def test_whitespace_session_id_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="   ",
            sequence=0,
        )


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):
        FieldState(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            timestamp=datetime(2026, 8, 14, 12, 0),
        )


def test_empty_state_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            state="   ",
        )


def test_non_numeric_metric_rejected():
    with pytest.raises(TypeError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            metrics={"S": "invalid"},
        )


def test_boolean_metric_rejected():
    with pytest.raises(TypeError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            metrics={"S": True},
        )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_metric_rejected(value):
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            metrics={"S": value},
        )


def test_empty_metric_name_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            metrics={"": 0.5},
        )


def test_whitespace_metric_name_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            metrics={"   ": 0.5},
        )


def test_failure_mode_must_be_non_empty_string():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            active_failure_modes=("   ",),
        )


def test_duplicate_failure_modes_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            active_failure_modes=("FM-01", "FM-01"),
        )


def test_field_state_is_frozen():
    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=0,
    )

    with pytest.raises(FrozenInstanceError):
        state.state = "CRITICAL"


def test_metrics_are_immutable():
    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=0,
        metrics={"S": 0.9},
    )

    with pytest.raises(TypeError):
        state.metrics["S"] = 0.1


def test_source_metrics_cannot_mutate_snapshot():
    source_metrics = {"S": 0.9}

    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=0,
        metrics=source_metrics,
    )

    source_metrics["S"] = 0.1

    assert state.metric("S") == 0.9


def test_failure_modes_are_immutable_tuple():
    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=0,
        active_failure_modes=["FM-01"],
    )

    assert isinstance(state.active_failure_modes, tuple)
    assert state.active_failure_modes == ("FM-01",)


def test_explicit_timestamp_supports_replay_and_deterministic_tests():
    timestamp = datetime(
        2026,
        8,
        14,
        12,
        0,
        tzinfo=timezone.utc,
    )

    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=10,
        timestamp=timestamp,
    )

    assert state.timestamp == timestamp
