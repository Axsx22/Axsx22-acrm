# ACRM — Adaptive Cognitive Regulation Module

**An independent research and engineering project for making observable, evaluable, and governable behavior in LLM-based cognitive systems explicit, inspectable, testable, and reproducible.**

ACRM is designed and developed by **Ali Farahani**, independent AI researcher and system architect. The repository preserves both the research lineage and the executable software that has emerged from it.

> **Repository principle:** ACRM distinguishes historical observation, research hypothesis, architecture, software contract, implementation, software testing, and empirical validation. Passing a software test does not by itself establish a scientific claim.

### Repository engineering model

The repository uses a **main-first GitHub Flow** model. `main` is the single canonical integration branch; short-lived purpose-specific branches are used for engineering, testing, documentation, research, and audit work. There is no permanent `develop` branch.

Branch lifecycle, naming, historical-branch handling, and contribution expectations are defined in [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/BRANCHING.md](docs/BRANCHING.md).

---

## 1. What is ACRM?

ACRM is an external behavioral observability and governance architecture for long-running LLM interactions. It focuses on representing observable state, tracking behavioral trajectories, detecting change, and providing controlled governance signals without requiring modification of the underlying model weights or Transformer internals.

The central research question is:

> **How can an LLM-based cognitive system remain observable, evaluable, and governable as its state, behavior, interactions, and trajectories evolve over time?**

The current executable baseline is **not** a safety filter, policy engine, autonomous self-modifying system, or scientifically validated theory of cognition. The target Session C architecture includes a separately governed evolution lifecycle, but Runtime Injection, Version Switch, authorization, and controlled execution are not implemented in the current core.

### Architectural boundary

```
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
        │ Report              │
        └─────────────────────┘
              │
              │ structured observation/report
              ▼
   Separately authorized downstream layer
       (e.g. Safety / Governance)
              │
              ▼
       Policy-defined decision/action
```

The core principle is:

> **ACRM is designed to derive governance value from independent visibility, not from direct control of the model.**

ACRM consumes externally observable state, signals, or telemetry. It does not require access to model weights, attention layers, hidden execution mechanisms, or internal Transformer components. Stronger claims about latent cognition, causality, generalization, or effectiveness require independent empirical evidence.

### Observation is not judgment

A central boundary of the current architecture is that ACRM reports observable change without deciding whether that change is correct, incorrect, desirable, undesirable, safe, unsafe, or otherwise worthy of intervention.

For a long-running interaction, ACRM may identify and report a persistent directional change in the observed behavioral trajectory or interaction field. The report can describe properties such as:

- what changed;
- how the current trajectory relates to its observed history;
- the persistence and magnitude of the change;
- whether the change approaches or occupies a field-derived envelope;
- the evidence available for the observation.

It does **not** determine:

- whether the deviation is an error;
- whether the model or user caused it;
- whether the change represents improvement or degradation;
- whether an intervention should occur;
- or what action a downstream system should take.

The intended separation is:

```
Observation
    ≠
Interpretation
    ≠
Decision
    ≠
Action
```

ACRM therefore acts as an **observatory and reporting layer**. Its output may be consumed by separately authorized layers—such as Safety, Governance, monitoring, or other policy-defined systems—which may apply their own criteria and make decisions. ACRM itself remains responsible for the observation and characterization of the observed change, not for determining whether that change is right or wrong.

---

## 2. Why ACRM emerged

The project began with a narrower problem: detecting behavioral drift early enough to observe deviation before it became an explicit failure. Long-running interaction showed that individually acceptable changes can accumulate into a trajectory-level deviation that is not adequately represented by isolated point-in-time checks.

Within the research program this phenomenon is referred to as **Soft Drift**.

The architectural progression was therefore problem-driven:

```
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

The current `main` branch contains the executable v8.6 runtime integration, the immutable `FieldState` contract, Session C observation and controlled-evolution components, unit tests, packaging, and GitHub Actions CI.

### Current execution architecture

```
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
                │ externally observable runtime output
                ▼
       ┌───────────────────────┐
       │       Session C       │
       │  independent observer │
       └───────────┬───────────┘
                   │
          ┌────────┼─────────┐
          │        │         │
     trajectory  dynamic   topic / evolution
     profiling   envelope     analysis
          │        │         │
          └────────┼─────────┘
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
                   │
                   ▼
       separately authorized action
