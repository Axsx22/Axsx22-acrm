# ACRM — Adaptive Cognitive Regulation Module

**An independent research and engineering project for making observable, evaluable, and governable behavior in LLM-based cognitive systems explicit, inspectable, testable, and reproducible.**

ACRM is designed and developed by **Ali Farahani**, independent AI researcher and system architect, as part of a broader human–LLM collaborative research program.

The repository currently contains a concrete **ACRM v8.5 implementation foundation** centered on the immutable `FieldState` contract, together with a tested **Session C evolution implementation checkpoint**, executable unit tests, GitHub Actions CI, technical contracts, architecture records, research artifacts, roadmap documents, demonstrations, and stakeholder reporting.

> **Repository principle:** ACRM emerged iteratively through observation, questioning, hypothesis formation, interaction with multiple LLMs, architectural refinement, implementation, and testing. The repository therefore preserves both the research lineage and the concrete software artifacts that resulted from it.

---

## 1. What is ACRM?

ACRM (Adaptive Cognitive Regulation Module) is a research architecture concerned with how an LLM-based cognitive system can represent, observe, evaluate, and govern evolving system state and behavior.

The central research question is:

> **How can an LLM-based cognitive system remain observable, evaluable, and governable as its state, behavior, interactions, and internal processes evolve over time?**

The research connects several areas:

- LLM behavior and long-running interaction;
- cognitive-system architecture;
- state representation and temporal change;
- observability and evaluation;
- governance and controlled system evolution;
- human–LLM collaborative system design.

ACRM is an evolving architectural research program whose repository distinguishes clearly between implemented software, research artifacts, prototypes, demonstrations, and future architectural direction.

---

## 2. Architectural provenance and origin

### System designer

**Ali Farahani** is the system architect and researcher responsible for the architectural direction, integration, research framing, evaluation strategy, and final system-level decisions.

### How the architecture emerged

ACRM was not designed top-down from a complete initial specification. It emerged through a long-running empirical and collaborative process in which observations generated questions, questions generated hypotheses, and hypotheses were examined through implementation and experiment.

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

Multiple LLMs participated as analytical collaborators: ideas and interpretations could be compared across models, and model-generated critiques could themselves become inputs to further analysis.

### Formation conditions

The early research was conducted independently and under constrained practical conditions, using consumer hardware and extensive direct interaction with LLMs rather than a conventional academic laboratory or research team.

Historical research records are preserved because they explain how architectural questions and decisions emerged. They are maintained separately from the current implementation specification.

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

Accordingly, each repository artifact should be interpreted at the evidence level it actually supports.

---

## 4. Current implementation status — ACRM v8.5

The current repository contains a concrete, contract-driven v8.5 foundation together with a separately identifiable, tested **Session C evolution implementation checkpoint**. Session C extends the repository's executable research surface while preserving the FieldState contract as the canonical low-level observation layer.

The current implementation can be understood as:

```text
Recorded / supplied state
          │
          ▼
      FieldState
          │
          ▼
  Session C observation
          │
          ├── trajectory / dynamic analysis
          ├── topic inference
          ├── evolution readiness
          ├── candidate generation
          ├── test gate
          └── weighted specialist review
                     │
                     ▼
              evolution decision
```

### Implemented in the current v8.5 repository

#### FieldState foundation

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

#### Session C implementation checkpoint

The repository also contains an executable Session C implementation with:

- immutable observation records and an observation boundary;
- observation-log handling;
- trajectory profiling and dynamic-envelope estimation;
- threshold-approach and evolution-readiness evaluation;
- topic inference from observed context;
- evolution candidate representation and generation;
- explicit generation and test gates;
- weighted specialist review;
- deterministic evolution decisions including retain, reject, and switch-recommended outcomes;
- orchestration through `SessionCEngine`;
- dedicated unit tests covering the Session C components and boundaries.

Session C is an **engineering implementation checkpoint** within the current repository and is directly inspectable through its source code, contracts, and tests.

The Session C governance layer does not execute generated candidate source and does not itself perform runtime source switching. Candidate testing is represented through an explicit tester boundary; execution of candidate source is not part of the Session C core implementation.

Authoritative current-status documents:

- [`docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`](docs/ACRM_v8_5_DEVELOPMENT_STATUS.md)
- [`docs/FIELD_STATE_CONTRACT.md`](docs/FIELD_STATE_CONTRACT.md)
- [`docs/SESSION_C_IMPLEMENTATION_STATUS.md`](docs/SESSION_C_IMPLEMENTATION_STATUS.md)
- [`docs/SESSION_C_ARCHITECTURE.md`](docs/SESSION_C_ARCHITECTURE.md)

