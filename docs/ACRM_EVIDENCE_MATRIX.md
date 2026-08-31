# ACRM Evidence Matrix

This matrix is the repository-level traceability map between claims, architecture, demonstrations, tests, benchmark protocols, evidence strength, and remaining gaps.

| Claim | Architecture | Demo / Artifact | Test / Benchmark | Evidence | Gap |
|---|---|---|---|---|---|
| Long-horizon session trajectory is observable | Field Emergence → Compression → Characterization | v5/v7/v8 demos; Field artifacts | TEST-03 | Demonstrated prototype + unit tests | Independent large-scale validation |
| Session-level monitoring differs from single-turn monitoring | Interaction Field ontology | v8 field demo | TEST-03 | Architectural claim + prototype | Comparative baseline study |
| Field is an interaction phenomenon, not a transcript | Field Ontology | Appendix A | Ontology review | Canonical design premise | Empirical operationalization |
| ACRM is an observer, not a controller | Alert-only boundary | v5/v8 demos | TEST-04 | Strong architectural invariant | Independent reproduction |
| Output is not modified | Pass-through architecture | Integration demos | TEST-04 | Testable invariant | Large-scale benchmark |
| ACRM is modular | Adapter / attach-detach boundary | Integration artifacts | TEST-01 | Explicit protocol + local tests | Independent execution |
| Thresholds can adapt to workload | Self-Tune / dynamic envelope | calibration and Session C prototypes | TEST-02 | Implemented prototype | Empirical calibration |
| Fixed universal thresholds are not sufficient | Field-relative envelope | v2 roadmap / Session C | TEST-02 | Architectural rationale | Baseline comparison |
| Degradation can be detected | Field properties + envelope | dashboards/demos | TEST-03 | Defined ground-truth protocol | TPR/FPR/F1 results |
| False alarms can be controlled | Self-regulation | calibration artifacts | TEST-02 | Mechanism exists | Measured FPR |
| Drift can be detected early | Temporal trajectory | v8 field / Session C | TEST-03 | Prototype | Lead-time comparison |
| Stability and risk can be characterized separately | S, ρ, ARQ + secondary metrics | v2/v7 artifacts | TEST-M / TEST-03 | Formal metric definitions | Metric-independence study |
| ARQ can capture adaptive reasoning quality | ARQ metric | v2/v7 code/docs | TEST-M | Research implementation | External validation |
| Oscillation can be detected | Temporal field model | v2 roadmap | TEST-FM | Specified research direction | Empirical threshold calibration |
| Temporal decay can reduce stale-signal effects | Dynamic temporal model | v2 roadmap | Future FM tests | Architecture specified | Empirical validation |
| Audit trail is tamper-evident | Immutable / signed audit design | v8 artifacts | TEST-05 | Contract + protocol | Independent tamper campaign |
| Multi-model compatibility is possible | Adapter abstraction | provider-neutral artifacts | TEST-07 | Explicit protocol | Four-model empirical result |
| No transformer modification is required | External observer | integration artifacts | TEST-01 | Architectural invariant | Independent integration |
| ACRM complements safety filters | Observer boundary | whitepaper | Scope boundary | Explicit non-goal | Comparative study only if desired |
| ACRM is not RLHF/DPO | Runtime observability boundary | whitepaper | Scope boundary | Explicit separation | None; this is intentional |
| Governance evidence can be produced | Audit + alert channel | dashboards / logs | TEST-05 | Prototype | Compliance-grade validation |
| Degradation can feed governance without direct mutation | Alert-only architecture | Session C | TEST-03/04/05 | Strong safety boundary | End-to-end external validation |
| Workload adaptation is measurable | Self-Tune | calibration artifacts | TEST-02 | Defined test design | Execution |
| Runtime overhead can be bounded | Modular observer | integration demos | TEST-01 | Defined thresholds | Measured production overhead |
| Compliance alignment is possible | Audit/RBAC architecture | technical brief / whitepaper | TEST-05 | Design alignment | Formal audit/certification |
| Failure modes can be structured | ACRM-BRF / FM taxonomy | v7 artifacts | TEST-FM01..03 | Formal research layer | Empirical causal validation |
| ACRM has a coherent research lineage | v5 → v7 → v8.5 → Session C | evolution roadmap | lineage audit | Strong documentary evidence | Version compatibility completion |
| Claims are falsifiable | Architecture + explicit benchmark | ACRM-EVAL | seven benchmark suites | Strong methodology | Independent replication |
| Session C adds governed evolution above monitoring | C-A → trajectory → dynamic envelope → topic → candidate → test → vote | Session C implementation | Session C tests | Experimental implementation | Scientific efficacy vs baseline |

## Evidence classes

- **Demonstrated:** executable demo or recorded behavior exists.
- **Tested:** repository tests exercise the invariant.
- **Specified:** benchmark/contract defines how the claim will be tested.
- **Validated:** independent empirical result exists.
- **Research:** hypothesis, roadmap, or architectural proposal not yet promoted.

## Promotion rule

A claim must not be described as empirically validated merely because a demo, unit test, or benchmark specification exists. The repository must preserve the distinction between implementation evidence and independent empirical validation.
