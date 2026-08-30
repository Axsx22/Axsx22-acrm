# ACRM Demo & Dashboard Catalog

## Purpose

This document separates **demonstration artifacts** from the currently implemented ACRM v8.5 runtime. The dashboards and source files supplied during development are valuable engineering/research evidence, but their UI labels, simulated values, heuristics, or prototype algorithms must not be interpreted as proof that every displayed subsystem is implemented in `acrm_core`.

## Evidence boundary

| Artifact | What the source actually contains | Repository role |
|---|---|---|
| ACRM v8 Interaction Field | RTL dashboard, interaction topology, S/ρ/H/RS display, test cards, hidden-state panel, behavior-pattern panel, temporal entropy chart, counterfactual panel, console, and a timed simulated evaluation sequence | Research/demo artifact |
| ACRM v7 Behavioral Runtime Field | Failure-mode heat layer, 17 FM definitions, six test definitions, causal links, temporal trajectory, state vector, console, calibration functions and asynchronous test runners | Research/demo artifact |
| Calibration v6.2 dashboard | Calibration-oriented visual test interface with mock Platt, sigmoid-risk, Laplace and softmax functions plus invariant-style test presentation | Research/demo artifact |
| Failure Mode Taxonomy implementation | Python-side taxonomy/scoring/orchestration material supplied with the demos | Candidate architecture/source material; not silently promoted to v8.5 core |
| ACRM v7.9 Obstruction Theory Layer | Python prototype for structural, semantic, topological, dynamical and critical obstructions; phase classification; force/friction heuristics; transformation blocking and reporting | Research/prototype artifact; reviewed but not core |
| Screen-recorded demos | Visual evidence of supplied UI running on a device | Demonstration evidence |

## Important transparency rule

The dashboards contain simulated/example values and client-side sequences. For example, the v8 Interaction Field demo initializes chart data in JavaScript and changes metrics on timed callbacks when `RUN FIELD EVALUATION` is pressed. It therefore demonstrates an interaction concept and UI behavior, not a production telemetry backend. The source also presents a `V8_LIVE` label, which is retained as part of the original artifact but should not be confused with the Python v8.5 runtime status.

The v7 demo similarly defines its own JavaScript failure-mode registry and six client-side test definitions. Those definitions are useful source material for future contracts, but they are not automatically equivalent to tested v8.5 Python components.

The v7.9 Obstruction Theory source requires the same distinction. Its `measure_topological()` implementation is explicitly a placeholder returning `0.0`; its force calculation is delta-based rather than a demonstrated numerical gradient of a defined potential; and its structural obstruction formula does not by itself make a one-variable addition exceed the default blocking threshold. These observations are documented in `ARCHITECTURE_REVIEW_V7_9.md`.

## v8 Interaction Field: observed components

The supplied HTML defines:

- `Component → Interaction → Behavior → FM → State` as its displayed architecture path;
- an SVG interaction topology with ENG-01, BUS-02, PWR-03, TLM-04 and RLY-05;
- reinforcing, balancing and damping edge types;
- system metrics `S`, `ρ`, `H`, and `RS`;
- hidden sub-state observers;
- recognized behavior patterns;
- temporal entropy vectors;
- counterfactual scenario display;
- an integrated interaction log stream;
- `RUN FIELD EVALUATION` and reset controls.

The runtime sequence changes the displayed values and appends chart points/log entries through JavaScript callbacks. These behaviors are explicitly demo logic and are therefore catalogued separately from `FieldState`.

## v7 Behavioral Runtime Field: observed components

The supplied HTML defines:

- a 17-item failure-mode registry (`FM-01` through `FM-17`);
- severity classes: critical, high, medium and low;
- causal relationships between failure modes;
- six test definitions: Platt Monotonicity, Risk Smoothness, Laplace Stability, Softmax Consistency, Calibration Invariance and Ensemble Sanity;
- state variables `S`, `ρ`, `ARQ`, and an FM vector;
- causal SVG visualization;
- temporal trajectory chart;
- behavioral runtime console;
- client-side test runners and calibration functions.

## v7.9 Obstruction Theory: review boundary

The v7.9 prototype introduces a failure-oriented vocabulary: transformation obstruction, critical states, phase classification, force-like change signals, and friction-like resistance. It is useful research material for a future higher-level ACRM layer.

The engineering review found several items that must be resolved before promotion:

- structural obstruction needs explicit boundary tests because the demonstration's `new_var` example does not inherently produce a blocking score under the supplied formula;
- topological obstruction is currently a placeholder;
- `F = -∇V` is a conceptual statement rather than an implemented gradient of a defined potential;
- force and friction are calculated but do not currently drive the transformation decision;
- phase-transition detection is a fixed classifier heuristic, not a formally established phase-transition model.

See [`docs/ARCHITECTURE_REVIEW_V7_9.md`](ARCHITECTURE_REVIEW_V7_9.md).

## Calibration and failure-mode integration policy

Calibration invariants and failure-mode taxonomy are candidates for a future contract layer. They must be kept separate at three evidence levels:

1. **Software invariant:** a deterministic implementation property is satisfied.
2. **Calibration quality:** statistical calibration is demonstrated on held-out data.
3. **Scientific validity:** the broader ACRM behavioral hypothesis is supported by empirical evidence.

A passing JavaScript or Python invariant test establishes the first category only.

## Integration policy for v8.5

The current v8.5 core remains intentionally small. Demo material should be migrated only when there is:

1. a clear responsibility;
2. a stable input/output contract;
3. explicit assumptions;
4. deterministic tests;
5. a documented failure boundary; and
6. a clear distinction between software evidence and scientific claims.

Accordingly, the dashboards and v7.9 prototype are preserved as **research artifacts**, while `acrm_core/field/state.py` remains the normative implementation boundary for the current v8.5 release line.

## Next demo intake

The remaining supplied demos should be added under `docs/demos/` after their source files are provided in a repository-uploadable form. Screen recordings should be catalogued alongside, but not mixed into, executable source artifacts.
