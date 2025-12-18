"""
GitaBae - Streamlit App

A chatbot that provides life guidance using wisdom from the Bhagavad Gita.

This file is the thin orchestrator that ties together all the modules.
Business logic, styling, and components are imported from src/.
"""

import streamlit as st

from src.constants import (
    APP_NAME,
    APP_ICON,
    WELCOME_MESSAGE,
    CHAT_PLACEHOLDER,
    RETRIEVAL_TOP_K,
    RETRIEVAL_MIN_SCORE,
    FEEDBACK_POSITIVE_TOAST,
    FEEDBACK_NEGATIVE_TOAST,
)
from src.styles import get_css
from src.components import (
    render_header,
    render_verse_card,
    render_verses_expander,
    render_feedback_buttons,
    render_sidebar_starters,
    render_sidebar_topics,
    render_sidebar_actions,
    render_sidebar_footer,
    show_typing_indicator,
    clear_typing_indicator,
)
from src.feedback import FeedbackEntry, get_feedback_storage
from src.generator import ResponseGenerator
from src.retriever import Retriever


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="centered"
)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialize all session state variables."""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "verses": []
        })

    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


init_session_state()


# =============================================================================
# CACHED RESOURCES
# =============================================================================

@st.cache_resource
def get_generator():
    """Get cached response generator."""
    return ResponseGenerator()


@st.cache_resource
def get_retriever():
    """Get cached retriever."""
    return Retriever()


generator = get_generator()
retriever = get_retriever()
feedback_storage = get_feedback_storage()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_conversation_history() -> list:
    """Get conversation history in format suitable for generator."""
    history = []
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    return history


def process_user_message(message: str) -> dict:
    """
    Process a user message and generate response.

    Args:
        message: User's input message

    Returns:
        Result dict with 'response' and 'verses'
    """
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": message,
        "verses": []
    })

    # Get conversation history and generate response
    history = get_conversation_history()
    result = generator.generate(
        message,
        conversation_history=history,
        top_k=RETRIEVAL_TOP_K,
        min_score=RETRIEVAL_MIN_SCORE
    )

    # Add assistant response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "verses": result["verses"]
    })

    return result


def handle_feedback(message_index: int, rating: str, query: str, response: str):
    """Handle feedback button click."""
    entry = FeedbackEntry.create(
        message_index=message_index,
        rating=rating,
        query=query,
        response=response
    )
    feedback_storage.save(entry)

    toast_msg = FEEDBACK_POSITIVE_TOAST if rating == "positive" else FEEDBACK_NEGATIVE_TOAST
    st.toast(toast_msg)
    st.rerun()


def clear_chat():
    """Clear chat history and feedback."""
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": WELCOME_MESSAGE,
        "verses": []
    })
    feedback_storage.clear_session()
    st.rerun()


# =============================================================================
# APPLY STYLES
# =============================================================================

st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)


# =============================================================================
# HEADER
# =============================================================================

render_header()


# =============================================================================
# CHAT DISPLAY
# =============================================================================

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show verse references and feedback for assistant messages (skip welcome)
        if message["role"] == "assistant" and i > 0:
            # Verse expander
            if message.get("verses"):
                render_verses_expander(message["verses"])

            # Feedback buttons with copy
            if message.get("content") and len(message["content"]) > 50:
                prev_query = ""
                if i > 0 and st.session_state.messages[i - 1]["role"] == "user":
                    prev_query = st.session_state.messages[i - 1]["content"]

                already_rated = feedback_storage.is_rated(i)

                render_feedback_buttons(
                    message_index=i,
                    on_positive=lambda idx=i, q=prev_query, r=message["content"]: handle_feedback(idx, "positive", q, r),
                    on_negative=lambda idx=i, q=prev_query, r=message["content"]: handle_feedback(idx, "negative", q, r),
                    already_rated=already_rated,
                    response_text=message["content"]
                )


# =============================================================================
# CHAT INPUT
# =============================================================================

if prompt := st.chat_input(CHAT_PLACEHOLDER):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display response
    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        show_typing_indicator(typing_placeholder)

        result = process_user_message(prompt)

        clear_typing_indicator(typing_placeholder)
        st.markdown(result["response"])

        if result["verses"]:
            render_verses_expander(result["verses"])


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    # Dark mode toggle
    dark_mode = st.toggle(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode,
        help="Toggle dark/light theme"
    )
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()

    st.markdown("---")

    # Conversation starters
    def on_starter_click(question: str):
        st.session_state.pending_question = question
        st.rerun()

    render_sidebar_starters(on_starter_click)

    st.markdown("---")

    # Topics
    tags = retriever.get_all_tags()
    render_sidebar_topics(tags)

    st.markdown("---")

    # Actions
    render_sidebar_actions(on_clear=clear_chat)

    # Footer with stats
    counts = feedback_storage.count_by_rating()
    render_sidebar_footer(
        positive_count=counts["positive"],
        negative_count=counts["negative"]
    )


# =============================================================================
# HANDLE PENDING QUESTION (from sidebar clicks)
# =============================================================================

if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None
    process_user_message(question)
    st.rerun()
