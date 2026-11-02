# Session C Implementation Status

**Status:** Active development / engineering checkpoint  
**Scope:** Session C in ACRM v8.6  
**Canonical architecture:** [SESSION_C_ARCHITECTURE.md](SESSION_C_ARCHITECTURE.md)

## 1. Status interpretation

Session C is an independent, continuously operating Runtime observer and controlled-evolution subsystem in the **target architecture**. The current `main` branch contains only part of that lifecycle. This document separates target responsibility from executable implementation so that neither the architecture nor the code is overstated.

## 2. Current executable components

| Component | What the current code does | Important boundary |
|---|---|---|
| Runtime evaluation | Produces a `RuntimeEvaluation`, `FieldState`, and observation records. | Producing records is not the same as continuously publishing them to Session C. |
| Observation record | Validates identity, kind, description, timezone-aware timestamp, source, and context. | In-memory record; no durable event transport. |
| Observation log | Append-only collection with duplicate-ID rejection. | Memory-only; not a durable evolution history. |
| Trajectory analyzer | Computes observation-kind counts, recurrence, and adjacent kind persistence. | Kind recurrence is not numerical signal persistence or semantic persistence. |
| Dynamic envelope | Derives quantile limits from numeric values in observation context. | No online windowing/decay or empirical calibration contract is established. |
| Readiness evaluator | Combines observation count, threshold state, and the current persistence descriptor. | Current gate is not yet the complete evidence-sufficiency decision described by the target architecture. |
| Topic engine | Maps constrained observation kinds to a small topic taxonomy. | Not a general semantic topic model. |
| Session C orchestrator | Accepts caller-pushed RuntimeEvaluation batches; enforces Runtime/Session/Field identity, monotonic sequence ordering, exact replay idempotency, and explicit gap recovery. | No background subscription/event bus, durable storage, restart recovery, or concurrent-ingestion guarantee. |
| Evolution candidate | Represents generated source and evidence IDs. | No immutable artifact store or content-hash/provenance ledger. |
| Candidate tester | Calls an injected tester and gates review on successful results. | The core does not provide sandboxing, process isolation, resource limits, or test artifact retention. |
| Weighted review | Aggregates reliability/relevance-weighted specialist votes. | Vote weights require validation; this is not execution authorization. |
| Evolution decision | Returns statuses such as wait, reject, retain, or `SWITCH_RECOMMENDED`. | Recommendation is not Runtime Injection, Version Switch, or authorization. |

## 3. Target lifecycle versus current implementation

The target lifecycle is:

```text
Runtime events/state
       |
       v
independent continuous Session C observer
       |
       v
append-only evolution history
       |
       v
trajectory and multi-layer evidence analysis
       |
       v
evidence-sufficiency decision
       |
       v
background candidate generation / modification
       |
       v
independent candidate testing
       |
       v
weighted cross-layer review
       |
       v
change-route decision
       |---------------------------|
       v                           v
Runtime Injection             Version Switch
       |                           |
       +-------------+-------------+
                     v
             authorization decision
                |             |
                v             v
              user        policy gate
                |             |
                +------+------+
                       v
             controlled execution
                       |
                       v
             verification / rollback
```

**Only some building blocks in this flow exist in the current code.** In particular, continuous event ingestion, durable history, route selection, authorization, active Runtime mutation/version activation, and rollback are not implemented in the current core.

## 4. Important semantics and known gaps

### Observation history and continuity
The canonical observation type and in-memory log exist. Runtime evaluation emits observation records, and `SessionCEngine.observe_runtime()` accepts caller-pushed evaluation batches. Normal ingestion is strictly monotonic: exact full-payload replay is idempotent, conflicting replay is rejected, and a forward sequence jump creates an immutable-range Gap with per-sequence OPEN state. Late events are rejected from normal ingestion and must use one of two explicit paths: `compensate_gap()` for OPEN members, or `record_late_recovery()` for members already declared UNRECOVERABLE. Partial recovery never shrinks or splits the original Gap. Gap status is derived from member states; audit events and late-recovery records are exposed as immutable snapshots. Analysis distinguishes time-scoped historical completeness from currently available recovered evidence.

This remains caller-pushed ingestion, not a background observer: automatic Runtime event subscription, durable storage, restart recovery, and thread-safe concurrent ingestion are not implemented.

### Historical analysis consistency — GAP-032

`SessionCEngine.analyze(as_of=T)` now scopes every observation-derived analysis component to records received by the observer no later than T:

- observation history used by the dynamic envelope;
- trajectory counts and numeric signal persistence used by readiness;
- the Runtime metric value used for threshold approach/readiness;
- topic inference.

