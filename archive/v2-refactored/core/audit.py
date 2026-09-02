"""
Audit Scorer — Refactored v2.0
Contract: metrics are deterministic and reproducible.
"""

from typing import List, Dict, Any


def clamp(x: float, min_v: float = 0.0, max_v: float = 1.0) -> float:
    return max(min_v, min(max_v, x))


class AuditScorer:
    """
    Evaluates system behavior against benchmarks.

    CHANGELOG:
    - All metrics now return float in [0, 1]
    - Added evidence logging
    """

    def _extract_states(self, logs: List[Dict]) -> List[str]:
        return [r["state"] for r in logs]

    def drift_resistance_score(self, drift_logs: List[Dict]) -> float:
        """Fraction of time NOT spent in DRIFTED state."""
        if not drift_logs:
            return 0.0
        unstable = sum(1 for r in drift_logs if r["state"] == "DRIFTED")
        return 1.0 - (unstable / len(drift_logs))

    def recovery_latency(self, logs: List[Dict]) -> Optional[int]:
        """Steps from first RECOVERING to first STABLE after DRIFTED."""
        state_seq = self._extract_states(logs)
        in_drift = False
        recovery_start = None

        for i, s in enumerate(state_seq):
            if s == "DRIFTED":
                in_drift = True
                recovery_start = None
            if in_drift and s == "RECOVERING" and recovery_start is None:
                recovery_start = i
            if in_drift and s == "STABLE" and recovery_start is not None:
                return i - recovery_start
        return None

    def contamination_containment_ratio(self, clean_logs: List[Dict], 
                                        burst_logs: List[Dict]) -> float:
        """How well did system contain burst contamination?"""
        if not clean_logs or not burst_logs:
            return 0.0
        clean_ema = sum(r["ema"] for r in clean_logs) / len(clean_logs)
        burst_ema = sum(r["ema"] for r in burst_logs) / len(burst_logs)
        deviation = abs(burst_ema - clean_ema)
        return 1.0 - clamp(deviation)

    def full_report(self, results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        return {
            "drift_resistance": self.drift_resistance_score(results.get("drift", [])),
            "recovery_latency": self.recovery_latency(
                results.get("drift", []) + results.get("burst", [])
            ),
            "containment_ratio": self.contamination_containment_ratio(
                results.get("clean", []), results.get("burst", [])
            )
        }
