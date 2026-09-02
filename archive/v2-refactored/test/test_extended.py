"""Additional regression tests for the archived v2.0 implementation."""

import pytest

from core.audit import AuditScorer
from core.cluster import MultiNodeACRMCluster
from core.fault import FaultToleranceManager
from core.gate import RecoveryGate
from core.tracker import AdaptiveEMATracker


class DummySystem:
    def __init__(self, session_id):
        self.session_id = session_id
        self.tracker = AdaptiveEMATracker()
        self.gate = RecoveryGate()

    def step(self, value, confidence, error):
        self.tracker.update(value, confidence)
        self.gate.update(error)
        return {"ema": self.tracker.ema, "state": self.gate.state}


def test_audit_scorer_import_and_recovery_latency():
    scorer = AuditScorer()
    logs = [
        {"state": "STABLE"},
        {"state": "DRIFTED"},
        {"state": "RECOVERING"},
        {"state": "STABLE"},
    ]
    assert scorer.recovery_latency(logs) == 1


def test_recovery_gate_requires_three_consecutive_recovery_observations():
    gate = RecoveryGate(stability_window=3, drift_threshold=0.25)
    assert gate.update(0.30) == "DRIFTED"
    assert gate.update(0.20) == "RECOVERING"
    assert gate.update(0.20) == "RECOVERING"
    assert gate.update(0.20) == "STABLE"


def test_recovery_gate_rejects_non_finite_error():
    gate = RecoveryGate()
    with pytest.raises(ValueError):
        gate.update(float("nan"))


def test_fault_recovery_restores_checkpoint_without_duplicate_node():
    cluster = MultiNodeACRMCluster(num_nodes=1, system_cls=DummySystem)
    manager = FaultToleranceManager(cluster)
    node = cluster.nodes[0]

    node.system.tracker.ema = 0.8
    node.system.tracker.confidence = 0.6
    node.system.gate.state = "RECOVERING"
    node.local_buffer.append({"event": "checkpointed"})
    manager.checkpoint_all()

    node.system.tracker.ema = 0.1
    node.system.tracker.confidence = 0.1
    node.local_buffer.clear()

    recovered = manager.recover_node(node.node_id)

    assert recovered is not None
    assert len(cluster.nodes) == 1
    assert recovered.system.tracker.ema == pytest.approx(0.8)
    assert recovered.system.tracker.confidence == pytest.approx(0.6)
    assert recovered.system.gate.state == "RECOVERING"
    assert recovered.local_buffer == [{"event": "checkpointed"}]
