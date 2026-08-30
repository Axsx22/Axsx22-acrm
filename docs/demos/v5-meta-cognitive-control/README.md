# ACRM v5.0 — Meta-Cognitive Control Architecture

## Purpose

This directory contains the **raw browser-executable source** of the ACRM v5.0 Meta-Cognitive Control Architecture demonstration supplied during development.

The demo is intentionally published as source rather than only as a screen recording or a fixed playback. Users can inspect the HTML/JavaScript, change `S`, `ρ`, and `Δ` manually, process inputs repeatedly, observe state/action changes, and optionally run a small sample sequence.

## Run

Open `acrm_v5_meta_cognitive_control.html` directly in a modern browser. No build step, package manager, server, or external CDN is required.

## Input model

The interactive controls expose three demonstration-level signals:

- `S`: semantic signal
- `ρ`: coherence signal
- `Δ`: deviation signal

The source updates an EMA baseline, derives a relative deviation signal, evaluates a small hypothesis registry, calculates demonstration governance/risk metrics, and selects a displayed policy state/action.

The browser API `window.ACRM_DEMO.processInput(S, rho, delta)` is also exposed for manual experimentation from the developer console.

## Important evidence boundary

This is a **research/demo artifact**, not a claim that the complete ACRM architecture or v8.5 core is implemented in this file. The decision logic is intentionally small and transparent so that users can inspect and experiment with it. The sample scenario is optional and is not the only execution path.

The normative implementation boundary remains the tested ACRM core documented elsewhere in the repository.
