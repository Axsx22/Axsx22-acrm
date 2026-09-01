# Changelog

All notable repository changes are recorded here. Version labels distinguish implementation releases from historical research artifacts.

## [Unreleased]

### Added
- Engineering governance and evidence policy in `docs/ENGINEERING_GOVERNANCE.md`.
- Calibration epistemic-invariant test contract in `docs/testing/EPISTEMIC_INVARIANTS.md`.
- v7.9 Obstruction Theory status record preserving the supplied implementation as a research artifact in `docs/research/ACRM_v7_9_OBSTRUCTION_THEORY_STATUS.md`.
- A repository-level implementation/gap matrix in `docs/IMPLEMENTATION_GAP_MATRIX.md` to keep engineering work, validation work, and unimplemented research claims explicitly separated.
- Explicit `high`/`low` signal direction support for dynamic readiness evaluation.
- Unit coverage for invalid quantiles, non-numeric/non-finite history, and signal-direction behavior.

### Changed
- Refined `FieldEnvelopeEstimator` and `DynamicReadinessEvaluator` for clearer validation, maintainability, and explicit calibration boundaries.
- Documented that dynamic thresholds are configurable engineering parameters rather than scientifically universal constants.

### Policy
- Advanced prototype concepts are not promoted into the v8.5 core without contracts, tests, documentation, and evidence.
- Scientific claims are explicitly separated from software-test results.
- Empirical validation remains a separate workstream and is not represented as complete by unit-test success.

## [8.5.0]

### Implemented
- Immutable validated `FieldState` core contract.
- Contract-focused unit tests.
- Python packaging for Python 3.10+.
- GitHub Actions CI across Python 3.10–3.13.

### Explicitly not claimed
- Behavioral inference engine.
- Causal analysis engine.
- Autonomous governance controller.
- Intervention engine.
- Scientific validation of the broader ACRM research hypotheses.
