"""
CSS Styling for GitaBae.

Centralized styling with support for dark/light modes.
Uses color variables to avoid repetition (DRY principle).

Design Principle: Colors are defined once in dictionaries.
The CSS template uses these variables, so changing a color
updates it everywhere automatically.
"""

from dataclasses import dataclass
from typing import Dict


# =============================================================================
# COLOR SCHEMES
# =============================================================================

@dataclass
class ColorScheme:
    """Color scheme for a theme mode."""
    # Backgrounds
    bg_primary: str       # Main app background
    bg_secondary: str     # Cards, chat messages
    bg_sidebar: str       # Sidebar background
    bg_input: str         # Input fields
    bg_button: str        # Buttons
    bg_button_hover: str  # Button hover state

    # Text
    text_primary: str     # Main text
    text_secondary: str   # Subtle text, labels
    text_muted: str       # Very subtle text

    # Accents
    accent: str           # Primary accent (orange)
    accent_hover: str     # Accent hover state
    accent_green: str     # Green for tags

    # Borders
    border: str           # Default border color

    # Special
    verse_card_bg: str    # Verse card background


DARK_COLORS = ColorScheme(
    bg_primary="#0f0f1a",
    bg_secondary="#1e1e2e",
    bg_sidebar="#1a1a2e",
    bg_input="#1e1e2e",
    bg_button="#2d2d44",
    bg_button_hover="#3d3d5c",
    text_primary="#e5e7eb",
    text_secondary="#9ca3af",
    text_muted="#6b7280",
    accent="#ed8936",
    accent_hover="#dd6b20",
    accent_green="#4ade80",
    border="#374151",
    verse_card_bg="#1f2937",
)

LIGHT_COLORS = ColorScheme(
    bg_primary="#ffffff",
    bg_secondary="#f8f9fa",
    bg_sidebar="#ffffff",
    bg_input="#ffffff",
    bg_button="#ffffff",
    bg_button_hover="#fff5eb",
    text_primary="#2c3e50",
    text_secondary="#718096",
    text_muted="#95a5a6",
    accent="#e67e22",
    accent_hover="#d35400",
    accent_green="#27ae60",
    border="#e0e0e0",
    verse_card_bg="#fdfbfb",
)


# =============================================================================
# COMMON STYLES (shared between modes)
# =============================================================================

COMMON_STYLES = """
    /* Header container */
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

    /* Verse card layout (non-color properties) */
    .verse-card {
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin: 0.75rem 0;
        border-left-width: 4px;
        border-left-style: solid;
    }
    .verse-ref {
        font-weight: 600;
    }
    .verse-text {
        font-style: italic;
    }

    /* Theme tags layout */
    .theme-tag {
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-right: 6px;
        display: inline-block;
    }

    /* Header text sizes */
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .header-subtitle {
        font-size: 1rem;
    }
"""


# =============================================================================
# DARK MODE SPECIFIC STYLES
# =============================================================================

