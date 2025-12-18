"""
Conversation Memory Module for GitaBae.

Manages conversation history and context for more coherent, contextual responses.
Uses LangChain's message types for compatibility and future extensibility.

Design Principle: Keep recent messages in full, summarize older ones when needed.
This provides conversation awareness while managing token limits.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from .logger import get_logger

logger = get_logger("gitabae.memory")


@dataclass
class ConversationManager:
    """
    Manages conversation context with a sliding window approach.

    Keeps the most recent messages in full and can generate a summary
    of the conversation for context-aware responses.
    """

    max_messages: int = 10  # Keep last N message pairs (20 messages total)
    messages: List[BaseMessage] = field(default_factory=list)

    def __post_init__(self):
        logger.info(f"ConversationManager initialized (max_messages={self.max_messages})")

    def add_exchange(self, user_input: str, ai_response: str) -> None:
        """
        Add a user-assistant exchange to memory.

        Args:
            user_input: The user's message
            ai_response: The assistant's response
        """
        self.messages.append(HumanMessage(content=user_input))
        self.messages.append(AIMessage(content=ai_response))

        # Trim if exceeds max (keep most recent)
        max_total = self.max_messages * 2
        if len(self.messages) > max_total:
            self.messages = self.messages[-max_total:]
            logger.debug(f"Trimmed memory to {len(self.messages)} messages")

        logger.debug(f"Added exchange (total: {len(self.messages)} messages)")

    def get_context_string(self) -> str:
        """
        Get conversation context as a formatted string for the LLM.

        Returns:
            Formatted string of conversation history
        """
        if not self.messages:
            return ""

        parts = []
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                parts.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                parts.append(f"GitaBae: {msg.content}")

        return "\n".join(parts)

    def get_summary(self) -> str:
        """
        Get a brief summary of the conversation topics discussed.

        Returns:
            Summary string describing main topics
        """
        if not self.messages:
            return "No previous conversation."

        # Extract key topics from user messages
        user_messages = [m.content for m in self.messages if isinstance(m, HumanMessage)]

        if len(user_messages) <= 2:
            return f"User has asked about: {user_messages[-1][:100]}..."

        return f"Conversation with {len(user_messages)} exchanges. Recent topic: {user_messages[-1][:100]}..."

    def get_message_count(self) -> int:
        """Get the number of messages in memory."""
        return len(self.messages)

    def get_exchange_count(self) -> int:
        """Get the number of user-assistant exchanges."""
        return len(self.messages) // 2

    def clear(self) -> None:
        """Clear all conversation memory."""
        self.messages = []
        logger.info("Conversation memory cleared")

    def get_recent_messages(self, n: int = 3) -> List[Dict[str, str]]:
        """
        Get the n most recent exchanges as a list of dicts.

        Args:
            n: Number of recent exchanges to return

        Returns:
            List of dicts with 'role' and 'content' keys
        """
        recent = []
        for msg in self.messages[-(n*2):]:
            if isinstance(msg, HumanMessage):
                recent.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                recent.append({"role": "assistant", "content": msg.content})

        return recent

    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """
        Get all messages in OpenAI chat format.

        Returns:
            List of dicts with 'role' and 'content' keys
        """
        result = []
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                result.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                result.append({"role": "assistant", "content": msg.content})
        return result

    def has_context(self) -> bool:
        """Check if there's any conversation history."""
        return len(self.messages) > 0


def create_conversation_manager(max_messages: int = 10) -> ConversationManager:
    """
    Factory function to create a ConversationManager.

    Args:
        max_messages: Max message pairs to keep in memory

    Returns:
        Configured ConversationManager instance
    """
    return ConversationManager(max_messages=max_messages)
