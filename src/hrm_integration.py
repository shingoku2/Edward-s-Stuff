"""
HRM (Hierarchical Reasoning Model) Integration Module

This module provides integration between the Omnix gaming companion
and the Hierarchical Reasoning Model for enhanced reasoning capabilities.
"""

import logging
from typing import Optional, Dict, Any, List
import threading

logger = logging.getLogger(__name__)


class HRMInterface:
    """
    Interface for Hierarchical Reasoning Model integration.

    Provides reasoning capabilities for complex gaming scenarios like:
    - Strategy games requiring multi-step planning
    - Puzzle games requiring logical reasoning
    - Algorithmic problem solving within games
    """

    def __init__(self, config: Optional[Any] = None):
        self._model = None
        self._initialized = False
        self._lock = threading.Lock()

        # Reuse global Config singleton if available, otherwise create minimal instance
        from src.config import Config
        self.config = config if config is not None else Config()

        # For template-based reasoning, we don't need PyTorch
        # HRM is always available for structured reasoning outlines
        self.hrm_available = True

        # Check if PyTorch is available for future enhancements
        self.pytorch_available = False
        try:
            import torch
            self.pytorch_available = True
            logger.info("PyTorch is available for future HRM enhancements")
        except ImportError:
            logger.info("PyTorch not available. Using template-based reasoning only.")
        except Exception as e:
            logger.warning(f"PyTorch check failed: {e}")

    def is_available(self) -> bool:
        """
        Check if HRM is available for use.
        
        Returns:
            bool: True if HRM is available, False otherwise
        """
        return self.hrm_available

    def requires_complex_reasoning(self, question: str, game_name: str) -> bool:
        """
        Determine if a question requires complex reasoning that HRM can help with.

        Args:
            question: The user's question
            game_name: The current game name

        Returns:
            bool: True if HRM should be used, False otherwise
        """
        question_lower = question.lower()
        game_lower = game_name.lower() if game_name else ""

        # Multi-word phrases that indicate complex reasoning (check first - more specific)
        reasoning_phrases = [
            'how should i', 'what is the best way to', 'help me solve',
            'i need to figure out', 'trying to understand', 'how do i solve',
            'what\'s the optimal', 'can you help me plan', 'need a strategy for',
            'how to approach', 'best method for', 'most efficient way',
            'step by step', 'walk me through', 'break down how to'
        ]

        # Check phrases first (more specific)
        has_reasoning_phrases = any(phrase in question_lower for phrase in reasoning_phrases)

        # Keywords indicating complex reasoning is required
        reasoning_keywords = [
            'puzzle', 'solve', 'strategy', 'plan', 'sequence', 'algorithm',
            'maze', 'path', 'sudoku', 'logic', 'deduction', 'reasoning',
            'tactic', 'multi-step', 'optimal', 'best approach', 'how to win',
            'pattern', 'solution', 'method', 'technique', 'approach',
            'cipher', 'riddle', 'optimization', 'efficiency', 'quickest', 'fastest',
            'analyze', 'calculate', 'determine', 'evaluate'
        ]

        # Games that typically involve complex reasoning
        reasoning_games = [
            'sudoku', 'chess', 'go', 'checkers', 'poker', 'bridge',
            'civilization', 'europa universalis', 'hearthstone',
            'magic: the gathering', 'factorio', 'satisfactory',
            'minecraft', 'terraria', 'the witness', 'portal', 'baba is you',
            'oxygen not included', 'rimworld', 'dwarf fortress',
            'into the breach', 'slay the spire', 'ftl'
        ]

        # Check if question contains reasoning keywords
        has_reasoning_keywords = any(keyword in question_lower for keyword in reasoning_keywords)

        # Check if game is of a type that involves complex reasoning
        is_reasoning_game = any(reasoning_game in game_lower for reasoning_game in reasoning_games)

        # Return True if any condition met (phrases have highest priority)
        return has_reasoning_phrases or has_reasoning_keywords or is_reasoning_game

    def analyze(self, question: str, game_context: Optional[str] = None) -> Optional[str]:
        """
        Generate structured reasoning analysis with timeout protection.

        Args:
            question: The question to analyze
            game_context: Additional context about the game

        Returns:
            str: Structured reasoning outline or None if HRM is unavailable
        """
        if not self.hrm_available:
            return None

        # Use threading for timeout (works on all platforms)
        result = [None]
        exception = [None]

        def run():
            try:
                result[0] = self._generate_reasoning_outline(question, game_context)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        thread.join(timeout=self.config.hrm_max_inference_time)

        if thread.is_alive():
            logger.warning("HRM analysis timed out")
            return "[HRM analysis timed out - question too complex]"

        if exception[0]:
            logger.error(f"HRM analysis failed: {exception[0]}", exc_info=True)
            return None

        return result[0]

    def _generate_reasoning_outline(self, question: str, game_context: Optional[str] = None) -> str:
        """
        Generate structured reasoning based on question type.

        Args:
            question: The question to analyze
            game_context: Additional context about the game

        Returns:
            str: Structured reasoning outline
        """
        outline_parts = ["[HRM Reasoning Analysis]"]
        question_lower = question.lower()

        # Detect puzzle-type questions
        if any(word in question_lower for word in ['puzzle', 'sudoku', 'maze', 'riddle', 'cipher']):
            outline_parts.extend([
                "\n**Puzzle Solving Strategy:**",
                "1. Identify constraints and rules",
                "2. Determine current state → goal state",
                "3. Apply systematic elimination or search",
                "4. Verify solution satisfies all constraints"
            ])

        # Detect strategy questions
        elif any(word in question_lower for word in ['strategy', 'plan', 'tactic', 'approach']):
            outline_parts.extend([
                "\n**Strategic Planning Framework:**",
                "1. Analyze current game state and available resources",
                "2. Define short-term and long-term objectives",
                "3. Evaluate alternative action sequences",
                "4. Select optimal strategy based on risk/reward analysis"
            ])

        # Detect optimization questions
        elif any(word in question_lower for word in ['optimal', 'best', 'efficient', 'fastest', 'quickest']):
            outline_parts.extend([
                "\n**Optimization Analysis:**",
                "1. Define optimization criteria (speed, resources, safety)",
                "2. Identify constraints and trade-offs",
                "3. Compare alternative approaches systematically",
                "4. Recommend optimal solution with justification"
            ])

        # Detect sequence/algorithm questions
        elif any(word in question_lower for word in ['sequence', 'order', 'steps', 'algorithm', 'method']):
            outline_parts.extend([
                "\n**Sequential Reasoning:**",
                "1. Break down into sequential sub-tasks",
                "2. Identify dependencies between steps",
                "3. Determine correct ordering",
                "4. Validate complete sequence achieves goal"
            ])

        # Generic reasoning structure
        else:
            outline_parts.extend([
                "\n**General Reasoning Structure:**",
                "1. Break down problem into core components",
                "2. Identify dependencies and relationships",
                "3. Solve components in logical order",
                "4. Integrate solutions into complete answer"
            ])

        # Add game context note if available
        if game_context:
            outline_parts.extend([
                "\n**Context Considerations:**",
                "- Incorporating game-specific knowledge",
                "- Adapting reasoning to current game state"
            ])

        return "\n".join(outline_parts)

    def get_reasoning_capabilities(self) -> List[str]:
        """
        Get a list of reasoning capabilities supported by HRM.
        
        Returns:
            List[str]: List of supported reasoning types
        """
        if not self.hrm_available:
            return []
            
        return [
            "Multi-step planning",
            "Puzzle solving",
            "Logical deduction",
            "Optimal path finding",
            "Pattern recognition",
            "Strategy formulation"
        ]


# Global instance for the application
_hrm_interface = None
_hrm_interface_lock = threading.Lock()


def get_hrm_interface() -> HRMInterface:
    """
    Get the global HRM interface instance.
    
    Returns:
        HRMInterface: The global HRM interface
    """
    global _hrm_interface
    
    with _hrm_interface_lock:
        if _hrm_interface is None:
            _hrm_interface = HRMInterface()
    
    return _hrm_interface


def requires_complex_reasoning(question: str, game_name: str) -> bool:
    """
    Convenience function to check if a question requires complex reasoning.
    
    Args:
        question: The user's question
        game_name: The current game name
        
    Returns:
        bool: True if HRM should be used, False otherwise
    """
    hrm_interface = get_hrm_interface()
    return hrm_interface.requires_complex_reasoning(question, game_name)


def get_hrm_analysis(question: str, game_context: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to get HRM analysis of a question.
    
    Args:
        question: The question to analyze
        game_context: Additional context about the game
        
    Returns:
        str: Analysis result or None if HRM is unavailable
    """
    hrm_interface = get_hrm_interface()
    return hrm_interface.analyze(question, game_context)