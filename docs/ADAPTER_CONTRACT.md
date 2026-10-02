# ACRM Provider Adapter Contract

## Purpose

This layer defines the transport boundary between ACRM and external LLM providers. It is deliberately separate from `FieldState`: adapters obtain model responses; they do not infer ACRM state, make governance decisions, or claim scientific validity.

## Contract

`ChatRequest` contains:

- `messages`: role/content mappings;
- `model`;
- `temperature`;
- optional `max_tokens`.

`ChatResponse` contains:

- normalized text;
- provider identifier;
- model identifier;
- provider-native raw response for traceability.

## Implementations

- `OpenAICompatibleAdapter`: HTTP `POST /v1/chat/completions`. This boundary is suitable for OpenAI-compatible servers, including vLLM deployments that expose that API shape.
- `AnthropicAdapter`: HTTP `POST /v1/messages` using the Anthropic Messages API shape.

The adapters use only the Python standard library. Credentials are supplied at runtime and are never stored by the package.

## Explicit non-claims

The adapter layer does **not** currently provide:

- Session C governance semantics;
- `BaselineValidator`, `FieldMeter`, `EnvelopeChecker`, `InterventionEngine`, `ReleaseBuilder`, or `AuditLogger`;
- automatic conversion of model output into `FieldState`;
- streaming, retries, rate-limit policy, tracing, or provider-specific advanced features;
- scientific or behavioral validation.

Those capabilities require their own contracts and tests before integration.
