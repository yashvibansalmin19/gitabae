"""
Response Generator Module for GitaBae.

Uses LLM to generate compassionate, wisdom-based responses.
Integrates retrieval, safety checking, and response generation.
"""

from typing import List, Optional

from .config import get_openai_client, Config
from .constants import (
    SYSTEM_PROMPT,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    BLOCKED_INPUT_MESSAGE,
    NO_VERSES_MESSAGE,
    GENERATION_ERROR_MESSAGE,
    CONNECTION_ERROR_MESSAGE,
    APP_NAME,
)
from .logger import get_generator_logger
from .retriever import Retriever, RetrievedVerse
from .safety import SafetyChecker, SafetyStatus

logger = get_generator_logger()


class ResponseGenerator:
    """Generates conversational responses using retrieved Gita wisdom."""

    def __init__(self):
        """Initialize the response generator with all dependencies."""
        Config.load()
        self.client = get_openai_client()
        self.retriever = Retriever()
        self.safety = SafetyChecker()
        logger.info("ResponseGenerator initialized")

    def generate(
        self,
        user_query: str,
        conversation_history: Optional[List[dict]] = None,
        top_k: int = 2,
        min_score: float = 0.5
    ) -> dict:
        """
        Generate a response to user's query.

        Args:
            user_query: User's question or concern
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            top_k: Number of verses to retrieve
            min_score: Minimum relevance score

        Returns:
            Dict with 'response', 'verses', 'success', and 'safety_status' keys
        """
        if conversation_history is None:
            conversation_history = []

        logger.info(f"Generating response for query: {user_query[:50]}...")

        # Sanitize input
        sanitized_query = self.safety.sanitize_input(user_query)

        # Check input safety
        safety_result = self.safety.check_input(sanitized_query)

        if safety_result.status == SafetyStatus.BLOCKED:
            logger.warning(f"Query blocked: {safety_result.reason}")
            return {
                "response": BLOCKED_INPUT_MESSAGE,
                "verses": [],
                "success": False,
                "safety_status": "blocked"
            }

        if safety_result.status == SafetyStatus.REDIRECT:
            logger.info(f"Query redirected: {safety_result.reason}")
            return {
                "response": safety_result.redirect_message,
                "verses": [],
                "success": True,
                "safety_status": "redirected",
                "redirect_reason": safety_result.reason
            }

        # Retrieve relevant verses
        verses = self.retriever.retrieve(sanitized_query, top_k=top_k, min_score=min_score)
        logger.info(f"Retrieved {len(verses)} verses")

        if not verses:
            logger.info("No relevant verses found")
            return {
                "response": NO_VERSES_MESSAGE,
                "verses": [],
                "success": False,
                "safety_status": "safe"
            }

        # Build context from verses
        context = self._build_context(verses)

        # Generate response using LLM with conversation history
        response = self._call_llm(sanitized_query, context, conversation_history)

        # Check output safety
        output_safety = self.safety.check_output(response)
        if output_safety.status == SafetyStatus.BLOCKED:
            logger.warning("Generated response blocked by safety check")
            response = GENERATION_ERROR_MESSAGE

        logger.info("Response generated successfully")
        return {
            "response": response,
            "verses": verses,
            "success": True,
            "safety_status": "safe"
        }

    def _build_context(self, verses: List[RetrievedVerse]) -> str:
        """Build context string from retrieved verses."""
        context_parts = []

        for i, verse in enumerate(verses, 1):
            context_parts.append(f"""
Verse {i} (Chapter {verse.chapter}, Verse {verse.verse}):
Translation: {verse.translation}
Commentary: {verse.commentary[:600]}
Themes: {', '.join(verse.tags)}
""")

        return "\n".join(context_parts)

    def _call_llm(
        self,
        user_query: str,
        context: str,
        conversation_history: Optional[List[dict]] = None
    ) -> str:
        """Call LLM to generate response with conversation context."""
        if conversation_history is None:
            conversation_history = []

        # Build messages array with conversation history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add recent conversation history (last 6 exchanges to keep context manageable)
        recent_history = conversation_history[-12:] if len(conversation_history) > 12 else conversation_history
        for msg in recent_history:
            if msg.get("role") in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Add current query with verse context
        current_message = f"""{user_query}

---
[Context for {APP_NAME} - relevant wisdom to draw from, express naturally:]
{context}"""

        messages.append({"role": "user", "content": current_message})

        try:
            logger.debug(f"Calling LLM with {len(messages)} messages")
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM call failed: {e}", exc_info=True)
            return f"{CONNECTION_ERROR_MESSAGE} (Error: {str(e)[:50]})"


def main():
    """Test the response generator."""
    print("=" * 60)
    print("GitaBae Response Generator Test")
    print("=" * 60)

    generator = ResponseGenerator()

    test_queries = [
        "I'm feeling anxious about my career choices",
        "How do I stop worrying about things I can't control?",
        "I feel stuck and don't know my purpose"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"User: {query}")
        print("=" * 60)

        result = generator.generate(query)
        print(f"\nGitaBae: {result['response']}")

        if result['verses']:
            print(f"\n📖 Based on: ", end="")
            refs = [f"Ch{v.chapter}:V{v.verse}" for v in result['verses']]
            print(", ".join(refs))


if __name__ == "__main__":
    main()
