from acrm_core.evolution.session_c import EvolutionCandidate, ObservationKind, SpecialistVote
from acrm_core.session_c.orchestrator import SessionCEngine

from test_session_c_dynamic import obs


def generator(observations):
    return EvolutionCandidate("candidate-1", "candidate source", tuple(o.observation_id for o in observations))


def candidate_tester(candidate):
    return True


def votes(candidate, context):
    return (SpecialistVote("stability", 0.9, 0.9, 1.0),)


def test_engine_waits_for_dynamic_tolerance_before_generation():
    items = tuple(obs(i, ObservationKind.PRESSURE, float(i)) for i in range(10))
    engine = SessionCEngine(observations=items, metric_name="load", current_value=4.0, generator=generator, tester=candidate_tester, vote_provider=votes)
    decision = engine.evolve()
    assert decision.status == "WAIT_DYNAMIC_TOLERANCE"
    assert engine.candidate is None


def test_engine_runs_test_then_weighted_review_after_dynamic_trigger():
    items = tuple(obs(i, ObservationKind.PRESSURE, float(i)) for i in range(10))
    engine = SessionCEngine(observations=items, metric_name="load", current_value=8.1, generator=generator, tester=candidate_tester, vote_provider=votes)
    first = engine.evolve()
    assert first.status == "TESTING_PROGRESS"
    second = engine.evolve()
    assert second.status == "SWITCH_RECOMMENDED"
    assert second.weighted_score == 0.9
