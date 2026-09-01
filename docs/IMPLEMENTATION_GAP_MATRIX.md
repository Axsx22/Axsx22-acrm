# ACRM implementation and validation gap matrix

**Status:** Active engineering control document  
**Scope:** ACRM v8.5 core and Session C  
**Purpose:** Keep implemented behavior, engineering verification, empirical validation, and future research claims explicitly separated.

## Status vocabulary

| Status | Meaning |
|---|---|
| Implemented | Present in the repository as executable code or a defined contract. |
| Tested | Covered by automated repository tests. |
| Specified | Defined architecturally or contractually, but not necessarily implemented. |
| Empirical | Requires measurements from controlled experiments rather than unit tests. |
| Independent | Requires reproduction or review outside the original implementation context. |
| Future | Not currently implemented and should not be implied by the v8.5 core. |

## Matrix

| Capability / claim | Current state | Evidence | Remaining work |
|---|---|---|---|
| Immutable FieldState contract | Implemented + Tested | `acrm_core/field/state.py`, unit tests | None for current contract; extend only with new requirements. |
| Neutral append-only C-A observation boundary | Implemented + Tested | `acrm_core/session_c/observation.py`, boundary tests | Add integration coverage as external producers are introduced. |
| Temporal trajectory profiling | Implemented + Tested | `TrajectoryAnalyzer`, dynamic tests | Validate descriptors against real longitudinal datasets. |
| Field-relative dynamic envelope | Implemented + Tested | `FieldEnvelopeEstimator`, dynamic tests | Empirically calibrate quantiles across models, tasks, and signal distributions. |
| High/low signal direction | Implemented + Tested | `DynamicReadinessEvaluator(direction=...)` | Define metric-specific direction in experimental protocols. |
| Dynamic readiness gating | Implemented + Tested | `DynamicReadinessEvaluator`, Session C tests | Measure false-positive/false-negative behavior experimentally. |
| Constrained topic inference | Implemented + Tested | `FieldDrivenTopicEngine`, topic tests | Expand taxonomy only when supported by evidence and a stable contract. |
| Candidate generation boundary | Implemented / isolated | `EvolutionSessionC` contracts | Connect to controlled candidate-generation experiments without enabling implicit runtime mutation. |
| Candidate testing gate | Implemented + Tested | Session C orchestration tests | Add adversarial and property-based testing around candidate artifacts. |
| Weighted specialist review | Implemented + Tested | Session C orchestration tests | Validate weighting assumptions against independent evaluators. |
| Runtime mutation / automatic deployment | Future | Explicitly absent from current Session C | Requires a separate safety and governance design; must never be inferred from candidate recommendation. |
| Causal analysis | Future | Not implemented in v8.5 core | Requires a separately defined causal methodology and evidence. |
| Full behavioral inference engine | Future | Not implemented | Define falsifiable scope and evaluation protocol before implementation. |
| Scientific threshold calibration | Empirical | Unit tests are insufficient | Run controlled multi-model longitudinal experiments and publish calibration results. |
| Long-horizon behavioral claims | Empirical | Research documents and hypotheses only | Execute preregistered or otherwise controlled long-horizon evaluations. |
| Multi-model generalization | Empirical | No completed repository result currently establishes it | Compare across model families, prompts/conditions, and repeated runs. |
| Independent reproduction | Independent | Not yet established | Provide reproducible experiment package and obtain external replication/review. |

## Required discipline for the next phase

1. Do not convert a unit-test result into a scientific claim.
2. Do not treat configurable quantiles as validated universal thresholds.
3. Record metric direction explicitly in each experiment.
4. Preserve the neutral observation boundary when adding new signal producers.
5. Keep candidate recommendation separate from runtime mutation.
6. Record experiment configuration, model/version, dataset/task, seed where applicable, and raw outputs sufficient for reproduction.
7. Promote a research claim only after the corresponding empirical evidence is documented.

## Definition of the next engineering milestone

The next milestone is **empirical readiness**, not automatic self-modification. The repository should first make it possible to run controlled longitudinal experiments, capture immutable evidence, compare conditions, and reproduce results before any broader runtime-control mechanism is considered.
