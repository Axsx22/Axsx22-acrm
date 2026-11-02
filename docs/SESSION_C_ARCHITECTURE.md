# ACRM Session C — Target Architecture and Implementation Contract

**Document status:** Target architecture and engineering contract  
**Applies to:** ACRM Runtime + Session C  
**Terminology:** The architectural component is **Session C** throughout this repository.

## 1. Architectural intent

Session C is an independent, continuously operating observer and controlled-evolution subsystem associated with the active ACRM Runtime.

It is not a second Runtime, does not reproduce Runtime internals, and is not part of the Runtime's turn-by-turn decision path. Its responsibility is to observe the Runtime from an independent boundary, preserve a longitudinal record of what it observes, assess whether the system needs to evolve, prepare and evaluate possible changes, and coordinate a governed handoff or execution after all required stages.

The intended relationship is therefore not merely:

`Runtime → occasional report → Session C`

It is:

`Runtime ⇄ observable event/state interface ⇄ independent Session C lifecycle`

The interface is for observation and controlled evolution. It does not imply access to model weights, hidden Transformer state, or private reasoning traces.

## 2. Independent components and responsibilities

### 2.1 Runtime

The Runtime is the active execution system. It:
- processes the interaction and its own field/governance logic;
- produces externally observable state snapshots, events, metrics, and reports;
- identifies the session, sequence, timestamp, and source associated with each emitted record;
- continues its ordinary operation without waiting for Session C's analysis or candidate-generation work.

The Runtime does not decide its own replacement merely because it emitted an observation.

### 2.2 Session C — continuous observer and evolution coordinator

Session C operates independently alongside the Runtime. Its target responsibilities are:

1. Receive Runtime events/state updates during execution through a defined observation interface.
2. Validate event identity, source, session, sequence, timestamp, and schema.
3. Append observations to an independent evolution history.
4. Preserve the relationship between each observation and the Runtime version/state from which it originated.
5. Analyze trajectories and changes over time, not just isolated snapshots.
6. Determine whether available evidence is sufficient to open an evolution cycle.
7. Coordinate candidate generation or background code modification when an evolution cycle is justified.
8. Coordinate independent testing and weighted review.
9. Determine the appropriate change route and the required authorization path.
10. Record the complete decision and execution outcome in the evolution history.

The observation process and the evolution process are logically distinct. Candidate generation, testing, and review must not block or corrupt the observer's ability to continue recording Runtime events.

### 2.3 Observation history

Session C maintains its own history; it must not rely solely on the Runtime's current in-memory state. The target history is append-only at the evidence layer and should retain, at minimum:

- observation/event ID;
- Runtime/session ID and sequence;
- event timestamp and ingestion timestamp;
- source component and Runtime version;
- observed values and relevant context;
- links to prior observations or the evolution cycle;
- later analysis references, without rewriting the original observation.

Corrections to interpretation or analysis should create new records linked to prior evidence. They must not silently rewrite historical observations.

A memory-only list is an implementation checkpoint, not durable evolution history. Durable storage, recovery, concurrency, and retention are separate implementation requirements.

## 3. Data flow and control flow

The intended lifecycle is:

```text
                 ACTIVE ACRM RUNTIME
                         |
              observable events / state
                         |
                         v
          +-----------------------------+
          | SESSION C: INDEPENDENT       |
          | CONTINUOUS OBSERVER         |
          |                             |
          | validate -> append -> index |
          | retain evolution history    |
          +--------------+--------------+
                         |
                         v
              trajectory / field analysis
                         |
                         v
                evidence sufficiency
                         |
              +----------+----------+
              |                     |
          insufficient          sufficient
              |                     |
        keep observing              v
                            evolution cycle opened
                                      |
                                      v
                         background candidate generation
                         / code modification in isolation
                                      |
                                      v
                              independent test gate
                                      |
                                      v
                         weighted multi-layer review
                                      |
                                      v
                         +------------------------+
                         | DECISION 1             |
                         | Is change justified?   |
                         +-----------+------------+
                                     |
                                     v
                         +------------------------+
                         | DECISION 2             |
                         | Which change route?    |
                         +-----------+------------+
                                     |
                       +-------------+-------------+
                       |                           |
                       v                           v
                RUNTIME INJECTION             VERSION SWITCH
                       |                           |
                       +-------------+-------------+
                                     |
                                     v
                         +------------------------+
                         | DECISION 3             |
                         | Who authorizes it?     |
                         +-----------+------------+
                                     |
                       +-------------+-------------+
                       |                           |
                       v                           v
                USER AUTHORIZATION          AUTOMATIC POLICY GATE
                       |                           |
                       +-------------+-------------+
                                     |
                                     v
                         controlled execution / handoff
                                     |
                                     v
                       verification, rollback, audit
                                     |
                                     v
                       Runtime continues on approved state
```

