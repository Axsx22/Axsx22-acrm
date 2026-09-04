# ACRM Repository Review Guide

**Repository:** ACRM v8.5  
**Review mode:** code-first, contract-first, evidence-aware

## 1. What this repository represents

This repository is a research-to-runtime engineering project. It contains both a concrete executable core and research lineage. The presence of a concept, historical artifact, dashboard, or architecture document does not by itself mean that capability is implemented in the current runtime.

The current executable center is `FieldState` plus the actively developing Session C implementation.

## 2. Recommended review order

### Step 1 — Repository scope

Read:

1. `README.md`
2. `docs/ACRM_v8_5_DEVELOPMENT_STATUS.md`
3. `docs/IMPLEMENTATION_GAP_MATRIX.md`
4. `docs/SESSION_C_IMPLEMENTATION_STATUS.md`

This establishes what is implemented, what is evolving, and what is explicitly outside scope.

### Step 2 — Canonical state contract

Inspect:

- `acrm_core/field/state.py`
- `docs/FIELD_STATE_CONTRACT.md`
- `tests/unit/test_field_state.py`

Review questions:

- What state is accepted?
- What invariants are enforced?
- Is the state immutable?
- Are timestamps and numeric values normalized/validated?
- Does the contract avoid embedding interpretation or intervention logic?

### Step 3 — Session C observation boundary

Inspect:

- `acrm_core/session_c/observation.py`
- `tests/unit/test_session_c_observation_boundary.py`

Review questions:

- Is observation neutral?
- Is the observation log append-only?
- Are observations immutable?
- Is interpretation kept downstream of the observation boundary?

### Step 4 — Dynamic and trajectory analysis

Inspect:

- `acrm_core/session_c/dynamic.py`
- `tests/unit/test_session_c_dynamic.py`

Pay particular attention to the distinction between:

- historical quantile envelope estimation;
- explicit signal direction;
- readiness evaluation;
- trajectory descriptors;
- persistence descriptors.

Do not assume that an implementation-level descriptor automatically establishes the broader research concept with the same name.

### Step 5 — Topic inference

Inspect:

- `acrm_core/session_c/topic.py`
- corresponding topic tests.

Determine whether the constrained taxonomy is sufficient for the current checkpoint. Do not evaluate it as though it claimed to be a complete semantic ontology.

### Step 6 — Evolution governance

Inspect:

- `acrm_core/evolution/session_c.py`
- `acrm_core/session_c/orchestrator.py`
- `tests/unit/test_session_c.py`
- `tests/unit/test_session_c_orchestrator.py`

Trace the full path:

```text
observations
    ↓
generation gate
    ↓
candidate
    ↓
independent tester
    ↓
test gate
    ↓
specialist voting
    ↓
evolution decision
```

Verify that candidate source is not implicitly executed and that recommendation is separated from runtime mutation.

### Step 7 — CI and packaging

Inspect:

- `pyproject.toml`
- `.github/workflows/ci.yml`

Verify supported Python versions, installation path, test command, and whether CI reflects the repository's documented verification boundary.

## 3. Maturity rules

Use the following classification during review:

| Classification | Interpretation |
|---|---|
| Implemented | Code or runtime contract exists. |
| Tested | Automated tests verify the defined behavior. |
| Evolving | Implemented and inspectable, but still under active refinement. |
| Specified | Documented architecture/contract without equivalent current runtime implementation. |
| Empirical | Requires controlled measurements. |
| Independent | Requires external reproduction or review. |
| Future | Explicitly outside the current runtime. |

A reviewer should not convert an **Evolving** component into either a defect or a final capability without examining its stated responsibility and development status.

## 4. Evidence rules

The repository separates four different questions:

1. **Does the code exist?** — implementation evidence.
2. **Does the code satisfy its contract?** — software-test evidence.
3. **Does the mechanism work as a behavioral/research hypothesis?** — empirical evidence.
4. **Does the result reproduce independently?** — external evidence.

A passing unit test answers question 2. It does not automatically answer questions 3 or 4.

## 5. Review output format

A rigorous review should report findings using this structure:

```text
Component:
Responsibility:
Current maturity:
Implementation evidence:
Test evidence:
Observed semantics:
Architectural claim:
Equivalence / mismatch:
Severity:
Required action:
Evidence needed for promotion:
```

Use **mismatch** only when the implementation materially differs from the responsibility claimed at its current maturity level. Use **evolving limitation** when the behavior is explicitly provisional and consistent with the current development checkpoint.

## 6. What is intentionally not required for this checkpoint

The current repository does not need to be judged as a complete autonomous agent or complete self-modifying system. In particular, the absence of runtime source execution, automatic deployment, causal inference, or full behavioral inference is explicitly documented rather than silently missing.

Those capabilities may become future architectural layers, but they should not be used as defects against the current v8.5 scope unless the repository later claims them as implemented.

## 7. Review principle

> **Review what the repository actually implements, compare it with the responsibility it currently claims, and classify the gap by maturity and evidence level before calling it a defect.**
