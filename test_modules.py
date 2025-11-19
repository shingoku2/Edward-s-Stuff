#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test module imports for Omnix Gaming Companion

This test file verifies that all core modules can be imported successfully.
It's designed to catch import errors, circular dependencies, and missing dependencies
early in the development/build process.

Usage:
    python test_modules.py
    python -m pytest test_modules.py
"""

import sys
import os
import unittest
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


class TestCoreModules(unittest.TestCase):
    """Test core application modules"""

    def test_config_import(self):
        """Test config module import"""
        try:
            from src import config
            from src.config import Config
            self.assertTrue(hasattr(config, 'Config'))
        except ImportError as e:
            self.fail(f"Failed to import config: {e}")

    def test_credential_store_import(self):
        """Test credential_store module import"""
        try:
            from src import credential_store
            from src.credential_store import CredentialStore
            self.assertTrue(hasattr(credential_store, 'CredentialStore'))
        except ImportError as e:
            self.fail(f"Failed to import credential_store: {e}")


class TestGameDetectionModules(unittest.TestCase):
    """Test game detection modules"""

    def test_game_detector_import(self):
        """Test game_detector module import"""
        try:
            from src import game_detector
            from src.game_detector import GameDetector
            self.assertTrue(hasattr(game_detector, 'GameDetector'))
        except ImportError as e:
            self.fail(f"Failed to import game_detector: {e}")

    def test_game_watcher_import(self):
        """Test game_watcher module import"""
        try:
            from src import game_watcher
            from src.game_watcher import GameWatcher
            self.assertTrue(hasattr(game_watcher, 'GameWatcher'))
        except ImportError as e:
            self.fail(f"Failed to import game_watcher: {e}")

    def test_game_profile_import(self):
        """Test game_profile module import"""
        try:
            from src import game_profile
            from src.game_profile import GameProfile, GameProfileStore
            self.assertTrue(hasattr(game_profile, 'GameProfile'))
            self.assertTrue(hasattr(game_profile, 'GameProfileStore'))
        except ImportError as e:
            self.fail(f"Failed to import game_profile: {e}")


class TestAIIntegrationModules(unittest.TestCase):
    """Test AI integration modules"""

    def test_ai_assistant_import(self):
        """Test ai_assistant module import"""
        try:
            from src import ai_assistant
            from src.ai_assistant import AIAssistant
            self.assertTrue(hasattr(ai_assistant, 'AIAssistant'))
        except ImportError as e:
            self.fail(f"Failed to import ai_assistant: {e}")

    def test_ai_router_import(self):
        """Test ai_router module import"""
        try:
            from src import ai_router
            from src.ai_router import AIRouter
            self.assertTrue(hasattr(ai_router, 'AIRouter'))
        except ImportError as e:
            self.fail(f"Failed to import ai_router: {e}")

    def test_providers_import(self):
        """Test providers module import"""
        try:
            from src import providers
            from src.providers import OpenAIProvider, AnthropicProvider, GeminiProvider
            self.assertTrue(hasattr(providers, 'OpenAIProvider'))
            self.assertTrue(hasattr(providers, 'AnthropicProvider'))
            self.assertTrue(hasattr(providers, 'GeminiProvider'))
        except ImportError as e:
            self.fail(f"Failed to import providers: {e}")

    def test_provider_tester_import(self):
        """Test provider_tester module import"""
        try:
            from src import provider_tester
            from src.provider_tester import ProviderTester
            self.assertTrue(hasattr(provider_tester, 'ProviderTester'))
        except ImportError as e:
            self.fail(f"Failed to import provider_tester: {e}")


class TestKnowledgeSystemModules(unittest.TestCase):
    """Test knowledge system modules"""

    def test_knowledge_pack_import(self):
        """Test knowledge_pack module import"""
        try:
            from src import knowledge_pack
            from src.knowledge_pack import KnowledgePack, KnowledgeSource
            self.assertTrue(hasattr(knowledge_pack, 'KnowledgePack'))
            self.assertTrue(hasattr(knowledge_pack, 'KnowledgeSource'))
        except ImportError as e:
            self.fail(f"Failed to import knowledge_pack: {e}")

    def test_knowledge_store_import(self):
        """Test knowledge_store module import"""
        try:
            from src import knowledge_store
            from src.knowledge_store import KnowledgePackStore, get_knowledge_pack_store
            self.assertTrue(hasattr(knowledge_store, 'KnowledgePackStore'))
            self.assertTrue(hasattr(knowledge_store, 'get_knowledge_pack_store'))
        except ImportError as e:
            self.fail(f"Failed to import knowledge_store: {e}")

    def test_knowledge_index_import(self):
        """Test knowledge_index module import"""
        try:
            from src import knowledge_index
            from src.knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding, get_knowledge_index
            self.assertTrue(hasattr(knowledge_index, 'KnowledgeIndex'))
            self.assertTrue(hasattr(knowledge_index, 'SimpleTFIDFEmbedding'))
            self.assertTrue(hasattr(knowledge_index, 'get_knowledge_index'))
        except ImportError as e:
            self.fail(f"Failed to import knowledge_index: {e}")

    def test_knowledge_integration_import(self):
        """Test knowledge_integration module import"""
        try:
            from src import knowledge_integration
            from src.knowledge_integration import KnowledgeIntegration, get_knowledge_integration
            self.assertTrue(hasattr(knowledge_integration, 'KnowledgeIntegration'))
            self.assertTrue(hasattr(knowledge_integration, 'get_knowledge_integration'))
        except ImportError as e:
            self.fail(f"Failed to import knowledge_integration: {e}")

    def test_knowledge_ingestion_import(self):
        """Test knowledge_ingestion module import"""
        try:
            from src import knowledge_ingestion
            from src.knowledge_ingestion import (
                IngestionPipeline,
                FileIngestor,
                URLIngestor,
                get_ingestion_pipeline
            )
            self.assertTrue(hasattr(knowledge_ingestion, 'IngestionPipeline'))
            self.assertTrue(hasattr(knowledge_ingestion, 'FileIngestor'))
            self.assertTrue(hasattr(knowledge_ingestion, 'URLIngestor'))
            self.assertTrue(hasattr(knowledge_ingestion, 'get_ingestion_pipeline'))
        except ImportError as e:
            self.fail(f"Failed to import knowledge_ingestion: {e}")


class TestMacroSystemModules(unittest.TestCase):
    """Test macro system modules"""

    def test_macro_manager_import(self):
        """Test macro_manager module import"""
        try:
            from src import macro_manager
            from src.macro_manager import Macro, MacroStep, MacroStepType
            self.assertTrue(hasattr(macro_manager, 'Macro'))
            self.assertTrue(hasattr(macro_manager, 'MacroStep'))
            self.assertTrue(hasattr(macro_manager, 'MacroStepType'))
        except ImportError as e:
            self.fail(f"Failed to import macro_manager: {e}")

    def test_macro_store_import(self):
        """Test macro_store module import"""
        try:
            from src import macro_store
            from src.macro_store import MacroStore
            self.assertTrue(hasattr(macro_store, 'MacroStore'))
        except ImportError as e:
            self.fail(f"Failed to import macro_store: {e}")

    def test_macro_runner_import(self):
        """Test macro_runner module import"""
        try:
            from src import macro_runner
            from src.macro_runner import MacroRunner, MacroExecutionState
            self.assertTrue(hasattr(macro_runner, 'MacroRunner'))
            self.assertTrue(hasattr(macro_runner, 'MacroExecutionState'))
        except ImportError as e:
            self.fail(f"Failed to import macro_runner: {e}")

    def test_macro_ai_generator_import(self):
        """Test macro_ai_generator module import"""
        try:
            from src import macro_ai_generator
            from src.macro_ai_generator import MacroAIGenerator
            self.assertTrue(hasattr(macro_ai_generator, 'MacroAIGenerator'))
        except ImportError as e:
            self.fail(f"Failed to import macro_ai_generator: {e}")

    def test_keybind_manager_import(self):
        """Test keybind_manager module import"""
        try:
            from src import keybind_manager
            from src.keybind_manager import KeybindManager, Keybind, MacroKeybind, KeybindAction
            self.assertTrue(hasattr(keybind_manager, 'KeybindManager'))
            self.assertTrue(hasattr(keybind_manager, 'Keybind'))
            self.assertTrue(hasattr(keybind_manager, 'MacroKeybind'))
            self.assertTrue(hasattr(keybind_manager, 'KeybindAction'))
        except ImportError as e:
            self.fail(f"Failed to import keybind_manager: {e}")


class TestSessionModules(unittest.TestCase):
    """Test session management modules"""

    def test_session_logger_import(self):
        """Test session_logger module import"""
        try:
            from src import session_logger
            from src.session_logger import SessionLogger, SessionEvent, get_session_logger
            self.assertTrue(hasattr(session_logger, 'SessionLogger'))
            self.assertTrue(hasattr(session_logger, 'SessionEvent'))
            self.assertTrue(hasattr(session_logger, 'get_session_logger'))
        except ImportError as e:
            self.fail(f"Failed to import session_logger: {e}")

    def test_session_coaching_import(self):
        """Test session_coaching module import"""
        try:
            from src import session_coaching
            from src.session_coaching import SessionCoach
            self.assertTrue(hasattr(session_coaching, 'SessionCoach'))
        except ImportError as e:
            self.fail(f"Failed to import session_coaching: {e}")


class TestGUIModules(unittest.TestCase):
    """Test GUI modules (may skip if PyQt6 not available)"""

    def test_gui_import(self):
        """Test gui module import"""
        try:
            from src import gui
            self.assertTrue(hasattr(gui, 'OmnixMainWindow'))
        except ImportError as e:
            # PyQt6 may not be available in all test environments
            if "PyQt6" in str(e) or "libEGL" in str(e):
                self.skipTest("PyQt6/GUI dependencies not available in test environment")
            else:
                self.fail(f"Failed to import gui: {e}")

    def test_overlay_modes_import(self):
        """Test overlay_modes module import"""
        try:
            from src import overlay_modes
            from src.overlay_modes import OverlayModeConfig, ModeTransitionHelper
            from src.type_definitions import OverlayMode
            self.assertTrue(hasattr(overlay_modes, 'OverlayModeConfig'))
            self.assertTrue(hasattr(overlay_modes, 'ModeTransitionHelper'))
            # MODES is a class attribute, not a module-level constant
            self.assertTrue(hasattr(OverlayModeConfig, 'MODES'))
        except ImportError as e:
            if "PyQt6" in str(e) or "libEGL" in str(e):
                self.skipTest("PyQt6/GUI dependencies not available in test environment")
            else:
                self.fail(f"Failed to import overlay_modes: {e}")

    def test_settings_dialog_import(self):
        """Test settings_dialog module import"""
        try:
            from src import settings_dialog
            from src.settings_dialog import SettingsDialog
            self.assertTrue(hasattr(settings_dialog, 'SettingsDialog'))
        except ImportError as e:
            if "PyQt6" in str(e) or "libEGL" in str(e):
                self.skipTest("PyQt6/GUI dependencies not available in test environment")
            else:
                self.fail(f"Failed to import settings_dialog: {e}")


class TestUIDesignSystem(unittest.TestCase):
    """Test UI design system modules"""

    def test_design_system_import(self):
        """Test ui/design_system module import"""
        try:
            # Import from the actual module file
            from src.ui import design_system as ds_module_instance
            # Import classes from the module
            import importlib
            ds_module = importlib.import_module('src.ui.design_system')

            # Check the module has the class
            self.assertTrue(hasattr(ds_module, 'OmnixDesignSystem'))
            # Check the instance is accessible from __init__.py
            self.assertTrue(hasattr(ds_module_instance, 'generate_base_stylesheet'))
        except ImportError as e:
            if "PyQt6" in str(e) or "libEGL" in str(e):
                self.skipTest("PyQt6/GUI dependencies not available in test environment")
            else:
                self.fail(f"Failed to import ui.design_system: {e}")

    def test_tokens_import(self):
        """Test ui/tokens module import"""
        try:
            # Import using importlib to get actual module
            import importlib
            tokens_module = importlib.import_module('src.ui.tokens')

            # Check module has the classes
            self.assertTrue(hasattr(tokens_module, 'OmnixDesignTokens'))
            self.assertTrue(hasattr(tokens_module, 'ColorPalette'))
            self.assertTrue(hasattr(tokens_module, 'Typography'))
            self.assertTrue(hasattr(tokens_module, 'Spacing'))

            # Import instances and check they exist
            from src.ui.tokens import tokens, COLORS, TYPOGRAPHY, SPACING
            self.assertIsNotNone(tokens)
            self.assertIsNotNone(COLORS)
            self.assertIsNotNone(TYPOGRAPHY)
            self.assertIsNotNone(SPACING)
        except ImportError as e:
            self.fail(f"Failed to import ui.tokens: {e}")

    def test_ui_components_import(self):
        """Test ui/components module import"""
        try:
            from src.ui import components
            # Test that components package exists
            self.assertTrue(hasattr(components, '__path__'))
        except ImportError as e:
            if "PyQt6" in str(e) or "libEGL" in str(e):
                self.skipTest("PyQt6/GUI dependencies not available in test environment")
            else:
                self.fail(f"Failed to import ui.components: {e}")


class TestThemeSystem(unittest.TestCase):
    """Test theme system modules"""

    def test_theme_manager_import(self):
        """Test ui/theme_manager module import"""
        try:
            from src.ui import theme_manager
            from src.ui.theme_manager import OmnixThemeManager, get_theme_manager
            self.assertTrue(hasattr(theme_manager, 'OmnixThemeManager'))
            self.assertTrue(hasattr(theme_manager, 'get_theme_manager'))
        except ImportError as e:
            if "PyQt6" in str(e) or "libEGL" in str(e):
                self.skipTest("PyQt6/GUI dependencies not available in test environment")
            else:
                self.fail(f"Failed to import ui.theme_manager: {e}")


class TestTypeDefinitions(unittest.TestCase):
    """Test type definitions module"""

    def test_type_definitions_import(self):
        """Test type_definitions module import"""
        try:
            from src import type_definitions
            # Verify it doesn't shadow Python's built-in types module
            import types as builtin_types
            self.assertTrue(hasattr(builtin_types, 'FunctionType'))
        except ImportError as e:
            self.fail(f"Failed to import type_definitions: {e}")


def run_tests():
    """Run all module import tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCoreModules))
    suite.addTests(loader.loadTestsFromTestCase(TestGameDetectionModules))
    suite.addTests(loader.loadTestsFromTestCase(TestAIIntegrationModules))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeSystemModules))
    suite.addTests(loader.loadTestsFromTestCase(TestMacroSystemModules))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionModules))
    suite.addTests(loader.loadTestsFromTestCase(TestGUIModules))
    suite.addTests(loader.loadTestsFromTestCase(TestUIDesignSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestThemeSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestTypeDefinitions))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("MODULE IMPORT TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    run_tests()
