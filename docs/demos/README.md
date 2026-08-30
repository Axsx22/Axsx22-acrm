# ACRM Demos

This directory is reserved for executable dashboard prototypes and their supporting evidence.

## Classification

**Demo / prototype:** a visual or interactive artifact used to explore an ACRM concept.

**Core implementation:** code that belongs to the tested v8.5 runtime contract.

**Evidence:** screenshots or screen recordings showing a demo being executed.

A demo is not promoted to core merely because it contains sophisticated UI, metrics, algorithms, or a convincing runtime simulation.

## Current source material reviewed

- ACRM v8 — Interaction Field Architecture
- ACRM v7 — Behavioral Runtime Field
- Calibration v6.2 dashboard
- Failure Mode Taxonomy source material
- ACRM v2.0 technical roadmap

The supplied v8 and v7 HTML files were inspected directly. They contain substantial client-side visualization and simulation logic and are therefore valuable research artifacts. Their observed behavior is documented in `../DEMO_CATALOG.md`.

## Planned layout

```text
Demos/
├── README.md
├── v6.2-calibration/
├── v7-behavioral-runtime/
├── v8-interaction-field/
├── screenshots/
└── videos/
```

## Reproducibility note

The original dashboards depend on browser-side JavaScript and, in places, external CDN resources such as Chart.js and Google Fonts. When executable copies are committed, the README for each demo should state its dependencies and whether the demo is self-contained/offline-capable.

## Evidence note

The screen recordings supplied during development are useful for showing that the dashboards were exercised on a device. They should be labelled with the demo name, version/date when known, and whether the observed behavior is simulated or connected to a real backend.

## Transparency rule

Historical prototypes and roadmap documents describe design intent and prior experiments. They do not, by themselves, establish that a capability exists in `acrm_core`. Promotion into v8.5 requires a defined contract, implementation, and tests.
