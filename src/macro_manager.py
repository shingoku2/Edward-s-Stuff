"""
Macro Manager Module
Handles macro creation, editing, and execution for gaming automation
Supports keyboard/mouse input, delays with jitter, and AI-assisted macro generation
"""

import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class MacroStepType(Enum):
    """Types of macro steps for keyboard/mouse automation"""

    KEY_PRESS = "key_press"  # Press and release a key
    KEY_DOWN = "key_down"  # Press key without releasing
    KEY_UP = "key_up"  # Release a pressed key
    KEY_SEQUENCE = "key_sequence"  # Type a sequence of keys
    MOUSE_MOVE = "mouse_move"  # Move mouse to position
    MOUSE_CLICK = "mouse_click"  # Click mouse button
    MOUSE_SCROLL = "mouse_scroll"  # Scroll mouse wheel
    DELAY = "delay"  # Pause execution

    # Legacy UI actions (for backward compatibility)
    SHOW_TIPS = "show_tips"
    SHOW_OVERVIEW = "show_overview"
    CLEAR_CHAT = "clear_chat"
    SEND_MESSAGE = "send_message"
    TOGGLE_OVERLAY = "toggle_overlay"
    CLOSE_OVERLAY = "close_overlay"
    OPEN_SETTINGS = "open_settings"
    CUSTOM_COMMAND = "custom_command"


@dataclass
class MacroStep:
    """Represents a single step in a macro"""

    type: str  # MacroStepType enum value

    # Keyboard parameters
    key: Optional[str] = None  # Key name or combination (e.g., "a", "ctrl+shift+e")
    duration_ms: int = 0  # For key hold duration or delay duration

    # Mouse parameters
    button: Optional[str] = None  # "left", "right", "middle"
    x: Optional[int] = None  # Mouse X coordinate
    y: Optional[int] = None  # Mouse Y coordinate
    scroll_amount: int = 0  # Scroll wheel amount

    # General parameters
    meta: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
    delay_jitter_ms: int = 0  # Random delay jitter (0 to this value)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "type": self.type,
            "key": self.key,
            "duration_ms": self.duration_ms,
            "button": self.button,
            "x": self.x,
            "y": self.y,
            "scroll_amount": self.scroll_amount,
            "meta": self.meta,
            "delay_jitter_ms": self.delay_jitter_ms,
        }

    @staticmethod
    def from_dict(data: dict) -> "MacroStep":
        """Create MacroStep from dictionary"""
        return MacroStep(
            type=data["type"],
            key=data.get("key"),
            duration_ms=data.get("duration_ms", 0),
            button=data.get("button"),
            x=data.get("x"),
            y=data.get("y"),
            scroll_amount=data.get("scroll_amount", 0),
            meta=data.get("meta", {}),
            delay_jitter_ms=data.get("delay_jitter_ms", 0),
        )


# Legacy action type for backward compatibility
class MacroActionType(Enum):
    """Types of macro actions (legacy - use MacroStepType instead)"""

    SHOW_TIPS = "show_tips"
    SHOW_OVERVIEW = "show_overview"
    CLEAR_CHAT = "clear_chat"
    SEND_MESSAGE = "send_message"
    TOGGLE_OVERLAY = "toggle_overlay"
    CLOSE_OVERLAY = "close_overlay"
    OPEN_SETTINGS = "open_settings"
    WAIT = "wait"
    CUSTOM_COMMAND = "custom_command"


@dataclass
class MacroAction:
    """Represents a single action in a macro (legacy - use MacroStep instead)"""

    action_type: str  # MacroActionType enum value
    parameters: Dict[str, Any] = field(default_factory=dict)
    delay_after: int = 0  # Delay in milliseconds after executing this action

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "MacroAction":
        """Create MacroAction from dictionary"""
        return MacroAction(**data)


