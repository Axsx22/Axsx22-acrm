Axsx22-acrm

Adaptive Cognitive Regulation Module (ACRM)

ACRM is an independent research and engineering project focused on making observable aspects of adaptive AI-system behavior explicit, inspectable, testable, and reproducible.

The repository currently contains a concrete Python implementation of the ACRM v8.5 observation layer, centered on the immutable "FieldState" primitive, together with its software contract, executable unit tests, development documentation, package configuration, and traceable Git history.

What is ACRM?

ACRM emerged from a long-term research process concerned with how adaptive AI systems behave during sustained interaction.

The work developed progressively from observation and questioning toward hypotheses, conceptual models, architectural structures, software implementation, explicit contracts, and executable verification.

This repository represents the engineering side of that research process through concrete software artifacts that can be inspected, executed, tested, and traced through version history.

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

Different forms of evidence are kept conceptually distinct.

Implementation demonstrates what has been built.

Executable tests demonstrate properties of the implemented software contracts.

Neither implementation nor software tests are presented by themselves as empirical confirmation of broader research hypotheses.

Current Implementation

The current concrete observation primitive of ACRM v8.5 is:

FieldState

"FieldState" represents an immutable snapshot of observable ACRM field state.

Observation
    ↓
FieldState
    ↓
Immutable Snapshot

The FieldState implementation provides a stable representation of an observation that can be inspected, validated, tested, and used as a foundation for higher-level analysis.

The observation layer records observable state. It does not modify model execution, model output, sampling behavior, or model policy.

FieldState Data Model

A "FieldState" contains:

- "field_id"
- "session_id"
- "sequence"
- "timestamp"
- "metrics"
- "state"
- "active_failure_modes"
- "governance_confidence"

Field Identity

"field_id" identifies the observed field.

"session_id" identifies the session associated with the observation.

Both are validated as non-empty strings.

Sequence

"sequence" represents the sequence position supplied to the observation.

The contract requires a non-negative integer.

Boolean values are explicitly rejected even though Python treats "bool" as a subclass of "int".

Timestamp

FieldState uses timezone-aware timestamps.

When an explicit timestamp is not supplied, the implementation provides a UTC timestamp.

Explicit timestamps are supported for deterministic observations and reproducible testing.

Metrics

Metrics are represented as named numeric values.

The implementation validates metric names and values and rejects:

- boolean values
- "NaN"
- positive infinity
- negative infinity
- other non-finite values

Metric storage is protected from later mutation.

State

The "state" field is represented as a non-empty string.

The FieldState observation layer does not impose a canonical scientific state vocabulary.

Active Failure Modes

Failure modes are represented as identifiers.

The contract validates the identifiers and rejects duplicate values.

The resulting collection is immutable.

Governance Confidence

"governance_confidence" is represented as a finite numeric value constrained to:

0.0 ≤ governance_confidence ≤ 1.0

Boolean and non-finite values are rejected.

Immutability

Immutability is a fundamental property of the FieldState implementation.

The FieldState object is frozen, while internal collections are also protected from mutation.

The implementation protects the observation through two mechanisms:

FieldState mutation
        ↓
     rejected

Source-container mutation
        ↓
does not alter existing snapshot

Once an observation has been recorded, later changes to source containers cannot silently modify the recorded snapshot.

This supports reproducible inspection, testing, replay, and later analysis of observations.

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

They do not, by themselves, establish scientific validity for the concepts represented by stored values.

Metric Representation

FieldState stores metrics as named values.

For example:

S   = 0.91
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

Failure Modes and State

FieldState records state and active failure-mode identifiers as part of an observation.

The observation layer keeps the following concepts distinct:

Observed State
      ≠
Failure Interpretation
      ≠
Governance Decision
      ≠
Intervention

This separation allows an observation to be recorded without embedding a complete interpretation or intervention policy into the observation primitive.

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

Test Suite

The repository contains a dedicated FieldState unit-test suite:

"tests/unit/test_field_state.py"

The current verified suite contains:

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

Current verified result:

33 passed

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

Package Configuration

The project uses "pyproject.toml" for Python package configuration.

Create a development environment with:

python -m venv .venv
source .venv/bin/activate

Install the package and test dependency with:

pip install -e ".[test]"

Run the tests with:

python -m pytest -q

Repository Structure

Axsx22-acrm/
├── acrm_core/
│   ├── __init__.py
│   └── field/
│       ├── __init__.py
│       └── state.py
├── docs/
│   ├── ACRM_v8_5_DEVELOPMENT_STATUS.md
│   └── FIELD_STATE_CONTRACT.md
├── tests/
│   └── unit/
│       └── test_field_state.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore

The repository keeps generated package metadata and local development environments outside source control.

Architectural Position

The current implementation occupies the observation layer of the broader ACRM architecture.

Its role is to provide a stable, validated, immutable representation of observable state.

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
       Documentation        Tests
              │               │
              └───────┬───────┘
                      ▼
              Verified Contract

The repository therefore provides a concrete foundation for examining observations independently before higher-level relationships and processes are introduced.

From Observation to Process

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

These higher-level concepts are architectural directions rather than claims about artifacts contained in the current FieldState implementation.

Each higher-level layer can be introduced through its own explicit contract and implementation when it becomes part of the repository.

Engineering and Research Principles

Explicit Contracts

Observable software behavior is defined through explicit contracts and executable tests.

Immutable Observations

Recorded observations remain protected from later mutation of their source data.

Deterministic Verification

Explicit timestamps and executable tests support reproducible verification.

Separation of Responsibility

Observation, temporal analysis, interpretation, governance, and intervention are treated as distinct concerns.

Evidence Before Inference

Evidence about implemented software is kept distinct from interpretation of broader research hypotheses.

Incremental Architecture

Architectural concepts become implementation artifacts through explicit development rather than being treated as implemented merely because they have been proposed.

Current Development State

ACRM v8.5 currently provides a concrete and tested observation layer centered on "FieldState".

The repository contains:

- an installable Python package
- an implemented immutable FieldState observation primitive
- explicit structural validation rules
- protected observation data
- deterministic timestamp support
- dedicated FieldState unit tests
- 33 passing tests
- a documented FieldState contract
- ACRM v8.5 development-status documentation
- Python package configuration
- reproducible installation and testing instructions
- traceable Git history

The repository is therefore directly inspectable, installable, executable, and testable as a concrete software artifact.

Researcher

ACRM is developed by Ali Farahani as an independent research and engineering project.

The repository documents the transition from research observation and conceptual development toward explicit architectural and software artifacts.

License

See "LICENSE" for the applicable license terms.
