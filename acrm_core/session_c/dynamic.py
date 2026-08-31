"""Field-relative trajectory and dynamic tolerance primitives for Session C.

This module intentionally performs no promotion, voting, code generation, or
runtime mutation. It turns neutral observations into descriptive trajectory
statistics and an early-warning state for C-B.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Iterable, Mapping

from acrm_core.evolution.session_c import EvolutionObservation, ObservationKind


@dataclass(frozen=True, slots=True)
class TrajectoryProfile:
    """Descriptive profile of an ordered observation trajectory."""

    observation_count: int
    by_kind: Mapping[ObservationKind, int]
    first_observed_at: datetime | None
    last_observed_at: datetime | None
    recurrence: float
    persistence: float

    def __post_init__(self) -> None:
        if self.observation_count < 0:
            raise ValueError("observation_count cannot be negative")
        if not 0.0 <= self.recurrence <= 1.0:
            raise ValueError("recurrence must be between 0 and 1")
        if not 0.0 <= self.persistence <= 1.0:
            raise ValueError("persistence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class DynamicEnvelope:
    """Field-relative limit description.

    ``warning_fraction`` is a normalized fraction of the configured envelope
    that marks an approach-to-limit region. It is a policy parameter, not a
    claim that a universal threshold exists for every field.
    """

    reference_capacity: float = 1.0
    warning_fraction: float = 0.8
    critical_fraction: float = 1.0

    def __post_init__(self) -> None:
        for name, value in (
            ("reference_capacity", self.reference_capacity),
            ("warning_fraction", self.warning_fraction),
            ("critical_fraction", self.critical_fraction),
        ):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not isfinite(float(value)):
                raise ValueError(f"{name} must be finite")
        if self.reference_capacity <= 0:
            raise ValueError("reference_capacity must be positive")
        if not 0 < self.warning_fraction <= self.critical_fraction:
            raise ValueError("warning_fraction must be > 0 and <= critical_fraction")


@dataclass(frozen=True, slots=True)
class ThresholdApproach:
    """Current position relative to a field-relative envelope."""

    normalized_load: float
    state: str
    distance_to_critical: float

    def __post_init__(self) -> None:
        if not isfinite(float(self.normalized_load)):
            raise ValueError("normalized_load must be finite")
        if not isfinite(float(self.distance_to_critical)):
            raise ValueError("distance_to_critical must be finite")
        if self.state not in {"NORMAL", "WARNING", "CRITICAL"}:
            raise ValueError("state must be NORMAL, WARNING, or CRITICAL")


class TrajectoryAnalyzer:
    """Derive descriptive trajectory statistics without assigning judgment."""

    def profile(self, observations: Iterable[EvolutionObservation]) -> TrajectoryProfile:
        items = tuple(observations)
        counts: dict[ObservationKind, int] = {}
        for item in items:
            counts[item.kind] = counts.get(item.kind, 0) + 1

        unique_kinds = len(counts)
        recurrence = 0.0 if not items else max(0.0, (len(items) - unique_kinds) / len(items))

        persistence = 0.0
        if len(items) >= 2:
            ordered = sorted(items, key=lambda x: x.observed_at_utc)
            same_kind_pairs = sum(a.kind == b.kind for a, b in zip(ordered, ordered[1:]))
            persistence = same_kind_pairs / (len(items) - 1)

        ordered = sorted(items, key=lambda x: x.observed_at_utc)
        return TrajectoryProfile(
            observation_count=len(items),
            by_kind=dict(counts),
            first_observed_at=ordered[0].observed_at_utc if ordered else None,
            last_observed_at=ordered[-1].observed_at_utc if ordered else None,
            recurrence=recurrence,
            persistence=persistence,
        )

    def approach(self, normalized_load: float, envelope: DynamicEnvelope) -> ThresholdApproach:
        load = float(normalized_load)
        if not isfinite(load) or load < 0:
            raise ValueError("normalized_load must be finite and non-negative")
        warning = envelope.warning_fraction
        critical = envelope.critical_fraction
        if load >= critical:
            state = "CRITICAL"
        elif load >= warning:
            state = "WARNING"
        else:
            state = "NORMAL"
        return ThresholdApproach(
            normalized_load=load,
            state=state,
            distance_to_critical=max(0.0, critical - load),
        )
