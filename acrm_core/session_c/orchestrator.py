"""Live Session C observer/orchestrator over Runtime evaluation events.

The engine can be initialized from historical observations and then receive
additional records through record() or observe_runtime(). The in-memory log
is independent of Runtime state; durable storage and background transport are
separate deployment concerns.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from acrm_core.evolution.session_c import (
    EvolutionCandidate, EvolutionContext, EvolutionDecision,
    EvolutionObservation, EvolutionSessionC, EvolutionTolerance,
)
from acrm_core.runtime.field_runtime import RuntimeEvaluation
from acrm_core.session_c.dynamic import (
    DynamicEnvelope, DynamicReadinessEvaluator, EvolutionReadiness,
    FieldEnvelopeEstimator, SignalDirection,
)
from acrm_core.session_c.observation import ObservationLog
from acrm_core.session_c.topic import FieldDrivenTopicEngine, TopicProfile


@dataclass(frozen=True, slots=True)
class SessionCAnalysis:
    readiness: EvolutionReadiness
    topic: TopicProfile
    envelope: DynamicEnvelope


class SessionCEngine:
    """Independent observer and evolution coordinator; does not mutate Runtime."""

    def __init__(
        self, *, observations: Iterable[EvolutionObservation] = (),
        metric_name: str, current_value: float | None = None,
        min_observations: int = 3, persistence_floor: float = 0.5,
        warning_quantile: float = 0.90, critical_quantile: float = 0.975,
        direction: SignalDirection = "high",
        tolerance: EvolutionTolerance | None = None,
        generator, tester, vote_provider,
    ) -> None:
        self._observation_log = ObservationLog()
        for observation in observations:
            self._observation_log.record(observation)
        self.metric_name = metric_name
        self.current_value = current_value
        self.min_observations = min_observations
        self.persistence_floor = persistence_floor
        self.warning_quantile = warning_quantile
        self.critical_quantile = critical_quantile
        self.direction = direction
        self._governance = EvolutionSessionC(
            tolerance=tolerance, generator=generator, tester=tester,
            vote_provider=vote_provider,
        )
        self._forwarded_ids: set[str] = set()
        self._runtime_identity = None
        self._runtime_batches = {}
        self._last_sequence = None
        self._closed = False

    @property
    def observations(self) -> tuple[EvolutionObservation, ...]:
        return self._observation_log.snapshot()

    def record(self, observation: EvolutionObservation) -> None:
        if self._closed:
            raise RuntimeError("Session C session is closed")
        if self._runtime_identity is not None:
            if not observation.observation_id.startswith(f"{self._runtime_identity[1]}:"):
                raise ValueError("observation does not belong to this Session C identity")
        self._observation_log.record(observation)

    def observe_runtime(self, evaluation: RuntimeEvaluation) -> int:
        """Atomically ingest events for one bound (Runtime ID, Session ID)."""
        if self._closed:
            raise RuntimeError("Session C session is closed")
        if not isinstance(evaluation, RuntimeEvaluation):
            raise TypeError("evaluation must be a RuntimeEvaluation")
        runtime_id = evaluation.field_state.field_id
        session_id = evaluation.field_state.session_id
        sequence = evaluation.field_state.sequence
        if not runtime_id or not session_id or sequence < 0:
            raise ValueError("Runtime identity and non-negative sequence are required")
        identity = (runtime_id, session_id)
        if self._runtime_identity is None:
            self._runtime_identity = identity
        elif self._runtime_identity != identity:
            raise ValueError("RuntimeEvaluation belongs to a different Runtime/Session; use a separate SessionCEngine")
        if self.metric_name not in evaluation.field_state.metrics:
            raise ValueError(f"Runtime FieldState does not contain metric {self.metric_name!r}")
        metric_value = float(evaluation.field_state.metrics[self.metric_name])
        import math
        if not math.isfinite(metric_value):
            raise ValueError("Runtime metric value must be finite")
        batch_key = (runtime_id, session_id, sequence)
        fingerprint = (tuple(item.observation_id for item in evaluation.observations), metric_value)
        previous = self._runtime_batches.get(batch_key)
        if previous is not None:
            if previous != fingerprint:
                raise ValueError("conflicting replay for Runtime sequence")
            return 0
        if self._last_sequence is not None and sequence <= self._last_sequence:
            raise ValueError("out-of-order Runtime sequence")
        for item in evaluation.observations:
            if not item.observation_id.startswith(f"{session_id}:{sequence}:"):
                raise ValueError("Runtime observation identity does not match its batch")
        added = self._observation_log.record_many(evaluation.observations)
        self._runtime_batches[batch_key] = fingerprint
        self._last_sequence = sequence
        self.current_value = metric_value
        return added

    def close(self) -> None:
        """Close this in-memory observer; durable recovery is not provided."""
        self._closed = True

    def analyze(self) -> SessionCAnalysis:
        if self._closed:
            raise RuntimeError("Session C session is closed")
        if self.current_value is None:
            raise ValueError("current_value is required before Session C analysis")
        items = self.observations
        envelope = FieldEnvelopeEstimator().estimate(
            items, metric_name=self.metric_name,
            warning_quantile=self.warning_quantile,
            critical_quantile=self.critical_quantile, direction=self.direction,
        )
        readiness = DynamicReadinessEvaluator().evaluate(
            items, envelope=envelope, current_value=self.current_value,
            min_observations=self.min_observations,
            persistence_floor=self.persistence_floor, direction=self.direction,
        )
        topic = FieldDrivenTopicEngine().infer(items)
        return SessionCAnalysis(readiness, topic, envelope)

    def evolve(self) -> EvolutionDecision:
        analysis = self.analyze()
        if not analysis.readiness.ready:
            return EvolutionDecision(
                "WAIT_DYNAMIC_TOLERANCE", None, None, 0,
                analysis.readiness.reason,
            )
        for observation in self.observations:
            if observation.observation_id not in self._forwarded_ids:
                self._governance.record(observation)
                self._forwarded_ids.add(observation.observation_id)
        candidate = self._governance.generate_candidate()
        if candidate is None:
            return EvolutionDecision(
                "WAIT_GENERATION", None, None, 0,
                "candidate generation tolerance has not been reached",
            )
        topic = analysis.topic.dominant.topic if analysis.topic.dominant else "undetermined"
        return self._governance.review(EvolutionContext(
            topic=topic,
            state={
                "readiness": analysis.readiness.state,
                "signal_persistence": analysis.readiness.signal_persistence,
                "metric": analysis.envelope.metric_name,
                "warning_limit": analysis.envelope.warning_limit,
                "critical_limit": analysis.envelope.critical_limit,
                "signal_direction": self.direction,
            },
        ))

    @property
    def candidate(self) -> EvolutionCandidate | None:
        return self._governance.candidate
