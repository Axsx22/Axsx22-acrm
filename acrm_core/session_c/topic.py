"""Field-driven topic inference for Session C-B."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from acrm_core.evolution.session_c import EvolutionObservation, ObservationKind

@dataclass(frozen=True, slots=True)
class TopicSignal:
    topic: str
    support: float
    contributing_kinds: tuple[ObservationKind, ...]

@dataclass(frozen=True, slots=True)
class TopicProfile:
    dominant: TopicSignal | None
    signals: tuple[TopicSignal, ...]

class FieldDrivenTopicEngine:
    _TOPICS: dict[str, tuple[ObservationKind, ...]] = {
        "capacity_stability": (ObservationKind.PRESSURE, ObservationKind.FAILURE),
        "ambiguity_resolution": (ObservationKind.AMBIGUITY,),
        "capability_gap": (ObservationKind.MISSING_CAPABILITY,),
        "evolution_need": (ObservationKind.EVOLUTION_SIGNAL,),
    }
    def infer(self, observations: Iterable[EvolutionObservation]) -> TopicProfile:
        items=tuple(observations)
        if not items: return TopicProfile(None,())
        total=len(items); signals=[]
        for topic,kinds in self._TOPICS.items():
            count=sum(item.kind in kinds for item in items)
            if count: signals.append(TopicSignal(topic,count/total,kinds))
        signals.sort(key=lambda s:(-s.support,s.topic))
        return TopicProfile(signals[0] if signals else None,tuple(signals))
