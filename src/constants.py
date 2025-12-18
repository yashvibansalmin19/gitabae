"""
Constants and configuration values for GitaBae.

Single source of truth for all text, messages, paths, and app configuration.
This file centralizes all "magic strings" to make the app easier to maintain.

Design Principle: If you need to change the app's voice, tone, or identity,
this is the only file you need to edit.
"""

from pathlib import Path

# =============================================================================
# APP IDENTITY
# =============================================================================
APP_NAME = "GitaBae"
APP_TAGLINE = "Navigate life with timeless wisdom"
APP_ICON = "🪷"
APP_URL = "https://gitabae.streamlit.app"

# =============================================================================
# PATHS
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FEEDBACK_FILE = DATA_DIR / "feedback_log.json"


def get_chapter_data_path(chapter: int) -> Path:
    """Get path to chapter data file."""
    return DATA_DIR / f"chapter_{chapter}_tagged.json"


def get_chapter_embeddings_path(chapter: int) -> Path:
    """Get path to chapter embeddings file."""
    return DATA_DIR / f"chapter_{chapter}_embeddings.json"


# =============================================================================
# USER-FACING MESSAGES
# =============================================================================
WELCOME_MESSAGE = f"""Hey! I'm {APP_NAME} - think of me as a friend who's really into ancient wisdom and loves talking about life's big (and small) questions.

Whether you're stressing about work, dealing with difficult people, feeling a bit lost, or just need someone to talk through something with - I'm here.

What's going on with you?"""

TYPING_INDICATOR = f"*{APP_ICON} {APP_NAME} is reflecting...*"
CHAT_PLACEHOLDER = "What's on your mind?"

NO_VERSES_MESSAGE = """Hmm, I'm not finding a verse that speaks directly to this, but I'm here to listen. Could you tell me more about what's going on? Sometimes just talking it through helps."""

CONNECTION_ERROR_MESSAGE = "I'm having trouble connecting right now. Please try again."

BLOCKED_INPUT_MESSAGE = "I'm not able to help with that request. Let's talk about something else - perhaps what's really troubling you?"

GENERATION_ERROR_MESSAGE = "I apologize, but I wasn't able to generate an appropriate response. Could you rephrase your question?"

# Feedback messages
FEEDBACK_POSITIVE_TOAST = "Thanks! This helps us improve."
FEEDBACK_NEGATIVE_TOAST = "Thanks for the feedback!"

# =============================================================================
# CONVERSATION STARTERS
# =============================================================================
CONVERSATION_STARTERS = [
    ("I'm stressed about work", "Work stress"),
    ("How do I stop overthinking everything?", "Overthinking"),
    ("I feel like I've lost my way", "Feeling lost"),
    ("Someone keeps making my life difficult", "Difficult people"),
    ("I can't decide what to do", "Decision making"),
    ("I keep dwelling on past mistakes", "Past regrets"),
    ("I'm scared about the future", "Fear & anxiety"),
    ("How do I stay motivated?", "Motivation"),
]

# =============================================================================
# SIDEBAR TEXT
# =============================================================================
SIDEBAR_STARTERS_TITLE = "Conversation Starters"
SIDEBAR_STARTERS_SUBTITLE = "Click to try one"
SIDEBAR_TOPICS_TITLE = "Topics I Know About"
SIDEBAR_CLEAR_BUTTON = "Clear chat"
SIDEBAR_SOURCE_TEXT = """Based on **Yatharth Gita**
Chapter 1 (47 verses)"""

# =============================================================================
# LLM SYSTEM PROMPT
# =============================================================================
SYSTEM_PROMPT = f"""You are {APP_NAME}, a warm and wise friend who helps young professionals navigate life using insights from the Bhagavad Gita.

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

# =============================================================================
# LLM GENERATION PARAMETERS
# =============================================================================
LLM_TEMPERATURE = 0.8  # Slightly higher for varied responses
LLM_MAX_TOKENS = 400

# =============================================================================
# RETRIEVAL PARAMETERS
# =============================================================================
RETRIEVAL_TOP_K = 2  # Number of verses to retrieve
RETRIEVAL_MIN_SCORE = 0.4  # Minimum relevance score (0-1)

# =============================================================================
# SAFETY REDIRECT MESSAGES
# =============================================================================
REDIRECT_MEDICAL = """I hear that you're going through something really difficult. While I can share wisdom from the Gita about inner peace and strength, I'm not qualified to provide medical or mental health advice.

If you're struggling with mental health, please reach out to a professional:
- **Crisis helpline (India):** iCall - 9152987821
- **International:** Visit findahelpline.com

You deserve proper support. Would you like to talk about finding inner strength or peace instead?"""

REDIRECT_LEGAL = """I understand you're facing a challenging legal situation. While the Gita teaches us about dharma (righteous duty), I'm not able to provide legal advice.

For legal matters, please consult a qualified lawyer or legal aid service.

Is there something about dealing with the stress or ethical aspects of your situation I can help with instead?"""

REDIRECT_FINANCIAL = """Financial decisions are important and deserve expert guidance. While the Gita speaks about detachment from material outcomes, I can't provide specific financial advice.

Please consult a financial advisor for investment or money matters.

Would you like to discuss managing stress around financial worries, or finding balance between material and spiritual goals?"""

REDIRECT_POLITICAL = """I appreciate your interest, but I try to stay away from political discussions. The Gita's wisdom transcends political boundaries and speaks to universal human experiences.

Is there something about your personal values, duty, or decision-making I can help with instead?"""

REDIRECT_OFF_TOPIC = f"""That's an interesting question, but it's a bit outside my area of wisdom! I'm {APP_NAME}, and I specialize in life guidance based on the Bhagavad Gita.

I can help you with:
- Career and purpose questions
- Dealing with anxiety, fear, or stress
- Relationships and difficult people
- Decision-making dilemmas
- Finding inner peace

What's on your mind in these areas?"""

# =============================================================================
# SAFETY KEYWORDS (for topic detection)
# =============================================================================
MEDICAL_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life",
    "self-harm", "cutting myself", "overdose",
    "diagnosis", "symptoms", "medication", "prescribe",
    "doctor", "therapy", "therapist", "psychiatrist",
    "depression medication", "antidepressant"
]

LEGAL_KEYWORDS = [
    "lawsuit", "sue", "legal action", "lawyer", "attorney",
    "court case", "divorce proceedings", "custody",
    "criminal", "arrest", "police complaint", "fir"
]

FINANCIAL_KEYWORDS = [
    "invest", "stock market", "crypto", "bitcoin",
    "loan", "debt", "bankruptcy", "tax advice",
    "financial planning", "retirement fund"
]

POLITICAL_KEYWORDS = [
    "election", "vote for", "political party", "bjp", "congress",
    "modi", "politician", "government policy", "protest",
    "left wing", "right wing", "conservative", "liberal"
]

OFF_TOPIC_KEYWORDS = [
    "recipe", "cook", "food", "restaurant",
    "movie", "film", "tv show", "netflix",
    "sports", "cricket", "football", "game score",
    "weather", "temperature",
    "code", "programming", "python", "javascript",
    "homework", "assignment", "exam answer"
]
