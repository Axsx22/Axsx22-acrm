"""
Fault Tolerance — Refactored v2.0
Contract: checkpoint/restore preserves deterministic state.
"""

import copy
import time
from typing import Dict, List, Optional


class HeartbeatMonitor:
    """Tracks node liveness."""

    def __init__(self, timeout: float = 3.0):
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        self.timeout = timeout
        self.last_seen: Dict[str, float] = {}

    def beat(self, node_id: str):
        self.last_seen[node_id] = time.time()

    def is_alive(self, node_id: str) -> bool:
        return (time.time() - self.last_seen.get(node_id, 0)) < self.timeout


class StateSnapshot:
    """Snapshot of the state required for node recovery."""

    def __init__(self, node):
        if node.system is None:
            raise RuntimeError("Cannot checkpoint node without an injected system")
        self.node_id = node.node_id
        self.ema_state = node.system.tracker.ema
        self.confidence = node.system.tracker.confidence
        self.gate_state = node.system.gate.state
        self.buffer_copy = copy.deepcopy(node.local_buffer)
        self.timestamp = time.time()


class CheckpointManager:
    """Manages state snapshots for recovery."""

    def __init__(self):
        self.snapshots: Dict[str, StateSnapshot] = {}

    def checkpoint(self, node):
        snap = StateSnapshot(node)
        self.snapshots[node.node_id] = snap
        return snap

    def restore(self, node, snapshot: StateSnapshot):
        if node.system is None:
            raise RuntimeError("Cannot restore node without an injected system")
        node.system.tracker.ema = snapshot.ema_state
        node.system.tracker.confidence = snapshot.confidence
        node.system.gate.state = snapshot.gate_state
        node.local_buffer = copy.deepcopy(snapshot.buffer_copy)


class FaultToleranceManager:
    """
    Orchestrates fault detection and recovery.

    Contract: recovery preserves state from last checkpoint.
    """

    def __init__(self, cluster):
        self.cluster = cluster
        self.heartbeat = HeartbeatMonitor()
        self.checkpoints = CheckpointManager()

    def monitor(self):
        for node in self.cluster.nodes:
            self.heartbeat.beat(node.node_id)

    def detect_failures(self) -> List:
        return [n for n in self.cluster.nodes
                if not self.heartbeat.is_alive(n.node_id)]

    def checkpoint_all(self):
        for node in self.cluster.nodes:
            self.checkpoints.checkpoint(node)

    def recover_node(self, node_id: str):
        """Replace a failed node using its checkpoint and the cluster's system factory."""
        snapshot = self.checkpoints.snapshots.get(node_id)
        if snapshot is None:
            return None
        if self.cluster.system_cls is None:
            raise RuntimeError("Cluster system_cls is required for node recovery")

        from .cluster import ACRMNode

        old_node = next((n for n in self.cluster.nodes if n.node_id == node_id), None)
        if old_node is None:
            return None

        new_node = ACRMNode(node_id, self.cluster.bus)
        new_node.system = self.cluster.system_cls(session_id=node_id)
        self.checkpoints.restore(new_node, snapshot)

        self.cluster.nodes = [
            new_node if node.node_id == node_id else node
            for node in self.cluster.nodes
        ]
        self.heartbeat.beat(node_id)
        return new_node
