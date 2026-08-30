# Axsx22-acrm

## Adaptive Cognitive Regulation Module (ACRM)

ACRM is an independent, research-oriented software project exploring structured approaches to observing and modeling adaptive behavior in AI systems.

> **Current implementation status — v8.5:** the repository provides a small, tested `FieldState` runtime contract, Python packaging, unit tests, and automated GitHub Actions CI. The larger ACRM architecture remains a research and development program; demo dashboards and conceptual modules are not represented as implemented core capabilities unless they have an explicit contract, implementation, and tests.

---

## v8.5 at a glance

```text
Observed / recorded state
          │
          ▼
     FieldState
          │
          ▼
 Future higher-level layers
```

`FieldState` is a validated, immutable representation of a **recorded state**. It is deliberately not an inference engine, causal engine, decision system, or intervention mechanism.

### Implemented

- immutable `FieldState` snapshots;
- non-empty `field_id` and `session_id` validation;
- non-negative integer sequence validation;
- timezone-aware timestamp validation;
- finite numeric metric validation;
- read-only metric storage;
- failure-mode identifier validation and duplicate rejection;
- `governance_confidence` validation in `[0.0, 1.0]`;
- deterministic metric/failure-mode access;
- UTC-normalized timestamp access;
- contract-focused unit tests;
- automated CI on Python 3.10–3.13.

See [`docs/FIELD_STATE_CONTRACT.md`](docs/FIELD_STATE_CONTRACT.md) and [`docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`](docs/ACRM_v8_5_DEVELOPMENT_STATUS.md).

---

## Demos and dashboards

ACRM has accumulated several interactive HTML dashboards and screen-recorded demonstrations during development. These artifacts are important because they preserve earlier architectural experiments and show how concepts such as interaction fields, failure modes, calibration, temporal state and visualization were explored.

**They are intentionally separated from the v8.5 core.** A dashboard can contain sophisticated UI, simulated values, client-side algorithms, or an apparent runtime without constituting a production implementation of the corresponding subsystem.

The reviewed source material includes:

- **ACRM v8 — Interaction Field Architecture:** interactive SVG topology, `S / ρ / H / RS` displays, component cards, hidden-state observers, behavior-pattern display, temporal entropy chart, counterfactual scenario panel, console, and a timed client-side evaluation sequence.
- **ACRM v7 — Behavioral Runtime Field:** a 17-item failure-mode registry, severity visualization, causal links, six client-side test definitions, state vector, temporal trajectory, console, and calibration/test runner logic.
- **Calibration v6.2 dashboard:** calibration-oriented test visualization and result presentation.
- **Failure Mode Taxonomy source material:** Python-side taxonomy, scoring, and orchestration concepts supplied during development.
- **Screen recordings:** visual evidence of dashboard execution on a device.

The detailed inventory and evidence boundaries are documented in [`docs/DEMO_CATALOG.md`](docs/DEMO_CATALOG.md). The archive policy is documented in [`docs/demos/README.md`](docs/demos/README.md).

### Evidence rule

Demo behavior is evidence that a prototype was designed or exercised. It is **not automatically evidence that the displayed values came from a production backend**, nor is it scientific validation of the underlying research hypothesis.

For example, the v8 Interaction Field dashboard initializes chart data in JavaScript and changes displayed metrics through timed callbacks when its evaluation control is run. The v7 dashboard likewise contains its own client-side failure-mode registry and test runners. These are valuable prototype behaviors, but they remain classified as demo/research artifacts until their responsibilities are converted into tested v8.5 contracts.

---

## Architectural boundary

The central engineering rule is the separation of **observation from interpretation**.

`FieldState` records and validates supplied state. It does not determine:

- why a state exists;
- what caused it;
- what it means;
- how observations are related;
- whether a transition occurred;
- which behavioral pattern should be inferred;
- which decision should be made;
- or which intervention should be performed.

> **Correlation or temporal succession must not automatically be represented as causality.**

Software tests establish compliance with software contracts. They do not, by themselves, prove a broader scientific or behavioral claim.

---

## Research evidence levels

The project distinguishes:

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

These levels are related but not interchangeable.

---

## Repository structure

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
├── FIELD_STATE_CONTRACT.md
├── DEMO_CATALOG.md
└── demos/
    └── README.md

pyproject.toml
README.md
LICENSE
```

The repository may grow as new responsibilities acquire explicit contracts, implementation boundaries, tests, and appropriate evidence.

---

## Installation

Requirements: **Python 3.10+** and `pip`.

```bash
python -m pip install -e ".[test]"
```

Run the test suite:

```bash
python -m pytest -q
```

The current v8.5 suite contains **15 contract-focused tests** for `FieldState`.

CI runs the same project contract across Python 3.10, 3.11, 3.12 and 3.13 on pushes to `main`/`develop` and pull requests targeting those branches.

---

## FieldState API

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

The complete contract is defined in `docs/FIELD_STATE_CONTRACT.md`.

---

## CI and engineering policy

`.github/workflows/ci.yml` checks out the repository, provisions supported Python versions, installs the package and test dependencies, and runs `pytest`.

CI is a regression guard for the implemented software contract. A green CI run must not be presented as scientific validation of ACRM's broader research direction.

---

## Future architecture

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

This is a **research/architectural direction**, not a claim that these components currently exist. Each future layer should define its responsibility, inputs/outputs, assumptions, failure modes, tests, and evaluation strategy before being promoted into the runtime.

---

## Development principles

1. **Observation is not inference.**
2. **Contracts precede complexity.**
3. **Implementation evidence is not scientific validation.**
4. **Prefer explicit and deterministic behavior.**
5. **Reject invalid state early.**
6. **Keep recording, relation detection, transition analysis, governance and intervention separated until their contracts justify integration.**
7. **Preserve prototypes as evidence without confusing them with production capabilities.**

---

## Contributing

Technical discussion, critical review and contributions are welcome. Substantial architectural changes should identify the problem, component responsibility, inputs/outputs, assumptions, failure modes, tests, and evaluation strategy.

## Research status

ACRM is an independent research project developed by **Ali Farahani**. The repository should be evaluated according to the implementation, documentation, tests, demonstrations, and evidence explicitly available in the project.

## License

See `LICENSE` for licensing information.
