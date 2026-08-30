# ACRM v7.9 Obstruction Theory — Engineering Review

**Review status:** Reviewed / research artifact / not promoted to `acrm_core`

**Review basis:** supplied v7.9 Python source, existing ACRM v8.5 repository contracts, failure-mode taxonomy, benchmark proposal, and calibration dashboard source.

## 1. Executive assessment

ACRM v7.9 is a substantial research prototype that extends the earlier architecture from observing successful transformations toward explicitly representing reasons a transformation may fail. The conceptual vocabulary — structural, semantic, topological, dynamical, and critical obstruction; phase classification; force/friction metaphors — is useful as an experimental architecture.

It should **not** currently be described as a mathematically implemented obstruction theory. Several quantities are explicitly simplified heuristics, some claimed physical/mathematical relationships are only analogies, and the supplied implementation contains paths whose observed behavior does not fully match their comments or demonstration labels.

Engineering disposition: **preserve, catalogue, test, and refine; do not silently merge into the v8.5 core.**

## 2. Evidence classification

| Element | Current evidence | Classification |
|---|---|---|
| `ObstructionClass` data model | Implemented in supplied source | Prototype implementation |
| Structural obstruction | Implemented heuristic based on variable-set mismatch | Prototype metric |
| Semantic obstruction | Implemented numeric difference heuristic | Prototype metric |
| Topological obstruction | Always returns `0.0` | Placeholder |
| Dynamical obstruction | Implemented average-change heuristic | Prototype metric |
| Critical points / phase classification | Implemented threshold classifier | Prototype mechanism |
| Force field | Implemented delta-based heuristic | Prototype mechanism; not validated gradient field |
| Friction | Implemented linear damping heuristic | Prototype mechanism |
| Transformation blocking | Implemented using obstruction threshold | Executable behavior, not empirical validation |
| Mathematical obstruction theory | Not established by source | Research hypothesis / future formalization |

## 3. Important implementation findings

### 3.1 Structural obstruction does not necessarily block the demonstrated `new_var` case

The structural metric is the symmetric difference in variable names divided by the union size. Adding one variable to an otherwise nine-variable state therefore produces a value around `1/10 = 0.1`, below the default blocking threshold `0.5`.

Therefore the demonstration comment **"BLOCKED TRANSFORMATION (Structural)"** is not supported by the supplied formula alone. The transformation may remain permitted unless another obstruction crosses the blocking threshold.

This is a concrete behavioral mismatch and should become a regression test before the artifact is presented as deterministic evidence.

### 3.2 Topological obstruction is a placeholder

`measure_topological()` always returns `0.0` and explicitly states that connectivity checking is simplified. Consequently, the v7.9 implementation does not currently detect a disconnected fiber space.

The correct engineering label is **unimplemented/placeholder**, not "topological obstruction detection".

### 3.3 The force implementation is not a demonstrated gradient of a potential

The comments state `F = -∇V`, where `V` is an obstruction potential. The implementation instead calculates a state delta multiplied by `(1 - structural_obstruction)`. No potential function is defined and no numerical gradient is taken.

This is a useful heuristic force-like signal, but the stronger mathematical statement should remain a hypothesis until a potential function and gradient definition are specified and tested.

### 3.4 Net friction/force is calculated but not used to determine transformation

`attempt_transform()` calculates `forces`, `friction`, and `net_force`, but the success decision is based only on blocking obstruction classes. Thus the force/friction layer currently has no causal effect on whether the transformation succeeds.

That is acceptable for an exploratory prototype, but the architecture should distinguish **computed telemetry** from **decision-driving state**.

### 3.5 Critical/phase obstruction is a threshold heuristic

A phase change is represented by a change in a classifier label, with a fixed obstruction value of `0.8`. This is a practical prototype rule, not evidence of a physical phase transition or a mathematically characterized critical phenomenon.

The documentation should use terms such as `phase-transition heuristic` or `critical-state classifier` until formal criteria exist.

## 4. Recommended contract before promotion

Before any v7.9 component enters `acrm_core`, define a narrow contract for each metric:

1. **Input domain** — accepted state representation and value ranges.
2. **Output domain** — exact range and numerical guarantees.
3. **Determinism** — identical inputs produce identical outputs.
4. **Monotonicity / continuity expectations** — where applicable.
5. **Degenerate cases** — empty states, missing variables, nonnumeric values, NaN/inf.
6. **Threshold semantics** — why a value blocks or permits transformation.
7. **Calibration** — how parameters are selected and validated.
8. **Failure modes** — explicit identifiers and severity.
9. **Reference tests** — unit and property-based tests.
10. **Empirical validation** — evidence required before scientific claims are made.

## 5. Relation to the existing ACRM boundary

The current v8.5 repository intentionally defines `FieldState` as a validated, immutable recorded-state contract. It explicitly separates observation from interpretation and does not claim to infer causes, establish causality, make decisions, or perform interventions.

Accordingly, v7.9 should remain outside the v8.5 core until its higher-level semantics are decomposed into independently testable contracts. This preserves the repository's existing evidence boundary rather than allowing a sophisticated prototype to become an implicit production claim.

## 6. Calibration and failure-mode integration

The reviewed calibration artifact defines client-side mock implementations for Platt scaling, sigmoid risk, Laplace smoothing, and softmax, together with invariant-style tests. The failure-mode taxonomy separately defines monotonicity, ranking, uncertainty-calibration, context/memory, coherence, retrieval-association, ensemble, and critical-system families.

These are strong candidates for a future contract layer, but the repository should distinguish:

- **algorithmic invariants** (software-level properties);
- **calibration quality** (empirical statistical property); and
- **scientific validity** of ACRM behavioral hypotheses.

A passing invariant test establishes the first category only.

## 7. Recommended next engineering sequence

### Phase A — Freeze the artifact

Preserve v7.9 as a versioned research artifact. Do not rewrite its history to make it appear more mature than it is.

### Phase B — Build a deterministic test harness

Add tests for:

- structural obstruction boundary behavior;
- semantic obstruction boundary behavior;
- topological placeholder behavior;
- dynamical obstruction bounds;
- critical-point classification;
- force-field determinism;
- friction sign and magnitude;
- transformation decision consistency;
- empty/degenerate state handling.

### Phase C — Separate mechanism from metaphor

Rename or document heuristic quantities so that terms such as `force`, `potential`, `phase transition`, and `topological connectivity` are not interpreted as formal mathematical results unless their definitions are supplied.

### Phase D — Formalize only the claims that survive testing

If the obstruction layer continues to show useful predictive behavior, define the state space, obstruction function, potential function, transition relation, and stability criteria mathematically. Only then consider a formal theorem/obstruction-theory claim.

### Phase E — Empirical evaluation

Use controlled transformations with known outcomes and compare obstruction scores against independently annotated failure events. Report precision/recall, calibration, false positives, false negatives, sensitivity to thresholds, and cross-workload robustness.

## 8. Review conclusion

**Disposition: ACCEPT AS RESEARCH ARTIFACT; REQUIRES HARDENING BEFORE CORE PROMOTION.**

The v7.9 work is valuable because it introduces explicit failure-oriented reasoning into the research archive. Its strongest contribution at this stage is architectural: it creates a vocabulary and executable scaffold for asking *why a transformation fails*. Its weakest point is the gap between the mathematical language used in comments and the simplified heuristics actually implemented.

That gap should be made explicit rather than hidden. Doing so strengthens the credibility of the repository and creates a clean path from prototype → contract → implementation → test → empirical evidence.
