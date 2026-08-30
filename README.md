# ACRM — Adaptive Cognitive Regulation Module

**An independent research-oriented architecture for studying observable, evaluable, and governable behavior in LLM-based cognitive systems.**

ACRM is developed by **Ali Farahani**, Independent AI Researcher & System Architect, as part of a broader research program on human–LLM collaborative cognitive systems.

> **Important:** This repository is intentionally explicit about the boundary between implemented software, prototypes, research artifacts, and future architecture. The presence of a dashboard, experiment, or conceptual design does not by itself mean that the corresponding capability is implemented in the ACRM v8.5 core.

---

## Stakeholder reporting

The repository maintains a dated, stakeholder-facing executive update alongside the detailed engineering and research records.

**Current reporting period: 23–30 Aug 2026 · Overall status: 🟢 GREEN**

- **[Executive stakeholder update](docs/STAKEHOLDER_UPDATE_2026-08-30.md)** — shipped work, RAG risks, next 30-day focus, and decisions needed.
- **[Executive PowerPoint deck](docs/ACRM_Executive_Update_2026-08-30.pptx)** — one-slide presentation version for stakeholder / steering-committee use.
- **[Stakeholder reporting policy](docs/STAKEHOLDER_REPORTING.md)** — reporting scope, evidence boundary, naming convention, and synchronization policy.

The executive update is a communication artifact and does not replace technical contracts, tests, development-status records, or research evidence. Stakeholder claims must remain proportional to the evidence actually present in the repository.

---

## What is ACRM?

ACRM (Adaptive Cognitive Regulation Module) is a research architecture concerned with how an LLM-based cognitive system can represent and study its evolving state and behavior over time.

The central research question is:

> **How can LLM-based cognitive systems be designed so that their behavior, state, changes, interactions, and processes remain observable, evaluable, and governable over time?**

This question connects several research domains:

- LLM behavior and long-term interaction
- cognitive systems and persistent agents
- state representation and temporal change
- observability and evaluation
- governance and system evolution
- human–LLM collaborative system design

The broader research program treats the system as an evolving process rather than only as an isolated sequence of model responses.

---

## Research context

ACRM is one of the principal architectures in a larger independent research program. That program has moved through a recurring cycle:

```text
Observation
    ↓
Question
    ↓
Hypothesis
    ↓
Concept
    ↓
Architecture
    ↓
Prototype
    ↓
Experiment
    ↓
Observation
    ↓
Revision
    ↓
New Architecture
```

The research has produced architectural designs, executable prototypes, tests, experiments, dashboards, demonstrations, and technical documentation. Observability is treated as a research capability rather than merely a UI concern.

The current research direction is to move from independently developed prototypes toward a more scalable, reviewable, reproducible, and externally evaluable research program.

---

## Human–LLM collaborative research model

A distinctive part of the research program is its human–LLM collaborative structure.

```text
Human System Architect
        │
        ▼
Collaborative interaction with multiple LLMs
        │
        ▼
Analysis · critique · comparison · scenario exploration
        │
        ▼
Architectural decision
        │
        ▼
Implementation · experimentation · observation
        │
        ▼
Revision
        └──────────────→ next research cycle
```

The human researcher remains responsible for problem framing, architectural decisions, integration, evaluation, research direction, and final system-level decisions. Language models participate as research partners for analysis, critique, idea generation, review, scenario analysis, and solution exploration.

This repository documents the resulting software and selected technical artifacts; it does not claim that model-generated material constitutes independent scientific validation.

---

## ACRM v8.5 — current implementation

The current repository deliberately keeps the v8.5 core small and contract-driven.

```text
Recorded / supplied state
          │
          ▼
      FieldState
          │
          ▼
 Future higher-level layers
```

`FieldState` is a validated, immutable representation of a **recorded state**. It is not an inference engine, causal engine, decision system, or intervention mechanism.

### Implemented in v8.5

- immutable `FieldState` snapshots;
- non-empty `field_id` and `session_id` validation;
- non-negative integer sequence validation;
- timezone-aware timestamp validation;
- finite numeric metric validation;
- read-only metric storage;
- failure-mode identifier validation and duplicate rejection;
- `governance_confidence` validation in `[0.0, 1.0]`;
- deterministic metric and failure-mode access;
- UTC-normalized timestamp access;
- contract-focused unit tests;
- Python packaging;
- automated GitHub Actions CI on Python 3.10–3.13.

See:

- [`docs/FIELD_STATE_CONTRACT.md`](docs/FIELD_STATE_CONTRACT.md)
- [`docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`](docs/ACRM_v8_5_DEVELOPMENT_STATUS.md)

### What v8.5 does not currently claim

The core does **not** currently claim to implement a complete behavioral inference stack, causal analysis engine, autonomous governance controller, intervention engine, or scientifically validated cognitive model.

Potential future layers such as relation detection, transition analysis, behavioral analysis, governance, and intervention require their own explicit contracts, implementations, tests, and evaluation evidence before they become core capabilities.

---

## Architectural boundary: observation is not interpretation

A fundamental engineering principle in ACRM is the separation of recorded state from interpretation.

`FieldState` records and validates supplied state. It does not decide:

- why a state exists;
- what caused it;
- what the state means;
- how observations are related;
- whether a transition occurred;
- which behavioral pattern should be inferred;
- which decision should be made;
- or which intervention should be performed.

This boundary is intentional. It prevents higher-level hypotheses from silently becoming low-level data-model assumptions.

