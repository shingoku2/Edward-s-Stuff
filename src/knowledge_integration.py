"""
Knowledge Integration Module
Integrates knowledge packs, session logging, and coaching into the AI assistant
"""

import logging
from typing import Optional, List, Dict

from src.knowledge_pack import RetrievedChunk
from src.knowledge_index import get_knowledge_index, KnowledgeIndex
from src.knowledge_store import get_knowledge_pack_store, KnowledgePackStore
from session_logger import get_session_logger, SessionLogger

logger = logging.getLogger(__name__)


class KnowledgeIntegration:
    """
    Handles integration of knowledge packs and session logging with AI chat
    """

    def __init__(
        self,
        knowledge_index: Optional[KnowledgeIndex] = None,
        knowledge_store: Optional[KnowledgePackStore] = None,
        session_logger: Optional[SessionLogger] = None
    ):
        """
        Initialize knowledge integration

        Args:
            knowledge_index: KnowledgeIndex instance (uses global if None)
            knowledge_store: KnowledgePackStore instance (uses global if None)
            session_logger: SessionLogger instance (uses global if None)
        """
        self.knowledge_index = knowledge_index or get_knowledge_index()
        self.knowledge_store = knowledge_store or get_knowledge_pack_store()
        self.session_logger = session_logger or get_session_logger()

        logger.info("KnowledgeIntegration initialized")

    def should_use_knowledge_packs(self, game_profile_id: str, extra_settings: Dict) -> bool:
        """
        Check if knowledge packs should be used for a game profile

        Args:
            game_profile_id: Game profile ID
            extra_settings: Profile's extra_settings dict

        Returns:
            True if knowledge packs should be used
        """
        # Check profile setting
        use_knowledge = extra_settings.get('use_knowledge_packs', True)

        # Check if there are any enabled packs for this game
        enabled_packs = self.knowledge_store.get_enabled_packs_for_game(game_profile_id)

        return use_knowledge and len(enabled_packs) > 0

    def get_knowledge_context(
        self,
        game_profile_id: str,
        question: str,
        extra_settings: Dict
    ) -> Optional[str]:
        """
        Retrieve knowledge context for a question

        Args:
            game_profile_id: Game profile ID
            question: User's question
            extra_settings: Profile's extra_settings dict

        Returns:
            Formatted context string or None if no relevant context found
        """
        try:
            # Get context depth setting (default: 5)
            top_k = extra_settings.get('knowledge_context_depth', 5)

            # Query the index
            chunks = self.knowledge_index.query(
                game_profile_id=game_profile_id,
                question=question,
                top_k=top_k
            )

            if not chunks:
                logger.debug(f"No knowledge chunks found for question in {game_profile_id}")
                return None

            # Filter by minimum score threshold (0.3 out of 1.0)
            min_score = extra_settings.get('knowledge_min_score', 0.3)
            relevant_chunks = [c for c in chunks if c.score >= min_score]

            if not relevant_chunks:
                logger.debug(f"No chunks met score threshold {min_score}")
                return None

            # Format context
            context_parts = [
                "=== Knowledge Pack Context ===",
                "The following information from your knowledge packs may be relevant:\n"
            ]

            for i, chunk in enumerate(relevant_chunks, 1):
                source_title = chunk.meta.get('source_title', 'Unknown')
                pack_name = chunk.meta.get('pack_name', 'Unknown Pack')

                context_parts.append(f"[Source {i}: {source_title} from {pack_name}]")
                context_parts.append(chunk.text)
                context_parts.append("")  # Empty line

            context_parts.append("=== End Knowledge Pack Context ===\n")

            context = "\n".join(context_parts)
            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks for question")

            # Log the knowledge query event
            self.session_logger.log_event(
                game_profile_id=game_profile_id,
                event_type='knowledge_query',
                content=question,
                meta={'chunks_retrieved': len(relevant_chunks)}
            )

            return context

        except Exception as e:
            logger.error(f"Failed to get knowledge context: {e}", exc_info=True)
            return None

    def log_conversation(
        self,
        game_profile_id: str,
        question: str,
        answer: str
    ) -> None:
        """
        Log a conversation interaction

        Args:
            game_profile_id: Game profile ID
            question: User's question
            answer: AI's answer
        """
        try:
            # Log question
            self.session_logger.log_event(
                game_profile_id=game_profile_id,
                event_type='question',
                content=question
            )

            # Log answer (truncate to save space)
            answer_summary = answer[:200] + "..." if len(answer) > 200 else answer
            self.session_logger.log_event(
                game_profile_id=game_profile_id,
                event_type='answer',
                content=answer_summary
            )

        except Exception as e:
            logger.error(f"Failed to log conversation: {e}")

    def log_macro_execution(
        self,
        game_profile_id: str,
        macro_name: str
    ) -> None:
        """
        Log a macro execution

        Args:
            game_profile_id: Game profile ID
            macro_name: Name of executed macro
        """
        try:
            self.session_logger.log_event(
                game_profile_id=game_profile_id,
                event_type='macro',
                content=macro_name
            )
        except Exception as e:
            logger.error(f"Failed to log macro execution: {e}")

    def format_knowledge_instructions(self) -> str:
        """
        Get instructions for AI on how to use knowledge pack context

        Returns:
            Instruction text to prepend to prompts
        """
        return """
IMPORTANT: Knowledge Pack Context Instructions

If you see a "=== Knowledge Pack Context ===" section in the user's message:
1. Use this context to answer the question more accurately
2. If the context conflicts with your general knowledge, prefer the context from knowledge packs
3. Mention which sources you used when answering (e.g., "According to [Source 1]...")
4. If the context is not relevant to the question, answer normally using your general knowledge

If there is no knowledge pack context, answer using your general knowledge as usual.
"""

    def get_session_stats(self, game_profile_id: str) -> Dict:
        """
        Get session statistics for a game profile

        Args:
            game_profile_id: Game profile ID

        Returns:
            Dictionary with session statistics
        """
        return self.session_logger.get_session_summary(game_profile_id)


# Global knowledge integration instance
_knowledge_integration: Optional[KnowledgeIntegration] = None


def get_knowledge_integration() -> KnowledgeIntegration:
    """Get or create the global knowledge integration instance"""
    global _knowledge_integration
    if _knowledge_integration is None:
        _knowledge_integration = KnowledgeIntegration()
    return _knowledge_integration
