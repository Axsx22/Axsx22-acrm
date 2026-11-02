"""Canonical neutral observation boundary for ACRM Session C C-A."""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class ObservationKind(str, Enum):
    PRESSURE = "pressure"
    AMBIGUITY = "ambiguity"
    MISSING_CAPABILITY = "missing_capability"
    EVOLUTION_SIGNAL = "evolution_signal"
    FAILURE = "failure"


def _freeze(value: object) -> object:
    """Recursively freeze supported container values at the observation boundary.

    Context is intentionally restricted to ordinary immutable scalars and
    built-in containers. Rejecting opaque mutable objects is safer than
    presenting a shallow read-only wrapper as an immutable evidence record.
    """
    if isinstance(value, Mapping):
        frozen = {}
        for key, item in value.items():
            if not isinstance(key, (str, int, float, bool, Enum)):
                raise TypeError("context mapping keys must be immutable scalar values")
            frozen[key] = _freeze(item)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze(item) for item in value)
    if value is None or isinstance(value, (str, int, float, bool, bytes, date, datetime, Decimal, Enum)):
        return value
    raise TypeError(
        f"unsupported mutable or opaque context value: {type(value).__name__}"
    )


@dataclass(frozen=True, slots=True)
class EvolutionObservation:
    """Immutable factual observation; no severity, score, judgment, or topic."""

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
        object.__setattr__(self, "context", _freeze(self.context))

    @property
    def observed_at_utc(self) -> datetime:
        return self.observed_at


# Backward-compatible name for the earlier draft API.
Observation = EvolutionObservation


class ObservationLog:
    """Append-only neutral observation store with unique observation IDs."""

    def __init__(self) -> None:
        self._items: list[EvolutionObservation] = []
        self._ids: set[str] = set()

    def record(self, observation: EvolutionObservation) -> bool:
        return self.record_many((observation,)) == 1

    def record_many(self, observations) -> int:
        """Atomically append a batch; exact replays are idempotent."""
        batch = tuple(observations)
        seen = {}
        for item in batch:
            if not isinstance(item, EvolutionObservation):
                raise TypeError("all observations must be EvolutionObservation instances")
            prior = seen.get(item.observation_id)
            if prior is not None and prior != item:
                raise ValueError(f"conflicting observation_id in batch: {item.observation_id}")
            seen[item.observation_id] = item

        pending = []
        for observation_id, item in seen.items():
            if observation_id in self._ids:
                existing = next(x for x in self._items if x.observation_id == observation_id)
                if existing != item:
                    raise ValueError(f"conflicting observation_id: {observation_id}")
            else:
                pending.append(item)

        self._items.extend(pending)
        self._ids.update(item.observation_id for item in pending)
        return len(pending)

    def snapshot(self) -> tuple[EvolutionObservation, ...]:
        return tuple(self._items)
