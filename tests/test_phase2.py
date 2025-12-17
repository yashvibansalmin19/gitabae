"""
Phase 2 Tests for GitaBae
Tests for configuration, tagging, embeddings, and vector store.
"""

import os
import json
import pytest
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfig:
    """Tests for configuration module."""

    def test_config_loads(self):
        """Test that configuration loads successfully."""
        from src.config import Config
        Config.load()

        assert Config.OPENROUTER_API_KEY is not None
        assert Config.PINECONE_API_KEY is not None
        assert Config.PINECONE_INDEX_NAME == "gitabae"

    def test_config_validates(self):
        """Test that configuration validates correctly."""
        from src.config import Config
        Config.load()

        assert Config.validate() is True

    def test_openai_client_creation(self):
        """Test that OpenAI client can be created."""
        from src.config import get_openai_client

        client = get_openai_client()
        assert client is not None

    def test_pinecone_client_creation(self):
        """Test that Pinecone client can be created."""
        from src.config import get_pinecone_index

        index = get_pinecone_index()
        assert index is not None


class TestTaggedData:
    """Tests for tagged verse data."""

    @pytest.fixture
    def tagged_data(self):
        """Load tagged data fixture."""
        data_path = Path(__file__).parent.parent / "data" / "chapter_1_tagged.json"
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_tagged_file_exists(self):
        """Test that tagged JSON file exists."""
        data_path = Path(__file__).parent.parent / "data" / "chapter_1_tagged.json"
        assert data_path.exists()

    def test_has_metadata(self, tagged_data):
        """Test that data has metadata."""
        assert "metadata" in tagged_data
        assert tagged_data["metadata"]["tagged"] is True

    def test_has_47_verses(self, tagged_data):
        """Test that data has 47 verses."""
        verses = tagged_data.get("verses", [])
        assert len(verses) == 47

    def test_all_verses_have_tags(self, tagged_data):
        """Test that all verses have tags."""
        verses = tagged_data.get("verses", [])
        for verse in verses:
            assert "tags" in verse
            assert len(verse["tags"]) >= 1
            assert len(verse["tags"]) <= 3

    def test_verse_structure(self, tagged_data):
        """Test that verses have correct structure."""
        verses = tagged_data.get("verses", [])
        required_fields = ["chapter", "verse", "sanskrit", "translation", "commentary", "tags"]

        for verse in verses:
            for field in required_fields:
                assert field in verse, f"Missing field: {field}"

    def test_first_verse_is_verse_1(self, tagged_data):
        """Test that first verse is verse 1."""
        verses = tagged_data.get("verses", [])
        assert verses[0]["verse"] == "1"


class TestTagger:
    """Tests for tagger module."""

    def test_tagger_creation(self):
        """Test that tagger can be created."""
        from src.tagger import VerseTagger

        tagger = VerseTagger()
        assert tagger is not None

    def test_tag_verse_returns_list(self):
        """Test that tag_verse returns a list."""
        from src.tagger import VerseTagger

        tagger = VerseTagger()
        tags = tagger.tag_verse(
            "One must perform their duty without attachment.",
            "This verse teaches the importance of selfless action."
        )

        assert isinstance(tags, list)
        assert len(tags) >= 1
        assert len(tags) <= 3

    def test_tags_are_strings(self):
        """Test that tags are strings."""
        from src.tagger import VerseTagger

        tagger = VerseTagger()
        tags = tagger.tag_verse(
            "Control the mind and find peace.",
            "The mind is restless but can be controlled through practice."
        )

        for tag in tags:
            assert isinstance(tag, str)
            assert len(tag) > 0


class TestEmbeddings:
    """Tests for embeddings module."""

    def test_generator_creation(self):
        """Test that embeddings generator can be created."""
        from src.embeddings import EmbeddingsGenerator

        generator = EmbeddingsGenerator()
        assert generator is not None

    def test_embedding_dimensions(self):
        """Test that embeddings have correct dimensions."""
        from src.embeddings import EmbeddingsGenerator

        generator = EmbeddingsGenerator()
        embedding = generator.generate_embedding("Test text for embedding")

        assert isinstance(embedding, list)
        assert len(embedding) == 1536  # ada-002 dimensions

    def test_embedding_values_are_floats(self):
        """Test that embedding values are floats."""
        from src.embeddings import EmbeddingsGenerator

        generator = EmbeddingsGenerator()
        embedding = generator.generate_embedding("Another test")

        for value in embedding[:10]:  # Check first 10
            assert isinstance(value, float)


class TestVectorStore:
    """Tests for vector store module."""

    def test_vectorstore_creation(self):
        """Test that vector store can be created."""
        from src.vectorstore import VectorStore

        store = VectorStore()
        assert store is not None

    def test_index_stats(self):
        """Test that we can get index stats."""
        from src.vectorstore import VectorStore

        store = VectorStore()
        stats = store.get_stats()

        assert "total_vectors" in stats
        assert "dimension" in stats
        assert stats["dimension"] == 1536

    def test_vectors_uploaded(self):
        """Test that vectors are uploaded to Pinecone."""
        from src.vectorstore import VectorStore

        store = VectorStore()
        stats = store.get_stats()

        assert stats["total_vectors"] == 47

    def test_query_returns_results(self):
        """Test that query returns results."""
        from src.vectorstore import VectorStore

        store = VectorStore()
        results = store.query("How to deal with fear?", top_k=3)

        assert isinstance(results, list)
        assert len(results) == 3

    def test_query_results_have_scores(self):
        """Test that query results have scores."""
        from src.vectorstore import VectorStore

        store = VectorStore()
        results = store.query("What is duty?", top_k=2)

        for result in results:
            assert "id" in result
            assert "score" in result
            assert 0 <= result["score"] <= 1

    def test_query_results_have_metadata(self):
        """Test that query results have metadata."""
        from src.vectorstore import VectorStore

        store = VectorStore()
        results = store.query("Finding peace", top_k=1)

        assert "metadata" in results[0]
        meta = results[0]["metadata"]
        assert "chapter" in meta
        assert "verse" in meta
        assert "tags" in meta


class TestRetrievalQuality:
    """Tests for retrieval quality."""

    def test_fear_query_returns_fear_tagged_verse(self):
        """Test that fear query returns verse tagged with fear."""
        from src.vectorstore import VectorStore

        store = VectorStore()
        results = store.query("How do I deal with anxiety and fear?", top_k=1)

        top_result = results[0]
        tags = top_result["metadata"].get("tags", [])

        # Should match verse with fear/anxiety tags
        assert any(tag in ["fear", "anxiety", "courage"] for tag in tags)

    def test_duty_query_returns_duty_tagged_verse(self):
        """Test that duty query returns verse tagged with duty."""
        from src.vectorstore import VectorStore

        store = VectorStore()
        results = store.query("What is my duty in life?", top_k=1)

        top_result = results[0]
        tags = top_result["metadata"].get("tags", [])

        assert "duty" in tags or "dharma" in tags

    def test_attachment_query_returns_relevant_verse(self):
        """Test that attachment query returns relevant verse."""
        from src.vectorstore import VectorStore

        store = VectorStore()
        results = store.query("How to overcome attachment?", top_k=3)

        # At least one result should have attachment-related tag
        all_tags = []
        for r in results:
            all_tags.extend(r["metadata"].get("tags", []))

        assert any(tag in ["attachment", "detachment", "renunciation", "surrender"] for tag in all_tags)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