Likewise:

> **Correlation or temporal succession must not automatically be represented as causality.**

Software tests establish compliance with software contracts. They do not, by themselves, establish scientific validity of the broader research hypotheses.

---

## From prototype to evidence

The research program distinguishes several levels of evidence:

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
    ↓
Independent reproduction
```

These levels are related but not interchangeable.

A prototype demonstrates that a design was implemented or exercised. A passing unit test demonstrates compliance with a software contract. Neither automatically establishes the truth of a broader behavioral or scientific hypothesis.

---

## Prototypes, dashboards, and research archive

The ACRM research history includes interactive dashboards and executable prototypes covering ideas such as:

- interaction-field visualization;
- behavioral runtime state;
- temporal state and trajectory observation;
- calibration and invariant testing;
- failure-mode taxonomies;
- quality-control and consensus concepts;
- observability and system-state visualization.

These artifacts are valuable because they preserve architectural experiments and show how concepts evolved. They are intentionally separated from the v8.5 core until a capability has a clear contract and corresponding implementation and tests.

See [`docs/DEMO_CATALOG.md`](docs/DEMO_CATALOG.md) for the reviewed artifact inventory and [`docs/demos/README.md`](docs/demos/README.md) for the archive policy.

### Evidence rule

A dashboard may contain sophisticated UI, simulated values, browser-side algorithms, or an apparent runtime. That is evidence of a prototype—not automatically evidence of a production backend, scientific validation, or a current v8.5 implementation.

This distinction is a deliberate part of the repository's transparency policy.

---

## Research and technical layers

The broader program can be understood as several connected but distinct layers:

```text
Theoretical Layer
  research questions · concepts · hypotheses
          ↓
Architectural Layer
  ACRM · PCS · related architectures
          ↓
Execution Layer
  prototypes · executable systems
          ↓
Experimental Layer
  tests · scenarios · experiments
          ↓
Observability Layer
  dashboards · state observation · visualization
          ↓
Documentation Layer
  contracts · architecture · research records
          ↓
Historical Layer
  version history · design evolution · research archive
```

ACRM v8.5 currently occupies the **implementation/contract foundation** of this larger research structure rather than representing the entire program.

---

## Relationship to PCS and related architectures

ACRM and PCS are two major architectures within the broader research program. Other concepts have emerged around memory, state, observability, evaluation, control, interaction, persistence, governance, and system evolution.

Some of these may eventually become independent subsystems or separate research projects. They are not automatically part of the ACRM v8.5 runtime simply because they appear in historical designs or demonstrations.

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
├── STAKEHOLDER_REPORTING.md
├── STAKEHOLDER_UPDATE_2026-08-30.md
├── ACRM_Executive_Update_2026-08-30.pptx
└── demos/
    └── README.md

pyproject.toml
README.md
LICENSE
```

As the project evolves, new components should be introduced through the same discipline: define the responsibility, establish a contract, implement it, test it, document assumptions and failure modes, and identify the evidence level.

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

CI runs the project contract across Python 3.10, 3.11, 3.12, and 3.13 on pushes to `main`/`develop` and pull requests targeting those branches.

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

`.github/workflows/ci.yml` provisions supported Python versions, installs the package and test dependencies, and runs the test suite.

CI is a regression guard for the implemented software contract. A green CI run must not be presented as scientific validation of ACRM's broader research direction.

---

## Development principles

1. **Observation before conclusion.**
2. **Experimentation before generalization.**
3. **Contracts precede complexity.**
4. **Architectures should be implementable.**
5. **Systems should be observable.**
6. **Implementation evidence is not scientific validation.**
7. **Keep recording, relation detection, transition analysis, governance, and intervention separated until their contracts justify integration.**
8. **Preserve research history and prototype provenance.**
9. **Prefer explicit, deterministic, reviewable behavior.**
10. **Make claims proportional to available evidence.**

---

## Future architecture

A possible future direction is:

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

This is a **research and architectural direction**, not a claim that these components currently exist in the v8.5 runtime.

Each future layer should define its responsibility, inputs and outputs, assumptions, failure modes, tests, and evaluation strategy before being promoted into the core.

---

## Current research stage

The broader program has progressed beyond idea-only research: it includes architectural designs, working prototypes, local execution, experimentation, dashboards, demonstrations, testing, and extensive documentation.

The next major transition is from independently developed prototype research toward:

```text
Architectural stabilization
        ↓
Scale and longer execution
        ↓
Longitudinal data generation
        ↓
Systematic analysis
        ↓
Independent evaluation
        ↓
Reproducibility
        ↓
Research collaboration
        ↓
Scientific / technical publication
```

Current known gaps include scale, compute and API capacity, longitudinal data, external collaboration, independent validation, reproducibility, publication, and infrastructure. These are documented as research constraints rather than hidden limitations.

---

## Researcher

**Ali Farahani** is the independent AI researcher and system architect responsible for the research direction and system-level architecture.

The broader research program has been developed through a sustained human–LLM collaborative process. The human role includes problem framing, architectural design, integration, evaluation, research direction, experimental design, and final system-level decisions.

The repository should be evaluated against the artifacts and evidence actually present in the project, rather than against claims implied by historical prototypes or future plans.

---

## Contributing and critical review

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

Critical review is part of the intended development process. The goal is not to eliminate criticism but to make the project's assumptions, boundaries, evidence, and limitations explicit enough to be reviewed constructively.

---

## License

See `LICENSE` for licensing information.
