# ACRM — Adaptive Cognitive Regulation Module

**An independent, research-oriented architecture for studying observable, evaluable, and governable behavior in LLM-based cognitive systems.**

ACRM is designed and developed by **Ali Farahani**, independent AI researcher and system architect, as part of a broader human–LLM collaborative research program.

> **Repository principle:** ACRM did not begin as a fully specified engineering system. Its architecture emerged iteratively through observation, questioning, hypothesis formation, interaction with multiple LLMs, architectural experimentation, implementation, testing, and revision. This repository therefore preserves artifacts from different stages of that evolution while maintaining an explicit boundary between historical research, conceptual architecture, implemented software, and future work.

---

## 1. What is ACRM?

ACRM (Adaptive Cognitive Regulation Module) is a research architecture concerned with how an LLM-based cognitive system can represent, observe, evaluate, and govern evolving system state and behavior over time.

The central research question is:

> **How can an LLM-based cognitive system remain observable, evaluable, and governable as its state, behavior, interactions, and internal processes evolve over time?**

The research connects several areas:

- LLM behavior and long-running interaction;
- cognitive-system architecture;
- state representation and temporal change;
- observability and evaluation;
- governance and controlled system evolution;
- human–LLM collaborative system design.

ACRM should therefore be understood as an evolving architectural research program, not as a claim that every concept described in its history is already implemented.

---

## 2. Architectural provenance and origin

### System designer

**Ali Farahani** is the system architect and researcher responsible for the architectural direction, integration, research framing, evaluation strategy, and final system-level decisions.

### How the architecture emerged

ACRM was not designed top-down from a complete initial specification. It emerged through a long-running empirical and collaborative process in which observations generated questions, questions generated hypotheses, and repeated interaction with multiple LLMs was used to examine, challenge, compare, and reformulate possible solutions.

A simplified representation of that process is:

```text
Observation
    ↓
Question
    ↓
Hypothesis
    ↓
Concept / Model
    ↓
Architectural proposal
    ↓
Prototype / Implementation
    ↓
Experiment / Test
    ↓
Observation
    ↓
Revision
    ↓
New architectural state
```

Multiple LLMs participated as analytical collaborators: ideas and interpretations could be compared across models, and model-generated critiques could themselves become inputs to further analysis. The human architect remained the common integration point and retained responsibility for architectural decisions.

### Formation conditions

The early research was conducted independently and under constrained practical conditions, using consumer hardware and extensive direct interaction with LLMs rather than a conventional academic laboratory or institutional engineering team. These conditions are recorded as part of the architecture's provenance; they are **not** presented as evidence of technical or scientific validity.

Historical research records are preserved because they explain how architectural questions and decisions emerged. They should not be confused with the current implementation specification.

---

## 3. Architectural lifecycle and evidence boundary

The repository uses an explicit distinction between stages of architectural maturity:

```text
Historical observation
        ↓
Research question
        ↓
Hypothesis
        ↓
Conceptual architecture
        ↓
Testable specification / contract
        ↓
Implementation
        ↓
Software testing
        ↓
Empirical evaluation
        ↓
Independent reproduction
```

These stages are related but **not interchangeable**.

- A historical artifact records what was explored.
- A conceptual architecture describes a proposed mechanism.
- A contract defines testable software behavior.
- An implementation demonstrates that code exists.
- Software tests demonstrate compliance with the defined software contract.
- Empirical evaluation tests broader behavioral or research claims.
- Independent reproduction provides stronger external evidence.

Accordingly, no dashboard, recording, prototype, architecture diagram, passing test, or historical document should be interpreted as evidence beyond the level it actually supports.

---

## 4. Current implementation status — ACRM v8.5

The current repository deliberately keeps the implemented v8.5 core small and contract-driven.

```text
Recorded / supplied state
          │
          ▼
      FieldState
          │
          ▼
 Future higher-level layers
```

`FieldState` is the current implemented boundary object for a recorded observation. It validates and preserves supplied state; it does not interpret that state.

### Implemented in v8.5

- immutable `FieldState` snapshots;
- non-empty `field_id` and `session_id` validation;
- non-negative integer sequence validation;
- timezone-aware timestamp validation;
- finite numeric metric validation;
- read-only metric storage;
- unique, non-empty failure-mode identifier validation;
- `governance_confidence` validation in `[0.0, 1.0]`;
- deterministic metric and failure-mode access;
- UTC-normalized timestamp access;
- contract-focused unit tests;
- Python packaging;
- automated GitHub Actions CI across Python 3.10–3.13.

