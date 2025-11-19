"""
Unit tests for macro and keybind system

Tests macro creation, storage, execution, and keybind management.
"""
import pytest
import json
from pathlib import Path


@pytest.mark.unit
class TestMacroStep:
    """Test MacroStep creation and serialization"""

    def test_key_press_step(self):
        """Test creating a key press step"""
        from macro_manager import MacroStep, MacroStepType

        step = MacroStep(
            type=MacroStepType.KEY_PRESS.value,
            key="a",
            duration_ms=0
        )

        assert step.type == "key_press"
        assert step.key == "a"

    def test_mouse_click_step(self):
        """Test creating a mouse click step"""
        from macro_manager import MacroStep, MacroStepType

        step = MacroStep(
            type=MacroStepType.MOUSE_CLICK.value,
            button="left",
            x=100,
            y=200
        )

        assert step.button == "left"
        assert step.x == 100
        assert step.y == 200

    def test_delay_step(self):
        """Test creating a delay step"""
        from macro_manager import MacroStep, MacroStepType

        step = MacroStep(
            type=MacroStepType.DELAY.value,
            duration_ms=500,
            delay_jitter_ms=100
        )

        assert step.duration_ms == 500
        assert step.delay_jitter_ms == 100

    def test_step_serialization(self):
        """Test MacroStep serialization"""
        from macro_manager import MacroStep, MacroStepType

        step = MacroStep(
            type=MacroStepType.KEY_PRESS.value,
            key="b"
        )

        # Serialize
        data = step.to_dict()
        assert isinstance(data, dict)

        # Deserialize
        restored = MacroStep.from_dict(data)
        assert restored.key == step.key


@pytest.mark.unit
class TestMacro:
    """Test Macro creation and management"""

    def test_macro_creation(self):
        """Test creating a macro"""
        from macro_manager import MacroManager

        manager = MacroManager()
        macro = manager.create_macro("Quick Attack", "Press 1 then 2")

        assert macro.name == "Quick Attack"
        assert len(manager.get_all_macros()) == 1

    def test_macro_add_steps(self):
        """Test adding steps to macro"""
        from macro_manager import MacroManager, MacroStep, MacroStepType

        manager = MacroManager()
        macro = manager.create_macro("Test", "Test macro")

        step1 = MacroStep(type=MacroStepType.KEY_PRESS.value, key="1")
        step2 = MacroStep(type=MacroStepType.DELAY.value, duration_ms=100)
        step3 = MacroStep(type=MacroStepType.KEY_PRESS.value, key="2")

        macro.add_step(step1)
        macro.add_step(step2)
        macro.add_step(step3)

        assert len(macro.steps) == 3

    def test_macro_validation(self):
        """Test macro validation"""
        from macro_manager import MacroManager, MacroStep, MacroStepType

        manager = MacroManager()
        macro = manager.create_macro("Valid", "Valid macro")

        # Empty macro is invalid
        is_valid, errors = manager.validate_macro(macro.id)
        assert is_valid is False
        assert any("at least one step" in e for e in errors)

        # Add valid step
        macro.add_step(MacroStep(type=MacroStepType.KEY_PRESS.value, key="a"))

        is_valid, errors = manager.validate_macro(macro.id)
        assert is_valid is True

    def test_macro_serialization(self):
        """Test macro serialization"""
        from macro_manager import Macro, MacroStep, MacroStepType

        macro = Macro(
            id="test_macro",
            name="Test",
            description="Test macro",
            steps=[
                MacroStep(type=MacroStepType.KEY_PRESS.value, key="a")
            ]
        )

        # Serialize
        macro_dict = macro.to_dict()
        assert isinstance(macro_dict, dict)
        assert macro_dict['id'] == 'test_macro'

        # Deserialize
        restored = Macro.from_dict(macro_dict)
        assert restored.name == macro.name
        assert len(restored.steps) == 1

    def test_macro_duplication(self):
        """Test duplicating macros"""
        from macro_manager import MacroManager, MacroStep, MacroStepType

        manager = MacroManager()
        original = manager.create_macro("Original", "Test macro")
        original.add_step(MacroStep(type=MacroStepType.KEY_PRESS.value, key="a"))

        duplicate = manager.duplicate_macro(original.id)

        assert duplicate is not None
        assert duplicate.name == "Original (Copy)"
        assert len(duplicate.steps) == 1
        assert len(manager.get_all_macros()) == 2

    def test_macro_duration_calculation(self):
        """Test calculating total macro duration"""
        from macro_manager import Macro, MacroStep, MacroStepType

        macro = Macro(
            id="test",
            name="Duration Test",
            description="Test",
            steps=[
                MacroStep(type=MacroStepType.KEY_PRESS.value, key="a"),
                MacroStep(type=MacroStepType.DELAY.value, duration_ms=100),
                MacroStep(type=MacroStepType.KEY_PRESS.value, key="b"),
                MacroStep(type=MacroStepType.DELAY.value, duration_ms=200)
            ],
            repeat=2
        )

        duration = macro.get_total_duration()
        # 100 + 200 = 300ms per repeat, * 2 repeats = 600ms
        assert duration == 600


