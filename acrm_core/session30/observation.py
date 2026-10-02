"""Observation-only intake for Session 30.

This layer records pressure, ambiguity, missing capability, change, and
emergent behavior without assigning severity, scores, causes, or decisions.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from typing import Iterable


class ObservationKind(str, Enum):
    """Kinds of runtime observations that may be recorded without judgment."""

    PRESSURE = "pressure"
    AMBIGUITY = "ambiguity"
    MISSING_CAPABILITY = "missing_capability"
    UPDATE_NEEDED = "update_needed"
    EMERGENT_CHANGE = "emergent_change"
    FAILURE = "failure"


@dataclass(frozen=True, slots=True)
class Observation:
    """A factual observation; it carries no severity or decision score."""

    observation_id: str
    kind: ObservationKind
    observed_at: datetime
    description: str
    context: str = ""
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.observation_id.strip():
            raise ValueError("observation_id must be non-empty")
        if not isinstance(self.kind, ObservationKind):
            raise TypeError("kind must be an ObservationKind")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if not self.description.strip():
            raise ValueError("description must be non-empty")
        if any(not ref.strip() for ref in self.evidence_refs):
            raise ValueError("evidence_refs must contain non-empty strings")
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs must not contain duplicates")

    @property
    def observed_at_utc(self) -> datetime:
        return self.observed_at.astimezone(timezone.utc)


class ObservationLedger:
    """Thread-safe append-only store for raw Session 30 observations."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._items: list[Observation] = []

    def record(self, observation: Observation) -> None:
        with self._lock:
            if any(item.observation_id == observation.observation_id for item in self._items):
                raise ValueError("observation_id must be unique")
            self._items.append(observation)

    def snapshot(self) -> tuple[Observation, ...]:
        with self._lock:
            return tuple(self._items)

    def since(self, observed_at: datetime) -> tuple[Observation, ...]:
        if observed_at.tzinfo is None or observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        cutoff = observed_at.astimezone(timezone.utc)
        with self._lock:
            return tuple(item for item in self._items if item.observed_at_utc >= cutoff)

    def count(self, kinds: Iterable[ObservationKind] | None = None) -> int:
        with self._lock:
            if kinds is None:
                return len(self._items)
            allowed = set(kinds)
            return sum(item.kind in allowed for item in self._items)