Authoritative current-status documents:

- [`docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`](docs/ACRM_v8_5_DEVELOPMENT_STATUS.md)
- [`docs/FIELD_STATE_CONTRACT.md`](docs/FIELD_STATE_CONTRACT.md)

### What v8.5 does not claim

The current core does **not** claim to implement a complete behavioral inference stack, causal-analysis engine, autonomous governance controller, intervention engine, or scientifically validated cognitive model.

Potential higher-level capabilities such as relation detection, transition analysis, behavioral analysis, governance, and intervention require their own explicit contracts, implementations, tests, and evaluation evidence before being promoted into the core.

---

## 5. Fundamental architectural boundary: observation is not interpretation

A core engineering principle is the separation of **recorded state** from **interpretation**.

`FieldState` records and validates supplied state. It does not decide:

- why a state exists;
- what the state means;
- what caused it;
- whether causality has been established;
- how observations relate to one another;
- whether a transition occurred;
- which behavioral pattern should be inferred;
- which decision should be made;
- or which intervention should be performed.

This boundary prevents higher-level hypotheses from silently becoming low-level data-model assumptions.

Likewise:

> **Temporal succession or correlation must not automatically be represented as causality.**

Software correctness and scientific validity are separate claims and require separate evidence.

---

## 6. Research architecture: Unconscious Bridge

One of the foundational conceptual artifacts in the ACRM research history is the **Unconscious Bridge Layer**.

The earliest architecture was generated from a conceptual definition of human unconscious processing and subsequently formalized through interaction with the collaborating LLMs. Its purpose in the research history is important: it represents an early architectural seed from which later questions about impasse, alternate processing paths, synthesis, incubation, integrity checking, and output selection developed.

A simplified conceptual flow is:

```text
Prompt / Input
      ↓
Conscious Stream
      ↓
Impasse Detector
   ↙          ↘
No Impasse    High Loss / Stuckness
   ↓                 ↓
Standard       Unconscious Bridge
Output              │
              ┌─────┴───────────┐
              ↓                 ↓
       Synthesis Flow     Incubation Pool
              └─────┬───────────┘
                    ↓
              Integrity Gate
               ↙          ↘
        Coherent/Resolved   Hard Mismatch
             ↓                   ↓
   Unconscious Output       Rejection /
                            Clarification
               \             /
                └─────┬─────┘
                      ↓
                 Final Output
```

This architecture is currently a **research concept / architectural artifact**, not an implemented runtime capability of v8.5.

The authoritative research record is:

- [`docs/research/ACRM_FOUNDATIONAL_UNCONSCIOUS_BRIDGE_ARCHITECTURE.md`](docs/research/ACRM_FOUNDATIONAL_UNCONSCIOUS_BRIDGE_ARCHITECTURE.md)

Its historical significance should be preserved separately from claims about present implementation.

---

## 7. Evolution of the architecture

The repository contains artifacts from different architectural generations. Earlier research should be read as evidence of architectural evolution, not as a second implementation of the current core.

For example, the repository preserves the v7.9 Obstruction Theory review and its identified limitations. This material is valuable for understanding the evolution of the research, but it is not equivalent to the v8.5 `FieldState` contract.

Relevant records include:

- [`docs/research/ACRM_v7_9_OBSTRUCTION_THEORY_STATUS.md`](docs/research/ACRM_v7_9_OBSTRUCTION_THEORY_STATUS.md)
- [`docs/ARCHITECTURE_REVIEW_V7_9.md`](docs/ARCHITECTURE_REVIEW_V7_9.md)
- [`docs/roadmap/ACRM_v2.0_technical_roadmap.md`](docs/roadmap/ACRM_v2.0_technical_roadmap.md)

The architectural direction is therefore evolutionary:

```text
Research history
      ↓
Architectural hypotheses
      ↓
Review / boundary clarification
      ↓
Explicit contracts
      ↓
Small validated core
      ↓
Gated higher-level capabilities
```

---

## 8. Roadmap discipline

For an emergent architecture such as ACRM, the roadmap is not a historical description of what was planned from the beginning. It is the **engineering mechanism for turning an organically developed architecture into a controlled, reviewable development sequence**.

The roadmap must answer:

1. Where is the system now?
2. What is the target architectural state?
3. Why is the next layer needed?
4. What prerequisites must exist before it is built?
5. What contract defines completion?
6. What tests and evidence are required?
7. What remains research-only?
8. What would cause a design to be rejected, revised, or deferred?

