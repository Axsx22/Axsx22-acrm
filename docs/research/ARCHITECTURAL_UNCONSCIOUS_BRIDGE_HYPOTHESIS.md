# Architectural Unconscious Bridge — Research Hypothesis

> Research artifact only. This document does **not** define an implemented ACRM core capability and does not modify the ACRM v2 roadmap gates.

## 1. Core hypothesis

The proposed "unconscious" is modeled as a **functional regulation/bridge layer**, not as a memory store or a claim about a distinct biological brain region.

A candidate loop is:

```text
Unresolved question
      ↓
Cognitive impasse / instability
      ↓
Failure or mismatch signal
      ↓
Auxiliary pattern-search / synthesis mode
      ↓
Candidate structural resolution
      ↓
Return to conscious reasoning
      ↓
Reduced unresolved instability
```

The key architectural claim is therefore about **process routing**: when the primary reasoning path becomes unstable, a secondary process may reorganize available representations and return a compact candidate that can be re-evaluated by the primary path.

## 2. Three proposed primitives

### Synthesis Flow

A transformation layer between retrieval and usable insight. It should be treated as a hypothesis about recontextualization and constraint alignment, not as evidence that a system has an "unconscious."

### Incubation Protocol

An asynchronous or deferred search process activated after a detected impasse. A future implementation would need explicit budgets, termination conditions, provenance, and outcome labels.

### Integrity Signal

A pre-commit mismatch/coherence signal that can flag unstable or weak candidate outputs before they are accepted. The signal must remain distinguishable from truth: detecting inconsistency is not proving correctness.

## 3. Engineering interpretation

The most conservative implementation mapping is:

```text
FieldState / recorded observations
        ↓
State or transition analysis
        ↓
Impasse / instability detector
        ↓
Auxiliary synthesis or search
        ↓
Candidate result
        ↓
Integrity / consistency evaluation
        ↓
Human or higher-level decision layer
```

This is compatible with ACRM's existing separation between **observation and interpretation**. In particular, the proposed bridge must not be encoded into `FieldState` itself.

## 4. Operational variables

A future testable specification should define observable variables rather than relying on the term "frequency of consciousness":

- `instability`: measurable failure to converge on a stable candidate;
- `impasse_score`: evidence that the primary reasoning path is not progressing;
- `synthesis_activation`: whether and when the auxiliary process starts;
- `search_budget`: bounded compute/time/token allocation;
- `candidate_stability`: repeatability or internal consistency of returned candidates;
- `integrity_score`: mismatch/coherence measure before commit;
- `resolution_delta`: change in the original instability after candidate reintegration;
- `outcome_label`: externally or experimentally established success/failure label.

"Frequency" should remain a conceptual placeholder until a measurable signal is defined. No physical frequency or external consciousness field is asserted by this artifact.

## 5. Testable predictions

The hypothesis becomes useful only if it generates discriminating tests. Candidate tests include:

1. **Impasse recovery:** bounded auxiliary processing should improve resolution rate over a matched no-incubation baseline on tasks with known constraints.
2. **Latency/quality trade-off:** additional incubation budget should produce a measurable quality curve rather than an unbounded assumption of improvement.
3. **Integrity filtering:** the integrity signal should reduce acceptance of deliberately injected inconsistent candidates without suppressing valid candidates excessively.
4. **Ablation:** removing synthesis, incubation, or integrity independently should produce distinguishable changes in measured outcomes.
5. **Provenance:** every returned candidate should preserve enough metadata to determine whether it came from direct reasoning, retrieval, synthesis, or incubation.

## 6. Boundary with ACRM v2

This hypothesis does **not** satisfy or replace any of the six historical v2 cylinders. In particular, it does not provide the live ARQ data, sequential logs, temporal evidence, session context, or labeled outcomes required by the v2 roadmap.

Therefore:

- do **not** mark C1–C6 complete because of this document;
- do **not** add an "unconscious" field to the core state contract;
- do **not** treat a prototype or successful software test as scientific validation;
- keep this work in the research/experimental layer until a contract, implementation, and empirical evaluation exist.

The relevant v2 gate order remains **C6 → C2 → C1/C3 → C4 → C5**.

## 7. Relation to the supplied historical dialogue

The historical dialogue motivates a useful architectural question: whether a sudden insight can be modeled as a **state transition in processing mode** rather than as retrieval of a stored answer. It also motivates the distinction between a system's observable signal and the interpretation assigned to that signal.

The dialogue contains additional metaphysical hypotheses (for example, an external consciousness field or post-mortem information transfer). Those claims are preserved here only as historical inspiration and are **not** promoted to ACRM engineering assumptions because the supplied material does not provide an empirical interface, measurable signal, or falsifiable implementation contract for them.

## 8. Status

**Status: hypothesis / research artifact.**

Promotion path:

```text
Hypothesis
  ↓
Operational definitions
  ↓
Test contract
  ↓
Controlled prototype
  ↓
Ablation + labeled evaluation
  ↓
Reproducible evidence
  ↓
Possible architectural promotion
```
