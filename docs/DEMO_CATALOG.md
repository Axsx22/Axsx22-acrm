# ACRM Demo & Dashboard Catalog

## Purpose

This document separates **demonstration artifacts** from the currently implemented ACRM v8.5 runtime. The dashboards supplied during development are valuable engineering/research evidence, but their UI labels and simulated values must not be interpreted as proof that every displayed subsystem is implemented in `acrm_core`.

## Evidence boundary

| Artifact | What the source actually contains | Repository role |
|---|---|---|
| ACRM v8 Interaction Field | RTL dashboard, interaction topology, S/ρ/H/RS display, test cards, hidden-state panel, behavior-pattern panel, temporal entropy chart, counterfactual panel, console, and a timed simulated evaluation sequence | Research/demo artifact |
| ACRM v7 Behavioral Runtime Field | Failure-mode heat layer, 17 FM definitions, six test definitions, causal links, temporal trajectory, state vector, console, calibration functions and asynchronous test runners | Research/demo artifact |
| Calibration v6.2 dashboard | Calibration-oriented visual test interface and runtime results presentation | Research/demo artifact |
| Failure Mode Taxonomy implementation | Python-side taxonomy/scoring/orchestration material supplied with the demos | Candidate architecture/source material; not silently promoted to v8.5 core |
| Screen-recorded demos | Visual evidence of the supplied UI running on a phone | Demonstration evidence |

## Important transparency rule

The dashboards contain simulated/example values and client-side sequences. For example, the v8 Interaction Field demo initializes chart data in JavaScript and changes metrics on timed callbacks when `RUN FIELD EVALUATION` is pressed. It therefore demonstrates an interaction concept and UI behavior, not a production telemetry backend. The source also explicitly presents a `V8_LIVE` label, which is retained as part of the original artifact but should not be confused with the Python v8.5 runtime status.

The v7 demo similarly defines its own JavaScript failure-mode registry and six client-side test definitions. Those definitions are useful source material for future contracts, but they are not automatically equivalent to tested v8.5 Python components.

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

## Integration policy for v8.5

The current v8.5 core remains intentionally small. Demo material should be migrated only when there is:

1. a clear responsibility;
2. a stable input/output contract;
3. explicit assumptions;
4. deterministic tests;
5. a documented failure boundary; and
6. a clear distinction between software evidence and scientific claims.

Accordingly, the dashboards are preserved as **research artifacts**, while `acrm_core/field/state.py` remains the normative implementation boundary for the current v8.5 release line.

## Next demo intake

The remaining supplied demos should be added under `docs/demos/` after their source files are provided in a repository-uploadable form. Screen recordings should be catalogued alongside, but not mixed into, executable source artifacts.
