"""Session 30: controlled self-evolution orchestration.

This module is deliberately separated from the runtime field controller. It
collects already-recorded observations, waits for a generation tolerance,
creates a candidate through an explicit code-generation boundary, verifies the
candidate through a separate test boundary, and only then aggregates weighted
specialist votes.

It never mutates the active runtime and never executes generated source.
A successful result is a *switch recommendation* for an external, controlled
handoff mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping


@dataclass(frozen=True, slots=True)
class EvolutionTolerance:
    """Independent gates for generation, test readiness, and switch approval."""

    generation_after: int = 3
    successful_tests_before_review: int = 2
    switch_score: float = 0.70

    def __post_init__(self) -> None:
        if self.generation_after < 1:
            raise ValueError("generation_after must be >= 1")
        if self.successful_tests_before_review < 1:
            raise ValueError("successful_tests_before_review must be >= 1")
        if not 0.0 <= self.switch_score <= 1.0:
            raise ValueError("switch_score must be between 0.0 and 1.0")


@dataclass(frozen=True, slots=True)
class EvolutionObservation:
    """A neutral observation emitted by Session 30's observation layer.

    The observation is descriptive. It intentionally carries no score or
    severity so the recording layer cannot silently become a judge.
    """

    observation_id: str
    kind: str
    description: str
    context: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, str) or not self.observation_id.strip():
            raise ValueError("observation_id must be non-empty")
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValueError("kind must be non-empty")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be non-empty")


@dataclass(frozen=True, slots=True)
class EvolutionCandidate:
    """Generated candidate source awaiting controlled verification."""

    candidate_id: str
    source: str
    based_on: tuple[str, ...]
    successful_test_runs: int = 0
    test_attempts: int = 0
    ready_for_review: bool = False


@dataclass(frozen=True, slots=True)
class SpecialistVote:
    """A specialist's assessment for the current evolution topic."""

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
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")

    @property
    def weight(self) -> float:
        return float(self.reliability) * float(self.relevance)


@dataclass(frozen=True, slots=True)
class EvolutionDecision:
    """Outcome of controlled review; it never changes the active runtime."""

    status: str
    candidate: EvolutionCandidate | None
    weighted_score: float | None
    votes_used: int
    reason: str


CodeGenerator = Callable[[tuple[EvolutionObservation, ...]], EvolutionCandidate]
CandidateTester = Callable[[EvolutionCandidate], bool]
VoteProvider = Callable[[EvolutionCandidate], Iterable[SpecialistVote]]


class EvolutionSession30:
    """Two-stage self-evolution supervisor for Session 30.

    Stage A is assumed to produce neutral observations. Stage B begins only
    after the observation-count tolerance is reached. A generated candidate
    must accumulate the configured number of *successful independent test
    runs* before voting is permitted. This second gate is intentionally
    independent from the observation threshold.
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
        """Store an observation without scoring, ranking, or judging it."""
        self._observations.append(observation)

    def generation_ready(self) -> bool:
        return len(self._observations) >= self.tolerance.generation_after

    def generate_candidate(self) -> EvolutionCandidate | None:
        """Generate a candidate only after the first tolerance is reached."""
        if not self.generation_ready():
            return None
        candidate = self._generator(tuple(self._observations))
        if not candidate.source.strip():
            raise ValueError("generated candidate source must be non-empty")
        self._candidate = candidate
        return candidate

    def review(self) -> EvolutionDecision:
        """Run one test attempt; vote only after the independent test gate passes."""
        if self._candidate is None:
            return EvolutionDecision(
                "WAIT_GENERATION", None, None, 0,
                "generation tolerance has not produced a candidate",
            )

        current = self._candidate
        passed = bool(self._tester(current))
        attempts = current.test_attempts + 1
        successful = current.successful_test_runs + int(passed)
        ready = successful >= self.tolerance.successful_tests_before_review
        self._candidate = EvolutionCandidate(
            candidate_id=current.candidate_id,
            source=current.source,
            based_on=current.based_on,
            successful_test_runs=successful,
            test_attempts=attempts,
            ready_for_review=ready,
        )

        if not passed:
            return EvolutionDecision(
                "REJECT_TEST", self._candidate, None, 0,
                "candidate failed the current independent test attempt",
            )

        if not ready:
            remaining = self.tolerance.successful_tests_before_review - successful
            return EvolutionDecision(
                "TESTING_PROGRESS", self._candidate, None, 0,
                f"candidate passed this test; {remaining} successful test run(s) remain before review",
            )

        votes = tuple(self._vote_provider(self._candidate))
        total_weight = sum(v.weight for v in votes)
        if total_weight <= 0.0:
            return EvolutionDecision(
                "REJECT_VOTE", self._candidate, None, len(votes),
                "no positive specialist weight is available",
            )

        weighted_score = sum(float(v.vote) * v.weight for v in votes) / total_weight
        if weighted_score >= self.tolerance.switch_score:
            return EvolutionDecision(
                "SWITCH_RECOMMENDED", self._candidate, weighted_score, len(votes),
                "candidate passed the test gate and reached the weighted vote threshold",
            )
        return EvolutionDecision(
            "RETAIN_CURRENT", self._candidate, weighted_score, len(votes),
            "candidate passed the test gate but did not reach the weighted vote threshold",
        )
