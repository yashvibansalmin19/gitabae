"""
Configuration module for GitaBae.
Handles API keys and client setup for OpenRouter and Pinecone.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def get_env(key: str, default: str = None) -> str:
    """
    Get environment variable, with support for Streamlit secrets.
    Falls back to .env file for local development.
    """
    # Try Streamlit secrets first (for production)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and len(st.secrets) > 0 and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    # Fall back to environment variables
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


# API Configuration
class Config:
    """Application configuration."""

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Model Configuration
    LLM_MODEL: str = "openai/gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "openai/text-embedding-ada-002"

    # Pinecone Configuration
    PINECONE_API_KEY: str = None
    PINECONE_INDEX_NAME: str = "gitabae"

    # App metadata (for OpenRouter)
    APP_NAME: str = "GitaBae"
    APP_URL: str = "https://gitabae.streamlit.app"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment."""
        cls.OPENROUTER_API_KEY = get_env("OPENROUTER_API_KEY")
        cls.PINECONE_API_KEY = get_env("PINECONE_API_KEY")
        cls.PINECONE_INDEX_NAME = get_env("PINECONE_INDEX_NAME", "gitabae")
        cls.LLM_MODEL = get_env("LLM_MODEL", "openai/gpt-3.5-turbo")
        cls.EMBEDDING_MODEL = get_env("EMBEDDING_MODEL", "openai/text-embedding-ada-002")
        return cls

    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        required = [
            ("OPENROUTER_API_KEY", cls.OPENROUTER_API_KEY),
            ("PINECONE_API_KEY", cls.PINECONE_API_KEY),
        ]

        missing = [name for name, value in required if not value]

        if missing:
            print(f"Missing required configuration: {', '.join(missing)}")
            print("Please set these in your .env file or environment variables.")
            return False

        return True


def get_openai_client():
    """
    Get OpenAI client configured for OpenRouter.
    Uses OpenRouter as a proxy to access OpenAI models.
    """
    from openai import OpenAI

    Config.load()

    client = OpenAI(
        api_key=Config.OPENROUTER_API_KEY,
        base_url=Config.OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": Config.APP_URL,
            "X-Title": Config.APP_NAME,
        }
    )

    return client


def get_pinecone_client():
    """Get Pinecone client."""
    from pinecone import Pinecone

    Config.load()

    pc = Pinecone(api_key=Config.PINECONE_API_KEY)
    return pc


def get_pinecone_index():
    """Get Pinecone index."""
    pc = get_pinecone_client()
    return pc.Index(Config.PINECONE_INDEX_NAME)


# Quick test function
def test_config():
    """Test that configuration is working."""
    print("Testing configuration...")

    try:
        Config.load()
        if Config.validate():
            print("✓ Configuration loaded successfully")
            print(f"  - OpenRouter API Key: {Config.OPENROUTER_API_KEY[:20]}...")
            print(f"  - Pinecone API Key: {Config.PINECONE_API_KEY[:20]}...")
            print(f"  - Pinecone Index: {Config.PINECONE_INDEX_NAME}")
            print(f"  - LLM Model: {Config.LLM_MODEL}")
            print(f"  - Embedding Model: {Config.EMBEDDING_MODEL}")
            return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


if __name__ == "__main__":
    test_config()
