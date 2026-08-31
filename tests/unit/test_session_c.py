from datetime import datetime, timedelta, timezone

import pytest

from acrm_core.evolution.session_c import (
    EvolutionCandidate,
    EvolutionContext,
    EvolutionObservation,
    EvolutionSessionC,
    EvolutionTolerance,
    ObservationKind,
    SpecialistVote,
)
from acrm_core.session_c.observation import EvolutionObservation as CanonicalObservation


def observation(number: int, *, offset_hours: int = 0) -> EvolutionObservation:
    return EvolutionObservation(
        observation_id=f"obs-{number}",
        kind=ObservationKind.PRESSURE,
        description=f"runtime pressure observation {number}",
        observed_at=datetime(
            2026, 8, 31, 12, number, tzinfo=timezone(timedelta(hours=offset_hours))
        ),
        context={"signal": "pressure", "sequence": number},
    )


def candidate_generator(observations):
    return EvolutionCandidate(
        candidate_id="candidate-1",
        source="def candidate_change():\n    return True\n",
        based_on=tuple(item.observation_id for item in observations),
    )


def votes(_candidate, context):
    assert context.topic == "runtime-coherence"
    return (
        SpecialistVote("relevant-high", 0.9, reliability=0.9, relevance=1.0),
        SpecialistVote("relevant-low", 0.2, reliability=0.5, relevance=0.2),
    )


def context():
    return EvolutionContext("runtime-coherence", {"field": "current"})


def make_session(**kwargs):
    return EvolutionSessionC(
        tolerance=kwargs.pop("tolerance", EvolutionTolerance()),
        generator=kwargs.pop("generator", candidate_generator),
        tester=kwargs.pop("tester", lambda _: True),
        vote_provider=kwargs.pop("vote_provider", votes),
    )


def test_observation_recording_is_neutral_and_generation_is_gated():
    session = make_session(tolerance=EvolutionTolerance(generation_after=3, successful_tests_before_review=2))
    session.record(observation(1))
    session.record(observation(2))
    assert session.generation_ready() is False
    assert session.generate_candidate() is None
    session.record(observation(3))
    candidate = session.generate_candidate()
    assert candidate is not None
    assert candidate.based_on == ("obs-1", "obs-2", "obs-3")


def test_observation_layer_uses_canonical_record_type():
    item = observation(1)
    assert isinstance(item, CanonicalObservation)


def test_observation_has_no_severity_or_score_and_context_is_immutable():
    item = observation(1)
    assert item.kind is ObservationKind.PRESSURE
    assert not hasattr(item, "severity")
    assert not hasattr(item, "score")
    with pytest.raises(TypeError):
        item.context["new"] = "value"
    assert item.context["signal"] == "pressure"


def test_observation_timestamp_is_normalized_to_utc():
    item = observation(1, offset_hours=4)
    assert item.observed_at.tzinfo == timezone.utc
    assert item.observed_at_utc == item.observed_at


def test_observation_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError):
        EvolutionObservation(
            "obs-naive",
            "pressure",
            "pressure observed",
            datetime(2026, 8, 31, 12, 0),
        )


def test_duplicate_observation_ids_are_rejected():
    session = make_session()
    session.record(observation(1))
    with pytest.raises(ValueError, match="duplicate observation_id"):
        session.record(observation(1))


def test_voting_is_blocked_until_successful_test_tolerance():
    session = make_session(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=2)
    )
    session.record(observation(1))
    session.generate_candidate()

    first = session.review(context())
    assert first.status == "TESTING_PROGRESS"
    assert first.votes_used == 0
    assert first.candidate.successful_test_runs == 1

    second = session.review(context())
    assert second.status == "SWITCH_RECOMMENDED"
    assert second.votes_used == 2
    assert second.weighted_score is not None
    assert second.candidate.ready_for_review is True


def test_failed_test_blocks_voting_but_allows_retest():
    outcomes = iter([False, True])
    session = make_session(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=1),
        tester=lambda _: next(outcomes),
    )
    session.record(observation(1))
    session.generate_candidate()

    failed = session.review(context())
    assert failed.status == "REJECT_TEST"
    assert failed.votes_used == 0
    assert failed.candidate.successful_test_runs == 0

    passed = session.review(context())
    assert passed.status == "SWITCH_RECOMMENDED"
    assert passed.votes_used == 2


def test_weighted_vote_can_retain_current_runtime():
    session = make_session(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=1, switch_score=0.8),
        vote_provider=lambda _candidate, _context: (SpecialistVote("only", 0.5, 1.0, 1.0),),
    )
    session.record(observation(1))
    session.generate_candidate()

    decision = session.review(context())
    assert decision.status == "RETAIN_CURRENT"
    assert decision.weighted_score == 0.5


def test_zero_total_vote_weight_is_rejected():
    session = make_session(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=1),
        vote_provider=lambda _candidate, _context: (SpecialistVote("zero", 1.0, 0.0, 1.0),),
    )
    session.record(observation(1))
    session.generate_candidate()

    decision = session.review(context())
    assert decision.status == "REJECT_VOTE"
    assert decision.votes_used == 1
    assert session.review_complete is True


def test_review_cannot_be_repeated_after_final_decision():
    session = make_session(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=1)
    )
    session.record(observation(1))
    session.generate_candidate()
    first = session.review(context())
    assert first.status == "SWITCH_RECOMMENDED"

    second = session.review(context())
    assert second.status == "REVIEW_COMPLETE"
    assert second.votes_used == 0


def test_session_c_never_executes_generated_source():
    executed = []

    def generator(_):
        return EvolutionCandidate(
            candidate_id="candidate-unsafe",
            source="executed.append('should never run')",
            based_on=("obs-1",),
        )

    session = make_session(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=1),
        generator=generator,
        tester=lambda candidate: candidate.source.startswith("executed.append"),
        vote_provider=lambda _candidate, _context: (SpecialistVote("test", 1.0, 1.0, 1.0),),
    )
    session.record(observation(1))
    session.generate_candidate()
    decision = session.review(context())

    assert decision.status == "SWITCH_RECOMMENDED"
    assert executed == []


def test_candidate_is_not_regenerated_when_new_observations_arrive():
    session = make_session(tolerance=EvolutionTolerance(generation_after=2, successful_tests_before_review=1))
    session.record(observation(1))
    session.record(observation(2))
    first = session.generate_candidate()
    session.record(observation(3))
    second = session.generate_candidate()
    assert first is second
    assert second.based_on == ("obs-1", "obs-2")


def test_tolerance_rejects_invalid_values():
    with pytest.raises(ValueError):
        EvolutionTolerance(generation_after=0)
    with pytest.raises(ValueError):
        EvolutionTolerance(successful_tests_before_review=0)
    with pytest.raises(ValueError):
        EvolutionTolerance(switch_score=1.1)


def test_specialist_vote_rejects_non_finite_values():
    with pytest.raises(ValueError):
        SpecialistVote("bad", float("nan"), 1.0, 1.0)
