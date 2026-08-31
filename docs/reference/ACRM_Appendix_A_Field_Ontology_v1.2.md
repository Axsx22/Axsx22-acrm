# Appendix A — Field Ontology
## A Formal Ontology of Interaction for the ACRM Architecture

**Author:** Ali Farahani  
**Version:** 1.2  
**Date:** 2026-08-04  
**Status:** Canonical Appendix to ACRM Whitepaper v1.1+

## A.1 Preamble

This appendix establishes the ontological foundation of ACRM. The term **Field** is used metaphorically for a bounded interactional domain; it does not imply a physical field theory.

## A.2 Interaction Field

> **An Interaction Field is the unique, ongoing domain of a specific interaction.**

It is the complete evolving phenomenon produced by sustained mutual influence. It is neither the user, nor the model, nor the transcript alone.

Not every interaction becomes an Interaction Field. The transition is gradual and depends on sustained mutual influence, feedback loops, coherence, and a recognizable trajectory.

### Core corollaries

1. The field is not an object; only observation records can be stored.
2. The field is not a container.
3. The field is emergent rather than a predefined process.
4. The field is irreducible to a transcript subset.
5. Each interaction has its own bounded field.
6. Field formation is threshold-dependent.

## A.3 Field Properties

Field Properties are measurable characteristics of an Interaction Field at a given moment, including stability `S(t)`, risk density `ρ(t)`, adaptive reasoning quality `ARQ(t)`, topical coherence, rhythmic density, convergence pressure, and cognitive-load distribution.

These are state variables rather than constituents of the field. They are apparatus-dependent, can be correlated, and have no privileged universal basis.

## A.4 ACRM's Relation to the Field

ACRM is a runtime observability layer that characterizes an Interaction Field without creating, modifying, or governing it. Its output is diagnostic characterization, not intervention.

### Two-stage model

**Stage 1 — Field Description:** observe the directional trajectory and establish local descriptive baselines when a direction remains stable.

**Stage 2 — Intent Alignment Comparison (optional):** only when a declared goal exists, compare the current trajectory with that intent. Without declared intent, a direction change is an event, not an anomaly.

### Operational invariants

- ACRM does not produce the field.
- ACRM does not control the field.
- ACRM does not modify output.
- An alert is a report, not a command.
- ACRM detects changes in direction; separate governance determines whether a change is an error.

## A.5 Architectural Implications

| Ontological commitment | Architectural consequence |
|---|---|
| Field is emergent | No fixed session-flow state machine is treated as the field itself |
| Field is irreducible | No dependency on model weights or internal activations |
| Field is threshold-dependent | Characterization follows sufficient interaction density |
| Properties are apparatus-dependent | Modular attach/detach architecture |
| Properties are not causal | Alert-only observation boundary |
| ACRM does not control | Self-Tune changes the apparatus, not the subject |
| ACRM does not modify output | Pass-through / non-interference invariant |
| Alert is report, not command | Separate alert/governance channel |

## A.6 Central Thesis

> **The field is not a representation of the interaction. The field is the interaction itself.**

> **A direction change is never an anomaly by itself. It becomes relevant only relative to the declared intent of the interaction.**

## A.7 Limitations

This is a working ontology, not a claim of metaphysical realism or a physical field theory. It makes no universality claim, provides no closed-form mathematics for the field itself, and does not specify a universal quantitative threshold for transition from interaction to Interaction Field.

*Repository reference copy derived from the supplied ACRM Appendix A v1.2 source.*
