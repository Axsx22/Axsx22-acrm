"""Session C: controlled self-evolution orchestration.

Session C is split into two deliberately separated responsibilities:

1. C-A / Observation: record factual runtime signals without scoring, judging,
   inferring, or deciding whether an evolution is needed.
2. C-B / Evolution: after an explicit observation tolerance is reached, obtain
   a candidate, test it independently, and only then collect topic-aware,
   reliability/relevance-weighted specialist votes.

Session C never mutates or executes the active runtime. A successful review
produces a switch recommendation for an external controlled handoff.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType
from typing import Callable, Iterable, Mapping

from ..session_c.observation import (
    EvolutionObservation,
    ObservationKind,
    ObservationLog,
)


@dataclass(frozen=True, slots=True)
class EvolutionTolerance:
    """Independent gates for candidate generation, testing, and review."""

    generation_after: int = 3
    successful_tests_before_review: int = 2
    switch_score: float = 0.70

    def __post_init__(self) -> None:
        if not isinstance(self.generation_after, int) or isinstance(self.generation_after, bool):
            raise TypeError("generation_after must be an integer")
        if self.generation_after < 1:
            raise ValueError("generation_after must be >= 1")
        if not isinstance(self.successful_tests_before_review, int) or isinstance(
            self.successful_tests_before_review, bool
        ):
            raise TypeError("successful_tests_before_review must be an integer")
        if self.successful_tests_before_review < 1:
            raise ValueError("successful_tests_before_review must be >= 1")
        if not isinstance(self.switch_score, (int, float)) or isinstance(self.switch_score, bool):
            raise TypeError("switch_score must be numeric")
        if not isfinite(float(self.switch_score)) or not 0.0 <= float(self.switch_score) <= 1.0:
            raise ValueError("switch_score must be finite and between 0.0 and 1.0")


@dataclass(frozen=True, slots=True)
class EvolutionCandidate:
    """Generated candidate source awaiting controlled verification."""

    candidate_id: str
    source: str
    based_on: tuple[str, ...]
    successful_test_runs: int = 0
    test_attempts: int = 0
    ready_for_review: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.candidate_id, str) or not self.candidate_id.strip():
            raise ValueError("candidate_id must be non-empty")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be non-empty")
        if not isinstance(self.based_on, tuple):
            raise TypeError("based_on must be a tuple")
        if self.successful_test_runs < 0 or self.test_attempts < 0:
            raise ValueError("test counters cannot be negative")
        if self.successful_test_runs > self.test_attempts:
            raise ValueError("successful_test_runs cannot exceed test_attempts")
        if not isinstance(self.ready_for_review, bool):
            raise TypeError("ready_for_review must be boolean")


@dataclass(frozen=True, slots=True)
class EvolutionContext:
    """Read-only snapshot of the current system/field context for voting."""

    topic: str
    state: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.topic, str) or not self.topic.strip():
            raise ValueError("topic must be non-empty")
        if not isinstance(self.state, Mapping):
            raise TypeError("state must be a mapping")
        object.__setattr__(self, "state", MappingProxyType(dict(self.state)))


@dataclass(frozen=True, slots=True)
class SpecialistVote:
    """A topic-specific assessment weighted by reliability and relevance."""

    specialist_id: str
    vote: float
    reliability: float
    relevance: float

    def __post_init__(self) -> None:
        if not isinstance(self.specialist_id, str) or not self.specialist_id.strip():
            raise ValueError("specialist_id must be non-empty")
        for name, value in (
            ("vote", self.vote),
            ("reliability", self.reliability),
            ("relevance", self.relevance),
        ):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be finite and between 0.0 and 1.0")

    @property
    def weight(self) -> float:
        return float(self.reliability) * float(self.relevance)


@dataclass(frozen=True, slots=True)
class EvolutionDecision:
    """Outcome of review; it never changes the active runtime."""

    status: str
    candidate: EvolutionCandidate | None
    weighted_score: float | None
    votes_used: int
    reason: str


CodeGenerator = Callable[[tuple[EvolutionObservation, ...]], EvolutionCandidate]
CandidateTester = Callable[[EvolutionCandidate], bool]
VoteProvider = Callable[[EvolutionCandidate, EvolutionContext], Iterable[SpecialistVote]]


class EvolutionSessionC:
    """Two-stage self-evolution supervisor with explicit safety gates."""

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
        self._observation_log = ObservationLog()
        self._candidate: EvolutionCandidate | None = None
        self._review_complete = False

    @property
    def observations(self) -> tuple[EvolutionObservation, ...]:
        return self._observation_log.snapshot()

    @property
    def candidate(self) -> EvolutionCandidate | None:
        return self._candidate

    @property
    def review_complete(self) -> bool:
        return self._review_complete

    def record(self, observation: EvolutionObservation) -> None:
        """C-A: record a neutral observation; never score or judge it."""
        if self._review_complete:
            raise RuntimeError("review cycle is complete; start a new Session C cycle")
        self._observation_log.record(observation)

    def generation_ready(self) -> bool:
        """Return whether the first explicit observation tolerance is reached."""
        return len(self.observations) >= self.tolerance.generation_after

    def generate_candidate(self) -> EvolutionCandidate | None:
        """C-B: cross the first tolerance and create one pending candidate."""
        if self._candidate is not None:
            return self._candidate
        if not self.generation_ready():
            return None
        candidate = self._generator(self.observations)
        if not isinstance(candidate, EvolutionCandidate):
            raise TypeError("generator must return an EvolutionCandidate")
        self._candidate = candidate
        return candidate

    def review(self, context: EvolutionContext) -> EvolutionDecision:
        """Test first; only after the test gate, collect weighted topic votes."""
        if not isinstance(context, EvolutionContext):
            raise TypeError("context must be an EvolutionContext")
        if self._candidate is None:
            return EvolutionDecision(
                "WAIT_GENERATION", None, None, 0,
                "generation tolerance has not produced a candidate",
            )
        if self._review_complete:
            return EvolutionDecision(
                "REVIEW_COMPLETE", self._candidate, None, 0,
                "review has already completed for this Session C cycle",
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

        votes = tuple(self._vote_provider(self._candidate, context))
        total_weight = sum(v.weight for v in votes)
        if total_weight <= 0.0:
            self._review_complete = True
            return EvolutionDecision(
                "REJECT_VOTE", self._candidate, None, len(votes),
                "no positive specialist weight is available for the current topic",
            )

        weighted_score = sum(float(v.vote) * v.weight for v in votes) / total_weight
        self._review_complete = True
        if weighted_score >= self.tolerance.switch_score:
            return EvolutionDecision(
                "SWITCH_RECOMMENDED", self._candidate, weighted_score, len(votes),
                "candidate passed the test gate and reached the weighted topic-aware vote threshold",
            )
        return EvolutionDecision(
            "RETAIN_CURRENT", self._candidate, weighted_score, len(votes),
            "candidate passed the test gate but did not reach the weighted topic-aware vote threshold",
        )


# Deliberately no runtime switch/execution API is exposed here. The active
# runtime remains outside Session C and consumes only an explicit handoff
# decision from a separate controlled mechanism.
