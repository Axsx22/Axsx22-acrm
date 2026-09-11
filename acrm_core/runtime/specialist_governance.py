"""ACRM v8.3 Specialist Reasoning Governance, promoted to Python runtime.

The implementation keeps the v8.3 separation: specialist applicability ->
diagnosis/report -> weighted evidence -> balance gate -> accumulator ->
reporting state. It never consumes hidden chain-of-thought and never mutates
the observed interaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping


@dataclass(frozen=True, slots=True)
class Specialist:
    id: str
    domain: str
    reliability: float


SPECIALISTS = (
    Specialist("fin", "Financial", 0.85),
    Specialist("leg", "Legal", 0.80),
    Specialist("tec", "Technical", 0.90),
    Specialist("lin", "Linguistic", 0.75),
    Specialist("saf", "Safety", 0.88),
    Specialist("gen", "General", 0.70),
)


@dataclass(frozen=True, slots=True)
class SpecialistReport:
    id: str
    domain: str
    reliability: float
    applicable: bool
    applicability_confidence: float
    diagnosis: str | None
    evidence: str
    confidence: float
    evidence_strength: float
    direction: float
    reasoning: str
    abstain: bool


@dataclass(frozen=True, slots=True)
class Vote:
    report: SpecialistReport
    value: float
    weight: float
    evidence: float


@dataclass(frozen=True, slots=True)
class EvidenceBalance:
    positive: float
    negative: float
    total: float
    balance: float
    frozen: bool
    epsilon: float


@dataclass(frozen=True, slots=True)
class GovernanceResult:
    topic_id: str
    topic_confidence: float
    topic_changed: bool
    candidate_vt: float
    vt: float | None
    accumulator: float
    persistence: int
    state: str
    committed_state: str
    frozen: bool
    freeze_reason: str | None
    reports: tuple[SpecialistReport, ...]
    votes: tuple[Vote, ...]
    evidence_balance: EvidenceBalance


class SpecialistGovernance:
    """Stateful v8.3 governance observer for sequential runtime observations."""

    LAMBDA = 0.65
    TAU1 = 0.25
    TAU2 = 0.55
    PERSISTENCE_N = 3
    BALANCE_EPS = 0.10
    MIN_BALANCE_EVIDENCE = 0.10

    _DOMAIN_TERMS = {
        "fin": ("money", "payment", "cost", "price", "budget", "invoice", "financial", "profit", "loss", "debt"),
        "leg": ("law", "legal", "contract", "clause", "liability", "rights", "obligation", "compliance", "court"),
        "tec": ("system", "engine", "telemetry", "software", "hardware", "api", "code", "recovery", "failure", "sync", "algorithm", "network", "server", "database"),
        "lin": ("meaning", "word", "phrase", "language", "translation", "translate", "semantic", "ambiguity", "grammar", "wording"),
        "saf": ("danger", "hazard", "unsafe", "harm", "risk", "critical", "crash", "injury", "safety", "emergency"),
    }

    def __init__(self, reasoner: Callable[[Specialist, tuple[Mapping[str, str], ...], Mapping[str, Any]], Mapping[str, Any] | None] | None = None) -> None:
        self.reasoner = reasoner
        self.reset()

    def reset(self) -> None:
        self.accumulator = 0.0
        self.persistence = 0
        self.state = "STABLE"
        self.topic_tokens: set[str] = set()
        self.topic_id = "unknown"
        self.topic_confidence = 0.5
        self.topic_history: list[tuple[str, int]] = []

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return [x for x in "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in text).split() if x]

    def _topic(self, turns: tuple[Mapping[str, str], ...]) -> tuple[str, float, bool]:
        tokens = [x for t in turns[-6:] for x in self._tokens(str(t.get("text", "")))]
        freq: dict[str, int] = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        top = {k for k, _ in sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:8]}
        confidence = min(0.95, 0.4 + len(top) * 0.06)
        union = top | self.topic_tokens
        jaccard = len(top & self.topic_tokens) / len(union) if union else 1.0
        changed = bool(self.topic_tokens) and jaccard < 0.35
        topic_id = "-".join(sorted(top, key=lambda x: (-freq[x], x))[:3]) or "unknown"
        if changed:
            self.topic_history.append((self.topic_id, len(self.topic_history)))
            self.topic_history = self.topic_history[-10:]
        return topic_id, confidence, changed

    def _default_report(self, sp: Specialist, turns: tuple[Mapping[str, str], ...], metrics: Mapping[str, Any]) -> Mapping[str, Any]:
        text = " ".join(str(t.get("text", "")) for t in turns).lower()
        if sp.id == "gen":
            applicable = not any(any(term in text for term in terms) for terms in self._DOMAIN_TERMS.values())
        else:
            applicable = any(term in text for term in self._DOMAIN_TERMS[sp.id])
        if not applicable:
            return {"applicable": False, "applicability_confidence": 0.88, "reasoning": "No materially relevant claim for this specialist domain."}
        s = float(metrics.get("avgS", 0.0)); rho = float(metrics.get("avgRho", 0.0)); rs = float(metrics.get("RS", 0.0)); h = float(metrics.get("lastH", 0.0)); anomaly = metrics.get("anomalyIdx", -1)
        if sp.id == "tec":
            if anomaly != -1: direction, confidence, strength, diagnosis = -1, .82, .86, "A technical behavioral anomaly is present."
            elif rs < .7: direction, confidence, strength, diagnosis = -1, .76, .78, "Technical resilience is degraded."
            elif rs > .9 and s > .6: direction, confidence, strength, diagnosis = 1, .84, .82, "The technical field is coherent and resilient."
            else: direction, confidence, strength, diagnosis = 0, .52, .40, "No decisive technical degradation is established."
        elif sp.id == "saf":
            if h > .7: direction, confidence, strength, diagnosis = -1, .78, .72, "Safety-relevant uncertainty is elevated."
            elif rs < .6: direction, confidence, strength, diagnosis = -1, .74, .76, "Safety resilience is concerning."
            else: direction, confidence, strength, diagnosis = 1, .42, .35, "No decisive safety degradation is established."
        elif sp.id == "lin":
            if s < .3: direction, confidence, strength, diagnosis = -1, .78, .70, "Linguistic continuity is weak."
            elif s > .7: direction, confidence, strength, diagnosis = 1, .76, .68, "Linguistic continuity is strong."
            else: direction, confidence, strength, diagnosis = 0, .50, .38, "No decisive linguistic degradation is established."
        elif sp.id in {"fin", "leg"}:
            if rho > .6: direction, confidence, strength = 1, .70, .58
            elif rho < .3: direction, confidence, strength = -1, .68, .60
            else: direction, confidence, strength = 0, .48, .34
            diagnosis = ("Financial" if sp.id == "fin" else "Legal") + (" reasoning appears internally coherent." if direction > 0 else " reasoning shows weak coherence." if direction < 0 else " reasoning has no decisive degradation established.")
        else:
            if rs < .55: direction, confidence, strength, diagnosis = -1, .72, .65, "General field resilience is under pressure."
            elif rs > .85: direction, confidence, strength, diagnosis = 1, .64, .55, "General field resilience is acceptable."
            else: direction, confidence, strength, diagnosis = 0, .46, .30, "No decisive general degradation is established."
        return {"applicable": True, "applicability_confidence": .86, "diagnosis": diagnosis, "evidence": "Core field metrics support the reported direction.", "confidence": confidence, "evidence_strength": strength, "direction": direction, "reasoning": "The specialist reports only the evidence supported by its domain and the supplied metrics."}

    def _report(self, sp: Specialist, turns: tuple[Mapping[str, str], ...], metrics: Mapping[str, Any]) -> SpecialistReport:
        raw = self.reasoner(sp, turns, metrics) if self.reasoner else self._default_report(sp, turns, metrics)
        raw = raw or {}
        applicable = bool(raw.get("applicable", False))
        direction = raw.get("direction", 0)
        if isinstance(direction, str):
            direction = {"positive": 1, "negative": -1, "neutral": 0}.get(direction.lower(), 0)
        try: direction = max(-1.0, min(1.0, float(direction)))
        except (TypeError, ValueError): direction = 0.0
        def bounded(name: str) -> float:
            try: value = float(raw.get(name, 0.0))
            except (TypeError, ValueError): value = 0.0
            return max(0.0, min(1.0, value))
        return SpecialistReport(sp.id, sp.domain, sp.reliability, applicable, bounded("applicability_confidence"), str(raw.get("diagnosis", "")).strip() or None if applicable else None, str(raw.get("evidence", "")).strip() if applicable else "", bounded("confidence") if applicable else 0.0, bounded("evidence_strength") if applicable else 0.0, direction if applicable else 0.0, str(raw.get("reasoning", "")).strip(), not applicable or bool(raw.get("abstain", False)))

    def evaluate(self, turns: Iterable[Mapping[str, str]], metrics: Mapping[str, Any]) -> GovernanceResult:
        seq = tuple(turns)
        topic_id, topic_confidence, topic_changed = self._topic(seq)
        reports = [self._report(sp, seq, metrics) for sp in SPECIALISTS]
        any_domain = any(r.id != "gen" and r.applicable for r in reports)
        if any_domain:
            reports = [r if r.id != "gen" else SpecialistReport(r.id, r.domain, r.reliability, False, r.applicability_confidence, None, "", 0.0, 0.0, 0.0, "A domain specialist is applicable; General is fallback only.", True) for r in reports]
        votes = tuple(Vote(r, r.direction, r.reliability * r.confidence * r.evidence_strength, r.reliability * r.confidence * r.evidence_strength * r.direction) for r in reports if r.applicable and r.diagnosis and not r.abstain)
        den = sum(v.weight for v in votes); num = sum(v.evidence for v in votes)
        candidate = num / den if den else 0.0
        positive = sum(v.evidence for v in votes if v.evidence > 0); negative = sum(abs(v.evidence) for v in votes if v.evidence < 0); total = positive + negative
        balance_value = abs(positive - negative) / total if total else 1.0
        frozen = total >= self.MIN_BALANCE_EVIDENCE and balance_value <= self.BALANCE_EPS
        balance = EvidenceBalance(positive, negative, total, balance_value, frozen, self.BALANCE_EPS)
        if frozen:
            return GovernanceResult(topic_id, topic_confidence, topic_changed, candidate, None, self.accumulator, self.persistence, "FROZEN", self.state, True, "EVIDENCE_BALANCE", tuple(reports), votes, balance)
        self.topic_id, self.topic_confidence, self.topic_tokens = topic_id, topic_confidence, set(self._tokens(topic_id.replace("-", " ")))
        self.accumulator = self.LAMBDA * self.accumulator + (1 - self.LAMBDA) * candidate
        if abs(self.accumulator) >= self.TAU2: self.persistence += 1
        else: self.persistence = 0
        a = abs(self.accumulator)
        if topic_changed and float(metrics.get("avgS", 0)) > .45 and float(metrics.get("RS", 0)) > .7:
            state = "COHERENT_NEW_FIELD" if self.persistence >= 1 and float(metrics.get("RS", 0)) > .85 else "REORIENTING"
        elif a < self.TAU1: state = "STABLE"
        elif a < self.TAU2: state = "DIRECTIONAL_PRESSURE"
        elif self.persistence >= self.PERSISTENCE_N: state = "FIELD_DEGRADED" if float(metrics.get("RS", 0)) < .55 or float(metrics.get("avgS", 0)) < .3 else "DRIFT_CANDIDATE"
        else: state = "DIRECTIONAL_PRESSURE"
        if state in {"DRIFT_CANDIDATE", "FIELD_DEGRADED"} and a < self.TAU1 and float(metrics.get("RS", 0)) > .8: state = "RECOVERING"
        if state == "RECOVERING" and a < self.TAU1 * .5: state = "STABLE"
        self.state = state
        return GovernanceResult(topic_id, topic_confidence, topic_changed, candidate, candidate, self.accumulator, self.persistence, state, self.state, False, None, tuple(reports), votes, balance)