### Evidence boundary

The implemented software and its tests provide evidence about defined software behavior and contracts. They do not by themselves establish the effectiveness of broader research hypotheses, the scientific validity of inferred behavioral mechanisms, or superiority in real-world LLM deployments.

Higher-level capabilities such as relation detection, transition analysis, broader behavioral analysis, expanded governance, and intervention are treated as separate architectural layers requiring their own contracts, implementations, tests, and appropriate evaluation.

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

The Session C observation boundary preserves the same distinction at the next layer: observations are recorded before higher-level trajectory, topic, readiness, or evolution decisions are derived from them.

This boundary prevents higher-level hypotheses from silently becoming low-level data-model assumptions.

Likewise:

> **Temporal succession or correlation must not automatically be represented as causality.**

Software correctness and scientific validity are separate claims and require separate evidence.

---

## 6. Engineering and Investment Readiness

ACRM is being developed as a **research-driven deep-tech software architecture**, not as a conventional feature-level application. The purpose of investment at this stage is therefore not to manufacture a market-ready claim from an unvalidated prototype, but to move a concrete engineering foundation through the next evidence-producing development gates.

### 6.1 Why the project is investable at this stage

The repository provides an inspectable technical base from which additional research and engineering can be executed incrementally:

```text
Research question
       ↓
Explicit architecture
       ↓
Software contracts
       ↓
Working implementation
       ↓
Automated tests
       ↓
Reproducible CI
       ↓
Controlled experimental infrastructure
       ↓
Empirical evidence
       ↓
External validation
       ↓
Potential product / platform layer
```

The investment thesis is therefore **milestone-based**. Capital is intended to purchase increased experimental capability, evaluation depth, infrastructure reliability, and engineering throughput—not to substitute funding for evidence.

### 6.2 Current technical evidence

The present repository establishes several concrete engineering properties:

- immutable and validated state representation;
- explicit separation between observation and interpretation;
- contract-driven Session C evolution flow;
- dynamic-envelope and direction-aware readiness mechanisms;
- candidate generation and testing boundaries;
- weighted specialist review and deterministic decision handling;
- explicit non-execution boundary for generated candidate source;
- unit tests for core contracts and failure conditions;
- automated CI across Python 3.10–3.13;
- documented distinction between implementation evidence and scientific evidence.

These are **software-engineering claims supported by repository artifacts and tests**. They should not be confused with claims that ACRM has already demonstrated a general solution to autonomous cognition, behavioral regulation, or scientific hypotheses about LLMs.

### 6.3 Technical differentiation

The intended differentiation is architectural rather than dependent on a single model provider or model checkpoint.

ACRM is designed around an external, modular layer that can observe and evaluate evolving LLM-system state without requiring modification of model weights. Its architecture emphasizes:

1. **Observability before intervention** — measurement is separated from action.
2. **Evidence boundaries** — implementation, testing, demonstration, and scientific validation are explicitly distinguished.
3. **Temporal reasoning** — state is evaluated as trajectories rather than isolated snapshots.
4. **Dynamic envelopes** — readiness is relative to observed system history rather than fixed universal thresholds.
5. **Controlled evolution** — candidate generation, testing, review, and decision are separate gates.
6. **Non-invasive integration** — the governance layer is designed as an external architectural layer rather than a modification of transformer weights.
7. **Model independence** — the architecture is intended to remain meaningful across different underlying LLM implementations.

The repository does not claim that these properties are already a defensible commercial moat. Their potential defensibility must be established through implementation depth, empirical results, integration know-how, evaluation datasets, reproducible benchmarks, and eventual external adoption.

### 6.4 What additional capital is intended to unlock

Future investment should be tied to measurable technical milestones rather than open-ended development. Priority workstreams are:

| Workstream | Near-term objective | Evidence produced |
|---|---|---|
| Empirical evaluation | Execute controlled experiments across representative LLM configurations | Reproducible experiment results |
| Calibration | Estimate and validate dynamic-envelope parameters on real datasets | Calibration reports and benchmark results |
| Behavioral analysis | Implement and test relation/transition analysis as separate contracts | New unit/integration tests and evaluation datasets |
| Long-running runtime | Validate state persistence and temporal behavior over extended operation | Runtime logs, failure analysis, endurance results |
| Reproducibility | Package experiments so independent researchers can rerun them | Reproducibility bundle |
| Benchmarking | Compare ACRM-enabled and baseline configurations under defined protocols | Comparative metrics and statistical analysis |
| Engineering hardening | Improve observability, fault isolation, versioning, and deployment interfaces | Release-grade artifacts |

