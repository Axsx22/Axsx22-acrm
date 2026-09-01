# Axsx22-acrm

## Adaptive Cognitive Regulation Module (ACRM)

ACRM is an independent research and engineering project focused on making observable aspects of adaptive AI-system behavior explicit, inspectable, testable, and reproducible.

The repository contains a concrete Python implementation of the ACRM v8.5 observation layer, centered on the immutable `FieldState` primitive, together with its software contract, executable unit tests, development documentation, package configuration, and traceable Git history.

## What is ACRM?

ACRM emerged from a long-term research process concerned with how adaptive AI systems behave during sustained interaction.

The work developed from observation through questions, hypotheses, conceptual models, architectural structures, software implementation, and executable verification.

The engineering side of this research is represented in this repository through explicit software artifacts: source code, contracts, tests, documentation, package configuration, and version history.

## Research Path

```text
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
```

Implementation demonstrates what has been built. Executable tests demonstrate properties of the implemented software contracts. Neither is presented by itself as empirical confirmation of the broader research hypotheses.

## Current Implementation

The current concrete observation primitive of ACRM v8.5 is `FieldState`.

`FieldState` represents an immutable snapshot of observable ACRM field state. It provides a stable, validated representation of an observation that can be inspected, tested, reproduced, and used as a foundation for higher-level runtime and analytical layers.

The FieldState implementation:

- identifies the observed field and session;
- records a non-negative sequence number;
- requires timezone-aware timestamps;
- supports explicit timestamps for deterministic testing and replay;
- stores named numeric metrics;
- rejects boolean and non-finite metric values;
- validates state as a non-empty structural label;
- records active failure-mode identifiers and rejects duplicates;
- validates governance confidence in the range `[0.0, 1.0]`;
- protects metric and failure-mode containers from later mutation;
- provides metric lookup and failure-mode detection.

The FieldState layer records observations. It does not modify model execution, model output, sampling behavior, or underlying model state.

## Current Architectural Position

The repository establishes the observation layer as a concrete and tested architectural foundation.

```text
                         ACRM
                          │
                          ▼
                  Observation Layer
                          │
                          ▼
                      FieldState
                          │
             immutable validated snapshot
                          │
                          ▼
              Higher-Level ACRM Runtime
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
      Temporal         Failure        Governance
      Analysis         Analysis        Evaluation
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                Higher-Level Regulation
```

The current architecture is prepared to serve as a foundation for larger field-testing and evaluation work. Its present evidence is the implemented observation primitive, its explicit contract, executable test coverage, deterministic construction support, and documented architectural boundary. Larger field tests constitute the next level of empirical evaluation rather than a claim that such field evaluation has already been completed.

## FieldState Data Model

A `FieldState` contains:

- `field_id`
- `session_id`
- `sequence`
- `timestamp`
- `metrics`
- `state`
- `active_failure_modes`
- `governance_confidence`

### Field identity

`field_id` and `session_id` are required to be non-empty strings.

### Sequence

`sequence` is a non-negative integer. Boolean values are explicitly rejected.

### Timestamp

Timestamps must be timezone-aware. When no timestamp is supplied, `FieldState.create()` uses the current UTC time. Explicit timestamps are supported for deterministic testing, replay, and imported observations.

### Metrics

Metrics are named numeric values. Metric names must be non-empty strings. Boolean and non-finite values, including `NaN` and infinities, are rejected.

### State

`state` is currently a non-empty structural string. The FieldState layer does not impose a canonical scientific state vocabulary.

### Active failure modes

Failure-mode identifiers must be non-empty strings. Duplicate active failure modes are rejected, and the resulting collection is immutable.

### Governance confidence

`governance_confidence` must be numeric, finite, and within `[0.0, 1.0]`. Boolean values are rejected.

## Immutability

Immutability is a fundamental property of the FieldState implementation.

The dataclass is frozen, while internal metric and failure-mode containers are also protected from mutation. Source dictionaries are copied during construction, so later changes to source containers cannot silently modify an existing observation snapshot.

This supports reproducible inspection, testing, replay, and later analysis.

## Validation and Contract

The FieldState contract defines software-level invariants for the observation object, including identity, sequence, timestamp, metric, state, failure-mode, confidence, and immutability constraints.

The complete contract is documented in:

`docs/FIELD_STATE_CONTRACT.md`

The contract deliberately separates observation storage from higher-level concerns such as:

- ordering between multiple snapshots;
- session continuity across snapshots;
- temporal direction;
- state-transition policy;
- metric semantic definitions and units;
- failure-mode taxonomy;
- governance decisions;
- model intervention.

## Test Suite

The repository contains a dedicated FieldState unit-test suite:

`tests/unit/test_field_state.py`

The current suite contains **33 passing tests** covering construction, deterministic and UTC timestamps, metric access, failure-mode detection, sequence validation, confidence validation, identity validation, state validation, metric validation, failure-mode validation, immutability, and protection against source-container mutation.

Run the tests with:

```bash
python -m pytest -q
```

Current verified result:

```text
33 passed
```

## Documentation

### FieldState Contract

`docs/FIELD_STATE_CONTRACT.md`

Defines the FieldState responsibility boundary and the structural invariants that the implementation preserves.

### ACRM v8.5 Development Status

`docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`

Records the development state of ACRM v8.5 and the implementation stage represented by the repository.

## Package Configuration

The project uses `pyproject.toml` for package configuration and test dependencies.

Create a development environment with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

Then run:

```bash
python -m pytest -q
```

## Development Record

The Git history records the incremental transition from the project baseline toward the current observation-layer implementation, including research documentation, ACRM v8.5 structure, FieldState architecture, implementation, contract hardening, unit-test coverage, development-status documentation, Python package configuration, repository hygiene, and README refinement.

The repository therefore provides a traceable engineering record rather than a static conceptual proposal.

## Research and Engineering Principles

### Explicit contracts

Observable software behavior is defined through explicit contracts and executable tests.

### Immutable observations

Recorded observations remain protected from later mutation of their source data.

### Deterministic verification

Explicit timestamps and executable tests support reproducible verification.

### Separation of responsibility

Observation, temporal analysis, interpretation, governance, and intervention are treated as distinct concerns.

### Evidence before inference

Evidence about implemented software is kept distinct from interpretation of broader research hypotheses.

### Incremental architecture

Architectural concepts become implementation artifacts through explicit development and verification.

## Current Repository State

**ACRM v8.5 — concrete observation layer implemented, contract-defined, and unit-tested; architecture prepared for larger field-testing and empirical evaluation.**

The repository currently provides:

- a Python package structure;
- an implemented immutable `FieldState` observation primitive;
- explicit structural validation rules;
- protected observation data;
- deterministic timestamp support;
- dedicated FieldState unit tests;
- 33 passing tests;
- a documented FieldState contract;
- ACRM v8.5 development-status documentation;
- Python package configuration;
- reproducible installation and testing instructions;
- Git-traceable development history.

The repository can be examined directly at the level of source code, software contracts, executable tests, documentation, package configuration, and version history.

## Researcher

ACRM is an independent research and engineering project developed by **Ali Farahani**.

## License

See `LICENSE` for the applicable license terms.
