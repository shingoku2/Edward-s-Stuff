"""
Integration tests for AI components

Tests integration between AI router, assistant, and providers.
"""
import pytest
import os


@pytest.mark.integration
class TestAIIntegration:
    """Test AI component integration"""

    def test_router_initialization(self):
        """Test AIRouter initialization with Config"""
        from config import Config
        from ai_router import AIRouter

        config = Config(require_keys=False)
        router = AIRouter(config)

        assert router is not None

    def test_list_configured_providers(self):
        """Test listing configured providers"""
        from config import Config
        from ai_router import AIRouter

        config = Config(require_keys=False)
        router = AIRouter(config)

        providers = router.list_configured_providers()
        assert isinstance(providers, list)

    def test_get_provider_status(self):
        """Test getting provider status"""
        from config import Config
        from ai_router import AIRouter

        config = Config(require_keys=False)
        router = AIRouter(config)

        for provider_name in ["anthropic", "openai", "gemini"]:
            status = router.get_provider_status(provider_name)
            assert isinstance(status, dict)
            assert "configured" in status

    @pytest.mark.skip_ci
    @pytest.mark.requires_api_key
    def test_assistant_with_router(self):
        """Test AIAssistant using AIRouter"""
        from ai_assistant import AIAssistant

        if not any([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_API_KEY")
        ]):
            pytest.skip("No API keys configured")

        try:
            assistant = AIAssistant()
            assert assistant is not None
        except ValueError:
            pytest.skip("No API keys configured")


@pytest.mark.integration
class TestGameIntegration:
    """Test game detection and profile integration"""

    def test_game_detection_with_profiles(self):
        """Test game detection integrating with profiles"""
        from game_detector import GameDetector
        from game_profile import GameProfileStore

        detector = GameDetector()
        store = GameProfileStore()

        # Detect any running game
        game = detector.detect_running_game()

        if game:
            # Try to get profile for detected game
            profile = store.get_profile_by_executable(game['name'])
            # Should at least get generic profile
            assert profile is not None

    def test_custom_profile_resolution(self):
        """Test custom profile can be resolved"""
        from game_profile import GameProfileStore, GameProfile

        store = GameProfileStore()

        # Create custom profile
        profile = GameProfile(
            id="integration_test_game",
            display_name="Integration Test Game",
            exe_names=["integration_test.exe"],
            system_prompt="Custom AI behavior"
        )

        # Clean up if exists
        if store.get_profile_by_id("integration_test_game"):
            store.delete_profile("integration_test_game")

        # Create it
        store.create_profile(profile)

        # Resolve by executable
        resolved = store.get_profile_by_executable("integration_test.exe")
        assert resolved is not None
        assert resolved.id == "integration_test_game"

        # Cleanup
        store.delete_profile("integration_test_game")


@pytest.mark.integration
class TestKnowledgeIntegration:
    """Test knowledge system integration"""

    def test_pack_storage_and_indexing(self, temp_dir):
        """Test knowledge pack storage and indexing together"""
        from knowledge_pack import KnowledgePack, KnowledgeSource
        from knowledge_store import KnowledgePackStore
        from knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding

        # Create store and index (must use same store instance)
        store = KnowledgePackStore(config_dir=temp_dir)
        embedding = SimpleTFIDFEmbedding()
        index = KnowledgeIndex(config_dir=temp_dir, embedding_provider=embedding, knowledge_store=store)

        # Create knowledge pack
        source = KnowledgeSource(
            id="s1",
            type="note",
            title="Boss Guide",
            content="To defeat the boss, use fire attacks and dodge left."
        )

        pack = KnowledgePack(
            id="pack1",
            name="Boss Tips",
            description="Tips for bosses",
            game_profile_id="test_game",
            sources=[source]
        )

        # Save to store
        assert store.save_pack(pack) is True

        # Index it
        index.add_pack(pack)

        # Query
        results = index.query(
            game_profile_id="test_game",
            question="How do I beat the boss?",
            top_k=3
        )

        # Should find relevant content
        assert len(results) > 0


@pytest.mark.integration
class TestFullWorkflow:
    """Test complete application workflows"""

    def test_config_to_router_workflow(self):
        """Test workflow from Config to AIRouter"""
        from config import Config
        from ai_router import AIRouter

        # Initialize config
        config = Config(require_keys=False)

        # Initialize router with config
        router = AIRouter(config)

        # Check providers
        providers = router.list_configured_providers()
        assert isinstance(providers, list)

    def test_game_detection_to_profile_workflow(self):
        """Test workflow from game detection to profile"""
        from game_detector import GameDetector
        from game_profile import GameProfileStore

        # Detect games
        detector = GameDetector()
        games = detector.get_running_games()

        # Get profiles
        store = GameProfileStore()

        if games:
            for game in games:
                profile = store.get_profile_by_executable(game['name'])
                # Should always get at least generic profile
                assert profile is not None
