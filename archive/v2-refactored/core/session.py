"""
Session Isolation Manager — Refactored v2.0
Contract: sessions are isolated; handoff preserves state with decay.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class SessionState:
    """Immutable-by-convention session snapshot."""
    ema: float
    confidence: float
    osc_count: int = 0


class SessionIsolationManager:
    """
    Manages isolated session states.

    Invariant: sessions do not share mutable state.
    """

    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}

    def create_session(self, session_id: str):
        if session_id in self.sessions:
            raise ValueError(f"Session {session_id} already exists")
        self.sessions[session_id] = SessionState(ema=0.5, confidence=0.0)

    def get(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        return self.sessions[session_id]

    def update(self, session_id: str, ema: float, confidence: float):
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        self.sessions[session_id] = SessionState(
            ema=ema,
            confidence=confidence,
            osc_count=self.sessions[session_id].osc_count
        )

    def handoff(self, from_session: str, to_session: str):
        """
        Transfer state between sessions with confidence decay.
        Contract: confidence decays by 20% on handoff (information loss).
        """
        source = self.get(from_session)
        self.sessions[to_session] = SessionState(
            ema=source.ema,
            confidence=source.confidence * 0.8,
            osc_count=0
        )
