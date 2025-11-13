"""
Overlay Modes Module
Defines compact and full panel modes for the in-game overlay
"""

from enum import Enum
from typing import Dict, Any


class OverlayMode(Enum):
    """Enumeration of overlay display modes"""
    COMPACT = "compact"
    FULL = "full"


class OverlayModeConfig:
    """
    Configuration and layout guidance for different overlay modes.
    """

    # Mode-specific settings
    MODES: Dict[str, Dict[str, Any]] = {
        "compact": {
            "display_name": "Compact",
            "description": "Single-line input with recent answer preview",
            "min_width": 300,
            "min_height": 80,
            "default_width": 500,
            "default_height": 120,
            "show_conversation_history": False,
            "show_model_selector": False,
            "show_system_prompt": False,
            "show_provider_selector": False,
            "input_rows": 1,
            "history_rows": 2,  # For preview of last response
            "icon": "📝",
        },
        "full": {
            "display_name": "Full Panel",
            "description": "Complete chat interface with full history",
            "min_width": 400,
            "min_height": 300,
            "default_width": 900,
            "default_height": 700,
            "show_conversation_history": True,
            "show_model_selector": True,
            "show_system_prompt": False,  # Hidden but can be toggled
            "show_provider_selector": True,
            "input_rows": 3,
            "history_rows": 15,  # Full conversation
            "icon": "💬",
        },
    }

    @classmethod
    def get_mode_config(cls, mode: str) -> Dict[str, Any]:
        """Get configuration for a specific mode"""
        return cls.MODES.get(mode, cls.MODES["compact"])

    @classmethod
    def get_display_name(cls, mode: str) -> str:
        """Get human-readable display name for mode"""
        config = cls.get_mode_config(mode)
        return config.get("display_name", mode)

    @classmethod
    def is_valid_mode(cls, mode: str) -> bool:
        """Check if a mode string is valid"""
        return mode in cls.MODES

    @classmethod
    def list_modes(cls) -> list:
        """List all available modes"""
        return list(cls.MODES.keys())

    @classmethod
    def get_default_dimensions(cls, mode: str) -> tuple:
        """Get default width and height for a mode as (width, height)"""
        config = cls.get_mode_config(mode)
        return (config.get("default_width"), config.get("default_height"))

    @classmethod
    def get_min_dimensions(cls, mode: str) -> tuple:
        """Get minimum width and height for a mode as (width, height)"""
        config = cls.get_mode_config(mode)
        return (config.get("min_width"), config.get("min_height"))

    @classmethod
    def should_show_conversation_history(cls, mode: str) -> bool:
        """Check if conversation history should be visible in this mode"""
        config = cls.get_mode_config(mode)
        return config.get("show_conversation_history", False)

    @classmethod
    def should_show_model_selector(cls, mode: str) -> bool:
        """Check if model selector should be visible in this mode"""
        config = cls.get_mode_config(mode)
        return config.get("show_model_selector", False)

    @classmethod
    def should_show_provider_selector(cls, mode: str) -> bool:
        """Check if provider selector should be visible in this mode"""
        config = cls.get_mode_config(mode)
        return config.get("show_provider_selector", False)

    @classmethod
    def get_input_rows(cls, mode: str) -> int:
        """Get number of rows for input text box"""
        config = cls.get_mode_config(mode)
        return config.get("input_rows", 1)

    @classmethod
    def get_history_rows(cls, mode: str) -> int:
        """Get number of rows for conversation history display"""
        config = cls.get_mode_config(mode)
        return config.get("history_rows", 2)

    @classmethod
    def get_icon(cls, mode: str) -> str:
        """Get emoji icon for mode"""
        config = cls.get_mode_config(mode)
        return config.get("icon", "")


class ModeTransitionHelper:
    """Helper for smooth transitions between overlay modes"""

    @staticmethod
    def calculate_new_size(
        current_width: int,
        current_height: int,
        from_mode: str,
        to_mode: str,
    ) -> tuple:
        """
        Calculate appropriate size when transitioning between modes.

        Args:
            current_width: Current window width
            current_height: Current window height
            from_mode: Current mode
            to_mode: Target mode

        Returns:
            (new_width, new_height) tuple
        """
        from_config = OverlayModeConfig.get_mode_config(from_mode)
        to_config = OverlayModeConfig.get_mode_config(to_mode)

        # If expanding, use the new default size
        if to_config.get("default_height", 0) > from_config.get("default_height", 0):
            return OverlayModeConfig.get_default_dimensions(to_mode)

        # If shrinking, use the new default size
        if to_config.get("default_height", 0) < from_config.get("default_height", 0):
            return OverlayModeConfig.get_default_dimensions(to_mode)

        # Same size category, keep current size but enforce minimums
        min_width, min_height = OverlayModeConfig.get_min_dimensions(to_mode)
        return (
            max(current_width, min_width),
            max(current_height, min_height),
        )

    @staticmethod
    def should_preserve_position(from_mode: str, to_mode: str) -> bool:
        """
        Determine if window position should be preserved during mode switch.

        Args:
            from_mode: Current mode
            to_mode: Target mode

        Returns:
            True to preserve position, False to allow repositioning
        """
        # Always preserve position unless expanding significantly
        return True

    @staticmethod
    def get_transition_message(from_mode: str, to_mode: str) -> str:
        """Get user-friendly message for mode transition"""
        if to_mode == "compact":
            return "Switched to compact mode (press 'E' or button to expand)"
        elif to_mode == "full":
            return "Switched to full panel mode (press 'C' or button to collapse)"
        return f"Switched to {to_mode} mode"
