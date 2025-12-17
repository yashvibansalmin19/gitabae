"""
GitaBae - Streamlit App
A chatbot that provides life guidance using wisdom from the Bhagavad Gita.
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from src.generator import ResponseGenerator
from src.retriever import Retriever

# Page config
st.set_page_config(
    page_title="GitaBae",
    page_icon="🪷",
    layout="centered"
)

# Initialize dark mode in session state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Initialize feedback log
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# CSS with dark mode support - comprehensive Streamlit overrides
def get_css(dark_mode: bool) -> str:
    # Common styles for both modes
    common = """
        /* Header styling */
        .header-container {
            text-align: center;
            padding: 1.5rem 0 2rem 0;
        }
        .logo-icon {
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    """

    if dark_mode:
        return f"""
        <style>
            {common}

            /* ===== DARK MODE OVERRIDES ===== */

            /* Main app background */
            .stApp, [data-testid="stAppViewContainer"], .main {{
                background-color: #0f0f1a !important;
            }}

            .block-container {{
                background-color: #0f0f1a !important;
            }}

            /* Header text colors */
            .header-title {{
                font-size: 2.2rem;
                font-weight: 700;
                color: #ffffff !important;
                margin-bottom: 0.25rem;
            }}
            .header-subtitle {{
                font-size: 1rem;
                color: #9ca3af !important;
            }}

            /* Sidebar */
            section[data-testid="stSidebar"] {{
                background-color: #1a1a2e !important;
            }}
            section[data-testid="stSidebar"] .stMarkdown,
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] span,
            section[data-testid="stSidebar"] label {{
                color: #e5e7eb !important;
            }}

            /* Chat messages */
            [data-testid="stChatMessage"] {{
                background-color: #1e1e2e !important;
                border: 1px solid #374151 !important;
            }}
            [data-testid="stChatMessageContent"],
            [data-testid="stChatMessageContent"] p,
            [data-testid="stChatMessageContent"] span {{
                color: #e5e7eb !important;
            }}

            /* Chat input */
            [data-testid="stChatInput"] textarea {{
                background-color: #1e1e2e !important;
                color: #e5e7eb !important;
                border-color: #374151 !important;
            }}
            [data-testid="stChatInput"] {{
                background-color: #1e1e2e !important;
            }}

            /* Buttons */
            .stButton > button {{
                background-color: #1e1e2e !important;
                color: #e5e7eb !important;
                border: 1px solid #374151 !important;
            }}
            .stButton > button:hover {{
                background-color: #2d2d44 !important;
                border-color: #ed8936 !important;
                color: #ffffff !important;
            }}

            /* Expander */
            [data-testid="stExpander"] {{
                background-color: #1e1e2e !important;
                border: 1px solid #374151 !important;
            }}
            .streamlit-expanderHeader {{
                color: #9ca3af !important;
                background-color: #1e1e2e !important;
            }}
            .streamlit-expanderContent {{
                background-color: #1e1e2e !important;
            }}

            /* Verse cards */
            .verse-card {{
                background: #1f2937 !important;
                padding: 1rem 1.25rem;
                border-radius: 12px;
                margin: 0.75rem 0;
                border-left: 4px solid #ed8936 !important;
            }}
            .verse-ref {{
                color: #ed8936 !important;
                font-weight: 600;
            }}
            .verse-text {{
                color: #e5e7eb !important;
                font-style: italic;
            }}

            /* Theme tags */
            .theme-tag {{
                background-color: rgba(72, 187, 120, 0.2) !important;
                color: #4ade80 !important;
                padding: 3px 10px;
                border-radius: 15px;
                font-size: 0.8rem;
                margin-right: 6px;
                display: inline-block;
            }}

            /* Toggle switch */
            [data-testid="stToggle"] span {{
                color: #e5e7eb !important;
            }}

            /* Markdown text */
            .stMarkdown, .stMarkdown p {{
                color: #e5e7eb !important;
            }}

            /* Dividers */
            hr {{
                border-color: #374151 !important;
            }}

            /* Toast */
            [data-testid="stToast"] {{
                background-color: #1e1e2e !important;
                color: #e5e7eb !important;
            }}
        </style>
        """
    else:
        return f"""
        <style>
            {common}

            /* ===== LIGHT MODE ===== */

            .header-title {{
                font-size: 2.2rem;
                font-weight: 700;
                color: #2c3e50;
                margin-bottom: 0.25rem;
            }}
            .header-subtitle {{
                font-size: 1rem;
                color: #718096;
            }}

            /* Verse cards */
            .verse-card {{
                background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
                padding: 1rem 1.25rem;
                border-radius: 12px;
                margin: 0.75rem 0;
                border-left: 4px solid #e67e22;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            .verse-ref {{
                color: #e67e22;
                font-weight: 600;
            }}
            .verse-text {{
                color: #34495e;
                font-style: italic;
            }}

            /* Theme tags */
            .theme-tag {{
                background-color: #e8f4e8;
                color: #27ae60;
                padding: 3px 10px;
                border-radius: 15px;
                font-size: 0.8rem;
                margin-right: 6px;
                display: inline-block;
            }}

            /* Suggestion buttons */
            .stButton > button {{
                width: 100%;
                text-align: left;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                background-color: white;
                transition: all 0.2s ease;
            }}
            .stButton > button:hover {{
                background-color: #fff5eb;
                border-color: #e67e22;
            }}
        </style>
        """

# Apply CSS based on dark mode setting
st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

# Initialize generator
@st.cache_resource
def get_generator():
    return ResponseGenerator()

@st.cache_resource
def get_retriever():
    return Retriever()

generator = get_generator()
retriever = get_retriever()

# Header
st.markdown("""
<div class="header-container">
    <div class="logo-icon">🪷</div>
    <div class="header-title">GitaBae</div>
    <div class="header-subtitle">Navigate life with timeless wisdom</div>