@dataclass
class Macro:
    """Represents a macro (sequence of steps for gaming automation)"""

    id: str
    name: str
    description: str
    steps: List[MacroStep] = field(default_factory=list)

    # Game profile association
    game_profile_id: Optional[str] = None  # None = global macro

    # Execution parameters
    repeat: int = 1  # Number of times to repeat macro
    randomize_delay: bool = False  # Add random jitter to delays
    delay_jitter_ms: int = 0  # Max random jitter in milliseconds
    # Optional per-macro safety overrides
    max_repeat: Optional[int] = None  # Optional per-macro maximum repeat override
    execution_timeout: Optional[int] = None  # Optional per-macro execution timeout (seconds)

    # Status
    enabled: bool = True
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    # Legacy support
    actions: List[MacroAction] = field(default_factory=list)  # For backward compatibility

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "game_profile_id": self.game_profile_id,
            "repeat": self.repeat,
            "randomize_delay": self.randomize_delay,
            "delay_jitter_ms": self.delay_jitter_ms,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            # Legacy
            "actions": [action.to_dict() for action in self.actions],
        }

    @staticmethod
    def from_dict(data: dict) -> "Macro":
        """Create Macro from dictionary"""
        # Support both new 'steps' and legacy 'actions' format
        steps = []
        if "steps" in data:
            steps = [MacroStep.from_dict(s) for s in data.get("steps", [])]

        actions = []
        if "actions" in data:
            actions = [MacroAction.from_dict(a) for a in data.get("actions", [])]

        return Macro(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            steps=steps,
            game_profile_id=data.get("game_profile_id"),
            repeat=data.get("repeat", 1),
            randomize_delay=data.get("randomize_delay", False),
            delay_jitter_ms=data.get("delay_jitter_ms", 0),
            enabled=data.get("enabled", True),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            actions=actions,
        )

    def add_step(self, step: MacroStep):
        """Add a step to the macro"""
        self.steps.append(step)
        self.updated_at = time.time()

    def remove_step(self, index: int) -> bool:
        """Remove a step by index"""
        if 0 <= index < len(self.steps):
            self.steps.pop(index)
            self.updated_at = time.time()
            return True
        return False

    def move_step(self, from_index: int, to_index: int) -> bool:
        """Move a step from one position to another"""
        if 0 <= from_index < len(self.steps) and 0 <= to_index < len(self.steps):
            step = self.steps.pop(from_index)
            self.steps.insert(to_index, step)
            self.updated_at = time.time()
            return True
        return False

    def get_total_duration(self) -> int:
        """Get total duration of macro execution in milliseconds"""
        total = 0
        for step in self.steps:
            if step.type == MacroStepType.DELAY.value:
                total += step.duration_ms
            elif (
                step.type == MacroStepType.KEY_DOWN.value
                or step.type == MacroStepType.KEY_PRESS.value
            ):
                if step.duration_ms > 0:
                    total += step.duration_ms
            # Add jitter
            if step.delay_jitter_ms > 0:
                total += step.delay_jitter_ms

        # Account for repetitions
        return total * self.repeat

    # Legacy methods for backward compatibility
    def add_action(self, action: MacroAction):
        """Add an action to the macro (legacy method)"""
        self.actions.append(action)
        self.updated_at = time.time()

    def remove_action(self, index: int) -> bool:
        """Remove an action by index (legacy method)"""
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
            self.updated_at = time.time()
            return True
        return False

    def move_action(self, from_index: int, to_index: int) -> bool:
        """Move an action from one position to another (legacy method)"""
        if 0 <= from_index < len(self.actions) and 0 <= to_index < len(self.actions):
            action = self.actions.pop(from_index)
            self.actions.insert(to_index, action)
            self.updated_at = time.time()
            return True
        return False


