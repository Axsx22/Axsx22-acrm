"""Behavioral contract tests for Session C sequence-gap handling.

These tests intentionally exercise the public SessionCEngine API and observable
analysis output. They do not inspect private storage or implementation classes.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from acrm_core.runtime.field_runtime import FieldRuntime, Turn
from acrm_core.session_c.orchestrator import SessionCEngine
from acrm_core.session_c.observation import EvolutionObservation, ObservationKind
from acrm_core.evolution.session_c import EvolutionCandidate, SpecialistVote


def _generator(observations):
    return EvolutionCandidate(
        "gap-contract-candidate",
        "candidate source",
        tuple(item.observation_id for item in observations),
    )


def _engine():
    return SessionCEngine(
        metric_name="S",
        generator=_generator,
        tester=lambda candidate: True,
        vote_provider=lambda candidate, context: (
            SpecialistVote("contract-reviewer", 1.0, 1.0, 1.0),
        ),
    )


def _evaluation(runtime, sequence, *, session="gap-contract-session", timestamp=None):
    turns = (
        Turn("user", f"Explain system behavior at sequence {sequence}."),
        Turn("model", f"System behavior observation {sequence}."),
    )
    return runtime.evaluate(
        turns,
        session_id=session,
        sequence=sequence,
        timestamp=timestamp,
    )


def _gap(engine):
    gaps = engine.sequence_gaps
    assert len(gaps) == 1
    return gaps[0]


def _state(gap, sequence):
    return gap.sequence_states[sequence]


# GAP-001 .. GAP-006: normal ingestion, replay, conflict, and ordering.

def test_GAP_001_accepts_first_sequence():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-1"), _engine()
    evaluation = _evaluation(runtime, 10)
    assert engine.observe_runtime(evaluation) == len(evaluation.observations)


def test_GAP_002_accepts_jump_and_records_missing_sequence():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-2"), _engine()
    engine.observe_runtime(_evaluation(runtime, 10))
    engine.observe_runtime(_evaluation(runtime, 12))
    gap = _gap(engine)
    assert (gap.start_sequence, gap.end_sequence) == (11, 11)
    assert gap.status == "OPEN"
    assert _state(gap, 11) == "OPEN"


def test_GAP_003_exact_replay_is_idempotent():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-3"), _engine()
    evaluation = _evaluation(runtime, 12)
    engine.observe_runtime(evaluation)
    before = engine.observations
    assert engine.observe_runtime(evaluation) == 0
    assert engine.observations == before


def test_GAP_004_changed_payload_replay_conflicts_without_mutation():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-4"), _engine()
    evaluation = _evaluation(runtime, 12)
    engine.observe_runtime(evaluation)
    changed = replace(evaluation, avg_stability=evaluation.avg_stability + 0.01)
    before = (engine.observations, engine.sequence_gaps)
    with pytest.raises(ValueError, match="conflict"):
        engine.observe_runtime(changed)
    assert (engine.observations, engine.sequence_gaps) == before


def test_GAP_005_normal_ingestion_rejects_sequence_inside_open_gap():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-5"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    before = (engine.observations, engine.sequence_gaps)
    with pytest.raises(ValueError, match="compensat|out.of.order|late"):
        engine.observe_runtime(_evaluation(runtime, 13))
    assert (engine.observations, engine.sequence_gaps) == before


def test_GAP_006_old_sequence_without_matching_gap_is_rejected():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-6"), _engine()
    engine.observe_runtime(_evaluation(runtime, 10))
    engine.observe_runtime(_evaluation(runtime, 12))
    before = (engine.observations, engine.sequence_gaps)
    with pytest.raises(ValueError):
        engine.observe_runtime(_evaluation(runtime, 9))
    assert (engine.observations, engine.sequence_gaps) == before


# GAP-007 .. GAP-012: partial compensation; original gap identity/range is stable.

def _open_13_16():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-partial"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 17))
    gap = _gap(engine)
    assert (gap.start_sequence, gap.end_sequence) == (13, 16)
    return runtime, engine, gap


def test_GAP_007_compensates_only_requested_sequence():
    runtime, engine, gap = _open_13_16()
    engine.compensate_gap(_evaluation(runtime, 14), source="authoritative-replay")
    current = _gap(engine)
    assert _state(current, 14) == "COMPENSATED"
    assert all(_state(current, n) == "OPEN" for n in (13, 15, 16))


def test_GAP_008_partial_compensation_preserves_original_gap_range_and_id():
    runtime, engine, original = _open_13_16()
    engine.compensate_gap(_evaluation(runtime, 14), source="authoritative-replay")
    current = _gap(engine)
    assert current.gap_id == original.gap_id
    assert (current.start_sequence, current.end_sequence) == (13, 16)


def test_GAP_009_second_compensation_changes_only_its_sequence():
    runtime, engine, _ = _open_13_16()
    engine.compensate_gap(_evaluation(runtime, 14), source="replay")
    engine.compensate_gap(_evaluation(runtime, 15), source="replay")
    gap = _gap(engine)
    assert _state(gap, 14) == _state(gap, 15) == "COMPENSATED"
    assert _state(gap, 13) == _state(gap, 16) == "OPEN"


def test_GAP_010_gap_remains_open_while_any_member_is_open():
    runtime, engine, _ = _open_13_16()
    engine.compensate_gap(_evaluation(runtime, 14), source="replay")
    engine.compensate_gap(_evaluation(runtime, 15), source="replay")
    assert _gap(engine).status == "OPEN"


def test_GAP_011_identical_compensation_replay_is_idempotent():
    runtime, engine, _ = _open_13_16()
    evaluation = _evaluation(runtime, 14)
    engine.compensate_gap(evaluation, source="replay")
    audit_before = engine.gap_audit_events
    engine.compensate_gap(evaluation, source="replay")
    assert engine.gap_audit_events == audit_before


def test_GAP_012_conflicting_compensation_does_not_change_history():
    runtime, engine, _ = _open_13_16()
    evaluation = _evaluation(runtime, 14)
    engine.compensate_gap(evaluation, source="replay")
    changed = replace(evaluation, avg_stability=evaluation.avg_stability + 0.02)
    before = (engine.gap_audit_events, engine.sequence_gaps)
    with pytest.raises(ValueError, match="conflict"):
        engine.compensate_gap(changed, source="replay")
    assert (engine.gap_audit_events, engine.sequence_gaps) == before


# GAP-013 .. GAP-016: explicit, append-only UNRECOVERABLE decisions.

def test_GAP_013_unrecoverable_requires_complete_decision_metadata():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-13"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    with pytest.raises((TypeError, ValueError)):
        engine.mark_gap_unrecoverable(13, 13)


def test_GAP_014_valid_unrecoverable_decision_is_audited():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-14"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    engine.mark_gap_unrecoverable(
        13, 13, reason="authoritative source confirms loss",
        source="retention-authority", decision_id="decision-14",
    )
    assert _gap(engine).status == "UNRECOVERABLE"
    assert engine.gap_audit_events[-1].decision_id == "decision-14"


def test_GAP_015_prior_gap_decision_cannot_be_overwritten():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-15"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    engine.mark_gap_unrecoverable(
        13, 13, reason="confirmed loss", source="retention-authority",
        decision_id="decision-original",
    )
    before = engine.gap_audit_events
    with pytest.raises(ValueError):
        engine.mark_gap_unrecoverable(
            13, 13, reason="replacement", source="other-authority",
            decision_id="decision-replacement",
        )
    assert engine.gap_audit_events == before


def test_GAP_016_elapsed_time_does_not_resolve_open_gap():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-16"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    assert _gap(engine).status == "OPEN"
    assert _gap(engine).status == "OPEN"


# GAP-017 .. GAP-022: late recovery preserves historical UNRECOVERABLE state.

def _unrecoverable_single_gap():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-late"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    engine.mark_gap_unrecoverable(
        13, 13, reason="confirmed loss at decision time",
        source="retention-authority", decision_id="decision-late",
    )
    return runtime, engine


def test_GAP_017_late_recovery_creates_separate_record():
    runtime, engine = _unrecoverable_single_gap()
    evaluation = _evaluation(runtime, 13)
    engine.record_late_recovery(evaluation, source="delayed-archive")
    assert engine.late_recovery_records[-1].sequence == 13


def test_GAP_018_late_recovery_does_not_rewrite_unrecoverable_decision():
    runtime, engine = _unrecoverable_single_gap()
    engine.record_late_recovery(_evaluation(runtime, 13), source="archive")
    assert _gap(engine).status == "UNRECOVERABLE"
    assert any(event.decision_id == "decision-late" for event in engine.gap_audit_events)


def test_GAP_019_late_recovery_is_visible_in_current_evidence():
    runtime, engine = _unrecoverable_single_gap()
    engine.record_late_recovery(_evaluation(runtime, 13), source="archive")
    analysis = engine.analyze()
    assert analysis.currently_available_evidence.count == 1
    assert analysis.currently_available_evidence.sequences == (13,)


def test_GAP_020_normal_ingestion_cannot_accept_late_recovery():
    runtime, engine = _unrecoverable_single_gap()
    before = engine.observations
    with pytest.raises(ValueError):
        engine.observe_runtime(_evaluation(runtime, 13))
    assert engine.observations == before


def test_GAP_021_identical_late_recovery_is_idempotent():
    runtime, engine = _unrecoverable_single_gap()
    evaluation = _evaluation(runtime, 13)
    engine.record_late_recovery(evaluation, source="archive")
    before = engine.late_recovery_records
    engine.record_late_recovery(evaluation, source="archive")
    assert engine.late_recovery_records == before


def test_GAP_022_conflicting_late_recovery_preserves_original_record():
    runtime, engine = _unrecoverable_single_gap()
    evaluation = _evaluation(runtime, 13)
    engine.record_late_recovery(evaluation, source="archive")
    changed = replace(evaluation, avg_stability=evaluation.avg_stability + 0.03)
    before = engine.late_recovery_records
    with pytest.raises(ValueError, match="conflict"):
        engine.record_late_recovery(changed, source="archive")
    assert engine.late_recovery_records == before


# GAP-023 .. GAP-026: append-only audit and per-sequence state derivation.

def test_GAP_023_each_compensation_appends_an_audit_event():
    runtime, engine, _ = _open_13_16()
    engine.compensate_gap(_evaluation(runtime, 14), source="replay")
    engine.compensate_gap(_evaluation(runtime, 15), source="replay")
    assert len(engine.gap_audit_events) == 2


def test_GAP_024_unrecoverable_decision_is_a_distinct_audit_event():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-24"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    engine.mark_gap_unrecoverable(
        13, 13, reason="confirmed loss", source="authority",
        decision_id="decision-24",
    )
    assert engine.gap_audit_events[-1].event_type == "UNRECOVERABLE"


def test_GAP_025_late_recovery_appends_evidence_without_replacing_decision():
    runtime, engine = _unrecoverable_single_gap()
    audit_before = engine.gap_audit_events
    engine.record_late_recovery(_evaluation(runtime, 13), source="archive")
    assert engine.gap_audit_events[:len(audit_before)] == audit_before
    assert _gap(engine).status == "UNRECOVERABLE"


def test_GAP_026_partial_state_is_per_sequence_and_gap_identity_is_stable():
    runtime, engine, original = _open_13_16()
    engine.compensate_gap(_evaluation(runtime, 14), source="replay")
    engine.compensate_gap(_evaluation(runtime, 15), source="replay")
    gap = _gap(engine)
    assert gap.gap_id == original.gap_id
    assert (gap.start_sequence, gap.end_sequence) == (13, 16)
    assert tuple(gap.sequence_states[n] for n in range(13, 17)) == (
        "OPEN", "COMPENSATED", "COMPENSATED", "OPEN"
    )


# GAP-027 .. GAP-030: time-scoped historical analysis and current evidence.

def test_GAP_027_analysis_exposes_historical_completeness():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-27"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    analysis = engine.analyze()
    assert analysis.historical_completeness is not None


def test_GAP_028_analysis_exposes_currently_available_evidence():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-28"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    analysis = engine.analyze()
    assert analysis.currently_available_evidence.count == 0
    assert analysis.currently_available_evidence.sequences == ()


def test_GAP_029_open_gap_marks_historical_scope_incomplete():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-29"), _engine()
    engine.observe_runtime(_evaluation(runtime, 12))
    engine.observe_runtime(_evaluation(runtime, 14))
    analysis = engine.analyze()
    assert analysis.historical_completeness.complete is False
    assert analysis.historical_completeness.expected_sequences == 3


def test_GAP_030_late_recovery_does_not_change_past_as_of_analysis():
    runtime, engine = _unrecoverable_single_gap()
    decision_time = datetime.now(timezone.utc)
    before = engine.analyze(as_of=decision_time)
    engine.record_late_recovery(
        _evaluation(runtime, 13, timestamp=decision_time + timedelta(seconds=1)),
        source="archive",
    )
    historical = engine.analyze(as_of=decision_time)
    current = engine.analyze()
    assert historical.historical_completeness == before.historical_completeness
    assert historical.currently_available_evidence.count == 0
    assert current.currently_available_evidence.sequences == (13,)
    assert current.historical_completeness.complete is True
    assert current.historical_completeness.available_sequences == 3


def test_GAP_031_future_sequence_does_not_expand_past_analysis_scope():
    runtime, engine = FieldRuntime(runtime_id="gap-runtime-31"), _engine()
    engine.observe_runtime(_evaluation(runtime, 10))
    engine.observe_runtime(_evaluation(runtime, 12))

    # Freeze the historical analysis point before the next sequence arrives.
    analysis_time = datetime.now(timezone.utc)
    historical_before = engine.analyze(as_of=analysis_time)

    engine.observe_runtime(_evaluation(runtime, 15))
    historical_after = engine.analyze(as_of=analysis_time)
    current = engine.analyze()

    assert historical_after.historical_completeness == historical_before.historical_completeness
    assert historical_after.historical_completeness.scope_start == 10
    assert historical_after.historical_completeness.scope_end == 12
    assert historical_after.historical_completeness.expected_sequences == 3
    assert historical_after.historical_completeness.available_sequences == 2
    assert len(historical_after.sequence_gaps) == 1
    assert (historical_after.sequence_gaps[0].start_sequence,
            historical_after.sequence_gaps[0].end_sequence) == (11, 11)
    assert current.historical_completeness.scope_end == 15
    assert current.historical_completeness.expected_sequences == 6
    assert len(current.sequence_gaps) == 2
    assert (current.sequence_gaps[-1].start_sequence,
            current.sequence_gaps[-1].end_sequence) == (13, 14)


def test_GAP_032_all_analysis_outputs_are_isolated_from_future_receipts():
    initial_time = datetime.now(timezone.utc)
    initial_observations = tuple(
        EvolutionObservation(
            observation_id=f"seed-{index}",
            kind=ObservationKind.AMBIGUITY,
            description=f"Initial metric sample {index}",
            observed_at=initial_time - timedelta(seconds=10 - index),
            context={"S": value},
            source="gap-032-seed",
        )
        for index, value in enumerate((0.1, 0.2, 0.3), start=1)
    )
    engine = SessionCEngine(
        observations=initial_observations,
        metric_name="S",
        current_value=-999.0,
        min_observations=1,
        generator=_generator,
        tester=lambda candidate: True,
        vote_provider=lambda candidate, context: (
            SpecialistVote("gap-032-reviewer", 1.0, 1.0, 1.0),
        ),
    )

    # T is after the seed state has been received by Session C.
    analysis_time = datetime.now(timezone.utc)
    historical_before = engine.analyze(as_of=analysis_time)

    # Both the event timestamp and the observation timestamps predate T,
    # but the observer receives these records only after T. They must not
    # be retroactively visible in the historical analysis.
    late_event_time = analysis_time - timedelta(seconds=1)
    runtime = FieldRuntime(runtime_id="gap-runtime-32")
    evaluation = _evaluation(
        runtime, 1, timestamp=late_event_time,
    )
    engine.observe_runtime(evaluation)

    for index, value in enumerate((10.0, 20.0, 30.0, 40.0, 50.0), start=1):
        engine.record(EvolutionObservation(
            observation_id=f"gap-contract-session:late:{index}",
            kind=ObservationKind.MISSING_CAPABILITY,
            description=f"Late-arriving metric sample {index}",
            observed_at=late_event_time,
            context={"S": value},
            source="gap-032-late-source",
        ))

    historical_after = engine.analyze(as_of=analysis_time)
    current = engine.analyze()

    # The entire historical result, not just Gap completeness, is stable.
    assert historical_after == historical_before
    assert historical_after.topic.dominant.topic == "ambiguity_resolution"
    assert historical_after.envelope.sample_count == 3
    assert historical_after.readiness.observation_count == 3
    assert historical_after.readiness.approach.value == -999.0

    # Current analysis sees the new evidence and the Runtime's latest value.
    assert current.topic.dominant.topic == "capability_gap"
    assert current.envelope.sample_count > historical_after.envelope.sample_count
    assert current.readiness.observation_count > historical_after.readiness.observation_count
    assert current.readiness.approach.value == evaluation.field_state.metrics["S"]
    assert current.readiness.approach.value != historical_after.readiness.approach.value



# GAP-033: deterministic observer order, serialized commits, and snapshot cuts.

def test_GAP_033_ingest_sequence_is_independent_of_wall_clock_order(monkeypatch):
    import acrm_core.session_c.orchestrator as orchestrator_module

    real_datetime = datetime
    clock_values = iter((
        real_datetime(2030, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
        real_datetime(2030, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
        real_datetime(2030, 1, 1, 0, 0, 0, 500000, tzinfo=timezone.utc),
        real_datetime(2030, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    ))

    class BackwardsClock(real_datetime):
        @classmethod
        def now(cls, tz=None):
            value = next(clock_values)
            return value if tz is None else value.astimezone(tz)

    monkeypatch.setattr(orchestrator_module, "datetime", BackwardsClock)
    engine = _engine()
    engine.current_value = 1.0
    engine.record(EvolutionObservation(
        "clock-first", ObservationKind.AMBIGUITY, "first",
        real_datetime(2029, 1, 1, tzinfo=timezone.utc), {"S": 1.0},
    ))
    engine.record(EvolutionObservation(
        "clock-second", ObservationKind.AMBIGUITY, "second",
        real_datetime(2029, 1, 1, tzinfo=timezone.utc), {"S": 2.0},
    ))

    snapshot = engine.analyze(
        as_of=real_datetime(2031, 1, 1, tzinfo=timezone.utc),
        as_of_ingest_sequence=2,
    )
    assert snapshot.snapshot_ingest_sequence == 2
    assert snapshot.readiness.observation_count == 1


def test_GAP_033_snapshot_cut_excludes_later_commits():
    engine = _engine()
    engine.current_value = 1.0
    first_time = datetime.now(timezone.utc)
    engine.record(EvolutionObservation(
        "snapshot-first", ObservationKind.AMBIGUITY, "first",
        first_time, {"S": 1.0},
    ))
    snapshot_time = datetime.now(timezone.utc)
    first = engine.analyze(as_of=snapshot_time)
    engine.record(EvolutionObservation(
        "snapshot-second", ObservationKind.MISSING_CAPABILITY, "second",
        first_time, {"S": 2.0},
    ))

    frozen = engine.analyze(as_of=snapshot_time, as_of_ingest_sequence=first.snapshot_ingest_sequence)
    current = engine.analyze()
    assert frozen == first
    assert frozen.snapshot_ingest_sequence == 2
    assert frozen.readiness.observation_count == 1
    assert current.snapshot_ingest_sequence == 3
    assert current.readiness.observation_count == 2


def test_GAP_033_concurrent_records_commit_once_and_snapshot_consistently():
    engine = _engine()
    engine.current_value = 1.0
    observed_at = datetime.now(timezone.utc)

    def add(index):
        engine.record(EvolutionObservation(
            f"concurrent-{index}", ObservationKind.AMBIGUITY,
            f"concurrent observation {index}", observed_at,
            {"S": float(index + 1)},
        ))

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = []
        for index in range(32):
            futures.append(pool.submit(add, index))
            futures.append(pool.submit(engine.analyze))
        snapshots = [future.result() for future in futures if future.result() is not None]

    snapshot = engine.analyze()
    assert snapshot.snapshot_ingest_sequence == 33
    assert snapshot.readiness.observation_count == 32
    assert snapshot.envelope.sample_count == 32
    assert len(engine.observations) == 32
    assert all(
        item.snapshot_ingest_sequence == item.readiness.observation_count + 1
        for item in snapshots
    )
