# ACRM v8.5 — FieldState Contract

## Purpose

`FieldState` is the immutable runtime snapshot contract for observable ACRM
field state.

It stores observations only. It does not modify model execution, model
output, sampling, or underlying model state.

## Current responsibilities

`FieldState` is responsible for:

- identifying a field;
- identifying a session;
- recording a non-negative sequence number;
- recording a timezone-aware timestamp;
- storing finite numeric metrics;
- recording a structural state label;
- recording active failure-mode identifiers;
- recording governance confidence in `[0.0, 1.0]`;
- providing immutable access to the snapshot.

## Current invariants

### Identity

- `field_id` must be a non-empty string.
- `session_id` must be a non-empty string.

### Sequence

- `sequence` must be an integer.
- Boolean values are not accepted as sequence numbers.
- `sequence >= 0`.

### Timestamp

- `timestamp` must be a `datetime`.
- `timestamp` must be timezone-aware.
- `create()` uses UTC when no timestamp is supplied.

### Metrics

- Metric names must be non-empty strings.
- Metric values must be numeric.
- Boolean values are not accepted as metric values.
- Metric values must be finite.
- Metrics are exposed through an immutable mapping.

### State

- `state` must currently be a non-empty string.
- The canonical ACRM state vocabulary is intentionally not defined here yet.
- State semantics must be established from the authoritative ACRM
  specification before a canonical enum is introduced.

### Failure modes

- Failure-mode identifiers must be non-empty strings.
- Duplicate active failure modes are rejected.
- Failure-mode semantics and taxonomy are not owned by `FieldState`.

### Governance confidence

- Must be numeric.
- Boolean values are not accepted.
- Must be finite.
- Must be within `[0.0, 1.0]`.

## Explicit non-responsibilities

`FieldState` does not enforce:

- ordering between multiple snapshots;
- session continuity;
- temporal direction;
- state-transition rules;
- metric semantic definitions;
- metric units;
- failure-mode taxonomy;
- governance decisions;
- model intervention.

Those responsibilities belong to higher-level ACRM runtime and analysis
components.

## Architectural boundary

```text
                    FieldState
                         |
             immutable observation
                         |
                         v
              Runtime Field / Stream
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Temporal        Failure       Governance
       Analysis        Taxonomy      Evaluation
