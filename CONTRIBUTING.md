# Contributing to ACRM

## Development model

ACRM follows a **main-first GitHub Flow** model.

- `main` is the canonical branch.
- Work is developed on short-lived purpose-specific branches.
- Changes return to `main` through review and CI.
- There is no permanent `develop` branch.
- Historical and research branches are not treated as current runtime baselines.

See [docs/BRANCHING.md](docs/BRANCHING.md) for the branch lifecycle policy.

## Before opening a change

1. Identify the architectural boundary affected by the change.
2. Keep Runtime and Session C responsibilities separate.
3. Preserve the distinction between observation, interpretation, decision, and action.
4. Add or update tests for changed software contracts.
5. Run the full test suite locally when practical.
6. Keep documentation synchronized with implemented behavior.
7. Do not silently promote research artifacts into the executable baseline.

## Branch naming

Use one of:

- `feat/<description>`
- `fix/<description>`
- `refactor/<description>`
- `test/<description>`
- `docs/<description>`
- `research/<description>`
- `audit/<description>`

Use lowercase, concise names, and one purpose per branch.

## Pull requests

A pull request should state:

- what changed;
- why it changed;
- which architectural boundary is affected;
- tests added or updated;
- CI/test status;
- whether the change is implementation, documentation, research, or experimental work.

Do not describe a software test result as empirical or scientific validation.

## Runtime and Session C

Changes involving Session C must preserve the observer boundary:

```
Runtime execution
      ↓
observable state/event
      ↓
Session C observation
      ↓
analysis / candidate / review
      ↓
recommendation
      ↓
external authorization
```

Session C must not silently become an automatic runtime mutation path.

## Merge standard

A change is ready for integration when:

- the intended contract is explicit;
- tests cover the relevant behavior;
- CI passes;
- documentation is consistent;
- the change does not unintentionally expand the architectural responsibility of the affected component.

## Research work

Research branches may contain hypotheses, experiments, or candidate implementations that are not ready for `main`.

When promoting research work:

1. identify the exact artifact being promoted;
2. separate hypothesis from implementation contract;
3. add tests for software behavior;
4. document what remains empirically unvalidated;
5. merge only the accepted implementation into `main`.
