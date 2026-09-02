# ACRM Source Archive Catalog

This catalog separates historical source artifacts from the current runtime.

## Current runtime — DO NOT MODIFY HERE

- `acrm_core/`
- Session C is an active development stream and is intentionally excluded from historical consolidation.

## Historical source artifacts currently preserved in the repository

### v2.0 refactored archive

- `archive/v2-refactored/`
- Origin: `acrm_v2_refactored (1).zip`
- Status: historical research archive; not current runtime.

### Additional source artifacts identified in the research library

The following source files are available and classified as historical/prototype artifacts. They must remain outside `acrm_core/` unless a future explicit decision promotes a component:

- `acrm_v62_calibration_tests.py (patched).py` — standalone v6.2 calibration/invariant test implementation.
- `AliFarahaniCognitiveModel_v2_1.py` — cognitive-model prototype with an ACRM self-monitoring layer.
- `acrm_v83_reasoning_governance.html` — v8.3 reasoning/governance prototype and interactive implementation.
- `acrm_calibration_tests.html` — browser-based calibration test artifact.
- `acrm_calibration_tests(1).html` — duplicate/versioned browser calibration test artifact.
- `acrm_demo.html` — ACRM v1.3 runtime-behavior demo artifact.

## Classification rule

These artifacts are preserved as lineage, not represented as the current ACRM runtime. Prototype/demo code may contain assumptions, simulated values, or architecture that predates the current Session C contract.

## Evidence boundary

Archive presence does not imply current validity, production readiness, scientific validation, or compatibility with Session C. Historical code is retained so that ACRM's development lineage remains inspectable and reproducible.

## Import policy

1. Never merge historical code directly into `acrm_core/` while Session C is under active development.
2. Preserve original source as faithfully as practical.
3. If a historical artifact requires a corrective patch for archival execution, document the patch separately rather than silently rewriting the historical source.
4. Demos and dashboards belong in archive/demo-oriented paths, not the current runtime.
