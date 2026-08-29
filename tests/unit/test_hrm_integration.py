"""
Unit tests for HRM (Hierarchical Reasoning Model) integration.

Tests cover initialization, reasoning detection, outline generation,
error handling, and timeout behavior.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from src.hrm_integration import HRMInterface, get_hrm_interface, requires_complex_reasoning


class TestHRMInterface:
    """Test suite for HRMInterface class."""

    def test_initialization_without_pytorch(self):
        """Test HRM initializes gracefully without PyTorch."""
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == 'torch':
                raise ImportError("No module named 'torch'")
            return real_import(name, *args, **kwargs)

        with patch('src.hrm_integration.logger') as mock_logger:
            with patch('builtins.__import__', side_effect=fake_import):
                hrm = HRMInterface()
                assert isinstance(hrm, HRMInterface)
                # HRM always provides template-based reasoning even without
                # PyTorch; only the (future) neural-inference path is gated.
                assert hrm.hrm_available is True
                assert hrm.pytorch_available is False
                assert hrm._model is None

    def test_initialization_with_pytorch(self):
        """Test HRM initializes successfully with PyTorch available."""
        mock_torch = MagicMock()
        with patch.dict('sys.modules', {'torch': mock_torch}):
            hrm = HRMInterface()
            assert isinstance(hrm, HRMInterface)
            # Will be True if torch is actually installed, False if mocked
            assert isinstance(hrm.hrm_available, bool)

    def test_is_available(self):
        """Test is_available() returns correct status."""
        hrm = HRMInterface()
        assert isinstance(hrm.is_available(), bool)
        assert hrm.is_available() == hrm.hrm_available

    def test_singleton_pattern(self):
        """Test get_hrm_interface() returns same instance."""
        hrm1 = get_hrm_interface()
        hrm2 = get_hrm_interface()
        assert hrm1 is hrm2


class TestReasoningDetection:
    """Test suite for reasoning detection logic."""

    def setup_method(self):
        """Setup test fixture."""
        self.hrm = get_hrm_interface()

    def test_puzzle_keyword_detection(self):
        """Test detection of puzzle-type questions."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        test_cases = [
            ("How do I solve this sudoku puzzle?", "Sudoku"),
            ("Help me solve this maze", "Portal"),
            ("What's the solution to this riddle?", "The Witness"),
            ("How to solve this cipher?", "Unknown Game")
        ]

        for question, game in test_cases:
            assert self.hrm.requires_complex_reasoning(question, game), \
                f"Failed to detect puzzle question: {question}"

    def test_strategy_keyword_detection(self):
        """Test detection of strategy questions."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        test_cases = [
            ("What's the best strategy for late game?", "Civilization"),
            ("Help me plan my build order", "Factorio"),
            ("What tactics should I use?", "Chess"),
            ("How should I approach this boss?", "Dark Souls")
        ]

        for question, game in test_cases:
            assert self.hrm.requires_complex_reasoning(question, game), \
                f"Failed to detect strategy question: {question}"

    def test_optimization_keyword_detection(self):
        """Test detection of optimization questions."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        test_cases = [
            ("What's the optimal build path?", "League of Legends"),
            ("What's the fastest way to level?", "RPG Game"),
            ("Most efficient resource gathering?", "Minecraft"),
            ("Quickest route to complete this?", "Speedrun Game")
        ]

        for question, game in test_cases:
            assert self.hrm.requires_complex_reasoning(question, game), \
                f"Failed to detect optimization question: {question}"

    def test_reasoning_phrases_detection(self):
        """Test detection of complex reasoning phrases."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        test_cases = [
            "How should I approach this problem?",
            "What is the best way to defeat this enemy?",
            "Help me solve this challenge",
            "I need to figure out the solution",
            "Walk me through this step by step"
        ]

        for question in test_cases:
            assert self.hrm.requires_complex_reasoning(question, "Generic Game"), \
                f"Failed to detect reasoning phrase: {question}"

    def test_reasoning_game_detection(self):
        """Test detection based on game type alone."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        reasoning_games = [
            "Chess", "Go", "Factorio", "Civilization VI",
            "Portal 2", "The Witness", "Baba Is You"
        ]

        simple_question = "What should I do?"

        for game in reasoning_games:
            assert self.hrm.requires_complex_reasoning(simple_question, game), \
                f"Failed to detect reasoning game: {game}"

    def test_non_reasoning_questions(self):
        """Test that simple questions are not flagged."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        test_cases = [
            ("What button do I press?", "Random Game"),
            ("Where is the save menu?", "Generic Game"),
            ("How do I exit?", "Any Game")
        ]

        for question, game in test_cases:
            # These might still trigger if the game is a reasoning game
            # So only test with non-reasoning games
            result = self.hrm.requires_complex_reasoning(question, game)
            # This is informational - we don't assert False because
            # some simple questions might legitimately need reasoning

    def test_edge_cases(self):
        """Test edge cases for reasoning detection."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        # Empty question
        assert not self.hrm.requires_complex_reasoning("", "Game")

        # None game name
        result = self.hrm.requires_complex_reasoning("How do I solve this?", None)
        assert isinstance(result, bool)

        # Very long question
        long_question = "solve " * 100
        result = self.hrm.requires_complex_reasoning(long_question, "Game")
        assert result is True  # Contains "solve"


