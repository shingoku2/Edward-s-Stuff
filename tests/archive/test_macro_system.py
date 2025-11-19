"""
Test suite for the macro and keybind system
Tests macro creation, storage, execution, and AI generation
"""

import sys
import os
import json
import tempfile
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from macro_manager import Macro, MacroStep, MacroStepType, MacroManager
from macro_store import MacroStore
from macro_runner import MacroRunner, MacroExecutionState
from keybind_manager import KeybindManager, Keybind, MacroKeybind, KeybindAction

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def test_macro_step_creation():
    """Test creating macro steps"""
    print("TEST: Macro step creation...")

    # Create a key press step
    step1 = MacroStep(
        type=MacroStepType.KEY_PRESS.value,
        key="a",
        duration_ms=0
    )
    assert step1.type == "key_press"
    assert step1.key == "a"

    # Create a mouse click step
    step2 = MacroStep(
        type=MacroStepType.MOUSE_CLICK.value,
        button="left",
        x=100,
        y=200
    )
    assert step2.button == "left"
    assert step2.x == 100

    # Create a delay step
    step3 = MacroStep(
        type=MacroStepType.DELAY.value,
        duration_ms=500,
        delay_jitter_ms=100
    )
    assert step3.duration_ms == 500

    # Test serialization
    data = step1.to_dict()
    step_from_dict = MacroStep.from_dict(data)
    assert step_from_dict.key == step1.key

    print("  ✓ Macro steps created and serialized successfully")


def test_macro_creation():
    """Test creating and managing macros"""
    print("TEST: Macro creation...")

    manager = MacroManager()

    # Create a macro
    macro = manager.create_macro(
        "Quick Attack",
        "Press 1 then 2 with delay"
    )
    assert macro.name == "Quick Attack"
    assert len(manager.get_all_macros()) == 1

    # Add steps to macro
    step1 = MacroStep(
        type=MacroStepType.KEY_PRESS.value,
        key="1"
    )
    step2 = MacroStep(
        type=MacroStepType.DELAY.value,
        duration_ms=100
    )
    step3 = MacroStep(
        type=MacroStepType.KEY_PRESS.value,
        key="2"
    )

    macro.add_step(step1)
    macro.add_step(step2)
    macro.add_step(step3)

    assert len(macro.steps) == 3

    # Test macro validation
    is_valid, errors = manager.validate_macro(macro.id)
    assert is_valid, f"Macro validation failed: {errors}"

    # Test macro serialization
    macro_dict = macro.to_dict()
    macro_restored = Macro.from_dict(macro_dict)
    assert macro_restored.name == macro.name
    assert len(macro_restored.steps) == 3

    print("  ✓ Macros created, managed, and validated successfully")


def test_macro_duplication():
    """Test duplicating macros"""
    print("TEST: Macro duplication...")

    manager = MacroManager()

    # Create original macro
    original = manager.create_macro("Original", "Test macro")
    original.add_step(MacroStep(type=MacroStepType.KEY_PRESS.value, key="a"))

    # Duplicate it
    duplicate = manager.duplicate_macro(original.id)
    assert duplicate is not None
    assert duplicate.name == "Original (Copy)"
    assert len(duplicate.steps) == 1

    # Check both exist
    assert len(manager.get_all_macros()) == 2

    print("  ✓ Macros duplicated successfully")


def test_macro_store():
    """Test macro persistence to disk"""
    print("TEST: Macro store persistence...")

    with tempfile.TemporaryDirectory() as tmpdir:
        store = MacroStore(tmpdir)

        # Create and save a macro
        macro = Macro(
            id="test_macro_1",
            name="Test Macro",
            description="For testing",
            steps=[
                MacroStep(type=MacroStepType.KEY_PRESS.value, key="a"),
                MacroStep(type=MacroStepType.DELAY.value, duration_ms=100),
                MacroStep(type=MacroStepType.KEY_PRESS.value, key="b")
            ]
        )

        assert store.save_macro(macro), "Failed to save macro"

        # Load it back
        loaded = store.load_macro("test_macro_1")
        assert loaded is not None
        assert loaded.name == macro.name
        assert len(loaded.steps) == 3

        # Test save all / load all
        macro2 = Macro(
            id="test_macro_2",
            name="Second Macro",
            description="Another test"
        )
        all_macros = {"test_macro_1": macro, "test_macro_2": macro2}
        store.save_all_macros(all_macros)

        loaded_all = store.load_all_macros()
        assert len(loaded_all) == 2

        # Test deletion
        assert store.delete_macro("test_macro_1")
        loaded_all = store.load_all_macros()
        assert len(loaded_all) == 1

        print("  ✓ Macro store saves and loads successfully")


