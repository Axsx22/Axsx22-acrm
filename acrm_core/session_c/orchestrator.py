"""Live Session C observer/orchestrator over Runtime evaluation events.

The engine can be initialized from historical observations and then receive
additional records through record() or observe_runtime(). The in-memory log
is independent of Runtime state; durable storage and background transport are
separate deployment concerns.
"""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
import hashlib
import json
import math
from typing import Iterable
from types import MappingProxyType
from uuid import uuid4

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
    if isinstance(value, date):
        return {"$date": value.isoformat()}
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("canonical payload cannot contain non-finite Decimals")
        return {"$decimal": format(value.normalize(), "f")}
    if isinstance(value, bytes):
        return {"$bytes_hex": value.hex()}
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
    """Immutable gap identity/range with an immutable per-sequence state projection."""

    start_sequence: int
    end_sequence: int
    previous_sequence: int
    next_sequence: int
    detected_at: datetime
    gap_id: str
    sequence_states: object

    def __post_init__(self) -> None:
        if self.start_sequence < 0 or self.end_sequence < self.start_sequence:
            raise ValueError("invalid sequence gap range")
        expected = set(range(self.start_sequence, self.end_sequence + 1))
        states = dict(self.sequence_states)
        if set(states) != expected:
            raise ValueError("sequence_states must cover the immutable original gap range")
        if any(value not in {"OPEN", "COMPENSATED", "UNRECOVERABLE"} for value in states.values()):
            raise ValueError("invalid sequence gap member state")
        object.__setattr__(self, "sequence_states", MappingProxyType(states))

    @property
    def status(self) -> str:
        states = tuple(self.sequence_states.values())
        if all(state == "COMPENSATED" for state in states):
            return "COMPENSATED"
        if all(state != "OPEN" for state in states) and "UNRECOVERABLE" in states:
            return "UNRECOVERABLE"
        return "OPEN"


@dataclass(frozen=True, slots=True)
class GapAuditEvent:
    event_id: str
    gap_id: str
    sequence: int
    event_type: str
    previous_status: str
    new_status: str
    occurred_at: datetime
    reason: str | None = None
    source: str | None = None
    decision_id: str | None = None


@dataclass(frozen=True, slots=True)
class LateRecoveryRecord:
    recovery_id: str
    gap_id: str
    runtime_id: str
    session_id: str
    sequence: int
    event_hash: str
    event_timestamp: datetime
    received_at: datetime
    source: str
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class HistoricalCompleteness:
    as_of: datetime
    scope_start: int | None
    scope_end: int | None
    expected_sequences: int
    available_sequences: int
    complete: bool
    ratio: float


@dataclass(frozen=True, slots=True)
class CurrentlyAvailableEvidence:
    count: int
    sequences: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class SessionCAnalysis:
    readiness: EvolutionReadiness
    topic: TopicProfile
    envelope: DynamicEnvelope
    sequence_gaps: tuple[SequenceGap, ...] = ()
    history_complete: bool = True
    historical_completeness: HistoricalCompleteness | None = None
    currently_available_evidence: CurrentlyAvailableEvidence = CurrentlyAvailableEvidence(0, ())


