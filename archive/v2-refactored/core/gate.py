"""
Recovery Gate — Refactored v2.0
Contract: state transitions are deterministic and evidence-based.
"""

import math
from typing import List


class RecoveryGate:
    """
    Three-state machine: STABLE → DRIFTED → RECOVERING → STABLE

    Invariant: can only exit DRIFTED if error is at or below the threshold
               for stability_window consecutive observations.

    CHANGELOG from original v2.0:
    - Added _history to track recent errors (evidence-based)
    - RECOVERING counts consecutive qualifying observations directly
    - stable_counter resets immediately when an error spikes
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
        self._history: List[float] = []

    def update(self, error: float) -> str:
        """Update state from one finite error observation."""
        error = float(error)
        if not math.isfinite(error):
            raise ValueError("error must be finite")

        self._history.append(error)
        if len(self._history) > self.stability_window:
            self._history.pop(0)

        if error > self.drift_threshold:
            self.state = "DRIFTED"
            self.stable_counter = 0
            return self.state

        if self.state == "DRIFTED":
            self.state = "RECOVERING"
            self.stable_counter = 0

        if self.state == "RECOVERING":
            self.stable_counter += 1
            if self.stable_counter >= self.stability_window:
                self.state = "STABLE"
                self.stable_counter = 0

        return self.state

    def get_evidence(self) -> List[float]:
        """Return recent error history for audit."""
        return self._history.copy()
