

````markdown
# Axsx22-acrm

## Adaptive Cognitive Regulation Module (ACRM)

ACRM is an independent, research-oriented software project exploring structured approaches to observing and modeling adaptive behavior in AI systems.

The project is developed incrementally, with an emphasis on separating recorded observations from higher-level analysis, inference, governance, and intervention.

> **Current status:** The present implementation establishes the `FieldState` runtime contract and its test coverage. The broader ACRM architecture remains under research and development.

---

## Research Context

ACRM originated from long-term observation and investigation of adaptive behavior in AI systems.

The research developed progressively through observation, questioning, hypothesis formation, conceptual modeling, architectural design, and software implementation.

The project follows a deliberate distinction between research claims and implementation evidence:

- an observation is not an interpretation;
- an interpretation is not a hypothesis;
- a hypothesis is not a validated model;
- an implementation is not validation of the underlying research hypothesis;
- passing software tests demonstrates compliance with defined software contracts, not the truth of broader scientific claims.

The research and engineering process can therefore be represented as:

**Observation → Questions → Hypotheses → Conceptual Models → Architecture → Testable Contracts → Implementation → Testing → Validation → Empirical Evaluation**

The repository represents the engineering and experimental side of this process.

---

## Current Implementation

The current development line is focused on **ACRM v8.5**.

The primary implemented component is:

```text
FieldState
````

`FieldState` provides an immutable, validated representation of a recorded system state.

The current implementation establishes contracts for:

* immutable state snapshots;
* `field_id` validation;
* `session_id` validation;
* non-negative sequence values;
* timezone-aware timestamps;
* explicit timestamps suitable for deterministic testing and replay;
* finite numeric metrics;
* immutable metric storage;
* failure-mode identifier validation;
* duplicate failure-mode detection;
* governance-confidence validation in the range `[0.0, 1.0]`;
* deterministic metric and failure-mode access.

The current `FieldState` implementation is covered by unit tests.

The current v8.5 development status and implementation boundaries are documented in:

`docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`

---

## Architectural Boundary

The current architecture deliberately establishes `FieldState` as a boundary around recorded state.

Conceptually:

```text
Observed and recorded state
            │
            ▼
       FieldState
            │
            ▼
   Higher-level processing
```

`FieldState` is responsible for representing and validating a recorded state.

It does not, by itself, determine:

* why a state exists;
* what caused a state;
* what a state means;
* how multiple states are related;
* whether a particular transition occurred;
* what behavioral pattern should be inferred;
* what decision should be made;
* or what intervention should be performed.

These responsibilities are outside the current implementation.

This separation is intentional.

---

## Future Research Direction

Future development may investigate additional architectural layers concerned with relationships between observations, changes across states, analysis, governance, and intervention.

A possible research direction is:

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

This diagram represents a **research and architectural direction**, not a claim that these components currently exist or have been scientifically validated.

In particular, a relationship between observations should not automatically be interpreted as causality, and an observed difference between states should not automatically be treated as an explanation of the underlying behavior.

Future layers will therefore require explicit definitions, responsibilities, testable contracts, and appropriate validation before they are implemented as part of the framework.

---

## What Is Not Currently Implemented

The current repository does not claim the following as implemented unless corresponding source code, contracts, and tests are explicitly present:

* runtime Field/Stream processing;
* ordering between multiple snapshots;
* session-continuity enforcement across snapshots;
* temporal or directional analysis;
* state-transition policies;
* canonical metric semantics and units;
* a failure-mode taxonomy or registry;
* governance evaluation;
* model intervention;
* continuous runtime regulation;
* experimental verification;
* benchmark evaluation.

The existence of `FieldState` should not be interpreted as evidence that these higher-level capabilities have already been implemented.

---

## Repository Structure

The current repository is intentionally small and focused on the implemented v8.5 scope.

```text
acrm_core/
└── field/
    └── state.py

tests/
└── unit/
    └── test_field_state.py

docs/
├── ACRM_v8_5_DEVELOPMENT_STATUS.md
└── FIELD_STATE_CONTRACT.md

pyproject.toml
README.md
LICENSE
```

The structure is expected to evolve as additional architectural contracts are defined and implemented.

---

## Installation

### Requirements

* Python 3.10 or later

### Install the package

```text
pip install .
```

### Install test dependencies

```text
pip install ".[test]"
```

---

## Running the Tests

The repository uses `pytest` for its current test suite.

Run:

```text
pytest
```

The current `FieldState` test suite contains 33 passing tests.

---

## Documentation

The following documents and source files provide the most direct view of the current implementation:

* `docs/ACRM_v8_5_DEVELOPMENT_STATUS.md` — current v8.5 implementation status and explicit boundaries.
* `docs/FIELD_STATE_CONTRACT.md` — `FieldState` responsibilities and non-responsibilities.
* `acrm_core/field/state.py` — runtime `FieldState` implementation.
* `tests/unit/test_field_state.py` — unit tests for the `FieldState` contract.

---

## Development Principles

ACRM development follows several principles:

### 1. Separate observation from inference

Recorded state should not be treated as an explanation of that state.

### 2. Define boundaries before implementation

A new architectural layer should have a clear responsibility and contract before it becomes a runtime component.

### 3. Keep research claims separate from implementation claims

Software implementation and passing tests provide evidence about the software itself. They do not, by themselves, validate broader hypotheses about AI behavior.

### 4. Prefer explicit contracts

Important assumptions should be expressed as explicit, testable contracts rather than remaining implicit in implementation behavior.

### 5. Increase complexity only when justified

The project prioritizes clarifying architectural responsibilities and their evidence requirements before adding additional runtime components.

---

## Contributing

Technical discussion, critical review, and contributions are welcome.

For substantial architectural changes, please discuss the proposed change before implementation.

Architectural proposals should, where applicable, identify:

* the problem being addressed;
* the responsibility of the proposed component;
* the information it receives;
* the information it produces;
* its relationship to existing contracts;
* assumptions introduced by the design;
* and how its behavior can be tested or evaluated.

---

## Research Status

ACRM is an independent research project developed by **Ali Farahani**.

The repository should be evaluated according to the implementation, documentation, tests, and evidence explicitly available in the project.

Broader research questions and hypotheses remain open to further investigation and empirical evaluation.

---

## License

See `LICENSE` for licensing information.

`
