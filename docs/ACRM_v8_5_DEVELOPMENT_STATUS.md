# ACRM v8.5 Development Status

**Status:** Pre-implementation baseline  
**Target:** ACRM-CORE v8.5  
**Branch:** `test/ssh-write-access`  
**Date:** 2026-08-14

---

## 1. Purpose

This document records the development state of ACRM v8.5 before implementation begins.

It is intended to provide an open-source development traceability record showing:

- which source specifications have been identified;
- which architectural decisions have been established;
- what has been verified at the repository and development-process level;
- what remains to be implemented;
- what has **not** yet been experimentally validated.

This document is **not** a claim of experimental validation, benchmark completion, production readiness, or scientific proof.

---

## 2. Source Specifications Identified

The current ACRM v8.5 implementation plan is based on the following project artifacts:

### ACRM-EVAL v1.1

System-level benchmark and evaluation specification defining the primary runtime verification requirements for ACRM.

### ACRM-BRF v7

Behavioral Runtime Field foundation providing the mathematical, field-state, and failure-mode foundation for the next ACRM implementation stage.

### ACRM Failure Mode Taxonomy v7

Diagnostic taxonomy defining failure modes, observable signals, systemic effects, and causal propagation concepts.

### ACRM Unified Evolution Roadmap

Architecture and migration roadmap defining the intended evolution toward ACRM-CORE v8.5.

### ACRM Ontology

Terminology and conceptual constraints for Field, metrics, governance, alarm semantics, and related ACRM concepts.

---

## 3. Architecture Decision

ACRM-CORE v8.5 is being developed as the implementation layer that unifies the system-level specification and the behavioral-runtime mathematical foundation:

```text
ACRM-EVAL v1.1  +  ACRM-BRF v7
             ↓
       ACRM-CORE v8.
