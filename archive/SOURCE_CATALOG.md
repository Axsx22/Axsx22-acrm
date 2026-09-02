# ACRM Historical Source Catalog

## Purpose

This directory preserves historical ACRM source artifacts separately from the current runtime.

**Evidence boundary:** archived material is historical/research/prototype material unless explicitly identified otherwise. It is not part of the current runtime merely because it is archived here.

## Runtime boundary

- Current runtime: `acrm_core/`
- Current Session C flow: **LOCKED / DO NOT TOUCH** during this archival phase.
- Historical material must not be merged into `acrm_core/` during archival.

## Archived sources

### v2-refactored

Source: `acrm_v2_refactored (1).zip`

Contents:
- `core/__init__.py`
- `core/audit.py`
- `core/cluster.py`
- `core/consensus.py`
- `core/fault.py`
- `core/gate.py`
- `core/session.py`
- `core/stats.py`
- `core/tracker.py`
- `test/test_core.py`
- `README.md`

Status: historical research archive. Preserved separately from the current runtime.

The archived copy received only the explicitly documented historical regression fixes that had already been established before archival: missing `Optional` import, gate recovery-counter behavior, `recover_node`, and its regression test. No Session C code was changed.

## Pending historical source inventory

The following known historical artifacts remain candidates for archival after exact byte/content transfer is available:

- `acrm_v62_calibration_tests.py (patched).py` — ACRM v6.2 standalone calibration/failure-taxonomy test suite.
- `AliFarahaniCognitiveModel_v2_1.py` — historical cognitive-model source.
- `acrm_v83_reasoning_governance.html` — v8.3 reasoning/governance prototype.
- `acrm_v7.html` — historical v7 HTML artifact.
- `acrm_demo_v19.html` — v1.9 direction-based controller demonstration.
- `acrm_demo.html` — historical demonstration.
- `Index.html` — historical dashboard/index artifact.
- `aics_dashboard.html` — historical dashboard artifact.
- `acrm_calibration_tests.html` / `acrm_calibration_tests(1).html` — historical calibration-test HTML artifacts; duplicates should be verified before retaining both.

## Classification rule

Historical source is archived **as-is**. Refactoring, correction, modernization, or semantic changes belong to a later audit phase and must not be mixed with lineage preservation.

## Audit phase

After the complete historical inventory is transferred, perform a separate archive audit for:

1. missing sources,
2. duplicate artifacts,
3. incorrect version classification,
4. broken historical references,
5. accidental overlap with `acrm_core/`, and
6. documentation consistency.

Only after that audit should any archive corrections be made.
