"""Observation-only recording primitives for ACRM Session C.

This module is the canonical C-A observation boundary. It records factual
runtime signals and deliberately performs no scoring, judgment, inference,
or promotion decision.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class ObservationKind(str, Enum):
    PRESSURE = "pressure"
    AMBIGUITY = "ambiguity"
    MISSING_CAPABILITY = "missing_capability"
    EVOLUTION_SIGNAL = "evolution_signal"
    FAILURE = "failure"


@dataclass(frozen=True, slots=True)
class EvolutionObservation:
    """Immutable factual observation; no severity, score, or decision."""

    observation_id: str
    kind: ObservationKind | str
    description: str
    observed_at: datetime
    context: Mapping[str, object] = field(default_factory=dict)
    source: str = "session_c"

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, str) or not self.observation_id.strip():
            raise ValueError("observation_id must be non-empty")
        if isinstance(self.kind, str):
            try:
                object.__setattr__(self, "kind", ObservationKind(self.kind))
            except ValueError as exc:
                raise ValueError("kind must be a supported ObservationKind") from exc
        elif not isinstance(self.kind, ObservationKind):
            raise TypeError("kind must be an ObservationKind or supported string")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be non-empty")
        if not isinstance(self.observed_at, datetime):
            raise TypeError("observed_at must be a datetime")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if not isinstance(self.context, Mapping):
            raise TypeError("context must be a mapping")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be non-empty")
        object.__setattr__(self, "observed_at", self.observed_at.astimezone(timezone.utc))
        object.__setattr__(self, "context", MappingProxyType(dict(self.context)))

    @property
    def observed_at_utc(self) -> datetime:
        return self.observed_at


# Backward-compatible short name for callers that used the earlier draft.
Observation = EvolutionObservation


class ObservationLog:
    """Append-only neutral observation store with unique observation IDs."""

    def __init__(self) -> None:
        self._items: list[EvolutionObservation] = []
        self._ids: set[str] = set()

    def record(self, observation: EvolutionObservation) -> None:
        if not isinstance(observation, EvolutionObservation):
            raise TypeError("observation must be an EvolutionObservation")
        if observation.observation_id in self._ids:
            raise ValueError(f"duplicate observation_id: {observation.observation_id}")
        self._items.append(observation)
        self._ids.add(observation.observation_id)

    def snapshot(self) -> tuple[EvolutionObservation, ...]:
        return tuple(self._items)
