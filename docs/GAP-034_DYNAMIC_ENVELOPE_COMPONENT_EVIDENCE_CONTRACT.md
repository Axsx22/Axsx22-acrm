# Dynamic Envelope Component Evidence Contract

**GAP:** 034 — Historical Evidence Provenance and Analysis Traceability  
**Component:** Dynamic Envelope  
**Contract status:** Accepted for design; recorded on the Session C working branch  
**Implementation status:** Not implemented by this document  
**Baseline inspected:** `codex/session-c-architecture-alignment` at `47861dd35d44da23966bdb572da73a17bd0bedce`  
**Pull request:** [#15](https://github.com/Axsx22/Axsx22-acrm/pull/15) — Draft, open, not merged

> Provenance must record what actually happened in computation, not what the architecture assumes should have happened.

This document records the accepted Dynamic Envelope evidence contract. It separates the currently observed execution path from provenance requirements and the gaps between them. It does not authorize or implement changes to numeric Envelope behavior.

## 1. Component identity

### Observed
- Calculation is performed by `FieldEnvelopeEstimator.estimate()`.
- The estimator produces a `DynamicEnvelope` from numeric values extracted from observations in the analysis snapshot.
- The current result includes median, warning and critical limits, and `sample_count`.

### Required
The component trace identifies component identity, algorithm version, evidence-selection policy version, and canonicalization version, and binds them to the Analysis Execution and snapshot that produced the result.

### Gap
The current result does not carry an independent Envelope algorithm version or component-specific provenance.

## 2. Observed execution path

The re-inspected path, as recorded for this contract, is:

1. The orchestrator creates the analysis snapshot using observer receipt time and the ingestion-sequence cut.
2. Snapshot observations are passed to the Envelope estimator.
3. The estimator validates `warning_quantile` and `critical_quantile`.
4. It validates `direction`.
5. It iterates over observations.
6. It reads the requested metric from each observation's context.
7. It checks the value type, rejecting Boolean and values outside `int` and `float`.
8. It converts accepted values to `float`.
9. It rejects non-finite converted values using `isfinite`.
10. It appends valid values to the shared `values` collection.
11. It sorts that collection.
12. It computes median and warning and critical quantiles.
13. It constructs the `DynamicEnvelope`.

The current estimator does not emit a per-observation decision trace.

## 3. Snapshot and input sources

### Observed
- The estimator receives observations selected by the orchestrator's analysis snapshot.
- Snapshot membership is scoped by observer receipt metadata and the ingestion-sequence boundary.
- An observation carries an identity, kind, description, observation timestamp, context, and source.
- `observed_at` is observation/event time; `received_at` is observer receipt time.
- `ingest_sequence` is observer-assigned commit order, not Runtime event-occurrence order.

### Required
For each available observation, the Envelope trace must reference its observation ID, `observed_at`, `received_at`, `ingest_sequence`, snapshot boundary, and owning Analysis Execution. Event time must not substitute for observer availability at the snapshot cut.

### Gap
The orchestrator can construct a time- and sequence-scoped snapshot, but the current Envelope path does not bind selected evidence to a component trace.

**Invariant:** Snapshot presence establishes `AVAILABLE` only. It does not by itself establish applicability, candidacy, or consumption.

## 4. Component-local evidence status and applicability

Evidence status belongs to the relationship **evidence — component — stage**, not permanently to the Observation. The same Observation may be excluded by Envelope and still be consumed by Readiness or Topic Inference.

The following are stage-qualified facts, not a single mandatory linear Enum on the Observation:

| Status | Contract meaning |
|---|---|
| `AVAILABLE` | Observation is present within this analysis snapshot. |
| `NOT_APPLICABLE` | Metric key is absent from the Observation context under the Envelope applicability rule. |
| `CANDIDATE` | Metric key exists; its value enters Envelope validation. |
| `EXCLUDED` | Candidate is rejected at a recorded validation stage for a recorded reason. |
| `CONSUMED` | Converted, finite value is appended to the shared numeric input collection. |

### Accepted decision ENV-Decision-01 — Candidate boundary

**The existence of the `metric_name` key in Context is the condition for Candidate status.**

Key membership must be tested explicitly. `context.get(metric_name)` alone cannot distinguish an absent key from a present key whose value is `None`.

- Key absent: `NOT_APPLICABLE`.
- Key present with `None`: `CANDIDATE`, then `EXCLUDED` with reason `NULL_VALUE`.

The status of this Observation in another component is unaffected.

### Observed
The current path reads with `context.get(metric_name)`; it does not produce this component-local status trace or preserve the absent-key versus present-null distinction in a trace.

### Required
The future trace records applicability and validation stage for each available Observation.

### Gap
The component currently returns neither the per-observation applicability decision nor candidate/exclusion records.

## 5. Validation and exclusion rules

These rules describe the accepted contract and must preserve the current accepted numeric domain. GAP-034 is not a vehicle for silently broadening it.

| Condition | Required status / reason | Contract behavior |
|---|---|---|
| Metric key absent | `NOT_APPLICABLE` | No numeric candidate is created. |
| Key exists, value is `None` | `EXCLUDED / NULL_VALUE` | Do not convert or consume. |
| Boolean value | `EXCLUDED / BOOLEAN_NOT_ALLOWED` | Boolean is not accepted as a numeric metric. |
| Type is not `int` or `float` | `EXCLUDED / UNSUPPORTED_NUMERIC_TYPE` | Do not broaden accepted types in GAP-034. |
| Converted value is NaN | `EXCLUDED / NON_FINITE_NAN` | Do not consume. |
| Converted value is positive or negative infinity | `EXCLUDED / NON_FINITE_INFINITY` | Do not consume. |
| Conversion raises `OverflowError` for this value | `EXCLUDED / NUMERIC_CONVERSION_OVERFLOW` | Exclude this evidence only; continue with other valid candidates. |

### Accepted decision ENV-Decision-02 — Decimal

`Decimal` is excluded under the current contract with reason `UNSUPPORTED_NUMERIC_TYPE`. Supporting Decimal would change the accepted numeric domain and is a separate behavior decision requiring evaluation of conversion precision, ordering, and quantile results.

### Accepted decision ENV-Decision-03 — Overflow and failure boundary

An `OverflowError` attributable to converting one identified evidence value is an exclusion of that evidence, not a failure of the whole analysis execution. Record at least the Observation ID, input type, failing stage, and reason. The rejected raw value need not be inserted into the numeric computation hash.

An algorithm failure, unexpected computation failure, or invariant violation is not an evidence exclusion. It makes the Analysis Execution `FAILED`.

### Gap
The current code does not persist exclusion reasons as trace records. Per-value overflow behavior and the failure distinction require explicit tests before implementation is considered complete.

## 6. Consumption and derived operations

### Observed
After valid values are collected, the current estimator sorts one shared collection and uses that same collection for median, warning quantile, and critical quantile. The direction setting affects quantile selection: `high` uses configured quantiles directly; `low` uses complementary quantiles.

### Required
Every value actually appended to the shared `values` collection is recorded as `CONSUMED` and remains referable to its source Observation. The trace records that median and both limits derive from this same consumed collection.

### Gap
The current output does not preserve the mapping from consumed values back to their Observation identities.

**Granularity rule:** Recording consumption once for the shared input set is sufficient while all three calculations use that same set. If future code introduces separate input sets or branches, the trace must reflect those distinct paths. The goal is all effective detail, not maximum detail.

## 7. Effective parameters and dependency closure

### Observed
The current path receives or uses:
- `metric_name`;
- `warning_quantile` (Engine default reported as 0.90);
- `critical_quantile` (Engine default reported as 0.975);
- `direction` (Engine default reported as `high`);
- `statistics.median`;
- the internal quantile implementation with linear interpolation;
- `math.isfinite`;
- `float(value)`;
- `sorted(values)`.

### Required
Record effective values for the actual execution, not merely declared defaults:
- metric name;
- effective warning and critical quantiles;
- effective direction;
- Envelope algorithm version;
- evidence-selection/validation policy version;
- canonicalization version;
- effective conversion, finite-value, sorting, median, and quantile policies.

Dependency closure applies: any indirect configuration, default, runtime state, or library behavior that actually affects the result must be identifiable in the trace. Do not record irrelevant environment details as if they were effective inputs. Do not expose secrets or credentials in parameter snapshots.

### Gap
The current result does not include an immutable per-execution parameter snapshot, independent algorithm version, or Envelope provenance hash. A general RuntimeEvaluation digest is not an Envelope provenance hash.

## 8. Canonicalization and hashes

### Required
Keep result identity and provenance identity separate:
- `result_hash` identifies the canonicalized Envelope result.
- `provenance_hash` identifies the defined evidence set/statuses, snapshot boundary, selection and validation policy, algorithm version, effective parameters, and canonicalization version.

Canonical evidence ordering must make equivalent evidence sets independent of incidental input iteration order, while preserving semantically meaningful ordering where the algorithm depends on it. Different exclusion reasons or effective parameters must change provenance identity.

Hash equality means equality under the declared canonicalization contract. It does not prove scientific correctness, data truth, or algorithm validity. Hashes alone do not reconstruct source evidence; stable references and required evidence metadata must remain available.

### Observed
A general canonicalization version and RuntimeEvaluation digest exist in the inspected code, but that digest is not a component-specific Envelope provenance hash.

### Gap
No dedicated Envelope result/provenance hash pair or immutable component trace is currently emitted.

## 9. Result-Provenance binding and execution failure

### Required
Result and provenance must be created within one Analysis Execution and bound to the same Analysis ID, component identity, snapshot boundary, effective parameters, component result, and component trace. A trace from one execution must not be attachable to a result from another.

Execution status and result publication status are distinct:
- Successful execution: `COMPLETED`, with a valid result eligible for publication.
- Failed execution: `FAILED`, with optional diagnostic partial trace, but no valid/published partial Envelope result.

A partial diagnostic trace from a failed execution must never be represented as complete provenance for a valid result.

### Gap
The current code has no explicit Envelope execution trace, failure-trace contract, or atomic Result-Provenance binding.

## 10. Acceptance tests

These are required acceptance criteria, not tests claimed to have been written or run.

| ID | Scenario | Acceptance criterion |
|---|---|---|
| ENV-A01 | Snapshot boundary | Evidence received after the snapshot cut is absent from both Envelope input and trace. |
| ENV-A02 | Missing metric key | Missing key is recorded as `NOT_APPLICABLE`. |
| ENV-A03 | Present null | Present key with `None` is Candidate then excluded as `NULL_VALUE`. |
| ENV-A04 | Boolean | `True` and `False` are excluded and never consumed. |
| ENV-A05 | Decimal | Decimal is excluded as `UNSUPPORTED_NUMERIC_TYPE`; numeric behavior is unchanged. |
| ENV-A06 | Non-finite | NaN and infinities are excluded with distinguishable reasons. |
| ENV-A07 | Consumed identity | Every value appended to the shared collection references its source Observation. |
| ENV-A08 | Shared input set | Trace identifies one shared consumed set as the source for median and both quantiles. |
| ENV-A09 | Effective parameters | A change to either quantile or direction changes the relevant provenance. |
| ENV-A10 | Canonical ordering | Reordering an equivalent input set does not change canonical provenance when policy and semantic inputs are unchanged. |
| ENV-A11 | Per-value overflow | One value's conversion overflow excludes only that evidence; other valid evidence is still processed. |
| ENV-A12 | Algorithm failure | Unexpected algorithm failure or invariant violation marks Execution failed and does not publish a valid partial result. |
| ENV-A13 | Dependency closure | Every effective input and derived dependency affecting the Envelope result is represented. |
| ENV-A14 | Component-local status | Exclusion in Envelope does not mutate the same Observation's status in another component. |
| ENV-A15 | Atomic binding | Result and provenance from different Analysis Executions cannot be combined. |
| ENV-A16 | Historical immutability | Evidence arriving after the snapshot does not alter an earlier analysis trace or result. |
| ENV-A17 | Exclusion distinction | Different exclusion reasons remain distinguishable in the trace and provenance identity. |

## 11. Known limitations and open gaps

1. The current estimator does not emit stage-level evidence provenance.
2. Consumed values are not linked to source Observation IDs in the result.
3. Exclusion reasons are not recorded.
4. The Envelope algorithm version is not recorded independently.
5. A component-specific provenance hash is not present.
6. Result-Provenance atomic binding is not implemented.
7. Failure trace and result publication semantics are not implemented.
8. Decimal remains unsupported under this contract.
9. This contract does not by itself guarantee bit-for-bit reproducibility across different runtime/library environments.
10. This contract does not introduce a database, event store, durable persistence, or restart recovery.

## 12. Contract invariants

- Evidence status is scoped to the evidence–component–stage relationship.
- Snapshot availability alone does not imply candidacy or consumption.
- Every candidate reaches a traceable validation outcome.
- Every exclusion has a reason and stage.
- Every consumed value is referable to its source Observation.
- Exclusion in Envelope does not imply exclusion in another component.
- All effective dependencies are represented in the component trace.
- Shared-set consumption granularity remains valid only while the actual computation uses one shared set.
- Result and provenance belong to the same Analysis Execution.
- A failed execution's partial trace is not complete provenance for a valid result.
- Provenance records actual computation, not an assumed architecture.

## 13. Implementation boundary and repository record

This is a design/contract artifact for GAP-034. It does not implement provenance, change Envelope numeric behavior, add persistence, or modify other Session C components.

Accepted decisions:
- **ENV-Decision-01:** Candidate begins when the `metric_name` key exists in Context.
- **ENV-Decision-02:** Decimal is excluded as `UNSUPPORTED_NUMERIC_TYPE` under the current accepted numeric domain.
- **ENV-Decision-03:** Per-value conversion overflow excludes that evidence; algorithm failure or invariant violation fails the Execution.

Adding this document to the working branch is documentation-only. The PR remains Draft and open; no merge is performed and `main` is not modified. GAP-034 implementation still requires separate authorization.
