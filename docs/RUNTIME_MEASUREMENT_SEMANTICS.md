# Runtime Measurement Semantics and Limitations

**Status:** Implemented measurement definitions; empirical validity not established  
**Scope:** ACRM v8.6 Runtime and built-in Specialist Governance  
**Purpose:** Prevent computational proxies and configured heuristics from being mistaken for semantic measurements or empirically calibrated probabilities.

## 1. Measurement boundary

The current Runtime computes deterministic lexical/statistical features from supplied turns. These values describe properties of the tokenized input under the current implementation. They do not, by themselves, establish meaning preservation, reasoning quality, user-intent preservation, truth, uncertainty, or behavioral drift.

The current implementation is a baseline measurement system. Its outputs are suitable for software-contract testing and controlled evaluation, but their interpretation requires separate empirical validation.

## 2. Lexical similarity and coherence

The Runtime tokenizes text into lowercase word-like units and builds term-frequency vectors. Cosine similarity is then used for adjacent-turn sequential similarity, centroid-based coherence, and user/model alignment-gap calculation.

These are lexical-overlap proxies. Paraphrases with different vocabulary can score low despite semantic similarity. Contradictory statements with shared vocabulary can score high. Tokenization does not resolve negation, reference, entailment, task intent, or discourse structure. The centroid is a weighted aggregate of token counts, not a semantic representation.

Accordingly, `avgS`, `avgRho`, and `delta` must be interpreted according to their implementation definitions, not as direct measures of semantic coherence or intent alignment.

## 3. Entropy

The current `_entropy` function computes normalized Shannon entropy over the term-frequency distribution of one turn:

`H = -sum(p_i * log2(p_i)) / log2(V)` for vocabulary size `V > 1`; empty or single-token-type vectors return zero.

This is lexical-distribution entropy. It is not model predictive entropy, calibrated uncertainty, confidence, or semantic entropy.

## 4. FieldState governance_confidence compatibility field

For compatibility with the current FieldState schema, FieldRuntime currently assigns `governance_confidence = 1 - last_entropy`, bounded to [0, 1].

This is a lexical-entropy-complement proxy. It is not a calibrated probability, a measure of specialist agreement, a confidence estimate validated against outcomes, semantic certainty, or evidence sufficiency.

The field name is retained for compatibility. Its current Runtime population must be treated as a legacy semantic mismatch pending a separately versioned schema/API decision. Consumers must not use it as a probabilistic confidence value.

## 5. Anomaly and resilience descriptors

The sequential anomaly index identifies the first inspected adjacent-turn similarity deviation that exceeds the configured threshold relative to an exponentially updated baseline. The resilience descriptor is derived from the difference between the final EMA and the mean sequential similarity.

These are deterministic descriptions of the current lexical signal path. They do not establish that a detected anomaly is a meaningful behavioral deviation or that the resilience value corresponds to a validated resilience construct.

## 6. Specialist governance assumptions

The built-in Specialist Governance currently uses fixed reliability constants in `SPECIALISTS`, keyword-based domain applicability, hand-authored metric thresholds and directional rules, and weighted aggregation based on reliability, report confidence, and evidence strength.

The reliability constants are configured weights, not measured specialist accuracy rates. The keyword rules are not a validated semantic classifier. The report confidence and evidence-strength values in the default reasoner are configured heuristics, not calibrated estimates.

These values must remain labeled as heuristic configuration until evaluated against independent labeled cases and compared with appropriate baselines.

## 7. Calibration terminology

The functions named `platt`, `sigmoid_risk`, `laplace`, and `softmax` implement numerical transformations or smoothing rules. `run_calibration_checks` checks selected mathematical properties on fixed examples.

Passing those checks establishes only the tested numerical properties. It does not establish empirical probability calibration, reliability, discrimination, or predictive validity against observed outcomes.

The Laplace function accepts integer counts only, requires `0 <= errors <= total`, and preserves the existing `(0, 0) -> 1.0` convention. The latter is a compatibility convention for the empty sample, not an empirical estimate.

## 8. Required empirical work

Before stronger measurement claims are made, experiments should include:

1. Human- or task-defined labels for meaningful trajectory changes.
2. Lexical baselines and semantic/intent-aware comparison baselines.
3. False-positive and false-negative analysis.
4. Sensitivity analysis for thresholds and EMA parameters.
5. Repeated runs and confidence intervals where appropriate.
6. Cross-model and cross-provider evaluation.
7. Ablation of individual metrics and specialist heuristics.
8. Calibration evaluation against labeled outcomes, if probabilistic confidence is claimed.

No result in this document asserts that these experiments have already been completed.

## 9. Change-control rule

A future change to metric semantics, thresholds, reliability weights, or the FieldState confidence field requires an explicit contract update, tests for changed computational behavior, migration/compatibility analysis where public fields change, documentation of the new evidence level, and empirical validation when the change is presented as improving behavioral measurement.
