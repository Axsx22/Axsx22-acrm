from datetime import datetime, timezone

import pytest

from acrm_core.runtime import FieldRuntime, SpecialistGovernance, parse_conversation
from acrm_core.runtime.failure_taxonomy import Calibration, FAILURE_MODES, run_calibration_checks


def test_v7_failure_taxonomy_and_calibration_are_promoted():
    assert len(FAILURE_MODES) == 17
    checks = run_calibration_checks()
    assert all(checks.values())
    assert Calibration.platt(0.8) > Calibration.platt(0.2)
    assert abs(sum(Calibration.softmax((1, 2, 3))) - 1.0) < 1e-9


def test_v7_runtime_uses_real_turns_and_records_observations():
    turns = parse_conversation(
        "user: explain the system failure\n"
        "model: the system failure follows a recovery path\n"
        "user: what causes the failure?\n"
        "model: telemetry and sync failure can contribute"
    )
    result = FieldRuntime().evaluate(
        turns,
        field_id="test-field",
        session_id="test-session",
        sequence=1,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert result.field_state.field_id == "test-field"
    assert result.field_state.session_id == "test-session"
    assert result.sequential_similarity
    assert result.observations
    assert result.governance is not None


def test_v83_balance_gate_can_freeze_conflicting_evidence():
    governance = SpecialistGovernance()
    turns = ({"role": "user", "text": "technical system failure and safety risk"}, {"role": "model", "text": "the system may recover but danger remains"})

    def reasoner(sp, _turns, _metrics):
        if sp.id == "tec":
            return {"applicable": True, "diagnosis": "technical conflict", "confidence": 1, "evidence_strength": 1, "direction": 1}
        if sp.id == "saf":
            return {"applicable": True, "diagnosis": "safety conflict", "confidence": 1, "evidence_strength": 1, "direction": -1}
        return {"applicable": False}

    governance.reasoner = reasoner
    result = governance.evaluate(turns, {"avgS": 0.6, "avgRho": 0.6, "lastH": 0.3, "RS": 0.8, "anomalyIdx": -1})
    assert result.frozen is True
    assert result.vt is None
    assert result.freeze_reason == "EVIDENCE_BALANCE"


def test_v83_does_not_freeze_when_evidence_is_directional():
    governance = SpecialistGovernance()

    def reasoner(sp, _turns, _metrics):
        if sp.id == "tec":
            return {"applicable": True, "diagnosis": "coherent", "confidence": 1, "evidence_strength": 1, "direction": 1}
        return {"applicable": False}

    governance.reasoner = reasoner
    result = governance.evaluate(
        ({"role": "user", "text": "technical system"}, {"role": "model", "text": "technical recovery"}),
        {"avgS": 0.8, "avgRho": 0.8, "lastH": 0.2, "RS": 0.9, "anomalyIdx": -1},
    )
    assert result.frozen is False
    assert result.vt is not None
    assert result.vt > 0


def test_runtime_rejects_short_input():
    with pytest.raises(ValueError):
        FieldRuntime().evaluate(({"role": "user", "text": "only one"},))
