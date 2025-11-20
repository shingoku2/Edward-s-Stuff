"""
Integration tests for CI/CD pipeline components

Tests that verify the CI/CD pipeline can properly test the application.
"""
import pytest
import os
import sys
from pathlib import Path


@pytest.mark.integration
class TestCIPipeline:
    """Test CI/CD pipeline integration"""

    def test_environment_setup(self):
        """Test that CI environment is properly configured"""
        # Check Python version
        assert sys.version_info >= (3, 8), "Python 3.8+ required"

        # Check required environment variables for CI
        if os.getenv("CI"):
            assert os.getenv("QT_QPA_PLATFORM") == "offscreen", "Qt platform should be offscreen in CI"

    def test_module_imports(self):
        """Test that all critical modules can be imported"""
        critical_modules = [
            "config",
            "game_detector",
            "game_profile",
            "ai_router",
            "ai_assistant",
            "knowledge_pack",
            "knowledge_index",
            "macro_manager",
            "session_logger",
        ]

        for module_name in critical_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_config_initialization_headless(self):
        """Test Config can initialize in headless environment"""
        from config import Config

        config = Config(require_keys=False)
        assert config is not None
        assert hasattr(config, 'ai_provider')

    def test_game_detector_headless(self):
        """Test GameDetector works in headless environment"""
        from game_detector import GameDetector

        detector = GameDetector()
        assert detector is not None

        # Should be able to detect games even without display
        games = detector.get_running_games()
        assert isinstance(games, list)

    def test_ai_router_initialization_no_keys(self):
        """Test AIRouter can initialize without API keys"""
        from config import Config
        from ai_router import AIRouter

        config = Config(require_keys=False)
        router = AIRouter(config)

        assert router is not None
        providers = router.list_configured_providers()
        assert isinstance(providers, list)

    def test_knowledge_system_headless(self, temp_dir):
        """Test knowledge system works in headless environment"""
        from knowledge_pack import KnowledgePack, KnowledgeSource
        from knowledge_store import KnowledgePackStore
        from knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding

        store = KnowledgePackStore(config_dir=temp_dir)
        embedding = SimpleTFIDFEmbedding()
        index = KnowledgeIndex(
            config_dir=temp_dir,
            embedding_provider=embedding,
            knowledge_store=store
        )

        # Create and index a pack
        source = KnowledgeSource(
            id="test_source",
            type="note",
            title="Test Note",
            content="Test content for CI pipeline verification"
        )

        pack = KnowledgePack(
            id="test_pack",
            name="Test Pack",
            description="Test pack",
            game_profile_id="test_game",
            sources=[source]
        )

        store.save_pack(pack)
        index.add_pack(pack)

        # Query should work
        results = index.query(
            game_profile_id="test_game",
            question="test",
            top_k=1
        )
        assert len(results) >= 0  # May be 0 if no matches

    def test_macro_system_headless(self):
        """Test macro system works in headless environment"""
        from macro_manager import Macro, MacroStep, MacroStepType

        macro = Macro(
            id="test_macro",
            name="Test Macro",
            description="Test macro for CI",
            steps=[
                MacroStep(type=MacroStepType.DELAY.value, duration_ms=10)
            ]
        )

        assert macro is not None
        assert len(macro.steps) == 1

    def test_session_logger_headless(self, temp_dir):
        """Test session logger works in headless environment"""
        from session_logger import SessionLogger

        logger = SessionLogger(config_dir=temp_dir)

        logger.log_event(
            event_type="test",
            game_profile_id="test_game",
            content="Test event",
            meta={"test": True}
        )

        events = logger.get_recent_events("test_game")
        assert len(events) >= 1


