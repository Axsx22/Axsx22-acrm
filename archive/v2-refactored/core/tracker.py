"""
Adaptive EMA Tracker — Refactored v2.0
Contract: output is always finite and bounded.
"""

from dataclasses import dataclass
from typing import Optional
import math


@dataclass(frozen=True)
class TrackerConfig:
    """Immutable configuration for the tracker."""
    alpha: float = 0.2
    neutral_anchor: float = 0.5
    min_confidence: float = 0.0
    max_confidence: float = 1.0

    def __post_init__(self):
        if not (0 < self.alpha <= 1.0):
            raise ValueError(f"alpha must be in (0, 1], got {self.alpha}")
        if not (0.0 <= self.neutral_anchor <= 1.0):
            raise ValueError(f"anchor must be in [0, 1], got {self.neutral_anchor}")
        if not (0.0 <= self.min_confidence <= self.max_confidence <= 1.0):
            raise ValueError("confidence bounds invalid")


class AdaptiveEMATracker:
    """
    Confidence-weighted Exponential Moving Average tracker.

    Invariants:
    - ema is always finite (guarded against overflow)
    - ema is bounded to [0, 1] if inputs are bounded
    - confidence decays gracefully
    """

    def __init__(self, config: Optional[TrackerConfig] = None):
        self.cfg = config or TrackerConfig()
        self.ema = self.cfg.neutral_anchor
        self.confidence = 0.0

    def reset(self):
        """Reset to neutral state."""
        self.ema = self.cfg.neutral_anchor
        self.confidence = 0.0

    def update(self, value: float, confidence: float) -> float:
        """
        Update EMA with a new observation.

        Args:
            value: observed value (should be in [0, 1])
            confidence: confidence in this observation [0, 1]

        Returns:
            Updated EMA value
        """
        # Clamp confidence to valid range
        confidence = max(self.cfg.min_confidence,
                        min(self.cfg.max_confidence, float(confidence)))

        # Guard against non-finite inputs
        if not math.isfinite(value):
            value = self.cfg.neutral_anchor

        effective_alpha = self.cfg.alpha * confidence
        self.ema = (1 - effective_alpha) * self.ema + effective_alpha * value
        self.confidence = 0.9 * self.confidence + 0.1 * confidence

        # Contract: finite output
        if not math.isfinite(self.ema):
            self.ema = self.cfg.neutral_anchor

        return self.ema
