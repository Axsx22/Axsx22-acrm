# Repository Branching and Lifecycle Policy

This repository uses a **main-first GitHub Flow** model.

## Canonical branch

- `main` is the only canonical integration branch.
- `main` represents the current documented and tested repository state.
- No permanent `develop` branch is used.
- Version branches are not maintained as parallel development lines.

## Branch classes

### 1. Active engineering branches

Use short-lived branches for work that is expected to return to `main`.

Recommended prefixes:

- `feat/<short-description>` — new capability
- `fix/<short-description>` — bug fix
- `refactor/<short-description>` — structural/code refactor
- `test/<short-description>` — testing or validation work
- `docs/<short-description>` — documentation-only work
- `research/<short-description>` — research or hypothesis work
- `audit/<short-description>` — security, architecture, or hardening work

Prefer one purpose per branch. Branches should normally be short-lived and should not become alternative permanent versions of the project.

### 2. Historical branches

Older development branches may be retained when they provide useful provenance for the evolution of ACRM.

Historical branches are **not alternative current implementations**.

Examples include:

- `acrm-v8.5`
- `acrm-v8.6`
- `session-c`
- `audit/session-c-hardening`

If a historical branch is no longer needed for provenance, it should be deleted rather than kept indefinitely.

### 3. Experimental/research branches

Research branches may remain independent when their work is intentionally exploratory and has not been accepted into `main`.

Examples:

- `research/unconscious-bridge-hypothesis`
- `session-c-adversarial-validation`
- `codex/calibration-invariants-contract`

A research branch does not imply that its implementation is part of the current ACRM baseline.

## Merge direction

The normal direction is:

```
active branch
     │
     ▼
  tests / CI
     │
     ▼
 pull request
     │
     ▼
   main
```

There should be no normal development flow from `main` into a permanent `develop` branch.

## Versioning policy

Version identifiers such as `v8.6` describe the software/research state; they are not intended to create permanently parallel branches.

Use:

- Git tags/releases for immutable version points;
- `main` for the current development baseline;
- short-lived work branches for changes;
- historical branches only when their provenance is useful.

## Branch hygiene

Before retaining a branch, ask:

1. Does it contain work not represented in `main`?
2. Is that work still active?
3. Is it intentionally experimental?
4. Does it provide meaningful historical provenance?
5. Could the same information be preserved by a tag, release, commit, or documentation?

Branches that answer "no" to all five should normally be deleted.

## Current repository classification

At the v8.6 baseline, the intended topology is:

```
                         ┌─ research/*
                         ├─ feat/*
                         ├─ fix/*
                         ├─ test/*
                         ├─ docs/*
                         └─ audit/*
                              │
                              ▼
                            main
                              │
                    current canonical state
```

The repository currently contains several legacy branches from the v8.5/v8.6 and Session C development history. They should be treated as historical or experimental until explicitly promoted into `main`.

## CI contract

CI targets `main` and pull requests targeting `main`.

A branch is not considered integrated merely because it exists on GitHub. Integration occurs only when its accepted changes are represented in `main` and pass the repository CI contract.

## Important distinction

Branch state is not evidence of research validity.

```
branch exists
    ≠
implementation accepted
    ≠
scientific claim validated
```

The same evidence boundary used throughout ACRM applies to Git history.