```

**Important architectural distinction:** Session C is **not a second implementation of the Runtime** and is not intended to reproduce or replace Runtime internals. Session C observes externally available Runtime outputs/events during execution and maintains its own observation, trajectory, dynamic-envelope, topic, candidate, and review representations.

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
- Runtime evaluation outputs and observation records that can be consumed by Session C; automatic continuous event subscription is not yet wired;
- unit coverage for the promoted execution path.

Historical browser/UI implementations remain preserved as evidence and lineage; the current executable source is represented in the Python core.

**Measurement semantics:** Current Runtime similarity, coherence, alignment-gap, and entropy outputs are lexical/statistical proxies. The legacy `FieldState.governance_confidence` value is populated from the complement of normalized lexical entropy; it is not a calibrated probability or specialist-consensus score. Built-in specialist reliability values and domain rules are fixed heuristics, not empirically measured accuracy estimates. See [docs/RUNTIME_MEASUREMENT_SEMANTICS.md](docs/RUNTIME_MEASUREMENT_SEMANTICS.md) for definitions, limitations, and required validation.

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

## 5. Session C — independent runtime observer and controlled evolution layer

Session C is designed as an **independent, continuously operating observer of the active Runtime**, with its own longitudinal evolution history. It does not duplicate Runtime internals or participate in the Runtime's ordinary turn-by-turn execution path.

The target lifecycle includes:

1. Receiving observable Runtime events/state during execution.
2. Maintaining an independent, append-only evolution history.
3. Analyzing trajectory and field changes over time.
4. Determining whether evidence is sufficient to open an evolution cycle.
5. Coordinating background candidate generation or code modification.
6. Sending the candidate through independent testing and weighted review.
7. Separately deciding the change route: **Runtime Injection** or **Version Switch**.
8. Separately deciding execution authorization: user authorization or a defined automatic policy gate.
9. Executing only after all required stages, then verifying the result and preserving rollback/audit evidence.

These are three different decisions:

- **Evidence decision:** Is a change justified?
- **Route decision:** Should the change be injected into the active Runtime or activated as a separate version?
- **Authorization decision:** Does the user authorize execution, or does a separately defined automatic policy gate permit it?

A weighted review is not execution authorization. `SWITCH_RECOMMENDED` is not a command to mutate or replace the active Runtime.

### Target architecture

```text
ACTIVE RUNTIME
      |
observable events / state
      v
SESSION C — independent continuous observer
      |
append-only evolution history
      |
trajectory / field analysis
      |
evidence sufficiency
      |
background candidate generation / modification
      |
independent testing
      |
weighted cross-layer review
      |
change-route decision
      |--------------------------|
      v                          v
Runtime Injection           Version Switch
      |                          |
      +------------+-------------+
                   v
          authorization decision
             |             |
             v             v
            user       automatic policy
             |             |
             +------+------+
                    v
          controlled execution
                    |
          verification / rollback
```

### Current implementation on `main`

The current code contains the observation data type and in-memory log, trajectory and dynamic-envelope primitives, constrained topic inference, candidate representation, callback-based generation/testing, and weighted review. Runtime evaluation also emits observation records.

However, the current `SessionCEngine` is initialized from a supplied observation collection and snapshots it. The full live Runtime → Session C event subscription, durable independent history, complete evidence-sufficiency contract, Runtime Injection/Version Switch route selection, user/automatic authorization, controlled execution, and rollback are **not yet implemented**.

The current candidate tester is an injected callback; the core does not provide a code-execution sandbox. Current trajectory persistence based on repeated observation kinds must not be interpreted as numerical signal persistence or semantic/behavioral persistence.

For the complete target contract and implementation-status matrix, see [docs/SESSION_C_ARCHITECTURE.md](SESSION_C_ARCHITECTURE.md) and [docs/SESSION_C_IMPLEMENTATION_STATUS.md](SESSION_C_IMPLEMENTATION_STATUS.md).

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

```
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

