# ACRM Session C — Architecture Contract (Draft)

Status: experimental branch; not a release contract.

## Purpose

Session C observes the running ACRM as a continuous system trajectory and prepares governed evolution before a limitation becomes a runtime failure.

Session C is not the runtime controller. It does not directly mutate, execute, or switch the active runtime.

## C-A — Neutral Observation

C-A records factual observations from the running system. It must not assign severity, score, judgment, cause, topic, promotion status, or intervention.

Observation units may reference a system/session sequence and a time window, but the observation layer remains descriptive.

The observation stream may contain pressure, ambiguity, missing capability, failure, and emerging-evolution signals. A failure is not required for an observation to exist.

## Trajectory

C-A observations are interpreted downstream as a temporally ordered trajectory. The trajectory is not a list of isolated messages: persistence, recurrence, co-occurrence, and change over time are properties of the accumulated evidence.

## Dynamic Envelope and Tolerance

C-B derives a field/system-relative operating envelope from observed trajectory evidence. Tolerance is a distance-to-limit concept, not a universal hard-coded error count.

A system may enter an approach/warning region while still functioning correctly. The purpose is early preparation, not post-failure repair.

A candidate-generation trigger therefore requires evidence that the current behavior is approaching or persistently occupying a limitation boundary; a fixed observation count alone is insufficient as the architectural trigger.

## Topic Engine

Topic is inferred in C-B from accumulated observations and their temporal/signal profile. It is not supplied as an unquestioned external label.

Topic inference may determine evaluator relevance, but must not modify observations, assert intent, decide promotion, generate code, or mutate runtime.

## C-B — Governed Evolution

C-B may, after an evidence threshold is reached:

1. formulate a candidate from recorded evidence;
2. isolate candidate generation from the active runtime;
3. test the candidate independently;
4. evaluate the candidate using the current system/field context;
5. collect topic-aware specialist votes weighted by reliability and relevance;
6. produce a retain/recommend-switch decision;
7. hand off to a separate controlled mechanism if a switch is recommended.

Passing tests does not imply promotion. Voting does not imply execution.

## Safety Boundaries

- C-A observation is not judgment.
- Topic inference is not a promotion decision.
- Candidate source is not runtime code.
- Test success is not promotion.
- A switch recommendation is not a runtime mutation.

## Open Research Boundary

The repository currently contains a constrained engineering implementation. This document describes the target architecture and must not be read as evidence that autonomous self-modification or empirical self-validation has already been achieved.
