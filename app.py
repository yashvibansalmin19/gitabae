"""
GitaBae - Streamlit App
A chatbot that provides life guidance using wisdom from the Bhagavad Gita.
"""

import streamlit as st
from src.generator import ResponseGenerator
from src.retriever import Retriever

# Page config
st.set_page_config(
    page_title="GitaBae",
    page_icon="🕉️",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        max-width: 800px;
    }

    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 12px;
    }

    /* Header styling */
    .header-container {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }

    .header-subtitle {
        font-size: 1.1rem;
        color: #7f8c8d;
        font-style: italic;
    }

    /* Verse card styling */
    .verse-card {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin: 0.75rem 0;
        border-left: 4px solid #e67e22;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .verse-ref {
        color: #e67e22;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .verse-text {
        color: #34495e;
        font-style: italic;
        margin: 0.5rem 0;
        line-height: 1.6;
    }

    /* Theme tag styling */
    .theme-tag {
        background-color: #e8f4e8;
        color: #27ae60;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-right: 6px;
        display: inline-block;
        margin-bottom: 4px;
    }

    /* Sidebar styling */
    .sidebar-header {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }

    /* Suggestion buttons */
    .stButton > button {
        width: 100%;
        text-align: left;
        padding: 0.5rem 1rem;
        margin-bottom: 0.25rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        background-color: white;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #fff5eb;
        border-color: #e67e22;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Expander styling */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
        color: #7f8c8d;
    }
</style>
""", unsafe_allow_html=True)

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
    <div class="header-title">🕉️ GitaBae</div>
    <div class="header-subtitle">Your wise friend for life's questions</div>
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

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show verse references if available (with improved styling)
        if message.get("verses"):
            with st.expander("See the wisdom behind this"):
                for verse in message["verses"]:
                    st.markdown(f"""
<div class="verse-card">
    <span class="verse-ref">Chapter {verse.chapter}, Verse {verse.verse}</span>
    <span style="color: #95a5a6; font-size: 0.85rem;"> • {verse.score:.0%} relevant</span>
    <p class="verse-text">"{verse.translation}"</p>
    <div>{''.join([f'<span class="theme-tag">{tag}</span>' for tag in verse.tags])}</div>
</div>
                    """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt, "verses": []})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response with conversation history
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Pass conversation history for context
            conversation_history = get_conversation_history()
            result = generator.generate(
                prompt,
                conversation_history=conversation_history,
                top_k=2,
                min_score=0.4
            )

            st.markdown(result["response"])

            # Show verse references (more subtle)
            if result["verses"]:
                with st.expander("See the wisdom behind this"):
                    for verse in result["verses"]:
                        st.markdown(f"""
<div class="verse-card">
    <span class="verse-ref">Chapter {verse.chapter}, Verse {verse.verse}</span>
    <span style="color: #95a5a6; font-size: 0.85rem;"> • {verse.score:.0%} relevant</span>
    <p class="verse-text">"{verse.translation}"</p>
    <div>{''.join([f'<span class="theme-tag">{tag}</span>' for tag in verse.tags])}</div>
</div>
                        """, unsafe_allow_html=True)

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "verses": result["verses"]
    })

# Sidebar
with st.sidebar:
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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

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
