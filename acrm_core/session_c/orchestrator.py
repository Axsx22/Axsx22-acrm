"""Session C-B orchestration over the neutral C-A observation stream."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from acrm_core.evolution.session_c import EvolutionCandidate, EvolutionDecision, EvolutionObservation, EvolutionSessionC, EvolutionTolerance, EvolutionContext
from acrm_core.session_c.dynamic import DynamicEnvelope, DynamicReadinessEvaluator, EvolutionReadiness, FieldEnvelopeEstimator
from acrm_core.session_c.topic import FieldDrivenTopicEngine, TopicProfile

@dataclass(frozen=True, slots=True)
class SessionCAnalysis:
    readiness: EvolutionReadiness
    topic: TopicProfile
    envelope: DynamicEnvelope

class SessionCEngine:
    """Coordinate C-A evidence with governed C-B evolution; never mutates runtime."""
    def __init__(self, *, observations: Iterable[EvolutionObservation], metric_name: str, current_value: float, min_observations: int = 3, persistence_floor: float = 0.5, warning_quantile: float = 0.90, critical_quantile: float = 0.975, tolerance: EvolutionTolerance | None = None, generator, tester, vote_provider) -> None:
        self.observations=tuple(observations); self.metric_name=metric_name; self.current_value=current_value
        self.min_observations=min_observations; self.persistence_floor=persistence_floor
        self.warning_quantile=warning_quantile; self.critical_quantile=critical_quantile
        self._governance=EvolutionSessionC(tolerance=tolerance,generator=generator,tester=tester,vote_provider=vote_provider)
    def analyze(self) -> SessionCAnalysis:
        envelope=FieldEnvelopeEstimator().estimate(self.observations,metric_name=self.metric_name,warning_quantile=self.warning_quantile,critical_quantile=self.critical_quantile)
        readiness=DynamicReadinessEvaluator().evaluate(self.observations,envelope=envelope,current_value=self.current_value,min_observations=self.min_observations,persistence_floor=self.persistence_floor)
        topic=FieldDrivenTopicEngine().infer(self.observations)
        return SessionCAnalysis(readiness,topic,envelope)
    def evolve(self) -> EvolutionDecision:
        analysis=self.analyze()
        if not analysis.readiness.ready: return EvolutionDecision("WAIT_DYNAMIC_TOLERANCE",None,None,0,analysis.readiness.reason)
        for observation in self.observations: self._governance.record(observation)
        candidate=self._governance.generate_candidate()
        if candidate is None: return EvolutionDecision("WAIT_GENERATION",None,None,0,"candidate generation tolerance has not been reached")
        topic=analysis.topic.dominant.topic if analysis.topic.dominant else "undetermined"
        return self._governance.review(EvolutionContext(topic=topic,state={"readiness":analysis.readiness.state,"metric":analysis.envelope.metric_name,"warning_limit":analysis.envelope.warning_limit,"critical_limit":analysis.envelope.critical_limit}))
    @property
    def candidate(self) -> EvolutionCandidate | None: return self._governance.candidate
