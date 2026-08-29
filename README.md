Axsx22-acrm

Adaptive Cognitive Regulation Module (ACRM)

ACRM is an independent research and engineering project focused on making observable aspects of adaptive AI-system behavior explicit, inspectable, testable, and reproducible.

The repository contains a concrete Python implementation of the ACRM v8.5 observation layer, centered on the immutable "FieldState" primitive, together with its software contract, executable unit tests, development documentation, package configuration, and traceable Git history.

---

What is ACRM?

ACRM emerged from a long-term research process concerned with how adaptive AI systems behave during sustained interaction.

The work began with observation and gradually developed through questions, hypotheses, conceptual models, architectural structures, software implementation, and executable verification.

The engineering side of this research is represented in this repository through explicit software artifacts rather than through conceptual descriptions alone.

The current repository therefore provides a concrete implementation of the observation layer of ACRM v8.5.

---

Research Path

The research developed through the following progression:

Observation
    ↓
Questions
    ↓
Hypotheses
    ↓
Conceptual Models
    ↓
Architecture
    ↓
Implementation
    ↓
Testable Contracts
    ↓
Validation
    ↓
Empirical Evaluation

This progression is important to the project because different forms of evidence are kept conceptually distinct.

Implementation demonstrates what has been built.

Executable tests demonstrate properties of the implemented software contracts.

Neither is presented by itself as empirical confirmation of the broader research hypotheses.

---

Current Implementation

The current concrete observation primitive of ACRM v8.5 is:

"FieldState"

"FieldState" represents an immutable snapshot of observable ACRM field state.

Conceptually:

Observation
     ↓
FieldState
     ↓
Immutable Snapshot

The implementation provides a stable representation of an observation that can be inspected, validated, tested, and used as a foundation for higher-level analysis.

The FieldState layer is intentionally concerned with recording observable state.

It does not modify model execution or regulate the model.

---

Repository Structure

The current repository contains the following implementation, documentation, testing, and configuration artifacts:

Axsx22-acrm/
│
├── acrm_core/
│   ├── __init__.py
│   └── field/
│       ├── __init__.py
│       └── state.py
│
├── docs/
│   ├── ACRM_v8_5_DEVELOPMENT_STATUS.md
│   └── FIELD_STATE_CONTRACT.md
│
├── tests/
│   └── unit/
│       └── test_field_state.py
│
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore

The repository uses standard Python package structure and keeps generated package metadata and local environments outside source control.

---

FieldState Data Model

A "FieldState" contains the following observable elements:

- "field_id"
- "session_id"
- "sequence"
- "timestamp"
- "metrics"
- "state"
- "active_failure_modes"
- "governance_confidence"

Field identity

"field_id" identifies the observed field.

"session_id" identifies the session associated with the observation.

Both are validated as non-empty strings.

Sequence

"sequence" represents the sequence position supplied to the observation.

The current contract requires a non-negative integer.

Boolean values are explicitly rejected even though Python treats "bool" as a subclass of "int".

Timestamp

FieldState uses timezone-aware timestamps.

When an explicit timestamp is not supplied, the implementation provides a UTC timestamp.

Explicit timestamps are supported for deterministic observations and reproducible testing.

Metrics

Metrics are represented as named numeric values.

The implementation validates metric names and values and rejects:

- boolean metric values
- "NaN"
- positive infinity
- negative infinity
- other non-finite values

Metric storage is protected from later mutation.

State

The "state" field is represented as a non-empty string.

The FieldState observation layer does not impose a canonical scientific state vocabulary.

Active failure modes

Failure modes are represented as identifiers.

The contract validates the identifiers and rejects duplicate values.

The resulting collection is immutable.

Governance confidence

"governance_confidence" is represented as a finite numeric value constrained to:

0.0 ≤ governance_confidence ≤ 1.0

Boolean and non-finite values are rejected.

---

Immutability

Immutability is a fundamental property of the FieldState implementation.

The FieldState object is frozen, while internal collections are also protected from mutation.

The implementation therefore protects the observation through two mechanisms:

FieldState mutation
       ↓
     rejected

Source-container mutation
       ↓
does not alter
existing snapshot

This ensures that once an observation has been recorded, later changes to source containers cannot silently modify the recorded snapshot.

This property is important for reproducible inspection, testing, replay, and later analysis of observations.

---

Validation

The FieldState contract provides structural validation for observable state.

The implemented validation covers:

- field identity
- session identity
- sequence type
- sequence range
- boolean sequence rejection
- timezone-aware timestamp requirements
- metric names
- metric numeric types
- boolean metric rejection
- finite metric values
- failure-mode identifiers
- duplicate failure-mode rejection
- state validation
- governance-confidence type
- governance-confidence range
- finite governance-confidence values

These validation rules define software-level invariants of the observation object.

They do not, by themselves, establish scientific validity for the concepts represented by the stored values.

---

Metric Representation

FieldState stores metrics as named values.

For example:

S = 0.91
rho = 0.22
ARQ = 0.74

The observation layer can store and validate such values without embedding their complete theoretical interpretation into the snapshot structure.

The FieldState contract therefore separates metric representation from questions concerning:

- the construct represented by a metric
- its scientific definition
- its unit
- its calculation procedure
- its directionality
- comparability across systems
- measurement error
- theoretical validity

This separation keeps the observation primitive independent from higher-level interpretation.

---

Failure Modes and State

FieldState records state and active failure-mode identifiers as part of an observation.

The observation layer keeps distinct concepts separate:

Observed State
      ≠
Failure Interpretation
      ≠
Governance Decision
      ≠
Intervention

The purpose of this separation is to allow an observation to be recorded without embedding a complete interpretation or intervention policy into the observation primitive.

---

Deterministic Observations

