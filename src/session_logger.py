"""
Session Logger Module
Tracks user interactions and AI responses per game profile for coaching and recap
"""

import logging
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class SessionEvent:
    """
    Represents a single event in a gaming session

    Attributes:
        timestamp: When the event occurred
        event_type: Type of event ('question', 'answer', 'macro', 'knowledge_query', etc.)
        game_profile_id: Associated game profile
        content: Event content (question text, answer summary, etc.)
        meta: Additional metadata
    """
    timestamp: datetime
    event_type: str
    game_profile_id: str
    content: str
    meta: Dict = None

    def __post_init__(self):
        if self.meta is None:
            self.meta = {}

        # Convert string timestamp back to datetime if needed
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "SessionEvent":
        """Create from dictionary"""
        return cls(**data)


class SessionLogger:
    """
    Logs gaming session events for coaching and recap features
    """

    # Maximum events to keep in memory per game
    MAX_EVENTS_IN_MEMORY = 100

    # Maximum events to persist to disk per game
    MAX_EVENTS_ON_DISK = 500

    # Session timeout (if no events for this duration, consider it a new session)
    SESSION_TIMEOUT = timedelta(hours=2)

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize session logger

        Args:
            config_dir: Directory to store session logs (defaults to ~/.gaming_ai_assistant)
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.gaming_ai_assistant")

        self.config_dir = Path(config_dir)
        self.logs_dir = self.config_dir / "session_logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # In-memory event storage: {game_profile_id: deque of events}
        self.events: Dict[str, deque] = {}

        # Current session IDs: {game_profile_id: session_id}
        self.current_sessions: Dict[str, str] = {}

        # Last event timestamps: {game_profile_id: datetime}
        self.last_event_time: Dict[str, datetime] = {}

        logger.info(f"SessionLogger initialized at {self.logs_dir}")

    def _get_session_file(self, game_profile_id: str, session_id: str) -> Path:
        """Get the file path for a session log"""
        return self.logs_dir / f"{game_profile_id}_{session_id}.json"

    def _get_current_session_id(self, game_profile_id: str) -> str:
        """
        Get or create current session ID for a game

        Creates a new session if:
        - No previous session exists
        - Last event was more than SESSION_TIMEOUT ago
        """
        now = datetime.now()

        # Check if we should start a new session
        last_time = self.last_event_time.get(game_profile_id)
        if last_time is None or (now - last_time) > self.SESSION_TIMEOUT:
            # New session
            session_id = now.strftime("%Y%m%d_%H%M%S")
            self.current_sessions[game_profile_id] = session_id
            logger.info(f"Started new session for {game_profile_id}: {session_id}")
        else:
            # Continue existing session
            session_id = self.current_sessions.get(game_profile_id)
            if not session_id:
                # Shouldn't happen, but create one just in case
                session_id = now.strftime("%Y%m%d_%H%M%S")
                self.current_sessions[game_profile_id] = session_id

        self.last_event_time[game_profile_id] = now
        return session_id

    def log_event(
        self,
        game_profile_id: str,
        event_type: str,
        content: str,
        meta: Optional[Dict] = None
    ) -> None:
        """
        Log a session event

        Args:
            game_profile_id: Game profile ID
            event_type: Type of event ('question', 'answer', 'macro', etc.)
            content: Event content
            meta: Optional metadata
        """
        try:
            # Create event
            event = SessionEvent(
                timestamp=datetime.now(),
                event_type=event_type,
                game_profile_id=game_profile_id,
                content=content,
                meta=meta or {}
            )

            # Add to in-memory storage
            if game_profile_id not in self.events:
                self.events[game_profile_id] = deque(maxlen=self.MAX_EVENTS_IN_MEMORY)

            self.events[game_profile_id].append(event)

            # Get current session
            session_id = self._get_current_session_id(game_profile_id)

            # Persist to disk periodically (every 10 events)
            if len(self.events[game_profile_id]) % 10 == 0:
                self._save_session(game_profile_id, session_id)

            logger.debug(f"Logged {event_type} event for {game_profile_id}")

        except Exception as e:
            logger.error(f"Failed to log event: {e}", exc_info=True)

    def _save_session(self, game_profile_id: str, session_id: str) -> None:
        """Save current session to disk"""
        try:
            if game_profile_id not in self.events:
                return

            session_file = self._get_session_file(game_profile_id, session_id)

            # Convert events to dict
            events_data = [event.to_dict() for event in self.events[game_profile_id]]

            # Limit to MAX_EVENTS_ON_DISK
            if len(events_data) > self.MAX_EVENTS_ON_DISK:
                events_data = events_data[-self.MAX_EVENTS_ON_DISK:]

            # Save to file
            with open(session_file, 'w') as f:
                json.dump({
                    'game_profile_id': game_profile_id,
                    'session_id': session_id,
                    'events': events_data
                }, f, indent=2)

            logger.debug(f"Saved session {session_id} for {game_profile_id}")

        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def _load_session(self, game_profile_id: str, session_id: str) -> List[SessionEvent]:
        """Load a session from disk"""
        try:
            session_file = self._get_session_file(game_profile_id, session_id)

            if not session_file.exists():
                return []

            with open(session_file, 'r') as f:
                data = json.load(f)

            events = [SessionEvent.from_dict(e) for e in data.get('events', [])]
            logger.debug(f"Loaded {len(events)} events for session {session_id}")
            return events

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return []

    def get_current_session_events(self, game_profile_id: str) -> List[SessionEvent]:
        """
        Get events from the current session

        Args:
            game_profile_id: Game profile ID

        Returns:
            List of events in chronological order
        """
        if game_profile_id not in self.events:
            return []

        return list(self.events[game_profile_id])

    def get_recent_events(self, game_profile_id: str, limit: int = 50) -> List[SessionEvent]:
        """
        Get recent events across all sessions

        Args:
            game_profile_id: Game profile ID
            limit: Maximum number of events to return

        Returns:
            List of recent events in chronological order
        """
        # Get current session events
        events = self.get_current_session_events(game_profile_id)

        # If we need more, load from recent session files
        if len(events) < limit:
            session_files = sorted(
                self.logs_dir.glob(f"{game_profile_id}_*.json"),
                reverse=True  # Most recent first
            )

            for session_file in session_files[:5]:  # Check last 5 sessions
                session_id = session_file.stem.split('_', 1)[1]  # Extract session_id
                if session_id not in self.current_sessions.values():
                    # Load historical session
                    historical_events = self._load_session(game_profile_id, session_id)
                    events = historical_events + events

                if len(events) >= limit:
                    break

        # Return most recent events up to limit
        return events[-limit:] if len(events) > limit else events

    def get_session_summary(self, game_profile_id: str) -> Dict:
        """
        Get a summary of the current session

        Args:
            game_profile_id: Game profile ID

        Returns:
            Dictionary with session statistics
        """
        events = self.get_current_session_events(game_profile_id)

        if not events:
            return {
                'total_events': 0,
                'session_id': None,
                'start_time': None,
                'duration_minutes': 0,
                'event_types': {}
            }

        # Count event types
        event_types = {}
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1

        # Calculate duration
        start_time = events[0].timestamp
        end_time = events[-1].timestamp
        duration = (end_time - start_time).total_seconds() / 60

        session_id = self.current_sessions.get(game_profile_id, 'unknown')

        return {
            'total_events': len(events),
            'session_id': session_id,
            'start_time': start_time.isoformat(),
            'duration_minutes': round(duration, 1),
            'event_types': event_types
        }

    def clear_session(self, game_profile_id: str) -> None:
        """
        Clear current session for a game (keeps disk logs)

        Args:
            game_profile_id: Game profile ID
        """
        if game_profile_id in self.events:
            # Save before clearing
            session_id = self.current_sessions.get(game_profile_id)
            if session_id:
                self._save_session(game_profile_id, session_id)

            # Clear memory
            del self.events[game_profile_id]
            if game_profile_id in self.current_sessions:
                del self.current_sessions[game_profile_id]

            logger.info(f"Cleared session for {game_profile_id}")

    def get_all_sessions(self, game_profile_id: str) -> List[str]:
        """
        Get all session IDs for a game profile

        Args:
            game_profile_id: Game profile ID

        Returns:
            List of session IDs (sorted by date, most recent first)
        """
        session_files = sorted(
            self.logs_dir.glob(f"{game_profile_id}_*.json"),
            reverse=True
        )

        session_ids = []
        for session_file in session_files:
            session_id = session_file.stem.split('_', 1)[1]
            session_ids.append(session_id)

        return session_ids


# Global session logger instance
_session_logger: Optional[SessionLogger] = None


def get_session_logger() -> SessionLogger:
    """Get or create the global session logger instance"""
    global _session_logger
    if _session_logger is None:
        _session_logger = SessionLogger()
    return _session_logger
