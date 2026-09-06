"""Omnix public package API."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

__version__ = "3.0.0"
__author__ = "Omnix Team"
__description__ = "A privacy-first local AI gaming companion"

if TYPE_CHECKING:
    from .ai_assistant import AIAssistant
    from .config import Config
    from .game_detector import GameDetector

__all__ = [
    "GameDetector",
    "AIAssistant",
    "Config",
]

_PUBLIC_IMPORTS = {
    "AIAssistant": ("omnix.ai_assistant", "AIAssistant"),
    "Config": ("omnix.config", "Config"),
    "GameDetector": ("omnix.game_detector", "GameDetector"),
}


def __getattr__(name: str) -> Any:
    """Load heavyweight public classes only when requested."""
    try:
        module_name, attribute = _PUBLIC_IMPORTS[name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value
