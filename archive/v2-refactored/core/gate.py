"""
Recovery Gate — Refactored v2.0
Contract: state transitions are deterministic and evidence-based.
"""

from typing import List


class RecoveryGate:
    """
    Three-state machine: STABLE → DRIFTED → RECOVERING → STABLE

    Invariant: can only exit DRIFTED if error < threshold 
               for stability_window consecutive steps.

    CHANGELOG from original v2.0:
    - Added _history to track recent errors (evidence-based)
    - RECOVERING now requires ALL recent errors below threshold
    - stable_counter resets if any recent error spikes
    """

    def __init__(self, stability_window: int = 5, drift_threshold: float = 0.25):
        if stability_window < 1:
            raise ValueError("stability_window must be >= 1")
        if not (0 < drift_threshold < 1):
            raise ValueError("drift_threshold must be in (0, 1)")

        self.state = "STABLE"
        self.stability_window = stability_window
        self.drift_threshold = drift_threshold
        self.stable_counter = 0
        self._history: List[float] = []  # Evidence buffer

    def update(self, error: float) -> str:
        """
        Update state machine with new error observation.

        Args:
            error: current error metric (lower is better)

        Returns:
            Current state string
        """
        # Record evidence
        self._history.append(float(error))
        if len(self._history) > self.stability_window:
            self._history.pop(0)

        # DRIFTED: error exceeds threshold
        if error > self.drift_threshold:
            self.state = "DRIFTED"
            self.stable_counter = 0
            return self.state

        # Transition: DRIFTED → RECOVERING
        if self.state == "DRIFTED":
            self.state = "RECOVERING"
            self.stable_counter = 0

        # RECOVERING: need sustained stability
        if self.state == "RECOVERING":
            # All recent errors must be below threshold
            if len(self._history) == self.stability_window and \
               all(e <= self.drift_threshold for e in self._history):
                self.stable_counter += 1
            else:
                self.stable_counter = 0  # Reset: evidence insufficient

            if self.stable_counter >= self.stability_window:
                self.state = "STABLE"
                self.stable_counter = 0

        return self.state

    def get_evidence(self) -> List[float]:
        """Return recent error history for audit."""
        return self._history.copy()
