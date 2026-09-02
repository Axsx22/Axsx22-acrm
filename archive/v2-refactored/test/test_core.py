"""
Unit tests for refactored v2.0 core.
Contract-focused tests aligned with v8.5 discipline.
"""

import pytest
from core.tracker import AdaptiveEMATracker, TrackerConfig
from core.gate import RecoveryGate
from core.session import SessionIsolationManager


class TestAdaptiveEMATracker:
    def test_initial_state(self):
        t = AdaptiveEMATracker()
        assert t.ema == 0.5
        assert t.confidence == 0.0

    def test_finite_output(self):
        t = AdaptiveEMATracker()
        result = t.update(float("inf"), 0.5)
        assert result == pytest.approx(0.5)  # Falls back to anchor

    def test_confidence_clamping(self):
        t = AdaptiveEMATracker()
        t.update(0.8, 2.0)  # Over 1.0
        assert t.confidence <= 1.0

    def test_invalid_config(self):
        with pytest.raises(ValueError):
            TrackerConfig(alpha=1.5)


class TestRecoveryGate:
    def test_stable_to_drifted(self):
        g = RecoveryGate()
        assert g.update(0.1) == "STABLE"
        assert g.update(0.3) == "DRIFTED"

    def test_recovery_requires_sustained_stability(self):
        g = RecoveryGate(stability_window=3, drift_threshold=0.25)
        g.update(0.3)  # DRIFTED
        g.update(0.2)  # RECOVERING
        g.update(0.2)  # Still RECOVERING (need 3 stable)
        assert g.state == "RECOVERING"
        g.update(0.2)  # Now should be STABLE
        assert g.state == "STABLE"

    def test_recovery_resets_on_spike(self):
        g = RecoveryGate(stability_window=3, drift_threshold=0.25)
        g.update(0.3)  # DRIFTED
        g.update(0.2)  # RECOVERING
        g.update(0.2)  # RECOVERING
        g.update(0.3)  # Spike! Should reset
        assert g.state == "DRIFTED"


class TestSessionIsolation:
    def test_isolation(self):
        mgr = SessionIsolationManager()
        mgr.create_session("A")
        mgr.update("A", 0.7, 0.5)
        state = mgr.get("A")
        assert state.ema == 0.7
        assert state.confidence == 0.5

    def test_handoff_decay(self):
        mgr = SessionIsolationManager()
        mgr.create_session("A")
        mgr.update("A", 0.8, 1.0)
        mgr.handoff("A", "B")
        b = mgr.get("B")
        assert b.confidence == pytest.approx(0.8)  # 20% decay
