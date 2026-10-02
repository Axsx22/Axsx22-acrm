"""Stable, provider-neutral boundary between ACRM and an LLM provider."""

from dataclasses import dataclass, field
from typing import Mapping, Protocol, Sequence


@dataclass(frozen=True, slots=True)
class ChatRequest:
    messages: Sequence[Mapping[str, str]]
    model: str
    temperature: float = 0.0
    max_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class ChatResponse:
    text: str
    model: str
    provider: str
    raw: Mapping[str, object] = field(default_factory=dict)


class ProviderAdapter(Protocol):
    """Minimal synchronous provider contract; no ACRM inference is implied."""

    def complete(self, request: ChatRequest) -> ChatResponse:
        ...
