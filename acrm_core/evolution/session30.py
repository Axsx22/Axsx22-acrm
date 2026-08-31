"""Session 30: controlled self-evolution orchestration.

This module is deliberately separated from the runtime field controller.  It
collects already-recorded observations, waits for configured tolerances, asks
a code-generation boundary for a candidate, verifies that candidate through a
separate test boundary, and only then aggregates weighted specialist votes.

It never mutates the active runtime and never executes generated source.
A successful result is a *switch recommendation* for an external, controlled
handoff mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping


@dataclass(frozen=True, slots=True)
class EvolutionTolerance:
    """Thresholds governing when candidate generation and review may begin."""

    generation_after: int = 3
    review_after: int = 1
    switch_score: float = 0.70

    def __post_init__(self) -> None:
        if self.generation_after < 1:
            raise ValueError("generation_after must be >= 1")
        if self.review_after < 1:
            raise ValueError("review_after must be >= 1")
        if self.review_after > self.generation_after:
            raise ValueError("review_after must be <= generation_after")
        if not 0.0 <= self.switch_score <= 1.0:
            raise ValueError("switch_score must be between 0.0 and 1.0")


@dataclass(frozen=True, slots=True)
class EvolutionObservation:
    """A neutral observation emitted by Session 30's observation layer.

    The observation is descriptive.  It intentionally carries no score or
    severity so the recording layer cannot silently become a judge.
    """

    observation_id: str
    kind: str
    description: str
    context: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.observation_id.strip():
            raise ValueError("observation_id must be non-empty")
        if not self.kind.strip():
            raise ValueError("kind must be non-empty")
        if not self.description.strip():
            raise ValueError("description must be non-empty")


@dataclass(frozen=True, slots=True)
class EvolutionCandidate:
    """Generated candidate source awaiting controlled verification."""

    candidate_id: str
    source: str
    based_on: tuple[str, ...]
    tested: bool = False
    test_passed: bool = False
    ready_for_review: bool = False


@dataclass(frozen=True, slots=True)
class SpecialistVote:
    """A specialist's signed assessment for the current evolution topic."""

    specialist_id: str
    vote: float
    reliability: float
    relevance: float

    def __post_init__(self) -> None:
        for name, value in (
            ("vote", self.vote),
            ("reliability", self.reliability),
            ("relevance", self.relevance),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")

    @property
    def weight(self) -> float:
        return self.reliability * self.relevance


@dataclass(frozen=True, slots=True)
class EvolutionDecision:
    """Outcome of the controlled review; no decision changes the active runtime."""

    status: str
    candidate: EvolutionCandidate | None
    weighted_score: float | None
    votes_used: int
    reason: str


CodeGenerator = Callable[[tuple[EvolutionObservation, ...]], EvolutionCandidate]
CandidateTester = Callable[[EvolutionCandidate], bool]
VoteProvider = Callable[[EvolutionCandidate], Iterable[SpecialistVote]]


class EvolutionSession30:
    """Two-stage evolution supervisor for the Session 30 design.

    Stage A is assumed to have produced neutral observations.  Stage B begins
    only after the configured generation tolerance.  A candidate must then
    pass the independent test boundary and become review-ready before weighted
    voting can produce a switch recommendation.
    """

    def __init__(
        self,
        *,
        tolerance: EvolutionTolerance | None = None,
        generator: CodeGenerator,
        tester: CandidateTester,
        vote_provider: VoteProvider,
    ) -> None:
        self.tolerance = tolerance or EvolutionTolerance()
        self._generator = generator
        self._tester = tester
        self._vote_provider = vote_provider
        self._observations: list[EvolutionObservation] = []
        self._candidate: EvolutionCandidate | None = None

    @property
    def observations(self) -> tuple[EvolutionObservation, ...]:
        return tuple(self._observations)

    @property
    def candidate(self) -> EvolutionCandidate | None:
        return self._candidate

    def record(self, observation: EvolutionObservation) -> None:
        """Store an observation without scoring, ranking, or triggering judgment."""
        self._observations.append(observation)

    def generation_ready(self) -> bool:
        return len(self._observations) >= self.tolerance.generation_after

    def generate_candidate(self) -> EvolutionCandidate | None:
        """Ask the code-generation boundary for a candidate once the tolerance is met."""
        if not self.generation_ready():
            return None
        candidate = self._generator(tuple(self._observations))
        if not candidate.source.strip():
            raise ValueError("generated candidate source must be non-empty")
        self._candidate = candidate
        return candidate

    def review(self) -> EvolutionDecision:
        """Test, then vote; return a switch recommendation only after both gates pass."""
        if self._candidate is None:
            return EvolutionDecision(
                "WAIT_GENERATION", None, None, 0,
                "generation tolerance has not produced a candidate",
            )

        if len(self._observations) < self.tolerance.review_after:
            return EvolutionDecision(
                "WAIT_REVIEW", self._candidate, None, 0,
                "review tolerance has not been reached",
            )

        passed = self._tester(self._candidate)
        self._candidate = EvolutionCandidate(
            candidate_id=self._candidate.candidate_id,
            source=self._candidate.source,
            based_on=self._candidate.based_on,
            tested=True,
            test_passed=passed,
            ready_for_review=passed,
        )
        if not passed:
            return EvolutionDecision(
                "REJECT_TEST", self._candidate, None, 0,
                "candidate failed the independent test boundary",
            )

        votes = tuple(self._vote_provider(self._candidate))
        total_weight = sum(v.weight for v in votes)
        if total_weight <= 0.0:
            return EvolutionDecision(
                "REJECT_VOTE", self._candidate, None, len(votes),
                "no positive specialist weight is available",
            )

        weighted_score = sum(v.vote * v.weight for v in votes) / total_weight
        if weighted_score >= self.tolerance.switch_score:
            return EvolutionDecision(
                "SWITCH_RECOMMENDED", self._candidate, weighted_score, len(votes),
                "candidate passed testing and reached the weighted vote threshold",
            )
        return EvolutionDecision(
            "RETAIN_CURRENT", self._candidate, weighted_score, len(votes),
            "candidate passed testing but did not reach the weighted vote threshold",
        )