@pytest.mark.unit
class TestMacroStore:
    """Test macro persistence"""

    def test_save_and_load_macro(self, temp_dir):
        """Test saving and loading a macro"""
        from macro_store import MacroStore
        from macro_manager import Macro, MacroStep, MacroStepType

        store = MacroStore(temp_dir)

        macro = Macro(
            id="test_macro_1",
            name="Test Macro",
            description="For testing",
            steps=[
                MacroStep(type=MacroStepType.KEY_PRESS.value, key="a"),
                MacroStep(type=MacroStepType.DELAY.value, duration_ms=100)
            ]
        )

        assert store.save_macro(macro) is True

        loaded = store.load_macro("test_macro_1")
        assert loaded is not None
        assert loaded.name == macro.name
        assert len(loaded.steps) == 2

    def test_delete_macro(self, temp_dir):
        """Test deleting a macro"""
        from macro_store import MacroStore
        from macro_manager import Macro

        store = MacroStore(temp_dir)

        macro = Macro(
            id="delete_test",
            name="Delete Test",
            description="Test"
        )

        store.save_macro(macro)
        assert store.delete_macro("delete_test") is True

        loaded = store.load_macro("delete_test")
        assert loaded is None

    def test_search_macros(self, temp_dir):
        """Test searching macros"""
        from macro_store import MacroStore
        from macro_manager import Macro

        store = MacroStore(temp_dir)

        macros = [
            Macro(id="m1", name="Quick Attack", description="Fast attack combo"),
            Macro(id="m2", name="Dodge Roll", description="Roll away"),
            Macro(id="m3", name="Quick Heal", description="Use healing spell")
        ]

        for m in macros:
            store.save_macro(m)

        # Search by name
        results = store.search_macros("Quick")
        assert len(results) == 2  # "Quick Attack" and "Quick Heal"

        # Search by description
        results = store.search_macros("spell")
        assert len(results) == 1  # "Quick Heal"


@pytest.mark.unit
class TestKeybinds:
    """Test keybind system"""

    def test_keybind_creation(self):
        """Test creating keybinds"""
        from keybind_manager import Keybind, KeybindAction

        keybind = Keybind(
            action=KeybindAction.TOGGLE_OVERLAY.value,
            keys="ctrl+shift+g",
            description="Toggle overlay",
            enabled=True,
            system_wide=True
        )

        assert keybind.action == "toggle_overlay"
        assert keybind.keys == "ctrl+shift+g"

    def test_keybind_serialization(self):
        """Test keybind serialization"""
        from keybind_manager import Keybind, KeybindAction

        keybind = Keybind(
            action=KeybindAction.TOGGLE_OVERLAY.value,
            keys="ctrl+shift+g",
            description="Toggle"
        )

        data = keybind.to_dict()
        restored = Keybind.from_dict(data)

        assert restored.keys == keybind.keys

    def test_macro_keybind_creation(self):
        """Test creating macro keybinds"""
        from keybind_manager import MacroKeybind

        macro_keybind = MacroKeybind(
            macro_id="attack_combo",
            keys="alt+1",
            description="Execute attack combo"
        )

        assert macro_keybind.macro_id == "attack_combo"
        assert macro_keybind.keys == "alt+1"

    def test_keybind_conflict_detection(self):
        """Test keybind conflict detection"""
        from keybind_manager import KeybindManager, Keybind

        manager = KeybindManager()

        keybind1 = Keybind(
            action="action1",
            keys="ctrl+shift+g",
            description="First"
        )

        keybind2 = Keybind(
            action="action2",
            keys="ctrl+shift+g",
            description="Second (same keys)"
        )

        # Register first
        assert manager.register_keybind(keybind1, lambda: None) is True

        # Try to register conflicting - should fail
        assert manager.register_keybind(keybind2, lambda: None) is False

        # With override should succeed
        assert manager.register_keybind(keybind2, lambda: None, override=True) is True


@pytest.mark.unit
class TestMacroRunner:
    """Test macro execution"""

    def test_runner_initialization(self):
        """Test macro runner initialization"""
        from macro_runner import MacroRunner, MacroExecutionState

        runner = MacroRunner(enabled=True)

        assert runner.enabled is True
        assert runner.state == MacroExecutionState.IDLE
        assert runner.is_running() is False