The observer receipt timestamp is distinct from the event's `observed_at` / Runtime event timestamp. A late-arriving event whose event timestamp predates T is still excluded from the T snapshot if Session C received it after T. Constructor-supplied observations and the constructor's initial `current_value` are treated as known at engine initialization. Later direct `record()` calls and accepted Runtime evaluations receive observer-side receipt timestamps. Runtime metric values are retained as a time-ordered in-memory history so a historical analysis uses the latest value known by T.

GAP-032 verifies that a single historical analysis remains identical after later Runtime sequence delivery and later observation receipt, while the current analysis reflects the new topic evidence, envelope distribution, observation count, and Runtime metric value.

This is an in-memory observer-time contract, not durable event sourcing: receipt metadata and value history are lost on process restart, and an `as_of` earlier than the engine's initialization cannot use the constructor's initial state. Persistence and restart reconstruction remain separate work.

### Deterministic ingestion and snapshot boundary — GAP-033

Observer receipt time and observer commit order are separate fields with separate meanings:

- `received_at` is the UTC wall-clock time at which the observer accepts a transaction. It supports time-based queries such as `analyze(as_of=T)`; it is not used as a unique ordering key.
- `ingest_sequence` is a monotonically increasing integer assigned by the observer to each accepted state-changing transaction. All observations in one accepted Runtime batch share that transaction's sequence. It records observer commit order, not Runtime event-occurrence order.
- Runtime event time remains in the original Runtime evaluation / observation evidence. A late-arriving event can therefore have an older event timestamp but a later observer receipt time and ingestion sequence.

A re-entrant in-process lock serializes direct observation receipt, Runtime batch acceptance, recovery/audit mutations, current-value updates, and analysis. Runtime batch validation and staging happen before the ObservationLog batch append; the ingestion sequence is advanced only after the batch append succeeds. Replays that do not add a new accepted transaction do not consume a new sequence. The same transaction sequence is associated with its accepted observations, Runtime sequence, and metric value.

`analyze(as_of_ingest_sequence=N)` provides an explicit snapshot cut: it includes only observer transactions committed at or before N. The returned `SessionCAnalysis.snapshot_ingest_sequence` identifies the cut used. Omitting N captures the current sequence while holding the same lock, so analysis cannot observe a partially committed in-process transition. The wall-clock `as_of` filter and ingestion-sequence cut can be combined; they answer different questions and both filters apply.

GAP-033 tests cover wall-clock reversal without ingestion-order reversal, an explicit historical sequence cut that excludes later records, and concurrent direct observation submissions followed by a consistent snapshot. This is process-local serialization only: it does not coordinate multiple processes, persist the sequence across restart, or establish the order in which events occurred inside Runtime.

### Persistence
Current trajectory persistence is based on adjacent repeated observation kinds. It must not be presented as persistence of the underlying numerical signal. A separate signal-level measure, with a declared window, direction, missing-data policy, and minimum evidence requirements, is needed.

### Dynamic envelope
The envelope is an empirical quantile calculation over supplied values. It is not an online adaptive threshold system with proven calibration. Its limitations must remain explicit.

### Candidate testing
The tester is a callback interface. The core does not execute candidate source and does not provide a sandbox. A successful callback result proves only that the injected callback returned the required result, not that candidate code was safely or independently validated.

### Weighted review
Reliability and relevance are multiplied to produce vote weights. Specialist identities must be unique within one review. Weighted review is not a substitute for evidence sufficiency, route selection, or execution authorization.

### Runtime Injection and Version Switch
These are distinct target routes with different compatibility, atomicity, verification, and rollback requirements. Neither route is implemented in the current Session C core.

### Authorization
User authorization and automatic policy authorization are separate target paths. A `SWITCH_RECOMMENDED` result is not permission to execute a change.

## 5. Immediate engineering priorities

1. Add background Runtime event subscription/event transport around the existing caller-pushed ingestion API.
2. Add durable Session C history and restart recovery; the current gap/audit/recovery contract is in-memory only.
3. Isolate Runtime governance state by session.
4. Replace kind-recurrence-as-signal-persistence with a separately named and tested signal-level persistence contract.
5. Add end-to-end tests proving Runtime → Session C event delivery and state isolation.
6. Bind candidates to evidence IDs, Runtime version, artifact hash, and reproducible test results.
7. Define isolated candidate testing before executing generated code.
8. Validate specialist identities and vote provenance.
9. Define Runtime Injection and Version Switch as separate route contracts.
10. Define user authorization and policy-gated automatic execution as separate contracts.
11. Implement execution, verification, and rollback only after the preceding contracts are testable.

## 6. Evidence boundary

Software tests establish behavior against the tests and contracts present in the repository. They do not establish scientific validity, semantic understanding, model generalization, safe autonomous evolution, or production effectiveness. Those require separate controlled experiments and independent evaluation.