The current roadmap treats future layers as gated work rather than assumed capabilities.

A useful high-level direction is:

```text
FieldState
    ↓
Relation
    ↓
Transition
    ↓
Analysis
    ↓
Governance
    ↓
Intervention
```

This is an **architectural direction**, not a statement that all of these components currently exist.

Each new layer should establish, before core promotion:

```text
Responsibility
     ↓
Interface / Contract
     ↓
Assumptions & Invariants
     ↓
Failure Modes
     ↓
Implementation
     ↓
Tests
     ↓
Evaluation
     ↓
Evidence-based promotion
```

---

## 9. Research archive, prototypes, and demonstrations

The broader research history includes dashboards, recordings, executable prototypes, experiments, and architectural demonstrations covering topics such as:

- interaction-field visualization;
- behavioral runtime state;
- temporal state and trajectory observation;
- calibration and invariant testing;
- failure-mode taxonomies;
- quality-control and consensus concepts;
- observability and system-state visualization.

These artifacts are retained because they preserve architectural experiments and the path by which concepts evolved.

They are **not automatically part of the current runtime**.

See:

- [`docs/DEMO_CATALOG.md`](docs/DEMO_CATALOG.md)
- [`docs/demos/README.md`](docs/demos/README.md)

### Evidence rule

A dashboard may contain sophisticated UI, simulated values, browser-side algorithms, or apparent runtime behavior. That is evidence of a prototype or demonstration—not automatically evidence of a production backend, scientific validation, or current v8.5 implementation.

Historical and demo provenance is deliberately preserved rather than erased, but it is kept separate from implementation claims.

---

## 10. Repository architecture

The repository currently contains the following principal layers:

```text
.github/workflows/
    CI automation

acrm_core/
    Implemented v8.5 runtime foundation

 tests/
    Executable software-contract tests

 docs/
    Technical contracts, status, governance,
    research records, roadmap, demos, reporting
```

The current implementation footprint is intentionally narrow:

```text
acrm_core/
└── field/
    └── state.py

 tests/
└── unit/
    └── test_field_state.py
```

The documentation structure separates implementation status, research, roadmap, testing, demos, and stakeholder reporting so that different evidence classes remain identifiable.

---

## 11. Engineering governance

ACRM follows an evidence-first engineering discipline.

A proposed capability should not enter the core merely because it appears in a research document, prototype, dashboard, diagram, or roadmap.

Before promotion, the capability should have:

- a clearly defined responsibility;
- explicit inputs and outputs;
- documented assumptions and invariants;
- identifiable failure modes;
- a testable contract;
- an implementation;
- executable tests;
- and an appropriate evaluation strategy.

See [`docs/ENGINEERING_GOVERNANCE.md`](docs/ENGINEERING_GOVERNANCE.md) and [`docs/testing/EPISTEMIC_INVARIANTS.md`](docs/testing/EPISTEMIC_INVARIANTS.md).

### Core principle

> **Complexity should be promoted only when its boundaries and evidence are strong enough to support it.**

---

## 12. Stakeholder reporting

The repository maintains an official, dated stakeholder-reporting record for executive and steering-committee communication.

**Current reporting period:** 23–30 Aug 2026  
**Current reported status:** 🟢 **GREEN**

Current reporting artifacts:

- [`docs/STAKEHOLDER_UPDATE_2026-08-30.md`](docs/STAKEHOLDER_UPDATE_2026-08-30.md) — source-of-record written update;
- [`docs/ACRM_Executive_Update_2026-08-30.pptx`](docs/ACRM_Executive_Update_2026-08-30.pptx) — one-slide executive presentation;
- [`docs/STAKEHOLDER_REPORTING.md`](docs/STAKEHOLDER_REPORTING.md) — reporting policy.

Stakeholder reporting communicates project status; it does not establish technical or scientific validity. Claims must remain proportional to the evidence in the repository.

The Markdown update and PowerPoint deck represent the same reporting baseline and should remain synchronized when status changes.

---

## 13. Installation and tests

Requirements: **Python 3.10+** and `pip`.

Install the project with test dependencies:

```bash
python -m pip install -e ".[test]"
```

Run the test suite:

```bash
python -m pytest -q
```

The current v8.5 test suite contains **15 contract-focused tests** for `FieldState`.

CI runs the project contract across Python 3.10, 3.11, 3.12, and 3.13 for pushes and pull requests targeting `main` or `develop`.

