from unittest.mock import MagicMock

import pytest

import ai_router
from ai_router import AIRouter
import ai_assistant
from ai_assistant import AIAssistant
from providers import ProviderAuthError, ProviderRateLimitError


class StubConfig:
    def __init__(self, keys, ai_provider="anthropic"):
        self.ai_provider = ai_provider
        self._keys = dict(keys)

    def get_api_key(self, provider_name):
        return self._keys.get(provider_name)

    def get_effective_provider(self):
        if self._keys.get(self.ai_provider):
            return self.ai_provider
        for provider in ["anthropic", "openai", "gemini"]:
            if self._keys.get(provider):
                return provider
        return self.ai_provider

    def set_api_key(self, provider, api_key):
        self._keys[provider] = api_key

    def clear_api_key(self, provider):
        self._keys.pop(provider, None)

    def has_provider_key(self, provider=None):
        target = provider or self.ai_provider
        return bool(self._keys.get(target))


def _fake_provider(name):
    provider = MagicMock()
    provider.name = name
    provider.is_configured.return_value = True
    provider.chat.return_value = {"content": f"{name}-ok"}
    provider.test_connection.return_value = MagicMock(
        is_healthy=True, message="ok", error_type=None, details={}
    )
    return provider


@pytest.mark.unit
def test_airouter_falls_back_to_available_provider(monkeypatch):
    cfg = StubConfig({"openai": "key-openai"}, ai_provider="anthropic")

    def fake_create(provider_name, api_key=None):
        return _fake_provider(provider_name)

    monkeypatch.setattr(ai_router, "create_provider", fake_create)

    router = AIRouter(config=cfg)
    provider = router.get_default_provider()

    assert provider.name == "openai"
    assert router.chat([{"role": "user", "content": "hi"}])["content"] == "openai-ok"


@pytest.mark.unit
def test_airouter_propagates_rate_limit(monkeypatch):
    cfg = StubConfig({"anthropic": "key-anthropic"}, ai_provider="anthropic")
    router = AIRouter(config=cfg)

    limited_provider = _fake_provider("anthropic")
    limited_provider.chat.side_effect = ProviderRateLimitError("slow down")
    router._providers = {"anthropic": limited_provider}

    with pytest.raises(ProviderRateLimitError):
        router.chat([{"role": "user", "content": "hi"}], provider="anthropic")


@pytest.mark.unit
def test_airouter_requires_configured_provider(monkeypatch):
    cfg = StubConfig({})
    router = AIRouter(config=cfg)
    router._providers = {}

    with pytest.raises(ProviderAuthError):
        router.chat([{"role": "user", "content": "hi"}], provider="openai")


class DummyKnowledgeIntegration:
    def should_use_knowledge_packs(self, game_profile_id, extra_settings=None):
        return False

    def get_knowledge_context(self, game_profile_id, question, extra_settings=None):
        return None

    def log_conversation(self, game_profile_id, question, answer):
        pass


class StubRouter:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def chat(self, messages, **kwargs):
        self.calls.append(messages)
        if self.error:
            raise self.error
        return {"content": self.response or "ok"}


def _assistant(config_provider=None, router=None, knowledge_integration=None):
    monkey_cfg = config_provider or type("Cfg", (), {"ai_provider": "anthropic"})()
    monkey_router = router or StubRouter(response="pong")
    monkey_knowledge = knowledge_integration or DummyKnowledgeIntegration()

    def router_factory(cfg=None):
        return monkey_router

    def knowledge_factory():
        return monkey_knowledge

    return monkey_cfg, router_factory, knowledge_factory


@pytest.mark.unit
def test_aiassistant_trims_conversation_history(monkeypatch):
    cfg, router_factory, knowledge_factory = _assistant()
    monkeypatch.setattr(ai_assistant, "get_router", router_factory)
    monkeypatch.setattr(ai_assistant, "get_knowledge_integration", knowledge_factory)

    assistant = AIAssistant(provider="anthropic", config=cfg)
    assistant.current_game = {"name": "Test Game"}

    with assistant._history_lock:
        assistant.conversation_history = [
            {"role": "system", "content": f"sys-{idx}"} for idx in range(5)
        ]
        assistant.conversation_history += [
            {"role": "user", "content": f"q{idx}"} for idx in range(25)
        ]

    assistant._trim_conversation_history()
    assert len(assistant.conversation_history) == assistant.MAX_CONVERSATION_MESSAGES
    assert (
        len([m for m in assistant.conversation_history if m["role"] == "system"]) <= 3
    )


@pytest.mark.unit
def test_aiassistant_handles_empty_question(monkeypatch):
    cfg, router_factory, knowledge_factory = _assistant()
    monkeypatch.setattr(ai_assistant, "get_router", router_factory)
    monkeypatch.setattr(ai_assistant, "get_knowledge_integration", knowledge_factory)

    assistant = AIAssistant(provider="anthropic", config=cfg)
    result = assistant.ask_question("")
    assert result == "Please provide a question."


@pytest.mark.unit
def test_aiassistant_formats_provider_errors(monkeypatch):
    cfg, _, knowledge_factory = _assistant()
    failing_router = StubRouter(error=ProviderRateLimitError("slow"))

    monkeypatch.setattr(ai_assistant, "get_router", lambda cfg=None: failing_router)
    monkeypatch.setattr(ai_assistant, "get_knowledge_integration", knowledge_factory)

    assistant = AIAssistant(provider="anthropic", config=cfg)
    assistant.current_game = {"name": "Test Game"}

    message = assistant.ask_question("Any tips?")
    assert "Rate Limit" in message
