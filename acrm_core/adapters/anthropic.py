"""Small stdlib-only adapter for Anthropic's Messages API."""

import json
from urllib.request import Request, urlopen

from .base import ChatRequest, ChatResponse


class AnthropicAdapter:
    def __init__(self, base_url: str = "https://api.anthropic.com", api_key: str | None = None, timeout: float = 60.0):
        if not api_key:
            raise ValueError("api_key is required")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def complete(self, request: ChatRequest) -> ChatResponse:
        system = "\n".join(m["content"] for m in request.messages if m.get("role") == "system")
        messages = [m for m in request.messages if m.get("role") != "system"]
        payload = {"model": request.model, "messages": messages, "max_tokens": request.max_tokens or 1024}
        if system:
            payload["system"] = system
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        req = Request(
            f"{self.base_url}/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        with urlopen(req, timeout=self.timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
        text = "".join(block.get("text", "") for block in raw.get("content", []) if block.get("type") == "text")
        return ChatResponse(text=text, model=raw.get("model", request.model), provider="anthropic", raw=raw)
