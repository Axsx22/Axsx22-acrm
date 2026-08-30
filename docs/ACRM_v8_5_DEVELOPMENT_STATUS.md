# ACRM v8.5 Development Status

## Status

ACRM v8.5 currently establishes the `FieldState` runtime contract as its first implemented core component.

The repository now contains:

- a Python package configuration in `pyproject.toml`;
- the `acrm_core` package;
- the immutable and validated `FieldState` implementation;
- unit tests for the FieldState contract;
- a GitHub Actions CI workflow.

## Implemented scope

`FieldState` represents a recorded state and validates its structural contract. The implementation covers:

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

## Explicit boundaries

`FieldState` does not determine causes, infer meaning, establish causality, infer behavioral patterns, decide transitions, make decisions, or perform interventions.

Those concerns remain outside the current runtime component and require separate contracts before implementation.

## Evidence level

Passing unit tests demonstrate compliance with the software contract. They do not validate broader scientific or behavioral claims about ACRM or AI systems.

## CI

GitHub Actions runs the test suite on Python 3.10 through 3.13 for pushes and pull requests targeting `main` or `develop`.

## Next development layers

Potential future layers include relationships between observations, transitions, analysis, governance, and intervention. Each layer should receive an explicit responsibility, interface, testable contract, and validation strategy before becoming part of the runtime.
