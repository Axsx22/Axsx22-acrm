"""Field-relative trajectory and dynamic tolerance primitives for Session C."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable, Mapping

from acrm_core.evolution.session_c import EvolutionObservation, ObservationKind


@dataclass(frozen=True, slots=True)
class TrajectoryProfile:
    """Descriptive trajectory statistics; no judgment is assigned."""
    observation_count: int
    by_kind: Mapping[ObservationKind, int]
    first_observed_at: datetime | None
    last_observed_at: datetime | None
    recurrence: float
    persistence: float


@dataclass(frozen=True, slots=True)
class DynamicEnvelope:
    """System-relative normalized operating envelope."""
    reference_capacity: float = 1.0
    warning_fraction: float = 0.8
    critical_fraction: float = 1.0

    def __post_init__(self) -> None:
        for name, value in (("reference_capacity", self.reference_capacity), ("warning_fraction", self.warning_fraction), ("critical_fraction", self.critical_fraction)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
                raise ValueError(f"{name} must be finite numeric")
        if self.reference_capacity <= 0:
            raise ValueError("reference_capacity must be positive")
        if not 0 < self.warning_fraction <= self.critical_fraction:
            raise ValueError("warning_fraction must be > 0 and <= critical_fraction")


@dataclass(frozen=True, slots=True)
class ThresholdApproach:
    normalized_load: float
    state: str
    distance_to_critical: float


class TrajectoryAnalyzer:
    """Derive temporal descriptive statistics without scoring observations."""

    def profile(self, observations: Iterable[EvolutionObservation]) -> TrajectoryProfile:
        items = tuple(observations)
        counts: dict[ObservationKind, int] = {}
        for item in items:
            counts[item.kind] = counts.get(item.kind, 0) + 1
        ordered = sorted(items, key=lambda x: x.observed_at_utc)
        kinds = len(counts)
        recurrence = 0.0 if not items else (len(items) - kinds) / len(items)
        persistence = 0.0
        if len(ordered) > 1:
            persistence = sum(a.kind == b.kind for a, b in zip(ordered, ordered[1:])) / (len(ordered) - 1)
        return TrajectoryProfile(len(items), dict(counts), ordered[0].observed_at_utc if ordered else None, ordered[-1].observed_at_utc if ordered else None, recurrence, persistence)

    def approach(self, normalized_load: float, envelope: DynamicEnvelope) -> ThresholdApproach:
        load = float(normalized_load)
        if not isfinite(load) or load < 0:
            raise ValueError("normalized_load must be finite and non-negative")
        if load >= envelope.critical_fraction:
            state = "CRITICAL"
        elif load >= envelope.warning_fraction:
            state = "WARNING"
        else:
            state = "NORMAL"
        return ThresholdApproach(load, state, max(0.0, envelope.critical_fraction - load))
