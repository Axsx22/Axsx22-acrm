# Session C implementation status (experimental)

This branch contains the current experimental implementation of the Session C architecture.

## Implemented

- C-A remains a neutral append-only observation boundary.
- C-B receives accumulated observations as a trajectory rather than relying solely on a fixed observation count.
- Field-relative envelope estimation derives warning and critical limits from observed numeric history.
- Readiness distinguishes NORMAL, WARNING, and CRITICAL states and requires persistent trajectory evidence before candidate preparation.
- Topic is inferred from accumulated observation signals in C-B.
- Existing candidate test/review/voting gates remain isolated from the active runtime.
- No runtime mutation or switch execution API is exposed.

## Important limitation

The current envelope estimator is an engineering prototype. Its quantile parameters are configurable policy parameters; they are not claimed to be universally correct. Real field calibration and empirical validation remain future work.

The current topic taxonomy is also a constrained implementation, not a claim that the full research-space topic ontology has been solved.

## Verification

The branch adds unit coverage for trajectory profiling, field-derived envelope estimation, early warning, topic inference, and C-B orchestration. Full CI verification is expected through the repository workflow before this branch is considered mergeable.
