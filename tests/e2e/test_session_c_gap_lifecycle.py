"""End-to-end Session C gap lifecycle.

Exercises the real Runtime -> SessionCEngine boundary and all three ingestion
paths in one longitudinal scenario. Persistence across process restart is
intentionally outside this in-memory contract.
"""
from datetime import datetime, timezone

from acrm_core.evolution.session_c import EvolutionCandidate, SpecialistVote
from acrm_core.runtime.field_runtime import FieldRuntime, Turn
from acrm_core.session_c.orchestrator import SessionCEngine


def _generator(observations):
    return EvolutionCandidate(
        "gap-e2e-candidate", "candidate source",
        tuple(item.observation_id for item in observations),
    )


def test_runtime_gap_partial_compensation_unrecoverable_and_late_recovery():
    runtime = FieldRuntime(runtime_id="e2e-runtime")
    engine = SessionCEngine(
        metric_name="S",
        generator=_generator,
        tester=lambda candidate: True,
        vote_provider=lambda candidate, context: (
            SpecialistVote("e2e-reviewer", 1.0, 1.0, 1.0),
        ),
    )
    turns = (
        Turn("user", "Observe the evolving system state."),
        Turn("model", "The runtime emits a state evaluation."),
    )

    events = {
        sequence: runtime.evaluate(
            turns + (Turn("user", f"Sequence {sequence}"),),
            session_id="e2e-session",
            sequence=sequence,
        )
        for sequence in (12, 13, 14, 15, 16, 17)
    }

    # Normal ingestion establishes the gap 13..16.
    engine.observe_runtime(events[12])
    engine.observe_runtime(events[17])
    gap = engine.sequence_gaps[0]
    original_gap_id = gap.gap_id
    assert (gap.start_sequence, gap.end_sequence) == (13, 16)
    assert gap.status == "OPEN"

    # Recovery is explicit and per-sequence; the original gap is retained.
    assert engine.compensate_gap(events[14], source="runtime-replay")
    assert engine.compensate_gap(events[15], source="runtime-replay")
    gap = engine.sequence_gaps[0]
    assert gap.gap_id == original_gap_id
    assert (gap.start_sequence, gap.end_sequence) == (13, 16)
    assert gap.sequence_states[14] == "COMPENSATED"
    assert gap.sequence_states[15] == "COMPENSATED"
    assert gap.sequence_states[13] == gap.sequence_states[16] == "OPEN"
    assert gap.status == "OPEN"

    # Explicit decision closes only remaining OPEN members.
    engine.mark_gap_unrecoverable(
        13, 16,
        reason="authoritative retention review declared remaining events unrecoverable",
        source="retention-review",
        decision_id="e2e-decision-001",
    )
    gap = engine.sequence_gaps[0]
    assert gap.status == "UNRECOVERABLE"
    assert gap.sequence_states[13] == "UNRECOVERABLE"
    assert gap.sequence_states[16] == "UNRECOVERABLE"
    audit_before_late_recovery = engine.gap_audit_events
    decision_time = datetime.now(timezone.utc)
    historical_at_decision = engine.analyze(as_of=decision_time)

    # The late arrival is not admitted through normal ingestion and does not
    # rewrite the UNRECOVERABLE member state or its audit decision.
    try:
        engine.observe_runtime(events[13])
    except ValueError:
        pass
    else:
        raise AssertionError("normal ingestion accepted a late event")
    record = engine.record_late_recovery(events[13], source="delayed-archive")
    assert record.sequence == 13
    assert record.event_timestamp == events[13].field_state.timestamp
    assert record.received_at >= decision_time
    assert engine.sequence_gaps[0].status == "UNRECOVERABLE"
    assert engine.sequence_gaps[0].sequence_states[13] == "UNRECOVERABLE"
    assert engine.gap_audit_events == audit_before_late_recovery

    # The past snapshot remains unchanged; the current view includes new evidence.
    past_again = engine.analyze(as_of=decision_time)
    current = engine.analyze()
    assert past_again.historical_completeness == historical_at_decision.historical_completeness
    assert past_again.currently_available_evidence.sequences == (14, 15)
    assert current.currently_available_evidence.sequences == (13, 14, 15)
    assert current.historical_completeness.available_sequences == 5
    assert current.historical_completeness.expected_sequences == 6