The diagram describes the target lifecycle. It is not a claim that every connection or execution mechanism is already implemented in the current `main` branch.

## 4. Three decisions that must remain separate

These decisions must not be collapsed into one weighted vote or one status string.

### Decision 1 — Evidence and change justification

Question: **Is the evidence sufficient to justify a change cycle?**

Inputs may include:
- recurrence and duration of observed conditions;
- signal-level magnitude, direction, and persistence;
- change relative to the Runtime's own relevant history;
- source quality, missing data, and uncertainty;
- impact across relevant independent layers;
- test and evaluation evidence.

A repeated event label alone is not proof that an underlying signal persisted. Observation-kind recurrence, numerical signal persistence, and semantic/behavioral persistence are different measurements and must be named and validated separately.

Outcome: continue observing, request more evidence, or open an evolution cycle.

### Decision 2 — Change route

Question: **If a change is justified, how should it be applied?**

The target architecture distinguishes at least two routes:

| Route | Meaning | Required controls |
|---|---|---|
| **Runtime Injection** | Apply a bounded, compatible change to the currently active Runtime state/version. | Compatibility checks, narrow scope, atomic application, pre/post verification, rollback to the exact prior state. |
| **Version Switch** | Prepare and activate a separately versioned Runtime candidate. | Candidate identity/hash, full test evidence, compatibility/migration checks, staged activation, health verification, rollback to the prior version. |

These routes are not interchangeable. The choice must be based on change scope, compatibility, dependency impact, reversibility, and failure consequences—not merely on the weighted approval score.

A decision that the candidate should be retained or rejected is also distinct from choosing either route.

### Decision 3 — Execution authorization

Question: **Who or what is permitted to authorize the selected route?**

The target architecture supports two authorization paths:

- **User-authorized execution:** Session C presents the evidence, proposed change, route, risks, and rollback plan. The user authorizes or declines execution.
- **Policy-authorized automatic execution:** the system may proceed only when a separately defined policy gate is satisfied. The gate must specify eligible change classes, scope limits, confidence/evidence requirements, test requirements, resource limits, rollback conditions, and audit obligations.

A weighted specialist vote is evidence for governance; it is not itself an execution credential. Likewise, `SWITCH_RECOMMENDED` must never be interpreted as authorization to inject code or activate a version.

## 5. Weighted review across independent layers

The weighted review stage evaluates the candidate and its evidence in relation to the issue under consideration.

Each participating layer/specialist must have:
- a stable identity;
- a defined responsibility and scope;
- an explicit relevance to the current issue;
- a reliability/weight basis;
- an evidence reference and an abstention path.

The review must reject duplicate identities masquerading as independent votes. Missing, conflicting, or out-of-scope evidence must remain visible; it must not be hidden by averaging.

The weighted review answers whether the candidate has sufficient cross-layer support under the defined review contract. It does not by itself:
- establish that the change is necessary;
- select Runtime Injection versus Version Switch;
- authorize execution;
- prove the candidate safe in every environment.

## 6. Candidate generation and background modification

When evidence justifies an evolution cycle, Session C may coordinate code generation or modifications in the background while the active Runtime remains isolated from unverified changes.

