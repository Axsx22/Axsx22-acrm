from datetime import datetime, timezone

import pytest

from acrm_core.session30 import (
    CandidateCode,
    EvolutionPolicy,
    EvolutionStage,
    EvolutionVote,
    EvolutionWorkflow,
    Observation,
    ObservationKind,
    ObservationLedger,
)


def observation(i: int, kind: ObservationKind = ObservationKind.PRESSURE) -> Observation:
    return Observation(
        observation_id=f"obs-{i}",
        kind=kind,
        observed_at=datetime(2026, 8, 31, 10, i, tzinfo=timezone.utc),
        description=f"Observed event {i}",
    )


def candidate(readiness: float = 0.85, tests_passed: bool = False) -> CandidateCode:
    return CandidateCode("cand-1", "field-governance", "# proposed code", readiness, tests_passed)


def test_observation_has_no_severity_or_score() -> None:
    item = observation(1, ObservationKind.AMBIGUITY)
    assert item.kind is ObservationKind.AMBIGUITY
    assert not hasattr(item, "severity")
    assert not hasattr(item, "score")


def test_ledger_is_append_only_and_deduplicates_ids() -> None:
    ledger = ObservationLedger()
    ledger.record(observation(1))
    assert ledger.count() == 1
    with pytest.raises(ValueError):
        ledger.record(observation(1))


def test_generation_requires_observation_tolerance() -> None:
    workflow = EvolutionWorkflow(EvolutionPolicy(generation_trigger_count=3))
    assert not workflow.generation_eligible(2)
    assert workflow.generation_eligible(3)
    assert workflow.stage is EvolutionStage.GENERATION_ELIGIBLE


def test_candidate_below_test_warning_is_not_tested() -> None:
    workflow = EvolutionWorkflow(EvolutionPolicy(test_warning_readiness=0.5))
    workflow.generation_eligible(3)
    assert workflow.submit_candidate(candidate(0.49)) is EvolutionStage.CANDIDATE
    with pytest.raises(RuntimeError):
        workflow.mark_tests(True)


def test_successful_tests_open_weighted_voting() -> None:
    workflow = EvolutionWorkflow()
    workflow.generation_eligible(3)
    assert workflow.submit_candidate(candidate(0.85)) is EvolutionStage.TESTING
    assert workflow.mark_tests(True) is EvolutionStage.VOTING


def test_vote_weight_is_topic_relevance_times_layer_weight() -> None:
    vote = EvolutionVote("observer-a", "cand-1", 0.8, 0.5, True)
    assert vote.weight == pytest.approx(0.4)


def test_switch_requires_weighted_consensus() -> None:
    workflow = EvolutionWorkflow(EvolutionPolicy(approval_threshold=0.67))
    workflow.generation_eligible(3)
    workflow.submit_candidate(candidate(0.9))
    workflow.mark_tests(True)
    workflow.cast_vote(EvolutionVote("a", "cand-1", 1.0, 1.0, True))
    workflow.cast_vote(EvolutionVote("b", "cand-1", 1.0, 0.5, False))
    assert workflow.weighted_approval == pytest.approx(2 / 3)
    assert workflow.switch_recommended
    assert workflow.stage is EvolutionStage.SWITCH_READY


def test_failed_tests_reject_candidate_and_block_votes() -> None:
    workflow = EvolutionWorkflow()
    workflow.generation_eligible(3)
    workflow.submit_candidate(candidate(0.9))
    assert workflow.mark_tests(False) is EvolutionStage.REJECTED
    with pytest.raises(RuntimeError):
        workflow.cast_vote(EvolutionVote("a", "cand-1", 1.0, 1.0, True))
