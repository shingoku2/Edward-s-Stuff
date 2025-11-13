"""
Macro Manager Module
Handles macro creation, editing, and execution
"""

import logging
import time
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class MacroActionType(Enum):
    """Types of macro actions"""
    SHOW_TIPS = "show_tips"
    SHOW_OVERVIEW = "show_overview"
    CLEAR_CHAT = "clear_chat"
    SEND_MESSAGE = "send_message"
    TOGGLE_OVERLAY = "toggle_overlay"
    CLOSE_OVERLAY = "close_overlay"
    OPEN_SETTINGS = "open_settings"
    WAIT = "wait"  # Wait for specified milliseconds
    CUSTOM_COMMAND = "custom_command"  # User-defined command


@dataclass
class MacroAction:
    """Represents a single action in a macro"""
    action_type: str  # MacroActionType enum value
    parameters: Dict[str, Any] = field(default_factory=dict)
    delay_after: int = 0  # Delay in milliseconds after executing this action

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'MacroAction':
        """Create MacroAction from dictionary"""
        return MacroAction(**data)


@dataclass
class Macro:
    """Represents a macro (sequence of actions)"""
    id: str
    name: str
    description: str
    actions: List[MacroAction] = field(default_factory=list)
    enabled: bool = True
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'actions': [action.to_dict() for action in self.actions],
            'enabled': self.enabled,
            'created_at': self.created_at,
            'modified_at': self.modified_at
        }

    @staticmethod
    def from_dict(data: dict) -> 'Macro':
        """Create Macro from dictionary"""
        actions = [MacroAction.from_dict(a) for a in data.get('actions', [])]
        return Macro(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            actions=actions,
            enabled=data.get('enabled', True),
            created_at=data.get('created_at', time.time()),
            modified_at=data.get('modified_at', time.time())
        )

    def add_action(self, action: MacroAction):
        """Add an action to the macro"""
        self.actions.append(action)
        self.modified_at = time.time()

    def remove_action(self, index: int) -> bool:
        """Remove an action by index"""
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
            self.modified_at = time.time()
            return True
        return False

    def move_action(self, from_index: int, to_index: int) -> bool:
        """Move an action from one position to another"""
        if 0 <= from_index < len(self.actions) and 0 <= to_index < len(self.actions):
            action = self.actions.pop(from_index)
            self.actions.insert(to_index, action)
            self.modified_at = time.time()
            return True
        return False

    def get_total_duration(self) -> int:
        """Get total duration of macro in milliseconds"""
        total = 0
        for action in self.actions:
            total += action.delay_after
            if action.action_type == MacroActionType.WAIT.value:
                total += action.parameters.get('duration', 0)
        return total


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
        macro = Macro(
            id=macro_id,
            name=name,
            description=description
        )
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
            actions=[MacroAction.from_dict(a.to_dict()) for a in original.actions],
            enabled=original.enabled
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

    def update_macro(self, macro_id: str, name: Optional[str] = None,
                    description: Optional[str] = None,
                    actions: Optional[List[MacroAction]] = None,
                    enabled: Optional[bool] = None) -> bool:
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
                    duration = action.parameters.get('duration', 0)
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
        return {
            macro_id: macro.to_dict()
            for macro_id, macro in self.macros.items()
        }

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

        if len(macro.actions) == 0:
            errors.append("Macro must have at least one action")

        # Validate each action
        for i, action in enumerate(macro.actions):
            if action.action_type not in [e.value for e in MacroActionType]:
                errors.append(f"Action {i+1}: Invalid action type '{action.action_type}'")

            # Validate action-specific parameters
            if action.action_type == MacroActionType.SEND_MESSAGE.value:
                if 'message' not in action.parameters or not action.parameters['message']:
                    errors.append(f"Action {i+1}: SEND_MESSAGE requires 'message' parameter")

            if action.action_type == MacroActionType.WAIT.value:
                if 'duration' not in action.parameters:
                    errors.append(f"Action {i+1}: WAIT requires 'duration' parameter")
                elif action.parameters['duration'] < 0:
                    errors.append(f"Action {i+1}: WAIT duration cannot be negative")

        return len(errors) == 0, errors


# Default macros (examples)
DEFAULT_MACROS = [
    {
        'name': 'Quick Tips',
        'description': 'Request tips and clear chat',
        'actions': [
            MacroAction(
                action_type=MacroActionType.SHOW_TIPS.value,
                delay_after=100
            ),
            MacroAction(
                action_type=MacroActionType.WAIT.value,
                parameters={'duration': 2000},
                delay_after=0
            ),
        ]
    },
    {
        'name': 'Reset View',
        'description': 'Clear chat and show overview',
        'actions': [
            MacroAction(
                action_type=MacroActionType.CLEAR_CHAT.value,
                delay_after=100
            ),
            MacroAction(
                action_type=MacroActionType.SHOW_OVERVIEW.value,
                delay_after=100
            ),
        ]
    },
]
