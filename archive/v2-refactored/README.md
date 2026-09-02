# ACRM v2.0 — Refactored Archive

**Location:** `archive/v2-refactored/`  
**Status:** Research Archive (not current runtime)  
**Current Runtime:** See `acrm_core/field/state.py` (v8.5)

## Purpose

This directory preserves the v2.0 implementation of ACRM's distributed monitoring and consensus layer, refactored to align with the v8.5 contract discipline.

## Changes from Original v2.0

| Component | Original Issue | Refactored Fix |
|---|---|---|
| RecoveryGate | Arbitrary counter reset | Evidence-based history check |
| AdaptiveEMATracker | No overflow guard | Finite output contract |
| GlobalConsensus | Arbitrary penalty (0.2) | Evidence-based stability factor |
| All modules | No input validation | Comprehensive validation |

## Structure

```
core/
  tracker.py      — Confidence-weighted EMA
  gate.py         — State machine with evidence
  session.py      — Session isolation
  cluster.py      — Multi-node cluster
  consensus.py    — Global consensus
  fault.py        — Fault tolerance
  audit.py        — Audit scoring
  stats.py        — Statistical testing
test/
  test_core.py    — Contract-focused tests
```

## Running Tests

```bash
cd archive/v2-refactored
python -m pytest test/ -v
```

## Evidence Boundary

This code is a **research artifact**. It demonstrates architectural concepts explored during ACRM's evolution. It is not part of the current v8.5 runtime and should not be interpreted as production software.
