# ACRM Engineering Governance

## Purpose

This document defines the engineering process used to move ACRM material from research artifacts toward maintainable runtime components.

The repository intentionally distinguishes **idea, prototype, software contract, implementation, empirical evidence, and scientific claim**. No layer is promoted merely because a later-looking artifact exists.

## Evidence ladder

```text
Research observation
      ↓
Research question
      ↓
Hypothesis / concept
      ↓
Architecture
      ↓
Prototype / demo
      ↓
Testable software contract
      ↓
Implementation
      ↓
Automated software tests
      ↓
Empirical evaluation
      ↓
Independent reproduction / review
```

A higher level must not be inferred from a lower one. In particular:

- a dashboard is not a production runtime;
- a passing unit test is not scientific validation;
- a mathematical analogy is not a mathematical proof;
- a benchmark target is not a benchmark result;
- a prototype observation is not a generalized claim.

## Change classification

Every substantial change should be classified as one of:

1. **Core** — normative runtime behavior with a stable contract.
2. **Research artifact** — executable or analytical exploration that is not yet normative.
3. **Demo** — presentation or interactive visualization, including simulated behavior.
4. **Experiment** — controlled evaluation intended to produce evidence.
5. **Documentation** — contracts, architecture, provenance, status, or review material.
6. **Roadmap** — proposed future work with no implementation claim.

## Promotion gate

A research component may be promoted into `acrm_core` only after all applicable items are satisfied:

- [ ] responsibility is explicitly defined;
- [ ] inputs and outputs are specified;
- [ ] invariants and assumptions are documented;
- [ ] failure modes are explicit;
- [ ] deterministic unit/contract tests exist;
- [ ] integration behavior is tested where applicable;
- [ ] numerical stability is considered where applicable;
- [ ] evidence level is recorded;
- [ ] provenance of the source artifact is retained;
- [ ] scientific claims are separated from software guarantees.

## Research-code handling

Historical or advanced prototype code should not be copied into the current core simply to make the repository appear more complete. Instead:

1. preserve the original artifact;
2. document what it actually implements;
3. identify unsupported assumptions;
4. extract contracts from the useful behavior;
5. implement the contract independently in the appropriate layer;
6. test it;
7. evaluate it empirically;
8. promote only when the evidence supports promotion.

## Review standard

For every major architecture change, reviewers should be able to answer:

- What problem does this solve?
- What exactly is implemented?
- What is simulated or illustrative?
- What assumptions does it make?
- What can make it fail?
- Which tests establish software correctness?
- Which experiments establish behavioral performance?
- Which claims remain hypotheses?
- What evidence would falsify the claim?

## Version discipline

Version labels must describe repository state, not imply maturity. Historical versions such as v6.x, v7.x, v7.9, or v8.x may remain visible as research provenance. The current core version is governed by the implementation and tests actually present in the repository.

## Definition of done

A component is considered engineering-complete for its declared scope when:

```text
Contract
  + Implementation
  + Tests
  + Documentation
  + CI
  + Known limitations
  = Reviewable component
```

Scientific validation is a separate milestone and must be reported separately.