The candidate lifecycle must preserve:
- candidate ID and immutable source/artifact reference;
- source Runtime version and evidence IDs;
- change description and intended scope;
- generation tool/model/version and relevant configuration;
- content hash and creation timestamp;
- test plan, environment, results, and artifacts;
- review votes, weights, abstentions, and final route;
- authorization identity/policy and execution record.

Generated code must not be executed in the active Runtime as a substitute for testing. Any executable candidate test requires a separately controlled environment with isolation, resource limits, timeouts, and retained logs. A callback that returns `True` is only an interface stub; it is not evidence of sandboxed code validation.

## 7. Isolation and failure handling

The architecture depends on the following invariants:

1. Runtime execution and Session C observation have separate state ownership.
2. Session C must not silently modify the active Runtime while observing it.
3. Failure or delay in Session C must not corrupt the Runtime's ordinary execution.
4. Failure or restart of the Runtime must not erase Session C's already committed history.
5. Events must be idempotently ingested; duplicate event IDs must not create duplicate evidence.
6. Per-session state must not leak between Runtime sessions.
7. Candidate generation/testing/review must be tied to explicit evidence and candidate identities.
8. No route is executed before its authorization requirement is satisfied.
9. Failed activation must have a defined rollback or safe-retain path.
10. Every state transition must be auditable.

## 8. Current implementation boundary on `main`

The current `main` branch contains useful Session C building blocks, but it does not yet implement the complete target lifecycle described above.

| Capability | Current `main` status |
|---|---|
| Neutral observation record and duplicate-ID log | Implemented; log is in-memory |
| Runtime evaluation output containing observation records | Implemented |
| Automatic continuous Runtime → Session C event subscription | Not implemented |
| Explicit live-ingestion API on `SessionCEngine` | Implemented as caller-pushed `record()` / `observe_runtime()`; no background subscription or durable transport |
| Durable independent evolution history | Not implemented |
| Trajectory descriptors and dynamic envelope | Implemented in constrained form; calibration and signal-level persistence need further validation |
| Constrained topic inference | Implemented |
| Candidate-generation callback and candidate representation | Implemented |
| Candidate execution sandbox | Not implemented by the core |
| Weighted specialist review | Implemented as a callback contract; duplicate-vote identity validation is required |
| Evidence sufficiency decision | Partially represented by current readiness gates; not a complete multi-layer decision contract |
| Runtime Injection vs Version Switch decision | Target architecture; not implemented |
| User authorization vs automatic policy authorization | Target architecture; not implemented |
| Controlled execution, health verification, and rollback | Not implemented |
| Durable audit trail for the full evolution lifecycle | Not implemented |

This table is intentionally explicit: an architectural responsibility must not be described as an implemented feature merely because adjacent data structures or callbacks exist.

## 9. Engineering sequence

The implementation should progress in dependency order:

1. **Observation boundary:** Runtime event adapter, live ingestion, event identity/order, per-session isolation, and durable history.
2. **Trajectory evidence:** distinguish event-kind recurrence from signal-level persistence; define windows, minimum sample requirements, missing-data behavior, and calibration.
3. **Evolution cycle:** link candidate generation and testing to exact evidence, Runtime version, candidate hash, and reproducible test artifacts.
4. **Review contract:** validate specialist identity, relevance, reliability, abstention, conflicting evidence, and decision thresholds.
5. **Change-route contract:** specify Runtime Injection and Version Switch separately, including compatibility, atomicity, rollback, and verification.
6. **Authorization contract:** specify user approval and policy-authorized automation as distinct gates.
7. **Execution integration:** implement only after the preceding contracts and adversarial/integration tests are in place.

## 10. Evidence boundary

Passing unit tests demonstrates software behavior against the tested contract. It does not establish:
- that the Runtime metrics are valid measures of semantic or behavioral coherence;
- that a candidate improves model behavior;
- that a weighted review is empirically calibrated;
- that automatic evolution is safe;
- or that the architecture generalizes across models and providers.

Those claims require controlled, reproducible, long-horizon and adversarial evaluation, followed where possible by independent replication.
