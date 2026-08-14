from datetime import timezone

import pytest

from acrm_core.field.state import FieldState


def test_create_field_state():
    state = FieldState.create(
        field_id="field-001",
        session_id="session-001",
        sequence=0,
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
    assert state.timestamp.tzinfo == timezone.utc


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


def test_invalid_confidence_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="field-001",
            session_id="session-001",
            sequence=0,
            governance_confidence=1.5,
        )


def test_empty_field_id_rejected():
    with pytest.raises(ValueError):
        FieldState.create(
            field_id="",
            session_id="session-001",
            sequence=0,
        )
