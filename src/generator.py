"""
Response Generator Module for GitaBae.
Uses LLM to generate compassionate, wisdom-based responses.
"""

from .config import get_openai_client, Config
from .retriever import Retriever, RetrievedVerse
from .safety import SafetyChecker, SafetyStatus


SYSTEM_PROMPT = """You are GitaBae, a warm and wise friend who helps young professionals navigate life using insights from the Bhagavad Gita.

Your voice:
- Speak like a caring friend who happens to know ancient wisdom - not a guru or teacher
- Be conversational, genuine, and relatable
- Match the user's energy - if they're casual, be casual; if they're distressed, be gentle
- Use "I" and "you" naturally, like in a real conversation
- It's okay to be brief when that's what's needed

How to respond:
- Start by connecting with what they shared (but don't over-acknowledge or be formulaic)
- Weave in Gita wisdom naturally - don't quote formally, paraphrase in modern language
- Share the insight as if you're telling them something that helped you personally
- Give ONE practical suggestion they can actually do today
- Keep it real - you can admit when life is genuinely hard

Vary your style:
- Sometimes ask a reflective question back
- Sometimes share a brief personal-style insight
- Sometimes just offer comfort without advice
- Don't always follow the same structure

Length: Match the depth of their question. Quick worries get quick comfort. Deep questions get thoughtful responses. Usually 100-200 words.

Important: Draw from the provided verses but express ideas in your own words. Never say "the Gita says" or quote formally unless it adds value."""


class ResponseGenerator:
    """Generates conversational responses using retrieved Gita wisdom."""

    def __init__(self):
        Config.load()
        self.client = get_openai_client()
        self.retriever = Retriever()
        self.safety = SafetyChecker()

    def generate(
        self,
        user_query: str,
        conversation_history: list = None,
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

        # Sanitize input
        sanitized_query = self.safety.sanitize_input(user_query)

        # Check input safety
        safety_result = self.safety.check_input(sanitized_query)

        if safety_result.status == SafetyStatus.BLOCKED:
            return {
                "response": "I'm not able to help with that request. Let's talk about something else - perhaps what's really troubling you?",
                "verses": [],
                "success": False,
                "safety_status": "blocked"
            }

        if safety_result.status == SafetyStatus.REDIRECT:
            return {
                "response": safety_result.redirect_message,
                "verses": [],
                "success": True,
                "safety_status": "redirected",
                "redirect_reason": safety_result.reason
            }

        # Retrieve relevant verses
        verses = self.retriever.retrieve(sanitized_query, top_k=top_k, min_score=min_score)

        if not verses:
            return {
                "response": "Hmm, I'm not finding a verse that speaks directly to this, but I'm here to listen. Could you tell me more about what's going on? Sometimes just talking it through helps.",
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
            response = "I apologize, but I wasn't able to generate an appropriate response. Could you rephrase your question?"

        return {
            "response": response,
            "verses": verses,
            "success": True,
            "safety_status": "safe"
        }

    def _build_context(self, verses: list[RetrievedVerse]) -> str:
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

    def _call_llm(self, user_query: str, context: str, conversation_history: list = None) -> str:
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
[Context for GitaBae - relevant wisdom to draw from, express naturally:]
{context}"""

        messages.append({"role": "user", "content": current_message})

        try:
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=0.8,  # Slightly higher for more varied responses
                max_tokens=400
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I'm having trouble connecting right now. Please try again. (Error: {str(e)[:50]})"


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
