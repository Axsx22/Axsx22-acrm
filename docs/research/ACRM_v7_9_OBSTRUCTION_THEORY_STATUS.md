# ACRM v7.9 — Obstruction Theory Status

## Classification

**Research / architecture artifact — not part of the current v8.5 core.**

This document records the supplied v7.9 Obstruction Theory Layer so that its ideas can be reviewed without silently presenting them as implemented production capabilities.

## Stated objective

The v7.9 design moves from asking whether a transformation succeeds to asking when and why a transformation is obstructed. It introduces continuous obstruction measures, critical points, phase classification, causal-force and friction metaphors, and an obstruction-aware transformation controller.

## Main concepts in the supplied implementation

### Obstruction classes

- structural obstruction;
- semantic obstruction;
- topological obstruction;
- dynamical obstruction;
- critical/phase-transition obstruction.

`ObstructionClass` records source and target fibers, an invariant label, and a continuous measure in `[0, 1]` by convention.

### Causal fibers

`CausalFiber` is an immutable state container holding:

- SCM state;
- intervention history;
- observation history.

It exposes deterministic value lookup and produces a hash from the stored state/history representation.

### Critical-point / phase model

`PhaseDiagram` stores critical points and classifies a fiber using proximity to those points and simple risk thresholds. A phase change is treated as a high obstruction in the supplied simplified implementation.

### Force and friction

`CausalForce` computes a direction-dependent quantity from state differences and structural obstruction. `CausalFriction` applies a linear resistance term to a supplied velocity vector.

These are useful architectural abstractions, but the supplied code does not establish that the quantities are physically meaningful forces or gradients of a formally defined potential.

## Important engineering findings

The supplied code is valuable source material, but several statements must remain hypotheses until formalized and tested:

1. **Obstruction is not yet a mathematical invariant.** The implementation computes heuristic measures; it does not prove invariance under a defined transformation group.
2. **Topological obstruction is currently a placeholder.** `measure_topological` returns `0.0` and assumes connectivity.
3. **Dynamical obstruction is heuristic.** The finite-gradient rule uses a fixed threshold and does not establish a dynamical-systems result.
4. **Semantic obstruction is value-distance based.** A numeric difference threshold of `0.5` is a heuristic, not a general semantic metric.
5. **Critical transitions are simplified.** Phase classification is based on configured thresholds, not an empirically established phase-transition model.
6. **Force is not yet derived from a formal potential.** The code comments use `F = -∇V`, but the implementation does not define `V` and calculate its gradient.
7. **Friction is a model assumption.** The linear coefficient is configurable in code but is not calibrated or validated against observed system dynamics.
8. **Transformation semantics need a contract.** A target with a new variable is treated as structurally obstructed, but the admissibility rules for adding/removing variables are not formally specified.
9. **The demonstration is not validation.** Successful/blocked examples exercise code paths but do not establish predictive accuracy or scientific validity.

## Recommended promotion path

```text
v7.9 research artifact
        ↓
formal definitions
        ↓
component contracts
        ↓
unit/property tests
        ↓
synthetic controlled experiments
        ↓
comparative evaluation
        ↓
independent review
        ↓
possible core integration
```

## First engineering tasks

- Define the mathematical object represented by a `CausalFiber`.
- Define admissible transformations and equivalence relations.
- Replace placeholder topology with an explicit graph/topological contract if required.
- Define each obstruction measure mathematically, including range, monotonicity, and calibration.
- Separate heuristic scores from proven invariants in names and documentation.
- Add property-based tests for symmetry/asymmetry, bounds, determinism, and monotonicity where those properties are actually intended.
- Add experiment fixtures that generate controlled transformations with known outcomes.
- Record false-positive and false-negative behavior before making predictive claims.

## Evidence status

**Current evidence:** supplied source code and demonstration logic.

**Not established by the artifact alone:** scientific obstruction theory, causal validity, physical interpretation, phase-transition detection accuracy, or generalization to LLM runtime behavior.
