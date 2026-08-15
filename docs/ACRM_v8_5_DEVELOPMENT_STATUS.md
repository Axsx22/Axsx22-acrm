# ACRM v8.5 — Development Status

**Status:** Incremental implementation — FieldState contract implemented

## Scope

ACRM v8.5 is being developed as an incremental research implementation.

The current implemented path establishes the runtime `FieldState` contract
and its unit-test coverage. The repository intentionally does not claim
future runtime, temporal, failure-mode, governance, or experimental
components as implemented unless they are explicitly present and documented.

## Currently implemented

### 1. FieldState runtime contract

The repository currently implements:

- immutable `FieldState` snapshots;
- `field_id` validation;
- `session_id` validation;
- non-negative integer sequence validation;
- timezone-aware timestamps;
- explicit timestamps for deterministic testing and replay;
- finite numeric metric validation;
- immutable metric storage;
- failure-mode identifier validation;
- duplicate failure-mode detection;
- governance-confidence validation in the range `[0.0, 1.0]`;
- deterministic metric and failure-mode access.

### 2. FieldState contract documentation

The implementation boundary and non-responsibilities of `FieldState` are
documented in:

`docs/FIELD_STATE_CONTRACT.md`

The contract intentionally keeps higher-level temporal, failure-mode,
governance, and intervention responsibilities outside `FieldState`.

### 3. Test coverage

The current FieldState implementation is covered by unit tests in:

`tests/unit/test_field_state.py`

The current test suite contains 33 passing tests.

## Explicitly not yet implemented

The following components are not claimed as implemented by this repository
unless corresponding source code and tests are added:

- Runtime Field / Stream;
- ordering between multiple snapshots;
- session-continuity enforcement across snapshots;
- temporal-direction analysis;
- state-transition policy;
- canonical metric semantics and units;
- failure-mode taxonomy and registry;
- governance evaluation;
- model intervention;
- continuous runtime regulation;
- experimental verification and benchmark evaluation.

These are future implementation or evaluation layers and must not be
inferred from the existence of the `FieldState` contract alone.

## Architectural boundary

The current architecture should be understood as:

```text
                    FieldState
                         |
                         v
             immutable observation
                         |
                         v
              Higher-level runtime
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Temporal        Failure       Governance
       Analysis        Taxonomy      Evaluation