class SessionCEngine:
    """Independent observer; gap recovery is explicit and in-memory/atomic."""

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
        initialized_at = datetime.now(timezone.utc)
        self._observation_received_at: dict[str, datetime] = {}
        for observation in observations:
            if self._observation_log.record(observation):
                self._observation_received_at[observation.observation_id] = initialized_at
        self.metric_name = metric_name
        self._current_value_history: list[tuple[float, datetime]] = []
        self._current_value = current_value
        if current_value is not None:
            self._current_value_history.append((float(current_value), initialized_at))
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
        self._accepted_sequences: dict[int, tuple[str, datetime]] = {}
        self._last_sequence = None
        self._sequence_gaps: list[SequenceGap] = []
        self._gap_audit_events: tuple[GapAuditEvent, ...] = ()
        self._compensation_records: dict[tuple[str, int], tuple[str, datetime, str]] = {}
        self._late_recovery_records: tuple[LateRecoveryRecord, ...] = ()
        self._late_recovery_index: dict[tuple[str, int], LateRecoveryRecord] = {}
        self._closed = False

    @property
    def current_value(self) -> float | None:
        return self._current_value

    @current_value.setter
    def current_value(self, value: float | None) -> None:
        received_at = datetime.now(timezone.utc)
        self._current_value = value
        if value is not None:
            self._current_value_history.append((float(value), received_at))

    @property
    def observations(self) -> tuple[EvolutionObservation, ...]:
        return self._observation_log.snapshot()

    @property
    def sequence_gaps(self) -> tuple[SequenceGap, ...]:
        return tuple(self._sequence_gaps)

    @property
    def gap_audit_events(self) -> tuple[GapAuditEvent, ...]:
        return self._gap_audit_events

    @property
    def late_recovery_records(self) -> tuple[LateRecoveryRecord, ...]:
        return self._late_recovery_records

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("Session C session is closed")

    def record(self, observation: EvolutionObservation) -> None:
        self._ensure_open()
        if self._runtime_identity is not None:
            if not observation.observation_id.startswith(f"{self._runtime_identity[1]}:"):
                raise ValueError("observation does not belong to this Session C identity")
        received_at = datetime.now(timezone.utc)
        added = self._observation_log.record(observation)
        if added:
            self._observation_received_at[observation.observation_id] = received_at

    def _validate_evaluation(self, evaluation: RuntimeEvaluation):
        if not isinstance(evaluation, RuntimeEvaluation):
            raise TypeError("evaluation must be a RuntimeEvaluation")
        runtime_id = evaluation.runtime_id
        session_id = evaluation.field_state.session_id
        sequence = evaluation.field_state.sequence
        field_id = evaluation.field_state.field_id
        if not isinstance(runtime_id, str) or not runtime_id.strip():
            raise ValueError("RuntimeEvaluation must carry an explicit runtime_id")
        if not isinstance(session_id, str) or not session_id.strip() or sequence < 0:
            raise ValueError("Runtime identity and non-negative sequence are required")
        if not isinstance(field_id, str) or not field_id.strip():
            raise ValueError("RuntimeEvaluation must carry an explicit field_id")
        identity = (runtime_id, session_id, field_id)
        if self._runtime_identity is not None and self._runtime_identity != identity:
            raise ValueError("RuntimeEvaluation belongs to a different Runtime/Session/Field; use a separate SessionCEngine")
        if self.metric_name not in evaluation.field_state.metrics:
            raise ValueError(f"Runtime FieldState does not contain metric {self.metric_name!r}")
        metric_value = float(evaluation.field_state.metrics[self.metric_name])
        if not math.isfinite(metric_value):
            raise ValueError("Runtime metric value must be finite")
        for item in evaluation.observations:
            if not item.observation_id.startswith(f"{session_id}:{sequence}:"):
                raise ValueError("Runtime observation identity does not match its batch")
        return identity, sequence, metric_value, runtime_evaluation_digest(evaluation)

    def observe_runtime(self, evaluation: RuntimeEvaluation) -> int:
        """Accept only new monotonic sequences; gaps are recorded, late events rejected."""
        self._ensure_open()
        identity, sequence, metric_value, fingerprint = self._validate_evaluation(evaluation)
        runtime_id, session_id, _ = identity
        batch_key = (runtime_id, session_id, sequence)
        previous = self._runtime_batches.get(batch_key)
        if previous is not None:
            if previous != fingerprint:
                raise ValueError("conflicting replay for Runtime sequence")
            return 0
        if self._last_sequence is not None and sequence <= self._last_sequence:
            raise ValueError("out-of-order or late Runtime sequence; use an explicit recovery API")
        now = datetime.now(timezone.utc)
        staged_gaps = list(self._sequence_gaps)
        if self._last_sequence is not None and sequence > self._last_sequence + 1:
            start, end = self._last_sequence + 1, sequence - 1
            states = {number: "OPEN" for number in range(start, end + 1)}
            staged_gaps.append(SequenceGap(
                start, end, self._last_sequence, sequence, now, str(uuid4()), states,
            ))
        # All validation and derived objects are prepared before the log mutation.
        known_observation_ids = {
            item.observation_id for item in self._observation_log.snapshot()
        }
        staged_observation_receipts = dict(self._observation_received_at)
        for item in evaluation.observations:
            if item.observation_id not in known_observation_ids:
                staged_observation_receipts[item.observation_id] = now
        added = self._observation_log.record_many(evaluation.observations)
        self._observation_received_at = staged_observation_receipts
        self._runtime_identity = identity
        self._runtime_batches[batch_key] = fingerprint
        self._sequence_gaps = staged_gaps
        self._accepted_sequences[sequence] = (fingerprint, now)
        if self._last_sequence is None or sequence > self._last_sequence:
            self._last_sequence = sequence
            self._current_value = metric_value
            self._current_value_history.append((metric_value, now))
        return added

    def _find_gap(self, sequence: int) -> SequenceGap:
        matches = [
            gap for gap in self._sequence_gaps
            if gap.start_sequence <= sequence <= gap.end_sequence
        ]
        if len(matches) != 1:
            raise ValueError("sequence does not belong to exactly one recorded gap")
        return matches[0]

    def _replace_gap_member_state(self, gap: SequenceGap, sequence: int, state: str) -> SequenceGap:
        states = dict(gap.sequence_states)
        states[sequence] = state
        return SequenceGap(
            gap.start_sequence, gap.end_sequence, gap.previous_sequence,
            gap.next_sequence, gap.detected_at, gap.gap_id, states,
        )

    def compensate_gap(self, evaluation: RuntimeEvaluation, *, source: str) -> bool:
        """Explicitly compensate one OPEN member without rewriting event chronology."""
        self._ensure_open()
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source must be non-empty")
        identity, sequence, _, fingerprint = self._validate_evaluation(evaluation)
        gap = self._find_gap(sequence)
        if gap.sequence_states[sequence] != "OPEN":
            existing = self._compensation_records.get((gap.gap_id, sequence))
            if existing and existing[0] == fingerprint:
                return False
            raise ValueError("sequence is not OPEN for compensation or conflicts with prior recovery")
        key = (gap.gap_id, sequence)
        existing = self._compensation_records.get(key)
        if existing:
            if existing[0] == fingerprint:
                return False
            raise ValueError("conflicting compensation replay")
        now = datetime.now(timezone.utc)
        updated = self._replace_gap_member_state(gap, sequence, "COMPENSATED")
        audit = GapAuditEvent(
            str(uuid4()), gap.gap_id, sequence, "COMPENSATED", "OPEN",
            "COMPENSATED", now, source=source,
        )
        # One logical in-process commit: all allocations/validation precede assignments.
        staged_gaps = list(self._sequence_gaps)
        staged_gaps[self._sequence_gaps.index(gap)] = updated
        staged_audit = (*self._gap_audit_events, audit)
        staged_records = dict(self._compensation_records)
        staged_records[key] = (fingerprint, now, source)
        self._sequence_gaps, self._gap_audit_events, self._compensation_records = (
            staged_gaps, staged_audit, staged_records,
        )
        return True

    def mark_gap_unrecoverable(
        self, start_sequence: int, end_sequence: int, *,
        reason: str, source: str, decision_id: str,
    ) -> None:
        """Record an explicit decision for every still-OPEN member in an exact gap."""
        self._ensure_open()
        if not all(isinstance(value, str) and value.strip() for value in (reason, source, decision_id)):
            raise ValueError("reason, source, and decision_id are required")
        matches = [
            gap for gap in self._sequence_gaps
            if gap.start_sequence == start_sequence and gap.end_sequence == end_sequence
        ]
        if len(matches) != 1:
            raise ValueError("an exact recorded gap range is required")
        gap = matches[0]
        if any(event.decision_id == decision_id for event in self._gap_audit_events):
            raise ValueError("decision_id has already been used")
        open_sequences = [n for n, state in gap.sequence_states.items() if state == "OPEN"]
        if not open_sequences:
            raise ValueError("gap has no OPEN members to decide")
        now = datetime.now(timezone.utc)
        updated = gap
        staged_events = list(self._gap_audit_events)
        for sequence in open_sequences:
            updated = self._replace_gap_member_state(updated, sequence, "UNRECOVERABLE")
            staged_events.append(GapAuditEvent(
                str(uuid4()), gap.gap_id, sequence, "UNRECOVERABLE", "OPEN",
                "UNRECOVERABLE", now, reason, source, decision_id,
            ))
        staged_gaps = list(self._sequence_gaps)
        staged_gaps[self._sequence_gaps.index(gap)] = updated
        self._sequence_gaps, self._gap_audit_events = staged_gaps, tuple(staged_events)

    def record_late_recovery(self, evaluation: RuntimeEvaluation, *, source: str) -> LateRecoveryRecord:
        """Record post-UNRECOVERABLE evidence without changing historical status."""
        self._ensure_open()
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source must be non-empty")
        identity, sequence, _, fingerprint = self._validate_evaluation(evaluation)
        gap = self._find_gap(sequence)
        if gap.sequence_states[sequence] != "UNRECOVERABLE":
            raise ValueError("late recovery is only valid for UNRECOVERABLE members")
        key = (gap.gap_id, sequence)
        existing = self._late_recovery_index.get(key)
        if existing:
            if existing.event_hash == fingerprint:
                return existing
            raise ValueError("conflicting late recovery replay")
        now = datetime.now(timezone.utc)
        record = LateRecoveryRecord(
            str(uuid4()), gap.gap_id, identity[0], identity[1], sequence,
            fingerprint, evaluation.field_state.timestamp, now, source, now,
        )
        staged_records = (*self._late_recovery_records, record)
        staged_index = dict(self._late_recovery_index)
        staged_index[key] = record
        self._late_recovery_records, self._late_recovery_index = staged_records, staged_index
        return record

    def analyze(self, *, as_of: datetime | None = None) -> SessionCAnalysis:
        self._ensure_open()
        if self.current_value is None:
            raise ValueError("current_value is required before Session C analysis")
        evaluated_at = as_of or datetime.now(timezone.utc)
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
            raise ValueError("analysis as_of must be timezone-aware")
        evaluated_at = evaluated_at.astimezone(timezone.utc)
        # Every observation-derived output is computed from records received
        # by the observer no later than evaluated_at. Event timestamps are
        # retained as evidence, but do not establish when Session C knew them.
        items = tuple(
            item for item in self.observations
            if item.observation_id in self._observation_received_at
            and self._observation_received_at[item.observation_id] <= evaluated_at
        )
        known_values = [
            (value, received_at)
            for value, received_at in self._current_value_history
            if received_at <= evaluated_at
        ]
        if not known_values:
            raise ValueError("current_value is not available as of requested analysis time")
        historical_current_value = known_values[-1][0]
        envelope = FieldEnvelopeEstimator().estimate(
            items, metric_name=self.metric_name,
            warning_quantile=self.warning_quantile,
            critical_quantile=self.critical_quantile, direction=self.direction,
        )
        readiness = DynamicReadinessEvaluator().evaluate(
            items, envelope=envelope, current_value=historical_current_value,
            min_observations=self.min_observations,
            persistence_floor=self.persistence_floor, direction=self.direction,
        )
        topic = FieldDrivenTopicEngine().infer(items)
        # Freeze the analysis denominator to sequences known by this as_of time.
        # _accepted_sequences stores observer receipt time, not the event's claimed
        # production timestamp, so future arrivals cannot expand a past scope.
        scoped_sequences = sorted(
            number
            for number, (_, received_at) in self._accepted_sequences.items()
            if received_at <= evaluated_at
        )
        scope_start = scoped_sequences[0] if scoped_sequences else None
        scope_end = scoped_sequences[-1] if scoped_sequences else None
        expected = (scope_end - scope_start + 1) if scope_start is not None else 0

        # Reconstruct each visible Gap from its original OPEN members plus only
        # audit transitions that had occurred by the requested analysis time.
        historical_gaps = []
        for gap in self._sequence_gaps:
            if gap.detected_at > evaluated_at:
                continue
            states = {number: "OPEN" for number in range(gap.start_sequence, gap.end_sequence + 1)}
            for event in self._gap_audit_events:
                if event.gap_id == gap.gap_id and event.occurred_at <= evaluated_at:
                    states[event.sequence] = event.new_status
            historical_gaps.append(SequenceGap(
                gap.start_sequence, gap.end_sequence, gap.previous_sequence,
                gap.next_sequence, gap.detected_at, gap.gap_id, states,
            ))
        gaps = tuple(historical_gaps)

        available = {
            number for number, (_, received_at) in self._accepted_sequences.items()
            if received_at <= evaluated_at
        }
        available.update(
            sequence for (gap_id, sequence), (_, recorded_at, _) in self._compensation_records.items()
            if recorded_at <= evaluated_at
        )
        available.update(
            record.sequence for record in self._late_recovery_records
            if record.recorded_at <= evaluated_at
        )
        scoped_available = tuple(sorted(n for n in available if scope_start is not None and scope_start <= n <= scope_end))
        count = len(scoped_available)
        ratio = (count / expected) if expected else 1.0
        historical = HistoricalCompleteness(
            evaluated_at, scope_start, scope_end, expected, count,
            count == expected, ratio,
        )
        current_missing_evidence = tuple(sorted({
            sequence for (gap_id, sequence), (_, recorded_at, _) in self._compensation_records.items()
            if recorded_at <= evaluated_at
        } | {
            record.sequence for record in self._late_recovery_records
            if record.recorded_at <= evaluated_at
        }))
        current_evidence = CurrentlyAvailableEvidence(
            len(current_missing_evidence), current_missing_evidence,
        )
        return SessionCAnalysis(
            readiness, topic, envelope, gaps, historical.complete,
            historical, current_evidence,
        )

    def close(self) -> None:
        """Close this in-memory observer; durable recovery is not provided."""
        self._closed = True

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
