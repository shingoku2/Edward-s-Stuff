#!/usr/bin/env python3
"""
Test GUI startup to identify specific issues
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set offscreen platform for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_imports():
    """Test that all GUI modules can be imported"""
    print("Testing imports...")
    try:
        from config import Config
        print("✓ Config")

        from credential_store import CredentialStore
        print("✓ CredentialStore")

        from ui.design_system import design_system
        print("✓ Design System")

        from PyQt6.QtWidgets import QApplication
        print("✓ PyQt6")

        from gui import MainWindow
        print("✓ MainWindow")

        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_init():
    """Test basic initialization"""
    print("\nTesting basic initialization...")
    try:
        from PyQt6.QtWidgets import QApplication
        from config import Config
        from credential_store import CredentialStore
        from ui.design_system import design_system
        from gui import MainWindow

        app = QApplication(sys.argv)
        print("✓ QApplication created")

        config = Config(require_keys=False)
        print("✓ Config created")

        credential_store = CredentialStore()
        print("✓ CredentialStore created")

        # Try to create MainWindow
        window = MainWindow(
            ai_assistant=None,  # No AI assistant for test
            config=config,
            credential_store=credential_store,
            design_system=design_system
        )
        print("✓ MainWindow created")

        # Clean up
        window.cleanup()
        app.quit()

        return True
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GUI Startup Test")
    print("=" * 60)
    print()

    success = True

    if not test_imports():
        success = False

    if not test_basic_init():
        success = False

    print()
    print("=" * 60)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)

    sys.exit(0 if success else 1)
