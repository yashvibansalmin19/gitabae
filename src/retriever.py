"""
Retriever Module for GitaBae.

Handles semantic search and context preparation for the chatbot.
Retrieves relevant verses from the vector store based on user queries.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

from .vectorstore import VectorStore
from .config import Config
from .constants import get_chapter_data_path
from .logger import get_retriever_logger

logger = get_retriever_logger()


@dataclass
class RetrievedVerse:
    """A retrieved verse with full content and relevance score."""
    chapter: int
    verse: str
    sanskrit: str
    translation: str
    commentary: str
    tags: List[str]
    score: float

    def to_context(self, include_commentary: bool = True) -> str:
        """Format verse as context for LLM."""
        context = f"**Chapter {self.chapter}, Verse {self.verse}**\n"
        context += f"Sanskrit: {self.sanskrit}\n"
        context += f"Translation: {self.translation}\n"
        if include_commentary and self.commentary:
            # Limit commentary length for context
            commentary = self.commentary[:500]
            if len(self.commentary) > 500:
                commentary += "..."
            context += f"Commentary: {commentary}\n"
        context += f"Themes: {', '.join(self.tags)}"
        return context


class Retriever:
    """Handles retrieval of relevant Gita verses for user queries."""

    def __init__(self, data_path: Optional[Union[str, Path]] = None, chapter: int = 1):
        """
        Initialize retriever.

        Args:
            data_path: Path to tagged JSON data file (optional, uses default if not provided)
            chapter: Chapter number to load (used if data_path not provided)
        """
        Config.load()
        self.vector_store = VectorStore()

        # Use provided path or get from constants
        if data_path is None:
            data_path = get_chapter_data_path(chapter)

        self.verses_data = self._load_verses(data_path)
        logger.info(f"Retriever initialized with {len(self.verses_data)} verses")

    def _load_verses(self, data_path: Union[str, Path]) -> dict:
        """Load verse data indexed by verse ID."""
        data_path = Path(data_path)

        if not data_path.exists():
            logger.error(f"Data file not found: {data_path}")
            raise FileNotFoundError(f"Data file not found: {data_path}")

        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Index by ID for quick lookup
        verses = {}
        for verse in data.get('verses', []):
            verse_id = f"chapter_{verse['chapter']}_verse_{verse['verse']}"
            verses[verse_id] = verse

        logger.debug(f"Loaded {len(verses)} verses from {data_path}")
        return verses

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.5
    ) -> List[RetrievedVerse]:
        """
        Retrieve relevant verses for a query.

        Args:
            query: User's question or concern
            top_k: Maximum number of verses to return
            min_score: Minimum relevance score (0-1)

        Returns:
            List of RetrievedVerse objects sorted by relevance
        """
        logger.info(f"Retrieving verses for: {query[:50]}...")

        # Query vector store
        results = self.vector_store.query(query, top_k=top_k)

        # Filter by minimum score and enrich with full data
        retrieved = []
        for result in results:
            if result['score'] < min_score:
                logger.debug(f"Skipping verse {result['id']} - score {result['score']:.2f} below threshold")
                continue

            verse_id = result['id']
            verse_data = self.verses_data.get(verse_id)

            if verse_data:
                retrieved.append(RetrievedVerse(
                    chapter=verse_data['chapter'],
                    verse=verse_data['verse'],
                    sanskrit=verse_data['sanskrit'],
                    translation=verse_data['translation'],
                    commentary=verse_data['commentary'],
                    tags=verse_data['tags'],
                    score=result['score']
                ))

        logger.info(f"Retrieved {len(retrieved)} verses above threshold {min_score}")
        return retrieved

    def get_context(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.5,
        include_commentary: bool = True
    ) -> str:
        """
        Get formatted context string for LLM.

        Args:
            query: User's question
            top_k: Maximum verses to include
            min_score: Minimum relevance score
            include_commentary: Whether to include verse commentary

        Returns:
            Formatted context string for LLM prompt
        """
        verses = self.retrieve(query, top_k=top_k, min_score=min_score)

        if not verses:
            return "No directly relevant verses found for this query."

        context_parts = [
            f"Found {len(verses)} relevant verse(s) from the Bhagavad Gita:\n"
        ]

        for i, verse in enumerate(verses, 1):
            context_parts.append(f"\n--- Verse {i} (Relevance: {verse.score:.0%}) ---")
            context_parts.append(verse.to_context(include_commentary=include_commentary))

        return "\n".join(context_parts)

    def retrieve_by_tag(self, tag: str, limit: int = 5) -> List[RetrievedVerse]:
        """
        Retrieve verses by tag/theme.

        Args:
            tag: Theme tag to search for
            limit: Maximum verses to return

        Returns:
            List of verses with matching tag
        """
        logger.info(f"Retrieving verses by tag: {tag}")
        matching = []

        for verse_id, verse_data in self.verses_data.items():
            if tag.lower() in [t.lower() for t in verse_data['tags']]:
                matching.append(RetrievedVerse(
                    chapter=verse_data['chapter'],
                    verse=verse_data['verse'],
                    sanskrit=verse_data['sanskrit'],
                    translation=verse_data['translation'],
                    commentary=verse_data['commentary'],
                    tags=verse_data['tags'],
                    score=1.0  # Direct tag match
                ))

        logger.info(f"Found {len(matching)} verses with tag '{tag}'")
        return matching[:limit]

    def get_all_tags(self) -> List[str]:
        """Get all unique tags in the dataset."""
        tags = set()
        for verse_data in self.verses_data.values():
            tags.update(verse_data.get('tags', []))
        return sorted(tags)


def main():
    """Test retrieval with sample queries."""
    print("=" * 60)
    print("GitaBae - Retrieval Test")
    print("=" * 60)

    retriever = Retriever()

    test_queries = [
        "I'm feeling anxious about my future",
        "How do I know what my duty is?",
        "I'm too attached to outcomes",
        "How to find inner peace?",
        "I feel overwhelmed by choices"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print("=" * 60)

        context = retriever.get_context(query, top_k=2)
        print(context)

    print(f"\n{'='*60}")
    print("Available Tags")
    print("=" * 60)
    print(retriever.get_all_tags())


if __name__ == "__main__":
    main()
