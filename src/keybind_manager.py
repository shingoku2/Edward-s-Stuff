"""
Keybind Manager Module
Handles keybind registration, conflict detection, and global hotkey listening
"""

import logging
from typing import Dict, Callable, Optional, Set, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode, HotKey
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    keyboard = None
    Key = None
    KeyCode = None
    HotKey = None

logger = logging.getLogger(__name__)


class KeybindAction(Enum):
    """Predefined keybind actions"""
    TOGGLE_OVERLAY = "toggle_overlay"
    TOGGLE_AI_ASSISTANT = "toggle_ai_assistant"
    START_RECORDING = "start_recording"
    STOP_RECORDING = "stop_recording"
    RUN_MACRO = "run_macro"
    OPEN_SETTINGS = "open_settings"
    SHOW_TIPS = "show_tips"
    SHOW_OVERVIEW = "show_overview"
    CLEAR_CHAT = "clear_chat"
    FOCUS_INPUT = "focus_input"
    MINIMIZE_APP = "minimize_app"
    CLOSE_OVERLAY = "close_overlay"


@dataclass
class Keybind:
    """Represents a keybind configuration"""
    action: str  # Action name or KeybindAction enum value
    keys: str  # Key combination string (e.g., "ctrl+shift+g")
    description: str  # Human-readable description
    enabled: bool = True
    system_wide: bool = False  # Whether this works outside the app

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'Keybind':
        """Create Keybind from dictionary"""
        return Keybind(**data)


