from acrm_core.evolution.session30 import (
    EvolutionCandidate,
    EvolutionObservation,
    EvolutionSession30,
    EvolutionTolerance,
    SpecialistVote,
)


def observation(number: int) -> EvolutionObservation:
    return EvolutionObservation(
        observation_id=f"obs-{number}",
        kind="pressure",
        description=f"runtime pressure observation {number}",
    )


def candidate_generator(observations):
    return EvolutionCandidate(
        candidate_id="candidate-1",
        source="def candidate_change():\n    return True\n",
        based_on=tuple(item.observation_id for item in observations),
    )


def votes(_candidate):
    return (
        SpecialistVote("relevant-high", 0.9, reliability=0.9, relevance=1.0),
        SpecialistVote("relevant-low", 0.2, reliability=0.5, relevance=0.2),
    )


def test_observation_recording_is_neutral_and_generation_is_gated():
    session = EvolutionSession30(
        tolerance=EvolutionTolerance(generation_after=3, successful_tests_before_review=2),
        generator=candidate_generator,
        tester=lambda _: True,
        vote_provider=votes,
    )
    session.record(observation(1))
    session.record(observation(2))
    assert session.generation_ready() is False
    assert session.generate_candidate() is None
    session.record(observation(3))
    candidate = session.generate_candidate()
    assert candidate is not None
    assert candidate.based_on == ("obs-1", "obs-2", "obs-3")


def test_voting_is_blocked_until_second_test_tolerance():
    session = EvolutionSession30(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=2),
        generator=candidate_generator,
        tester=lambda _: True,
        vote_provider=votes,
    )
    session.record(observation(1))
    session.generate_candidate()

    first = session.review()
    assert first.status == "TESTING_PROGRESS"
    assert first.votes_used == 0
    assert first.candidate.successful_test_runs == 1

    second = session.review()
    assert second.status == "SWITCH_RECOMMENDED"
    assert second.votes_used == 2
    assert second.weighted_score is not None
    assert second.candidate.ready_for_review is True


def test_failed_test_blocks_voting():
    session = EvolutionSession30(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=1),
        generator=candidate_generator,
        tester=lambda _: False,
        vote_provider=votes,
    )
    session.record(observation(1))
    session.generate_candidate()

    decision = session.review()
    assert decision.status == "REJECT_TEST"
    assert decision.votes_used == 0
    assert decision.candidate.successful_test_runs == 0
    assert decision.candidate.ready_for_review is False


def test_weighted_vote_can_retain_current_runtime():
    session = EvolutionSession30(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=1, switch_score=0.8),
        generator=candidate_generator,
        tester=lambda _: True,
        vote_provider=lambda _: (SpecialistVote("only", 0.5, 1.0, 1.0),),
    )
    session.record(observation(1))
    session.generate_candidate()

    decision = session.review()
    assert decision.status == "RETAIN_CURRENT"
    assert decision.weighted_score == 0.5


def test_zero_total_vote_weight_is_rejected():
    session = EvolutionSession30(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=1),
        generator=candidate_generator,
        tester=lambda _: True,
        vote_provider=lambda _: (SpecialistVote("zero", 1.0, 0.0, 1.0),),
    )
    session.record(observation(1))
    session.generate_candidate()

    decision = session.review()
    assert decision.status == "REJECT_VOTE"
    assert decision.votes_used == 1


def test_session30_never_executes_generated_source():
    executed = []

    def generator(_):
        return EvolutionCandidate(
            candidate_id="candidate-unsafe",
            source="executed.append('should never run')",
            based_on=("obs-1",),
        )

    session = EvolutionSession30(
        tolerance=EvolutionTolerance(generation_after=1, successful_tests_before_review=1),
        generator=generator,
        tester=lambda candidate: candidate.source.startswith("executed.append"),
        vote_provider=lambda _: (SpecialistVote("test", 1.0, 1.0, 1.0),),
    )
    session.record(observation(1))
    session.generate_candidate()
    decision = session.review()

    assert decision.status == "SWITCH_RECOMMENDED"
    assert executed == []