Session C validation should additionally cover:

- Runtime → Session C observation isolation;
- independent Session C state and lifecycle behavior;
- temporal/trajectory observation under normal and adversarial sequences;
- dynamic tolerance and readiness boundaries;
- candidate generation, including code-bearing candidates;
- independent candidate test behavior;
- failed-test retry and review behavior;
- specialist vote weighting and decision thresholds;
- `SWITCH_RECOMMENDED` without automatic Runtime mutation;
- separation between recommendation and external authorization;
- malformed or conflicting candidate/review inputs;
- resource and isolation properties where production deployment requires them.

These tests establish software behavior against defined contracts. They do not establish scientific validity, generalization, or production effectiveness.

---

## 10. Research and engineering roadmap

The next stages are evidence-driven rather than claim-driven.

### Near-term engineering priorities

1. Integrate provider adapters into a controlled evaluation path.
2. Execute reproducible API/GPU-backed experiments across representative LLM configurations.
3. Expand adversarial and long-horizon validation of the Session C observer boundary and evolution workflow.
4. Reconcile and promote the strongest Session C hardening/validation work into the main baseline.
5. Synchronize documentation and version identity around v8.6.
6. Develop separate contracts for higher-level relation/transition/behavioral analysis before implementation.
7. Establish reproducible benchmark protocols and external evaluation.

### Longer-term research direction

Potential future layers include broader behavioral characterization, relation/transition analysis, expanded governance, intervention interfaces, and controlled evolution mechanisms. These remain subject to separate contracts, implementation, testing, and empirical evidence.

---

## 11. Investment, infrastructure & collaboration

ACRM is currently at the transition from an **architecturally developed research prototype** toward **empirical validation**.

The next meaningful step is not simply adding architectural complexity. It is evaluating the implemented system against real LLM workloads under controlled, reproducible conditions.

This requires access to:
- model/provider APIs;
- GPU-backed inference where self-hosted or open-weight models are appropriate;
- evaluation and experiment infrastructure;
- telemetry, trace, and reproducibility tooling;
- software/evaluation engineering capacity;
- long-horizon and adversarial interaction workloads;
- independent evaluation and replication.

The intended progression is:

```
implemented architecture
        ↓
API / GPU evaluation environment
        ↓
controlled real-model experiments
        ↓
long-horizon + adversarial evaluation
        ↓
reproducible benchmark evidence
        ↓
independent validation
        ↓
evidence-based decisions about further development
```

The immediate research questions concern whether ACRM can reliably characterize persistent directional change in long-running interaction fields, its false-positive/false-negative behavior, its robustness across models/providers, and whether the Runtime/Session C observer boundary remains isolated under adversarial conditions.

These are **research questions, not established product claims**.

Resource requirements should therefore be milestone-driven:

1. **Experimental foundation** — provider integration, evaluation harness, trace/telemetry contracts, baselines.
2. **Controlled validation** — API/GPU experiments, long-horizon workloads, adversarial sequences, ablation studies, quantitative error analysis.
3. **Independent evaluation** — replication, cross-provider/model testing, robustness and failure analysis.
4. **Engineering decision** — use measured evidence to determine whether further investment should target production integration, broader evaluation, additional governance layers, or a revised research direction.

Investment or infrastructure support would primarily increase execution capacity, experimental scale, reproducibility, validation depth, and engineering throughput.

The project does **not** currently claim production effectiveness, universal model generalization, scientific proof of its cognitive hypotheses, autonomous self-improvement, product-market fit, or production safety certification solely from repository evidence.

The detailed resource requirements, validation program, collaboration models, and evidence milestones are documented in [docs/INVESTMENT.md](docs/INVESTMENT.md).

**Current requirement:** API/model access + GPU/inference infrastructure + evaluation engineering + controlled real-world interaction traces.

## 12. Repository map

```
acrm_core/
├── runtime/       # Current executable behavioral runtime integration
├── field/         # Canonical FieldState contract
└── session_c/     # Independent observer + controlled evolution implementation

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

**Current architectural focus: executable behavioral runtime + independent Session C observation + controlled candidate evolution/review + preparation for real provider/API-backed empirical evaluation.**