class KeybindManager:
    """
    Manages keyboard shortcuts and global hotkeys

    Features:
    - Register/unregister keybinds
    - Conflict detection
    - Global hotkey listening (system-wide)
    - Platform-friendly key parsing
    """

    def __init__(self):
        """Initialize the keybind manager"""
        self.keybinds: Dict[str, Keybind] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.listener: Optional[keyboard.Listener] = None
        self.active_hotkeys: Dict[str, HotKey] = {}
        self.currently_pressed: Set = set()

        if not PYNPUT_AVAILABLE:
            logger.warning("pynput not available - global hotkeys will not work")

    def register_keybind(self, keybind: Keybind, callback: Callable, override: bool = False) -> bool:
        """
        Register a keybind with a callback function

        Args:
            keybind: Keybind configuration
            callback: Function to call when keybind is pressed
            override: If True, override existing keybind (default: False)

        Returns:
            True if successful, False if conflict exists and override=False
        """
        # Check for conflicts
        if not override and self.has_conflict(keybind.keys, keybind.action):
            logger.warning(f"Keybind conflict: {keybind.keys} already assigned")
            return False

        # Unregister old keybind if it exists
        if keybind.action in self.keybinds:
            self.unregister_keybind(keybind.action)

        # Store keybind and callback
        self.keybinds[keybind.action] = keybind
        self.callbacks[keybind.action] = callback

        # Register hotkey if system-wide
        if keybind.system_wide and keybind.enabled:
            self._register_hotkey(keybind.action, keybind.keys)

        logger.info(f"Registered keybind: {keybind.action} -> {keybind.keys}")
        return True

    def unregister_keybind(self, action: str) -> bool:
        """
        Unregister a keybind

        Args:
            action: Action name to unregister

        Returns:
            True if successful, False if action not found
        """
        if action not in self.keybinds:
            return False

        # Unregister hotkey if it was system-wide
        if action in self.active_hotkeys:
            self._unregister_hotkey(action)

        # Remove keybind and callback
        del self.keybinds[action]
        if action in self.callbacks:
            del self.callbacks[action]

        logger.info(f"Unregistered keybind: {action}")
        return True

    def has_conflict(self, keys: str, exclude_action: Optional[str] = None) -> bool:
        """
        Check if a key combination is already assigned

        Args:
            keys: Key combination string
            exclude_action: Action to exclude from conflict check

        Returns:
            True if conflict exists, False otherwise
        """
        normalized_keys = self._normalize_keys(keys)

        for action, keybind in self.keybinds.items():
            if action == exclude_action:
                continue
            if self._normalize_keys(keybind.keys) == normalized_keys:
                return True

        return False

    def get_conflicts(self, keys: str, exclude_action: Optional[str] = None) -> List[Keybind]:
        """
        Get all keybinds that conflict with the given keys

        Args:
            keys: Key combination string
            exclude_action: Action to exclude from conflict check

        Returns:
            List of conflicting Keybind objects
        """
        conflicts = []
        normalized_keys = self._normalize_keys(keys)

        for action, keybind in self.keybinds.items():
            if action == exclude_action:
                continue
            if self._normalize_keys(keybind.keys) == normalized_keys:
                conflicts.append(keybind)

        return conflicts

    def start_listening(self) -> bool:
        """
        Start listening for global hotkeys

        Returns:
            True if successful, False if pynput not available
        """
        if not PYNPUT_AVAILABLE:
            logger.warning("Cannot start listening - pynput not available")
            return False

        if self.listener is not None and self.listener.is_alive():
            logger.warning("Listener already running")
            return True

        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            logger.info("Started global hotkey listener")
            return True
        except Exception as e:
            logger.error(f"Failed to start listener: {e}")
            return False

    def stop_listening(self):
        """Stop listening for global hotkeys"""
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
            logger.info("Stopped global hotkey listener")

    def _register_hotkey(self, action: str, keys: str):
        """Register a system-wide hotkey"""
        if not PYNPUT_AVAILABLE:
            return

        try:
            # Parse key combination
            key_combo = self._parse_keys(keys)

            # Create hotkey
            def on_activate():
                self._trigger_action(action)

            hotkey = HotKey(key_combo, on_activate)
            self.active_hotkeys[action] = hotkey

            logger.debug(f"Registered hotkey: {action} -> {keys}")
        except Exception as e:
            logger.error(f"Failed to register hotkey {action}: {e}")

    def _unregister_hotkey(self, action: str):
        """Unregister a system-wide hotkey"""
        if action in self.active_hotkeys:
            del self.active_hotkeys[action]
            logger.debug(f"Unregistered hotkey: {action}")

    def _on_press(self, key):
        """Handle key press events"""
        self.currently_pressed.add(key)

        # Check all active hotkeys
        for action, hotkey in self.active_hotkeys.items():
            hotkey.press(key)

    def _on_release(self, key):
        """Handle key release events"""
        if key in self.currently_pressed:
            self.currently_pressed.remove(key)

        # Check all active hotkeys
        for action, hotkey in self.active_hotkeys.items():
            hotkey.release(key)

    def _trigger_action(self, action: str):
        """Trigger a keybind action"""
        if action in self.callbacks and action in self.keybinds:
            keybind = self.keybinds[action]
            if keybind.enabled:
                logger.info(f"Triggering keybind action: {action}")
                try:
                    self.callbacks[action]()
                except Exception as e:
                    logger.error(f"Error executing keybind callback {action}: {e}")

    def _parse_keys(self, keys: str) -> Set:
        """
        Parse key combination string into pynput key set

        Args:
            keys: Key combination string (e.g., "ctrl+shift+g")

        Returns:
            Set of pynput Key/KeyCode objects
        """
        if not PYNPUT_AVAILABLE:
            return set()

        key_set = set()
        parts = keys.lower().split('+')

        for part in parts:
            part = part.strip()

            # Map common key names
            key_map = {
                'ctrl': Key.ctrl_l,
                'control': Key.ctrl_l,
                'shift': Key.shift_l,
                'alt': Key.alt_l,
                'win': Key.cmd,
                'cmd': Key.cmd,
                'super': Key.cmd,
                'tab': Key.tab,
                'esc': Key.esc,
                'escape': Key.esc,
                'enter': Key.enter,
                'return': Key.enter,
                'space': Key.space,
                'backspace': Key.backspace,
                'delete': Key.delete,
                'up': Key.up,
                'down': Key.down,
                'left': Key.left,
                'right': Key.right,
                'home': Key.home,
                'end': Key.end,
                'pageup': Key.page_up,
                'pagedown': Key.page_down,
                'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
                'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
                'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
            }

            if part in key_map:
                key_set.add(key_map[part])
            elif len(part) == 1:
                # Single character key
                key_set.add(KeyCode.from_char(part))
            else:
                logger.warning(f"Unknown key: {part}")

        return key_set

    def _normalize_keys(self, keys: str) -> str:
        """
        Normalize key combination string for comparison

        Args:
            keys: Key combination string

        Returns:
            Normalized string (lowercase, sorted)
        """
        parts = [p.strip().lower() for p in keys.split('+')]

        # Normalize key names
        normalize_map = {
            'control': 'ctrl',
            'command': 'cmd',
            'super': 'cmd',
            'windows': 'win',
            'return': 'enter',
            'escape': 'esc',
        }

        parts = [normalize_map.get(p, p) for p in parts]
        parts.sort()

        return '+'.join(parts)

    def get_all_keybinds(self) -> List[Keybind]:
        """Get all registered keybinds"""
        return list(self.keybinds.values())

    def get_keybind(self, action: str) -> Optional[Keybind]:
        """Get keybind by action name"""
        return self.keybinds.get(action)

    def validate_keys(self, keys: str) -> Tuple[bool, str]:
        """
        Validate key combination string

        Args:
            keys: Key combination string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not keys or not keys.strip():
            return False, "Key combination cannot be empty"

        parts = keys.lower().split('+')

        if len(parts) < 1:
            return False, "Key combination must have at least one key"

        if len(parts) > 4:
            return False, "Key combination cannot have more than 4 keys"

        # Check for valid keys
        valid_modifiers = {'ctrl', 'control', 'shift', 'alt', 'win', 'cmd', 'super'}
        valid_special = {'tab', 'esc', 'escape', 'enter', 'return', 'space',
                        'backspace', 'delete', 'up', 'down', 'left', 'right',
                        'home', 'end', 'pageup', 'pagedown'}
        valid_function = {f'f{i}' for i in range(1, 13)}

        has_non_modifier = False

        for part in parts:
            part = part.strip()

            if part in valid_modifiers:
                continue
            elif part in valid_special or part in valid_function:
                has_non_modifier = True
            elif len(part) == 1 and part.isalnum():
                has_non_modifier = True
            else:
                return False, f"Invalid key: {part}"

        if not has_non_modifier:
            return False, "Key combination must include at least one non-modifier key"

        return True, ""

    def save_to_dict(self) -> dict:
        """Save all keybinds to dictionary for JSON serialization"""
        return {
            action: keybind.to_dict()
            for action, keybind in self.keybinds.items()
        }

    def load_from_dict(self, data: dict):
        """Load keybinds from dictionary"""
        for action, keybind_data in data.items():
            try:
                keybind = Keybind.from_dict(keybind_data)
                # Note: callback must be registered separately
                self.keybinds[action] = keybind
            except Exception as e:
                logger.error(f"Failed to load keybind {action}: {e}")


# Default keybinds
DEFAULT_KEYBINDS = [
    Keybind(
        action=KeybindAction.TOGGLE_OVERLAY.value,
        keys="ctrl+shift+g",
        description="Toggle in-game overlay visibility",
        enabled=True,
        system_wide=True
    ),
    Keybind(
        action=KeybindAction.OPEN_SETTINGS.value,
        keys="ctrl+shift+s",
        description="Open settings dialog",
        enabled=True,
        system_wide=False
    ),
    Keybind(
        action=KeybindAction.CLEAR_CHAT.value,
        keys="ctrl+shift+x",
        description="Clear chat history",
        enabled=True,
        system_wide=False
    ),
    Keybind(
        action=KeybindAction.FOCUS_INPUT.value,
        keys="ctrl+shift+f",
        description="Focus chat input field",
        enabled=True,
        system_wide=False
    ),
]
