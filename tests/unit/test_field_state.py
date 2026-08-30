from datetime import datetime, timezone

import pytest

from acrm_core.field.state import FieldState


def make_state(**overrides):
    values = {
        "field_id": "field-1",
        "session_id": "session-1",
        "sequence": 0,
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "metrics": {"score": 1.0},
        "failure_modes": ("none",),
        "governance_confidence": 0.5,
    }
    values.update(overrides)
    return FieldState(**values)


def test_valid_state():
    state = make_state()
    assert state.field_id == "field-1"
    assert state.metric("score") == 1.0


def test_field_id_required():
    with pytest.raises(ValueError):
        make_state(field_id="")


def test_session_id_required():
    with pytest.raises(ValueError):
        make_state(session_id="")


def test_negative_sequence_rejected():
    with pytest.raises(ValueError):
        make_state(sequence=-1)


def test_sequence_must_be_integer():
    with pytest.raises(TypeError):
        make_state(sequence=1.5)


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):
        make_state(timestamp=datetime(2026, 1, 1))


def test_non_datetime_timestamp_rejected():
    with pytest.raises(TypeError):
        make_state(timestamp="2026-01-01")


def test_non_finite_metric_rejected():
    with pytest.raises(ValueError):
        make_state(metrics={"score": float("nan")})


def test_metric_must_be_numeric():
    with pytest.raises(TypeError):
        make_state(metrics={"score": "1"})


def test_metrics_are_immutable():
    state = make_state()
    with pytest.raises(TypeError):
        state.metrics["score"] = 2.0


def test_duplicate_failure_modes_rejected():
    with pytest.raises(ValueError):
        make_state(failure_modes=("x", "x"))


def test_failure_mode_lookup():
    state = make_state(failure_modes=("timeout",))
    assert state.has_failure_mode("timeout")
    assert not state.has_failure_mode("other")


def test_confidence_range_rejected():
    with pytest.raises(ValueError):
        make_state(governance_confidence=1.1)


def test_confidence_must_be_numeric():
    with pytest.raises(TypeError):
        make_state(governance_confidence="0.5")


def test_recorded_at_utc():
    state = make_state()
    assert state.recorded_at_utc.tzinfo == timezone.utc


def test_state_is_frozen():
    state = make_state()
    with pytest.raises(AttributeError):
        state.sequence = 2
