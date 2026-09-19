# ACRM External Reviewer Path

**Purpose:** provide a deterministic, code-first path for an engineer, evaluator, QA reviewer, or research collaborator who is seeing the repository for the first time.

This document defines **how to review the repository**, not how to validate the scientific hypotheses behind ACRM.

## 1. Review boundary

The current baseline is:

- **Primary branch:** `main`
- **Current package/runtime:** ACRM v8.6.0
- **Historical version branch:** `acrm-v8.5`
- **Current version branch:** `acrm-v8.6`

The repository deliberately separates:

```text
orientation
   ↓
scope
   ↓
contract
   ↓
implementation
   ↓
tests
   ↓
CI / reproducibility
   ↓
research evidence
```

A reviewer should follow this order before forming conclusions about individual capabilities.

## 2. Reproduce the software baseline first

From a clean checkout:

```bash
git clone https://github.com/Axsx22/Axsx22-acrm.git
cd Axsx22-acrm

python -m venv .venv
source .venv/bin/activate

python -m pip install -e ".[test]"
python -m pytest -q
```

Supported Python range for the current CI baseline is **3.10–3.13**.

The repository currently has no runtime dependency set beyond the Python standard library; the `test` extra supplies the test tooling.

A successful test run establishes software behavior against the repository's defined contracts. It does **not** establish scientific validity, generalization, production effectiveness, or causal claims.

## 3. Recommended review sequence

### Gate A — Orientation

Read:

1. `README.md`
2. `docs/IMPLEMENTATION_GAP_MATRIX.md`
3. `docs/SESSION_C_IMPLEMENTATION_STATUS.md`
4. `docs/ENGINEERING_GOVERNANCE.md`

Use the README for orientation. Use the other documents to determine what is current, evolving, specified, empirical, independent, or future.

The document `docs/ACRM_v8_5_DEVELOPMENT_STATUS.md` is a **historical v8.5 checkpoint**, not the current baseline.

### Gate B — Canonical contract

Inspect:

- `acrm_core/field/state.py`
- `docs/FIELD_STATE_CONTRACT.md`
- `tests/unit/test_field_state.py`

Verify:

- required fields and validation;
- immutability;
- timestamp handling;
- finite numeric metrics;
- failure-mode normalization;
- governance-confidence bounds;
- explicit non-responsibilities.

At this gate, the question is:

> **What does the repository formally record and guarantee at the state boundary?**

Do not infer higher-level semantics from the existence of the data structure.

### Gate C — Runtime implementation

Inspect:

- `acrm_core/runtime/`
- corresponding runtime tests.

Trace the actual execution path from supplied interaction state to runtime measurements, governance evidence, and `FieldState`.

Separate:

- implemented algorithms;
- configurable parameters;
- heuristic choices;
- documented limitations.

The reviewer should be able to identify which behavior is executable without relying on historical demos or research documents.

### Gate D — Session C observer boundary

Inspect:

- `acrm_core/session_c/observation.py`
- `acrm_core/session_c/dynamic.py`
- `acrm_core/session_c/topic.py`
- `acrm_core/session_c/orchestrator.py`
- `acrm_core/evolution/session_c.py`
- corresponding Session C tests.

Trace:

```text
Runtime output / event
        ↓
Session C observation
        ↓
trajectory analysis
        ↓
dynamic/readiness analysis
        ↓
topic / evolution context
        ↓
candidate generation boundary
        ↓
independent test gate
        ↓
specialist review
        ↓
recommendation
        ↓
external authorization
```

Verify specifically that:

- Session C observes rather than silently replacing Runtime internals;
- candidate source is not implicitly executed by the governance path;
- testing is separated from active Runtime mutation;
- `SWITCH_RECOMMENDED` is a recommendation, not an execution command;
- external authorization remains outside the current Session C core.

### Gate E — Test evidence

Inspect the relevant tests beside the implementation they verify.

Classify each result as:

- **contract/software evidence** — the defined behavior is exercised by tests;
- **empirical evidence** — behavior has been measured under a controlled experimental protocol;
- **independent evidence** — the result has been reproduced or reviewed outside the original implementation context.

Do not merge these evidence classes.

### Gate F — CI and packaging

Inspect:

- `pyproject.toml`
- `.github/workflows/ci.yml`

Confirm:

- supported Python versions;
- package installation path;
- test command;
- CI trigger boundary;
- whether the documented local test path corresponds to CI.

The current CI matrix is Python 3.10, 3.11, 3.12, and 3.13.

### Gate G — Research/evidence boundary

Only after the software path is understood, inspect:

- `docs/ACRM_EVIDENCE_MATRIX.md`
- `docs/IMPLEMENTATION_GAP_MATRIX.md`
- relevant `research/` documents
- historical artifacts in `archive/` and `demos/`

Use these to answer:

> **What does the repository claim, and what evidence level is actually attached to that claim?**

Historical artifacts are provenance and research lineage unless the current implementation explicitly promotes their behavior.

## 4. Reviewer checklist

A reviewer should be able to answer **yes, no, or not established** for each item:

### Repository identity

- [ ] Current version is identifiable.
- [ ] Historical versions are distinguishable from the current baseline.
- [ ] The primary development branch is identifiable.
- [ ] Current implementation scope is documented.

### Architecture

- [ ] Responsibilities are separated by component.
- [ ] Observation is distinguishable from interpretation.
- [ ] Recommendation is distinguishable from execution.
- [ ] Runtime mutation boundaries are explicit.
- [ ] Future capabilities are not presented as current implementation.

### Contracts

- [ ] Core state contracts are inspectable.
- [ ] Inputs, outputs, invariants, and non-responsibilities are documented.
- [ ] Invalid state is handled explicitly.
- [ ] Component boundaries can be tested independently.

### Implementation

- [ ] Claimed current capabilities have corresponding source code.
- [ ] Research/demo artifacts are distinguishable from normative runtime code.
- [ ] Evolving components are explicitly marked as evolving.

### Verification

- [ ] Unit/contract tests exist for the defined behavior.
- [ ] Relevant edge cases are covered.
- [ ] CI executes the documented test suite.
- [ ] Local reproduction instructions are available.
- [ ] Software-test evidence is separated from empirical evidence.

### Evidence discipline

- [ ] Research hypotheses are not presented as established facts.
- [ ] Configurable thresholds are not presented as universal validation.
- [ ] Historical demonstrations are not treated as current runtime proof.
- [ ] Independent reproduction is identified separately from repository tests.

## 5. Review finding format

For each significant finding, use:

```text
Component:
Responsibility:
Current maturity:
Implementation evidence:
Test evidence:
Observed behavior:
Claim being evaluated:
Match / mismatch:
Severity:
Required action:
Evidence needed for promotion:
```

Use **mismatch** only when implementation materially differs from the responsibility claimed at the current maturity level.

Use **evolving limitation** when the behavior is explicitly provisional and consistent with the documented checkpoint.

## 6. Maturity vocabulary

| Status | Meaning |
|---|---|
| Implemented | Executable code or a defined runtime contract exists. |
| Tested | Automated tests verify the defined software behavior. |
| Evolving | Implemented and inspectable, but still under refinement. |
| Specified | Architecture/contract is defined without equivalent current implementation. |
| Empirical | Requires controlled measurement. |
| Independent | Requires external reproduction or review. |
| Future | Explicitly outside the current runtime baseline. |

## 7. Stop conditions

A reviewer should stop making stronger claims when the available evidence stops.

Examples:

```text
Unit test
  ≠
Scientific validation

Prototype
  ≠
Generalized capability

Architecture
  ≠
Implementation

Benchmark protocol
  ≠
Benchmark result

Repository test
  ≠
Independent reproduction
```

These are not disclaimers added after the fact; they are part of the repository's engineering review model.

## 8. Definition of a reviewable component

For the declared engineering scope, a component is reviewable when the reviewer can trace:

```text
Responsibility
    ↓
Contract
    ↓
Implementation
    ↓
Tests
    ↓
CI / reproduction
    ↓
Known limitations
    ↓
Evidence classification
```

If one of these links is missing, the gap should be recorded explicitly rather than filled by inference.

## 9. Final review principle

> **Review the repository from the outside in: establish scope, reproduce the software, inspect contracts, trace implementation, verify tests and CI, then evaluate research evidence. Do not infer a stronger claim than the evidence supports.**