class MacroManager:
    """
    Manages macros and their execution

    Features:
    - Create/edit/delete/duplicate macros
    - Execute macros
    - Record macro sequences
    - Validate macro actions
    """

    def __init__(self):
        """Initialize the macro manager"""
        self.macros: Dict[str, Macro] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self.recording_macro: Optional[Macro] = None
        self.is_recording: bool = False

    def create_macro(self, name: str, description: str = "") -> Macro:
        """
        Create a new macro

        Args:
            name: Macro name
            description: Macro description

        Returns:
            Created Macro object
        """
        macro_id = str(uuid.uuid4())
        macro = Macro(id=macro_id, name=name, description=description)
        self.macros[macro_id] = macro
        logger.info(f"Created macro: {name} (ID: {macro_id})")
        return macro

    def duplicate_macro(self, macro_id: str) -> Optional[Macro]:
        """
        Duplicate an existing macro

        Args:
            macro_id: ID of macro to duplicate

        Returns:
            Duplicated Macro object or None if not found
        """
        if macro_id not in self.macros:
            logger.warning(f"Macro not found: {macro_id}")
            return None

        original = self.macros[macro_id]
        new_macro = Macro(
            id=str(uuid.uuid4()),
            name=f"{original.name} (Copy)",
            description=original.description,
            steps=[MacroStep.from_dict(s.to_dict()) for s in original.steps],
            game_profile_id=original.game_profile_id,
            repeat=original.repeat,
            randomize_delay=original.randomize_delay,
            delay_jitter_ms=original.delay_jitter_ms,
            enabled=original.enabled,
            actions=[MacroAction.from_dict(a.to_dict()) for a in original.actions],
        )
        self.macros[new_macro.id] = new_macro
        logger.info(f"Duplicated macro: {original.name} -> {new_macro.name}")
        return new_macro

    def delete_macro(self, macro_id: str) -> bool:
        """
        Delete a macro

        Args:
            macro_id: ID of macro to delete

        Returns:
            True if successful, False if not found
        """
        if macro_id in self.macros:
            macro_name = self.macros[macro_id].name
            del self.macros[macro_id]
            logger.info(f"Deleted macro: {macro_name} (ID: {macro_id})")
            return True
        return False

    def get_macro(self, macro_id: str) -> Optional[Macro]:
        """Get macro by ID"""
        return self.macros.get(macro_id)

    def get_all_macros(self) -> List[Macro]:
        """Get all macros"""
        return list(self.macros.values())

    def update_macro(
        self,
        macro_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        actions: Optional[List[MacroAction]] = None,
        enabled: Optional[bool] = None,
    ) -> bool:
        """
        Update macro properties

        Args:
            macro_id: ID of macro to update
            name: New name (optional)
            description: New description (optional)
            actions: New actions list (optional)
            enabled: New enabled state (optional)

        Returns:
            True if successful, False if not found
        """
        if macro_id not in self.macros:
            return False

        macro = self.macros[macro_id]

        if name is not None:
            macro.name = name
        if description is not None:
            macro.description = description
        if actions is not None:
            macro.actions = actions
        if enabled is not None:
            macro.enabled = enabled

        macro.modified_at = time.time()
        logger.info(f"Updated macro: {macro.name}")
        return True

    def register_action_handler(self, action_type: str, handler: Callable):
        """
        Register a handler for a macro action type

        Args:
            action_type: MacroActionType enum value
            handler: Function to call when executing this action
        """
        self.action_handlers[action_type] = handler
        logger.debug(f"Registered action handler: {action_type}")

    def execute_macro(self, macro_id: str) -> bool:
        """
        Execute a macro

        Args:
            macro_id: ID of macro to execute

        Returns:
            True if successful, False if not found or disabled
        """
        if macro_id not in self.macros:
            logger.warning(f"Macro not found: {macro_id}")
            return False

        macro = self.macros[macro_id]

        if not macro.enabled:
            logger.warning(f"Macro is disabled: {macro.name}")
            return False

        logger.info(f"Executing macro: {macro.name}")

        try:
            for i, action in enumerate(macro.actions):
                logger.debug(f"Executing action {i+1}/{len(macro.actions)}: {action.action_type}")

                # Execute action
                if action.action_type in self.action_handlers:
                    handler = self.action_handlers[action.action_type]
                    handler(**action.parameters)
                elif action.action_type == MacroActionType.WAIT.value:
                    duration = action.parameters.get("duration", 0)
                    time.sleep(duration / 1000.0)
                else:
                    logger.warning(f"No handler for action type: {action.action_type}")

                # Delay after action
                if action.delay_after > 0:
                    time.sleep(action.delay_after / 1000.0)

            logger.info(f"Macro execution completed: {macro.name}")
            return True

        except Exception as e:
            logger.error(f"Error executing macro {macro.name}: {e}")
            return False

    def start_recording(self, name: str, description: str = "") -> bool:
        """
        Start recording a new macro

        Args:
            name: Name for the macro being recorded
            description: Description for the macro

        Returns:
            True if recording started, False if already recording
        """
        if self.is_recording:
            logger.warning("Already recording a macro")
            return False

        self.recording_macro = self.create_macro(name, description)
        self.is_recording = True
        logger.info(f"Started recording macro: {name}")
        return True

    def record_action(self, action: MacroAction):
        """
        Record an action to the currently recording macro

        Args:
            action: MacroAction to record
        """
        if not self.is_recording or self.recording_macro is None:
            logger.warning("Not currently recording a macro")
            return

        self.recording_macro.add_action(action)
        logger.debug(f"Recorded action: {action.action_type}")

    def stop_recording(self) -> Optional[Macro]:
        """
        Stop recording the current macro

        Returns:
            The recorded Macro object or None if not recording
        """
        if not self.is_recording:
            logger.warning("Not currently recording a macro")
            return None

        macro = self.recording_macro
        self.is_recording = False
        self.recording_macro = None
        logger.info(f"Stopped recording macro: {macro.name} ({len(macro.actions)} actions)")
        return macro

    def cancel_recording(self):
        """Cancel the current recording and discard the macro"""
        if not self.is_recording or self.recording_macro is None:
            return

        macro_id = self.recording_macro.id
        self.is_recording = False
        self.recording_macro = None
        self.delete_macro(macro_id)
        logger.info("Cancelled macro recording")

    def save_to_dict(self) -> dict:
        """Save all macros to dictionary for JSON serialization"""
        return {macro_id: macro.to_dict() for macro_id, macro in self.macros.items()}

    def load_from_dict(self, data: dict):
        """Load macros from dictionary"""
        self.macros.clear()
        for macro_id, macro_data in data.items():
            try:
                macro = Macro.from_dict(macro_data)
                self.macros[macro_id] = macro
            except Exception as e:
                logger.error(f"Failed to load macro {macro_id}: {e}")

    def validate_macro(self, macro_id: str) -> tuple[bool, List[str]]:
        """
        Validate a macro

        Args:
            macro_id: ID of macro to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if macro_id not in self.macros:
            return False, ["Macro not found"]

        macro = self.macros[macro_id]
        errors = []

        if not macro.name or not macro.name.strip():
            errors.append("Macro name cannot be empty")

        if len(macro.steps) == 0:
            errors.append("Macro must have at least one step")

        # Validate execution parameters
        if macro.repeat < 1:
            errors.append("Repeat count must be at least 1")

        if macro.delay_jitter_ms < 0:
            errors.append("Delay jitter cannot be negative")

        # Validate each step
        for i, step in enumerate(macro.steps):
            valid_types = [e.value for e in MacroStepType]
            if step.type not in valid_types:
                errors.append(f"Step {i+1}: Invalid step type '{step.type}'")

            # Validate step-specific parameters
            if (
                step.type == MacroStepType.KEY_PRESS.value
                or step.type == MacroStepType.KEY_DOWN.value
            ):
                if not step.key:
                    errors.append(f"Step {i+1}: KEY step requires key parameter")

            if step.type == MacroStepType.KEY_SEQUENCE.value:
                if not step.key:
                    errors.append(f"Step {i+1}: KEY_SEQUENCE requires key parameter")

            if step.type == MacroStepType.MOUSE_CLICK.value:
                if not step.button or step.button not in ["left", "right", "middle"]:
                    errors.append(
                        f"Step {i+1}: MOUSE_CLICK requires valid button (left/right/middle)"
                    )

            if step.type == MacroStepType.MOUSE_MOVE.value:
                if step.x is None or step.y is None:
                    errors.append(f"Step {i+1}: MOUSE_MOVE requires x and y coordinates")

            if step.type == MacroStepType.DELAY.value:
                if step.duration_ms < 0:
                    errors.append(f"Step {i+1}: DELAY duration cannot be negative")

            if step.delay_jitter_ms < 0:
                errors.append(f"Step {i+1}: Delay jitter cannot be negative")

        # Validate legacy actions if present
        for i, action in enumerate(macro.actions):
            if action.action_type not in [e.value for e in MacroActionType]:
                errors.append(f"Action {i+1}: Invalid action type '{action.action_type}'")

        return len(errors) == 0, errors


# Default macros (examples)
DEFAULT_MACROS = [
    {
        "name": "Quick Tips",
        "description": "Request tips and pause",
        "steps": [
            MacroStep(type=MacroStepType.SHOW_TIPS.value, duration_ms=100),
            MacroStep(type=MacroStepType.DELAY.value, duration_ms=2000),
        ],
    },
    {
        "name": "Reset View",
        "description": "Clear chat and show overview",
        "steps": [
            MacroStep(type=MacroStepType.CLEAR_CHAT.value, duration_ms=100),
            MacroStep(type=MacroStepType.SHOW_OVERVIEW.value, duration_ms=100),
        ],
    },
]
