import pytest

from omnix.providers import LLMProvider


def test_llm_provider_is_abstract():
    """Verify that LLMProvider cannot be instantiated directly."""
    # Since LLMProvider is abstract, we can't check instantiation of the class itself directly
    # in the same way if it has abstract methods.
    # Instead, we try to define a subclass that doesn't implement the methods

    class IncompleteProvider(LLMProvider):
        pass

    with pytest.raises(TypeError):
        IncompleteProvider()


def test_llm_provider_contract():
    """Verify that a subclass implementing all methods can be instantiated."""

    class CompleteProvider(LLMProvider):
        def generate_response(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
            return "response"

        def health_check(self) -> bool:
            return True

    provider = CompleteProvider()
    assert provider.generate_response("sys", "user") == "response"
    assert provider.health_check() is True
