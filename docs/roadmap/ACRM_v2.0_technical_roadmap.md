# ACRM v2.0 Technical Roadmap

> Historical roadmap preserved as research documentation. It is not a statement that these features are implemented in ACRM v8.5.

The supplied roadmap describes six inactive cylinders from the v1.3 research prototype:

1. **C1 — ARQ Integration into Arbitration** — proposed as critical; requires live ARQ data, correlation analysis, threshold calibration, and false-positive analysis.
2. **C2 — Oscillation Detection** — proposed as high impact; requires sequential status logs and calibration of the oscillation threshold.
3. **C3 — Temporal Decay for Counters** — proposed as high impact; requires timestamp data, session-length information, and empirical signal half-life.
4. **C4 — Adaptive Thresholds** — proposed as high impact; depends on earlier cylinders plus per-session context labels and sufficient observations by task type.
5. **C5 — Multi-Signal Fusion** — proposed as medium impact; requires labeled outcomes and calibration of signal weights.
6. **C6 — Bounded History with Sliding Window** — proposed as medium impact and described as immediately activatable without external data.

## Version gates in the source roadmap

| Version | Roadmap status |
| --- | --- |
| v1.3 | 3/6 active; stable research prototype baseline |
| v1.5 | 4/6 active; C6 merged and C2 activated from episode logs |
| v2.0-beta | 5/6 active; ARQ and temporal decay integrated with validation |
| v2.0 | 6/6 active; multi-signal fusion calibrated on labeled outcomes |

These are historical roadmap targets. The repository must not infer implementation status from this document alone.

## Traceability

The original source states that the document was generated from analysis of the ACRM v1.3 stable research prototype and identifies live log collection schema design as the next phase.
