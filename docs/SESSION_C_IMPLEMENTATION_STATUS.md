# Session C implementation status (experimental)

Session C is present on `main` as a tested engineering checkpoint.

## Implemented

- C-A remains a neutral append-only observation boundary.
- C-B receives accumulated observations as a trajectory rather than relying solely on a fixed observation count.
- Field-relative envelope estimation derives warning and critical limits from observed numeric history.
- Envelope quantiles are explicit configurable parameters rather than hidden constants.
- Readiness distinguishes NORMAL, WARNING, and CRITICAL states and requires persistent trajectory evidence before candidate preparation.
- Readiness supports both `high` and `low` signal directions so the evaluator does not silently assume that larger values are always worse.
- Topic is inferred from accumulated observation signals in C-B.
- Candidate testing and topic-aware weighted review remain isolated from the active runtime.
- No runtime mutation or switch execution API is exposed.

## Calibration limitation

The envelope estimator is an engineering prototype. Its quantile parameters are configurable policy parameters; they are not claimed to be universally correct. The repository now validates parameter ordering and non-finite/non-numeric history handling, but real field calibration and empirical validation remain future work.

Signal direction is likewise an explicit engineering parameter. A production or research evaluation should justify the selected direction for each metric rather than assuming that `high` is universally adverse.

The topic taxonomy is a constrained implementation, not a claim that the full research-space topic ontology has been solved.

## Verification boundary

Unit tests cover trajectory profiling, field-derived envelope estimation, calibration edge cases, signal direction, early warning, topic inference, and C-B orchestration. Repository CI remains the authoritative integration check.

Passing unit tests demonstrate implementation behavior only. They do not establish the broader ACRM scientific hypotheses.