def _get_dark_mode_css(c: ColorScheme) -> str:
    """Generate dark mode CSS from color scheme."""
    return f"""
        /* ===== DARK MODE ===== */

        /* Force dark on all main containers */
        html, body, .stApp, [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > div,
        [data-testid="stAppViewContainer"] > div > div,
        .main, .main > div, .block-container,
        [data-testid="stMainBlockContainer"],
        [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"],
        [class*="stAppViewBlockContainer"],
        [class*="block-container"] {{
            background-color: {c.bg_primary} !important;
            background: {c.bg_primary} !important;
        }}

        /* Bottom input area */
        [data-testid="stBottom"],
        [data-testid="stBottom"] > div,
        [data-testid="stBottom"] [data-testid="stVerticalBlock"],
        [data-testid="stBottomBlockContainer"],
        [class*="stBottom"],
        .stChatFloatingInputContainer,
        [data-testid="stChatFloatingInputContainer"],
        [class*="ChatInput"],
        [class*="chatInput"] {{
            background-color: {c.bg_primary} !important;
            background: {c.bg_primary} !important;
        }}

        /* Header */
        [data-testid="stHeader"], header, [data-testid="stToolbar"] {{
            background-color: {c.bg_primary} !important;
            background: {c.bg_primary} !important;
        }}

        /* Header text colors */
        .header-title {{
            color: {c.text_primary} !important;
        }}
        .header-subtitle {{
            color: {c.text_secondary} !important;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarNav"] {{
            background-color: {c.bg_sidebar} !important;
            background: {c.bg_sidebar} !important;
        }}

        /* Sidebar text */
        section[data-testid="stSidebar"] * {{
            color: {c.text_primary} !important;
        }}

        /* Sidebar buttons */
        section[data-testid="stSidebar"] button,
        section[data-testid="stSidebar"] .stButton > button,
        section[data-testid="stSidebar"] [data-testid="baseButton-secondary"] {{
            background-color: {c.bg_button} !important;
            background: {c.bg_button} !important;
            color: {c.text_primary} !important;
            border: 1px solid {c.border} !important;
        }}
        section[data-testid="stSidebar"] button:hover,
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background-color: {c.bg_button_hover} !important;
            background: {c.bg_button_hover} !important;
            border-color: {c.accent} !important;
        }}
        section[data-testid="stSidebar"] button p,
        section[data-testid="stSidebar"] button span {{
            color: {c.text_primary} !important;
        }}

        /* Chat messages */
        [data-testid="stChatMessage"] {{
            background-color: {c.bg_secondary} !important;
            background: {c.bg_secondary} !important;
            border: 1px solid {c.border} !important;
        }}
        [data-testid="stChatMessage"] *,
        [data-testid="stChatMessageContent"],
        [data-testid="stChatMessageContent"] * {{
            color: {c.text_primary} !important;
        }}

        /* Chat input */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div {{
            background-color: {c.bg_primary} !important;
        }}
        [data-testid="stChatInput"] [data-baseweb="textarea"],
        [data-testid="stChatInput"] [class*="TextArea"] {{
            background-color: {c.bg_input} !important;
            border-color: {c.border} !important;
        }}
        [data-testid="stChatInput"] textarea {{
            background-color: {c.bg_input} !important;
            color: {c.text_primary} !important;
        }}
        [data-testid="stChatInput"] textarea::placeholder {{
            color: {c.text_secondary} !important;
        }}
        [data-testid="stChatInput"] button {{
            color: {c.accent} !important;
        }}

        /* Main area buttons */
        .stButton > button {{
            background-color: {c.bg_secondary} !important;
            background: {c.bg_secondary} !important;
            color: {c.text_primary} !important;
            border: 1px solid {c.border} !important;
        }}
        .stButton > button:hover {{
            background-color: {c.bg_button} !important;
            background: {c.bg_button} !important;
            border-color: {c.accent} !important;
            color: {c.text_primary} !important;
        }}

        /* Expander */
        [data-testid="stExpander"],
        [data-testid="stExpander"] > div {{
            background-color: {c.bg_secondary} !important;
            background: {c.bg_secondary} !important;
            border: 1px solid {c.border} !important;
        }}
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary span {{
            color: {c.text_secondary} !important;
            background-color: transparent !important;
        }}
        [data-testid="stExpanderDetails"] {{
            background-color: {c.bg_secondary} !important;
            background: {c.bg_secondary} !important;
        }}

        /* Verse cards */
        .verse-card {{
            background: {c.verse_card_bg} !important;
            border-left-color: {c.accent} !important;
        }}
        .verse-ref {{
            color: {c.accent} !important;
        }}
        .verse-text {{
            color: {c.text_primary} !important;
        }}

        /* Theme tags */
        .theme-tag {{
            background-color: rgba(72, 187, 120, 0.2) !important;
            color: {c.accent_green} !important;
        }}

        /* Toggle */
        [data-testid="stToggle"] span {{
            color: {c.text_primary} !important;
        }}

        /* All markdown text */
        .stMarkdown, .stMarkdown p, .stMarkdown span {{
            color: {c.text_primary} !important;
        }}

        /* Dividers */
        hr {{
            border-color: {c.border} !important;
        }}

        /* Toast */
        [data-testid="stToast"] {{
            background-color: {c.bg_secondary} !important;
            color: {c.text_primary} !important;
        }}

        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: {c.bg_sidebar};
        }}
        ::-webkit-scrollbar-thumb {{
            background: {c.border};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {c.text_muted};
        }}

        /* Catch-all for remaining light backgrounds */
        [class*="st-emotion-cache"] {{
            background-color: transparent !important;
        }}
    """


# =============================================================================
# LIGHT MODE SPECIFIC STYLES
# =============================================================================

def _get_light_mode_css(c: ColorScheme) -> str:
    """Generate light mode CSS from color scheme."""
    return f"""
        /* ===== LIGHT MODE ===== */

        .header-title {{
            color: {c.text_primary};
        }}
        .header-subtitle {{
            color: {c.text_secondary};
        }}

        /* Verse cards */
        .verse-card {{
            background: linear-gradient(135deg, {c.verse_card_bg} 0%, #ebedee 100%);
            border-left-color: {c.accent};
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .verse-ref {{
            color: {c.accent};
        }}
        .verse-text {{
            color: {c.text_primary};
        }}

        /* Theme tags */
        .theme-tag {{
            background-color: #e8f4e8;
            color: {c.accent_green};
        }}

        /* Suggestion buttons */
        .stButton > button {{
            width: 100%;
            text-align: left;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            border: 1px solid {c.border};
            background-color: {c.bg_button};
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
            background-color: {c.bg_button_hover};
            border-color: {c.accent};
        }}
    """


# =============================================================================
# MAIN CSS GENERATOR
# =============================================================================

def get_css(dark_mode: bool = False) -> str:
    """
    Generate complete CSS for the application.

    Args:
        dark_mode: Whether to generate dark mode styles

    Returns:
        Complete CSS wrapped in <style> tags

    Usage:
        st.markdown(get_css(dark_mode=True), unsafe_allow_html=True)
    """
    colors = DARK_COLORS if dark_mode else LIGHT_COLORS
    mode_css = _get_dark_mode_css(colors) if dark_mode else _get_light_mode_css(colors)

    return f"""
    <style>
        {COMMON_STYLES}
        {mode_css}
    </style>
    """


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_color(name: str, dark_mode: bool = False) -> str:
    """
    Get a specific color value.

    Args:
        name: Color attribute name (e.g., 'bg_primary', 'accent')
        dark_mode: Whether to use dark mode colors

    Returns:
        Color hex value

    Example:
        primary_bg = get_color('bg_primary', dark_mode=True)
    """
    colors = DARK_COLORS if dark_mode else LIGHT_COLORS
    return getattr(colors, name, "#000000")


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    # Print sample CSS for inspection
    print("=" * 60)
    print("LIGHT MODE CSS (first 500 chars)")
    print("=" * 60)
    print(get_css(dark_mode=False)[:500])

    print("\n" + "=" * 60)
    print("DARK MODE CSS (first 500 chars)")
    print("=" * 60)
    print(get_css(dark_mode=True)[:500])
