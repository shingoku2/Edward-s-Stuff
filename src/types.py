"""
Type definitions for better code clarity
"""

from typing import Protocol, TypedDict, List, Dict, Any, Optional, Union
from enum import Enum


class GameInfo(TypedDict):
    """Game information structure"""

    name: str
    exe: str
    process_name: str
    pid: int
    path: str


class ApiKeyStatus(TypedDict):
    """API key status information"""

    provider: str
    present: bool
    valid: bool
    error: Optional[str]


class ConversationMessage(TypedDict):
    """Chat message structure"""

    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float


class MacroStepType(Enum):
    """Types of macro steps"""

    KEY_PRESS = "key_press"
    KEY_HOLD = "key_hold"
    KEY_RELEASE = "key_release"
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    MOUSE_SCROLL = "mouse_scroll"
    DELAY = "delay"
    TEXT_TYPE = "text_type"


class OverlayMode(Enum):
    """Overlay display modes"""

    COMPACT = "compact"
    FULL = "full"


# Protocol definitions for better interface typing
class GameDetectorProtocol(Protocol):
    """Protocol for game detector interface"""

    def detect_running_game(self) -> Optional[GameInfo]:
        ...

    def get_running_games(self) -> List[GameInfo]:
        ...

    def is_game_running(self, game_name: str) -> bool:
        ...


class AIAssistantProtocol(Protocol):
    """Protocol for AI assistant interface"""

    provider: str

    def ask_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        ...

    def set_current_game(self, game: Optional[GameInfo]) -> None:
        ...
