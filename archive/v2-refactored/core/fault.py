"""
Fault Tolerance — Refactored v2.0
Contract: checkpoint/restore preserves deterministic state.
"""

import time
import copy
from typing import Dict, Optional, List


class HeartbeatMonitor:
    """Tracks node liveness."""

    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout
        self.last_seen: Dict[str, float] = {}

    def beat(self, node_id: str):
        self.last_seen[node_id] = time.time()

    def is_alive(self, node_id: str) -> bool:
        return (time.time() - self.last_seen.get(node_id, 0)) < self.timeout


class StateSnapshot:
    """Immutable snapshot of node state."""

    def __init__(self, node):
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
        snap = self.checkpoints.snapshots.get(node_id)
        if not snap:
            return None
        # Create new node with same ID
        from .cluster import ACRMNode
        new_node = ACRMNode(node_id, self.cluster.bus)
        self.checkpoints.restore(new_node, snap)
        self.cluster.bus.subscribe(new_node)
        self.cluster.nodes.append(new_node)
        return new_node
