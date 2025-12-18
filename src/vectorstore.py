"""
Vector Store Module for GitaBae.

Handles Pinecone operations: upsert, query, and retrieval.
Provides abstraction over vector database operations.
"""

import json
from pathlib import Path
from typing import List, Optional

from .config import get_pinecone_index, get_openai_client, Config
from .constants import get_chapter_embeddings_path
from .logger import get_vectorstore_logger

logger = get_vectorstore_logger()


class VectorStore:
    """Handles Pinecone vector operations."""

    def __init__(self):
        """Initialize vector store."""
        Config.load()
        self.index = get_pinecone_index()
        self.client = get_openai_client()
        logger.info("VectorStore initialized")

    def upsert_vectors(
        self,
        vectors: List[dict],
        batch_size: int = 50,
        namespace: str = ""
    ) -> int:
        """
        Upsert vectors to Pinecone.

        Args:
            vectors: List of vector dicts with 'id', 'values', 'metadata'
            batch_size: Number of vectors per batch
            namespace: Optional namespace

        Returns:
            Number of vectors upserted
        """
        total = len(vectors)
        upserted = 0

        logger.info(f"Upserting {total} vectors to Pinecone")

        for i in range(0, total, batch_size):
            batch = vectors[i:i + batch_size]

            # Convert to Pinecone format
            pinecone_vectors = [
                {
                    "id": v["id"],
                    "values": v["values"],
                    "metadata": v["metadata"]
                }
                for v in batch
            ]

            self.index.upsert(vectors=pinecone_vectors, namespace=namespace)
            upserted += len(batch)
            logger.info(f"Upserted {upserted}/{total} vectors")

        logger.info(f"Completed upserting {upserted} vectors")
        return upserted

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        namespace: str = "",
        include_metadata: bool = True
    ) -> List[dict]:
        """
        Query vectors by text.

        Args:
            query_text: Text to search for
            top_k: Number of results to return
            namespace: Optional namespace
            include_metadata: Whether to include metadata in results

        Returns:
            List of matching results with scores
        """
        logger.debug(f"Querying for: {query_text[:50]}...")

        # Generate query embedding
        response = self.client.embeddings.create(
            model=Config.EMBEDDING_MODEL,
            input=query_text
        )
        query_vector = response.data[0].embedding

        # Query Pinecone
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=include_metadata
        )

        # Format results
        matches = []
        for match in results.matches:
            result = {
                "id": match.id,
                "score": match.score,
            }
            if include_metadata and match.metadata:
                result["metadata"] = match.metadata
            matches.append(result)

        logger.debug(f"Found {len(matches)} matches")
        return matches

    def get_stats(self) -> dict:
        """Get index statistics."""
        stats = self.index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "namespaces": dict(stats.namespaces) if stats.namespaces else {}
        }

    def delete_all(self, namespace: str = "") -> bool:
        """Delete all vectors in namespace."""
        try:
            logger.warning(f"Deleting all vectors in namespace: '{namespace}'")
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info("Delete operation completed")
            return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}", exc_info=True)
            return False


def upload_embeddings_to_pinecone(
    embeddings_path: Optional[str] = None,
    chapter: int = 1,
    namespace: str = ""
) -> int:
    """
    Upload embeddings from JSON file to Pinecone.

    Args:
        embeddings_path: Path to embeddings JSON file (optional)
        chapter: Chapter number (used if path not provided)
        namespace: Optional namespace

    Returns:
        Number of vectors upserted
    """
    if embeddings_path is None:
        embeddings_path = get_chapter_embeddings_path(chapter)
    else:
        embeddings_path = Path(embeddings_path)

    logger.info(f"Loading embeddings from {embeddings_path}")

    with open(embeddings_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    vectors = data.get("vectors", [])
    logger.info(f"Found {len(vectors)} vectors to upload")

    logger.info("Uploading to Pinecone...")
    store = VectorStore()
    count = store.upsert_vectors(vectors, namespace=namespace)

    logger.info("Upload complete!")
    stats = store.get_stats()
    logger.info(f"Index stats: {stats}")

    return count


def test_retrieval(queries: List[str], top_k: int = 3) -> None:
    """
    Test retrieval with sample queries.

    Args:
        queries: List of test queries
        top_k: Number of results per query
    """
    store = VectorStore()

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print("=" * 60)

        results = store.query(query, top_k=top_k)

        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} (score: {result['score']:.4f}) ---")
            meta = result.get("metadata", {})
            print(f"Chapter {meta.get('chapter')}, Verse {meta.get('verse')}")
            print(f"Tags: {meta.get('tags', [])}")
            print(f"Translation: {meta.get('translation', '')[:200]}...")


def main():
    """Main function to upload embeddings and test retrieval."""
    import sys

    print("=" * 60)
    print("GitaBae - Vector Store Operations")
    print("=" * 60)

    # Use default path from constants
    embeddings_path = get_chapter_embeddings_path(1)

    if len(sys.argv) > 1:
        embeddings_path = Path(sys.argv[1])

    # Check if embeddings file exists
    if not embeddings_path.exists():
        print(f"Embeddings file not found: {embeddings_path}")
        print("Run embeddings.py first to generate embeddings.")
        return

    # Upload to Pinecone
    upload_embeddings_to_pinecone(str(embeddings_path))

    # Test retrieval
    print("\n" + "=" * 60)
    print("Testing Retrieval")
    print("=" * 60)

    test_queries = [
        "How do I deal with anxiety and fear?",
        "What is my duty in life?",
        "How to overcome attachment?"
    ]

    test_retrieval(test_queries, top_k=3)


if __name__ == "__main__":
    main()
