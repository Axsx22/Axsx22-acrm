# ACRM — Adaptive Cognitive Regulation Module

**An independent research and engineering project for making observable, evaluable, and governable behavior in LLM-based cognitive systems explicit, inspectable, testable, and reproducible.**

ACRM is designed and developed by **Ali Farahani**, independent AI researcher and system architect. The repository preserves both the research lineage and the executable software that has emerged from it.

> **Repository principle:** ACRM distinguishes historical observation, research hypothesis, architecture, software contract, implementation, software testing, and empirical validation. Passing a software test does not by itself establish a scientific claim.

---

## 1. What is ACRM?

ACRM is an external behavioral observability and governance architecture for long-running LLM interactions. It focuses on representing observable state, tracking behavioral trajectories, detecting change, and providing controlled governance signals without requiring modification of the underlying model weights or Transformer internals.

The central research question is:

> **How can an LLM-based cognitive system remain observable, evaluable, and governable as its state, behavior, interactions, and trajectories evolve over time?**

ACRM is intentionally **not** presented as a safety filter, policy engine, autonomous self-modifying system, or scientifically validated theory of cognition.

### Architectural boundary

```text
Primary human ↔ AI interaction
              │
              │ observable state / signals
              ▼
        ┌─────────────────────┐
        │        ACRM         │
        │ Observe             │
        │ Measure             │
        │ Analyze             │
        │ Characterize        │
        │ Govern / Report     │
        └─────────────────────┘
              │
              ▼
     Separately authorized action
```

The core principle is:

> **ACRM is designed to derive governance value from independent visibility, not from direct control of the model.**

ACRM consumes externally observable state, signals, or telemetry. It does not require access to model weights, attention layers, hidden execution mechanisms, or internal Transformer components. Stronger claims about latent cognition, causality, generalization, or effectiveness require independent empirical evidence.

---

## 2. Why ACRM emerged

The project began with a narrower problem: detecting behavioral drift early enough to observe deviation before it became an explicit failure. Long-running interaction showed that individually acceptable changes can accumulate into a trajectory-level deviation that is not adequately represented by isolated point-in-time checks.

Within the research program this phenomenon is referred to as **Soft Drift**.

The architectural progression was therefore problem-driven:

```text
Drift detection
      ↓
Early / pre-failure detection
      ↓
Long-running interaction
      ↓
Soft Drift
      ↓
Trajectory observation
      ↓
Independent behavioral observability
      ↓
Measurement → Analysis → Characterization
      ↓
Governance / reporting signal
      ↓
Controlled evolution research
```

The repository preserves this history while keeping historical artifacts separate from claims about the current executable system.

---

## 3. Current implementation — ACRM v8.6

**Current package/runtime version: `8.6.0`.**

The current `main` branch contains the executable v8.6 runtime integration, the immutable `FieldState` contract, Session C governance/evolution components, unit tests, packaging, and GitHub Actions CI.

### Current execution architecture

```text
Observed / supplied interaction state
                │
                ▼
        ACRM Field Runtime
                │
        ┌───────┴────────┐
        │                │
   Field metrics    Specialist governance
        │                │
        └───────┬────────┘
                ▼
           FieldState
                │
                ▼
        Session C observation
                │
        ┌───────┼──────────────────┐
        │       │                  │
   trajectory  dynamic        topic/evolution
   profiling   envelope           analysis
        │       │                  │
        └───────┴──────────┬───────┘
                           ▼
                   evolution readiness
                           │
                           ▼
                  candidate generation
                           │
                           ▼
                       test gate
                           │
                           ▼
                  weighted specialist review
                           │
                           ▼
                retain / reject / switch-recommended
```

### v8.6 runtime integration

The v8.6 runtime promotes the previously developed v7 Behavioral Runtime Field and v8.3 Specialist Reasoning Governance into executable Python under `acrm_core/runtime/`.

The integrated runtime includes:

- v7 failure-mode taxonomy and calibration/sanity layer;
- sequential turn inspection;
- centroid coherence and alignment-gap analysis;
- entropy and baseline-deviation measurements;
- runtime `FieldState` production;
- v8.3 specialist applicability/diagnosis/reporting;
- weighted evidence and balance handling;
- persistence and reporting state;
- explicit runtime → neutral Session C observation bridge;
- unit coverage for the promoted execution path.

Historical browser/UI implementations remain preserved as evidence and lineage; the current executable source is represented in the Python core.

---

## 4. FieldState: canonical observation contract

`FieldState` is the low-level immutable observation contract used by the current runtime.

It provides validated snapshots with properties including:

- non-empty `field_id` and `session_id`;
- non-negative integer sequence numbers;
- timezone-aware timestamps;
- finite numeric metrics;
- read-only metric storage;
- unique failure-mode identifiers;
- bounded `governance_confidence` in `[0.0, 1.0]`;
- deterministic metric/failure-mode access;
- UTC-normalized timestamps.

`FieldState` does **not** establish causality, explain why a state exists, or decide what intervention should occur. It records and validates the state supplied to it.

This distinction is fundamental:

> **Observation is not interpretation. Correlation or temporal succession is not automatically causality.**

---

## 5. Session C — controlled evolution layer

Session C is the current controlled-evolution research/engineering layer.

Its architecture separates:

```text
Observation
    ↓
Trajectory / envelope analysis
    ↓
Readiness
    ↓
Topic relevance
    ↓
Candidate generation
    ↓
Independent test gate
    ↓
Topic-aware weighted specialist review
    ↓
Evolution decision
```

The current implementation deliberately maintains a hard boundary between candidate generation/testing and the active runtime.

### What Session C currently does

