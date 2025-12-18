"""
UI Components for GitaBae.

Reusable Streamlit UI components for consistent rendering.
Each component is a pure function that returns HTML or renders to Streamlit.

Design Principle: Components are stateless and reusable.
They receive data as input and render output - no side effects.
"""

import streamlit as st
from typing import List, Optional

from .constants import (
    APP_NAME,
    APP_ICON,
    APP_TAGLINE,
    CONVERSATION_STARTERS,
    SIDEBAR_STARTERS_TITLE,
    SIDEBAR_STARTERS_SUBTITLE,
    SIDEBAR_TOPICS_TITLE,
    SIDEBAR_CLEAR_BUTTON,
    SIDEBAR_SOURCE_TEXT,
)
from .retriever import RetrievedVerse


# =============================================================================
# HEADER COMPONENT
# =============================================================================

def render_header() -> None:
    """
    Render the app header with logo, title, and tagline.

    Renders directly to Streamlit.
    """
    st.markdown(f"""
    <div class="header-container">
        <div class="logo-icon">{APP_ICON}</div>
        <div class="header-title">{APP_NAME}</div>
        <div class="header-subtitle">{APP_TAGLINE}</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# VERSE CARD COMPONENT
# =============================================================================

def render_verse_card(verse: RetrievedVerse) -> str:
    """
    Generate HTML for a verse card.

    Args:
        verse: RetrievedVerse object with chapter, verse, translation, etc.

    Returns:
        HTML string for the verse card
    """
    tags_html = ''.join([
        f'<span class="theme-tag">{tag}</span>'
        for tag in verse.tags
    ])

    return f"""
    <div class="verse-card">
        <span class="verse-ref">Chapter {verse.chapter}, Verse {verse.verse}</span>
        <span style="color: #95a5a6; font-size: 0.85rem;"> • {verse.score:.0%} relevant</span>
        <p class="verse-text">"{verse.translation}"</p>
        <div>{tags_html}</div>
    </div>
    """


def render_verses_expander(verses: List[RetrievedVerse], title: str = "See the wisdom behind this") -> None:
    """
    Render an expander containing verse cards.

    Args:
        verses: List of RetrievedVerse objects
        title: Expander title text
    """
    if not verses:
        return

    with st.expander(title):
        for verse in verses:
            st.markdown(render_verse_card(verse), unsafe_allow_html=True)


# =============================================================================
# FEEDBACK BUTTONS COMPONENT
# =============================================================================

def render_feedback_buttons(
    message_index: int,
    on_positive: callable,
    on_negative: callable,
    already_rated: bool = False
) -> None:
    """
    Render thumbs up/down feedback buttons.

    Args:
        message_index: Index of the message being rated
        on_positive: Callback when positive button clicked
        on_negative: Callback when negative button clicked
        already_rated: Whether this message was already rated
    """
    col1, col2, col3 = st.columns([1, 1, 10])

    if already_rated:
        with col1:
            st.markdown(
                "<small style='color: #95a5a6;'>✓ Rated</small>",
                unsafe_allow_html=True
            )
    else:
        with col1:
            if st.button("👍", key=f"like_{message_index}", help="This was helpful"):
                on_positive()
        with col2:
            if st.button("👎", key=f"dislike_{message_index}", help="Not helpful"):
                on_negative()


# =============================================================================
# SIDEBAR COMPONENTS
# =============================================================================

def render_sidebar_starters(on_starter_click: callable) -> None:
    """
    Render conversation starter buttons in sidebar.

    Args:
        on_starter_click: Callback(question: str) when a starter is clicked
    """
    st.markdown(f"### 💭 {SIDEBAR_STARTERS_TITLE}")
    st.markdown(
        f"<small style='color: #7f8c8d;'>{SIDEBAR_STARTERS_SUBTITLE}</small>",
        unsafe_allow_html=True
    )

    for question, label in CONVERSATION_STARTERS:
        if st.button(f"💬 {label}", key=question, help=question):
            on_starter_click(question)


def render_sidebar_topics(tags: List[str], max_tags: int = 12) -> None:
    """
    Render topic tags in sidebar.

    Args:
        tags: List of topic tags
        max_tags: Maximum tags to display
    """
    st.markdown(f"### 🏷️ {SIDEBAR_TOPICS_TITLE}")

    sorted_tags = sorted(tags)[:max_tags]
    tag_html = " ".join([
        f'<span class="theme-tag">{tag}</span>'
        for tag in sorted_tags
    ])

    st.markdown(
        f"<div style='line-height: 2;'>{tag_html}</div>",
        unsafe_allow_html=True
    )


def render_sidebar_actions(on_clear: callable) -> None:
    """
    Render action buttons in sidebar (Clear chat, etc).

    Args:
        on_clear: Callback when clear button is clicked
    """
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            f"🗑️ {SIDEBAR_CLEAR_BUTTON}",
            use_container_width=True,
            help="Clear conversation"
        ):
            on_clear()


def render_sidebar_footer(positive_count: int = 0, negative_count: int = 0) -> None:
    """
    Render sidebar footer with feedback stats and source info.

    Args:
        positive_count: Number of positive ratings in session
        negative_count: Number of negative ratings in session
    """
    # Feedback stats (if any)
    if positive_count > 0 or negative_count > 0:
        st.markdown(f"""
        <div style='text-align: center; color: #95a5a6; font-size: 0.75rem; margin-top: 1rem;'>
            Session feedback: 👍 {positive_count} | 👎 {negative_count}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Source info
    st.markdown(f"""
    <div style='text-align: center; color: #95a5a6; font-size: 0.8rem;'>
        {SIDEBAR_SOURCE_TEXT}
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TYPING INDICATOR
# =============================================================================

def show_typing_indicator(placeholder) -> None:
    """
    Show typing indicator in a placeholder.

    Args:
        placeholder: Streamlit empty() placeholder
    """
    from .constants import TYPING_INDICATOR
    placeholder.markdown(TYPING_INDICATOR)


def clear_typing_indicator(placeholder) -> None:
    """
    Clear the typing indicator.

    Args:
        placeholder: Streamlit empty() placeholder
    """
    placeholder.empty()