FieldState supports explicitly supplied timestamps.

This allows deterministic observation objects to be created for testing and controlled analysis.

For example:

from datetime import datetime, timezone

timestamp = datetime(
    2026,
    8,
    14,
    12,
    0,
    tzinfo=timezone.utc,
)

An explicit timestamp can then be supplied when constructing a FieldState.

This provides deterministic test inputs while keeping temporal-stream behavior separate from the individual observation object.

---

FieldState API

The current implementation provides construction and observation access through the FieldState API.

A representative usage pattern is:

from acrm_core.field.state import FieldState

state = FieldState.create(
    field_id="field-001",
    session_id="session-001",
    sequence=0,
    metrics={
        "S": 0.91,
        "rho": 0.22,
        "ARQ": 0.74,
    },
    state="HEALTHY",
    governance_confidence=0.95,
)

print(state.metric("S"))
print(state.has_failure_mode("FM-01"))

This example demonstrates the implemented observation interface.

The example values do not by themselves define the scientific semantics of "S", "rho", or "ARQ".

---

Test Suite

The repository contains a dedicated FieldState unit-test suite:

"tests/unit/test_field_state.py"

The current suite contains:

33 passing tests

The tests exercise the implemented FieldState contract, including:

- FieldState creation
- explicit timestamps
- UTC timestamps
- deterministic timestamps
- metric access
- failure-mode detection
- sequence validation
- boolean sequence rejection
- confidence validation
- confidence boundary conditions
- non-finite confidence rejection
- field identity validation
- session identity validation
- timezone-aware timestamp requirements
- state validation
- metric validation
- boolean metric rejection
- non-finite metric rejection
- metric-name validation
- failure-mode validation
- duplicate failure-mode rejection
- object immutability
- metric immutability
- source-dictionary mutation protection
- immutable failure-mode representation

Run the test suite with:

python -m pytest -q

The current verified result is:

33 passed

---

Documentation

The implementation is accompanied by two dedicated documents.

FieldState Contract

"docs/FIELD_STATE_CONTRACT.md"

The FieldState contract defines the responsibility boundary of the observation layer and documents the behavior that the implementation is required to preserve.

It establishes the distinction between observation storage and higher-level concerns such as temporal relationships, transition rules, metric semantics, failure-mode taxonomy, governance decisions, and intervention.

ACRM v8.5 Development Status

"docs/ACRM_v8_5_DEVELOPMENT_STATUS.md"

This document records the development state of ACRM v8.5 and provides a traceable description of the implementation stage represented by the repository.

Together, the implementation, tests, and documentation form a connected software artifact:

Contract
    ↓
Implementation
    ↓
Tests
    ↓
Development Record

---

Package Configuration

The project uses "pyproject.toml" for Python package configuration.

A development environment can be created with:

python -m venv .venv
source .venv/bin/activate

The package and test dependency can then be installed with:

pip install -e ".[test]"

The tests can be executed with:

python -m pytest -q

---

Development History

The repository has evolved incrementally from an initial ACRM project baseline into a concrete observation-layer implementation.

The Git history records the development process through successive changes to:

- project documentation
- research navigation
- ACRM v8.5 structure
- FieldState architecture
- FieldState implementation
- contract hardening
- unit-test coverage
- development-status documentation
- Python package configuration
- repository hygiene
- README documentation

The Git history is part of the engineering record of the project and provides a traceable chronology of the work.

---

Architectural Position

The current implementation occupies the observation layer of the broader ACRM architecture.

Its role is to provide a stable, validated, immutable representation of observable state.

Conceptually:

                    ACRM
                      │
                      ▼
             Observation Layer
                      │
                      ▼
                 FieldState
                      │
              ┌───────┴───────┐
              ▼               ▼
       Documentation       Tests
              │               │
              └───────┬───────┘
                      ▼
              Verified Contract

The repository therefore provides a concrete foundation for examining observations independently before higher-level relationships and processes are introduced.

---

From Observation to Process

The current architecture begins with the observation itself.

A single FieldState represents a point of observable state.

A sequence of observations provides material for examining relationships between states:

State A
   ↓
State B
   ↓
State C

The conceptual progression beyond the observation layer is:

Observation
     ↓
Relation
     ↓
Transition
     ↓
Pattern
     ↓
Model
     ↓
Prediction / Regulation

The important architectural principle is that these concepts should not be assumed to exist merely because they have been described conceptually.

Each higher-level layer can be introduced through its own explicit contract and implementation when it becomes part of the repository.

---

Engineering and Research Principles

Explicit contracts

Observable software behavior is defined through explicit contracts and executable tests.

Immutable observations

Recorded observations remain protected from later mutation of their source data.

Deterministic verification

Explicit timestamps and executable tests support reproducible verification.

Separation of responsibility

Observation, temporal analysis, interpretation, governance, and intervention are treated as distinct concerns.

Evidence before inference

Evidence about implemented software is kept distinct from interpretation of broader research hypotheses.

Incremental architecture

Architectural concepts become implementation artifacts through explicit development rather than being treated as implemented merely because they have been proposed.

---

Current Repository State

The current ACRM v8.5 repository provides a concrete, inspectable, installable, executable, and testable software artifact centered on the FieldState observation layer.

The repository currently provides:

- a Python package structure
- an implemented immutable FieldState observation primitive
- explicit validation rules
- protected observation data
- deterministic timestamp support
- dedicated FieldState unit tests
- 33 passing tests
- a documented FieldState contract
- ACRM v8.5 development-status documentation
- Python package configuration
- reproducible installation instructions
- Git-traceable development history

The repository can therefore be examined directly at the level of source code, software contracts, executable tests, documentation, package configuration, and version history.

---

License

See "LICENSE" for the applicable license terms.
