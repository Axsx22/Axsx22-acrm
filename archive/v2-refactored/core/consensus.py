"""
Global Consensus Layer — Refactored v2.0
Contract: weights are evidence-based, not arbitrary.
"""

from typing import Dict


class GlobalConsensusLayer:
    """
    Aggregates EMA across cluster nodes with evidence-based weighting.

    CHANGELOG from original v2.0:
    - Weight calculation uses confidence * stability_factor
    - Removed arbitrary penalty constants
    - Added minimum weight floor (0.01) to prevent collapse
    """

    def __init__(self, cluster, alpha: float = 0.1):
        self.cluster = cluster
        self.global_ema = 0.5
        self.alpha = alpha
        self.node_weights: Dict[str, float] = {}

    def _stability_factor(self, node) -> float:
        """
        Calculate stability factor based on node state.
        Returns value in [0, 1] where 1 = fully stable.
        """
        state = node.system.gate.state
        if state == "STABLE":
            return 1.0
        elif state == "RECOVERING":
            return 0.7
        elif state == "DRIFTED":
            return 0.0
        return 0.5

    def compute_node_weight(self, node) -> float:
        """
        Weight = confidence * stability_factor
        Minimum weight: 0.01 (prevents complete exclusion)
        """
        confidence = node.system.tracker.confidence
        stability = self._stability_factor(node)
        weight = max(0.01, confidence * stability)
        return weight

    def aggregate(self) -> float:
        weighted_sum = 0.0
        total_weight = 0.0

        for node in self.cluster.nodes:
            w = self.compute_node_weight(node)
            weighted_sum += w * node.system.tracker.ema
            total_weight += w
            self.node_weights[node.node_id] = round(w, 4)

        if total_weight == 0:
            return self.global_ema

        new_global = weighted_sum / total_weight
        self.global_ema = (1 - self.alpha) * self.global_ema + self.alpha * new_global
        return self.global_ema

    def broadcast(self):
        """Broadcast global EMA to all nodes (soft coupling)."""
        for node in self.cluster.nodes:
            node.system.tracker.ema = (
                0.8 * node.system.tracker.ema + 
                0.2 * self.global_ema
            )

    def step(self) -> dict:
        self.aggregate()
        self.broadcast()
        return {
            "global_ema": round(self.global_ema, 6),
            "node_weights": self.node_weights
        }
