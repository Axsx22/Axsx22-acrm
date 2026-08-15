from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class FieldState:
    """
    Immutable runtime snapshot of the observable ACRM field state.

    This contract stores observations only. It does not modify model
    execution, model output, sampling, or any underlying model state.

    Responsibilities of FieldState:
    - represent one immutable runtime observation snapshot;
    - enforce local structural and type invariants;
    - provide deterministic access to observed metrics and failure modes.

    Responsibilities NOT owned by FieldState:
    - temporal ordering across multiple snapshots;
    - session continuity;
    - state-transition policy;
    - metric semantic definitions;
    - failure-mode taxonomy;
    - governance decision logic.
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
        # Identity invariants
        if not isinstance(self.field_id, str) or not self.field_id.strip():
            raise ValueError("field_id must be a non-empty string")

        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string")

        # Sequence invariant
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise TypeError("sequence must be an integer")

        if self.sequence < 0:
            raise ValueError("sequence must be >= 0")

        # Timestamp invariant
        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp must be a datetime")

        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")

        # State structural invariant.
        # Semantic state vocabulary is intentionally not enforced here.
        if not isinstance(self.state, str) or not self.state.strip():
            raise ValueError("state must be a non-empty string")

        # Governance confidence invariant
        if (
            isinstance(self.governance_confidence, bool)
            or not isinstance(self.governance_confidence, (int, float))
        ):
            raise TypeError("governance_confidence must be numeric")

        if not isfinite(float(self.governance_confidence)):
            raise ValueError("governance_confidence must be finite")

        if not 0.0 <= float(self.governance_confidence) <= 1.0:
            raise ValueError(
                "governance_confidence must be between 0.0 and 1.0"
            )

        # Normalize and validate metrics.
        normalized_metrics: dict[str, float] = {}

        for name, value in self.metrics.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    "metric names must be non-empty strings"
                )

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(
                    f"metric '{name}' must contain a numeric value"
                )

            if not isfinite(float(value)):
                raise ValueError(
                    f"metric '{name}' must contain a finite numeric value"
                )

            normalized_metrics[name] = float(value)

        # Normalize failure modes into an immutable tuple.
        normalized_failure_modes: list[str] = []

        for failure_mode in self.active_failure_modes:
            if (
                not isinstance(failure_mode, str)
                or not failure_mode.strip()
            ):
                raise ValueError(
                    "failure modes must be non-empty strings"
                )

            if failure_mode in normalized_failure_modes:
                raise ValueError(
                    f"duplicate failure mode: {failure_mode}"
                )

            normalized_failure_modes.append(failure_mode)

        # Deepen immutability of container fields.
        object.__setattr__(
            self,
            "metrics",
            MappingProxyType(normalized_metrics),
        )

        object.__setattr__(
            self,
            "active_failure_modes",
            tuple(normalized_failure_modes),
        )

        # Normalize numeric confidence to float.
        object.__setattr__(
            self,
            "governance_confidence",
            float(self.governance_confidence),
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
        timestamp: datetime | None = None,
    ) -> "FieldState":
        """
        Create a field snapshot.

        If timestamp is omitted, the current UTC time is used.
        An explicit timestamp is supported for deterministic testing,
        replay, and imported observations.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        return cls(
            field_id=field_id,
            session_id=session_id,
            sequence=sequence,
            timestamp=timestamp,
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