A green CI result is evidence about the implemented software contract. It is not, by itself, evidence that the broader ACRM research hypotheses are scientifically validated.

---

## 14. Minimal FieldState example

```python
from datetime import datetime, timezone
from acrm_core.field.state import FieldState

state = FieldState(
    field_id="field-1",
    session_id="session-1",
    sequence=0,
    timestamp=datetime.now(timezone.utc),
    metrics={"score": 1.0},
    failure_modes=("none",),
    governance_confidence=0.5,
)

state.metric("score")
state.has_failure_mode("none")
```

The complete software contract is defined in [`docs/FIELD_STATE_CONTRACT.md`](docs/FIELD_STATE_CONTRACT.md).

---

## 15. Development principles

1. **Observation before conclusion.**
2. **Experimentation before generalization.**
3. **Contracts before complexity.**
4. **Architectures should be implementable.**
5. **Systems should be observable.**
6. **Implementation evidence is not scientific validation.**
7. **Keep recording, relation detection, transition analysis, governance, and intervention separated until their contracts justify integration.**
8. **Preserve research history and prototype provenance.**
9. **Prefer explicit, deterministic, reviewable behavior.**
10. **Make claims proportional to available evidence.**
11. **Do not allow historical or conceptual artifacts to silently become implementation claims.**

---

## 16. Current maturity and next transition

ACRM has progressed beyond idea-only research. The repository contains architectural records, research artifacts, prototypes and demonstrations, an implemented v8.5 contract foundation, executable tests, CI, and formalized evidence boundaries.

The immediate engineering transition is from a deliberately small, validated foundation toward higher-level capabilities without losing architectural discipline.

The intended progression is:

```text
Current validated foundation
          ↓
Architectural stabilization
          ↓
Explicit next-layer contracts
          ↓
Controlled implementation
          ↓
Regression testing
          ↓
Longitudinal / empirical evaluation
          ↓
Independent review and reproduction
```

Known constraints include limited scale and execution capacity, the need for suitable longitudinal data, external validation, reproducibility, and research collaboration. These are explicit development constraints rather than hidden assumptions.

---

## 17. Contributing and critical review

Technical discussion, critical review, reproducibility work, and contributions are welcome.

Substantial architectural changes should identify, where applicable:

- the problem being addressed;
- component responsibility;
- inputs and outputs;
- assumptions and invariants;
- failure modes;
- tests;
- evaluation strategy;
- evidence level;
- and whether the change belongs to core, demo, research artifact, or roadmap.

Critical review is part of the intended development process. The objective is not to eliminate criticism but to make assumptions, boundaries, evidence, and limitations explicit enough to support constructive technical review.

---

## 18. Navigation

| Area | Primary document |
|---|---|
| Current implementation | [`docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`](docs/ACRM_v8_5_DEVELOPMENT_STATUS.md) |
| Core contract | [`docs/FIELD_STATE_CONTRACT.md`](docs/FIELD_STATE_CONTRACT.md) |
| Foundational research architecture | [`docs/research/ACRM_FOUNDATIONAL_UNCONSCIOUS_BRIDGE_ARCHITECTURE.md`](docs/research/ACRM_FOUNDATIONAL_UNCONSCIOUS_BRIDGE_ARCHITECTURE.md) |
| Historical architecture review | [`docs/ARCHITECTURE_REVIEW_V7_9.md`](docs/ARCHITECTURE_REVIEW_V7_9.md) |
| Roadmap | [`docs/roadmap/ACRM_v2.0_technical_roadmap.md`](docs/roadmap/ACRM_v2.0_technical_roadmap.md) |
| Engineering governance | [`docs/ENGINEERING_GOVERNANCE.md`](docs/ENGINEERING_GOVERNANCE.md) |
| Epistemic invariants | [`docs/testing/EPISTEMIC_INVARIANTS.md`](docs/testing/EPISTEMIC_INVARIANTS.md) |
| Demo inventory | [`docs/DEMO_CATALOG.md`](docs/DEMO_CATALOG.md) |
| Demo archive policy | [`docs/demos/README.md`](docs/demos/README.md) |
| Stakeholder reporting | [`docs/STAKEHOLDER_REPORTING.md`](docs/STAKEHOLDER_REPORTING.md) |
| Current stakeholder update | [`docs/STAKEHOLDER_UPDATE_2026-08-30.md`](docs/STAKEHOLDER_UPDATE_2026-08-30.md) |

---

## License

See `LICENSE` for licensing information.
