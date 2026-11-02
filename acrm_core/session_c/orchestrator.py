"""Live Session C observer/orchestrator over Runtime evaluation events.

The engine can be initialized from historical observations and then receive
additional records through record() or observe_runtime(). The in-memory log
is independent of Runtime state; durable storage and background transport are
separate deployment concerns.
"""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import math
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


CANONICALIZATION_VERSION = 1


def _canonical_value(value):
    if is_dataclass(value):
        return {item.name: _canonical_value(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("canonical timestamps must be timezone-aware")
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, dict) or hasattr(value, "items"):
        return {str(key): _canonical_value(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical_value(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("canonical payload cannot contain non-finite floats")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported canonical payload value: {type(value).__name__}")


def runtime_evaluation_digest(evaluation: RuntimeEvaluation) -> str:
    payload = {"canonicalization_version": CANONICALIZATION_VERSION, "evaluation": _canonical_value(evaluation)}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class SequenceGap:
    start_sequence: int
    end_sequence: int
    previous_sequence: int
    next_sequence: int
    detected_at: datetime
    status: str = "open"
    resolved_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class SessionCAnalysis:
    readiness: EvolutionReadiness
    topic: TopicProfile
    envelope: DynamicEnvelope
    sequence_gaps: tuple[SequenceGap, ...] = ()
    history_complete: bool = True


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
        self._sequence_gaps: list[SequenceGap] = []
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
        runtime_id = evaluation.runtime_id
        if not isinstance(runtime_id, str) or not runtime_id.strip():
            raise ValueError("RuntimeEvaluation must carry an explicit runtime_id")
        session_id = evaluation.field_state.session_id
        sequence = evaluation.field_state.sequence
        if not runtime_id or not session_id or sequence < 0:
            raise ValueError("Runtime identity and non-negative sequence are required")
        field_id = evaluation.field_state.field_id
        if not isinstance(field_id, str) or not field_id.strip():
            raise ValueError("RuntimeEvaluation must carry an explicit field_id")
        identity = (runtime_id, session_id, field_id)
        if self._runtime_identity is not None and self._runtime_identity != identity:
            raise ValueError("RuntimeEvaluation belongs to a different Runtime/Session/Field; use a separate SessionCEngine")
        if self.metric_name not in evaluation.field_state.metrics:
            raise ValueError(f"Runtime FieldState does not contain metric {self.metric_name!r}")
        metric_value = float(evaluation.field_state.metrics[self.metric_name])
        import math
        if not math.isfinite(metric_value):
            raise ValueError("Runtime metric value must be finite")
        batch_key = (runtime_id, session_id, sequence)
        fingerprint = runtime_evaluation_digest(evaluation)
        previous = self._runtime_batches.get(batch_key)
        if previous is not None:
            if previous != fingerprint:
                raise ValueError("conflicting replay for Runtime sequence")
            return 0
        late_gap_index = None
        if self._last_sequence is not None and sequence <= self._last_sequence:
            late_gap_index = next((i for i, gap in enumerate(self._sequence_gaps) if gap.status == "open" and gap.start_sequence <= sequence <= gap.end_sequence), None)
            if late_gap_index is None:
                raise ValueError("out-of-order Runtime sequence")
        for item in evaluation.observations:
            if not item.observation_id.startswith(f"{session_id}:{sequence}:"):
                raise ValueError("Runtime observation identity does not match its batch")
        # Validate and stage every state change before the in-memory commit point.
        staged_gaps = list(self._sequence_gaps)
        now = datetime.now(timezone.utc)
        if late_gap_index is not None:
            gap = staged_gaps[late_gap_index]
            if gap.start_sequence == gap.end_sequence:
                staged_gaps[late_gap_index] = SequenceGap(gap.start_sequence, gap.end_sequence, gap.previous_sequence, gap.next_sequence, gap.detected_at, "compensated", now)
            elif sequence == gap.start_sequence:
                staged_gaps[late_gap_index] = SequenceGap(gap.start_sequence + 1, gap.end_sequence, gap.previous_sequence, gap.next_sequence, gap.detected_at, "open", None)
            elif sequence == gap.end_sequence:
                staged_gaps[late_gap_index] = SequenceGap(gap.start_sequence, gap.end_sequence - 1, gap.previous_sequence, gap.next_sequence, gap.detected_at, "open", None)
            else:
                staged_gaps[late_gap_index:late_gap_index + 1] = [
                    SequenceGap(gap.start_sequence, sequence - 1, gap.previous_sequence, gap.next_sequence, gap.detected_at),
                    SequenceGap(sequence + 1, gap.end_sequence, gap.previous_sequence, gap.next_sequence, gap.detected_at),
                ]
        elif self._last_sequence is not None and sequence > self._last_sequence + 1:
            staged_gaps.append(SequenceGap(self._last_sequence + 1, sequence - 1, self._last_sequence, sequence, now))
        # record_many validates the complete batch before mutating its log.
        added = self._observation_log.record_many(evaluation.observations)
        self._runtime_identity = identity
        self._runtime_batches[batch_key] = fingerprint
        self._sequence_gaps = staged_gaps
        if self._last_sequence is None or sequence > self._last_sequence:
            self._last_sequence = sequence
            self.current_value = metric_value
        return added

    @property
    def sequence_gaps(self) -> tuple[SequenceGap, ...]:
        return tuple(self._sequence_gaps)

    def close(self) -> None:
        """Close this in-memory observer; durable recovery is not provided."""
        self._closed = True

    def mark_gap_unrecoverable(self, start_sequence: int, end_sequence: int) -> None:
        """Explicitly close an open gap as unrecoverable without rewriting history."""
        if self._closed:
            raise RuntimeError("Session C session is closed")
        if start_sequence < 0 or end_sequence < start_sequence:
            raise ValueError("invalid gap sequence range")
        matches = [i for i, gap in enumerate(self._sequence_gaps) if gap.status == "open" and gap.start_sequence == start_sequence and gap.end_sequence == end_sequence]
        if len(matches) != 1:
            raise ValueError("an exact open gap range is required")
        index = matches[0]
        gap = self._sequence_gaps[index]
        self._sequence_gaps[index] = SequenceGap(gap.start_sequence, gap.end_sequence, gap.previous_sequence, gap.next_sequence, gap.detected_at, "unrecoverable", datetime.now(timezone.utc))

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
        gaps = tuple(self._sequence_gaps)
        return SessionCAnalysis(readiness, topic, envelope, gaps, not any(gap.status in {"open", "unrecoverable"} for gap in gaps))

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
