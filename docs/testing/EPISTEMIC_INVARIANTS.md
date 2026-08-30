# ACRM Calibration — Epistemic Invariants

## Purpose

The calibration layer requires behavioral contracts that remain true across valid implementations. These are **software invariants**, not proof that the calibration model is scientifically correct.

The six invariants below originate from the reviewed ACRM v6.2 calibration design and should be implemented only against concrete calibration functions with an explicit API contract.

## 1. Platt monotonicity

**Invariant:** if `raw1 > raw2`, then `platt(raw1) >= platt(raw2)`.

Test the interior, equality, and descending cases. A descending pair is expected to preserve the monotone ordering and therefore should not trigger a false failure.

## 2. Risk smoothness

**Invariant:** a sufficiently small change in stability should produce a bounded change in risk.

A Lipschitz-style test may be used:

```text
|risk(S2) - risk(S1)| <= k * |S2 - S1| + tolerance
```

The value of `k` must come from the actual calibration function or a documented bound. It must not be treated as a universal constant without derivation.

## 3. Laplace boundary stability

**Invariant:** uncertainty remains non-zero at zero observed errors when smoothing is intended, and approaches its high-error limit as the error rate approaches one.

The exact formula and boundary semantics must be documented before asserting numerical thresholds such as `0.99`.

## 4. Softmax consistency

For finite score inputs:

- probabilities are non-negative;
- probabilities sum to approximately one within numerical tolerance;
- strict score ordering is preserved for equal-temperature softmax.

The implementation should use numerically stable exponentiation for large-magnitude inputs.

## 5. Calibration ranking invariance

**Invariant:** a strictly monotone transformation should preserve ranking.

This test must be phrased carefully. Arbitrary scaling is not a general invariance of Platt calibration's *probability values*. What can be required is ranking preservation when the transformation remains within the documented monotone calibration contract.

Therefore, the test must not claim that `platt(x) == platt(2x)`; it only checks the ordering of outputs.

## 6. Ensemble weight sanity

If an uncertainty/error-derived quantity is converted into ensemble weights, the contract must state the direction explicitly.

For the supplied v6.2 example, lower error rate is expected to produce higher weight after normalization. The test should therefore verify:

```text
better calibrated performance → no lower ensemble weight
sum(normalized_weights) ≈ 1
weights are finite and non-negative
```

This requires the actual weighting function. A raw uncertainty score must not be mislabeled as a weight without documenting the inversion/normalization step.

## Test classification

| Test | Software invariant | Scientific claim? |
|---|---|---|
| Platt monotonicity | Yes | No |
| Risk smoothness | Yes, if bound is defined | No |
| Laplace stability | Yes, if formula is defined | No |
| Softmax consistency | Yes | No |
| Ranking invariance | Yes, under stated transform | No |
| Ensemble weight sanity | Yes, after weight contract | No |

Passing these tests establishes implementation compliance. It does **not** establish calibration quality, predictive validity, causal validity, or generalization across models.

## Promotion criteria

Before adding these tests to the normative core:

- [ ] concrete `Calibration` API exists;
- [ ] each function has a mathematical/behavioral contract;
- [ ] numerical tolerances are justified;
- [ ] edge cases are covered;
- [ ] property-based testing is considered for monotonicity and bounds;
- [ ] implementation is independent of dashboard/demo code;
- [ ] CI executes the suite.
