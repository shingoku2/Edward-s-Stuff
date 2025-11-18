"""
Macro Runner Module
Executes macros with keyboard/mouse input simulation
Cross-platform support with anti-cheat awareness
"""

import logging
import time
import threading
import random
from typing import Optional, Callable
from enum import Enum

from macro_manager import Macro, MacroStep, MacroStepType, MacroManager

logger = logging.getLogger(__name__)

# Try to import input simulation library
try:
    from pynput import mouse, keyboard
    from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logger.warning("pynput not available - macro execution will be limited")
    mouse = None
    keyboard = None
    Key = None
    KeyCode = None
    KeyboardController = None


class MacroExecutionState(Enum):
    """States of macro execution"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class MacroRunner:
    """
    Executes macros with keyboard/mouse input simulation
    Runs in background thread to keep UI responsive
    """

    def __init__(self, enabled: bool = False, macro_manager: Optional[MacroManager] = None, config=None):
        """
        Initialize the macro runner

        Args:
            enabled: Whether macros are enabled (respects anti-cheat awareness)
            macro_manager: The MacroManager instance with UI action handlers
            config: Configuration object with timeout settings
        """
        self.enabled = enabled
        self.macro_manager = macro_manager
        self.config = config
        self.state = MacroExecutionState.IDLE
        self.current_macro: Optional[Macro] = None
        self.execution_thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_step_executed: Optional[Callable] = None
        self.on_macro_finished: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

        # Input controllers
        if PYNPUT_AVAILABLE:
            self.keyboard_controller = KeyboardController()
            self.mouse_controller = mouse.Controller()
        else:
            self.keyboard_controller = None
            self.mouse_controller = None

        logger.info(f"MacroRunner initialized (enabled={enabled}, macro_manager={'present' if macro_manager else 'None'})")

    def execute_macro(self, macro: Macro) -> bool:
        """
        Execute a macro in background thread

        Args:
            macro: Macro to execute

        Returns:
            True if execution started successfully
        """
        if not self.enabled:
            logger.warning("Macro execution is disabled")
            return False

        if not PYNPUT_AVAILABLE:
            logger.error("pynput not available - cannot execute macros")
            return False

        if self.state == MacroExecutionState.RUNNING:
            logger.warning("Macro already executing")
            return False

        # Validate repeat count against configured maximum
        max_repeat = 100  # Default safety limit
        if self.config and hasattr(self.config, 'max_macro_repeat'):
            max_repeat = self.config.max_macro_repeat

        if macro.repeat > max_repeat:
            error_msg = f"Macro repeat count ({macro.repeat}) exceeds maximum allowed ({max_repeat})"
            logger.error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False

        # Validate macro
        is_valid, errors = self._validate_macro(macro)
        if not is_valid:
            error_msg = "; ".join(errors)
            logger.error(f"Macro validation failed: {error_msg}")
            if self.on_error:
                self.on_error(f"Macro validation failed: {error_msg}")
            return False

        self.current_macro = macro
        self.state = MacroExecutionState.RUNNING

        # Start execution in background thread
        self.execution_thread = threading.Thread(
            target=self._execute_macro_thread,
            daemon=True
        )
        self.execution_thread.start()

        logger.info(f"Started executing macro: {macro.name}")
        return True

    def _execute_macro_thread(self):
        """Execute macro in background thread"""
        try:
            macro = self.current_macro
            if not macro:
                return

            # Get timeout setting (default: 30 seconds)
            timeout_seconds = 30
            if self.config and hasattr(self.config, 'macro_execution_timeout'):
                timeout_seconds = self.config.macro_execution_timeout

            # Track start time for timeout enforcement
            start_time = time.time()

            # Execute macro 'repeat' times
            for repeat_count in range(macro.repeat):
                # Check for timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout_seconds:
                    error_msg = f"Macro exceeded {timeout_seconds}s timeout (elapsed: {elapsed_time:.1f}s)"
                    logger.error(error_msg)
                    if self.on_error:
                        self.on_error(error_msg)
                    self.state = MacroExecutionState.ERROR
                    return

                if self.state == MacroExecutionState.STOPPED:
                    logger.info("Macro execution stopped by user")
                    break

                logger.debug(f"Executing macro repeat {repeat_count + 1}/{macro.repeat}")

                # Execute each step
                for step_idx, step in enumerate(macro.steps):
                    # Check for timeout in inner loop too
                    elapsed_time = time.time() - start_time
                    if elapsed_time > timeout_seconds:
                        error_msg = f"Macro exceeded {timeout_seconds}s timeout (elapsed: {elapsed_time:.1f}s)"
                        logger.error(error_msg)
                        if self.on_error:
                            self.on_error(error_msg)
                        self.state = MacroExecutionState.ERROR
                        return

                    if self.state == MacroExecutionState.STOPPED:
                        logger.info("Macro execution stopped by user")
                        break

                    try:
                        self._execute_step(step)

                        # Callback for each step
                        if self.on_step_executed:
                            self.on_step_executed(step_idx + 1, len(macro.steps))

                    except Exception as e:
                        logger.error(f"Error executing step {step_idx + 1}: {e}")
                        if self.on_error:
                            self.on_error(f"Error in step {step_idx + 1}: {str(e)}")
                        raise

            # Macro completed successfully
            self.state = MacroExecutionState.IDLE
            logger.info(f"Macro execution completed: {macro.name}")

            if self.on_macro_finished:
                self.on_macro_finished(macro)

        except Exception as e:
            self.state = MacroExecutionState.ERROR
            logger.error(f"Macro execution error: {e}")
            if self.on_error:
                self.on_error(f"Macro execution error: {str(e)}")

    def _execute_step(self, step: MacroStep):
        """
        Execute a single macro step

        Args:
            step: MacroStep to execute
        """
        # Add optional jitter to delays
        delay = step.duration_ms if step.duration_ms > 0 else 0
        if step.delay_jitter_ms > 0 and step.type == MacroStepType.DELAY.value:
            jitter = random.randint(0, step.delay_jitter_ms)
            delay = step.duration_ms + jitter

        try:
            if step.type == MacroStepType.KEY_PRESS.value:
                self._press_key(step.key)
                if delay > 0:
                    time.sleep(delay / 1000.0)

            elif step.type == MacroStepType.KEY_DOWN.value:
                self._key_down(step.key)
                if step.duration_ms > 0:
                    time.sleep(step.duration_ms / 1000.0)
                    self._key_up(step.key)

            elif step.type == MacroStepType.KEY_UP.value:
                self._key_up(step.key)

            elif step.type == MacroStepType.KEY_SEQUENCE.value:
                self._type_sequence(step.key)
                if delay > 0:
                    time.sleep(delay / 1000.0)

            elif step.type == MacroStepType.MOUSE_MOVE.value:
                self._move_mouse(step.x, step.y)
                if delay > 0:
                    time.sleep(delay / 1000.0)

            elif step.type == MacroStepType.MOUSE_CLICK.value:
                self._click_mouse(step.button, step.x, step.y)
                if delay > 0:
                    time.sleep(delay / 1000.0)

            elif step.type == MacroStepType.MOUSE_SCROLL.value:
                self._scroll_mouse(step.x, step.y, step.scroll_amount)
                if delay > 0:
                    time.sleep(delay / 1000.0)

            elif step.type == MacroStepType.DELAY.value:
                time.sleep(delay / 1000.0)

            # Handle UI/legacy actions via the MacroManager
            elif self.macro_manager and step.type in self.macro_manager.action_handlers:
                logger.debug(f"Executing UI action: {step.type}")
                handler = self.macro_manager.action_handlers[step.type]

                # Note: UI action steps typically don't have parameters
                # For SEND_MESSAGE action, the text would be stored in 'key' field
                params = {}
                if step.type == MacroStepType.SEND_MESSAGE.value and step.key:
                    params['message'] = step.key

                # Execute the handler
                handler(**params)

                # Apply delay if specified
                if delay > 0:
                    time.sleep(delay / 1000.0)

            # Handle unknown/unhandled step types
            elif step.type in [e.value for e in MacroStepType]:
                logger.warning(f"Skipping unhandled legacy/UI action type: {step.type}")

        except Exception as e:
            logger.error(f"Error executing step {step.type}: {e}")
            raise

    def _press_key(self, key_combo: str):
        """Press and release a key or key combination"""
        if not self.keyboard_controller:
            return

        keys = self._parse_key_combo(key_combo)

        # Press all keys
        for key in keys:
            self.keyboard_controller.press(key)
            time.sleep(0.01)  # Small delay between key press

        # Release all keys in reverse order
        for key in reversed(keys):
            self.keyboard_controller.release(key)
            time.sleep(0.01)

    def _key_down(self, key_combo: str):
        """Press down a key without releasing"""
        if not self.keyboard_controller:
            return

        keys = self._parse_key_combo(key_combo)

        for key in keys:
            self.keyboard_controller.press(key)
            time.sleep(0.01)

    def _key_up(self, key_combo: str):
        """Release a pressed key"""
        if not self.keyboard_controller:
            return

        keys = self._parse_key_combo(key_combo)

        for key in reversed(keys):
            self.keyboard_controller.release(key)
            time.sleep(0.01)

    def _type_sequence(self, text: str):
        """Type a sequence of characters"""
        if not self.keyboard_controller:
            return

        for char in text:
            self.keyboard_controller.type(char)
            time.sleep(0.01)  # Small delay between characters

    def _move_mouse(self, x: int, y: int):
        """Move mouse to position"""
        if not self.mouse_controller:
            return

        self.mouse_controller.position = (x, y)

    def _click_mouse(self, button: str, x: Optional[int] = None, y: Optional[int] = None):
        """Click mouse button"""
        if not self.mouse_controller:
            return

        # Move to position if specified
        if x is not None and y is not None:
            self.mouse_controller.position = (x, y)

        # Click button
        button_map = {
            'left': mouse.Button.left,
            'right': mouse.Button.right,
            'middle': mouse.Button.middle
        }

        click_button = button_map.get(button, mouse.Button.left)
        self.mouse_controller.click(click_button)

    def _scroll_mouse(self, x: int, y: int, amount: int):
        """Scroll mouse wheel"""
        if not self.mouse_controller:
            return

        # Move to position
        self.mouse_controller.position = (x, y)

        # Scroll
        self.mouse_controller.scroll(0, amount)

    def _parse_key_combo(self, key_combo: str) -> list:
        """
        Parse key combination string into pynput keys

        Args:
            key_combo: Key combination string (e.g., "ctrl+shift+a")

        Returns:
            List of pynput Key/KeyCode objects
        """
        if not Key or not KeyCode:
            return []

        keys = []
        parts = key_combo.lower().split('+')

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
                keys.append(key_map[part])
            elif len(part) == 1:
                # Single character key
                try:
                    keys.append(KeyCode.from_char(part))
                except ValueError:
                    logger.warning(f"Cannot convert character to key: {part}")
            else:
                logger.warning(f"Unknown key: {part}")

        return keys

    def stop_macro(self):
        """Stop currently executing macro"""
        if self.state == MacroExecutionState.RUNNING:
            self.state = MacroExecutionState.STOPPED
            logger.info("Macro execution stop requested")

    def pause_macro(self):
        """Pause currently executing macro"""
        if self.state == MacroExecutionState.RUNNING:
            self.state = MacroExecutionState.PAUSED
            logger.info("Macro execution paused")

    def resume_macro(self):
        """Resume paused macro"""
        if self.state == MacroExecutionState.PAUSED:
            self.state = MacroExecutionState.RUNNING
            logger.info("Macro execution resumed")

    def _validate_macro(self, macro: Macro) -> tuple[bool, list]:
        """
        Quick validation of macro before execution

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        if not macro.name:
            errors.append("Macro name is empty")

        if len(macro.steps) == 0:
            errors.append("Macro has no steps")

        if macro.repeat < 1:
            errors.append("Repeat count must be at least 1")

        # Check that we have required input simulation capabilities
        if not PYNPUT_AVAILABLE:
            errors.append("Input simulation library (pynput) not available")

        return len(errors) == 0, errors

    def get_state(self) -> MacroExecutionState:
        """Get current execution state"""
        return self.state

    def is_running(self) -> bool:
        """Check if macro is currently running"""
        return self.state == MacroExecutionState.RUNNING