def test_macro_search():
    """Test searching macros"""
    print("TEST: Macro search...")

    with tempfile.TemporaryDirectory() as tmpdir:
        store = MacroStore(tmpdir)

        # Create and save test macros
        macros = [
            Macro(id="m1", name="Quick Attack", description="Fast attack combo"),
            Macro(id="m2", name="Dodge Roll", description="Roll away from danger"),
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

        print("  ✓ Macro search works correctly")


def test_macro_duration_calculation():
    """Test calculating macro duration"""
    print("TEST: Macro duration calculation...")

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
    assert duration == 600, f"Expected 600ms, got {duration}ms"

    print("  ✓ Macro duration calculated correctly")


def test_keybind_creation():
    """Test creating keybinds"""
    print("TEST: Keybind creation...")

    manager = KeybindManager()

    keybind = Keybind(
        action=KeybindAction.TOGGLE_OVERLAY.value,
        keys="ctrl+shift+g",
        description="Toggle overlay",
        enabled=True,
        system_wide=True
    )

    assert keybind.action == "toggle_overlay"
    assert keybind.keys == "ctrl+shift+g"

    # Test serialization
    data = keybind.to_dict()
    restored = Keybind.from_dict(data)
    assert restored.keys == keybind.keys

    print("  ✓ Keybinds created successfully")


def test_macro_keybind_creation():
    """Test creating macro keybinds"""
    print("TEST: Macro keybind creation...")

    macro_keybind = MacroKeybind(
        macro_id="attack_combo",
        keys="alt+1",
        description="Execute attack combo"
    )

    assert macro_keybind.macro_id == "attack_combo"
    assert macro_keybind.keys == "alt+1"

    # Test serialization
    data = macro_keybind.to_dict()
    restored = MacroKeybind.from_dict(data)
    assert restored.macro_id == macro_keybind.macro_id

    print("  ✓ Macro keybinds created successfully")


def test_keybind_conflict_detection():
    """Test keybind conflict detection"""
    print("TEST: Keybind conflict detection...")

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

    # Register first keybind
    assert manager.register_keybind(keybind1, lambda: None)

    # Try to register conflicting keybind
    assert not manager.register_keybind(keybind2, lambda: None)

    # Should be able to register with override
    assert manager.register_keybind(keybind2, lambda: None, override=True)

    print("  ✓ Keybind conflict detection works")


def test_macro_runner_initialization():
    """Test macro runner initialization"""
    print("TEST: Macro runner initialization...")

    runner = MacroRunner(enabled=True)

    assert runner.enabled is True
    assert runner.state == MacroExecutionState.IDLE
    assert not runner.is_running()

    print("  ✓ Macro runner initialized correctly")


def test_macro_validation_with_errors():
    """Test macro validation catches errors"""
    print("TEST: Macro validation error detection...")

    manager = MacroManager()

    # Create invalid macro (no steps)
    invalid_macro = manager.create_macro("Invalid", "No steps")

    is_valid, errors = manager.validate_macro(invalid_macro.id)
    assert not is_valid
    assert any("at least one step" in e for e in errors)

    # Add invalid step
    invalid_step = MacroStep(
        type=MacroStepType.MOUSE_CLICK.value,
        button="invalid_button"  # Invalid button
    )
    invalid_macro.add_step(invalid_step)

    is_valid, errors = manager.validate_macro(invalid_macro.id)
    assert not is_valid

    print("  ✓ Macro validation detects errors correctly")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("RUNNING MACRO SYSTEM TEST SUITE")
    print("="*60 + "\n")

    tests = [
        test_macro_step_creation,
        test_macro_creation,
        test_macro_duplication,
        test_macro_store,
        test_macro_search,
        test_macro_duration_calculation,
        test_keybind_creation,
        test_macro_keybind_creation,
        test_keybind_conflict_detection,
        test_macro_runner_initialization,
        test_macro_validation_with_errors,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
