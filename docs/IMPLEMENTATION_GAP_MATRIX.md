# ACRM implementation and validation gap matrix

**Status:** Active engineering control document  
**Scope:** ACRM v8.6 core and Session C  
**Purpose:** Keep implemented behavior, evolving implementation, engineering verification, empirical validation, and future research claims explicitly separated.

## Status vocabulary

| Status | Meaning |
|---|---|
| Implemented | Present in the repository as executable code or a defined runtime contract. |
| Tested | Covered by automated repository tests. |
| Evolving | Implemented and reviewable, but still being refined; not a frozen final specification. |
| Specified | Defined architecturally or contractually, but not necessarily implemented. |
| Empirical | Requires measurements from controlled experiments rather than unit tests. |
| Independent | Requires reproduction or review outside the original implementation context. |
| Future | Not currently implemented and should not be implied by the v8.6 core. |

## Matrix

| Capability / claim | Current state | Evidence | Remaining work |
|---|---|---|---|
| Immutable FieldState contract | Implemented + Tested | `acrm_core/field/state.py`, unit tests | None for current contract; extend only with new requirements. |
| Neutral Session C observation boundary | Implemented + Tested | `acrm_core/session_c/observation.py`, boundary tests | Add integration coverage as external producers are introduced. |
| Temporal trajectory profiling | Implemented + Tested + Evolving | `TrajectoryAnalyzer`, dynamic tests | Refine descriptors where required and validate against real longitudinal datasets. |
| Field-relative dynamic envelope | Implemented + Tested + Evolving | `FieldEnvelopeEstimator`, dynamic tests | Empirically calibrate quantiles across models, tasks, and signal distributions. |
| High/low signal direction | Implemented + Tested | `DynamicReadinessEvaluator(direction=...)` | Define metric-specific direction in experimental protocols. |
| Dynamic readiness gating | Implemented + Tested + Evolving | `DynamicReadinessEvaluator`, Session C tests | Measure false-positive/false-negative behavior experimentally and refine if evidence requires it. |
| Constrained topic inference | Implemented + Tested + Evolving | `FieldDrivenTopicEngine`, topic tests | Expand taxonomy only when supported by evidence and a stable contract. |
| Candidate generation boundary | Implemented / isolated | `EvolutionSessionC` contracts | Connect to controlled candidate-generation experiments without enabling implicit runtime mutation. |
| Candidate testing gate | Implemented + Tested | Session C orchestration tests | Add adversarial and property-based testing around candidate artifacts. |
| Weighted specialist review | Implemented + Tested + Evolving | Session C orchestration tests | Validate weighting assumptions against independent evaluators. |
| Evolution decision | Implemented + Tested | `EvolutionSessionC`, orchestration tests | Refine decision policy only through explicit contract changes and evidence. |
| Runtime mutation / automatic deployment | Future | Explicitly absent from current Session C | Requires a separate safety and governance design; must never be inferred from candidate recommendation. |
| Causal analysis | Future | Not implemented in v8.6 core | Requires a separately defined causal methodology and evidence. |
| Full behavioral inference engine | Future | Not implemented | Define falsifiable scope and evaluation protocol before implementation. |
| Scientific threshold calibration | Empirical | Unit tests are insufficient | Run controlled multi-model longitudinal experiments and publish calibration results. |
| Long-horizon behavioral claims | Empirical | Research documents and hypotheses only | Execute controlled long-horizon evaluations. |
| Multi-model generalization | Empirical | No completed repository result currently establishes it | Compare across model families, prompts/conditions, and repeated runs. |
| Independent reproduction | Independent | Not yet established | Provide reproducible experiment package and obtain external replication/review. |

## Runtime measurement limitations

The current Runtime produces useful executable baseline signals, but their interpretation must remain narrow:

| Signal | Current operational meaning | Must not be claimed as |
|---|---|---|
| Sequential similarity | Cosine similarity between adjacent token-frequency vectors | Semantic consistency or intent preservation |
| Centroid coherence | Cosine similarity against an exponentially updated lexical centroid | General semantic coherence |
| Alignment gap | One minus lexical cosine similarity for adjacent user/model turns | Misalignment of goals or meaning |
| Entropy | Normalized lexical token-frequency entropy within a turn | Model uncertainty or cognitive uncertainty |
| Anomaly index | Deviation from an EMA of sequential lexical similarity | Confirmed behavioral drift or failure |
| Governance confidence | Current implementation derives this as 1 minus latest lexical entropy | Calibrated probability or validated confidence |

These are operational definitions of the current implementation, not validated interpretations of LLM behavior. Any broader interpretation requires a separate operational definition and empirical evaluation.

## Known engineering hardening items

| Item | Main baseline status | Required action |
|---|---|---|
| Laplace error-count validation | Hardened on audit branch | Reject non-integer, Boolean, negative, and errors-greater-than-total inputs |
| Anomaly threshold finiteness | Hardened on audit branch | Reject NaN and positive/negative infinity |
| Deep immutability of observation context | Main remains shallow | Integrate and test supported recursive freezing before claiming deep immutability |
| Historical evidence provenance for Dynamic Envelope | GAP-034 contract only on Session C development branch | Implement separately with component-level evidence and snapshot provenance |
| Runtime/provider event transport | Not established | Define transport, retry, acknowledgement, ordering, and failure semantics |
| Durable sequence and restart recovery | Not implemented | Define persistence and recovery contract before implementation |

## Required discipline for the next phase

1. Do not convert a unit-test result into a scientific claim.
2. Do not treat configurable quantiles as validated universal thresholds.
3. Record metric direction explicitly in each experiment.
4. Preserve the neutral observation boundary when adding new signal producers.
5. Keep candidate recommendation separate from runtime mutation.
6. Record experiment configuration, model/version, dataset/task, seed where applicable, and raw outputs sufficient for reproduction.
7. Mark implementation that is still under refinement as **Evolving**, rather than silently treating it as final.
8. Promote a research claim only after the corresponding empirical evidence is documented.

## Definition of the next engineering milestone

The next milestone remains **completion and empirical readiness**, not automatic self-modification. Session C should be completed incrementally: each responsibility should have a clear contract, implementation, tests, documented semantics, and an evidence classification before it is promoted to a stable architectural claim.
