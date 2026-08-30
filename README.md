# Axsx22-acrm

## Adaptive Cognitive Regulation Module (ACRM)

ACRM is an independent, research-oriented software project exploring structured approaches to observing and modeling adaptive behavior in AI systems.

The project is developed incrementally, with a deliberate separation between **recorded observations** and higher-level **analysis, inference, governance, and intervention**.

> **Current status — ACRM v8.5:** the repository implements the `FieldState` runtime contract, contract-focused unit tests, Python packaging, and automated GitHub Actions CI. The broader ACRM architecture remains a research and development program; future layers are not represented as implemented capabilities unless explicitly documented and tested.

---

## What ACRM v8.5 currently is

The current implementation is intentionally small. Its first runtime boundary is:

```text
Observed / recorded state
          │
          ▼
     FieldState
          │
          ▼
 Future higher-level layers
```

`FieldState` is a validated, immutable representation of a **recorded state**. It is a data-contract boundary, not an inference engine, decision system, or intervention mechanism.

### Implemented in v8.5

- immutable state snapshots;
- non-empty `field_id` validation;
- non-empty `session_id` validation;
- non-negative integer sequence validation;
- timezone-aware timestamp validation;
- explicit timestamps for deterministic testing and replay;
- finite numeric metric validation;
- read-only metric storage;
- failure-mode identifier validation;
- duplicate failure-mode rejection;
- `governance_confidence` validation in `[0.0, 1.0]`;
- deterministic metric and failure-mode access;
- UTC-normalized timestamp access;
- unit tests covering the runtime contract;
- automated CI on Python 3.10, 3.11, 3.12, and 3.13.

See [`docs/FIELD_STATE_CONTRACT.md`](docs/FIELD_STATE_CONTRACT.md) for the normative boundary of `FieldState` and [`docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`](docs/ACRM_v8_5_DEVELOPMENT_STATUS.md) for implementation status.

---

## Architectural boundary

The most important design rule in the current version is the separation of **observation from interpretation**.

`FieldState` records and validates what was explicitly supplied to it. It does **not** by itself determine:

- why a state exists;
- what caused a state;
- what a state means;
- how multiple observations are related;
- whether a transition occurred;
- what behavioral pattern should be inferred;
- what decision should be made;
- or what intervention should be performed.

These responsibilities remain outside the current runtime component and require their own explicit contracts before implementation.

In particular:

> **Correlation or temporal succession must not automatically be represented as causality.**

The project therefore treats a software contract as evidence about software behavior, not as proof of a broader scientific or behavioral hypothesis.

---

## Research context

ACRM originated from long-term observation and investigation of adaptive behavior in AI systems. The research process developed progressively through observation, questioning, hypothesis formation, conceptual modeling, architectural design, software implementation, and testing.

The repository distinguishes these evidence levels:

```text
Observation
    ↓
Question
    ↓
Hypothesis
    ↓
Conceptual model
    ↓
Architecture
    ↓
Testable contract
    ↓
Implementation
    ↓
Software testing
    ↓
Empirical evaluation
```

These stages are related but not interchangeable. Passing software tests demonstrates compliance with defined software contracts; it does not, by itself, validate a scientific hypothesis about AI behavior.

---

## Repository structure

The current `main` branch reflects the implemented v8.5 scope:

```text
.github/
└── workflows/
    └── ci.yml

acrm_core/
├── __init__.py
└── field/
    ├── __init__.py
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

The structure is expected to evolve only when a new architectural responsibility has a defined contract, implementation boundary, tests, and appropriate evidence.

---

## Installation

### Requirements

- Python **3.10 or later**
- `pip`

### Install the package

```bash
python -m pip install .
```

### Install test dependencies

```bash
python -m pip install ".[test]"
```

### Development install

For local development, an editable install can be used:

```bash
python -m pip install -e ".[test]"
```

---

## Running the tests

The project currently uses `pytest` for its unit-test suite.

Run:

```bash
python -m pytest -q
```

The current suite contains **15 contract-focused tests** for `FieldState`.

The CI workflow runs the test suite across:

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

It is triggered by pushes to `main`/`develop` and pull requests targeting those branches.

---

## FieldState API at a glance

A minimal construction looks like:

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
```

Recorded metrics can be accessed deterministically:

```python
state.metric("score")
```

Explicitly recorded failure modes can be checked with:

```python
state.has_failure_mode("none")
```

The state is immutable. Attempts to modify dataclass fields or the stored metric mapping are rejected.

For the complete contract, see [`docs/FIELD_STATE_CONTRACT.md`](docs/FIELD_STATE_CONTRACT.md).

---

## CI and engineering checks

The repository includes:

```text
.github/workflows/ci.yml
```

The workflow:

1. checks out the repository;
2. provisions supported Python versions;
3. installs the package;
4. installs test dependencies;
5. runs the `pytest` suite.

The purpose of CI is to prevent changes from silently violating the implemented software contract.

CI success should be interpreted as **software evidence for the tested contract**, not as scientific validation of ACRM's broader research direction.

---

## Documentation map

| Document / source | Purpose |
|---|---|
| `README.md` | Project overview, scope, architecture, installation, testing, and development principles |
| `docs/ACRM_v8_5_DEVELOPMENT_STATUS.md` | Current v8.5 implementation status and explicit boundaries |
| `docs/FIELD_STATE_CONTRACT.md` | Normative `FieldState` responsibilities and validation contract |
| `acrm_core/field/state.py` | Runtime implementation of `FieldState` |
| `tests/unit/test_field_state.py` | Contract-focused unit tests |
| `.github/workflows/ci.yml` | Automated CI pipeline |
| `pyproject.toml` | Python package/build/test configuration |

---

## Future research direction

A possible future architecture is:

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

This is a **research and architectural direction**, not a statement that these components currently exist.

Each future layer should define, before implementation:

- its responsibility;
- its inputs and outputs;
- its relationship to existing contracts;
- assumptions introduced by the design;
- failure modes and boundary conditions;
- testable behavior;
- and an appropriate validation/evaluation strategy.

No future layer should silently convert observation into causality, explanation, or intervention.

---

## Development principles

### 1. Observation is not inference

Recorded state should not be treated as an explanation of that state.

### 2. Contracts precede complexity

A new architectural layer should have a clear responsibility and testable contract before becoming a runtime component.

### 3. Implementation evidence is not scientific validation

Passing tests establish behavior of the implemented software. They do not prove broader claims about AI behavior.

### 4. Prefer explicit, deterministic behavior

Important assumptions should be visible in contracts and tests rather than hidden in implicit runtime behavior.

### 5. Reject invalid state early

The current `FieldState` contract rejects invalid recorded state at construction time rather than silently converting it into a potentially misleading value.

### 6. Keep responsibilities separated

Recording, relation detection, transition analysis, governance, and intervention should remain distinct until their contracts justify integration.

---

## Contributing

Technical discussion, critical review, and contributions are welcome.

For substantial architectural changes, discuss the proposed change before implementation.

An architectural proposal should, where applicable, identify:

- the problem being addressed;
- the responsibility of the proposed component;
- the information it receives;
- the information it produces;
- its relationship to existing contracts;
- assumptions introduced by the design;
- expected failure modes;
- and how its behavior can be tested or empirically evaluated.

---

## Research status

ACRM is an independent research project developed by **Ali Farahani**.

The repository should be evaluated according to the implementation, documentation, tests, and evidence explicitly available in the project.

Broader research questions and hypotheses remain open to further investigation and empirical evaluation.

## License

See `LICENSE` for licensing information.
