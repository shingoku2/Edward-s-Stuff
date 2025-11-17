"""
Gaming AI Assistant
A real-time AI companion for gamers
"""

__version__ = "1.0.0"
__author__ = "Gaming AI Assistant Team"
__description__ = "An intelligent gaming companion that detects games and provides AI-powered assistance"

# Ensure the package directory itself is on sys.path so that legacy absolute
# imports (e.g., ``import config``) continue to work even when importing the
# package via ``src.*``. This mirrors the runtime behavior in main.py where the
# ``src`` directory is explicitly added to sys.path.
import sys as _sys
from pathlib import Path as _Path

_SRC_DIR = str(_Path(__file__).resolve().parent)
if _SRC_DIR not in _sys.path:
    _sys.path.insert(0, _SRC_DIR)

from .game_detector import GameDetector
from .ai_assistant import AIAssistant
from .config import Config

__all__ = [
    'GameDetector',
    'AIAssistant',
    'Config',
]