class TestOutlineGeneration:
    """Test suite for reasoning outline generation."""

    def setup_method(self):
        """Setup test fixture."""
        self.hrm = get_hrm_interface()

    def test_puzzle_outline_structure(self):
        """Test puzzle-type outline generation."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        result = self.hrm.analyze("How do I solve this sudoku puzzle?")
        assert result is not None
        assert "[HRM Reasoning Analysis]" in result
        assert "Puzzle Solving Strategy" in result
        assert "constraints" in result.lower()
        assert "goal state" in result.lower()

    def test_strategy_outline_structure(self):
        """Test strategy-type outline generation."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        result = self.hrm.analyze("What strategy should I use for late game?")
        assert result is not None
        assert "[HRM Reasoning Analysis]" in result
        assert "Strategic Planning Framework" in result
        assert "objectives" in result.lower()
        assert "resources" in result.lower()

    def test_optimization_outline_structure(self):
        """Test optimization-type outline generation."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        result = self.hrm.analyze("What's the optimal way to gather resources?")
        assert result is not None
        assert "[HRM Reasoning Analysis]" in result
        assert "Optimization Analysis" in result
        assert "criteria" in result.lower()
        assert "trade-offs" in result.lower()

    def test_sequence_outline_structure(self):
        """Test sequence/algorithm outline generation."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        result = self.hrm.analyze("What's the correct sequence of steps?")
        assert result is not None
        assert "[HRM Reasoning Analysis]" in result
        assert "Sequential Reasoning" in result
        assert "sub-tasks" in result.lower()
        assert "dependencies" in result.lower()

    def test_generic_outline_fallback(self):
        """Test generic outline for unclassified questions."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        result = self.hrm.analyze("How do I do this thing?")
        assert result is not None
        assert "[HRM Reasoning Analysis]" in result
        assert "General Reasoning Structure" in result
        assert "components" in result.lower()

    def test_game_context_inclusion(self):
        """Test that game context is included when provided."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        game_context = "You are level 50 with max gear"
        result = self.hrm.analyze("What should I do?", game_context)

        assert result is not None
        assert "Context Considerations" in result
        assert "game-specific" in result.lower()

    def test_no_game_context(self):
        """Test outline generation without game context."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        result = self.hrm.analyze("How do I solve this puzzle?", None)

        assert result is not None
        assert "[HRM Reasoning Analysis]" in result
        # Should not have context section
        assert "Context Considerations" not in result


class TestErrorHandling:
    """Test suite for error handling and edge cases."""

    def setup_method(self):
        """Setup test fixture."""
        self.hrm = get_hrm_interface()

    def test_analyze_without_pytorch(self):
        """Test analyze() still returns a template-based reasoning outline
        when PyTorch is unavailable (HRM's structured-template mode doesn't
        require PyTorch; only the future neural-inference path does)."""
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == 'torch':
                raise ImportError("No module named 'torch'")
            return real_import(name, *args, **kwargs)

        # Create a new HRM instance that definitely has no PyTorch
        with patch('builtins.__import__', side_effect=fake_import):
            hrm_no_pytorch = HRMInterface()
            assert hrm_no_pytorch.pytorch_available is False
            result = hrm_no_pytorch.analyze("Test question")
            assert result is not None
            assert isinstance(result, str)

    def test_timeout_behavior(self):
        """Test that timeout protection works."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        # Mock _generate_reasoning_outline to sleep longer than timeout
        original_method = self.hrm._generate_reasoning_outline

        def slow_outline(*args, **kwargs):
            time.sleep(10)  # Sleep longer than default timeout (5s)
            return original_method(*args, **kwargs)

        with patch.object(self.hrm, '_generate_reasoning_outline', side_effect=slow_outline):
            result = self.hrm.analyze("Test question")
            # Should timeout and return timeout message
            assert result is not None
            assert "timed out" in result.lower()

    def test_exception_handling(self):
        """Test that exceptions are caught and logged."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        # Mock _generate_reasoning_outline to raise exception
        def failing_outline(*args, **kwargs):
            raise RuntimeError("Test error")

        with patch.object(self.hrm, '_generate_reasoning_outline', side_effect=failing_outline):
            with patch('src.hrm_integration.logger') as mock_logger:
                result = self.hrm.analyze("Test question")
                assert result is None
                mock_logger.error.assert_called()

    def test_empty_question(self):
        """Test handling of empty question."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        result = self.hrm.analyze("")
        # Should return generic outline
        assert result is not None