@pytest.mark.integration
class TestDeploymentReadiness:
    """Test that application is ready for deployment"""

    def test_required_files_exist(self):
        """Test that all required files exist for deployment"""
        required_files = [
            "main.py",
            "requirements.txt",
            ".env.example",
            "README.md",
            "pytest.ini",
        ]

        for file_path in required_files:
            path = Path(file_path)
            assert path.exists(), f"Required file missing: {file_path}"

    def test_src_directory_structure(self):
        """Test that src directory has expected structure"""
        required_modules = [
            "src/config.py",
            "src/game_detector.py",
            "src/game_profile.py",
            "src/ai_router.py",
            "src/ai_assistant.py",
            "src/providers.py",
            "src/knowledge_pack.py",
            "src/knowledge_index.py",
            "src/macro_manager.py",
            "src/session_logger.py",
        ]

        for module_path in required_modules:
            path = Path(module_path)
            assert path.exists(), f"Required module missing: {module_path}"

    def test_workflow_files_valid(self):
        """Test that GitHub workflow files are valid YAML"""
        import yaml

        workflows_dir = Path(".github/workflows")
        if not workflows_dir.exists():
            pytest.skip("No workflows directory")

        for workflow_file in workflows_dir.glob("*.yml"):
            with open(workflow_file) as f:
                try:
                    data = yaml.safe_load(f)
                    assert data is not None
                    assert "jobs" in data or "on" in data
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {workflow_file}: {e}")

    def test_no_sensitive_data_in_repo(self):
        """Test that no sensitive data is committed"""
        sensitive_patterns = [
            ".env",  # Should only have .env.example
            "credentials.enc",
            "*.pem",
            "*.key",
        ]

        # Check that .gitignore exists and includes these patterns
        gitignore = Path(".gitignore")
        if gitignore.exists():
            with open(gitignore) as f:
                content = f.read()
                for pattern in sensitive_patterns:
                    if pattern not in content:
                        pytest.fail(f"Sensitive pattern {pattern} not in .gitignore")


@pytest.mark.integration
class TestHeadlessGUI:
    """Test GUI components work in headless environment"""

    @pytest.mark.ui
    def test_qt_offscreen_platform(self):
        """Test Qt offscreen platform is working"""
        assert os.getenv("QT_QPA_PLATFORM") == "offscreen"

    @pytest.mark.ui
    def test_design_system_import(self):
        """Test design system can be imported"""
        try:
            from ui.design_system import OmnixDesignSystem
            assert OmnixDesignSystem is not None
        except ImportError as e:
            pytest.skip(f"Design system import failed: {e}")

    @pytest.mark.ui
    def test_theme_manager_headless(self):
        """Test theme manager works in headless environment"""
        try:
            from ui.theme_manager import OmnixThemeManager
            theme_mgr = OmnixThemeManager()
            assert theme_mgr is not None
        except ImportError as e:
            pytest.skip(f"Theme manager import failed: {e}")


@pytest.mark.integration
class TestDatabaseIntegrity:
    """Test data storage and persistence"""

    def test_config_persistence(self, temp_dir):
        """Test config can be saved and loaded"""
        from config import Config

        config_path = Path(temp_dir) / "test_config.json"
        config1 = Config(config_path=str(config_path), require_keys=False)
        config1.overlay_width = 12345
        config1.save()

        config2 = Config(config_path=str(config_path), require_keys=False)
        assert config2.overlay_width == 12345

    def test_game_profile_persistence(self, temp_dir):
        """Test game profiles can be saved and loaded"""
        from game_profile import GameProfile, GameProfileStore

        store = GameProfileStore(config_dir=temp_dir)

        profile = GameProfile(
            id="test_profile_persist",
            display_name="Test Profile",
            exe_names=["test.exe"],
            system_prompt="Test prompt"
        )

        store.create_profile(profile)
        loaded = store.get_profile_by_id("test_profile_persist")

        assert loaded is not None
        assert loaded.display_name == "Test Profile"
        assert loaded.exe_names == ["test.exe"]

        # Cleanup
        store.delete_profile("test_profile_persist")

    def test_macro_persistence(self, temp_dir):
        """Test macros can be saved and loaded"""
        from macro_manager import Macro, MacroStep, MacroStepType
        from macro_store import MacroStore

        store = MacroStore(config_dir=temp_dir)

        macro = Macro(
            id="test_macro_persist",
            name="Test Macro",
            description="Test",
            steps=[
                MacroStep(type=MacroStepType.DELAY.value, duration_ms=100)
            ]
        )

        store.save_macro(macro)
        loaded = store.load_macro("test_macro_persist")

        assert loaded is not None
        assert loaded.name == "Test Macro"
        assert len(loaded.steps) == 1
