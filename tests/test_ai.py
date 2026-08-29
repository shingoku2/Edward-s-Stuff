from unittest.mock import MagicMock

import pytest

import src.ai_assistant as ai_assistant
from src.ai_router import AIRouter
from src.ai_assistant import AIAssistant
from src.providers import ProviderError, ProviderConnectionError


class StubConfig:
    def __init__(self, keys, ai_provider="ollama"):
        self.ai_provider = ai_provider
        self.ollama_host = "http://localhost:11434"
        self.ollama_model = "llama3"
        self.ai_api_key = None
        self.ai_base_url = None
        self.ai_model = None

    def get_effective_provider(self):
        return "ollama"

    def get_ai_config(self):
        return {
            "AI_PROVIDER": self.ai_provider,
            "OLLAMA_BASE_URL": self.ollama_host,
            "OLLAMA_MODEL": self.ollama_model,
            "AI_API_KEY": None,
            "AI_BASE_URL": None,
            "AI_MODEL": None
        }


def _fake_provider(name):
    provider = MagicMock()
    provider.name = name
    provider.is_configured.return_value = True
    provider.chat.return_value = {"content": f"{name}-ok"}
    provider.test_connection.return_value = MagicMock(
        is_healthy=True, message="ok", error_type=None, details={}
    )
    return provider


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
    monkey_cfg = config_provider or StubConfig({})
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
    
    mock_provider = MagicMock()
    mock_provider.generate_response.return_value = "response"
    monkeypatch.setattr(ai_assistant, "get_provider", lambda config: mock_provider)
    monkeypatch.setattr(ai_assistant, "get_knowledge_integration", knowledge_factory)

    assistant = AIAssistant(provider="ollama", config=cfg)
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
    
    mock_provider = MagicMock()
    monkeypatch.setattr(ai_assistant, "get_provider", lambda config: mock_provider)
    monkeypatch.setattr(ai_assistant, "get_knowledge_integration", knowledge_factory)

    assistant = AIAssistant(provider="ollama", config=cfg)
    result = assistant.ask_question("")
    assert result == "Please provide a question."


@pytest.mark.unit
def test_aiassistant_formats_provider_errors(monkeypatch):
    cfg, _, knowledge_factory = _assistant()
    
    # Mock provider instance that raises error
    mock_provider = MagicMock()
    mock_provider.generate_response.side_effect = ProviderError("Ollama error")
    
    # Patch get_provider to return our mock
    monkeypatch.setattr(ai_assistant, "get_provider", lambda config: mock_provider)
    monkeypatch.setattr(ai_assistant, "get_knowledge_integration", knowledge_factory)

    assistant = AIAssistant(provider="ollama", config=cfg)
    assistant.current_game = {"name": "Test Game"}

    message = assistant.ask_question("Any tips?")
    assert "Ollama error" in message
