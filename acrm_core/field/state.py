from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class FieldState:
    """
    Immutable runtime snapshot of the observable ACRM field state.

    This contract stores observations only. It does not modify model
    execution, model output, sampling, or any underlying model state.
    """

    field_id: str
    session_id: str
    sequence: int
    timestamp: datetime

    metrics: Mapping[str, float] = field(default_factory=dict)

    state: str = "UNKNOWN"
    active_failure_modes: tuple[str, ...] = ()
    governance_confidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.field_id:
            raise ValueError("field_id must not be empty")

        if not self.session_id:
            raise ValueError("session_id must not be empty")

        if self.sequence < 0:
            raise ValueError("sequence must be >= 0")

        if not 0.0 <= self.governance_confidence <= 1.0:
            raise ValueError(
                "governance_confidence must be between 0.0 and 1.0"
            )

        for name, value in self.metrics.items():
            if not isinstance(name, str) or not name:
                raise ValueError("metric names must be non-empty strings")

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"metric '{name}' must contain a numeric value"
                )

    @classmethod
    def create(
        cls,
        *,
        field_id: str,
        session_id: str,
        sequence: int,
        metrics: Mapping[str, float] | None = None,
        state: str = "UNKNOWN",
        active_failure_modes: tuple[str, ...] = (),
        governance_confidence: float = 0.0,
    ) -> "FieldState":
        """
        Create a field snapshot using a UTC timestamp.
        """
        return cls(
            field_id=field_id,
            session_id=session_id,
            sequence=sequence,
            timestamp=datetime.now(timezone.utc),
            metrics=dict(metrics or {}),
            state=state,
            active_failure_modes=tuple(active_failure_modes),
            governance_confidence=governance_confidence,
        )

    def metric(self, name: str) -> float | None:
        """Return a metric value, or None when it is not present."""
        return self.metrics.get(name)

    def has_failure_mode(self, failure_mode: str) -> bool:
        """Return whether a failure mode is active in this snapshot."""
        return failure_mode in self.active_failure_modes
