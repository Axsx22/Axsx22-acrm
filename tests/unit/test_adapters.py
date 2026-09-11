import json

import pytest

from acrm_core.adapters import AnthropicAdapter, ChatRequest, OpenAICompatibleAdapter


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_openai_compatible_adapter(monkeypatch):
    seen = {}

    def fake_urlopen(req, timeout):
        seen["url"] = req.full_url
        seen["headers"] = dict(req.header_items())
        seen["body"] = json.loads(req.data.decode())
        return FakeResponse({"model": "test-model", "choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr("acrm_core.adapters.openai_compatible.urlopen", fake_urlopen)
    response = OpenAICompatibleAdapter("http://localhost:8000", "secret").complete(
        ChatRequest(messages=({"role": "user", "content": "hi"},), model="test-model", max_tokens=20)
    )
    assert response.text == "ok"
    assert response.provider == "openai-compatible"
    assert seen["url"].endswith("/v1/chat/completions")
    assert seen["body"]["max_tokens"] == 20


def test_anthropic_adapter(monkeypatch):
    seen = {}

    def fake_urlopen(req, timeout):
        seen["url"] = req.full_url
        seen["headers"] = dict(req.header_items())
        seen["body"] = json.loads(req.data.decode())
        return FakeResponse({"model": "claude-test", "content": [{"type": "text", "text": "ok"}]})

    monkeypatch.setattr("acrm_core.adapters.anthropic.urlopen", fake_urlopen)
    response = AnthropicAdapter(api_key="secret").complete(
        ChatRequest(
            messages=({"role": "system", "content": "system"}, {"role": "user", "content": "hi"}),
            model="claude-test",
        )
    )
    assert response.text == "ok"
    assert response.provider == "anthropic"
    assert seen["url"].endswith("/v1/messages")
    assert seen["body"]["system"] == "system"
    assert seen["headers"]["X-api-key"] == "secret"


def test_anthropic_requires_api_key():
    with pytest.raises(ValueError):
        AnthropicAdapter()