</div>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome message - more casual and inviting
    welcome = """Hey! I'm GitaBae - think of me as a friend who's really into ancient wisdom and loves talking about life's big (and small) questions.

Whether you're stressing about work, dealing with difficult people, feeling a bit lost, or just need someone to talk through something with - I'm here.

What's going on with you?"""
    st.session_state.messages.append({"role": "assistant", "content": welcome, "verses": []})


def get_conversation_history():
    """Get conversation history in format suitable for generator."""
    history = []
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    return history


def log_feedback(message_index: int, rating: str, query: str, response: str):
    """Log user feedback for analysis."""
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "message_index": message_index,
        "rating": rating,
        "query": query[:100] if query else "",
        "response_preview": response[:150] if response else "",
    }
    st.session_state.feedback_log.append(feedback_entry)

    # Also save to file for persistence (optional)
    feedback_file = Path(__file__).parent / "data" / "feedback_log.json"
    try:
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                all_feedback = json.load(f)
        else:
            all_feedback = []

        all_feedback.append(feedback_entry)

        with open(feedback_file, 'w') as f:
            json.dump(all_feedback, f, indent=2)
    except Exception:
        pass  # Silently fail if can't write to file


def render_verse_card(verse):
    """Render a verse card with consistent styling."""
    return f"""
<div class="verse-card">
    <span class="verse-ref">Chapter {verse.chapter}, Verse {verse.verse}</span>
    <span style="color: #95a5a6; font-size: 0.85rem;"> • {verse.score:.0%} relevant</span>
    <p class="verse-text">"{verse.translation}"</p>
    <div>{''.join([f'<span class="theme-tag">{tag}</span>' for tag in verse.tags])}</div>
</div>
    """

# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show verse references and feedback for assistant messages
        if message["role"] == "assistant" and i > 0:  # Skip welcome message
            # Verse references
            if message.get("verses"):
                with st.expander("See the wisdom behind this"):
                    for verse in message["verses"]:
                        st.markdown(render_verse_card(verse), unsafe_allow_html=True)

            # Feedback buttons (only for assistant responses with content)
            if message.get("content") and len(message["content"]) > 50:
                # Get the user query that preceded this response
                prev_query = ""
                if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                    prev_query = st.session_state.messages[i-1]["content"]

                col1, col2, col3 = st.columns([1, 1, 10])
                feedback_key = f"feedback_{i}"

                # Check if already rated
                already_rated = any(
                    f.get("message_index") == i
                    for f in st.session_state.feedback_log
                )

                if not already_rated:
                    with col1:
                        if st.button("👍", key=f"like_{i}", help="This was helpful"):
                            log_feedback(i, "positive", prev_query, message["content"])
                            st.toast("Thanks! This helps us improve.")
                            st.rerun()
                    with col2:
                        if st.button("👎", key=f"dislike_{i}", help="Not helpful"):
                            log_feedback(i, "negative", prev_query, message["content"])
                            st.toast("Thanks for the feedback!")
                            st.rerun()
                else:
                    with col1:
                        st.markdown("<small style='color: #95a5a6;'>✓ Rated</small>", unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt, "verses": []})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response with conversation history
    with st.chat_message("assistant"):
        # Typing indicator
        typing_placeholder = st.empty()
        typing_placeholder.markdown("*🪷 GitaBae is reflecting...*")

        # Pass conversation history for context
        conversation_history = get_conversation_history()
        result = generator.generate(
            prompt,
            conversation_history=conversation_history,
            top_k=2,
            min_score=0.4
        )

        # Clear typing indicator and show response
        typing_placeholder.empty()
        st.markdown(result["response"])

        # Show verse references
        if result["verses"]:
            with st.expander("See the wisdom behind this"):
                for verse in result["verses"]:
                    st.markdown(render_verse_card(verse), unsafe_allow_html=True)

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "verses": result["verses"]
    })

# Sidebar
with st.sidebar:
    # Dark mode toggle at top
    # st.markdown("### ⚙️ Settings")
    dark_mode = st.toggle(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode,
        help="Toggle dark/light theme"
    )
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()

    st.markdown("---")

    st.markdown("### 💭 Conversation Starters")
    st.markdown("<small style='color: #7f8c8d;'>Click to try one</small>", unsafe_allow_html=True)

    suggestions = [
        ("I'm stressed about work", "Work stress"),
        ("How do I stop overthinking everything?", "Overthinking"),
        ("I feel like I've lost my way", "Feeling lost"),
        ("Someone keeps making my life difficult", "Difficult people"),
        ("I can't decide what to do", "Decision making"),
        ("I keep dwelling on past mistakes", "Past regrets"),
        ("I'm scared about the future", "Fear & anxiety"),
        ("How do I stay motivated?", "Motivation"),
    ]

    for question, label in suggestions:
        if st.button(f"💬 {label}", key=question, help=question):
            st.session_state.pending_question = question
            st.rerun()

    st.markdown("---")

    st.markdown("### 🏷️ Topics I Know About")
    tags = retriever.get_all_tags()
    # Display tags in a nicer format
    tag_html = " ".join([f'<span class="theme-tag">{tag}</span>' for tag in sorted(tags)[:12]])
    st.markdown(f"<div style='line-height: 2;'>{tag_html}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear chat", use_container_width=True, help="Clear conversation"):
            st.session_state.messages = []
            st.session_state.feedback_log = []
            st.rerun()

    # Feedback stats (if any)
    if st.session_state.feedback_log:
        positive = sum(1 for f in st.session_state.feedback_log if f["rating"] == "positive")
        negative = sum(1 for f in st.session_state.feedback_log if f["rating"] == "negative")
        st.markdown(f"""
        <div style='text-align: center; color: #95a5a6; font-size: 0.75rem; margin-top: 1rem;'>
            Session feedback: 👍 {positive} | 👎 {negative}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #95a5a6; font-size: 0.8rem;'>
        Based on <strong>Yatharth Gita</strong><br/>
        Chapter 1 (47 verses)
    </div>
    """, unsafe_allow_html=True)

# Handle suggestion clicks
if "pending_question" in st.session_state:
    question = st.session_state.pending_question
    del st.session_state.pending_question

    # Add to messages
    st.session_state.messages.append({"role": "user", "content": question, "verses": []})

    # Generate with conversation history
    conversation_history = get_conversation_history()
    result = generator.generate(
        question,
        conversation_history=conversation_history,
        top_k=2,
        min_score=0.4
    )
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "verses": result["verses"]
    })
    st.rerun()
