"""Governed candidate lifecycle for Session 30.

No candidate is applied to the active runtime here. The workflow only moves a
candidate through explicit gates: observation threshold -> candidate creation
-> test warning -> tests -> weighted vote -> switch recommendation.
"""

from dataclasses import dataclass
from enum import Enum


class EvolutionStage(str, Enum):
    DORMANT = "dormant"
    GENERATION_ELIGIBLE = "generation_eligible"
    CANDIDATE = "candidate"
    TESTING = "testing"
    VOTING = "voting"
    SWITCH_READY = "switch_ready"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class EvolutionPolicy:
    """Explicit tolerances for promotion; values are policy, not observations."""

    generation_trigger_count: int = 3
    test_warning_readiness: float = 0.50
    required_runtime_readiness: float = 0.80
    approval_threshold: float = 0.67

    def __post_init__(self) -> None:
        if self.generation_trigger_count < 1:
            raise ValueError("generation_trigger_count must be >= 1")
        for name in ("test_warning_readiness", "required_runtime_readiness", "approval_threshold"):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")
        if self.test_warning_readiness > self.required_runtime_readiness:
            raise ValueError("test warning readiness cannot exceed required runtime readiness")


@dataclass(frozen=True, slots=True)
class CandidateCode:
    """A proposed code revision held outside the active runtime."""

    candidate_id: str
    topic: str
    source: str
    runtime_readiness: float
    tests_passed: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id must be non-empty")
        if not self.topic.strip():
            raise ValueError("topic must be non-empty")
        if not self.source.strip():
            raise ValueError("source must be non-empty")
        if not 0.0 <= float(self.runtime_readiness) <= 1.0:
            raise ValueError("runtime_readiness must be between 0.0 and 1.0")


@dataclass(frozen=True, slots=True)
class EvolutionVote:
    """A weighted vote from one evaluator for a candidate."""

    voter_id: str
    candidate_id: str
    topic_relevance: float
    layer_weight: float
    approve: bool

    def __post_init__(self) -> None:
        if not self.voter_id.strip() or not self.candidate_id.strip():
            raise ValueError("voter_id and candidate_id must be non-empty")
        for name in ("topic_relevance", "layer_weight"):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")

    @property
    def weight(self) -> float:
        return float(self.topic_relevance) * float(self.layer_weight)


class EvolutionWorkflow:
    """State machine for preparing a candidate without mutating the runtime."""

    def __init__(self, policy: EvolutionPolicy | None = None) -> None:
        self.policy = policy or EvolutionPolicy()
        self.stage = EvolutionStage.DORMANT
        self.candidate: CandidateCode | None = None
        self._votes: list[EvolutionVote] = []

    def generation_eligible(self, observation_count: int) -> bool:
        if observation_count < 0:
            raise ValueError("observation_count must be non-negative")
        eligible = observation_count >= self.policy.generation_trigger_count
        if eligible and self.stage == EvolutionStage.DORMANT:
            self.stage = EvolutionStage.GENERATION_ELIGIBLE
        return eligible

    def submit_candidate(self, candidate: CandidateCode) -> EvolutionStage:
        if self.stage not in {EvolutionStage.GENERATION_ELIGIBLE, EvolutionStage.CANDIDATE, EvolutionStage.REJECTED}:
            raise RuntimeError("candidate submission is not allowed at the current stage")
        self.candidate = candidate
        self._votes.clear()
        self.stage = EvolutionStage.TESTING if candidate.runtime_readiness >= self.policy.test_warning_readiness else EvolutionStage.CANDIDATE
        return self.stage

    def mark_tests(self, passed: bool) -> EvolutionStage:
        if self.candidate is None:
            raise RuntimeError("no candidate is available")
        if self.stage != EvolutionStage.TESTING:
            raise RuntimeError("candidate has not reached the test warning threshold")
        self.candidate = CandidateCode(
            candidate_id=self.candidate.candidate_id,
            topic=self.candidate.topic,
            source=self.candidate.source,
            runtime_readiness=self.candidate.runtime_readiness,
            tests_passed=passed,
        )
        self.stage = EvolutionStage.VOTING if passed and self.candidate.runtime_readiness >= self.policy.required_runtime_readiness else EvolutionStage.REJECTED
        return self.stage

    def cast_vote(self, vote: EvolutionVote) -> None:
        if self.candidate is None or self.stage != EvolutionStage.VOTING:
            raise RuntimeError("votes are accepted only after successful tests and readiness")
        if vote.candidate_id != self.candidate.candidate_id:
            raise ValueError("vote candidate_id does not match active candidate")
        if any(existing.voter_id == vote.voter_id for existing in self._votes):
            raise ValueError("each voter may vote once per candidate")
        self._votes.append(vote)
        if self.switch_recommended:
            self.stage = EvolutionStage.SWITCH_READY

    @property
    def weighted_approval(self) -> float:
        total = sum(v.weight for v in self._votes)
        if total == 0.0:
            return 0.0
        approved = sum(v.weight for v in self._votes if v.approve)
        return approved / total

    @property
    def switch_recommended(self) -> bool:
        return bool(
            self.candidate
            and self.candidate.tests_passed
            and self.candidate.runtime_readiness >= self.policy.required_runtime_readiness
            and self.weighted_approval >= self.policy.approval_threshold
        )

    @property
    def votes(self) -> tuple[EvolutionVote, ...]:
        return tuple(self._votes)

    def reset(self) -> None:
        """Discard the pending candidate; the active runtime is never modified."""
        self.stage = EvolutionStage.DORMANT
        self.candidate = None
        self._votes.clear()
