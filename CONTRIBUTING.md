# Contributing to ACRM

ACRM is a research-oriented engineering project. Contributions should make the system more reviewable, reproducible, and explicit about evidence.

## Before changing code

1. Identify the component's responsibility.
2. State whether the change is core, research, demo, experiment, or documentation.
3. Define inputs, outputs, invariants, and failure boundaries.
4. Check whether the proposed behavior already exists elsewhere in the repository.

## For core changes

A core change should normally include:

- implementation;
- contract documentation;
- unit tests;
- edge-case tests;
- relevant integration tests;
- updated status/changelog information;
- explicit limitations.

## For research artifacts

Do not rewrite a research artifact to make it appear production-ready. Preserve provenance and document:

- what the artifact actually does;
- which values are simulated or heuristic;
- known mathematical or engineering assumptions;
- what remains unvalidated;
- how it could be promoted into a tested component.

## Tests

Run:

```bash
python -m pytest -q
```

A green test suite establishes compliance with implemented software contracts. It is not evidence of scientific validity.

## Pull requests

A useful PR description should answer:

- What changed?
- Why was it needed?
- What evidence supports the change?
- What tests were added or updated?
- What remains unvalidated?
- Does the change alter the public contract?

Avoid unsupported claims such as "proven," "production-ready," "causal," or "scientifically validated" unless the repository contains evidence that supports the exact claim.
