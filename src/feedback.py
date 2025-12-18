"""
Feedback System for GitaBae.

Handles user feedback collection and storage with a clean abstraction.
Storage backend can be swapped without changing the rest of the app.

Design Principle: Dependency Inversion - high-level feedback logic
doesn't depend on low-level storage details.
"""

import json
import streamlit as st
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .logger import get_feedback_logger
from .constants import FEEDBACK_FILE

logger = get_feedback_logger()


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class FeedbackEntry:
    """A single feedback entry."""
    timestamp: str
    message_index: int
    rating: str  # "positive" or "negative"
    query: str
    response_preview: str

    @classmethod
    def create(
        cls,
        message_index: int,
        rating: str,
        query: str,
        response: str,
        max_query_len: int = 100,
        max_response_len: int = 150
    ) -> "FeedbackEntry":
        """
        Create a feedback entry with truncated text.

        Args:
            message_index: Index of the rated message
            rating: "positive" or "negative"
            query: User's query that prompted the response
            response: The assistant's response
            max_query_len: Max chars to store for query
            max_response_len: Max chars to store for response

        Returns:
            FeedbackEntry instance
        """
        return cls(
            timestamp=datetime.now().isoformat(),
            message_index=message_index,
            rating=rating,
            query=query[:max_query_len] if query else "",
            response_preview=response[:max_response_len] if response else "",
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


# =============================================================================
# STORAGE ABSTRACTION
# =============================================================================

class FeedbackStorage(ABC):
    """Abstract base class for feedback storage backends."""

    @abstractmethod
    def save(self, entry: FeedbackEntry) -> bool:
        """
        Save a feedback entry.

        Args:
            entry: FeedbackEntry to save

        Returns:
            True if saved successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> List[FeedbackEntry]:
        """
        Get all feedback entries.

        Returns:
            List of FeedbackEntry objects
        """
        pass

    @abstractmethod
    def count_by_rating(self) -> dict:
        """
        Count entries by rating.

        Returns:
            Dict with 'positive' and 'negative' counts
        """
        pass


class SessionFeedbackStorage(FeedbackStorage):
    """
    Session-only feedback storage (no persistence).
    Uses Streamlit session state.
    """

    SESSION_KEY = "feedback_log"

    def __init__(self):
        """Initialize session storage."""
        if self.SESSION_KEY not in st.session_state:
            st.session_state[self.SESSION_KEY] = []

    def save(self, entry: FeedbackEntry) -> bool:
        """Save to session state."""
        try:
            st.session_state[self.SESSION_KEY].append(entry.to_dict())
            logger.info(f"Feedback saved to session: {entry.rating}")
            return True
        except Exception as e:
            logger.error(f"Failed to save feedback to session: {e}")
            return False

    def get_all(self) -> List[FeedbackEntry]:
        """Get all from session state."""
        entries = []
        for data in st.session_state.get(self.SESSION_KEY, []):
            try:
                entries.append(FeedbackEntry(**data))
            except Exception:
                continue
        return entries

    def count_by_rating(self) -> dict:
        """Count by rating in session."""
        feedback_list = st.session_state.get(self.SESSION_KEY, [])
        return {
            "positive": sum(1 for f in feedback_list if f.get("rating") == "positive"),
            "negative": sum(1 for f in feedback_list if f.get("rating") == "negative"),
        }

    def clear(self) -> None:
        """Clear all session feedback."""
        st.session_state[self.SESSION_KEY] = []

    def is_rated(self, message_index: int) -> bool:
        """Check if a message has already been rated."""
        return any(
            f.get("message_index") == message_index
            for f in st.session_state.get(self.SESSION_KEY, [])
        )


class FileFeedbackStorage(FeedbackStorage):
    """
    File-based feedback storage (persistent).
    Stores feedback in a JSON file.
    """

    def __init__(self, file_path: Optional[Path] = None):
        """
        Initialize file storage.

        Args:
            file_path: Path to feedback JSON file (default: from constants)
        """
        self.file_path = file_path or FEEDBACK_FILE

    def save(self, entry: FeedbackEntry) -> bool:
        """Save to JSON file."""
        try:
            existing = self._load_from_file()
            existing.append(entry.to_dict())

            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)

            logger.info(f"Feedback saved to file: {entry.rating}")
            return True

        except Exception as e:
            logger.error(f"Failed to save feedback to file: {e}")
            return False

    def get_all(self) -> List[FeedbackEntry]:
        """Get all from file."""
        entries = []
        for data in self._load_from_file():
            try:
                entries.append(FeedbackEntry(**data))
            except Exception:
                continue
        return entries

    def count_by_rating(self) -> dict:
        """Count by rating in file."""
        data = self._load_from_file()
        return {
            "positive": sum(1 for f in data if f.get("rating") == "positive"),
            "negative": sum(1 for f in data if f.get("rating") == "negative"),
        }

    def _load_from_file(self) -> List[dict]:
        """Load existing feedback from file."""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load feedback file: {e}")
            return []


# =============================================================================
# COMBINED STORAGE (Session + File)
# =============================================================================

class CombinedFeedbackStorage(FeedbackStorage):
    """
    Combined storage that saves to both session and file.
    Session for quick access, file for persistence.
    """

    def __init__(self, file_path: Optional[Path] = None):
        """Initialize both storage backends."""
        self.session_storage = SessionFeedbackStorage()
        self.file_storage = FileFeedbackStorage(file_path)

    def save(self, entry: FeedbackEntry) -> bool:
        """Save to both session and file."""
        session_ok = self.session_storage.save(entry)
        file_ok = self.file_storage.save(entry)

        # Return True if at least session storage worked
        return session_ok

    def get_all(self) -> List[FeedbackEntry]:
        """Get from session (faster)."""
        return self.session_storage.get_all()

    def count_by_rating(self) -> dict:
        """Count from session (faster)."""
        return self.session_storage.count_by_rating()

    def is_rated(self, message_index: int) -> bool:
        """Check if rated (session)."""
        return self.session_storage.is_rated(message_index)

    def clear_session(self) -> None:
        """Clear session storage only."""
        self.session_storage.clear()


# =============================================================================
# DEFAULT INSTANCE
# =============================================================================

def get_feedback_storage() -> CombinedFeedbackStorage:
    """
    Get the default feedback storage instance.

    Returns:
        CombinedFeedbackStorage instance
    """
    return CombinedFeedbackStorage()
