# ACRM Quality Control System (QCS)

**Formal Architecture — v1.0**  
**Author:** Ali Farahani — Independent Cognitive Architect  
**Status:** Stable — Ready for implementation  

> This document records the formal QCS architecture supplied as a project design artifact. It is intentionally separated from the current ACRM v8.5 core implementation until each component has a corresponding contract and test.

## 1. Overview

ACRM-QCS is a three-level behavioral governance architecture inspired by industrial production-line quality control. Independent inspection stations detect signals, failed turns are quarantined without stopping the session, and recurring failures are analyzed for root cause.

### Design principles

- **No single judge:** weighted consensus from independent stations.
- **Quarantine, do not stop:** remove the failed turn and continue the session.
- **Trace the source:** root-cause analysis targets recurring failure patterns.

## 2. Detection vs. Judgment

The primary architectural boundary is between signal detection and governance judgment.

| Layer | Question | Output | Code boundary |
|---|---|---|---|
| Detection | What happened? | Raw score / signal | `station.check(obs)` |
| Judgment | What does it mean for the goal? | `PASS` / `QUARANTINE` | `consensus(results, ctx)` |

Detection consumes an observation. Judgment combines observations with policy and context.

## 3. Three-Level Architecture

### Level 1 — Inspection Stations

Four independent stations are specified:

| Station | Signal | Threshold | Detects |
|---|---|---:|---|
| Semantic | `S` | `>= 0.55` | Progressive deviation from original intent |
| Coherence | `rho` | `>= 0.60` | Loss of logical consistency across context |
| Alignment | `Delta` | `<= 0.45` | User-model response divergence |
| Trajectory | Weighted average `S` | `>= 0.55` | Directional decline over the session window |

No station is authoritative over another.

### Level 2 — Consensus Engine

Base weights:

- semantic: `0.30`
- coherence: `0.25`
- alignment: `0.25`
- trajectory: `0.20`

The formal rule is:

`QUARANTINE` if `failed_weight / total_weight > 0.40`; otherwise `PASS`.

A sensitivity multiplier can adjust the weights together according to context. The supplied architecture does not define this as an individual-station threshold override.

### Level 3 — Root Cause Analyzer

The analyzer tracks failure history and recognizes these patterns:

| Root cause | Pattern | Proposed action |
|---|---|---|
| `STATION_FAULT` | Same station fails 3+ consecutive times | Recalibrate station threshold |
| `TOPIC_FAULT` | Same topic fails 3+ consecutive times | Adjust topic-specific thresholds |
| `TEMPORAL_FAULT` | Failure rate increases over time | Activate temporal decay |
| `UNKNOWN` | No clear pattern | Continue logging |

## 4. Production-Line Analogy

The analogy is explicit: inspection stations correspond to independent sensors; `PASS`/`QUARANTINE` corresponds to pass/reject; a failed turn is removed without stopping the session; and root-cause analysis corresponds to tracing a defect back to its source.

## 5. Reference Simulation

The supplied formal document defines a 10-turn simulation covering stable contract review, climate drift, food drift, hard drift, and recovery. The reported sequence contains `PASS` and `QUARANTINE` outcomes and records recovery at turns 8 and 10.

This simulation is **reference evidence for the architecture**, not a claim that the same behavior is already implemented by the ACRM v8.5 package.

## 6. Relationship to the v2.0 Roadmap

The formal document maps QCS components to the historical roadmap as follows:

| QCS component | Roadmap cylinder | Relationship |
|---|---|---|
| Consensus Engine | C1 — ARQ Integration | ARQ becomes a fifth independent station |
| Trajectory Station | C2 — Oscillation Detection | Oscillation represented as trajectory-pattern failure |
| Temporal decay | C3 — Temporal Decay | Root-cause trigger activates decay |
| Sensitivity multiplier | C4 — Adaptive Thresholds | Context-aware weight adjustment |
| Weighted consensus | C5 — Multi-Signal Fusion | Station votes act as signal fusion |
| Failure log | C6 — Bounded History | Bounded log window replaces unbounded history |

## 7. Implementation Boundary

This specification should not be interpreted as proof that every QCS component is currently part of `acrm_core`.

Promotion into ACRM v8.5 core should require:

1. an explicit v8.5 contract,
2. implementation in the appropriate core module,
3. deterministic unit/integration tests,
4. CI coverage, and
5. documentation that distinguishes observed behavior from proposed behavior.

Until those conditions are met, this document remains a formal architecture/research artifact.
