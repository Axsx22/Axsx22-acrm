"""Field-relative trajectory and dynamic tolerance primitives for Session C."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from statistics import median
from typing import Iterable, Mapping

from acrm_core.session_c.observation import EvolutionObservation, ObservationKind

@dataclass(frozen=True, slots=True)
class TrajectoryProfile:
    """Descriptive temporal profile; no judgment is assigned."""
    observation_count: int
    by_kind: Mapping[ObservationKind, int]
    first_observed_at: datetime | None
    last_observed_at: datetime | None
    recurrence: float
    persistence: float

@dataclass(frozen=True, slots=True)
class DynamicEnvelope:
    """Empirically derived operating envelope for one runtime signal."""
    metric_name: str
    baseline: float
    warning_limit: float
    critical_limit: float
    sample_count: int
    def __post_init__(self) -> None:
        if not isinstance(self.metric_name, str) or not self.metric_name.strip(): raise ValueError("metric_name must be non-empty")
        if not all(isfinite(float(v)) for v in (self.baseline, self.warning_limit, self.critical_limit)): raise ValueError("envelope values must be finite")
        if self.sample_count < 1: raise ValueError("sample_count must be >= 1")
        if self.warning_limit > self.critical_limit: raise ValueError("warning_limit cannot exceed critical_limit")

@dataclass(frozen=True, slots=True)
class ThresholdApproach:
    value: float
    state: str
    distance_to_critical: float

@dataclass(frozen=True, slots=True)
class EvolutionReadiness:
    state: str
    approach: ThresholdApproach
    persistence: float
    observation_count: int
    ready: bool
    reason: str

class TrajectoryAnalyzer:
    def profile(self, observations: Iterable[EvolutionObservation]) -> TrajectoryProfile:
        items = tuple(observations); counts: dict[ObservationKind, int] = {}
        for item in items: counts[item.kind] = counts.get(item.kind, 0) + 1
        ordered = sorted(items, key=lambda x: x.observed_at_utc); kinds = len(counts)
        recurrence = 0.0 if not items else (len(items) - kinds) / len(items)
        persistence = 0.0 if len(ordered) <= 1 else sum(a.kind == b.kind for a,b in zip(ordered, ordered[1:])) / (len(ordered)-1)
        return TrajectoryProfile(len(items), dict(counts), ordered[0].observed_at_utc if ordered else None, ordered[-1].observed_at_utc if ordered else None, recurrence, persistence)

class FieldEnvelopeEstimator:
    def estimate(self, observations: Iterable[EvolutionObservation], *, metric_name: str, warning_quantile: float = 0.90, critical_quantile: float = 0.975) -> DynamicEnvelope:
        if not 0.0 < warning_quantile <= critical_quantile <= 1.0: raise ValueError("quantiles must satisfy 0 < warning <= critical <= 1")
        values = [float(v) for o in observations if isinstance((v:=o.context.get(metric_name)), (int,float)) and not isinstance(v,bool) and isfinite(float(v))]
        if not values: raise ValueError(f"no numeric field history for metric {metric_name!r}")
        ordered = sorted(values)
        return DynamicEnvelope(metric_name, median(ordered), self._quantile(ordered, warning_quantile), self._quantile(ordered, critical_quantile), len(ordered))
    @staticmethod
    def _quantile(values: list[float], q: float) -> float:
        if len(values) == 1: return values[0]
        position=(len(values)-1)*q; lower=int(position); upper=min(lower+1,len(values)-1); fraction=position-lower
        return values[lower]+(values[upper]-values[lower])*fraction

class DynamicReadinessEvaluator:
    def evaluate(self, observations: Iterable[EvolutionObservation], *, envelope: DynamicEnvelope, current_value: float, min_observations: int = 3, persistence_floor: float = 0.5) -> EvolutionReadiness:
        if min_observations < 1: raise ValueError("min_observations must be >= 1")
        if not 0.0 <= persistence_floor <= 1.0: raise ValueError("persistence_floor must be between 0 and 1")
        profile=TrajectoryAnalyzer().profile(observations); value=float(current_value)
        if not isfinite(value): raise ValueError("current_value must be finite")
        state="CRITICAL" if value >= envelope.critical_limit else "WARNING" if value >= envelope.warning_limit else "NORMAL"
        approach=ThresholdApproach(value,state,max(0.0,envelope.critical_limit-value))
        ready=profile.observation_count >= min_observations and state in {"WARNING","CRITICAL"} and profile.persistence >= persistence_floor
        if state == "NORMAL": reason="current signal remains inside the field-derived envelope"
        elif profile.observation_count < min_observations: reason="insufficient trajectory history for an evolution signal"
        elif profile.persistence < persistence_floor: reason="approach is not persistent enough in the observed trajectory"
        else: reason="trajectory persistently approaches or occupies the field-derived limit"
        return EvolutionReadiness(state,approach,profile.persistence,profile.observation_count,ready,reason)