- records neutral, immutable observations;
- accumulates trajectory context;
- estimates dynamic envelopes from observed history;
- evaluates threshold approach and evolution readiness;
- infers relevant evolution topics from observed context;
- represents and generates candidates through explicit interfaces;
- applies deterministic testing/readiness gates;
- performs weighted specialist review;
- returns controlled decisions such as retain, reject, or switch-recommended.

### What Session C does not claim to do

- it does not execute generated source as part of the core governance path;
- it does not automatically mutate the active runtime;
- it does not prove autonomous self-evolution;
- it does not establish scientific validity of the underlying behavioral hypotheses.

The current Session C implementation is therefore best described as a **controlled evolution supervisor / engineering checkpoint**, not an autonomous self-modifying runtime.

---

## 6. Provider integration boundary

A provider-neutral chat contract has also been developed on a dedicated branch, with standard-library HTTP adapters for:

- OpenAI-compatible endpoints, including vLLM-style deployments;
- Anthropic Messages API.

These adapters are deliberately separated from the core observation/governance contracts and include mocked contract tests.

**They are not yet part of the current `main` runtime baseline.** Their integration is a next engineering step for real API/GPU-backed evaluation.

---

## 7. Calibration, QCS, and research artifacts

The repository contains several intentionally separated research/architecture tracks.

### Calibration

The research calibration harness implements deterministic invariant checks and numerical safeguards. It remains separated from `acrm_core` until the required empirical contracts and evidence exist.

### QCS

The ACRM-QCS formal architecture documents independent inspection stations, consensus, and root-cause analysis. It is an architecture/research artifact, not a claim that the complete QCS architecture is already implemented in the runtime.

### Unconscious Bridge hypothesis

The historical Unconscious / Bridge concept is preserved as a testable research hypothesis. Metaphysical or unverified claims are intentionally kept outside the implementation boundary.

### Historical source archive

The repository also preserves checksums and provenance for historical ACRM source artifacts, including earlier Python, HTML, calibration, demo, dashboard, and v7/v8.3 materials. These records are preservation checkpoints and should not be confused with the current executable core.

---

## 8. Evidence boundary

ACRM uses the following maturity distinction:

```text
Historical observation
        ↓
Research question
        ↓
Hypothesis
        ↓
Conceptual architecture
        ↓
Software contract
        ↓
Implementation
        ↓
Software testing
        ↓
Empirical evaluation
        ↓
Independent reproduction
```

These levels are **not interchangeable**.

- A historical artifact records what was explored.
- A hypothesis proposes something to investigate.
- An architecture describes a proposed mechanism.
- A contract defines testable software behavior.
- An implementation demonstrates that code exists.
- Software tests establish behavior against the defined contract.
- Empirical evaluation tests broader behavioral/research claims.
- Independent reproduction provides stronger external evidence.

The repository therefore avoids treating a passing unit test, dashboard, demo, or architectural document as proof of a broader scientific claim.

---

## 9. Testing and CI

The repository uses automated Python testing and GitHub Actions CI.

The current CI matrix covers:

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

The latest validated `main` checkpoint is tested across this matrix.

The test suite should be interpreted as **software validation**, not as a substitute for empirical validation of ACRM's research hypotheses.

---

## 10. Research and engineering roadmap

The next stages are evidence-driven rather than claim-driven.

### Near-term engineering priorities

1. Integrate provider adapters into a controlled evaluation path.
2. Execute reproducible API/GPU-backed experiments across representative LLM configurations.
3. Expand adversarial and long-horizon validation of Session C.
4. Reconcile and promote the strongest Session C hardening/validation work into the main baseline.
5. Synchronize documentation and version identity around v8.6.
6. Develop separate contracts for higher-level relation/transition/behavioral analysis before implementation.
7. Establish reproducible benchmark protocols and external evaluation.

### Longer-term research direction

Potential future layers include broader behavioral characterization, relation/transition analysis, expanded governance, intervention interfaces, and controlled evolution mechanisms. These remain subject to separate contracts, implementation, testing, and empirical evidence.

---

## 11. Investment / collaboration position

ACRM is a **research-driven deep-tech software architecture**, not a conventional feature-level application.

The current repository provides an inspectable engineering foundation from which additional research can be executed incrementally. The immediate value of additional engineering resources is therefore to increase:

- experimental capability;
- API/GPU infrastructure;
- evaluation depth;
- reproducibility;
- testing capacity;
- integration throughput;
- and independent validation.

The project does not claim that commercial defensibility, scientific validity, or production readiness has already been established. Those are future evidence milestones.

Potential collaborators can contribute as engineering, evaluation, infrastructure, QA, research, or strategic partners without being represented as employees of the project unless a formal employment relationship exists.

---

## 12. Repository map

```text
acrm_core/
├── runtime/       # Current executable behavioral runtime integration
├── field/         # Canonical FieldState contract
└── session_c/     # Controlled evolution / Session C implementation

 tests/             # Software and contract tests
 research/          # Research-only calibration and experimental contracts
 docs/              # Architecture, status, contracts, roadmap, and evidence boundary
 archive/           # Historical source inventories and preservation records
 demos/             # Demonstrations and historical execution evidence
 .github/workflows/ # Automated CI
```

For implementation details, inspect the source and the corresponding contracts/tests together. The README is an orientation document; source code, tests, and status/architecture documents are authoritative for the exact behavior of individual components.

---

## 13. License and status

ACRM is an independent research and engineering project. The repository contains a mixture of executable software, research artifacts, historical material, and architecture documents; each should be interpreted according to its documented evidence level.

**Current baseline: ACRM v8.6.0**

**Primary branch: `main`**

**Current architectural focus: executable behavioral runtime + controlled Session C evolution + preparation for real provider/API-backed empirical evaluation.**
