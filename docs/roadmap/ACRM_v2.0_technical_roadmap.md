# ACRM v2.0 Technical Roadmap

> Historical roadmap preserved as research documentation. It is not a statement that these features are implemented in ACRM v8.5.

## Stage 0 — Foundational Unconscious Bridge Architecture

The ACRM v2 research line now records a foundational architecture preceding the implementation-oriented roadmap below:

**Conscious Stream → Impasse Detector → Unconscious Bridge Layer → Final Output**

The Unconscious Bridge Layer contains three conceptual primitives:

1. **Synthesis Flow** — pattern morphing / reframing of candidate structures.
2. **Incubation Pool** — asynchronous background search following a soft mismatch.
3. **Integrity Gate** — coherence evaluation before a candidate is returned or rejected.

The complete originating artifact is preserved in [`docs/research/ACRM_FOUNDATIONAL_UNCONSCIOUS_BRIDGE_ARCHITECTURE.md`](../research/ACRM_FOUNDATIONAL_UNCONSCIOUS_BRIDGE_ARCHITECTURE.md).

### Why this is Stage 0

This architecture is treated as the **starting point of the corresponding research flow**, not as a claim that the mechanism already exists in the executable ACRM core. It provides the conceptual topology from which later specifications, contracts, prototypes, tests, and empirical evaluation can be derived.

Its research hypothesis is functional: an unconscious-like subsystem may be modeled as a processing bridge that becomes relevant when the conscious reasoning path reaches an impasse, performs synthesis/incubation/integrity evaluation, and returns either a coherent candidate or a rejection/clarification signal.

The terms used in this conceptual model must remain distinguishable from established biological mechanisms. In particular, the architecture does not by itself establish claims about human consciousness, unconsciousness, or any physical "frequency of consciousness."

### Foundational flow

```text
Prompt / Input
      ↓
Conscious Stream
      ↓
Impasse Detector
      ├── No Impasse ─────────────→ Standard Output
      │
      └── High Loss / Stuckness → Unconscious Bridge Layer
                                      ├─ Synthesis Flow
                                      ├─ Incubation Pool
                                      └─ Integrity Gate
                                                ↓
                                   Unconscious Output / Rejection
                                                ↓
                                           Final Output
```

### Evidence and implementation gate

Stage 0 is currently a **conceptual research artifact**. It must progress through explicit specification and testable contracts before any component is represented as an implemented ACRM capability:

```text
Foundational concept
        ↓
Formal specification
        ↓
Testable contract
        ↓
Prototype
        ↓
Implementation
        ↓
Software tests
        ↓
Empirical evaluation
```

The Stage 0 artifact also records its human–LLM collaborative provenance: the functional definition of the unconscious as a processing bridge was developed in the research dialogue and subsequently expressed as a system architecture with LLM assistance. Model-generated formalization is not independent scientific validation.

---

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

The Stage 0 foundational architecture is separately preserved as research provenance and is intentionally not retroactively represented as one of the six historical cylinders.
