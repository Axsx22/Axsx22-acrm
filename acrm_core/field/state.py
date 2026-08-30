"""Validated immutable recorded state for ACRM v8.5."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class FieldState:
    """Recorded field state; no inference, causality, decisions, or intervention."""

    field_id: str
    session_id: str
    sequence: int
    timestamp: datetime
    metrics: Mapping[str, float] = field(default_factory=dict)
    failure_modes: tuple[str, ...] = ()
    governance_confidence: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.field_id, str) or not self.field_id.strip():
            raise ValueError("field_id must be a non-empty string")
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise TypeError("sequence must be an integer")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp must be a datetime")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        if not isinstance(self.metrics, Mapping):
            raise TypeError("metrics must be a mapping")
        for name, value in self.metrics.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("metric names must be non-empty strings")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"metric '{name}' must be numeric")
            if not math.isfinite(float(value)):
                raise ValueError(f"metric '{name}' must be finite")
        if not isinstance(self.failure_modes, tuple):
            raise TypeError("failure_modes must be a tuple")
        if any(not isinstance(x, str) or not x.strip() for x in self.failure_modes):
            raise ValueError("failure-mode identifiers must be non-empty strings")
        if len(self.failure_modes) != len(set(self.failure_modes)):
            raise ValueError("failure_modes must not contain duplicates")
        if isinstance(self.governance_confidence, bool) or not isinstance(self.governance_confidence, (int, float)):
            raise TypeError("governance_confidence must be numeric")
        confidence = float(self.governance_confidence)
        if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
            raise ValueError("governance_confidence must be finite and between 0.0 and 1.0")
        object.__setattr__(self, "metrics", MappingProxyType(dict(self.metrics)))
        object.__setattr__(self, "failure_modes", tuple(self.failure_modes))

    def metric(self, name: str) -> float:
        return self.metrics[name]

    def has_failure_mode(self, mode: str) -> bool:
        return mode in self.failure_modes

    @property
    def recorded_at_utc(self) -> datetime:
        return self.timestamp.astimezone(timezone.utc)
