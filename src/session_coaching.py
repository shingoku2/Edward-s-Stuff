"""
Session Coaching Module
Provides AI-powered session recaps and coaching based on session logs
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from session_logger import SessionLogger, SessionEvent, get_session_logger
from ai_router import get_router, AIRouter
from config import Config

logger = logging.getLogger(__name__)


class SessionCoach:
    """
    Provides coaching and session recap features using AI
    """

    def __init__(
        self,
        session_logger: Optional[SessionLogger] = None,
        config: Optional[Config] = None
    ):
        """
        Initialize session coach

        Args:
            session_logger: SessionLogger instance (uses global if None)
            config: Config instance (creates new if None)
        """
        self.session_logger = session_logger or get_session_logger()
        self.config = config or Config()
        self.router = get_router(self.config)

        logger.info("SessionCoach initialized")

    def _format_events_for_recap(self, events: List[SessionEvent]) -> str:
        """
        Format session events into a readable summary for the AI

        Args:
            events: List of session events

        Returns:
            Formatted text summary
        """
        if not events:
            return "No events in this session."

        lines = []
        lines.append(f"Session started at: {events[0].timestamp.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Total events: {len(events)}\n")

        # Group by event type
        questions = []
        answers = []
        macros = []
        knowledge_queries = []

        for event in events:
            if event.event_type == 'question':
                questions.append(event.content)
            elif event.event_type == 'answer':
                # Only keep summary/first 100 chars
                summary = event.content[:100] + "..." if len(event.content) > 100 else event.content
                answers.append(summary)
            elif event.event_type == 'macro':
                macros.append(event.content)
            elif event.event_type == 'knowledge_query':
                knowledge_queries.append(event.content)

        # Format sections
        if questions:
            lines.append("## Questions Asked:")
            for i, q in enumerate(questions[-10:], 1):  # Last 10 questions
                lines.append(f"{i}. {q}")
            lines.append("")

        if macros:
            lines.append("## Macros Used:")
            for m in set(macros[-5:]):  # Last 5 unique macros
                lines.append(f"- {m}")
            lines.append("")

        if knowledge_queries:
            lines.append("## Knowledge Pack Queries:")
            for kq in knowledge_queries[-5:]:  # Last 5 knowledge queries
                lines.append(f"- {kq}")
            lines.append("")

        return "\n".join(lines)

    def generate_session_recap(
        self,
        game_profile_id: str,
        game_name: Optional[str] = None
    ) -> str:
        """
        Generate an AI-powered session recap

        Args:
            game_profile_id: Game profile ID
            game_name: Optional game display name

        Returns:
            AI-generated recap text
        """
        try:
            # Get session events
            events = self.session_logger.get_current_session_events(game_profile_id)

            if not events:
                return "No session activity to recap yet. Start chatting to build your session history!"

            # Get session summary stats
            summary = self.session_logger.get_session_summary(game_profile_id)

            # Format events
            events_text = self._format_events_for_recap(events)

            # Create prompt for AI
            game_str = game_name or game_profile_id
            prompt = f"""You are a gaming coach providing a session recap for {game_str}.

Session Statistics:
- Duration: {summary['duration_minutes']} minutes
- Total interactions: {summary['total_events']}

Session Activity:
{events_text}

Please provide a concise session recap that includes:
1. **Summary**: What the user worked on this session (2-3 sentences)
2. **Key Insights**: Main topics/builds/strategies discussed (bullet points)
3. **Next Steps**: 2-3 concrete suggestions for what to focus on next

Keep the tone friendly and encouraging. Format the response with clear sections."""

            # Call AI
            response = self.router.generate_response(
                prompt=prompt,
                provider=self.config.ai_provider,
                system_prompt="You are a helpful gaming coach providing session recaps and next-step suggestions.",
                conversation_history=[]
            )

            logger.info(f"Generated session recap for {game_profile_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to generate session recap: {e}", exc_info=True)
            return f"Failed to generate session recap: {str(e)}"

    def ask_coach(
        self,
        game_profile_id: str,
        question: str,
        game_name: Optional[str] = None
    ) -> str:
        """
        Ask the coach a question with session history context

        Args:
            game_profile_id: Game profile ID
            question: User's question
            game_name: Optional game display name

        Returns:
            AI-generated coaching response
        """
        try:
            # Get recent session events for context
            events = self.session_logger.get_recent_events(game_profile_id, limit=30)

            # Format session context
            context_lines = []
            if events:
                context_lines.append("Recent session activity:")
                for event in events[-10:]:  # Last 10 events
                    if event.event_type == 'question':
                        context_lines.append(f"- User asked: {event.content}")

            context = "\n".join(context_lines) if context_lines else "No prior session context."

            # Create prompt
            game_str = game_name or game_profile_id
            prompt = f"""You are a gaming coach for {game_str}.

{context}

User's question: {question}

Please provide helpful coaching advice based on their question and session history.
Focus on:
- Progress tracking
- Next steps and goals
- Build/strategy suggestions
- Learning resources if relevant

Keep the response concise and actionable."""

            # Call AI
            response = self.router.generate_response(
                prompt=prompt,
                provider=self.config.ai_provider,
                system_prompt="You are a helpful gaming coach focused on progress tracking and improvement.",
                conversation_history=[]
            )

            logger.info(f"Answered coach question for {game_profile_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to answer coach question: {e}", exc_info=True)
            return f"Failed to get coaching response: {str(e)}"

    def get_progress_summary(
        self,
        game_profile_id: str,
        game_name: Optional[str] = None,
        days: int = 7
    ) -> str:
        """
        Generate a progress summary over multiple sessions

        Args:
            game_profile_id: Game profile ID
            game_name: Optional game display name
            days: Number of days to look back

        Returns:
            AI-generated progress summary
        """
        try:
            # Get all recent events
            events = self.session_logger.get_recent_events(game_profile_id, limit=100)

            if not events:
                return "No session history available yet."

            # Filter by date range
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_events = [e for e in events if e.timestamp >= cutoff_date]

            if not recent_events:
                return f"No session activity in the last {days} days."

            # Count sessions (approximate by gaps)
            session_count = 1
            for i in range(1, len(recent_events)):
                time_gap = recent_events[i].timestamp - recent_events[i-1].timestamp
                if time_gap.total_seconds() > 7200:  # 2 hour gap = new session
                    session_count += 1

            # Format for AI
            events_text = self._format_events_for_recap(recent_events)

            game_str = game_name or game_profile_id
            prompt = f"""You are a gaming coach reviewing progress for {game_str}.

Activity over the last {days} days:
- Sessions played: {session_count}
- Total interactions: {len(recent_events)}

{events_text}

Please provide a progress summary that includes:
1. **Overall Progress**: What the user has been working on
2. **Patterns**: Any recurring themes or focus areas
3. **Achievements**: Positive progress or breakthroughs
4. **Recommendations**: What to focus on moving forward

Keep it encouraging and constructive."""

            # Call AI
            response = self.router.generate_response(
                prompt=prompt,
                provider=self.config.ai_provider,
                system_prompt="You are a supportive gaming coach analyzing player progress.",
                conversation_history=[]
            )

            logger.info(f"Generated progress summary for {game_profile_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to generate progress summary: {e}", exc_info=True)
            return f"Failed to generate progress summary: {str(e)}"


# Global session coach instance
_session_coach: Optional[SessionCoach] = None


def get_session_coach(config: Optional[Config] = None) -> SessionCoach:
    """Get or create the global session coach instance"""
    global _session_coach
    if _session_coach is None:
        _session_coach = SessionCoach(config=config)
    return _session_coach
