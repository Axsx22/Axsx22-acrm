# ACRM v8.5 Development Status

**Status:** Active development  
**Repository role:** Research-to-runtime engineering checkpoint

## 1. Current status

ACRM v8.5 establishes the immutable `FieldState` runtime contract as its canonical low-level state foundation and includes an executable **Session C evolution implementation checkpoint**.

**Session C is still under active development.** The current implementation is therefore reviewable and testable, but should not be interpreted as a frozen final Session C specification.

The repository currently contains:

- Python package configuration in `pyproject.toml`;
- the `acrm_core` package;
- the immutable and validated `FieldState` implementation;
- Session C observation, dynamic-analysis, topic, evolution, and orchestration components;
- dedicated unit tests for FieldState and Session C contracts and boundaries;
- GitHub Actions CI.

## 2. Implemented scope

### FieldState foundation

`FieldState` represents recorded state and validates its structural contract. The implementation covers:

- non-empty `field_id` and `session_id`;
- non-negative integer sequence values;
- timezone-aware timestamps;
- finite numeric metrics;
- immutable metric storage;
- non-empty failure-mode identifiers;
- duplicate failure-mode rejection;
- `governance_confidence` in the inclusive range `[0.0, 1.0]`;
- deterministic metric and failure-mode access;
- UTC normalization of recorded timestamps.

### Session C implementation checkpoint

The repository contains a tested Session C implementation covering:

- a neutral append-only observation boundary;
- observation-log handling;
- trajectory profiling;
- field-relative dynamic-envelope estimation;
- explicit high/low signal direction;
- threshold-approach and evolution-readiness evaluation;
- constrained topic inference;
- evolution candidate representation and generation;
- explicit generation and test gates;
- weighted specialist review;
- deterministic evolution decisions;
- orchestration through `SessionCEngine`.

Session C is an **active engineering implementation checkpoint**. Components may be refined as the architecture is completed. Current behavior must be judged against the code, contracts, tests, and the explicit maturity classification in `docs/SESSION_C_IMPLEMENTATION_STATUS.md`.

## 3. Maturity and evidence levels

| Level | Meaning |
|---|---|
| Implemented | Executable behavior or an explicit runtime contract exists. |
| Tested | Automated tests verify defined software behavior. |
| Evolving | Implemented behavior is still being refined and should not be treated as final architecture. |
| Specified | Architecture/contract is documented but is not necessarily present in the runtime. |
| Empirical | Requires controlled measurements beyond unit tests. |
| Independent | Requires external reproduction or review. |
| Future | Not currently part of the v8.5 runtime. |

These levels are deliberately non-interchangeable. A green test does not promote an empirical hypothesis to a scientific result.

## 4. Explicit boundaries

`FieldState` does not determine causes, infer meaning, establish causality, infer behavioral patterns, decide transitions, make decisions, or perform interventions.

Session C does not expose a runtime source-switching API and does not execute generated candidate source as part of its core implementation. Candidate testing is represented through an explicit tester boundary.

Higher-level concerns remain subject to explicit contracts, implementations, tests, and appropriate evaluation before stronger implementation or scientific claims are made.

## 5. Important current semantics

The current dynamic envelope derives warning and critical limits from historical numeric observations using configurable quantiles. It is therefore an **empirical field-relative envelope**; the repository does not claim universal calibration of those parameters.

The current trajectory persistence descriptor is based on recurrence of observation kinds. This is an implementation-level descriptor and should not automatically be interpreted as persistence of an underlying behavioral signal.

The current topic engine uses a constrained observation-kind-to-topic mapping. It is not a claim that the complete semantic topic ontology has been implemented.

These points are active development boundaries, not evidence that the overall Session C architecture is complete or defective.

## 6. Verification boundary

Passing unit tests demonstrate compliance with defined software contracts and component behavior. They do not validate broader scientific or behavioral claims about ACRM or AI systems.

The current repository contains **44 unit-test functions** across the five dedicated FieldState and Session C test modules currently present on `main`. Repository CI is the authoritative integration check.

## 7. CI

GitHub Actions runs the test suite on Python 3.10 through 3.13 for pushes and pull requests targeting `main` or `develop`.

## 8. Current architecture boundary

The implemented repository should currently be understood as:

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

This does **not** imply that the complete Relation → Transition → Analysis → Governance → Intervention architecture has been implemented.

## 9. Next development layers

Potential future layers include relationships between observations, explicit transition modeling, broader behavioral analysis, governance expansion, and intervention. Each layer should receive an explicit responsibility, interface, testable contract, and validation strategy before becoming part of the promoted runtime.

For the active Session C work, the governing objective is **completion without premature promotion**: implement and test each capability, document its current semantics and limitations, and only then promote it to a stable architectural claim.