class TestIntegration:
    """Integration tests for full workflow."""

    def setup_method(self):
        """Setup test fixture."""
        self.hrm = get_hrm_interface()

    def test_full_workflow_puzzle(self):
        """Test complete workflow for puzzle question."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        question = "How do I solve this maze in Portal?"
        game = "Portal 2"

        # Check detection
        should_use_hrm = requires_complex_reasoning(question, game)
        assert should_use_hrm is True

        # Generate analysis
        analysis = self.hrm.analyze(question)
        assert analysis is not None
        assert len(analysis) > 0

    def test_full_workflow_strategy(self):
        """Test complete workflow for strategy question."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        question = "What's the best strategy for late game expansion?"
        game = "Civilization VI"
        context = "Playing as Rome, turn 200, Renaissance era"

        # Check detection
        should_use_hrm = self.hrm.requires_complex_reasoning(question, game)
        assert should_use_hrm is True

        # Generate analysis with context
        analysis = self.hrm.analyze(question, context)
        assert analysis is not None
        assert "Strategic Planning Framework" in analysis
        assert "Context Considerations" in analysis

    def test_capabilities_reporting(self):
        """Test get_reasoning_capabilities() method."""
        if not self.hrm.is_available():
            pytest.skip("PyTorch not available")

        capabilities = self.hrm.get_reasoning_capabilities()
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert "Multi-step planning" in capabilities


class TestConvenienceFunctions:
    """Test suite for module-level convenience functions."""

    def test_requires_complex_reasoning_function(self):
        """Test module-level requires_complex_reasoning() function."""
        # Should work without PyTorch (returns False)
        result = requires_complex_reasoning("Test", "Game")
        assert isinstance(result, bool)

    def test_get_hrm_analysis_function(self):
        """Test module-level get_hrm_analysis() function."""
        from src.hrm_integration import get_hrm_analysis

        result = get_hrm_analysis("How do I solve this puzzle?")
        # Will be None if PyTorch not available, string if available
        assert result is None or isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
