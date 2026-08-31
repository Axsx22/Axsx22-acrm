"""Observation-only recording primitives for ACRM Session C.

Session C observes the running ACRM system and records signals that indicate
pressure, ambiguity, capability gaps, or possible opportunities for evolution.
It deliberately does not score, judge, modify, or execute the runtime.
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
class Observation:
    """Immutable factual observation; no severity, score, or decision."""

    kind: ObservationKind
    description: str
    observed_at: datetime
    context: Mapping[str, object] = field(default_factory=dict)
    source: str = "session_c"

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ObservationKind):
            raise TypeError("kind must be an ObservationKind")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string")
        if not isinstance(self.observed_at, datetime):
            raise TypeError("observed_at must be a datetime")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if not isinstance(self.context, Mapping):
            raise TypeError("context must be a mapping")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")
        object.__setattr__(self, "context", MappingProxyType(dict(self.context)))

    @property
    def observed_at_utc(self) -> datetime:
        return self.observed_at.astimezone(timezone.utc)


class ObservationLog:
    """Append-only in-memory observation store.

    Recording is the only responsibility. Evaluation and promotion belong to
    later Session C stages and are intentionally absent here.
    """

    def __init__(self) -> None:
        self._items: list[Observation] = []

    def record(self, observation: Observation) -> None:
        if not isinstance(observation, Observation):
            raise TypeError("observation must be an Observation")
        self._items.append(observation)

    def snapshot(self) -> tuple[Observation, ...]:
        return tuple(self._items)
