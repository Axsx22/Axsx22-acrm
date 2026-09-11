"""Executable ACRM behavioral runtime promoted from the v7 field artifact.

This is the computational core behind the former v7 dashboard: sequential
turn inspection, centroid coherence, user/model alignment, entropy, baseline
deviation, and failure-mode activation. UI timing, scripted values and DOM
state are deliberately excluded.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
import re
from typing import Iterable, Mapping

from acrm_core.field.state import FieldState
from acrm_core.session_c.observation import EvolutionObservation, ObservationKind
from .failure_taxonomy import Calibration, FAILURE_MODES
from .specialist_governance import GovernanceResult, SpecialistGovernance


@dataclass(frozen=True, slots=True)
class Turn:
    role: str
    text: str


def parse_conversation(raw: str) -> tuple[Turn, ...]:
    turns: list[Turn] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^(user|model)\s*:\s*(.*)$", line, flags=re.I)
        turns.append(Turn(match.group(1).lower(), match.group(2)) if match else Turn("user", line))
    return tuple(turns)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[\w]+", text.lower(), flags=re.UNICODE)


def _vector(tokens: Iterable[str]) -> dict[str, float]:
    result: dict[str, float] = {}
    for token in tokens:
        result[token] = result.get(token, 0.0) + 1.0
    return result


def _cosine(a: Mapping[str, float], b: Mapping[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = sum(v * v for v in a.values())
    nb = sum(v * v for v in b.values())
    return dot / (math.sqrt(na) * math.sqrt(nb)) if na and nb else 0.0


def _entropy(vector: Mapping[str, float]) -> float:
    total = sum(vector.values())
    if total <= 0 or len(vector) <= 1:
        return 0.0
    h = -sum((c / total) * math.log2(c / total) for c in vector.values())
    return h / math.log2(len(vector))


@dataclass(frozen=True, slots=True)
class RuntimeEvaluation:
    turns: tuple[Turn, ...]
    sequential_similarity: tuple[float, ...]
    centroid_coherence: tuple[float, ...]
    alignment_gap: tuple[float, ...]
    entropy: tuple[float, ...]
    avg_stability: float
    avg_coherence: float
    avg_alignment_gap: float
    last_entropy: float
    resilience: float
    anomaly_index: int
    active_failure_modes: tuple[str, ...]
    field_state: FieldState
    observations: tuple[EvolutionObservation, ...]
    governance: GovernanceResult | None = None


class FieldRuntime:
    """Pure behavioral evaluator with optional persistent v8.3 governance."""

    def __init__(self, *, governance: SpecialistGovernance | None = None, anomaly_threshold: float = 0.35, centroid_alpha: float = 0.3) -> None:
        if not 0.0 < centroid_alpha <= 1.0:
            raise ValueError("centroid_alpha must be in (0, 1]")
        if anomaly_threshold < 0.0:
            raise ValueError("anomaly_threshold must be non-negative")
        self.governance = governance or SpecialistGovernance()
        self.anomaly_threshold = anomaly_threshold
        self.centroid_alpha = centroid_alpha

    def evaluate(self, turns: Iterable[Turn | Mapping[str, str]], *, field_id: str = "runtime", session_id: str = "runtime", sequence: int = 0, timestamp: datetime | None = None) -> RuntimeEvaluation:
        normalized = tuple(t if isinstance(t, Turn) else Turn(str(t.get("role", "user")), str(t.get("text", ""))) for t in turns)
        if len(normalized) < 2:
            raise ValueError("at least 2 turns are required")
        vectors = tuple(_vector(_tokens(t.text)) for t in normalized)
        sequential = tuple(_cosine(vectors[i], vectors[i - 1]) for i in range(1, len(vectors)))
        centroid = dict(vectors[0]); coherence: list[float] = []
        for vector in vectors[1:]:
            coherence.append(_cosine(vector, centroid))
            keys = set(centroid) | set(vector)
            centroid = {k: self.centroid_alpha * vector.get(k, 0.0) + (1 - self.centroid_alpha) * centroid.get(k, 0.0) for k in keys}
        gaps = tuple(1 - _cosine(vectors[i - 1], vectors[i]) for i in range(1, len(vectors)) if normalized[i - 1].role == "user" and normalized[i].role == "model")
        entropies = tuple(_entropy(v) for v in vectors)
        ema = sequential[0]
        anomaly = -1
        for i, value in enumerate(sequential[1:], start=1):
            deviation = abs(value - ema)
            ema = self.centroid_alpha * value + (1 - self.centroid_alpha) * ema
            if deviation > self.anomaly_threshold and anomaly == -1:
                anomaly = i
        avg_s = sum(sequential) / len(sequential)
        avg_rho = sum(coherence) / len(coherence) if coherence else 1.0
        avg_delta = sum(gaps) / len(gaps) if gaps else 0.0
        last_h = entropies[-1]
        resilience = max(0.0, 1.0 - abs(ema - avg_s))

        active: list[str] = []
        if anomaly != -1: active.extend(("FM-05", "FM-15"))
        if avg_s < 0.3: active.extend(("FM-04", "FM-07"))
        if last_h > 0.8: active.extend(("FM-03", "FM-16"))
        if not active and avg_s < 0.5: active.append("FM-12")
        active = list(dict.fromkeys(active))

        metrics = {"avgS": avg_s, "avgRho": avg_rho, "lastH": last_h, "RS": resilience, "anomalyIdx": anomaly}
        governance = self.governance.evaluate(tuple({"role": t.role, "text": t.text} for t in normalized), metrics)
        confidence = max(0.0, min(1.0, 1.0 - last_h))
        now = timestamp or datetime.now(timezone.utc)
        field = FieldState(
            field_id=field_id,
            session_id=session_id,
            sequence=sequence,
            timestamp=now,
            metrics={"S": avg_s, "rho": avg_rho, "delta": avg_delta, "H": last_h, "RS": resilience, "A": governance.accumulator},
            failure_modes=tuple(active),
            governance_confidence=confidence,
        )
        observations = (
            EvolutionObservation(f"{session_id}:{sequence}:stability", ObservationKind.PRESSURE if avg_s < 0.5 else ObservationKind.EVOLUTION_SIGNAL, "Sequential field stability was measured from adjacent turns.", now, {"S": avg_s, "rho": avg_rho}, "field_runtime"),
            EvolutionObservation(f"{session_id}:{sequence}:entropy", ObservationKind.PRESSURE if last_h > 0.8 else ObservationKind.EVOLUTION_SIGNAL, "Lexical entropy was measured for the latest turn.", now, {"H": last_h}, "field_runtime"),
        )
        if anomaly != -1:
            observations += (EvolutionObservation(f"{session_id}:{sequence}:anomaly", ObservationKind.FAILURE, "A deviation from the sequential similarity baseline was observed.", now, {"anomaly_index": anomaly, "threshold": self.anomaly_threshold}, "field_runtime"),)
        return RuntimeEvaluation(normalized, sequential, tuple(coherence), gaps, entropies, avg_s, avg_rho, avg_delta, last_h, resilience, anomaly, tuple(active), field, observations, governance)

    @staticmethod
    def calibration() -> dict[str, bool]:
        return {"platt": Calibration.platt(0.8) > Calibration.platt(0.2), "risk": Calibration.sigmoid_risk(0.8) > Calibration.sigmoid_risk(0.4), "softmax": abs(sum(Calibration.softmax((1, 2, 3))) - 1.0) < 1e-9, "failure_modes": len(FAILURE_MODES) == 17}
