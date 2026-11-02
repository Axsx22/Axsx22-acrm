# FieldState Contract — ACRM v8.6

## Purpose

`FieldState` is the boundary object for a recorded field observation. It stores validated state without turning that observation into an explanation or decision.

## Required fields

- `field_id`: non-empty string.
- `session_id`: non-empty string.
- `sequence`: non-negative integer.
- `timestamp`: timezone-aware `datetime`.
- `metrics`: mapping of non-empty metric names to finite numeric values.
- `failure_modes`: tuple of unique, non-empty identifiers.
- `governance_confidence`: finite numeric value in `[0.0, 1.0]`.

## Producer-specific semantics

The `governance_confidence` field is a legacy, bounded confidence-like slot. Its name does not guarantee that every producer supplies a calibrated probability, a specialist-consensus score, or a validated estimate of governance confidence.

For the current `FieldRuntime` producer, the value is populated as:

```text
lexical_entropy_complement = 1 - normalized_lexical_entropy
```

The Runtime also records this quantity under `metrics["lexical_entropy_complement"]` so its actual meaning is explicit. It is a lexical/statistical proxy only. It must not be interpreted as semantic certainty, model confidence, or empirical calibration.

Consumers should prefer the explicitly named metric when interpreting current Runtime output. Any future producer that assigns a different meaning to the legacy field must document that meaning separately.

## Immutability

The dataclass is frozen. Metric storage is wrapped in a read-only mapping and failure modes are normalized to a tuple, so the recorded state cannot be mutated through ordinary field or mapping assignment.

## Determinism

The caller supplies the timestamp explicitly. This keeps construction deterministic for testing, replay, and recorded-state comparison. `recorded_at_utc` provides a normalized UTC view.

## Access

`metric(name)` retrieves a recorded metric. `has_failure_mode(mode)` checks whether a failure mode was explicitly recorded.

## Non-responsibilities

`FieldState` does not:

- infer causes;
- infer meaning;
- establish causality;
- infer behavioral patterns;
- determine transitions;
- make decisions;
- perform interventions.

Higher-level components must define separate contracts for those responsibilities.

## Validation principle

Invalid recorded state is rejected at construction time rather than silently normalized into a potentially misleading state.