### 6.5 Milestone logic

A proposed funding program should be evaluated through gates such as:

```text
Gate 0 — Existing foundation
Contracts + implementation + tests + CI

Gate 1 — Experimental readiness
Controlled datasets + experiment harness + instrumentation

Gate 2 — Empirical signal
Repeatable behavioral measurements above predefined baselines

Gate 3 — Cross-model robustness
Replication across multiple model families/configurations

Gate 4 — Independent reproducibility
External researcher or engineering team reproduces material findings

Gate 5 — Productization decision
Evidence sufficient to justify a production/platform investment
```

Failure at an empirical gate is itself a valid research outcome. Funding should therefore be understood as purchasing **information and validated engineering capability**, not a guaranteed scientific conclusion.

### 6.6 Principal technical risks

A technically credible investment case must acknowledge the main uncertainties:

- observed behavioral patterns may not generalize across models;
- dynamic thresholds may require substantial calibration and may vary by task or deployment;
- long-running systems can accumulate state and failure modes not visible in short experiments;
- correlation and temporal succession may be mistaken for causal structure unless explicitly controlled;
- candidate generation does not imply candidate usefulness or safe deployment;
- external observability may have limited access to latent/internal model processes;
- engineering complexity may increase substantially when moving from checkpoint implementations to production-scale runtime infrastructure.

These risks are not hidden by the architecture. They define the experimental program required to reduce uncertainty.

### 6.7 Commercialization path

ACRM's potential commercialization should be treated as a staged hypothesis rather than an established market fact:

```text
Research infrastructure
        ↓
Evaluation / observability tooling
        ↓
Governance interfaces for long-running LLM systems
        ↓
Enterprise reliability / audit layer
        ↓
Potential platform or licensing model
```

Possible future value propositions include runtime observability, behavioral evaluation, governance instrumentation, controlled system evolution, auditability, and research infrastructure for long-running AI agents. Market demand, pricing, customer segment, and product-market fit require separate validation.

### 6.8 Intellectual-property and open-source position

The current open repository is intentionally evidence-oriented. Public code demonstrates architectural credibility and reproducibility. Potential future defensibility may instead emerge from the combination of:

- proprietary evaluation datasets and protocols;
- validated calibration methods;
- implementation and deployment know-how;
- specialized integrations;
- accumulated longitudinal behavioral data;
- benchmark methodology;
- production reliability engineering;
- and, where appropriate and legally supportable, patentable implementation details.

No claim of patent protection or proprietary moat is made by this repository unless separately documented.

### 6.9 Investment principle

> **ACRM does not ask an investor to fund a conclusion. It asks an investor to fund the controlled engineering and empirical process required to determine whether the architecture's hypotheses survive rigorous testing.**

This distinction is central to the project's credibility.

The objective of the next funding stage is to transform an already inspectable software foundation into a body of reproducible empirical evidence strong enough to support a subsequent technical, scientific, or commercial decision.

---

## 7. Current implementation boundaries

ACRM does **not** currently claim:

- a general behavioral inference engine;
- a complete causal analysis engine;
- scientifically validated dynamic thresholds;
- autonomous runtime governance across arbitrary LLM deployments;
- automatic production deployment of generated code;
- scientific validation of the broader ACRM research hypotheses;
- or product-market fit.

These are explicit future or validation targets rather than implied capabilities.

---

## 8. Repository evidence and reproducibility

The repository maintains an evidence-oriented structure so that technical reviewers can inspect the relationship between claims, implementation, tests, and research status.

Relevant documents include:

- `docs/IMPLEMENTATION_GAP_MATRIX.md`
- `docs/ENGINEERING_GOVERNANCE.md`
- `docs/testing/EPISTEMIC_INVARIANTS.md`
- `docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`
- `docs/SESSION_C_IMPLEMENTATION_STATUS.md`
- `docs/SESSION_C_ARCHITECTURE.md`
- `docs/FIELD_STATE_CONTRACT.md`

The project deliberately distinguishes **implemented**, **tested**, **demonstrated**, **specified**, and **validated** states. This distinction is part of the engineering governance model, not merely documentation style.

---

## 9. Roadmap

The next stage is not to maximize feature count. It is to maximize **evidence quality per engineering effort**.

Priority sequence:

1. empirical evaluation infrastructure;
2. calibration studies;
3. controlled multi-model experiments;
4. long-running runtime validation;
5. relation and transition contracts;
6. reproducibility package;
7. independent evaluation;
8. production-oriented architecture only after evidence justifies it.

This ordering is intentional: **evidence precedes scale, and validation precedes commercialization claims.**
