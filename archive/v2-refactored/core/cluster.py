"""
Multi-Node Cluster — Refactored v2.0
Contract: event bus is decoupled; nodes process independently.
"""

import uuid
from typing import List, Dict, Any


class EventBus:
    """Simple pub-sub event bus."""

    def __init__(self):
        self.subscribers: List[Any] = []

    def publish(self, event: dict):
        for sub in self.subscribers:
            sub.receive(event)

    def subscribe(self, node):
        self.subscribers.append(node)


class ACRMNode:
    """
    Single node in ACRM cluster.
    Contract: local processing only; global state via EventBus.
    """

    def __init__(self, node_id: str, bus: EventBus):
        self.node_id = node_id
        self.bus = bus
        self.system = None  # Will be injected
        self.local_buffer: List[dict] = []

    def receive(self, event: dict):
        if event.get("source") != self.node_id:
            self.local_buffer.append(event)

    def process_local(self, value, confidence, error):
        if self.system is None:
            raise RuntimeError("System not injected")
        result = self.system.step(value, confidence, error)
        self.bus.publish({"source": self.node_id, **result})
        return result


class MultiNodeACRMCluster:
    """Cluster of ACRM nodes with shared event bus."""

    def __init__(self, num_nodes: int = 3, system_cls=None):
        self.bus = EventBus()
        self.nodes: List[ACRMNode] = []
        self.system_cls = system_cls

        for _ in range(num_nodes):
            node_id = str(uuid.uuid4())[:8]
            node = ACRMNode(node_id, self.bus)
            if system_cls:
                node.system = system_cls(session_id=node_id)
            self.bus.subscribe(node)
            self.nodes.append(node)

    def step_all(self, inputs):
        results = []
        for node, (v, c, e) in zip(self.nodes, inputs):
            results.append(node.process_local(v, c, e))
        return results
