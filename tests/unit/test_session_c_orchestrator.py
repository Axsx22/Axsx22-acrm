from acrm_core.evolution.session_c import EvolutionCandidate, ObservationKind, SpecialistVote
from acrm_core.runtime.field_runtime import FieldRuntime, Turn
import pytest
from acrm_core.session_c.orchestrator import SessionCEngine
from test_session_c_dynamic import obs


def generator(observations):
    return EvolutionCandidate(
        "candidate-1",
        "candidate source",
        tuple(o.observation_id for o in observations),
    )


def candidate_tester(candidate):
    return True


def votes(candidate, context):
    return (SpecialistVote("stability", 0.9, 0.9, 1.0),)


def test_engine_waits_for_dynamic_tolerance_before_generation():
    items = tuple(obs(i, ObservationKind.PRESSURE, float(i)) for i in range(10))
    engine = SessionCEngine(
        observations=items,
        metric_name="load",
        current_value=4.0,
        generator=generator,
        tester=candidate_tester,
        vote_provider=votes,
    )
    decision = engine.evolve()
    assert decision.status == "WAIT_DYNAMIC_TOLERANCE"
    assert engine.candidate is None


def test_engine_runs_test_then_weighted_review_after_dynamic_trigger():
    items = tuple(obs(i, ObservationKind.PRESSURE, float(i)) for i in range(10))
    engine = SessionCEngine(
        observations=items,
        metric_name="load",
        current_value=8.1,
        generator=generator,
        tester=candidate_tester,
        vote_provider=votes,
    )
    first = engine.evolve()
    assert first.status == "TESTING_PROGRESS"
    second = engine.evolve()
    assert second.status == "SWITCH_RECOMMENDED"
    assert second.weighted_score == 0.9


def test_engine_propagates_low_signal_direction():
    items = tuple(obs(i, ObservationKind.PRESSURE, float(10 - i)) for i in range(10))
    engine = SessionCEngine(
        observations=items,
        metric_name="load",
        current_value=1.8,
        direction="low",
        generator=generator,
        tester=candidate_tester,
        vote_provider=votes,
    )
    analysis = engine.analyze()
    assert analysis.envelope.direction == "low"
    assert analysis.readiness.state == "WARNING"
    assert analysis.readiness.ready is True



def test_engine_ingests_runtime_evaluations_as_new_observations():
    runtime = FieldRuntime()
    engine = SessionCEngine(
        metric_name="S",
        generator=generator,
        tester=candidate_tester,
        vote_provider=votes,
    )
    turns = (
        Turn("user", "Explain the software system and API behavior."),
        Turn("model", "The software system exposes an API and records telemetry."),
    )
    first = runtime.evaluate(turns, session_id="live-session", sequence=1)
    added_first = engine.observe_runtime(first)
    second = runtime.evaluate(turns + (
        Turn("user", "Continue explaining the software system API."),
        Turn("model", "The software API continues to expose system telemetry."),
    ), session_id="live-session", sequence=2)
    added_second = engine.observe_runtime(second)

    assert added_first == len(first.observations)
    assert added_second == len(second.observations)
    assert len(engine.observations) == added_first + added_second
    assert engine.current_value == second.field_state.metrics["S"]
    assert engine.observations[-1].observation_id.startswith("live-session:2:")


def test_engine_rejects_duplicate_runtime_observation_delivery():
    runtime = FieldRuntime()
    engine = SessionCEngine(
        metric_name="S",
        generator=generator,
        tester=candidate_tester,
        vote_provider=votes,
    )
    evaluation = runtime.evaluate(
        (Turn("user", "Explain a software system."), Turn("model", "A software system has components.")),
        session_id="duplicate-delivery",
        sequence=1,
    )
    engine.observe_runtime(evaluation)
    assert engine.observe_runtime(evaluation) == 0


def test_engine_rejects_cross_session_delivery():
    runtime = FieldRuntime()
    engine = SessionCEngine(
        metric_name="S", generator=generator, tester=candidate_tester,
        vote_provider=votes,
    )
    turns = (
        Turn("user", "Explain a software system."),
        Turn("model", "A software system has components."),
    )
    a = runtime.evaluate(turns, field_id="runtime-a", session_id="session-a", sequence=1)
    b = runtime.evaluate(turns, field_id="runtime-a", session_id="session-b", sequence=1)
    engine.observe_runtime(a)
    before = engine.observations
    with pytest.raises(ValueError, match="different Runtime/Session"):
        engine.observe_runtime(b)
    assert engine.observations == before


def test_engine_rejects_out_of_order_delivery_atomically():
    runtime = FieldRuntime()
    engine = SessionCEngine(
        metric_name="S", generator=generator, tester=candidate_tester,
        vote_provider=votes,
    )
    turns = (
        Turn("user", "Explain a software system."),
        Turn("model", "A software system has components."),
    )
    later = runtime.evaluate(turns, session_id="ordered", sequence=2)
    earlier = runtime.evaluate(turns, session_id="ordered", sequence=1)
    engine.observe_runtime(later)
    before = engine.observations
    with pytest.raises(ValueError, match="out-of-order"):
        engine.observe_runtime(earlier)
    assert engine.observations == before



def test_runtime_instances_have_distinct_stable_ids():
    first = FieldRuntime()
    second = FieldRuntime()
    assert first.runtime_id
    assert first.runtime_id == first.evaluate(
        (Turn("user", "Explain a system."), Turn("model", "A system has parts.")),
        sequence=1,
    ).runtime_id
    assert first.runtime_id != second.runtime_id


def test_sequence_gap_is_recorded_and_late_event_compensates_it():
    runtime = FieldRuntime(runtime_id="runtime-gap")
    engine = SessionCEngine(
        metric_name="S", generator=generator, tester=candidate_tester,
        vote_provider=votes,
    )
    turns = (
        Turn("user", "Explain a software system."),
        Turn("model", "A software system has components."),
    )
    seq12 = runtime.evaluate(turns, session_id="gap-session", sequence=12)
    seq14 = runtime.evaluate(turns, session_id="gap-session", sequence=14)
    seq13 = runtime.evaluate(turns, session_id="gap-session", sequence=13)

    engine.observe_runtime(seq12)
    engine.observe_runtime(seq14)
    assert len(engine.sequence_gaps) == 1
    gap = engine.sequence_gaps[0]
    assert (gap.start_sequence, gap.end_sequence) == (13, 13)
    assert gap.previous_sequence == 12
    assert gap.next_sequence == 14
    assert gap.status == "open"

    engine.observe_runtime(seq13)
    gap = engine.sequence_gaps[0]
    assert gap.status == "compensated"
    assert gap.resolved_at is not None
    assert engine.observations[-1].observation_id.startswith("gap-session:13:")


def test_same_sequence_with_changed_full_payload_is_a_conflict():
    from dataclasses import replace
    from datetime import timedelta

    runtime = FieldRuntime(runtime_id="runtime-hash")
    engine = SessionCEngine(
        metric_name="S", generator=generator, tester=candidate_tester,
        vote_provider=votes,
    )
    evaluation = runtime.evaluate(
        (Turn("user", "Explain a system."), Turn("model", "A system has parts.")),
        session_id="hash-session", sequence=1,
    )
    engine.observe_runtime(evaluation)
    changed_observation = replace(
        evaluation.observations[0],
        observed_at=evaluation.observations[0].observed_at + timedelta(seconds=1),
    )
    changed = replace(evaluation, observations=(changed_observation,) + evaluation.observations[1:])
    with pytest.raises(ValueError, match="conflicting replay"):
        engine.observe_runtime(changed)
