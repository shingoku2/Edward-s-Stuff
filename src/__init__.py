"""
Gaming AI Assistant
A real-time AI companion for gamers
"""

__version__ = "1.0.0"
__author__ = "Gaming AI Assistant Team"
__description__ = "An intelligent gaming companion that detects games and provides AI-powered assistance"

from .game_detector import GameDetector
from .ai_assistant import AIAssistant
from .info_scraper import GameInfoScraper
from .config import Config

__all__ = [
    'GameDetector',
    'AIAssistant',
    'GameInfoScraper',
    'Config',
]
