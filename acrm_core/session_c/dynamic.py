"""Field-relative trajectory and dynamic tolerance primitives for Session C.

The module deliberately separates descriptive trajectory measurements from
readiness decisions. Thresholds are configurable engineering parameters; they
are not presented as scientifically universal calibration constants.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from statistics import median
from typing import Iterable, Literal, Mapping

from acrm_core.session_c.observation import EvolutionObservation, ObservationKind


SignalDirection = Literal["high", "low"]


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
    direction: SignalDirection = "high"

    def __post_init__(self) -> None:
        if not isinstance(self.metric_name, str) or not self.metric_name.strip():
            raise ValueError("metric_name must be non-empty")
        if self.direction not in {"high", "low"}:
            raise ValueError("direction must be 'high' or 'low'")
        if not all(
            isfinite(float(value))
            for value in (self.baseline, self.warning_limit, self.critical_limit)
        ):
            raise ValueError("envelope values must be finite")
        if self.sample_count < 1:
            raise ValueError("sample_count must be >= 1")
        if self.direction == "high" and self.warning_limit > self.critical_limit:
            raise ValueError("warning_limit cannot exceed critical_limit for high direction")
        if self.direction == "low" and self.warning_limit < self.critical_limit:
            raise ValueError("warning_limit cannot be below critical_limit for low direction")


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
    signal_persistence: float
    observation_count: int
    ready: bool
    reason: str


class TrajectoryAnalyzer:
    """Compute temporal descriptors without assigning causal meaning."""

    def profile(
        self, observations: Iterable[EvolutionObservation]
    ) -> TrajectoryProfile:
        items = tuple(observations)
        counts: dict[ObservationKind, int] = {}
        for item in items:
            counts[item.kind] = counts.get(item.kind, 0) + 1

        ordered = sorted(items, key=lambda item: item.observed_at_utc)
        kinds = len(counts)
        recurrence = 0.0 if not items else (len(items) - kinds) / len(items)
        persistence = (
            0.0
            if len(ordered) <= 1
            else sum(
                first.kind == second.kind
                for first, second in zip(ordered, ordered[1:])
            )
            / (len(ordered) - 1)
        )

        return TrajectoryProfile(
            observation_count=len(items),
            by_kind=dict(counts),
            first_observed_at=(ordered[0].observed_at_utc if ordered else None),
            last_observed_at=(ordered[-1].observed_at_utc if ordered else None),
            recurrence=recurrence,
            persistence=persistence,
        )


class FieldEnvelopeEstimator:
    """Estimate a field-relative envelope from observed numeric history."""

    def estimate(
        self,
        observations: Iterable[EvolutionObservation],
        *,
        metric_name: str,
        warning_quantile: float = 0.90,
        critical_quantile: float = 0.975,
        direction: SignalDirection = "high",
    ) -> DynamicEnvelope:
        if not 0.0 < warning_quantile <= critical_quantile <= 1.0:
            raise ValueError(
                "quantiles must satisfy 0 < warning <= critical <= 1"
            )
        if direction not in {"high", "low"}:
            raise ValueError("direction must be 'high' or 'low'")

        values: list[float] = []
        for observation in observations:
            value = observation.context.get(metric_name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            numeric_value = float(value)
            if isfinite(numeric_value):
                values.append(numeric_value)

        if not values:
            raise ValueError(
                f"no numeric field history for metric {metric_name!r}"
            )

        ordered = sorted(values)
        if direction == "high":
            warning_limit = self._quantile(ordered, warning_quantile)
            critical_limit = self._quantile(ordered, critical_quantile)
        else:
            warning_limit = self._quantile(ordered, 1.0 - warning_quantile)
            critical_limit = self._quantile(ordered, 1.0 - critical_quantile)

        return DynamicEnvelope(
            metric_name=metric_name,
            baseline=median(ordered),
            warning_limit=warning_limit,
            critical_limit=critical_limit,
            sample_count=len(ordered),
            direction=direction,
        )

    @staticmethod
    def _directional_persistence(values: list[float], direction: SignalDirection) -> float:
        """Fraction of adjacent transitions that do not reverse the risk direction.

        For high-risk signals, flat or increasing transitions count as persistent;
        for low-risk signals, flat or decreasing transitions do. This is a numeric
        descriptor, not semantic persistence or causal evidence.
        """
        if len(values) <= 1:
            return 0.0
        pairs = tuple(zip(values, values[1:]))
        if direction == "high":
            persistent = sum(current >= previous for previous, current in pairs)
        else:
            persistent = sum(current <= previous for previous, current in pairs)
        return persistent / len(pairs)

    @staticmethod
    def _quantile(values: list[float], quantile: float) -> float:
        if len(values) == 1:
            return values[0]

        position = (len(values) - 1) * quantile
        lower = int(position)
        upper = min(lower + 1, len(values) - 1)
        fraction = position - lower
        return values[lower] + (values[upper] - values[lower]) * fraction


class DynamicReadinessEvaluator:
    """Evaluate readiness relative to the envelope's signal direction."""

    @staticmethod
    def _directional_persistence(values: list[float], direction: SignalDirection) -> float:
        """Fraction of adjacent transitions that do not reverse risk direction."""
        if len(values) <= 1:
            return 0.0
        pairs = tuple(zip(values, values[1:]))
        if direction == "high":
            persistent = sum(current >= previous for previous, current in pairs)
        else:
            persistent = sum(current <= previous for previous, current in pairs)
        return persistent / len(pairs)


    def evaluate(
        self,
        observations: Iterable[EvolutionObservation],
        *,
        envelope: DynamicEnvelope,
        current_value: float,
        min_observations: int = 3,
        persistence_floor: float = 0.5,
        direction: SignalDirection | None = None,
    ) -> EvolutionReadiness:
        if min_observations < 1:
            raise ValueError("min_observations must be >= 1")
        if not 0.0 <= persistence_floor <= 1.0:
            raise ValueError("persistence_floor must be between 0 and 1")
        if direction is not None and direction not in {"high", "low"}:
            raise ValueError("direction must be 'high' or 'low'")
        if direction is not None and direction != envelope.direction:
            raise ValueError("direction must match envelope.direction")

        effective_direction = envelope.direction if direction is None else direction
        items = tuple(observations)
        profile = TrajectoryAnalyzer().profile(items)
        value = float(current_value)
        if not isfinite(value):
            raise ValueError("current_value must be finite")

        if effective_direction == "high":
            state = (
                "CRITICAL"
                if value >= envelope.critical_limit
                else "WARNING"
                if value >= envelope.warning_limit
                else "NORMAL"
            )
            distance_to_critical = max(0.0, envelope.critical_limit - value)
        else:
            state = (
                "CRITICAL"
                if value <= envelope.critical_limit
                else "WARNING"
                if value <= envelope.warning_limit
                else "NORMAL"
            )
            distance_to_critical = max(0.0, value - envelope.critical_limit)

        approach = ThresholdApproach(
            value=value,
            state=state,
            distance_to_critical=distance_to_critical,
        )
        numeric_history = [
            float(item.context[envelope.metric_name])
            for item in sorted(items, key=lambda item: item.observed_at_utc)
            if isinstance(item.context.get(envelope.metric_name), (int, float))
            and not isinstance(item.context.get(envelope.metric_name), bool)
            and isfinite(float(item.context[envelope.metric_name]))
        ]
        signal_persistence = self._directional_persistence(numeric_history, effective_direction)
        ready = (
            profile.observation_count >= min_observations
            and state in {"WARNING", "CRITICAL"}
            and signal_persistence >= persistence_floor
        )

        if state == "NORMAL":
            reason = "current signal remains inside the field-derived envelope"
        elif profile.observation_count < min_observations:
            reason = "insufficient trajectory history for an evolution signal"
        elif signal_persistence < persistence_floor:
            reason = "numeric signal direction is not persistent enough in the observed history"
        else:
            reason = (
                "trajectory persistently approaches or occupies the "
                "field-derived limit"
            )

        return EvolutionReadiness(
            state=state,
            approach=approach,
            persistence=profile.persistence,
            signal_persistence=signal_persistence,
            observation_count=profile.observation_count,
            ready=ready,
            reason=reason,
        )
