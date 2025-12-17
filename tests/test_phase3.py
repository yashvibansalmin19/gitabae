"""
Phase 3 Tests for GitaBae
Tests for the retrieval module.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRetrieverCreation:
    """Tests for Retriever initialization."""

    def test_retriever_creation(self):
        """Test that retriever can be created."""
        from src.retriever import Retriever

        retriever = Retriever()
        assert retriever is not None

    def test_retriever_loads_verses(self):
        """Test that retriever loads verse data."""
        from src.retriever import Retriever

        retriever = Retriever()
        assert len(retriever.verses_data) == 47

    def test_retriever_has_vector_store(self):
        """Test that retriever has vector store."""
        from src.retriever import Retriever

        retriever = Retriever()
        assert retriever.vector_store is not None


class TestRetrieval:
    """Tests for verse retrieval."""

    @pytest.fixture
    def retriever(self):
        """Create retriever fixture."""
        from src.retriever import Retriever
        return Retriever()

    def test_retrieve_returns_list(self, retriever):
        """Test that retrieve returns a list."""
        results = retriever.retrieve("How to deal with fear?")
        assert isinstance(results, list)

    def test_retrieve_returns_correct_count(self, retriever):
        """Test that retrieve returns requested count."""
        results = retriever.retrieve("What is duty?", top_k=3)
        assert len(results) <= 3

    def test_retrieve_respects_min_score(self, retriever):
        """Test that retrieve filters by minimum score."""
        results = retriever.retrieve("Finding peace", min_score=0.7)
        for result in results:
            assert result.score >= 0.7

    def test_retrieve_returns_retrieved_verse_objects(self, retriever):
        """Test that retrieve returns RetrievedVerse objects."""
        from src.retriever import RetrievedVerse

        results = retriever.retrieve("How to overcome attachment?")
        assert len(results) > 0
        assert isinstance(results[0], RetrievedVerse)

    def test_retrieved_verse_has_all_fields(self, retriever):
        """Test that RetrievedVerse has all required fields."""
        results = retriever.retrieve("What is dharma?")
        assert len(results) > 0

        verse = results[0]
        assert verse.chapter is not None
        assert verse.verse is not None
        assert verse.sanskrit is not None
        assert verse.translation is not None
        assert verse.commentary is not None
        assert verse.tags is not None
        assert verse.score is not None

    def test_retrieved_verse_has_non_empty_content(self, retriever):
        """Test that retrieved verses have non-empty content."""
        results = retriever.retrieve("How to find peace?")
        assert len(results) > 0

        verse = results[0]
        assert len(verse.sanskrit) > 0
        assert len(verse.translation) > 0
        assert len(verse.tags) > 0


class TestContext:
    """Tests for context generation."""

    @pytest.fixture
    def retriever(self):
        """Create retriever fixture."""
        from src.retriever import Retriever
        return Retriever()

    def test_get_context_returns_string(self, retriever):
        """Test that get_context returns a string."""
        context = retriever.get_context("How to deal with anxiety?")
        assert isinstance(context, str)

    def test_get_context_includes_verse_info(self, retriever):
        """Test that context includes verse information."""
        context = retriever.get_context("What is my purpose?")
        assert "Chapter" in context
        assert "Verse" in context

    def test_get_context_includes_translation(self, retriever):
        """Test that context includes translation."""
        context = retriever.get_context("How to overcome fear?")
        assert "Translation:" in context

    def test_get_context_includes_relevance(self, retriever):
        """Test that context includes relevance score."""
        context = retriever.get_context("Finding inner peace")
        assert "Relevance:" in context

    def test_get_context_without_commentary(self, retriever):
        """Test context without commentary."""
        context = retriever.get_context(
            "What is duty?",
            include_commentary=False
        )
        assert "Commentary:" not in context

    def test_get_context_with_commentary(self, retriever):
        """Test context with commentary."""
        context = retriever.get_context(
            "How to act without attachment?",
            include_commentary=True
        )
        assert "Commentary:" in context


class TestRetrievalQuality:
    """Tests for retrieval quality."""

    @pytest.fixture
    def retriever(self):
        """Create retriever fixture."""
        from src.retriever import Retriever
        return Retriever()

    def test_fear_query_returns_relevant_verses(self, retriever):
        """Test that fear-related query returns relevant verses."""
        results = retriever.retrieve("I'm feeling anxious and afraid", top_k=3)
        assert len(results) > 0

        all_tags = []
        for r in results:
            all_tags.extend(r.tags)

        # Should have some relevant tags
        relevant_tags = ["fear", "anxiety", "courage", "sorrow", "peace"]
        assert any(tag in all_tags for tag in relevant_tags)

    def test_duty_query_returns_relevant_verses(self, retriever):
        """Test that duty-related query returns relevant verses."""
        results = retriever.retrieve("What should I do in life?", top_k=3)
        assert len(results) > 0

        all_tags = []
        for r in results:
            all_tags.extend(r.tags)

        relevant_tags = ["duty", "dharma", "action", "karma"]
        assert any(tag in all_tags for tag in relevant_tags)

    def test_attachment_query_returns_relevant_verses(self, retriever):
        """Test that attachment query returns relevant verses."""
        results = retriever.retrieve("I'm too attached to results", top_k=3)
        assert len(results) > 0

        all_tags = []
        for r in results:
            all_tags.extend(r.tags)

        relevant_tags = ["attachment", "detachment", "surrender", "renunciation"]
        assert any(tag in all_tags for tag in relevant_tags)


class TestTagRetrieval:
    """Tests for tag-based retrieval."""

    @pytest.fixture
    def retriever(self):
        """Create retriever fixture."""
        from src.retriever import Retriever
        return Retriever()

    def test_get_all_tags(self, retriever):
        """Test that we can get all tags."""
        tags = retriever.get_all_tags()
        assert isinstance(tags, list)
        assert len(tags) > 0

    def test_retrieve_by_tag(self, retriever):
        """Test retrieval by tag."""
        results = retriever.retrieve_by_tag("duty")
        assert len(results) > 0

        for result in results:
            assert "duty" in [t.lower() for t in result.tags]

    def test_retrieve_by_tag_respects_limit(self, retriever):
        """Test that retrieve_by_tag respects limit."""
        results = retriever.retrieve_by_tag("duty", limit=2)
        assert len(results) <= 2


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.fixture
    def retriever(self):
        """Create retriever fixture."""
        from src.retriever import Retriever
        return Retriever()

    def test_empty_query(self, retriever):
        """Test handling of empty query."""
        results = retriever.retrieve("")
        assert isinstance(results, list)

    def test_very_high_min_score(self, retriever):
        """Test with very high minimum score."""
        results = retriever.retrieve("test query", min_score=0.99)
        # Should return empty or very few results
        assert len(results) <= 1

    def test_nonexistent_tag(self, retriever):
        """Test retrieval with nonexistent tag."""
        results = retriever.retrieve_by_tag("nonexistent_tag_xyz")
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
