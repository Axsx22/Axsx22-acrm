"""
ACRM v2.0 — Refactored Archive
==============================
Preserved from historical implementation and refactored to align with v8.5 contract discipline.

This is a RESEARCH ARCHIVE, not the current runtime.
See acrm_core/field/state.py for the current v8.5 contract.
"""

from .tracker import AdaptiveEMATracker, TrackerConfig
from .gate import RecoveryGate
from .session import SessionIsolationManager, SessionState
from .cluster import MultiNodeACRMCluster, EventBus, ACRMNode
from .consensus import GlobalConsensusLayer
from .fault import FaultToleranceManager, HeartbeatMonitor, CheckpointManager, StateSnapshot
from .audit import AuditScorer
from .stats import StatisticalSignificanceTester

__all__ = [
    "AdaptiveEMATracker", "TrackerConfig",
    "RecoveryGate",
    "SessionIsolationManager", "SessionState",
    "MultiNodeACRMCluster", "EventBus", "ACRMNode",
    "GlobalConsensusLayer",
    "FaultToleranceManager", "HeartbeatMonitor", "CheckpointManager", "StateSnapshot",
    "AuditScorer",
    "StatisticalSignificanceTester",
]
